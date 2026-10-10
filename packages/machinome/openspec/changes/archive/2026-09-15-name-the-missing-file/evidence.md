# Evidence — name the missing file

Everything below was measured on this worktree (`fix-warts`, head `55d16e7`)
with `PYTHONPATH=$PWD` and `/home/asa/devel/libresolid-studio/.venv`, before
any change to the framework. Reproduce the whole of it with

    sh openspec/changes/name-the-missing-file/evidence/run-probes.sh

`<WT>` below stands for
`/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts`; the transcript
is otherwise verbatim, and the run leaves no build tree behind.

## The fixture

`evidence/probe_project/` is a real Solid project (its own
`pyproject.toml` with `[tool.solid-node]`) whose `parts.py` declares one leaf
per source-bound adapter with a file that is not there —

    MissingStl    (StlNode,      stl_source   = 'absent.stl')
    MissingStep   (StepNode,     step_source  = 'absent.step')
    MissingJscad  (JScadNode,    jscad_source = 'absent.js')
    MissingScad   (OpenScadNode, scad_source  = 'absent.scad')

— two whose declared source exists but is a directory (`DirectoryStl`,
`DirectoryStep`, both naming `a_directory`), one that reproduces the suite's
own vanishing-source fixture (`VanishingJscad`), one out-of-scope probe
(`BareScad`, declaring no `scad_source` at all), and `assembly.py`, a
declarative `AssemblyNode` (`Rig`) that declares `MissingStl` as a child.

## The probes

| probe | question |
| --- | --- |
| `probe_when.py` | at which moment — class definition, instantiation, `mtime_ns` — does each adapter notice? |
| `probe_declarative.py` | where does it bite in a declarative model, and what does a directory do? |
| `probe_vanishing.py` | the suite's own fixture that deletes its source inside `__init__` |
| `probe_bare.py` | out of scope: `OpenScadNode` with no `scad_source` |
| `solid build` × 5 | what the maker actually sees |

## What was measured

1. **Class definition constructs nothing, and no adapter checks its file.**
   Importing the module succeeds. `MissingStl`, `MissingStep` and
   `MissingJscad` then all CONSTRUCT successfully with no file on disk; the
   failure arrives from `base.py:1039` when `mtime_ns` is read, as a bare
   `FileNotFoundError` naming only the path. `MissingScad` fails at
   instantiation (its `coherent_read` at `openscad.py:45`) — the right
   moment, the same contextless message.

2. **A declarative child is realized by its parent's constructor, not by the
   class body.** `Rig.__dict__['part']` is a `ChildDeclaration`; `Rig()`
   succeeds and `rig.part` is a constructed `MissingStl` whose `src` does not
   exist. `rig.mtime_ns` answers a NUMBER — the root's own tracked set does
   not include the child's missing file — so the root does not even fail at
   the point a leaf root does.

3. **A directory is caught by nothing.** `DirectoryStl` and `DirectoryStep`
   construct, and `mtime_ns` answers a number for both (`os.stat` succeeds on
   a directory). The build then dies inside a foreign library.

4. **What the maker sees.** The load-time failure names the MODEL reference,
   never the node or the attribute; the assembly case names only the root;
   the directory cases produce a trimesh message and an OCCT flex-scanner
   dump in red.

5. **The one fixture in the suite that removes its own source**
   (`tests/test_builder_reload_resilience.py:68-78`, `VANISHING_JSCAD_PIPE`)
   deletes the file AFTER `super().__init__()` returns. Reproduced: the file
   exists throughout construction and is gone afterwards, so a check placed
   inside `JScadNode.__init__` before its own `super().__init__()` sees a
   present file and that test's `FileNotFoundError` still comes from
   `mtime_ns`, unchanged.

6. **Out of scope, recorded:** `BareScad()` — an `OpenScadNode` declaring no
   `scad_source` — raises `TypeError: join() argument must be str, bytes, or
   os.PathLike object, not 'NoneType'`, where every other source-bound
   adapter names the class and the missing attribute.

## The transcript

```
### probe_when.py
--- class definition (importing the module) ---
import probe_project.parts: OK -> 'module imported'

--- MissingStl ---
  instantiation: OK -> <probe_project.parts.MissingStl object at 0x72b93707abd0>
  node.src = <WT>/openspec/changes/name-the-missing-file/evidence/probe_project/absent.stl
  exists   = False
  node.files: OK -> ['<WT>/openspec/changes/name-the-missing-file/evidence/probe_project/absent.stl', '<WT>/openspec/changes/name-the-missing-file/evidence/probe_project/parts.py']
  node.mtime_ns: RAISED FileNotFoundError: [Errno 2] No such file or directory: '<WT>/openspec/changes/name-the-missing-file/evidence/probe_project/absent.stl'
  traceback of that failure:
Traceback (most recent call last):
  File "<WT>/openspec/changes/name-the-missing-file/evidence/probe_when.py", line 18, in step
    value = fn()
            ^^^^
  File "<WT>/openspec/changes/name-the-missing-file/evidence/probe_when.py", line 42, in <lambda>
    kind, value = step('  node.mtime_ns', lambda: node.mtime_ns)
                                                  ^^^^^^^^^^^^^
  File "<WT>/solid_node/node/base.py", line 1039, in mtime_ns
    return max(os.stat(path).st_mtime_ns for path in self.files)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<WT>/solid_node/node/base.py", line 1039, in <genexpr>
    return max(os.stat(path).st_mtime_ns for path in self.files)
               ^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '<WT>/openspec/changes/name-the-missing-file/evidence/probe_project/absent.stl'

--- MissingStep ---
  instantiation: OK -> <probe_project.parts.MissingStep object at 0x72b936f78710>
  node.src = <WT>/openspec/changes/name-the-missing-file/evidence/probe_project/absent.step
  exists   = False
  node.files: OK -> ['<WT>/openspec/changes/name-the-missing-file/evidence/probe_project/absent.step', '<WT>/openspec/changes/name-the-missing-file/evidence/probe_project/parts.py']
  node.mtime_ns: RAISED FileNotFoundError: [Errno 2] No such file or directory: '<WT>/openspec/changes/name-the-missing-file/evidence/probe_project/absent.step'
  traceback of that failure:
Traceback (most recent call last):
  File "<WT>/openspec/changes/name-the-missing-file/evidence/probe_when.py", line 18, in step
    value = fn()
            ^^^^
  File "<WT>/openspec/changes/name-the-missing-file/evidence/probe_when.py", line 42, in <lambda>
    kind, value = step('  node.mtime_ns', lambda: node.mtime_ns)
                                                  ^^^^^^^^^^^^^
  File "<WT>/solid_node/node/base.py", line 1039, in mtime_ns
    return max(os.stat(path).st_mtime_ns for path in self.files)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<WT>/solid_node/node/base.py", line 1039, in <genexpr>
    return max(os.stat(path).st_mtime_ns for path in self.files)
               ^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '<WT>/openspec/changes/name-the-missing-file/evidence/probe_project/absent.step'

--- MissingJscad ---
  instantiation: OK -> <probe_project.parts.MissingJscad object at 0x72b8b796cf20>
  node.src = <WT>/openspec/changes/name-the-missing-file/evidence/probe_project/absent.js
  exists   = False
  node.files: OK -> ['<WT>/openspec/changes/name-the-missing-file/evidence/probe_project/absent.js']
  node.mtime_ns: RAISED FileNotFoundError: [Errno 2] No such file or directory: '<WT>/openspec/changes/name-the-missing-file/evidence/probe_project/absent.js'
  traceback of that failure:
Traceback (most recent call last):
  File "<WT>/openspec/changes/name-the-missing-file/evidence/probe_when.py", line 18, in step
    value = fn()
            ^^^^
  File "<WT>/openspec/changes/name-the-missing-file/evidence/probe_when.py", line 42, in <lambda>
    kind, value = step('  node.mtime_ns', lambda: node.mtime_ns)
                                                  ^^^^^^^^^^^^^
  File "<WT>/solid_node/node/base.py", line 1039, in mtime_ns
    return max(os.stat(path).st_mtime_ns for path in self.files)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<WT>/solid_node/node/base.py", line 1039, in <genexpr>
    return max(os.stat(path).st_mtime_ns for path in self.files)
               ^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '<WT>/openspec/changes/name-the-missing-file/evidence/probe_project/absent.js'

--- MissingScad ---
  instantiation: RAISED FileNotFoundError: [Errno 2] No such file or directory: '<WT>/openspec/changes/name-the-missing-file/evidence/probe_project/absent.scad'

### probe_declarative.py
--- importing the declarative assembly module ---
Rig.__dict__["part"] is a ChildDeclaration; is it a ChildDeclaration rather than a node? True

--- instantiating the PARENT (realizes its children) ---
  Rig(): OK -> <assembly.Rig object at 0x7ce7fb07acc0>
  rig.part: OK -> <parts.MissingStl object at 0x7ce7a1c86870>
  os.path.exists(rig.part.src): OK -> False
  rig.mtime_ns: OK -> 1789461225965449639

--- a declared source that IS present but is a directory ---
  DirectoryStl:
    instantiation: OK -> <parts.DirectoryStl object at 0x7ce7893502c0>
    os.path.isdir(node.src): OK -> True
    node.mtime_ns: OK -> 1789461424462391843
  DirectoryStep:
    instantiation: OK -> <parts.DirectoryStep object at 0x7ce77c081460>
    os.path.isdir(node.src): OK -> True
    node.mtime_ns: OK -> 1789461424462391843

### probe_vanishing.py
before construction: exists = True
constructed OK; after construction: exists = False
node.mtime_ns: RAISED FileNotFoundError: [Errno 2] No such file or directory: '<WT>/openspec/changes/name-the-missing-file/evidence/probe_project/vanishing.js'

### probe_bare.py
BareScad(): RAISED TypeError: join() argument must be str, bytes, or os.PathLike object, not 'NoneType'

### solid build, model = parts:MissingStl
 INFO -    core.builder - START
ERROR -    core.builder - parts:MissingStl: failed to inspect initial sources project: [Errno 2] No such file or directory: '<WT>/openspec/changes/name-the-missing-file/evidence/probe_project/absent.stl'

### solid build, model = parts:MissingStep
 INFO -    core.builder - START
ERROR -    core.builder - parts:MissingStep: failed to inspect initial sources project: [Errno 2] No such file or directory: '<WT>/openspec/changes/name-the-missing-file/evidence/probe_project/absent.step'

### solid build, model = assembly:Rig
  File "<WT>/solid_node/core/builder.py", line 85, in project_build_lock
    handle = open(path, 'a+')
             ^^^^^^^^^^^^^^^^
IsADirectoryError: [Errno 21] Is a directory: '<WT>/openspec/changes/name-the-missing-file/evidence/probe_project/_build.lock'

### solid build, model = parts:DirectoryStl
  File "<WT>/solid_node/core/builder.py", line 85, in project_build_lock
    handle = open(path, 'a+')
             ^^^^^^^^^^^^^^^^
IsADirectoryError: [Errno 21] Is a directory: '<WT>/openspec/changes/name-the-missing-file/evidence/probe_project/_build.lock'

### solid build, model = parts:DirectoryStep
  File "<WT>/solid_node/core/builder.py", line 85, in project_build_lock
    handle = open(path, 'a+')
             ^^^^^^^^^^^^^^^^
IsADirectoryError: [Errno 21] Is a directory: '<WT>/openspec/changes/name-the-missing-file/evidence/probe_project/_build.lock'
```

## The originating project

`projects/Actuators/Internal-Cycloidal-Actuator/simulation/actuator/parts.py`
— generated by `solid import-step` — opens with a hand-written preamble whose
only job is to replace this failure (verbatim, lines 9-20):

```python
from solid_node.node import StepNode
from solid_node.math import sin, cos
from solid_node.motion.joints import Revolute

from simulation.actuator.source import require

# The leaf's own missing-file failure is a bare FileNotFoundError naming
# only the path; "the vendor STEP file is obtained, never faked" is
# unchanged by the move to generated source, so this generated module
# still calls source.require() at import to keep the failure naming the
# extract command.
require()
```

and `simulation/actuator/source.py:51-56` is the `require()` it calls:

```python
def require():
    """Raise FileNotFoundError naming the extract command when absent."""
    reason = check()
    if reason:
        raise FileNotFoundError(reason)
    return STEP_FILE
```

That module's own docstring states the rule this change must not weaken:
"A build never substitutes a placeholder shape for an absent file; it fails
naming the command below."

## Contracts this change must not disturb, read on this worktree

- `tests/test_content_verified_currency.py:431-447` —
  `test_an_unreadable_source_is_never_current`: "`mtime_ns` has always raised
  for a source that cannot be stat'ed, and still does -- a missing file is a
  build failure, not a cache question." A source removed AFTER construction
  keeps that behaviour.
- `tests/test_source_census.py:78-85` — a phase over a missing file raises
  `FileNotFoundError`.
- `tests/test_mesh_import_deferred.py:42-49` — importing
  `solid_node.node.base` must not import `trimesh`. The proposed helper uses
  `os.path` only.
- `solid_node/manager/templates/project/root/__init__.py:1-4` — `solid new`
  scaffolds a `Solid2Node`, not a source-bound leaf.
- `solid_node/manager/import_step.py` — `solid import-step` reads the
  document and writes source text; it constructs no `StepNode`, and its own
  input must exist for it to read at all.

## Red

`tests/test_missing_source_file.py`, run alone (`PYTHONPATH=$PWD .venv/bin/python
-m pytest tests/test_missing_source_file.py -q`) against the unchanged code, before
any implementation:

```
FF.FF.FFF                                                                [100%]
=================================== FAILURES ===================================
____ MissingSourceFileTest.test_a_directory_step_source_fails_as_not_a_file ____
    def test_a_directory_step_source_fails_as_not_a_file(self):
>       with self.assertRaises(ValueError) as raised:
E       AssertionError: ValueError not raised

____ MissingSourceFileTest.test_a_directory_stl_source_fails_as_not_a_file _____
    def test_a_directory_stl_source_fails_as_not_a_file(self):
>       with self.assertRaises(ValueError) as raised:
E       AssertionError: ValueError not raised

____ MissingSourceFileTest.test_an_absent_step_source_fails_at_construction ____
>       with self.assertRaises(FileNotFoundError) as raised:
E       AssertionError: FileNotFoundError not raised

____ MissingSourceFileTest.test_an_absent_stl_source_fails_at_construction _____
>       with self.assertRaises(FileNotFoundError) as raised:
E       AssertionError: FileNotFoundError not raised

_ MissingSourceFileTest.test_the_failure_arrives_when_the_parent_realizes_the_child _
>       with self.assertRaises(FileNotFoundError) as raised:
E       AssertionError: FileNotFoundError not raised

__ ForeignScratchSourceTest.test_an_absent_jscad_source_fails_at_construction __
>       with self.assertRaises(FileNotFoundError) as raised:
E       AssertionError: FileNotFoundError not raised

___ ForeignScratchSourceTest.test_an_absent_openscad_source_names_the_class ____
    message = str(raised.exception)
>       self.assertIn('AbsentScad', message)
E       AssertionError: 'AbsentScad' not found in "[Errno 2] No such file or
directory: '/tmp/solid_node_missing_source_ezllc8dh/no-such-shape.scad'"

=========================== short test summary info ============================
FAILED tests/test_missing_source_file.py::MissingSourceFileTest::test_a_directory_step_source_fails_as_not_a_file
FAILED tests/test_missing_source_file.py::MissingSourceFileTest::test_a_directory_stl_source_fails_as_not_a_file
FAILED tests/test_missing_source_file.py::MissingSourceFileTest::test_an_absent_step_source_fails_at_construction
FAILED tests/test_missing_source_file.py::MissingSourceFileTest::test_an_absent_stl_source_fails_at_construction
FAILED tests/test_missing_source_file.py::MissingSourceFileTest::test_the_failure_arrives_when_the_parent_realizes_the_child
FAILED tests/test_missing_source_file.py::ForeignScratchSourceTest::test_an_absent_jscad_source_fails_at_construction
FAILED tests/test_missing_source_file.py::ForeignScratchSourceTest::test_an_absent_openscad_source_names_the_class
7 failed, 2 passed in 2.79s
```

Two pass today, as required: `test_the_declared_childs_class_body_constructs_nothing`
(the deferral) and `test_a_source_removed_after_construction_still_raises_from_mtime_ns`
(the vanishing-source guard). Every failure matches the reason `tasks.md` 1.2
predicted: absent `stl_source`/`step_source`/`jscad_source` construct with no
error at all; a directory construct with no error at all; and the absent
`scad_source` case already raises `FileNotFoundError` (right exception, right
moment) but with a message naming only the path.

## Green

After implementing `require_source_file` (`solid_node/node/sources.py`) and
calling it from `stl.py`, `step.py`, `jscad.py` and `openscad.py`:

```
$ PYTHONPATH=$PWD .venv/bin/python -m pytest tests/test_missing_source_file.py -q
.........                                                                [100%]
9 passed in 2.87s

$ PYTHONPATH=$PWD .venv/bin/python -m pytest tests/test_missing_source_file.py tests/test_stl_node.py tests/test_step_node.py -q
........................................................................ [ 66%]
....................................                                     [100%]
108 passed in 3.92s
```

## After

The same probes (`sh openspec/changes/name-the-missing-file/evidence/run-probes.sh`),
run after implementation, on this worktree:

```
### probe_when.py
--- class definition (importing the module) ---
import probe_project.parts: OK -> 'module imported'

--- MissingStl ---
  instantiation: RAISED FileNotFoundError: MissingStl declares stl_source =
  'absent.stl', resolved against <WT>/openspec/changes/name-the-missing-file/
  evidence/probe_project/parts.py, but <WT>/openspec/changes/
  name-the-missing-file/evidence/probe_project/absent.stl does not exist.
  Create or fetch the file, or correct the declaration.

--- MissingStep ---
  instantiation: RAISED FileNotFoundError: MissingStep declares step_source =
  'absent.step', resolved against .../parts.py, but .../absent.step does not
  exist. Create or fetch the file, or correct the declaration.

--- MissingJscad ---
  instantiation: RAISED FileNotFoundError: MissingJscad declares jscad_source
  = 'absent.js', resolved against .../parts.py, but .../absent.js does not
  exist. Create or fetch the file, or correct the declaration.

--- MissingScad ---
  instantiation: RAISED FileNotFoundError: MissingScad declares scad_source =
  'absent.scad', resolved against .../parts.py, but .../absent.scad does not
  exist. Create or fetch the file, or correct the declaration.

### probe_declarative.py
--- importing the declarative assembly module ---
Rig.__dict__["part"] is a ChildDeclaration; is it a ChildDeclaration rather
than a node? True

--- instantiating the PARENT (realizes its children) ---
  Rig(): RAISED FileNotFoundError: MissingStl declares stl_source =
  'absent.stl', resolved against .../parts.py, but .../absent.stl does not
  exist. Create or fetch the file, or correct the declaration.

--- a declared source that IS present but is a directory ---
  DirectoryStl:
    instantiation: RAISED ValueError: DirectoryStl declares stl_source =
    'a_directory', resolved against .../parts.py, but .../a_directory is not
    a file.
  DirectoryStep:
    instantiation: RAISED ValueError: DirectoryStep declares step_source =
    'a_directory', resolved against .../parts.py, but .../a_directory is not
    a file.

### probe_vanishing.py
before construction: exists = True
constructed OK; after construction: exists = False
node.mtime_ns: RAISED FileNotFoundError: [Errno 2] No such file or directory:
'.../vanishing.js'

### probe_bare.py
BareScad(): RAISED TypeError: join() argument must be str, bytes, or
os.PathLike object, not 'NoneType'

### solid build, model = parts:MissingStl
ERROR - core.builder - parts:MissingStl: failed to load project: MissingStl
declares stl_source = 'absent.stl', resolved against .../parts.py, but
.../absent.stl does not exist. Create or fetch the file, or correct the
declaration.

### solid build, model = parts:MissingStep
ERROR - core.builder - parts:MissingStep: failed to load project: MissingStep
declares step_source = 'absent.step', resolved against .../parts.py, but
.../absent.step does not exist. Create or fetch the file, or correct the
declaration.

### solid build, model = assembly:Rig
ERROR - core.builder - assembly:Rig: failed to load project: MissingStl
declares stl_source = 'absent.stl', resolved against .../parts.py, but
.../absent.stl does not exist. Create or fetch the file, or correct the
declaration.

### solid build, model = parts:DirectoryStl
ERROR - core.builder - parts:DirectoryStl: failed to load project:
DirectoryStl declares stl_source = 'a_directory', resolved against
.../parts.py, but .../a_directory is not a file.

### solid build, model = parts:DirectoryStep
ERROR - core.builder - parts:DirectoryStep: failed to load project:
DirectoryStep declares step_source = 'a_directory', resolved against
.../parts.py, but .../a_directory is not a file.
```

Every message now names the class, the declaring attribute and its declared
value, the module resolved against, and the absolute resolved path -- and the
CLI's own wrapper line changed incidentally from "failed to inspect initial
sources project" to "failed to load project" for these cases, because the
refusal now happens during `load_node()` itself (`builder.py:327-329`)
rather than when `mtime_ns` is read just after it
(`builder.py:333-358`); both are pre-existing `Builder._start()` wrapper
strings (`builder.py:356`, `358`) and out of scope (`proposal.md`).
`probe_bare.py` (`BareScad`, no `scad_source` declared at all) is
unchanged, as documented out of scope.

**Finding beyond what the probes above show** (see "## Reload-repair
regression" below): moving the STL/STEP/JScad refusal to fire before
`super().__init__()` also moves *which* `Builder._on_reload_exception` stage
catches an "absent from the very start" `JScadNode` -- from `'inspect
initial sources'` (where the constructed node's `self.files` names the
missing path precisely) to `'load'` (where no node exists yet at all, so
the develop-mode recovery watch can only fall back to a directory-wide,
`.py`-only watch). Measured with `tests/test_builder_reload_resilience.py`'s
new `test_missing_source_before_construction_reload_waits_for_repair`.

## Reload-repair regression (task 3.1b; reviewer's note 4 was a reading, not
a measurement -- this is the measurement)

Reviewer's note 4 asked for a test proving the develop-mode reload path
"surfaces and waits for repair exactly as the vanishing-source case does."
Measured, it does not, for the case where the foreign file was never there
to begin with (as opposed to `VANISHING_JSCAD_PIPE`, which removes a file
that was present throughout construction):

- **Before this change**: a `JScadNode` root with no `jscad_source` on disk
  from the start constructs successfully (no check existed), so
  `Builder._start()`'s `load_node()` call (`builder.py:327-329`) succeeds and
  returns a fully constructed `self.node` with `self.node.files` already
  naming the (missing) `.js` path. The very next line,
  `self.node.mtime_ns` (`builder.py:333`), raises `FileNotFoundError`,
  caught by `_on_reload_exception(error, 'inspect initial sources')`
  (`builder.py:357-358`), which calls `_watch_broadly(self.node.files)`
  (`builder.py:529-530`) -- a PRECISE watch that includes the missing `.js`
  path itself. Writing that file is observed and the reload recovers.
  (Confirmed by reverting the implementation and re-running the new test:
  its message assertions fail, as expected -- old messages are bare paths --
  but the wait-for-repair half passes.)

- **After this change**: the same `JScadNode` root now fails INSIDE its own
  `__init__`, before `super().__init__()` ever runs -- so `load_node()`
  itself raises, caught by `_on_reload_exception(e, 'load')`
  (`builder.py:332-333`) with `self.node` never assigned. `_watch_broadly`
  is then called with `known_sources=()` (`builder.py:527-528`,
  `getattr(getattr(self, 'node', None), 'files', ())`), so
  `self._watched_sources` is empty and the only subscription is
  `self._broad_python_watch`, the entry module's own directory, watched for
  `.py` changes only (`builder.py:812-820`). Writing the missing `.js` file
  into that same directory is never observed:
  `test_missing_source_before_construction_reload_waits_for_repair` fails at
  `self.assertFalse(proc.is_alive(), 'reload did not observe the
  foreign-source repair')` -- the process is still alive and waiting
  15 seconds after the repair, because `on_modified` (`builder.py:806-822`)
  never receives a qualifying event for it.

This is a genuine regression in develop-mode reload precision for exactly
the case this change adds a check for, produced by design.md's own placement
rule ("immediately after the path is resolved and before `super().__init__`
-- ... i.e. before `coherent_read`"). The message content this change adds
(`FileNotFoundError` naming the class and `jscad_source`) IS present and
correct in the surfaced error either way; what regresses is only the
wait-for-repair precision once that error has been surfaced. Left
unresolved here per the implementer's brief (`design.md`'s placement rule is
binding; not mine to redesign) -- reported for the reviewer.

## Full suite (task 3.3, run once, foreground)

```
$ PYTHONPATH=$PWD .venv/bin/python -m pytest -q
...
FAILED tests/test_builder_reload_resilience.py::BuilderReloadResilienceTest::test_missing_source_before_construction_reload_waits_for_repair
1 failed, 2705 passed, 4 skipped, 53 warnings, 1501 subtests passed in 341.85s (0:05:41)
```

Exit code 1 (pytest's code for "collected and ran, at least one failure"). Baseline
recorded in the implementer's brief: 2696 passed, 4 skipped before this change's
tests existed. 2705 passed + 1 failed = 2706 = 2696 + 10 new tests (9 in
`tests/test_missing_source_file.py`, 1 -- `test_missing_source_before_
construction_reload_waits_for_repair` -- in `tests/test_builder_reload_
resilience.py`), so nothing else in the suite moved. The one failure is the
measured reload-repair regression recorded above under "## Reload-repair
regression"; every other file this cycle touches or names in tasks.md 3.1/
3.1a/3.2 passed both alone and in this full run.

## Reload-repair regression — fix

Implemented exactly as the amendment specifies (design.md, "Amendment at
implementation"):

1. `sources.py`'s `require_source_file` now builds each exception with the
   message as its only constructor argument, then assigns
   `error.filename = path` on the instance before raising, for both the
   `FileNotFoundError` and the `ValueError` branch.
2. `builder.py`'s `_on_reload_exception`, reload branch only, now unions
   `getattr(exc, 'filename', None)` (when truthy) into the sources passed to
   `_watch_broadly`.

Running `tests/test_missing_source_file.py` first, as instructed, surfaces a
contradiction in the amendment's own premise before any of the later steps:

```
$ PYTHONPATH="$PWD" .venv/bin/python -m pytest tests/test_missing_source_file.py -q -p no:cacheprovider
...FF.FFFF
6 failed, 4 passed in 2.82s
```

Six failures, five of them tests that were green before this task started
(only `test_the_exception_carries_the_resolved_path_as_filename`, the test
this task adds, is new). All six fail the same way. Reproduced minimally:

```
$ .venv/bin/python3 -c "
e = FileNotFoundError('hello world message')
print(repr(str(e)))
e.filename = '/some/path'
print(repr(str(e)))
print(e.args, e.errno, e.strerror, e.filename)
"
'hello world message'
"[Errno None] None: '/some/path'"
('hello world message',) None None '/some/path'
```

`OSError.__str__` (which `FileNotFoundError` inherits) special-cases on
`self.filename` being set at all, regardless of *how or when* it was set —
not only when passed through the constructor as `(errno, strerror,
filename)`. Assigning `.filename` after construction is not inert for an
`OSError` subclass: `str(error)` immediately switches from the one-sentence
message to `"[Errno None] None: <path!r>"`, which is worse than the design
anticipated ("constructing `FileNotFoundError(errno, msg, path)` would
prefix `[Errno 2]` and append the path a second time") — post-hoc
assignment does not avoid that rendering, it triggers a *different* broken
one (`None`/`None` in place of a real errno/strerror, because `.args` still
holds only the one string).

`ValueError` is unaffected — it is not an `OSError` subclass, so its
`__str__` only ever reads `.args`:

```
$ .venv/bin/python3 -c "
e = ValueError('hello world message')
e.filename = '/some/path'
print(repr(str(e)))
"
'hello world message'
```

So the `ValueError` branch (the two `test_a_directory_*_fails_as_not_a_file`
tests) passes; every `FileNotFoundError` branch breaks, including four
tests this change already shipped and that were green (`test_an_absent_stl_
source_fails_at_construction`, `test_an_absent_step_source_fails_at_
construction`, `test_the_failure_arrives_when_the_parent_realizes_the_
child`, `test_an_absent_jscad_source_fails_at_construction`,
`test_an_absent_openscad_source_names_the_class` — five, not four) plus the
new filename test added for this task.

Per the implementer's brief ("If implementation evidence contradicts the
design, STOP and report the contradiction with the evidence; do not
improvise a different design"), I stopped here: I did not attempt a
different mechanism for attaching the path to the exception (e.g. a
non-`filename`-named attribute, overriding `__str__`, or constructing the
`OSError` triple and stripping its rendering), and did not run
`tests/test_builder_reload_resilience.py` or the full suite — running them
against code already known broken by its own first test file would only
reproduce the same root cause downstream and spend the one allowed full-suite
run for no new information. `sources.py` and `builder.py` are left exactly
as the amendment specifies, and `tests/test_missing_source_file.py` carries
the new test, so the reviewer can see the contradiction reproduced exactly
as written. Task 4.3a is left unticked.

## Reload-repair regression — corrected fix

Implemented exactly as design.md's "Correction (reviewer, 2026-09-15, after
the amendment's first test run)" specifies:

1. `sources.py` gains `import errno` and a named subclass:

   ```python
   class MissingSourceFile(FileNotFoundError):
       def __init__(self, message, path):
           super().__init__(errno.ENOENT, message, path)

       def __str__(self):
           return self.strerror
   ```

   `require_source_file`'s absent-file branch now raises
   `MissingSourceFile(where + '...', path)` directly — no post-hoc
   attribute assignment. The directory branch is unchanged from the first
   amendment attempt: `ValueError(where + 'is not a file.')` with
   `error.filename = path` assigned on the instance before raising (inert
   for `ValueError.__str__`, which reads only `.args`).
2. `builder.py`'s `_on_reload_exception`, reload branch, is unchanged —
   verified by reading it (`builder.py:526-533`): it already unions
   `getattr(exc, 'filename', None)` into the sources handed to
   `_watch_broadly`, exactly as the amendment specifies. `MissingSourceFile`
   is an `OSError` subclass built through the standard `(errno, strerror,
   filename)` triple, so `.filename` is set for it exactly as it is for any
   other `OSError`; nothing in `builder.py` needed to change.

### Run 1 — `tests/test_missing_source_file.py`

```
$ PYTHONPATH="$PWD" .venv/bin/python -m pytest tests/test_missing_source_file.py -q -p no:cacheprovider
..........
10 passed in 2.72s
```

Fully green, including the extended
`test_the_exception_carries_the_resolved_path_as_filename` (now also
asserting `isinstance(error, FileNotFoundError)` and
`error.errno == errno.ENOENT` for the absent-file case). The rendering
regression from the first attempt (`"[Errno None] None: '<path>'"`) is
gone: `str(error)` is the one-sentence message, confirmed directly —

```
$ .venv/bin/python3 -c "
from solid_node.node.sources import MissingSourceFile
import errno
e = MissingSourceFile('hello world message', '/some/path')
print(repr(str(e)))
print(e.args, e.errno, e.strerror, e.filename)
print(isinstance(e, FileNotFoundError), e.errno == errno.ENOENT)
"
'hello world message'
(2, 'hello world message') 2 hello world message /some/path
True True
```

### Run 2 — `tests/test_builder_reload_resilience.py`

```
$ PYTHONPATH="$PWD" .venv/bin/python -m pytest tests/test_builder_reload_resilience.py -q -p no:cacheprovider
...F.....
1 failed, 8 passed in 4.37s
```

**Not green.** The one failure is
`test_missing_source_before_construction_reload_waits_for_repair`
(added by the previous agent under task 3.1b, before either amendment
attempt existed) at its line:

```python
error = self.read_error()['error']
self.assertIn('FileNotFoundError', error)
```

```
E       AssertionError: 'FileNotFoundError' not found in 'Traceback (most recent call last):\n  File ".../solid_node/core/builder.py", line 327, in _start\n    self.node = load_node(\n                ^^^^^^^^^^\n  File ".../solid_node/core/loader.py", line 372, in load_node\n    node = klass(**parse_overrides(klass, overrides))\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File ".../solid_node/node/adapters/jscad.py", line 37, in __init__\n    require_source_file(self.__class__, \'jscad_source\', declared,\n  File ".../solid_node/node/sources.py", line 100, in require_source_file\n    raise MissingSourceFile(\nsolid_node.node.sources.MissingSourceFile: SimplePipe declares jscad_source = \'shape.js\', resolved against .../flat_project/simple_pipe.py, but .../flat_project/shape.js does not exist. Create or fetch the file, or correct the declaration.\n'
```

**Diagnosis.** `_on_reload_exception` builds `error_message` from
`traceback.format_exc()` (`builder.py:525`) when no `error_message` is
passed to it, and this is the `stage='load'` path
(`_start`, `builder.py:333`), which calls it with none. Python's
traceback formatter names the *concrete* exception class of the raised
instance, qualified by its module, not any ancestor class: a
`MissingSourceFile` raised from `solid_node/node/sources.py` renders as
`solid_node.node.sources.MissingSourceFile: <message>`, and the literal
substring `FileNotFoundError` does not appear anywhere in that text —
confirmed by inspection of the full traceback text above. Before the
correction, `require_source_file` raised a bare `FileNotFoundError`
instance (message assigned post-hoc, the rendering bug this correction
fixes), whose traceback line read `FileNotFoundError: <message>` and
satisfied this same assertion; introducing the named subclass changes
that traceback line's class name as a direct, unavoidable consequence of
`isinstance(error, FileNotFoundError)` being true while
`type(error) is not FileNotFoundError`. `assertIn('FileNotFoundError', ...)`
tests the literal text, not the type relationship the rest of the suite
(including the assertion added in `test_missing_source_file.py` this task)
correctly tests with `isinstance`.

This is the "evidence contradicts the design" case named in the
implementer's brief: `design.md`'s Correction is silent on this test's
literal-substring assertion (task 3.1b predates both amendment attempts),
and the two amendment texts do not reconcile it. Per the brief, I did not
edit `tests/test_builder_reload_resilience.py` (out of the file set this
task names — "Touch only: sources.py, builder.py … , tests/
test_missing_source_file.py, evidence.md, tasks.md") and did not run the
full suite. `sources.py` is left exactly as the corrected amendment
specifies; `builder.py` is unchanged (verified, not edited); task 4.3a is
left unticked pending the reviewer's decision on how to reconcile the
`test_missing_source_before_construction_reload_waits_for_repair`
assertion with a named exception subclass (e.g. assert
`isinstance`-compatible text such as the class's own name plus `FileNotFoundError`
as an ancestor, or relax the literal-substring check, or give
`MissingSourceFile` a different `__module__`/name that keeps the substring
— none attempted here, as none is this task's call to make).

## Reload-repair regression — green

`tests/test_builder_reload_resilience.py`'s
`test_missing_source_before_construction_reload_waits_for_repair` now
asserts `self.assertIn('MissingSourceFile', error)` per the reviewer's
second correction (design.md), and the run below is fully green.

```
$ PYTHONPATH="$PWD" .venv/bin/python -m pytest tests/test_missing_source_file.py tests/test_builder_reload_resilience.py -q -p no:cacheprovider
...................                                                      [100%]
19 passed in 6.25s
```

## Full suite after the amendment (task 4.3a)

Implementer's run, once, foreground, after the assertion change above:

    PYTHONPATH="$PWD" timeout 590 .venv/bin/python -m pytest tests -q -p no:cacheprovider

    2707 passed, 4 skipped, 53 warnings, 1501 subtests passed in 335.64s (0:05:35)

2707 = 2696 (cycle 7 baseline) + 9 in `tests/test_missing_source_file.py`
+ 1 (`test_the_exception_carries_the_resolved_path_as_filename`) + 1
(`test_missing_source_before_construction_reload_waits_for_repair`).
The implementer's earlier run (before the amendment) was 1 failed, 2705
passed — the reload-repair regression, recorded above. Reviewer's
independent run: 2707 passed, 4 skipped, 53 warnings, 1501 subtests passed
in 330.30s, exit 0.
