# Evidence — `follow-a-sibling-packages-init`

Cycle 19 of the fix-warts-3 campaign (`workflow/ongoing/fix-warts-3.md`).
Bench `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch
`fix-warts-3`, planning commit `8590e8b1b6b0c704035455c9017222bb978b302c`
(`git -C <bench> rev-parse HEAD`), clean tree at the start. Every framework
command ran as
`env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1 /home/asa/devel/machinome/.venv/bin/<tool> ...`;
`python -c 'import machinome; print(machinome.__file__)'` under that
environment printed
`/home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py`.

`<scratchpad>` is
`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad`,
`<scratch>` is `<scratchpad>/cycle19`, `<copy>` is `<scratchpad>/I1/proj`
(the investigation's scratch copy of 3DPrintedClocks at project commit
`ec2a05d1`; `diff -rq -x __pycache__` of its `clocks/` and `simulation/`
against the project printed nothing at the start). `projects/3DPrintedClocks`
was only run, unchanged, with a scratch `SOLID_BUILD_DIR` and
`PYTHONDONTWRITEBYTECODE=1`; its `git status --short` printed
` M screenshots/wall_clock_03.png` and `?? WTs/` (neither from this cycle)
before and after every run. Before every test run or build,
`ps -eo pid,args | grep '[p]ytest\|[m]achinome test\|[m]achinome snapshot\|[m]achinome build'`
printed nothing; runs were one at a time.

## 1. Baseline on the unmodified tree (8590e8b1)

### 1.2 Focused tests

```text
$ env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -f 'wall %e s' \
    .venv/bin/pytest -q -p no:cacheprovider \
    tests/test_source_set.py tests/test_files.py tests/test_source_closure_index.py
26 passed in 5.02s
wall 5.99 s
```

### 1.3 The probe

`<scratch>/probe_repro.py`:

```python
"""Reproduce the sibling-facade gap in the red-test fixture's shape.

Run with cwd = repro/, PYTHONPATH=<bench>, SOLID_BUILD_DIR=<scratch build>.
FIX=1 monkeypatches the candidate closure rule into this process only:
an __init__.py is dropped only when its package directory contains the
importing file. No framework file is edited.
"""
import os
import sys
import time

import machinome
from machinome.node import sources

print('machinome from', machinome.__file__)

if os.environ.get('FIX'):
    _original = sources._parse_project_imports

    def _project_file_for(name, root, importer):
        module = sys.modules.get(name)
        if module is None:
            return None
        filename = getattr(module, '__file__', None)
        if not filename:
            return None
        path = os.path.realpath(filename)
        if (os.path.basename(path) == '__init__.py'
                and os.environ.get('FIX') != 'naive'):
            package_dir = os.path.dirname(path)
            if os.path.commonpath((package_dir, importer)) == package_dir:
                return None
        if not path.startswith(root + os.sep):
            return None
        if (path == sources.FRAMEWORK_DIR
                or path.startswith(sources.FRAMEWORK_DIR + os.sep)):
            return None
        return path

    def _parse_project_imports(path, root):
        import ast
        if not path.endswith('.py'):
            return frozenset()
        try:
            with open(path, 'rb') as fh:
                tree = ast.parse(fh.read(), filename=path)
        except (OSError, SyntaxError):
            return frozenset()
        package = sources._package_of(path)
        names = set()
        for statement in ast.walk(tree):
            if isinstance(statement, ast.Import):
                names.update(alias.name for alias in statement.names)
            elif isinstance(statement, ast.ImportFrom):
                names.update(sources._import_from_targets(statement, package))
        return frozenset(
            found for found in (_project_file_for(name, root, path)
                                for name in names)
            if found is not None)

    sources._parse_project_imports = _parse_project_imports
    sources._import_cache.clear()
    print(f'FIX={os.environ["FIX"]}: rule patched in this process '
          '(naive = follow every __init__.py)')
else:
    print('bench rule, unpatched')

from machinome.core.loader import import_module_from_path  # noqa: E402

root = os.path.realpath(os.getcwd())
shop = import_module_from_path(os.path.join(root, 'shop', '__init__.py'), root)
from shop.wide import Wide  # noqa: E402
from shop.lonely import Lonely  # noqa: E402
from shop.narrow import Narrow  # noqa: E402

MEASURES = os.path.join(root, 'shop', 'library', 'measures.py')


def rel(node):
    return sorted(os.path.relpath(os.path.realpath(p), root) for p in node.files)


print('Wide tracks  ', rel(Wide()))
print('Lonely tracks', rel(Lonely()))
print('Narrow tracks', rel(Narrow()))
print('measures.py tracked by Wide:', 'shop/library/measures.py' in rel(Wide()))

built = Wide()
built.assemble()
print('after build, Wide STL up to date:', built._up_to_date(built.stl_file))

with open(MEASURES, 'rb') as fh:
    original = fh.read()
stat = os.stat(MEASURES)
try:
    with open(MEASURES, 'ab') as fh:
        fh.write(b'# probe edit\n')
    future = time.time() + 10
    os.utime(MEASURES, (future, future))
    rebuilt = Wide()
    print('after editing measures.py, Wide STL up to date:',
          rebuilt._up_to_date(rebuilt.stl_file))
finally:
    with open(MEASURES, 'wb') as fh:
        fh.write(original)
    os.utime(MEASURES, ns=(stat.st_atime_ns, stat.st_mtime_ns))
```

The probe project `<scratch>/repro/`:

`repro/pyproject.toml`:

```toml
[tool.machinome]
model = "shop:Assembly"
```

`repro/shop/__init__.py`:

```python
"""The root assembly's own source, as in tests/source_set_project."""

from machinome.node.assembly import AssemblyNode

from .wide import Wide
from .lonely import Lonely
from .narrow import Narrow


class Assembly(AssemblyNode):

    def render(self):
        return [Wide(), Lonely(), Narrow()]
```

`repro/shop/dims.py`:

```python
DEPTH = 2
```

`repro/shop/library/__init__.py`:

```python
"""A library facade: nothing of its own, every name re-exported."""

from .measures import *  # noqa: F401,F403
```

`repro/shop/library/measures.py`:

```python
WIDTH = 3
```

`repro/shop/lonely.py`:

```python
import cadquery as cq

from machinome.node.cadquery import CadQueryNode


class Lonely(CadQueryNode):
    """Imports no project module: must track its own file only."""

    def render(self):
        return cq.Workplane('XY').box(1, 1, 1)
```

`repro/shop/narrow.py`:

```python
import cadquery as cq

from machinome.node.cadquery import CadQueryNode

from . import dims


class Narrow(CadQueryNode):
    """Reaches a sibling module through its own package: `from . import`
    offers the containing package, whose __init__ is the root assembly."""

    def render(self):
        return cq.Workplane('XY').box(1, 1, dims.DEPTH)
```

`repro/shop/wide.py`:

```python
import cadquery as cq

from machinome.node.cadquery import CadQueryNode

from .library import WIDTH


class Wide(CadQueryNode):
    """A leaf whose width comes through a sibling package's facade."""

    def render(self):
        return cq.Workplane('XY').box(WIDTH, 2, 2)
```

Three runs, one at a time, each into a fresh build directory:

```text
$ env -C <scratch>/repro PYTHONDONTWRITEBYTECODE=1 SOLID_BUILD_DIR=<scratch>/build-a-none \
    PYTHONPATH=<bench> .venv/bin/python <scratch>/probe_repro.py
machinome from /home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py
bench rule, unpatched
Wide tracks   ['shop/wide.py']
Lonely tracks ['shop/lonely.py']
Narrow tracks ['shop/dims.py', 'shop/narrow.py']
measures.py tracked by Wide: False
after build, Wide STL up to date: True
after editing measures.py, Wide STL up to date: True

$ env -C <scratch>/repro FIX=1 ... SOLID_BUILD_DIR=<scratch>/build-a-fix ...
FIX=1: rule patched in this process (naive = follow every __init__.py)
Wide tracks   ['shop/library/__init__.py', 'shop/library/measures.py', 'shop/wide.py']
Lonely tracks ['shop/lonely.py']
Narrow tracks ['shop/dims.py', 'shop/narrow.py']
measures.py tracked by Wide: True
after build, Wide STL up to date: True
after editing measures.py, Wide STL up to date: False

$ env -C <scratch>/repro FIX=naive ... SOLID_BUILD_DIR=<scratch>/build-a-naive ...
FIX=naive: rule patched in this process (naive = follow every __init__.py)
Wide tracks   ['shop/library/__init__.py', 'shop/library/measures.py', 'shop/wide.py']
Lonely tracks ['shop/lonely.py']
Narrow tracks ['shop/__init__.py', 'shop/dims.py', 'shop/library/__init__.py', 'shop/library/measures.py', 'shop/lonely.py', 'shop/narrow.py', 'shop/wide.py']
measures.py tracked by Wide: True
after build, Wide STL up to date: True
after editing measures.py, Wide STL up to date: False
```

(The `machinome from` line, identical in every run, is shown once.) The
three blocks are design.md's: the bench rule leaves `Wide` current after
`measures.py` changes; the candidate rule tracks the library and refuses
it; the naive rule puts the whole project into `Narrow`'s set.

### 1.4 The catalogue scan

`<scratch>/scan_facades.py` (read-only: it parses project files and imports
nothing):

```python
"""Read-only static scan of the catalogue: which project files import
through the __init__.py of a package that does not contain them.

Nothing is imported or executed; every project file is only parsed. For
each project (a directory holding a pyproject.toml with [tool.machinome],
outermost wins, project worktrees under WTs/ skipped), every .py file
outside WTs/, _build/, hidden directories, __pycache__, node_modules,
venvs and site-packages is parsed and each import statement resolved
statically against the project root (absolute) or the file's directory
(relative), as the source closure's sys.modules lookup would find it when
the project root is on sys.path.

For an import whose module resolves to a package __init__.py whose
directory does NOT contain the importing file (a sibling package), it
records:

- facade: `from pkg import NAME` where NAME is not a submodule file or
  subpackage of pkg -- the name comes from the __init__'s namespace, so
  the bench tracks none of what produced it (the clocks case);
  split into `reexport` (the __init__ has an import statement, so NAME may
  come from another module) and `own` (the __init__ only defines names);
- submodule: `from pkg import mod` with mod a submodule -- tracked today
  through `pkg.mod`; the candidate adds pkg/__init__.py;
- bare: `import pkg` / `import a.pkg` resolving to a non-ancestor
  __init__.py -- untracked today, tracked by the candidate.

An __init__.py that is empty (no statements, or only a docstring) adds
nothing to a closure when tracked except its own file; it is counted
apart as `empty`.

Output: one JSON document on stdout and a short table on stderr.
"""
import ast
import json
import os
import sys

PROJECTS = '/home/asa/devel/machinome/projects'
SKIP_DIRS = {'WTs', '_build', '__pycache__', 'node_modules', 'venv',
             'site-packages', 'build', 'dist'}


def is_machinome_manifest(path):
    try:
        with open(path, encoding='utf-8', errors='replace') as fh:
            return '[tool.machinome' in fh.read()
    except OSError:
        return False


def project_roots():
    roots = []
    for dirpath, dirnames, filenames in os.walk(PROJECTS, followlinks=False):
        dirnames[:] = sorted(d for d in dirnames
                             if d not in SKIP_DIRS and not d.startswith('.'))
        depth = os.path.relpath(dirpath, PROJECTS).count(os.sep)
        if 'pyproject.toml' in filenames and is_machinome_manifest(
                os.path.join(dirpath, 'pyproject.toml')):
            if os.path.isdir(os.path.join(dirpath, '.git')) or os.path.isfile(
                    os.path.join(dirpath, '.git')):
                roots.append(dirpath)
                dirnames[:] = []
                continue
        if depth >= 2:
            dirnames[:] = []
    return roots


def python_files(root):
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = sorted(d for d in dirnames
                             if d not in SKIP_DIRS and not d.startswith('.'))
        for name in sorted(filenames):
            if name.endswith('.py'):
                yield os.path.join(dirpath, name)


def resolve(base_dir, parts):
    """The file a dotted module path resolves to under base_dir."""
    path = os.path.join(base_dir, *parts) if parts else base_dir
    if os.path.isfile(os.path.join(path, '__init__.py')):
        return os.path.join(path, '__init__.py')
    if parts and os.path.isfile(path + '.py'):
        return path + '.py'
    return None


def init_kind(path, cache={}):
    if path in cache:
        return cache[path]
    try:
        with open(path, 'rb') as fh:
            tree = ast.parse(fh.read(), filename=path)
    except (OSError, SyntaxError, ValueError):
        cache[path] = 'unparsable'
        return 'unparsable'
    body = [s for s in tree.body
            if not (isinstance(s, ast.Expr)
                    and isinstance(s.value, ast.Constant))]
    if not body:
        kind = 'empty'
    elif any(isinstance(s, (ast.Import, ast.ImportFrom))
             for s in ast.walk(tree)):
        kind = 'reexport'
    else:
        kind = 'own'
    cache[path] = kind
    return kind


def contains(directory, path):
    return os.path.commonpath((directory, path)) == directory


def scan(root):
    rows = []
    for path in python_files(root):
        try:
            with open(path, 'rb') as fh:
                tree = ast.parse(fh.read(), filename=path)
        except (OSError, SyntaxError, ValueError):
            continue
        here = os.path.dirname(path)
        for st in ast.walk(tree):
            targets = []
            if isinstance(st, ast.Import):
                for alias in st.names:
                    targets.append((alias.name.split('.'), None, root))
            elif isinstance(st, ast.ImportFrom):
                parts = (st.module or '').split('.') if st.module else []
                if st.level:
                    base = here
                    for _ in range(st.level - 1):
                        base = os.path.dirname(base)
                    targets.append((parts, st.names, base))
                else:
                    targets.append((parts, st.names, root))
            for parts, names, base in targets:
                if not parts and base == root:
                    continue
                found = resolve(base, parts)
                if found is None or not found.endswith('__init__.py'):
                    continue
                package_dir = os.path.dirname(found)
                if contains(package_dir, path):
                    continue  # ancestor: dropped by both rules
                if not contains(root, found):
                    continue
                kind = init_kind(found)
                if names is None:
                    rows.append(dict(file=path, init=found, how='bare',
                                     kind=kind, names=[]))
                    continue
                facade_names = [a.name for a in names
                                if a.name != '*' and resolve(
                                    package_dir, [a.name]) is None]
                star = any(a.name == '*' for a in names)
                sub_names = [a.name for a in names
                             if a.name != '*' and a.name not in facade_names]
                if facade_names or star:
                    rows.append(dict(file=path, init=found, how='facade',
                                     kind=kind,
                                     names=facade_names + (['*'] if star
                                                           else [])))
                if sub_names:
                    rows.append(dict(file=path, init=found, how='submodule',
                                     kind=kind, names=sub_names))
    return rows


def is_test(path):
    name = os.path.basename(path)
    return (name.startswith('test_') or name.endswith('_test.py')
            or '/tests/' in path or name == 'conftest.py')


def main():
    report = {}
    for root in project_roots():
        rows = scan(root)
        report[os.path.relpath(root, PROJECTS)] = [
            dict(row, file=os.path.relpath(row['file'], root),
                 init=os.path.relpath(row['init'], root),
                 test=is_test(row['file']))
            for row in rows]
    json.dump(report, sys.stdout, indent=1)

    def affected(pred):
        return sorted(p for p, rows in report.items()
                      if any(pred(r) for r in rows))

    lost = affected(lambda r: r['how'] in ('facade', 'bare')
                    and r['kind'] in ('reexport', 'own') and not r['test'])
    lost_reexport = affected(lambda r: r['how'] in ('facade', 'bare')
                             and r['kind'] == 'reexport' and not r['test'])
    grows = affected(lambda r: r['kind'] != 'empty' and not r['test'])
    any_init = affected(lambda r: not r['test'])
    print(f'projects scanned: {len(report)}', file=sys.stderr)
    print(f'non-test file names a non-ancestor package __init__: '
          f'{len(any_init)}', file=sys.stderr)
    print(f'  ... a non-empty one (closure grows): {len(grows)}',
          file=sys.stderr)
    print(f'  ... takes a name from its namespace (facade or bare, '
          f'non-empty): {len(lost)}', file=sys.stderr)
    print(f'  ... of which the __init__ re-exports through imports: '
          f'{len(lost_reexport)}', file=sys.stderr)
    for p in lost:
        inits = sorted({r['init'] for r in report[p]
                        if r['how'] in ('facade', 'bare')
                        and r['kind'] in ('reexport', 'own')
                        and not r['test']})
        files = len({r['file'] for r in report[p]
                     if r['how'] in ('facade', 'bare')
                     and r['kind'] in ('reexport', 'own') and not r['test']})
        print(f'    {p}: {files} files through {inits}', file=sys.stderr)
    only_grow = sorted(set(grows) - set(lost))
    for p in only_grow:
        inits = sorted({r['init'] for r in report[p]
                        if r['kind'] != 'empty' and not r['test']})
        print(f'    (grows only) {p}: {inits}', file=sys.stderr)


if __name__ == '__main__':
    main()
```

```text
$ /usr/bin/time -f 'wall %e s' .venv/bin/python -B <scratch>/scan_facades.py \
    > <scratch>/logs/scan-a.json 2> <scratch>/logs/scan-a.txt
projects scanned: 77
non-test file names a non-ancestor package __init__: 13
  ... a non-empty one (closure grows): 2
  ... takes a name from its namespace (facade or bare, non-empty): 2
  ... of which the __init__ re-exports through imports: 2
    3DPrintedClocks: 120 files through ['clocks/__init__.py', 'clocks/cq_gears/__init__.py']
    Robots/roboto_origin: 10 files through [13 __init__.py under modules/roboparty_train/robolab/...]
wall 10.30 s
$ cmp <scratch>/logs/scan.json <scratch>/logs/scan-a.json   # Stage P's output
(identical)
```

(The stderr also carries six `SyntaxWarning: invalid escape sequence` lines
from project files the scan parses: four in `3DPrintedClocks/clocks/`, one
in `openflexure-microscope/compare_hashes.py`, one in `splitflap`.)

Restricted, as design.md's table is, to non-test files a node can import
(excluding paths under `docs/`, `openspec/`, `tools/`, `scripts/`, `spike/`,
`upstream/`, `modules/`, `restoration/` and `_build_worktrees/`), with a
one-off filter over `scan-a.json` printing files and rows by
(`__init__.py`, kind, how):

```text
3DPrintedClocks 224 files
    clocks/__init__.py reexport bare 33
    clocks/__init__.py reexport facade 86
    clocks/cq_gears/__init__.py reexport facade 3
    simulation/shared/__init__.py empty submodule 215
Calculators/Curta-Type-I-3x 10 files
    simulation/standard/__init__.py empty submodule 10
Lab-Equipment/openflexure-microscope 10 files
    simulation/microscope/actuators/__init__.py empty submodule 3
    simulation/microscope/body/__init__.py empty submodule 7
Robots/YouCanBuildDog 1 files
    simulation/tools/__init__.py empty submodule 1
```

The four projects of design.md, "What the catalogue loses", and no other.

### 1.5 The unchanged project, unmodified bench

```text
$ env -C /home/asa/devel/machinome/projects/3DPrintedClocks PYTHONDONTWRITEBYTECODE=1 \
    SOLID_BUILD_DIR=<scratch>/build-real PYTHONPATH=<bench> /usr/bin/time -v timeout 3000 \
    .venv/bin/machinome test wall_clock_22 --mesh --volume-epsilon 0.001 --set facing=0
```

Cold (`build-real` did not exist; log `<scratch>/logs/real-1-cold.log`):

```text
Ran 25 tests in 39.62 seconds: 19 passed, 6 failed (mesh engine, volume epsilon 0.001 mm³)
Elapsed (wall clock) time (h:mm:ss or m:ss): 0:42.96
Maximum resident set size (kbytes): 916168
Exit status: 1
```

The six failures are the clock's own: `test_assembly_integrity`,
`test_movement_runs_free_through_a_swing`,
`test_the_author_weight_hangs_clear_below_the_compact_frame` and
`test_the_train_runs_free_over_twelve_hours` raise the mesh engine's
`ValueError` refusing `clock-SlidingWeightShell,...stl` (NotManifold);
`test_solid_integrity` (`bow_tie_red` has 5 connected bodies) and
`test_source_body_inventory` (the bow ties' 5 and 4 bodies, the weight
shell's 2, and the intersections those meshes cause) are body-count
failures.

`state.py save <scratch>/build-real <scratch>/logs/real-cold.json`: 290
files recorded. Warm (log `real-2-warm.log`):

```text
Ran 25 tests in 19.39 seconds: 19 passed, 6 failed (mesh engine, volume epsilon 0.001 mm³)
Elapsed (wall clock) time (h:mm:ss or m:ss): 0:22.52
$ .venv/bin/python <scratchpad>/I1/state.py diff <scratch>/logs/real-cold.json <scratch>/build-real
before 290 files, after 292
added 2, removed 0, replaced (new inode) 0, same inode but stat changed 0
  ADDED .seg: 2      (two verdict-memo segments under .verdicts/)
$ .venv/bin/python <scratchpad>/I1/state.py save <scratch>/build-real <scratch>/logs/real-warm.json
292 files recorded
```

Same six failures. No artifact was rewritten by the warm run.

## 2. Red tests, unmodified `machinome/`

Fixture additions in `tests/source_set_project/`: `library/__init__.py`
(`from .measures import *  # noqa: F401,F403`), `library/measures.py`
(`WIDTH = 3`), `wide.py` (`Wide`, a `CadQueryNode` box `WIDTH x 2 x 2`
through `from .library import WIDTH`), `peg.py` (`Peg`, a `CadQueryNode`
box of height `dimensions.HEIGHT` through `from . import dimensions`), and
the fixture `__init__.py` importing `Peg` and `Wide` beside the existing
nodes (its `Assembly.render` unchanged; its docstring now says the walk
never follows "the package containing the module that imports through
it"). `tests/test_source_set.py`, `SourceSetTest`, gains
`test_a_module_behind_a_sibling_package_init_is_tracked`,
`test_editing_a_module_behind_a_sibling_package_init_invalidates_the_artifact`
and the guard `test_the_importers_own_package_init_is_not_tracked`;
`setUp`/`tearDown` restore `MEASURES`'s times as they do `DIMENSIONS`'s.

```text
$ env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -f 'wall %e s' \
    .venv/bin/pytest -q -p no:cacheprovider \
    tests/test_source_set.py tests/test_files.py tests/test_source_closure_index.py
E       AssertionError: '<bench>/tests/source_set_project/library/measures.py' not found in {'<bench>/tests/source_set_project/wide.py'}
tests/test_source_set.py:112: AssertionError
E       AssertionError: True is not false
tests/test_source_set.py:177: AssertionError
FAILED tests/test_source_set.py::SourceSetTest::test_a_module_behind_a_sibling_package_init_is_tracked
FAILED tests/test_source_set.py::SourceSetTest::test_editing_a_module_behind_a_sibling_package_init_invalidates_the_artifact
2 failed, 27 passed in 4.85s
wall 5.73 s
```

Red for the reasons named: `Wide` tracks only `wide.py`, and after
`measures.py` is rewritten and moved 10 s ahead a fresh `Wide` still
reports its STL up to date (line 177 is the `assertFalse`). The guard
`test_the_importers_own_package_init_is_not_tracked` and every existing
test pass on the unmodified code.

## 3. The change

`machinome/node/sources.py`: `_parse_project_imports(path, root)` passes
`path` (always a real path: `source_closure` starts from
`os.path.realpath(src)` and queues only paths `_project_file` returned) to
`_project_file(name, root, importer)`, which now drops an `__init__.py` only
when `os.path.commonpath((package, importer)) == package` for its package
directory. The comment above the test says which `__init__.py` is dropped,
which is followed, and why; the docstring names `importer`. Nothing else in
the file changed (`git diff machinome/node/sources.py`: 3 hunks, 23
insertions, 12 deletions).

```text
$ ... pytest -q -p no:cacheprovider tests/test_source_set.py tests/test_files.py tests/test_source_closure_index.py
29 passed in 5.28s
wall 6.33 s
$ ... pytest -p no:cacheprovider tests/test_source_set.py -v \
    -k "sibling or importers_own or package_init_is_not or unrelated or library_modules"
test_a_module_behind_a_sibling_package_init_is_tracked PASSED
test_editing_a_module_behind_a_sibling_package_init_invalidates_the_artifact PASSED
test_library_modules_are_not_tracked PASSED
test_package_init_is_not_tracked PASSED
test_the_importers_own_package_init_is_not_tracked PASSED
test_unrelated_node_is_not_invalidated PASSED
6 passed, 13 deselected in 2.70s
```

The probe, unpatched, against the changed bench (fresh build directory
`<scratch>/build-a-changed`) prints the `FIX=1` block of section 1.3:

```text
bench rule, unpatched
Wide tracks   ['shop/library/__init__.py', 'shop/library/measures.py', 'shop/wide.py']
Lonely tracks ['shop/lonely.py']
Narrow tracks ['shop/dims.py', 'shop/narrow.py']
measures.py tracked by Wide: True
after build, Wide STL up to date: True
after editing measures.py, Wide STL up to date: False
```

## 4. Validation in the originating project

### 4.1 The scratch copy, cold, changed bench

```text
$ env -C <copy> PYTHONDONTWRITEBYTECODE=1 SOLID_BUILD_DIR=<scratch>/build-copy PYTHONPATH=<bench> \
    /usr/bin/time -v timeout 3000 .venv/bin/machinome test wall_clock_22 --mesh \
    --volume-epsilon 0.001 --set facing=0
Ran 25 tests in 40.32 seconds: 19 passed, 6 failed (mesh engine, volume epsilon 0.001 mm³)
Elapsed (wall clock) time (h:mm:ss or m:ss): 0:43.91
$ .venv/bin/python <scratchpad>/I1/state.py save <scratch>/build-copy <scratch>/logs/copy-cold.json
290 files recorded
```

The same six failures as section 1.5 (log `<scratch>/logs/copy-1-cold.log`).

### 4.2 The pillar edit

One Edit to `<copy>/clocks/plates.py`, line 1356, under `if self.heavy:`:
`self.bottom_pillar_r = self.plate_distance / 2` became
`self.bottom_pillar_r = self.plate_distance / 2 + 3.0`. Then the
investigation's pose probe, which builds the model the way `machinome test`
does and reports the pillar's artifact:

```text
$ env -C <copy> PYTHONDONTWRITEBYTECODE=1 SOLID_BUILD_DIR=<scratch>/build-copy PYTHONPATH=<bench> \
    /usr/bin/time -f 'wall %e s' .venv/bin/python <scratchpad>/I1/probe_pose.py
machinome from /home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py
...
wound_position (live datum): -92.94310323421598
assembly.weight_positions[0]: (-13.907004366451044, np.float64(-92.94310323421598), 30.5)
frame_bottom: -18.55
weight.shell world translation: [-13.907, -30.5, -92.9431]
pillars.pillar: parts-FramePillar,dial_diameter=200.0,in... ino=286050 size=76284 sha256=90c98bf085ce9233 up_to_date=True
pillars.pillar: STL on disk extents [14.469, 37.096, 31.1]
pillars.pillar: live render extents [14.473, 37.1, 31.104]
weight.shell: clock-SlidingWeightShell,dial_diameter=2... ino=286310 size=171884 sha256=9bcda6b28a04f33d up_to_date=True
weight.shell: STL on disk extents [55.0, 272.499, 54.985]
weight.shell: live render extents [55.0, 272.5, 55.0]
wall 43.26 s
$ SHOW=20 .venv/bin/python <scratchpad>/I1/state.py diff <scratch>/logs/copy-cold.json <scratch>/build-copy
before 290 files, after 290
added 0, removed 0, replaced (new inode) 288, same inode but stat changed 0
  REPLACED .brep: 72
  REPLACED .sources: 144
  REPLACED .stl: 72
```

The STL on disk now has the edited pillar's 37.096 mm, where the bench
before this change rewrote nothing and kept 31.096 mm (the investigation's
measurement, design.md, "In the originating project"). Every leaf's STL,
BREP and both currency records were re-derived (72 leaves, 288 files),
including all twelve `FramePillar` files (three pillars, each an STL, a
BREP and two `.sources` records); the two files left alone are a verdict
segment and the model's lock file. Every clock leaf runs `spec.movement`,
which executes the whole `clocks` library, so an edit to `clocks/plates.py`
re-derives every leaf.

The BREPs, measured with `<scratch>/pillar_extents.py`:

```python
"""Extents of every FramePillar STL and BREP in a build directory.

    pillar_extents.py <build_dir>
"""
import glob
import os
import sys

import cadquery as cq
import trimesh

folder = os.path.join(sys.argv[1], 'wall_clock_22', 'simulation',
                      'wall_clock_22')
for stl in sorted(glob.glob(os.path.join(folder, 'parts-FramePillar,*.stl'))):
    index = stl.split('index=')[1].split(',')[0]
    mesh = trimesh.load(stl, force='mesh')
    box = cq.Shape.importBrep(stl[:-len('.stl')] + '.brep').BoundingBox()
    print(f'FramePillar index={index}: '
          f'STL {[round(float(v), 3) for v in mesh.extents]}, '
          f'BREP {[round(v, 3) for v in (box.xlen, box.ylen, box.zlen)]}')
```

```text
$ env -C <scratch> PYTHONDONTWRITEBYTECODE=1 .venv/bin/python <scratch>/pillar_extents.py <scratch>/build-copy
FramePillar index=0: STL [14.469, 37.096, 31.1], BREP [14.469, 37.1, 31.1]
FramePillar index=1: STL [14.469, 37.096, 31.1], BREP [14.469, 37.1, 31.1]
FramePillar index=2: STL [21.6, 21.593, 31.1], BREP [21.6, 21.6, 31.1]
$ ... pillar_extents.py <scratch>/build-real     # section 1.5's build, unedited source
FramePillar index=0: STL [14.469, 31.096, 31.1], BREP [14.469, 31.1, 31.1]
FramePillar index=1: STL [14.469, 31.096, 31.1], BREP [14.469, 31.1, 31.1]
FramePillar index=2: STL [21.6, 21.593, 31.1], BREP [21.6, 21.6, 31.1]
```

The two bottom pillars' STL and BREP agree at 37.1 mm; index 2 is the top
pillar, which the edit does not size. Before this change the BREP kept
31.1 mm even when a deleted STL was regenerated (the finding's last
sentence).

What the pillar tracks, measured once on `<copy>` with the change
(`<scratch>/tracked_counts.py`, which loads the model with `load_node` and
builds nothing):

```python
"""How many files Wall Clock 22's pillar and root track. Run with cwd =
the project (or its scratch copy); loads the model, builds nothing.
"""
import os
import time

import machinome
from machinome.core.loader import load_node, select_model

print('machinome from', machinome.__file__)
root = os.path.realpath(os.getcwd())
selection = select_model('wall_clock_22')
selection.anchor()
started = time.perf_counter()
node = load_node(selection.reference, overrides=['facing=0'])
print(f'load_node {time.perf_counter() - started:.2f} s')


def rel(paths):
    return sorted(os.path.relpath(os.path.realpath(p), root) for p in paths)


pillar = rel(node.pillars.pillar.files)
print('pillar tracks', len(pillar), 'files,',
      sum(p.startswith('clocks/') for p in pillar), 'under clocks/')
for name in ('clocks/__init__.py', 'clocks/plates.py', 'clocks/assembly.py',
             'clocks/cq_gears/__init__.py', 'simulation/__init__.py',
             'simulation/wall_clock_22/__init__.py',
             'simulation/shared/__init__.py'):
    print(f'  {name}: {"tracked" if name in pillar else "not tracked"}')
print('root tracks', len(rel(node.files)), 'files')
```

```text
load_node 10.49 s
pillar tracks 43 files, 30 under clocks/
  clocks/__init__.py: tracked
  clocks/plates.py: tracked
  clocks/assembly.py: tracked
  clocks/cq_gears/__init__.py: tracked
  simulation/__init__.py: not tracked
  simulation/wall_clock_22/__init__.py: not tracked
  simulation/shared/__init__.py: tracked
root tracks 45 files
```

The investigation's figures with the rule patched in (43, 30, 45; the two
ancestor `__init__.py` untracked, the sibling `simulation/shared/__init__.py`
tracked), now from the bench's own code.

### 4.3 Revert, then the documented test

One Edit restored line 1356. `diff -rq -x __pycache__ <copy>/clocks
/home/asa/devel/machinome/projects/3DPrintedClocks/clocks` printed nothing
(exit 0).

```text
$ .venv/bin/python <scratchpad>/I1/state.py save <scratch>/build-copy <scratch>/logs/copy-edited.json
290 files recorded
$ env -C <copy> ... machinome test wall_clock_22 --mesh --volume-epsilon 0.001 --set facing=0
Ran 25 tests in 40.73 seconds: 19 passed, 6 failed (mesh engine, volume epsilon 0.001 mm³)
Elapsed (wall clock) time (h:mm:ss or m:ss): 0:44.08
$ .venv/bin/python <scratchpad>/I1/state.py diff <scratch>/logs/copy-edited.json <scratch>/build-copy
before 290 files, after 291
added 1, removed 0, replaced (new inode) 287, same inode but stat changed 1
  ADDED .seg: 1
  REPLACED .brep: 72
  REPLACED .sources: 143
  REPLACED .stl: 72
  RESTAMPED .sources: 1
$ ... pillar_extents.py <scratch>/build-copy
FramePillar index=0: STL [14.469, 31.096, 31.1], BREP [14.469, 31.1, 31.1]
FramePillar index=1: STL [14.469, 31.096, 31.1], BREP [14.469, 31.1, 31.1]
FramePillar index=2: STL [21.6, 21.593, 31.1], BREP [21.6, 21.6, 31.1]
```

The revert is itself a source edit, so every leaf is re-derived again and
the pillars return to 31.1 mm in both artifacts. (The one `.sources` record
`state.py` counts as same-inode is `parts-Frame...24169d7b6c05.brep.sources`,
whose BREP was replaced with the rest; `state.py` compares inode numbers, and
a freed number can be reused.) Same six failures. Then warm:

```text
$ .venv/bin/python <scratchpad>/I1/state.py save <scratch>/build-copy <scratch>/logs/copy-reverted.json
291 files recorded
$ env -C <copy> ... machinome test wall_clock_22 --mesh --volume-epsilon 0.001 --set facing=0
Ran 25 tests in 19.52 seconds: 19 passed, 6 failed (mesh engine, volume epsilon 0.001 mm³)
Elapsed (wall clock) time (h:mm:ss or m:ss): 0:22.99
$ .venv/bin/python <scratchpad>/I1/state.py diff <scratch>/logs/copy-reverted.json <scratch>/build-copy
before 291 files, after 293
added 2, removed 0, replaced (new inode) 0, same inode but stat changed 0
  ADDED .seg: 2
```

No artifact rewritten; only two verdict-memo segments added.

### 4.4 The unchanged project, changed bench

Into section 1.5's `<scratch>/build-real` (last recorded as
`real-warm.json`, 292 files):

```text
$ env -C /home/asa/devel/machinome/projects/3DPrintedClocks PYTHONDONTWRITEBYTECODE=1 \
    SOLID_BUILD_DIR=<scratch>/build-real PYTHONPATH=<bench> /usr/bin/time -v timeout 3000 \
    .venv/bin/machinome test wall_clock_22 --mesh --volume-epsilon 0.001 --set facing=0
Ran 25 tests in 40.35 seconds: 19 passed, 6 failed (mesh engine, volume epsilon 0.001 mm³)
Elapsed (wall clock) time (h:mm:ss or m:ss): 0:43.45
$ .venv/bin/python <scratchpad>/I1/state.py diff <scratch>/logs/real-warm.json <scratch>/build-real
before 292 files, after 293
added 1, removed 0, replaced (new inode) 288, same inode but stat changed 0
  ADDED .seg: 1
  REPLACED .brep: 72
  REPLACED .sources: 144
  REPLACED .stl: 72
$ .venv/bin/python <scratchpad>/I1/state.py save <scratch>/build-real <scratch>/logs/real-changed.json
293 files recorded
```

The one rebuild: every leaf's tracked set grew, so its recorded digest no
longer matches and the model is re-derived once (43.45 s against the
unmodified bench's warm 22.52 s). Second run:

```text
Ran 25 tests in 19.19 seconds: 19 passed, 6 failed (mesh engine, volume epsilon 0.001 mm³)
Elapsed (wall clock) time (h:mm:ss or m:ss): 0:22.35
$ .venv/bin/python <scratchpad>/I1/state.py diff <scratch>/logs/real-changed.json <scratch>/build-real
before 293 files, after 295
added 2, removed 0, replaced (new inode) 0, same inode but stat changed 0
  ADDED .seg: 2
```

Warm again, nothing rewritten, 22.35 s against 22.52 s before the change.
The six failures are the same tests in both runs. `git -C
/home/asa/devel/machinome/projects/3DPrintedClocks status --short` printed
` M screenshots/wall_clock_03.png` and `?? WTs/` before and after, as at
the start.

| run (Wall Clock 22, documented test) | bench | build dir | wall | tests | files rewritten |
|---|---|---|---|---|---|
| project, cold | unmodified | build-real (new) | 42.96 s | 25 / 19 / 6 | all (cold) |
| project, warm | unmodified | build-real | 22.52 s | 25 / 19 / 6 | 0 |
| copy, cold | changed | build-copy (new) | 43.91 s | 25 / 19 / 6 | all (cold) |
| copy, pillar edit (pose probe build) | changed | build-copy | 43.26 s | — | 288 |
| copy, reverted | changed | build-copy | 44.08 s | 25 / 19 / 6 | 287 + 1 |
| copy, warm | changed | build-copy | 22.99 s | 25 / 19 / 6 | 0 |
| project, first run after the change | changed | build-real | 43.45 s | 25 / 19 / 6 | 288 |
| project, warm | changed | build-real | 22.35 s | 25 / 19 / 6 | 0 |

## 5. Words and records

- `docs/adrs/NODE/ADR-033-import-closure-source-set-and-up-to-date-leaf-path.md`:
  the section "Amendment (2026-10-07, change
  `follow-a-sibling-packages-init`)" appended as design.md Decision 2
  words it; the header's `**Amended by:**` line gains "; amended 2026-10-07
  (change follow-a-sibling-packages-init) — a sibling package's
  __init__.py is followed". `docs/adrs/README.md`: ADR-033's entry ends
  ", amended 2026-10-07".
- `docs/architecture.md`, the source-set invariant: "never the
  `__init__.py` of a package containing the importing module, which would
  make every node depend on every file, though a sibling package's
  `__init__.py` is followed (ADR-033, amended)". `grep -n "__init__"
  docs/architecture.md` afterwards: the other matches are about
  constructors, `machinome/node/__init__.py`, namespace packages and the
  module table; none states the walk's rule.
- `docs/concepts/node-tree.rst`, "Freshness": the bullet of design.md
  Decision 4. `grep -rn "__init__" docs --include=*.rst` outside
  `docs/adrs/`: `docs/reference/cli.rst` lines 463 and 489 describe
  `machinome vet`'s own import walk ("package `__init__.py` files
  included"), not the source set; the rest are constructors and a
  directory listing. No page states the old rule.
- `docs/project/changelog.rst`: design.md Decision 4's bullet, last under
  `Unreleased`.

```text
$ ... pytest -q -p no:cacheprovider tests/test_release_records.py
9 passed, 58 subtests passed in 0.15s
$ env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1 .venv/bin/sphinx-build -W -q -b html docs <scratch>/docs-html
(exit 0, wall 5.25 s)
```

Lint, on `machinome/node/sources.py`, `tests/test_source_set.py`,
`tests/source_set_project/__init__.py` and the four new fixture files,
compared with the same files at HEAD (`git show HEAD:<file>` into
`<scratch>/head/`):

```text
$ env -C <bench> flake8 --max-line-length=89 <files>          # pyenv shim
tests/source_set_project/__init__.py:18:1: F401 '.block.Block' imported but unused
tests/test_source_set.py:245:24: E128 continuation line under-indented for visual indent
$ env -C <scratch>/head flake8 --max-line-length=89 <the three files at HEAD>
tests/source_set_project/__init__.py:18:1: F401 '.block.Block' imported but unused
tests/test_source_set.py:197:24: E128 continuation line under-indented for visual indent
```

The same two findings, both on lines this change does not touch (the E128
is `export_stub`'s signature, moved down by the new tests). The two new
imports in the fixture `__init__.py` carry `# noqa: F401`, the root
assembly importing nodes it does not render.

```text
$ env -C <bench> .venv/bin/black --check <files>              # black 26.5.1
would reformat tests/source_set_project/wide.py
would reformat tests/source_set_project/peg.py
would reformat machinome/node/sources.py
would reformat tests/test_source_set.py
4 files would be reformatted, 3 files would be left unchanged.
$ env -C <scratch>/head .venv/bin/black --config <bench>/pyproject.toml --check <the three files at HEAD>
would reformat tests/test_source_set.py
would reformat machinome/node/sources.py
2 files would be reformatted, 1 file would be left unchanged.
$ env -C <bench> .venv/bin/black --check tests/source_set_project/block.py tests/source_set_project/cyl.py tests/source_set_project/lonely.py
would reformat tests/source_set_project/block.py
```

`black --check` is red at HEAD on these files: the tree keeps single
quotes. With string normalization off (`black -S --diff`), the four new
fixture files and the fixture `__init__.py` need nothing, and the only
lines black would change that HEAD does not already have are
`_parse_project_imports`'s generator, which black reshapes at HEAD as
well, now over two lines instead of one, and `self.measures_times`, written in the shape of
`self.dimensions_times` beside it, which black rewrites at HEAD too. The new
`wide.py` and `peg.py` differ from black only in `'XY'`, as `block.py` does.

## 6. Findings record

- `workflow/warts.md`: the entry "Generated-artifact freshness is not
  dependable for source-bound CAD leaves" and its section heading
  "3DPrintedClocks" (it was the section's only entry) deleted; in
  "Planned, never done", the line "**Generated-artifact freshness**
  (3DPrintedClocks, the first entry). Investigation never started; ..."
  deleted.
- `workflow/archive/fix-warts-3-2026-10-06/resolved.md`: the entry verbatim
  under `## \`follow-a-sibling-packages-init\``, with its "What shipped"
  paragraph (the rule, the red-then-green tests, the probe, the copy's
  pillar edit, the unchanged project's one rebuild and warm run, and the
  two halves that no longer reproduce with the investigation's
  measurements).
- `workflow/ongoing/fix-warts-3.md`, "Progress": one line for
  investigation 1 and one for this cycle, after cycle 18's.

## 7. Sync, archive, suite

Before archiving, `openspec validate follow-a-sibling-packages-init`:
"Change 'follow-a-sibling-packages-init' is valid". Each delta requirement,
compared with `diff` against its baseline block, differs only in the
source-set paragraph and the two added scenarios (`build-pipeline`) and the
first sentence (`source-closure-cost`).

```text
$ env -C <bench> openspec archive follow-a-sibling-packages-init --yes
Proposal warnings in proposal.md (non-blocking):
  ⚠ Why section should not exceed 1000 characters
Task status: 26/29 tasks
Warning: 3 incomplete task(s) found. Continuing due to --yes flag.
Specs to update:
  build-pipeline: update
  source-closure-cost: update
Applying changes to openspec/specs/build-pipeline/spec.md:
  ~ 1 modified
Applying changes to openspec/specs/source-closure-cost/spec.md:
  ~ 1 modified
Totals: + 0, ~ 2, - 0, → 0
Specs updated successfully.
Change 'follow-a-sibling-packages-init' archived as '2026-10-07-follow-a-sibling-packages-init'.
```

The three incomplete tasks were section 7's own, ticked here after the
archive. Every carried and added scenario appears once in the synced specs
(`grep -c "Scenario: <title>"` = 1 for the two new ones, "Imported project
module edit invalidates dependants", "Source edit invalidates ancestors",
"A library change does not invalidate", "A binding change selects a
different snapshot", and the three of `source-closure-cost`). The tool
left a trailing blank line at the end of
`openspec/specs/source-closure-cost/spec.md`, as an earlier archive did to
`build-pipeline/spec.md`.

```text
$ env -C <bench> openspec validate --specs
Totals: 45 passed, 0 failed (45 items)
$ ... pytest -q -p no:cacheprovider tests/test_source_set.py tests/test_files.py tests/test_source_closure_index.py
29 passed in 4.93s
wall 5.89 s
$ env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -f 'wall %e s' \
    .venv/bin/pytest -q -p no:cacheprovider          # alone, the whole suite
4756 passed, 4 skipped, 55 warnings, 6708 subtests passed in 678.77s (0:11:18)
wall 681.14 s
```

No fixture node's grown set failed a test. Nothing is committed.
