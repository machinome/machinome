"""Prototype: statement-level reachability scoping over a node's import closure.

Usage: run from a project root with the project's modules importable.
  python reach.py <module.path:Class> [<module.path:Class> ...]
Prints, per node class, the number of top-level statements kept/dropped per
closure file, and for spec.py the kept statements with the chain that kept them.
"""
import ast, importlib, os, sys, inspect
sys.path.insert(0, os.getcwd())
from machinome.node.sources import source_closure

DYNAMIC = {'globals', 'locals', 'vars', '__dict__', 'eval', 'exec', '__import__',
           'import_module', 'dir', '__getattr__', '__getattribute__'}


def defined_names(stmt):
    if isinstance(stmt, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        return {stmt.name}
    if isinstance(stmt, ast.Assign):
        names = set()
        for t in stmt.targets:
            names |= target_names(t)
        return names
    if isinstance(stmt, ast.AnnAssign):
        return target_names(stmt.target)
    if isinstance(stmt, ast.Import):
        return {(a.asname or a.name.split('.')[0]) for a in stmt.names}
    if isinstance(stmt, ast.ImportFrom):
        return {(a.asname or a.name) for a in stmt.names}
    return set()


def target_names(t):
    if isinstance(t, ast.Name):
        return {t.id}
    if isinstance(t, (ast.Tuple, ast.List)):
        s = set()
        for e in t.elts:
            s |= target_names(e)
        return s
    if isinstance(t, ast.Starred):
        return target_names(t.value)
    return None  # attribute / subscript target: not a plain definition


def removable(stmt):
    if isinstance(stmt, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        return not stmt.decorator_list
    if isinstance(stmt, ast.Assign):
        return all(target_names(t) is not None for t in stmt.targets)
    if isinstance(stmt, ast.AnnAssign):
        return target_names(stmt.target) is not None
    if isinstance(stmt, (ast.Import, ast.ImportFrom)):
        return not any(a.name == '*' for a in stmt.names)
    return False


def mentions(stmt):
    found = set()
    for inner in ast.walk(stmt):
        if isinstance(inner, ast.Name):
            found.add(inner.id)
        elif isinstance(inner, ast.Attribute):
            found.add(inner.attr)
        elif isinstance(inner, ast.Constant) and isinstance(inner.value, str):
            found.add(inner.value)
    return found


def analyse(path):
    with open(path, 'rb') as fh:
        tree = ast.parse(fh.read(), filename=path)
    out = []
    for stmt in tree.body:
        out.append(dict(stmt=stmt, defines=defined_names(stmt) if removable(stmt) else set(),
                        removable=removable(stmt), mentions=mentions(stmt),
                        line=(stmt.lineno, stmt.end_lineno)))
    return out


def reach(files, seed):
    """seed: {path: {class names}}. Returns kept flags and the keeping chain."""
    analyses = {p: analyse(p) for p in files if p.endswith('.py')}
    kept = {}   # (path, index) -> reason
    for p, stmts in analyses.items():
        for i, s in enumerate(stmts):
            if not s['removable']:
                kept[(p, i)] = 'not removable'
            elif p in seed and isinstance(s['stmt'], ast.ClassDef) and s['stmt'].name in seed[p]:
                kept[(p, i)] = 'seed'
    changed = True
    while changed:
        changed = False
        reached = set()
        for (p, i) in kept:
            reached |= analyses[p][i]['mentions']
        for p, stmts in analyses.items():
            for i, s in enumerate(stmts):
                if (p, i) in kept:
                    continue
                hit = s['defines'] & reached
                if hit:
                    # find one keeper mentioning it, for the chain
                    who = next(((q, j) for (q, j) in kept if analyses[q][j]['mentions'] & hit), None)
                    kept[(p, i)] = f'named {sorted(hit)} by {os.path.basename(who[0])}:{analyses[who[0]][who[1]]["line"][0]}'
                    changed = True
    dyn = set()
    for (p, i) in kept:
        dyn |= analyses[p][i]['mentions'] & DYNAMIC
    return analyses, kept, dyn


def main():
    for ref in sys.argv[1:]:
        modname, clsname = ref.split(':')
        module = importlib.import_module(modname)
        klass = getattr(module, clsname)
        src = inspect.getfile(klass)
        files = sorted(source_closure(src))
        root = os.getcwd()
        analyses, kept, dyn = reach(files, {os.path.realpath(src): {clsname}})
        print(f'=== {ref}  src={os.path.relpath(src, root)}  closure={len(files)} files')
        total_kept = total = 0
        for p, stmts in sorted(analyses.items()):
            k = sum(1 for i in range(len(stmts)) if (p, i) in kept)
            total_kept += k; total += len(stmts)
            print(f'  {os.path.relpath(p, root):55s} kept {k:3d} / {len(stmts):3d}')
        print(f'  TOTAL kept {total_kept} / {total}; dynamic mentions in kept text: {sorted(dyn)}')
        for p, stmts in analyses.items():
            if p.endswith('wall_clock_02/spec.py'):
                print('  --- spec.py statements:')
                for i, s in enumerate(stmts):
                    tag = kept.get((p, i), 'DROPPED')
                    head = ast.dump(s['stmt'])[:0]
                    name = (sorted(s['defines']) or [type(s['stmt']).__name__])[0]
                    print(f'    L{s["line"][0]:>3}-{s["line"][1]:<3} {name:28s} {tag}')
        print()


if __name__ == '__main__':
    main()
