## Context

### Reproduction at `bad5ebe`

Bench `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch
`fix-warts-3`, `git rev-parse HEAD` = `bad5ebefcba8a6e79fc876a3d30975ac020640c9`,
clean tree. `python -c 'import machinome; print(machinome.__file__)'` under
`PYTHONPATH=<bench>` prints `<bench>/machinome/__init__.py`.

The fixture is a scratch project in the campaign scratchpad,
`<scratch>` = `/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle12`:
`<scratch>/probe_project/pyproject.toml` (`[tool.machinome]` alone),
`parts.py` (a subclass of each adapter declaring nothing — `BareStl`,
`BareStep`, `BareJscad`, `BareScad` — one of each declaring `''` —
`EmptyStl`, `EmptyStep`, `EmptyJscad`, `EmptyScad` — a `Solid2Node`
`GhostContributor` that adds a missing `ghost.py` to its `files` after
construction, and a `Solid2Node` `FailingPreparation` whose `_prepare`
raises `RuntimeError('preparation failed deliberately')`), `assembly.py`
(`Rig` holds `arm = Arm()`, `Arm` holds `bracket = BareStl()`) and
`markings_probe.py` (a `Solid2Node` with `Marking(Svg(''), ...)` and with
`Svg(None)`). `<scratch>/probe_construct.py` constructs each leaf of
`parts.py`, and a subclass `BareMesh` of the leaf-contract stand-in
`tests.contract_package.faceted_stand_in.MeshPart` declaring no
`mesh_source`, and prints what each raises. The applier copies every probe
source into `evidence.md` (tasks.md 1.3): the scratchpad is not durable.

```text
$ env -C <scratch>/probe_project BENCH=<bench> PYTHONPATH=<bench> \
    /home/asa/devel/machinome/.venv/bin/python <scratch>/probe_construct.py
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

$ env -C <scratch>/probe_project PYTHONPATH=<bench>:<scratch>/probe_project \
    /home/asa/devel/machinome/.venv/bin/python <scratch>/probe_project/markings_probe.py
Svg(''): ValueError: Plate declares logo = '', resolved against <scratch>/probe_project/markings_probe.py, but <scratch>/probe_project is not a file.
Svg(None): TypeError: join() argument must be str, bytes, or os.PathLike object, not 'NoneType'
```

Where each comes from: `StlNode.__init__` guards `if not self.stl_source`
(`machinome/node/stl.py:136`) and `StepNode.__init__` the same
(`step.py:489`), each with its own text; `JScadNode.__init__` raises a bare
`Exception` with a text written when the class was called `OpenJScadNode`
(`jscad.py:29`); `OpenScadNode.__init__` has no guard and joins first
(`openscad/__init__.py:70`). All four then call
`require_source_file(klass, attribute, declared, path)`
(`machinome/node/sources.py:129`) on the path they joined, so the shared
admission never sees an undeclared source: for `None` the adapter's join
raises first, and for `''` the join yields the module's own directory,
which `require_source_file` refuses as "not a file". `MeshPart`, written
outside `machinome/` as a node package's leaf would be, follows the same
pattern and fails as `OpenScadNode` does.

`machinome build` on the same project, one model at a time (each run
alone, exit status 1 for all six):

```text
$ env -C <scratch>/probe_project PYTHONPATH=<bench> \
    /home/asa/devel/machinome/.venv/bin/machinome build <reference>
### assembly:Rig
ERROR -    core.builder - assembly:Rig: failed to load project: BareStl is an StlNode and must declare "stl_source", the path of an STL file in the same directory as the python module defining it
### parts:BareStl
ERROR -    core.builder - parts:BareStl: failed to load project: BareStl is an StlNode and must declare "stl_source", the path of an STL file in the same directory as the python module defining it
### parts:BareScad
ERROR -    core.builder - parts:BareScad: failed to load project: join() argument must be str, bytes, or os.PathLike object, not 'NoneType'
### parts:BareJscad
ERROR -    core.builder - parts:BareJscad: failed to load project: OpenJScadNode subclass must declare "jscad_source" property with path with a valid OpenJScad js file
### parts:GhostContributor
ERROR -    core.builder - parts:GhostContributor: failed to inspect initial sources project: [Errno 2] No such file or directory: '<scratch>/probe_project/ghost.py'
### parts:FailingPreparation
ERROR -    core.builder - parts:FailingPreparation: failed to assemble project: preparation failed deliberately
```

Each log is `INFO START` and then that one line; the traceback goes to
`_build/errors.json`. The line is `Builder._on_reload_exception`'s, on the
initial (not reload) path (`machinome/core/builder.py:531`):
`logger.error(f'{self.path}: failed to {stage} project: {exc}')`, where
`self.path` is the resolved model reference `machinome build` hands its
builder (`manager/build.py`, `selection.reference`) and `stage` is one of
the three words `_start` passes: `'load'` around `load_node` (`:332`),
`'inspect initial sources'` around the first read of `mtime_ns` (`:356`),
and `'assemble'` around `_prepare` (`:487`). On a watch reload the same
method logs the whole traceback instead and starts the broad recovery
watch; that path is not changed.

### Who reads the old texts

```text
$ grep -rIn --include=*.py --exclude-dir=_build --exclude-dir=.git \
    --exclude-dir=node_modules --exclude-dir=.venv \
    -e "must declare" -e "failed to load project" -e "failed to inspect" \
    -e "failed to assemble" -e "project: " -e "OpenJScadNode subclass" \
    -e "is an StlNode" -e "is a StepNode" -e "join() argument" \
    /home/asa/devel/machinome/projects/
```

16 791 Python files (`find ... -name '*.py'`, builds and Git directories
excluded); 11 lines match, all `"project: "` false positives (a
`wandb_project: str` field, and "Run from the project:" in docstrings). No
test or code in the catalogue asserts on, matches or catches any old text,
and none catches the `TypeError` an undeclared `scad_source` raises (a grep
for `except TypeError` / `assertRaises(TypeError` in files naming a
`*_source` finds nothing). The workspace's `scripts/` and `skills/`, the
studio's `floor/`, `shop-skills/` and `profiles/`, and the viewer package
quote none of them. On the bench, `tests/test_stl_node.py:187` and
`tests/test_step_node.py:236` (`test_a_missing_declaration_fails_naming_the_class`)
assert `Exception` with the class name and the attribute in the message, and
no test asserts on the builder's line.

### Focused tests at `bad5ebe`

`pytest -q -p no:cacheprovider tests/test_missing_source_file.py
tests/test_builder_lifecycle.py tests/test_leaf_contract_mesh.py
tests/test_builder_reload_resilience.py`: 71 passed, 7 subtests passed,
9.84 s (11.0 s wall). `pytest -q -p no:cacheprovider tests/test_stl_node.py
tests/test_step_node.py -k missing_declaration`: 2 passed, 96 deselected,
3.00 s.

## Goals / Non-Goals

**Goals:**

- One refusal for a source attribute that names no file, the same
  exception and the same words for every source-bound leaf, naming the
  class, the attribute and the module the declaration belongs in, made
  before anything is resolved, read or run.
- The refusal made in one place that the documented pattern for a leaf
  written outside the core reaches before it can fail on its own.
- A builder line a reader can act on: what the builder was doing with
  which model, then the failure's own message.

**Non-Goals:**

- Naming the faulty leaf's position in the tree; the class is where the
  declaration is written (proposal, "Deliberately out").
- Any change to the declared-but-absent, not-a-file or outside-the-project
  refusals, to `errors.json`, or to the reload path.
- A new public name.

## Decisions

### 1. `require_source_file` makes the refusal, and resolves a declaration given alone

`require_source_file` is already the leaf contract's declared admission for
a source file (`leaf-contract`, "A leaf states its source identity through
declared members"; ADR-163) and already receives the declared value. It
refuses a value that names no file as its first step. To reach it before
the join that fails on `None`, it also takes the join: `path` becomes
optional.

```python
def require_source_file(klass, attribute, declared, path=None):
    module = sys.modules.get(klass.__module__)
    declaring = getattr(module, '__file__', None)
    if not declared:
        raise _undeclared(klass, attribute, declared, declaring)
    if path is None:
        path = os.path.realpath(
            os.path.join(os.path.dirname(module.__file__), declared))
    if declaring:
        _require_inside_project(klass, attribute, declared, path,
                                os.path.realpath(declaring))
    if os.path.isfile(path):
        return path
    ...  # the not-a-file and does-not-exist refusals, unchanged
```

The resolution is the one each of the four adapters performs today,
character for character: `os.path.realpath(os.path.join(os.path.dirname(module.__file__), declared))`,
with `module = sys.modules[klass.__module__]`; an absolute declaration
still resolves to itself. Containment and existence are judged on the
resolved path exactly as before, in the same order. It returns the path it
judged in both forms (today it returns `None`, which no caller reads).

The four adapters drop their guard and their join:

```python
# StlNode.__init__ (StepNode alike, with step_source)
module = sys.modules[self.__class__.__module__]
wrapper = os.path.realpath(module.__file__)
self.stl_source = require_source_file(self.__class__, 'stl_source',
                                      self.stl_source)
# JScadNode.__init__
self.jscad_source = require_source_file(self.__class__, 'jscad_source',
                                        self.jscad_source)
# OpenScadNode.__init__ (scad_source keeps the declared value)
self.openscad_source = require_source_file(self.__class__, 'scad_source',
                                           self.scad_source)
```

`StlNode` and `StepNode` keep `wrapper` for `source_closure`. `OpenScadNode`
keeps reading the module for nothing else and can drop `basedir`. The
contract stand-in `MeshPart` (`tests/contract_package/faceted_stand_in.py`)
takes the same one call, since it is the documented example of a leaf a
node package writes.

Alternatives considered:

- **A private helper each core adapter calls before its join, and the
  same check first in the four-argument `require_source_file`.** No
  contract change, and the four core adapters agree. But a leaf written
  outside the core in the documented pattern still joins `None` itself and
  raises `TypeError` before reaching the check, as `MeshPart` does
  today; a fifth adapter gets the refusal only if it knows to call a
  private function. This is the fallback if Open Question 1 is answered
  against the optional argument.
- **A new public function** (`resolve_source_file`, say) beside
  `require_source_file`. The same effect as the decision, with a second
  declared name for one admission; the contract has no need of two.
- **Keeping each adapter's own guard and rewording the four texts alike.**
  Four copies of one sentence, and the next adapter writes a fifth or none,
  which is how the finding came about.

### 2. The words of the refusal

```python
def _undeclared(klass, attribute, declared, declaring):
    """The refusal of a source attribute that names no file."""
    where = f' in {os.path.realpath(declaring)}' if declaring else ''
    if declared is None:
        head = f'{klass.__name__} does not declare {attribute}.'
    else:
        head = (f'{klass.__name__} declares {attribute} = {declared!r}, '
                f'which names no file.')
    return ValueError(
        f'{head} Set {attribute}{where} to the path of the file it is '
        f'is read from, relative to that module\'s directory or absolute.')
```

Measured shapes the applier confirms (tasks.md 4.2):

```text
BareStl does not declare stl_source. Set stl_source in <scratch>/probe_project/parts.py to the path of the file it is read from, relative to that module's directory or absolute.
EmptyScad declares scad_source = '', which names no file. Set scad_source in <scratch>/probe_project/parts.py to the path of the file it is read from, relative to that module's directory or absolute.
```

(Revised at the orchestrator's review of the implementation, 7 October
2026: the sentence read "the file its part is read from", which a
marking's `Svg('')` also reaches, and a marking's file is its artwork;
"the file it is read from" serves both. The `JScadNode` and
`OpenScadNode` class docstrings, which still stated the old
same-directory rule the removed error texts had, were corrected in the
same review.)

`ValueError`, as `StlNode` and `StepNode` raise today and as the
not-a-file and outside-the-project refusals raise: a declaration to
correct, not an absent file, so not `FileNotFoundError`. `None` and `''`
read differently because one was never declared and the other was declared
empty; any other falsy value reads as the second. No `.filename` is set:
there is no foreign file for reload repair to watch, and the fix is an
edit of Python source, which the broad recovery watch a load failure
starts is there to notice. The module named is the one defining the
class, the one `require_source_file` already resolves against and names in
its other refusals ("resolved against <module>"). It does not repeat the
adapter's kind ("an StlNode"): the attribute already says which file is
meant, and the text stays one for every caller.

### 3. Every caller of `require_source_file` gets the refusal

The check sits in both forms, so a caller that resolves its own path and
passes a falsy declaration is refused in the same words. The callers on
this tree are the four adapters, `MeshPart`, and `Svg.resolve` in
`machinome/node/markings.py`. For a marking, `Svg('')` is today refused as
"Plate declares logo = '', resolved against …, but <its directory> is not
a file." and becomes "Plate declares logo = '', which names no file. Set
logo in … to …"; `Svg(None)` still fails in `Svg.resolve`'s own join,
outside this change (proposal, "Deliberately out"). The marking code is
not edited.

### 4. The builder's line names the model and the step

```python
#: What the builder was doing with the model when an initial failure
#: stopped it, by the stage `_start` names: the head of the one line
#: `_on_reload_exception` logs.
_INITIAL_FAILURE = {
    'load': 'The model {} could not be loaded',
    'inspect initial sources': 'The sources of the model {} could not be read',
    'assemble': 'The model {} could not be assembled',
}
...
logger.error(f'{_INITIAL_FAILURE[stage].format(self.path)}: {exc}')
```

The three stage words stay as `_start` passes them (they are private and
nothing else reads them), so only the line changes. Measured shapes:

```text
The model assembly:Rig could not be loaded: BareStl does not declare stl_source. Set stl_source in <scratch>/probe_project/parts.py to ...
The sources of the model parts:GhostContributor could not be read: [Errno 2] No such file or directory: '<scratch>/probe_project/ghost.py'
The model parts:FailingPreparation could not be assembled: preparation failed deliberately
```

`self.path` is what the builder was asked to build — a declared model's
reference or the command's argument — so it is named as the model, not as
the node that failed; the inner message names the node, and for the
refusals this change and `name-the-missing-file` made it names the leaf's
class and the module where the declaration belongs. The exception's type
is not added (proposal, "Deliberately out").

### 5. No ADR; the leaf contract version stays 3

`leaf-contract` requires the version `CONTRACT` to change with "a change to
the meaning of a declared member, or the removal or renaming of one". The
four-argument call keeps its meaning: it judges the path it is given, in
the same order, with the same refusals; the one difference is that a
declared value that names no file is refused as such rather than as "not a
file" — the same exception type, and a case no leaf could have relied on
to construct. The optional fourth argument and the return value are
additions. A leaf declaring `leaf_contract = 3` keeps loading. The decision
belongs in the `leaf-contract` and `node-model` specs, not an ADR: no
architecture moves.

### 6. The specs

Five MODIFIED requirements, each carried whole with every scenario:

- `node-model`, "A source-bound leaf names its missing file": a paragraph
  for the undeclared source and three scenarios (an undeclared attribute on
  each of the four adapters, an empty declaration, a leaf written outside
  the core).
- `leaf-contract`, "A leaf states its source identity through declared
  members": `require_source_file` resolves a declaration given alone and
  returns the path, and refuses an undeclared source; one scenario.
- `stl-import`, "STL source declaration and freshness", and `step-import`,
  "STEP source declaration and freshness": the sentence "A subclass without
  `…_source` SHALL fail at construction with an error naming the class"
  states the exception and its contents; the scenario "A missing
  declaration fails at construction" says `ValueError` and names the
  module.
- `build-pipeline`, "File-based build error propagation": the initial-launch
  line; one scenario.

### 7. Manual and changelog

No manual page states the refusal of an undeclared source, quotes one of
the four old texts, quotes the builder's line, or documents
`require_source_file`'s signature (`grep -rn "must declare\|failed to\|require_source_file" docs/ --include=*.rst`
outside `docs/adrs/` finds only an unrelated changelog line). The
`api.rst` attribute entries for `stl_source`, `scad_source` and
`jscad_source` describe the attribute, not its absence, and stay. The
changelog takes one bullet under `Unreleased`, naming the change.

## Risks / Trade-offs

- A caller that passed `''` to the four-argument form to mean "the
  module's directory" would now be refused differently. None does: the
  callers on this tree are listed in Decision 3, and a directory is refused
  as not a file anyway.
- A leaf outside the core that keeps the four-argument form and joins
  `None` itself still raises `TypeError`. The resolving form is the way out
  of it, shown by `MeshPart`; nothing forces a package to adopt it.
- The resolving form reads `module.__file__` exactly as the adapters did,
  so a class defined in a module with no file fails in the same way as
  before (an `AttributeError`), not with a new refusal.

## Migration Plan

None. No project declares a source attribute empty or leaves it undeclared
and builds today; a project that did was already refused. A node package
may keep its four-argument call.

## Open Questions

1. **The optional fourth argument of a declared member** (Decision 1). The
   finding asks that the refusal be "raised where `require_source_file` is
   reached or beside it, so a fifth adapter gets it for free"; only a
   resolving form reached before any join gives that to a leaf written
   outside the core. Recommendation: the optional argument, as designed,
   with `CONTRACT` unchanged (Decision 5). If the orchestrator or the pilot
   prefers no change to a declared member's signature, the fallback is
   Decision 1's first alternative: a private helper the four core adapters
   call before their join, the same check in the four-argument form, no
   change to `MeshPart`, and a `warts.md` entry recording that a package
   leaf joining `None` still raises `TypeError`. Answered by the
   orchestrator at ratification (7 October 2026): the optional argument,
   `CONTRACT` unchanged.
2. **The builder's line for an exception with an empty or bare message**
   (`KeyError('x')` reads `... could not be loaded: 'x'`). Left as it is;
   recorded in `warts.md` by the applier only if the orchestrator asks.
   Answered at ratification (7 October 2026): left as it is, not recorded.
