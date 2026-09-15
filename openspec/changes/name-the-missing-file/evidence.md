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
