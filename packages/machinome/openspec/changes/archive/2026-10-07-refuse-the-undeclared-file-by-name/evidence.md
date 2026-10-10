# Evidence — `refuse-the-undeclared-file-by-name`

Cycle 12 of the fix-warts-3 campaign (`workflow/ongoing/fix-warts-3.md`).
Bench `machinome/WTs/fix-warts-3`, branch `fix-warts-3`, planning commit
1cddf6d (`git -C <bench> rev-parse HEAD` printed
`1cddf6d0c9ae4d737c84c44953a29725b09cfaea`). Every framework command below
ran as
`env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1 /home/asa/devel/machinome/.venv/bin/<tool> ...`,
with `-p no:cacheprovider` for pytest, one process at a time, never in
parallel (`ps -eo pid,args | grep '[p]ytest\|[m]achinome test\|[m]achinome
snapshot\|[m]achinome build'` listed no run but the checking shell itself
before each heavy run). Python 3.12.3. The interpreter check,
`python -c 'import machinome; print(machinome.__file__)'`, printed
`/home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py`.

No catalogue project was run or edited: this change is a framework message
contract, validated on fixture projects (proposal, Authorization).

`<scratch>` is the campaign scratchpad's `cycle12/` directory
(`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle12`).
The scratchpad is not durable; the probe sources this record depends on
are copied in 1.3. `<focused>` is the two sets of tasks.md 1.2:

- `<focused-a>`: `tests/test_missing_source_file.py
  tests/test_builder_lifecycle.py tests/test_leaf_contract_mesh.py
  tests/test_builder_reload_resilience.py`;
- `<focused-b>`: `tests/test_stl_node.py tests/test_step_node.py -k
  missing_declaration`.

## 1. Baseline on the unmodified tree (1cddf6d)

### 1.2 Focused tests

```
$ pytest -q -p no:cacheprovider <focused-a>
71 passed, 7 subtests passed in 9.93s            (wall 11.03 s)
$ pytest -q -p no:cacheprovider <focused-b>
2 passed, 96 deselected in 2.99s                 (wall 3.95 s)
```

Stage P's counts (71 passed, 7 subtests; 2 passed, 96 deselected) hold.

### 1.3 The probes and the six builds

`<scratch>/probe_construct.py`:

```python
"""Construct every undeclared source-bound leaf and print what it raises.

Run with the probe project on sys.path and the bench on PYTHONPATH.
"""

import os
import sys
import importlib

HERE = os.path.dirname(os.path.realpath(__file__))
PROJECT = os.path.join(HERE, 'probe_project')
sys.path.insert(0, PROJECT)

import machinome  # noqa: E402

print('machinome from', machinome.__file__)

parts = importlib.import_module('parts')

for name in ('BareStl', 'BareStep', 'BareJscad', 'BareScad',
             'EmptyStl', 'EmptyStep', 'EmptyJscad', 'EmptyScad'):
    klass = getattr(parts, name)
    try:
        klass()
    except BaseException as error:  # noqa: B902
        print(f'{name}: {type(error).__name__}: {error}')
    else:
        print(f'{name}: constructed')

# A node package's own adapter, the declared-contract stand-in.
sys.path.insert(0, os.environ['BENCH'])
from tests.contract_package.faceted_stand_in import MeshPart  # noqa: E402


class BareMesh(MeshPart):
    """No mesh_source."""


try:
    BareMesh()
except BaseException as error:  # noqa: B902
    print(f'BareMesh (contract package): {type(error).__name__}: {error}')
else:
    print('BareMesh (contract package): constructed')
```

`<scratch>/probe_project/pyproject.toml`:

```toml
[tool.machinome]
```

`<scratch>/probe_project/parts.py`:

```python
"""Source-bound leaves that never say which file they are."""

import os

from solid2 import cube

from machinome.node.jscad import JScadNode
from machinome.node.openscad import OpenScadNode
from machinome.node.solid2 import Solid2Node
from machinome.node.step import StepNode
from machinome.node.stl import StlNode

HERE = os.path.dirname(os.path.realpath(__file__))


class BareStl(StlNode):
    """No stl_source."""


class BareStep(StepNode):
    """No step_source."""


class BareJscad(JScadNode):
    """No jscad_source."""


class BareScad(OpenScadNode):
    """No scad_source."""


class EmptyStl(StlNode):
    stl_source = ''


class EmptyStep(StepNode):
    step_source = ''


class EmptyJscad(JScadNode):
    jscad_source = ''


class EmptyScad(OpenScadNode):
    scad_source = ''


class GhostContributor(Solid2Node):
    """Constructs, then names a tracked file that is not there, so the
    builder's 'inspect initial sources' stage is the one that fails."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.files.add(os.path.join(HERE, 'ghost.py'))

    def render(self):
        return cube(1)


class FailingPreparation(Solid2Node):
    """Loads, then fails while the builder assembles it."""

    def render(self):
        return cube(1)

    def _prepare(self, root=None):
        raise RuntimeError('preparation failed deliberately')
```

`<scratch>/probe_project/assembly.py`:

```python
"""A declarative assembly whose nested leaf lacks its declaration."""

from machinome.node.assembly import AssemblyNode

from parts import BareStl


class Arm(AssemblyNode):
    """The leaf is two levels below the root."""

    bracket = BareStl()


class Rig(AssemblyNode):
    """The model a maker builds; the faulty leaf is not its child."""

    arm = Arm()
```

`<scratch>/probe_project/markings_probe.py`:

```python
"""A marking whose artwork path is empty, or None."""

from machinome.node.markings import Marking, Svg, Wrapped
from machinome.node.solid2 import Solid2Node

for label, artwork in (('empty', ''), ('none', None)):
    try:
        class Plate(Solid2Node):
            logo = Marking(Svg(artwork),
                           Wrapped(axis=(0, 0, 1), radius=9.45, at=(0, 0, 0)),
                           color='#FFFFFF')
    except BaseException as error:  # noqa: B902
        print(f'Svg({artwork!r}): {type(error).__name__}: {error}')
    else:
        print(f'Svg({artwork!r}): class created')
```

The construction probe (` INFO -` lines filtered out), exit status 0:

```
$ env -C <scratch>/probe_project BENCH=<bench> PYTHONPATH=<bench> \
    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python <scratch>/probe_construct.py
machinome from <bench>/machinome/__init__.py
BareStl: ValueError: BareStl is an StlNode and must declare "stl_source", the path of an STL file in the same directory as the python module defining it
BareStep: ValueError: BareStep is a StepNode and must declare "step_source", the path of a STEP file in the same directory as the python module defining it
BareJscad: Exception: OpenJScadNode subclass must declare "jscad_source" property with path with a valid OpenJScad js file
BareScad: TypeError: join() argument must be str, bytes, or os.PathLike object, not 'NoneType'
EmptyStl: ValueError: EmptyStl is an StlNode and must declare "stl_source", the path of an STL file in the same directory as the python module defining it
EmptyStep: ValueError: EmptyStep is a StepNode and must declare "step_source", the path of a STEP file in the same directory as the python module defining it
EmptyJscad: Exception: OpenJScadNode subclass must declare "jscad_source" property with path with a valid OpenJScad js file
EmptyScad: ValueError: EmptyScad declares scad_source = '', resolved against <scratch>/probe_project/parts.py, but <scratch>/probe_project is not a file.
BareMesh (contract package): TypeError: join() argument must be str, bytes, or os.PathLike object, not 'NoneType'
```

The markings probe, exit status 0:

```
$ env -C <scratch>/probe_project PYTHONPATH=<bench>:<scratch>/probe_project \
    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python <scratch>/probe_project/markings_probe.py
Svg(''): ValueError: Plate declares logo = '', resolved against <scratch>/probe_project/markings_probe.py, but <scratch>/probe_project is not a file.
Svg(None): TypeError: join() argument must be str, bytes, or os.PathLike object, not 'NoneType'
```

The six builds, one at a time, `SOLID_BUILD_DIR` unset, each log
`<scratch>/build.<reference>.A-before.log` (` INFO -` lines filtered out;
each log is `INFO START` and then the one line):

```
$ env -u SOLID_BUILD_DIR -C <scratch>/probe_project PYTHONPATH=<bench> \
    PYTHONDONTWRITEBYTECODE=1 .venv/bin/machinome build <reference>
### assembly:Rig                       exit 1
ERROR -    core.builder - assembly:Rig: failed to load project: BareStl is an StlNode and must declare "stl_source", the path of an STL file in the same directory as the python module defining it
### parts:BareStl                      exit 1
ERROR -    core.builder - parts:BareStl: failed to load project: BareStl is an StlNode and must declare "stl_source", the path of an STL file in the same directory as the python module defining it
### parts:BareScad                     exit 1
ERROR -    core.builder - parts:BareScad: failed to load project: join() argument must be str, bytes, or os.PathLike object, not 'NoneType'
### parts:BareJscad                    exit 1
ERROR -    core.builder - parts:BareJscad: failed to load project: OpenJScadNode subclass must declare "jscad_source" property with path with a valid OpenJScad js file
### parts:GhostContributor             exit 1
ERROR -    core.builder - parts:GhostContributor: failed to inspect initial sources project: [Errno 2] No such file or directory: '<scratch>/probe_project/ghost.py'
### parts:FailingPreparation           exit 1
ERROR -    core.builder - parts:FailingPreparation: failed to assemble project: preparation failed deliberately
```

All as design.md's Context records.

### 1.4 The catalogue scan

Rerun as design.md, "Who reads the old texts", writes it:

```
$ grep -rIn --include=*.py --exclude-dir=_build --exclude-dir=.git \
    --exclude-dir=node_modules --exclude-dir=.venv \
    -e "must declare" -e "failed to load project" -e "failed to inspect" \
    -e "failed to assemble" -e "project: " -e "OpenJScadNode subclass" \
    -e "is an StlNode" -e "is a StepNode" -e "join() argument" \
    /home/asa/devel/machinome/projects/
```

16 791 Python files (`find /home/asa/devel/machinome/projects/ -name .git
-prune -o -name _build -prune -o -name node_modules -prune -o -name .venv
-prune -o -name '*.py' -print | wc -l`). 11 lines match, the same 11 Stage
P found, all `"project: "` false positives: four `self.wandb_project: str =
...` fields under `Robots/roboto_origin/modules/roboparty_train/`, and seven
docstrings reading `Run from the project: python -m simulation.tools....`
(`Calculators/Curta-Type-I-3x/simulation/tools/probe.py` and the same file in
four of its worktrees, `Locks/designs/simulation/tools/probe.py` and
`browser.py`). No test or code in the catalogue asserts on, matches or
catches an old text.

## 2. Red tests

Written before any code change:

- `tests/test_missing_source_file.py`, class `UndeclaredSourceTest` (its own
  scratch project per test, `leaf.py` imported under a unique module name):
  - `test_an_undeclared_source_is_refused_naming_class_attribute_and_module`
    (2.1), one subtest per adapter, `machinome.node.openscad.coherent_read`
    patched and asserted not called;
  - `test_an_empty_declaration_names_no_file` (2.2), one subtest per adapter;
  - `test_a_leaf_written_outside_the_core_refuses_it_the_same_way` (2.3),
    `BareMesh(MeshPart)` declared in the scratch `leaf.py`;
  - `test_a_declaration_given_alone_is_resolved_beside_its_module` (2.4);
- `tests/test_missing_source_file.py`, class `UndeclaredNestedBuildTest`,
  `test_a_failure_at_launch_names_the_model_and_the_step` (2.7): a scratch
  project (`parts.py` with `BareStl`, `assembly.py` with `Arm` holding it and
  `Rig` holding `Arm`), `machinome build assembly:Rig` through
  `[sys.executable, '-c', 'from machinome.cli import manage; manage()', ...]`
  with `PYTHONPATH=<repository root>`, `SOLID_BUILD_DIR` and
  `SOLID_TEST_ENGINE` removed. Its assertions run in the order exit status,
  `<project>/_build/errors.json` holds a traceback, the new line, the old
  line absent, so the red run confirms the `errors.json` path on the
  unmodified tree before it fails on the line;
- `tests/test_builder_lifecycle.py`, class `InitialFailureLineTest` (2.6),
  one test per stage, `Builder('model.py', build_dir=<temporary>,
  watch=False)._start()` under `asyncio.run` and
  `assertLogs('core.builder', level='ERROR')`, each outcome
  `BuildOutcome.FAILED` and the logged ERROR lines equal to the one expected
  line. All three stages were reached with the patches tasks.md names (the
  inspect stage through `PropertyMock` on the `Mock` node's own type).

### 2.8 The red run, unmodified code

```
$ pytest -q -p no:cacheprovider tests/test_missing_source_file.py \
    tests/test_builder_lifecycle.py::InitialFailureLineTest
14 failed, 26 passed in 5.39s                    (exit 1)
```

The 14 failures are the six RED tests and the eight subtests of 2.1 and 2.2;
the 26 passing are every existing test of `test_missing_source_file.py`
(2.5, the guard). The failure line of each RED case:

```
2.1 stl_source   AssertionError: '/tmp/machinome_undeclared_source_do2d_ppu/leaf.py' not found in 'BareStl is an StlNode and must declare "stl_source", the path of an STL file in the same directory as the python module defining it'
2.1 step_source  AssertionError: '/tmp/machinome_undeclared_source_do2d_ppu/leaf.py' not found in 'BareStep is a StepNode and must declare "step_source", the path of a STEP file in the same directory as the python module defining it'
2.1 jscad_source AssertionError: <class 'Exception'> is not <class 'ValueError'> : Exception('OpenJScadNode subclass must declare "jscad_source" property with path with a valid OpenJScad js file')
2.1 scad_source  AssertionError: <class 'TypeError'> is not <class 'ValueError'> : TypeError("join() argument must be str, bytes, or os.PathLike object, not 'NoneType'")
2.2 stl_source   AssertionError: "= ''" not found in 'EmptyStl is an StlNode and must declare "stl_source", the path of an STL file in the same directory as the python module defining it'
2.2 step_source  AssertionError: "= ''" not found in 'EmptyStep is a StepNode and must declare "step_source", the path of a STEP file in the same directory as the python module defining it'
2.2 jscad_source AssertionError: <class 'Exception'> is not <class 'ValueError'> : Exception('OpenJScadNode subclass must declare "jscad_source" property with path with a valid OpenJScad js file')
2.2 scad_source  AssertionError: 'names no file' not found in "EmptyScad declares scad_source = '', resolved against /tmp/machinome_undeclared_source_8jtcqyjs/leaf.py, but /tmp/machinome_undeclared_source_8jtcqyjs is not a file."
2.3              AssertionError: <class 'TypeError'> is not <class 'ValueError'> : TypeError("join() argument must be str, bytes, or os.PathLike object, not 'NoneType'")
2.4              TypeError: require_source_file() missing 1 required positional argument: 'path'
2.6 load         AssertionError: Lists differ: ['model.py: failed to load project: broken model'] != ['The model model.py could not be loaded: broken model']
2.6 inspect      AssertionError: Lists differ: ['model.py: failed to inspect initial sources project: [Errno 2] No such file or directory: '/nowhere/ghost.py''] != ['The sources of the model model.py could not be read: [Errno 2] No such file or directory: '/nowhere/ghost.py'']
2.6 assemble     AssertionError: Lists differ: ['model.py: failed to assemble project: preparation failed deliberately'] != ['The model model.py could not be assembled: preparation failed deliberately']
2.7              AssertionError: 'The model assembly:Rig could not be loaded: BareStl does not declare stl_source' not found in ' INFO -    core.builder - START\nERROR -    core.builder - assembly:Rig: failed to load project: BareStl is an StlNode and must declare "stl_source", the path of an STL file in the same directory as the python module defining it\n'
```

2.4's first call raises `TypeError` (the missing argument), so its second
assertion (that the four-argument form returns `None` today) is not reached;
tasks.md names both.

2.5's other half, `<focused-b>` on the unmodified tree, is 1.2's
`2 passed, 96 deselected`.

## 3. The change

- 3.1 `machinome/node/sources.py`: `_undeclared(klass, attribute, declared,
  declaring)` beside `require_source_file`, and `require_source_file(klass,
  attribute, declared, path=None)` as design.md, Decisions 1 and 2: the
  undeclared refusal first (`if not declared`), then, when `path` is `None`,
  `os.path.realpath(os.path.join(os.path.dirname(module.__file__),
  declared))`, then containment and existence unchanged; it returns the path
  it judged where it returned `None`. Its docstring describes both forms and
  names the change. 2.4 alone:
  `1 passed in 2.58s`.
- 3.2 The four adapters. `StlNode.__init__` and `StepNode.__init__` keep
  `module` and `wrapper` (for `source_closure`) and take
  `self.stl_source = require_source_file(self.__class__, 'stl_source',
  self.stl_source)` (`step_source` alike); `JScadNode.__init__` is the one
  call for `jscad_source`; `OpenScadNode.__init__` keeps `scad_source` as
  declared and stores the call's result in `openscad_source`. Their own
  guards, joins and `declared` locals are gone, and with them the imports
  nothing else read: `sys` in `machinome/node/jscad.py`, `os` and `sys` in
  `machinome/node/openscad/__init__.py` (flake8 F401 on each after the
  edit; `grep -rn "node\.openscad\.\(os\|sys\)\|node\.jscad\.\(os\|sys\)"`
  over `machinome/` and `tests/` finds no patch of them). 2.1, 2.2 and the
  2.5 guards of `tests/test_missing_source_file.py`
  (`MissingSourceFileTest`, `ForeignScratchSourceTest`, `ContainmentTest`,
  `ScratchContainmentTest`, `UndeclaredSourceTest`): `1 failed, 27 passed,
  8 subtests passed in 2.71s`, the one failure 2.3, which waits for 3.3.
- 3.3 `tests/contract_package/faceted_stand_in.py`: `MeshPart.__init__` is
  `self.mesh_source = require_source_file(type(self), 'mesh_source',
  self.mesh_source)`; its unused `sys` import is gone and the module
  docstring's sentence on resolution says one call resolves the file beside
  the declaring module or refuses the leaf. `UndeclaredSourceTest`,
  `tests/test_leaf_contract_mesh.py` and `tests/test_leaf_contract_reach.py`
  (which checks the stand-ins import only declared core modules):
  `15 passed, 28 subtests passed in 4.72s`; `<focused-b>`:
  `2 passed, 96 deselected in 2.89s`.
- 3.4 `machinome/core/builder.py`: the module constant `_INITIAL_FAILURE`
  under `logger`, mapping `'load'`, `'inspect initial sources'` and
  `'assemble'` to the line's head, and in `_on_reload_exception`
  `logger.error(f'{_INITIAL_FAILURE[stage].format(self.path)}: {exc}')`.
  The three stage words `_start` passes are unchanged (they are the only
  callers: `builder.py:342`, `:366`, `:497`); the reload branch is
  untouched. 2.6 and 2.7: `4 passed in 4.96s`.
- 3.5 `grep -rIn --include=*.py 'OpenJScadNode subclass\|the path of an STL
  file in the same\|the path of a STEP file in the same\|failed to
  {stage}\|os.path.join(basedir' machinome/`: nothing, exit 1 (without
  `-I --include=*.py` the only hits are three stale `__pycache__/*.pyc`
  binaries). `grep -rn "require_source_file(" machinome/
  tests/contract_package/`:

  ```
  machinome/node/jscad.py:28:        self.jscad_source = require_source_file(self.__class__, 'jscad_source',
  machinome/node/step.py:491:        self.step_source = require_source_file(self.__class__, 'step_source',
  machinome/node/stl.py:138:        self.stl_source = require_source_file(self.__class__, 'stl_source',
  machinome/node/sources.py:142:def require_source_file(klass, attribute, declared, path=None):
  machinome/node/openscad/__init__.py:64:        self.openscad_source = require_source_file(
  machinome/node/markings.py:207:        require_source_file(owner, attribute, self.path, path)
  tests/contract_package/faceted_stand_in.py:38:        self.mesh_source = require_source_file(type(self), 'mesh_source',
  ```

  The four adapters and `MeshPart` in the resolving form (three arguments),
  `Svg.resolve` in the four-argument form.
- 3.6 The focused sets after the change, every existing test unedited:

  ```
  $ pytest -q -p no:cacheprovider <focused-a>
  79 passed, 15 subtests passed in 11.92s        (wall 13.02 s)
  $ pytest -q -p no:cacheprovider <focused-b>
  2 passed, 96 deselected in 2.80s               (wall 3.77 s)
  ```

  79 = 1.2's 71 and the eight new tests; 15 subtests = 7 and the eight new.

## 4. Framework validation

### 4.1 Lint

The nine touched Python files (`machinome/core/builder.py`,
`machinome/node/jscad.py`, `machinome/node/openscad/__init__.py`,
`machinome/node/sources.py`, `machinome/node/step.py`,
`machinome/node/stl.py`, `tests/contract_package/faceted_stand_in.py`,
`tests/test_builder_lifecycle.py`, `tests/test_missing_source_file.py`),
on the working tree and as they are at HEAD (extracted with `git show
HEAD:<file>` into `<scratch>/head/`, beside HEAD's `setup.cfg` so its
`[flake8]` per-file ignores apply the same way):

- `flake8 --max-line-length=89` (pyenv shim, 7.3.0): 22 findings at HEAD
  and 22 after, the same ones by file and code (compared with line numbers
  stripped, `diff` exit 0): `builder.py` E303 and F401 (`DOCUMENT_FORMAT`),
  `openscad/__init__.py` E501 (92 columns, the `render` refusal), 18 E128
  in `step.py`, one E127 in `test_builder_lifecycle.py`, all pre-existing.
  The first runs after the change found E501 on lines of this change in
  `faceted_stand_in.py`'s docstring; the paragraph was rewrapped, and the
  run above is after that.
- `black --check` (26.5.1): all nine files "would reformat" at HEAD and
  after. None of them follows black at any line length: `black -S -t py311
  --diff` at `-l 89` changes 219 lines of `builder.py` at HEAD and 219
  after, and every file has a diff at HEAD. The new code is written in the
  files' own style (visual-indent continuation lines, closing bracket on the
  last line, single quotes), so black's diff grows in `sources.py` (35 to
  47 lines at `-l 89`) and in the two test files by that style alone; in
  the four adapters and `faceted_stand_in.py` it shrinks with the removed
  lines.

### 4.2 The probes and the six builds after the change

The construction probe, as in 1.3, exit status 0:

```
machinome from <bench>/machinome/__init__.py
BareStl: ValueError: BareStl does not declare stl_source. Set stl_source in <scratch>/probe_project/parts.py to the path of the file its part is read from, relative to that module's directory or absolute.
BareStep: ValueError: BareStep does not declare step_source. Set step_source in <scratch>/probe_project/parts.py to the path of the file its part is read from, relative to that module's directory or absolute.
BareJscad: ValueError: BareJscad does not declare jscad_source. Set jscad_source in <scratch>/probe_project/parts.py to the path of the file its part is read from, relative to that module's directory or absolute.
BareScad: ValueError: BareScad does not declare scad_source. Set scad_source in <scratch>/probe_project/parts.py to the path of the file its part is read from, relative to that module's directory or absolute.
EmptyStl: ValueError: EmptyStl declares stl_source = '', which names no file. Set stl_source in <scratch>/probe_project/parts.py to the path of the file its part is read from, relative to that module's directory or absolute.
EmptyStep: ValueError: EmptyStep declares step_source = '', which names no file. Set step_source in <scratch>/probe_project/parts.py to the path of the file its part is read from, relative to that module's directory or absolute.
EmptyJscad: ValueError: EmptyJscad declares jscad_source = '', which names no file. Set jscad_source in <scratch>/probe_project/parts.py to the path of the file its part is read from, relative to that module's directory or absolute.
EmptyScad: ValueError: EmptyScad declares scad_source = '', which names no file. Set scad_source in <scratch>/probe_project/parts.py to the path of the file its part is read from, relative to that module's directory or absolute.
BareMesh (contract package): ValueError: BareMesh does not declare mesh_source. Set mesh_source in <scratch>/probe_construct.py to the path of the file its part is read from, relative to that module's directory or absolute.
```

(`BareMesh` is defined in `probe_construct.py` itself, so that is the
module it names.) The markings probe, exit status 0:

```
Svg(''): ValueError: Plate declares logo = '', which names no file. Set logo in <scratch>/probe_project/markings_probe.py to the path of the file its part is read from, relative to that module's directory or absolute.
Svg(None): TypeError: join() argument must be str, bytes, or os.PathLike object, not 'NoneType'
```

`Svg(None)` is unchanged, as design.md's Decision 3 and the proposal's
"Deliberately out" say. The six builds, one at a time, as in 1.3, logs
`<scratch>/build.<reference>.A-after.log`:

```
### assembly:Rig                       exit 1
ERROR -    core.builder - The model assembly:Rig could not be loaded: BareStl does not declare stl_source. Set stl_source in <scratch>/probe_project/parts.py to the path of the file its part is read from, relative to that module's directory or absolute.
### parts:BareStl                      exit 1
ERROR -    core.builder - The model parts:BareStl could not be loaded: BareStl does not declare stl_source. Set stl_source in <scratch>/probe_project/parts.py to the path of the file its part is read from, relative to that module's directory or absolute.
### parts:BareScad                     exit 1
ERROR -    core.builder - The model parts:BareScad could not be loaded: BareScad does not declare scad_source. Set scad_source in <scratch>/probe_project/parts.py to the path of the file its part is read from, relative to that module's directory or absolute.
### parts:BareJscad                    exit 1
ERROR -    core.builder - The model parts:BareJscad could not be loaded: BareJscad does not declare jscad_source. Set jscad_source in <scratch>/probe_project/parts.py to the path of the file its part is read from, relative to that module's directory or absolute.
### parts:GhostContributor             exit 1
ERROR -    core.builder - The sources of the model parts:GhostContributor could not be read: [Errno 2] No such file or directory: '<scratch>/probe_project/ghost.py'
### parts:FailingPreparation           exit 1
ERROR -    core.builder - The model parts:FailingPreparation could not be assembled: preparation failed deliberately
```

Every shape is design.md's Decisions 2 and 4.

## 5. Words

- 5.1 `grep -rn "must declare\|failed to\|require_source_file\|does not
  declare" docs/ --include=*.rst --include=*.md`, outside `docs/adrs/`:
  four hits, none about this change — `docs/architecture.md:2764` (a
  document naming an id its table does not declare),
  `docs/concepts/running.rst:101` and `:105` (running declarations), and
  `docs/project/changelog.rst:436` (the build root). No manual page states
  the refusal of an undeclared source, quotes an old text or the builder's
  line, or documents `require_source_file`; `docs/reference/api.rst`'s
  "Leaf nodes" section lists the leaf bases' members and not
  `machinome.node.sources`, and its `scad_source`, `jscad_source` and
  `stl_source` entries, like `docs/howto/backends.rst` and
  `docs/howto/imported-parts.rst`, state the declared-but-absent and
  outside-the-project refusals only. Nothing was changed.
- 5.2 `docs/project/changelog.rst`: one bullet at the end of the existing
  `Unreleased` section, "A leaf that names no source file is refused in one
  shape.", naming `refuse-the-undeclared-file-by-name`.
  `pytest -q -p no:cacheprovider tests/test_release_records.py`:
  `9 passed, 58 subtests passed in 0.14s`.

## 6. Findings record

- 6.1 The whole section "name-the-missing-file (2026-09-15, found while
  fixing)" of `workflow/warts.md`, its introduction and both entries, moved
  verbatim to `workflow/archive/fix-warts-3-2026-10-06/resolved.md` under
  `## \`refuse-the-undeclared-file-by-name\``, with a "What shipped"
  paragraph, and deleted from `warts.md`.
- 6.2 Open Question 2 was answered at ratification as "left as it is, not
  recorded": no `warts.md` entry.
- 6.3 `workflow/ongoing/fix-warts-3.md`, "Progress": one line for this
  cycle, after cycle 11's.

## 7. Sync and archive

- 7.1 `openspec archive refuse-the-undeclared-file-by-name --yes`
  (openspec 1.6.0), the CLI's own sync: "Specs to update: build-pipeline,
  leaf-contract, node-model, step-import, stl-import: update", each "~ 1
  modified", "Totals: + 0, ~ 5, - 0, → 0", "Change
  'refuse-the-undeclared-file-by-name' archived as
  '2026-10-07-refuse-the-undeclared-file-by-name'". Its warnings: the Why
  section's length, and 25 of 29 tasks complete (4.3 and 7.1 to 7.3, done
  after it and ticked in the archived copy). Checked by script: each of
  the five requirements appears once in its baseline spec, its synced text
  equals the delta's (blank lines aside), and no scenario title is
  duplicated in any of the five specs; the scenarios are 10 (`node-model`,
  7 carried and 3 added), 5 (`leaf-contract`, 4 and 1), 8 (`stl-import`), 8
  (`step-import`) and 5 (`build-pipeline`, 4 and 1).
- 7.2 `openspec validate --specs`: `Totals: 45 passed, 0 failed (45
  items)`. The archived folder is
  `openspec/changes/archive/2026-10-07-refuse-the-undeclared-file-by-name/`.
- 7.3 The focused sets on the final tree:

  ```
  $ pytest -q -p no:cacheprovider <focused-a>
  79 passed, 15 subtests passed in 11.73s        (wall 12.84 s)
  $ pytest -q -p no:cacheprovider <focused-b>
  2 passed, 96 deselected in 2.92s               (wall 3.85 s)
  $ pytest -q -p no:cacheprovider tests/test_release_records.py tests/test_leaf_contract_reach.py
  14 passed, 78 subtests passed in 0.38s
  ```

### 4.3 The full suite

`pytest -q -p no:cacheprovider` at the bench root, alone (`ps` showed no
run of ours), log `<scratch>/full-suite.log`:

```
FAILED tests/test_core_names_no_scad.py::TheCoreNamesNoScadTest::test_no_module_outside_the_allowed_zones_holds_the_word
1 failed, 4725 passed, 4 skipped, 55 warnings, 6673 subtests passed in 638.97s (0:10:38)   (exit 1, wall 641 s)
```

The failure was this change's: `require_source_file`'s new docstring named
`OpenScadNode` in `machinome/node/sources.py`, a module outside the zones
allowed to hold that word (`{'machinome/node/sources.py': (1, [(143,
'"""Admit a leaf\'s declared source file, ...')])} != {}`). The name was
taken out of the docstring's list of callers ("`StlNode`, `StepNode`,
`JScadNode`, and a node package's own", as it read before), and the
paragraph rewrapped. Then `tests/test_core_names_no_scad.py`: `5 passed, 15
subtests passed in 0.57s`; `<focused-a>`: `79 passed, 15 subtests passed in
11.65s`; `flake8 --max-line-length=89 machinome/node/sources.py`: exit 0.

The full suite again, alone, log `<scratch>/full-suite.2.log`:

```
4726 passed, 4 skipped, 55 warnings, 6673 subtests passed in 641.63s (0:10:41)   (exit 0, wall 644 s)
```

Everything is left uncommitted.
