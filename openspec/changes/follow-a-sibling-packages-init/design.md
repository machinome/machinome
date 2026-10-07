## Context

### The rule today

`machinome/node/sources.py` builds a node's tracked set (`node.files`,
`base.py:705`, unioned upward by `node/internal.py`) as the node's own
source plus the transitive closure of the project modules it imports.
`_parse_project_imports(path, root)` reads each file's import statements
from its AST, `_import_from_targets` offers, for `from X import a, b`, the
names `X`, `X.a` and `X.b`, and `_project_file(name, root)` maps each name
through `sys.modules` to a file. `_project_file` then drops every
`__init__.py`:

```python
    # A package __init__ is, in the conventional layout, the root
    # assembly's own source: it imports every node in the project.
    # [...]
    if os.path.basename(path) == '__init__.py':
        return None
```

That is ADR-033's bold sentence, "The walk follows only the modules a
statement names; it never follows the `__init__.py` of a package it
traverses", whose reason is a package that contains the importer: "In the
conventional layout that file is the root assembly's own source and
imports every node beneath it, and Python executes it to resolve any
relative import inside the package. [...] That import is a child depending
on its parent." The `build-pipeline` requirement "Mtime-equality caching"
states the set without that exception: "A node's tracked files SHALL
include its own source together with project-local modules it imports
transitively. [...] Where the contributing set cannot be determined
exactly, the system SHALL track more files rather than fewer."

Every currency layer beneath the set — the integer-nanosecond stamp
(ADR-050), the per-contributor fingerprint (ADR-081), the node-scoped
digest (ADR-071), the request census (`source-closure-cost`), the sealed
generation (ADR-084), the loaded-shape cache (ADR-164) — is correct about
the files it is given. None is given a module that a node reaches only
through a package's `__init__.py`.

### Reproduction at `297d9286`

Bench `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch
`fix-warts-3`, `git rev-parse HEAD` =
`297d9286195f318b781df9afe9bdd7f61545ece8`, clean tree. Under
`PYTHONPATH=<bench>` the probe prints `machinome from
<bench>/machinome/__init__.py`.

`<scratch>` is
`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle19`.
`<scratch>/repro/` is a project in the red test's shape:
`pyproject.toml` (`[tool.machinome]`, `model = "shop:Assembly"`);
`shop/__init__.py`, the root assembly, importing `Wide`, `Lonely` and
`Narrow`; `shop/library/__init__.py`, `from .measures import *`;
`shop/library/measures.py`, `WIDTH = 3`; `shop/wide.py`, a `CadQueryNode`
doing `from .library import WIDTH`; `shop/lonely.py`, a `CadQueryNode`
importing no project module; `shop/dims.py`, `DEPTH = 2`; and
`shop/narrow.py`, a `CadQueryNode` doing `from . import dims`.
`<scratch>/probe_repro.py` imports the package, prints each leaf's tracked
set, builds `Wide`, appends a comment to `measures.py`, moves its mtime 10
s ahead, asks a fresh `Wide` whether its STL is up to date, and restores
the file. `FIX=1` patches the candidate rule (Decision 1) into that process
only; `FIX=naive` patches a rule that follows every `__init__.py`. No
framework file was edited.

```text
$ env -C <scratch>/repro PYTHONDONTWRITEBYTECODE=1 SOLID_BUILD_DIR=<scratch>/build-none \
    PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/python <scratch>/probe_repro.py
bench rule, unpatched
Wide tracks   ['shop/wide.py']
Lonely tracks ['shop/lonely.py']
Narrow tracks ['shop/dims.py', 'shop/narrow.py']
measures.py tracked by Wide: False
after build, Wide STL up to date: True
after editing measures.py, Wide STL up to date: True

$ ... FIX=1 ...
Wide tracks   ['shop/library/__init__.py', 'shop/library/measures.py', 'shop/wide.py']
Lonely tracks ['shop/lonely.py']
Narrow tracks ['shop/dims.py', 'shop/narrow.py']
measures.py tracked by Wide: True
after build, Wide STL up to date: True
after editing measures.py, Wide STL up to date: False

$ ... FIX=naive ...
Wide tracks   ['shop/library/__init__.py', 'shop/library/measures.py', 'shop/wide.py']
Lonely tracks ['shop/lonely.py']
Narrow tracks ['shop/__init__.py', 'shop/dims.py', 'shop/library/__init__.py',
               'shop/library/measures.py', 'shop/lonely.py', 'shop/narrow.py', 'shop/wide.py']
```

The last run is why the exception exists: `from . import dims` offers the
containing package `shop`, whose `__init__.py` is the root assembly, and
following it puts every node in `Narrow`'s set. The existing guard
`test_package_init_is_not_tracked` cannot see this: `Cyl` imports `from
.dimensions import ...`, which offers `source_set_project.dimensions` and
never the package itself, so it stays green under the naive rule too. A
`from . import` leaf is the fixture that tells the two rules apart.

### In the originating project

The investigation of 7 October 2026
(`<scratchpad>/investigations/artifact-freshness.md`, scratch copy of
`projects/3DPrintedClocks` at `ec2a05d1` in `<scratchpad>/I1/proj`,
byte-identical to the project for `clocks/`, `simulation/` and
`pyproject.toml`) measured Wall Clock 22 with the same rule patched in one
process (`<scratchpad>/I1/probe_fix.py`; `NOFIX=1` for the bench rule):

| | bench rule | candidate rule |
|---|---|---|
| `pillars.pillar` tracked files (of them in `clocks/`) | 15 (3) | 43 (30) |
| `clocks/plates.py`, `clocks/assembly.py`, `clocks/__init__.py` | not tracked | tracked |
| `simulation/__init__.py`, `simulation/wall_clock_22/__init__.py` (ancestors) | not tracked | not tracked |
| `simulation/shared/__init__.py` (a sibling, empty) | not tracked | tracked |
| root tracked files | 17 | 45 |
| pillar `_up_to_date` with the pillar edit applied | True (stale) | False |
| first build after the edit | 0.17 s, pillar STL stays 31.096 | 32.58 s, 288 files replaced, pillar STL 37.096 |
| warm build after that | 0.17 s | 0.42 s, nothing rewritten, `_up_to_date` True |
| `load_node` | 10.73 s | 11.00-11.20 s |

The documented run, `machinome test wall_clock_22 --mesh --volume-epsilon
0.001 --set facing=0`, gives 25 tests, 19 passed and 6 failed on the
unedited copy, cold (46.5 s) and warm (24.2 s). The six are the clock's
own: four `ValueError`s where the mesh engine refuses the
`SlidingWeightShell` STL as NotManifold, and two body-count failures for
the five-body bow ties.

### What the catalogue loses

`<scratch>/scan_facades.py` (read-only; it parses project files and
imports nothing) walks every catalogue project (a Git repository holding a
`pyproject.toml` with `[tool.machinome]`; 77 found), skipping `WTs/`,
`_build/`, hidden directories, venvs and `node_modules`, resolves each
import statement statically against the project root (absolute) or the
file's directory (relative), and records every import that names a
package whose `__init__.py` does not contain the importing file. Output:
`<scratch>/logs/scan.json`, `<scratch>/logs/scan.txt`; 11.6 s.

Restricted to files a node can import (not tests, and not `docs/`,
`openspec/`, `tools/`, `scripts/`, `spike/`, `upstream/`, `modules/`,
`restoration/` or a nested `_build_worktrees/` copy), four projects name a
sibling package:

| project | files | sibling `__init__.py` | what the bench loses |
|---|---|---|---|
| 3DPrintedClocks | 224 | `clocks/__init__.py` (re-exports 18 modules; 86 `from clocks import NAME`, 33 `import clocks`), `clocks/cq_gears/__init__.py` (re-exports; 3), `simulation/shared/__init__.py` (empty; 215 submodule imports) | every `clocks/` module reached only through the facade |
| Calculators/Curta-Type-I-3x | 10 | `simulation/standard/__init__.py` (empty; submodule imports) | nothing; the set gains one empty file |
| Lab-Equipment/openflexure-microscope | 10 | `simulation/microscope/body/__init__.py`, `.../actuators/__init__.py` (empty; `from ..body import layout`) | nothing; the set gains empty files |
| Robots/YouCanBuildDog | 1 | `simulation/tools/__init__.py` (empty), from `simulation/leg_contracts.py`, which only `test_dog.py` imports | nothing; no node reaches it |

So one project loses dependencies today, the originating one, and every
one of its clock models is affected the same way. The other matches gain
an empty `__init__.py`, which changes their tracked set and so re-derives
their artifacts once (Curta-Type-I-3x and openflexure-microscope; a
YouCanBuildDog node does not reach `leg_contracts.py`). The scan is an
upper bound on reach (it cannot know which files a node's closure
reaches) and resolves absolute imports against the project root only, as
the loader seeds it. Outside node trees, Robots/roboto_origin's vendored
training code under `modules/` imports through re-exporting facades, but no
module under its `simulation/` imports from `modules/`.

The suite's own fixtures do it too (the same scan of `tests/`):
`deep_project/` reaches each level through a re-exporting sub-package
`__init__.py` (`from .one import TwoCylindersTwice`), so its assemblies'
sets gain those files; `tests/test_files.py` asserts membership only and
is unaffected. Several test modules import a fixture package
(`from .source_set_project import dimensions`); a node class defined
inline in such a test module would now track that package's
`__init__.py` and what it imports. The full suite in the apply stage is
the check.

### Focused tests at `297d9286`

```text
$ env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1 \
    /home/asa/devel/machinome/.venv/bin/pytest -q -p no:cacheprovider \
    tests/test_source_set.py tests/test_files.py tests/test_source_closure_index.py
26 passed in 4.90s
```

## Goals / Non-Goals

**Goals**

- A node tracks the modules it reaches through the `__init__.py` of a
  project package that does not contain the importing module, so an edit
  to `clocks/plates.py` re-derives the pillar's STL and BREP together.
- The `__init__.py` of a package containing the importing module stays
  unfollowed, so a root assembly does not enter every node's set.
- ADR-033, the spec and the manual state the rule as the code applies it.

**Non-Goals**

- Following the parent packages of a dotted import, or a library module's
  own facade (proposal, "Deliberately out").
- Any change to artifact identity, paths, recipes, the digest, the
  fingerprint, the census or the sealed generation.
- Any edit to a catalogue project.

## Decisions

### 1. An `__init__.py` is dropped only when its package contains the importing file

`_project_file` takes the real path of the file whose statement is being
resolved and drops an `__init__.py` only when that file lies inside the
`__init__.py`'s package directory:

```python
def _parse_project_imports(path, root):
    ...
    return frozenset(
        found for found in (_project_file(name, root, path)
                            for name in names)
        if found is not None
    )


def _project_file(name, root, importer):
    """The project file a module name, imported by the file at real path
    `importer`, resolves to, or None if it is not one the node should
    track."""
    ...
    path = os.path.realpath(filename)

    # <the comment, rewritten: a package containing the importer is, in
    # the conventional layout, the root assembly or a sub-assembly above
    # it; following it would put every node in every node's set. A
    # package that does not contain the importer -- a library such as
    # 3DPrintedClocks' `clocks`, reached as `from clocks import Weight`
    # -- is code the importer runs, and its __init__ is followed
    # (OpenSpec change follow-a-sibling-packages-init).>
    if os.path.basename(path) == '__init__.py':
        package = os.path.dirname(path)
        if os.path.commonpath((package, importer)) == package:
            return None
    ...  # root and framework exclusions unchanged
```

`importer` is always a real path: `source_closure` starts from
`os.path.realpath(src)` and every file it queues came from
`_project_file`, which returns real paths. The `__init__.py` file itself
is the module's `__file__`, so a package reached by a symbolic link is
compared by its real directory, as every other tracked path is.

**Why the importing file, not the node's own source.** Two readings of
"contains" were weighed:

- *the importing file* (chosen). The answer depends only on the file
  whose statement is parsed, so `_parse_project_imports` stays a function
  of that file and `sys.modules`, and `_import_cache`, keyed on the file's
  observation, stays sound with no change. Inside `clocks/`, the library's
  own `from . import x` never pulls `clocks/__init__.py`; inside a
  sub-assembly package, a module's `from . import part` never pulls that
  sub-assembly's `__init__.py`.
- *the node's own source* (the start of the walk). More inclusive, but the
  parse result would depend on which node asked, so the cache would have
  to be keyed on (file, node) or the filter moved into `source_closure`.
  Worse, any module the walk reaches inside a sub-assembly package that
  does `from . import x` would pull that sub-assembly's `__init__.py` and,
  through it, every node of the sub-assembly into a leaf elsewhere: the
  growth ADR-033 refused, arriving sideways.

**Alternatives rejected**

- *Follow every `__init__.py`.* The `FIX=naive` run above: a `from .
  import` leaf tracks the whole project.
- *Follow a sibling `__init__.py` only from the node's own file, not
  transitively.* Misses the clock's real chain: the node module
  `simulation/wall_clock_22/parts.py` does `from . import spec`, and it is
  `spec.py` that does `from clocks import (...)`.
- *Follow only a non-empty `__init__.py`.* It would spare Curta-Type-I-3x
  and openflexure-microscope their one rebuild, but it makes membership
  depend on the `__init__.py`'s content while the import cache is keyed on
  the importing file's observation: an empty `__init__.py` that later
  gains `from .layout import *` would stay out of a set whose importer did
  not change. A sound version needs the cache keyed on more files; the
  one-time rebuild is cheaper.
- *Track the generation's imported modules* (`SourceGeneration`): ADR-033
  rejected it; every module would belong to every node.
- *Have the project import named submodules.* A workaround in a read-only
  project, fragile, and the spec puts the obligation on the framework.

### 2. ADR-033 is amended, not superseded

The decision ADR-033 records — a static import closure over project
modules, with an exception for the package above the importer — stands.
The amendment narrows its bold sentence to the case its own rationale
gives. A dated section is appended to
`docs/adrs/NODE/ADR-033-import-closure-source-set-and-up-to-date-leaf-path.md`:

> ## Amendment (2026-10-07, change `follow-a-sibling-packages-init`)
>
> The walk drops the `__init__.py` of a package only when that package
> contains the file whose import statement names it. A package that does
> not contain the importing file is code that file runs, and its
> `__init__.py` is followed like any named module, together with what it
> imports. The bold sentence above described a broader rule than its
> reason: the root assembly's `__init__.py`, and a sub-assembly's, lie
> above the modules that reach them through a relative import, and those
> are still never followed. A library package beside the importer is not
> that case. 3DPrintedClocks builds every clock through
> `from clocks import ...`, where `clocks/__init__.py` re-exports 18
> modules; dropping it left Wall Clock 22's leaves tracking 3 of the 30
> `clocks/` modules they run, and an edit to the pillar radius in
> `clocks/plates.py` served the old pillar from a build that reported
> itself current. With the narrower rule the pillar tracks all 30, the
> edit re-derives its STL and BREP together, and a warm rebuild rewrites
> nothing. The containment test reads only the importing file's path, so
> the per-file import cache is unchanged. The walk still follows only the
> module a dotted statement names, not the parent packages Python runs on
> the way, and a library module that reaches its own package's
> `__init__.py` is still not followed through it. Projects whose nodes
> import through a sibling package rebuild once.

The header's `**Amended by:**` line gains, after the ADR-071 entry:
`; amended 2026-10-07 (change follow-a-sibling-packages-init) — a sibling
package's __init__.py is followed`. The index entry in
`docs/adrs/README.md` for ADR-033 gains `, amended 2026-10-07` in the form
ADR-096's entry uses.

### 3. The specs

- `build-pipeline`, "Mtime-equality caching": the source-set paragraph
  gains two sentences between "imports transitively." and "Modules outside
  the project tree": a package's `__init__.py` is tracked, and followed to
  what it imports, when a tracked module names that package and the
  package's directory does not contain that module; the `__init__.py` of a
  package containing the importing module is not followed, with the
  reason. Two scenarios are added after "Imported project module edit
  invalidates dependants"; every other line of the requirement is carried
  verbatim (checked with `diff` against
  `openspec/specs/build-pipeline/spec.md` lines 390-640: the only
  differences are the paragraph and the two scenarios).
- `source-closure-cost`, "The tracked source set is unchanged": its first
  sentence named "exactly the source closure it produces today", which,
  read after this change, would forbid it. It becomes "exactly the source
  closure that `build-pipeline`'s Mtime-equality caching defines"; the
  second paragraph and the three scenarios are carried. The requirement's
  subject, that the package lookup changes no node's set, is unchanged.

### 4. Words

- `docs/architecture.md`, the invariant beginning "A node's source set is
  its own file plus the project-local modules it imports, transitively —
  never the `__init__.py` of a package the walk merely traverses, which
  would make every node depend on every file (ADR-033)": "never the
  `__init__.py` of a package the walk merely traverses" becomes "never the
  `__init__.py` of a package containing the importing module, which would
  make every node depend on every file, though a sibling package's
  `__init__.py` is followed (ADR-033, amended)". The two other mentions
  (Principle 2, the build-flow paragraph) state the closure without the
  exception and stay.
- `docs/concepts/node-tree.rst`, "Freshness": the bullet "The walk never
  follows a package's `__init__.py`. A value reached through the package
  rather than the module that defines it is not tracked, and its edit
  serves a stale model." becomes: "The walk follows a package's
  `__init__.py` when the importing module lies outside that package, so a
  library imported as `from mylib import Gear` is tracked through its
  `__init__.py`. It never follows the `__init__.py` of the importing
  module's own package or one above it, which is usually an assembly that
  imports every node; a value a module reaches through its own package
  (`from . import WIDTH`, defined in that `__init__.py`) is not tracked,
  and its edit serves a stale model."
- `machinome/node/sources.py`: the comment above the test (Decision 1) and
  the module docstring's sentence on ambiguity stay true; the
  `_project_file` docstring names `importer`.
- `tests/source_set_project/__init__.py`: its docstring's "the source walk
  must follow only the modules a statement names and never the package it
  traverses" becomes "never the package containing the module that
  imports through it".
- `docs/project/changelog.rst`, under `Unreleased`:

  > * **An edit behind a library's `__init__.py` rebuilds what uses it.** A
  >   node's tracked sources now include the `__init__.py` of a project
  >   package it imports from outside, and what that file imports, so a
  >   leaf built through `from clocks import Weight`, where
  >   `clocks/__init__.py` re-exports the library's modules, is re-derived
  >   when one of those modules changes; it used to report itself current
  >   and serve the old shape. The `__init__.py` of the importing module's
  >   own package, usually an assembly, is still not followed. Projects
  >   whose nodes import through another package of their own rebuild once
  >   (follow-a-sibling-packages-init).

### 5. No new ADR

The amendment narrows an accepted sentence to its rationale; no new
mechanism, vocabulary or interface. `docs/architecture.md`'s module table
already lists ADR-033 for the node model.

## Proof plan

- RED, `tests/test_source_set.py`: a leaf `Wide` (`wide.py`, `from
  .library import WIDTH`) tracks `library/measures.py` and
  `library/__init__.py` and not the fixture's own `__init__.py`; red today
  on `measures.py`.
- RED: with `Wide` built and current, `edit_source` on
  `library/measures.py` plus a future mtime makes a fresh `Wide`'s
  `_up_to_date(stl_file)` False; red today (True).
- GUARD: a leaf `Peg` (`peg.py`, `from . import dimensions`, reading
  `dimensions.HEIGHT`) tracks `dimensions.py` and not the fixture's
  `__init__.py`. It is the suite's counterpart of the probe's `Narrow`:
  green before and after, and the `FIX=naive` run above shows it is the
  test that refuses a rule following every `__init__.py`.
- GUARD, unedited: `test_package_init_is_not_tracked`,
  `test_unrelated_node_is_not_invalidated`,
  `test_library_modules_are_not_tracked`, `tests/test_files.py`,
  `tests/test_source_closure_index.py`.
- Project, scratch copy (`<scratchpad>/I1/proj`, a fresh build directory
  under `<scratch>`): build cold with the change; apply the pillar edit
  (`clocks/plates.py`, `self.bottom_pillar_r = self.plate_distance / 2`
  → `+ 3.0`); the next build re-derives the pillar STL and BREP to 37.096 /
  37.1 mm (measured with `trimesh` and `cq.Shape.importBrep`); revert; the
  documented `machinome test` gives 25 tests, 19 passed, 6 failed, and a
  warm rerun rewrites nothing (`<scratchpad>/I1/state.py` diffs).
- Project, unchanged (`projects/3DPrintedClocks`, read-only, a scratch
  `SOLID_BUILD_DIR`, `PYTHONDONTWRITEBYTECODE=1`): the documented run
  against the unmodified bench, cold and warm; then against the changed
  bench into the same build directory, recording that the first run
  re-derives the model once, then warm. Counts stay 25/19/6.

## Risks / Trade-offs

- **One rebuild after upgrading** for every project whose nodes import
  through a sibling package: in the catalogue, every 3DPrintedClocks model
  (the ~32 s cold build per clock measured for Wall Clock 22),
  Curta-Type-I-3x and openflexure-microscope. Stated in the changelog.
- **Edits to a library invalidate every node using it.** Every clock leaf
  runs `spec.movement`, which executes the whole `clocks` library, so an
  edit anywhere in `clocks/` re-derives every leaf of every clock. That is
  what the leaves depend on, and the spec's direction.
- **A sibling package that is itself an assembly** (`from ..arm import
  ARM_LENGTH`, where `arm/__init__.py` imports every node of the arm)
  brings the arm's nodes into the importer's set. Python runs those
  modules for that import, so this is over-invalidation, not a wrong
  answer; the scan finds no node module in the catalogue that imports a
  non-empty sibling `__init__.py` other than 3DPrintedClocks' libraries.
- **Closure cost.** More files are parsed once per observation; measured
  `load_node` 10.7 s against 11.0-11.2 s on Wall Clock 22.

## Migration Plan

None beyond the one rebuild. No document, artifact name or recipe changes,
so nothing published is invalidated except by that rebuild.

## Open Questions

1. **Could following a sibling `__init__.py` track a file that changes on
   its own, so that a build is never current?** For the orchestrator.
   Measured: the change adds only `.py` files that the project's own
   import statements name, inside the project root (the root and framework
   exclusions are unchanged), and the modules those import. In the
   originating project the newly tracked files are `clocks/__init__.py`,
   `clocks/cq_gears/__init__.py`, `simulation/shared/__init__.py` and the
   `clocks/` modules behind them (30 `clocks/` files tracked by the pillar,
   against 3), all committed source (`git ls-files`), and the
   investigation's warm build after the change rewrote nothing in 0.42 s,
   so none of them moved between runs. A grep of every catalogue project
   (excluding `WTs/`, `_build/`, `_build_worktrees/`, `.tools/`,
   `upstream/`, `node_modules/`) for code that opens a `.py` path for
   writing, or calls `write_text`/`write_bytes` on one, finds one hit:
   Curta-Type-I-3x's `simulation/tools/compact_import.py`, a one-shot tool
   run by hand after `machinome import-step` to compact the generated
   `simulation/standard/parts.py` and `assembly.py`. Those are written by
   an explicit command, never by a build, and are committed; regenerating
   them is a source edit that should rebuild. What Curta newly tracks is
   the empty `simulation/standard/__init__.py`. No catalogue project keeps a virtual environment
   under its root (a search for `site-packages` finds only Dum-E's
   unpacked FreeCAD under `.tools/`, which no node module imports; FreeCAD
   is reached through the `machinome_freecad` package outside the
   project). The one shape that could misbehave is a project with its own
   venv inside its root: `import numpy` would then name a package
   `__init__.py` under the root and the walk would follow it into the
   library. That already happens today for a dotted import into such a
   venv (`from cadquery.occ_impl.shapes import Solid` is tracked), it only
   moves when the venv is upgraded, and no project has one.
   Recommendation: no exclusion and no content-based rule in this change;
   record the in-root venv as a `warts.md` entry only if a project ever
   hits it. Answered by the orchestrator at review (7 October 2026): as
   recommended.
2. **Plain amendment, or the pilot's call?** The change narrows an
   accepted ADR sentence. This design treats it as within the mandate,
   because it restores the sentence to its stated reason and to the
   spec's "more files rather than fewer"; the orchestrator decides whether
   the pilot should see it first. Answered by the orchestrator at review
   (7 October 2026): within the mandate, as a dated amendment; a silent
   stale artifact is a correctness defect, and the amendment keeps the
   sentence's own reason.
