"""Prototype 2: statement reachability over a node's import closure with
Python name resolution. A bare name resolves in its own module (its top-level
definitions and import bindings, then star-import sources); an attribute
chain rooted at a module binding resolves into that module; any other
attribute name, and any string constant, matches every top-level definition
of that name in every closure file (the ADR-071 catch-all). Non-definition
statements, decorated non-node definitions and star imports are never
dropped.

Usage (from the project root, modules importable):
  python reach2.py [--overlay DIR] module:Class [module:Class ...]
"""
import ast, importlib, os, sys, inspect, json
sys.path.insert(0, os.getcwd())
from importlib.util import resolve_name
from machinome.node.sources import source_closure, _loaded_as, _project_file, node_classes_in

DYNAMIC_CALLS = {'globals', 'locals', 'vars', 'dir', 'eval', 'exec', '__import__'}
overlay = None
args = sys.argv[1:]
if args and args[0] == '--overlay':
    overlay = args[1]; args = args[2:]
ROOT = os.getcwd()


def read(path):
    if overlay:
        rel = os.path.relpath(path, ROOT)
        cand = os.path.join(overlay, rel)
        if os.path.exists(cand):
            return open(cand, 'rb').read()
    return open(path, 'rb').read()


def target_names(t):
    if isinstance(t, ast.Name):
        return {t.id}
    if isinstance(t, (ast.Tuple, ast.List)):
        s = set()
        for e in t.elts:
            r = target_names(e)
            if r is None:
                return None
            s |= r
        return s
    if isinstance(t, ast.Starred):
        return target_names(t.value)
    return None


class Module:
    def __init__(self, path):
        self.path = path
        self.tree = ast.parse(read(path), filename=path)
        self.package, self.modname = _loaded_as(path)
        self.nodes = node_classes_in(path) or frozenset()
        self.stmts = list(self.tree.body)
        self.defs = {}        # name -> [stmt index]
        self.bindings = {}    # name -> ('module', path) | ('name', path, name)
        self.stars = []       # star-imported closure paths
        self.removable = []
        self.dynamic = False
        for i, s in enumerate(self.stmts):
            self.removable.append(self._removable(s))
            for n in self._defined(s):
                self.defs.setdefault(n, []).append(i)
            self._bind(s)

    def _removable(self, s):
        if isinstance(s, ast.ClassDef):
            return not s.decorator_list or s.name in self.nodes
        if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return not s.decorator_list
        if isinstance(s, ast.Assign):
            return all(target_names(t) is not None for t in s.targets)
        if isinstance(s, ast.AnnAssign):
            return target_names(s.target) is not None
        if isinstance(s, (ast.Import, ast.ImportFrom)):
            return not any(a.name == '*' for a in s.names)
        return False

    def _defined(self, s):
        if isinstance(s, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            return {s.name}
        if isinstance(s, ast.Assign):
            out = set()
            for t in s.targets:
                out |= target_names(t) or set()
            return out
        if isinstance(s, ast.AnnAssign):
            return target_names(s.target) or set()
        if isinstance(s, ast.Import):
            return {(a.asname or a.name.split('.')[0]) for a in s.names}
        if isinstance(s, ast.ImportFrom):
            return {(a.asname or a.name) for a in s.names if a.name != '*'}
        return set()

    def _resolve_module(self, name):
        """closure path for an absolute module name, or None."""
        return _project_file(name, ROOT_REAL, self.path)

    def _bind(self, s):
        if isinstance(s, ast.Import):
            for a in s.names:
                p = self._resolve_module(a.name)
                self.bindings[a.asname or a.name.split('.')[0]] = ('module', p, a.name) if a.asname else ('module', self._resolve_module(a.name.split('.')[0]), a.name.split('.')[0])
        elif isinstance(s, ast.ImportFrom):
            base = s.module or ''
            if s.level:
                try:
                    base = resolve_name('.' * s.level + base, self.package or '')
                except (ImportError, ValueError):
                    return
            for a in s.names:
                if a.name == '*':
                    p = self._resolve_module(base)
                    if p:
                        self.stars.append(p)
                    continue
                sub = self._resolve_module(f'{base}.{a.name}')
                if sub:
                    self.bindings[a.asname or a.name] = ('module', sub, f'{base}.{a.name}')
                else:
                    p = self._resolve_module(base)
                    self.bindings[a.asname or a.name] = ('name', p, a.name)


def mentions(stmt):
    """(bare names, attribute chains as tuples, strings) in a statement."""
    names, chains, strings, dyn = set(), set(), set(), False
    for inner in ast.walk(stmt):
        if isinstance(inner, ast.Name):
            names.add(inner.id)
        elif isinstance(inner, ast.Attribute):
            chain = []
            node = inner
            while isinstance(node, ast.Attribute):
                chain.append(node.attr)
                node = node.value
            if isinstance(node, ast.Name):
                chains.add((node.id,) + tuple(reversed(chain)))
            else:
                for a in chain:
                    chains.add((None, a))
            if inner.attr == '__dict__':
                dyn = True
        elif isinstance(inner, ast.Constant) and isinstance(inner.value, str):
            strings.add(inner.value)
        elif isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name) and inner.func.id in DYNAMIC_CALLS:
            dyn = True
        elif isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute) and inner.func.attr == 'import_module':
            dyn = True
    return names, chains, strings, dyn


class Reach:
    def __init__(self, files):
        self.modules = {p: Module(p) for p in files if p.endswith('.py')}
        self.kept = {}
        self.global_defs = {}
        for p, m in self.modules.items():
            for n, idx in m.defs.items():
                self.global_defs.setdefault(n, []).extend((p, i) for i in idx)

    def keep(self, p, i, why):
        if (p, i) in self.kept:
            return False
        self.kept[(p, i)] = why
        return True

    def resolve_name_in(self, m, name, seen=None):
        """statements (path, i) a bare name in module m can refer to."""
        seen = seen or set()
        if (m.path, name) in seen:
            return []
        seen.add((m.path, name))
        out = [(m.path, i) for i in m.defs.get(name, [])]
        b = m.bindings.get(name)
        if b and b[0] == 'name' and b[1] in self.modules:
            out += self.resolve_name_in(self.modules[b[1]], b[2], seen)
        if not out:
            for star in m.stars:
                if star in self.modules:
                    out += self.resolve_name_in(self.modules[star], name, seen)
        return out

    def resolve_chain(self, m, chain):
        """attribute chain rooted at a bare name: into a module binding when
        the root is one, else the catch-all on the last attribute."""
        root, *attrs = chain
        if root is None:
            return self.global_defs.get(attrs[0], [])
        b = m.bindings.get(root)
        target = None
        if b and b[0] == 'module' and b[1] in self.modules:
            target = self.modules[b[1]]
        if target is None:
            out = list(self.resolve_name_in(m, root))
            for a in attrs:
                out += self.global_defs.get(a, [])
            return out
        out = [(m.path, i) for i in m.defs.get(root, [])]
        # walk attrs: submodule (package __init__ bindings) or definition
        for k, a in enumerate(attrs):
            nb = target.bindings.get(a)
            if nb and nb[0] == 'module' and nb[1] in self.modules and k < len(attrs) - 1:
                out += [(target.path, i) for i in target.defs.get(a, [])]
                target = self.modules[nb[1]]
                continue
            out += self.resolve_name_in(target, a)
            for rest in attrs[k + 1:]:
                out += self.global_defs.get(rest, [])
            break
        return out

    def run(self, seed):
        for p, m in self.modules.items():
            for i, s in enumerate(m.stmts):
                if not m.removable[i]:
                    self.keep(p, i, 'not removable')
                elif p in seed and isinstance(s, ast.ClassDef) and s.name in seed[p]:
                    self.keep(p, i, 'seed')
        frontier = list(self.kept)
        while frontier:
            p, i = frontier.pop()
            m = self.modules[p]
            names, chains, strings, dyn = mentions(m.stmts[i])
            if dyn:
                m.dynamic = True
            targets = []
            for n in names:
                targets += [(t, f'name {n} from {os.path.basename(p)}:{m.stmts[i].lineno}') for t in self.resolve_name_in(m, n)]
            for c in chains:
                targets += [(t, f'attr {".".join(x or "?" for x in c)} from {os.path.basename(p)}:{m.stmts[i].lineno}') for t in self.resolve_chain(m, c)]
            for st in strings:
                targets += [(t, f'string {st!r} from {os.path.basename(p)}:{m.stmts[i].lineno}') for t in self.global_defs.get(st, [])]
            for (tp, ti), why in targets:
                if self.keep(tp, ti, why):
                    frontier.append((tp, ti))


ROOT_REAL = os.path.realpath(ROOT)

def main():
    results = {}
    for ref in args:
        modname, clsname = ref.split(':')
        module = importlib.import_module(modname)
        klass = getattr(module, clsname)
        src = os.path.realpath(inspect.getfile(klass))
        files = sorted(os.path.realpath(f) for f in source_closure(src))
        r = Reach(files)
        r.run({src: {clsname}})
        total = sum(len(m.stmts) for m in r.modules.values())
        print(f'=== {ref}  closure={len(files)} files, kept {len(r.kept)} / {total} statements')
        spec = next((p for p in r.modules if p.endswith('wall_clock_02/spec.py')), None)
        m = r.modules[spec]
        kept_spec = []
        for i, s in enumerate(m.stmts):
            name = sorted(m._defined(s))[:1] or [type(s).__name__]
            tag = r.kept.get((spec, i))
            if tag:
                kept_spec.append(name[0])
            if name[0] in ('STRING_ROUTE', 'Movement', 'StringGeometry', 'string_geometry', 'movement', 'WoundStringRoute'):
                print(f'    spec.py L{s.lineno:>3}-{s.end_lineno:<3} {name[0]:20s} {tag or "DROPPED"}')
        dyn = [os.path.relpath(p, ROOT) for p, mm in r.modules.items() if mm.dynamic]
        print(f'    spec.py kept {len(kept_spec)}/{len(m.stmts)}; dynamic lookups in kept text of: {dyn}')
        per_file = {os.path.relpath(p, ROOT): (sum(1 for i in range(len(mm.stmts)) if (p, i) in r.kept), len(mm.stmts)) for p, mm in r.modules.items()}
        results[ref] = dict(kept=len(r.kept), total=total, per_file=per_file,
                            string_route_kept=any(n == 'STRING_ROUTE' for n in kept_spec))
    print(json.dumps({k: dict(kept=v['kept'], total=v['total'], string_route_kept=v['string_route_kept']) for k, v in results.items()}, indent=1))
    out = os.environ.get('REACH_OUT')
    if out:
        json.dump(results, open(out, 'w'), indent=1)

main()
