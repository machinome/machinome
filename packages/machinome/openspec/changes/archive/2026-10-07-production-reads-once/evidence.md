# Evidence — `production-reads-once`

Cycle 10 of the fix-warts-3 campaign (`workflow/ongoing/fix-warts-3.md`).
Bench `machinome/WTs/fix-warts-3`, branch `fix-warts-3`, planning commit
fbd7e75 (`git -C <bench> rev-parse HEAD` printed
`fbd7e75c0e5be23ca109b6be9b4ac54a6a658559`). Every framework command below
ran as
`env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1 /home/asa/devel/machinome/.venv/bin/<tool> ...`,
with `-p no:cacheprovider` for pytest, one process at a time, never in
parallel (`ps -eo pid,args | grep '[p]ytest\|[m]achinome test\|[m]achinome
snapshot\|[m]achinome build'` listed no run before the first one). The
interpreter check, `python -c 'import machinome; print(machinome.__file__)'`,
printed
`/home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py`.

`<project>` is `/home/asa/devel/machinome/projects/Calculators/Curta-Type-I-3x`,
branch `main`, head `1f3dc22` (`git -C <project> rev-parse --short HEAD`,
before and after). The production slice's worktree
`<project>/WTs/production-layer-3x` is at `7c9121e` (`git -C
<project>/WTs/production-layer-3x rev-parse --short HEAD`). Both were read
and run, never written: `git -C <project> status --short` listed the same
four untracked entries before and after every Curta run
(`"3D Printed Curta Calculator Assembly_720p.mp4"`, `CREDITS`,
`curta-2x-files/`, `screenshots/reverser_inspection.png`), and the
worktree's `git status --short` was empty before and after its run.

`<scratch>` is the campaign scratchpad's `cycle10/` directory
(`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle10/`).
It holds a `pyproject.toml` (`[tool.machinome]`, empty) that gives its
scripts a project root. It is not durable; the scripts this record depends
on are copied below. `<focused>` is `tests/test_model_consumption.py
tests/test_production.py tests/test_production_documentation.py`.

## 1. Baseline on the unmodified tree (fbd7e75)

### 1.1 The scripts and the overlay

`<scratch>/repro_doubling.py`, run as
`env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1 .venv/bin/python <scratch>/repro_doubling.py`
with its ` INFO -` lines filtered out. Each order runs in its own build
root; "lifecycle" is `trigger_stl()`, "facade" is
`ModelSnapshot(model).occurrences`:

```python
"""Reproduce: binding a production after a build doubles the placements of
children positioned in a rigid internal node's render().

A faceted FusionNode of two self-materializing boxes with one child
translated in render(), read in four orders, each in its own build root.
"""

import os
import sys
import tempfile

SCRATCH = os.path.dirname(os.path.abspath(__file__))

import trimesh  # noqa: E402

from machinome.node.assembly import AssemblyNode  # noqa: E402
from machinome.node.leaf import LeafNode  # noqa: E402
from machinome.node.fusion import FusionNode  # noqa: E402
from machinome.model import ModelSnapshot  # noqa: E402
from machinome.core.pieces import _digest_bytes  # noqa: E402


class Box(LeafNode):
    def render(self):
        return trimesh.creation.box(extents=(2, 3, 4))

    def materialize(self, rendered):
        self.publish_artifact(
            self.stl_file, lambda path: rendered.export(path, file_type="stl")
        )


class Pair(FusionNode):
    a = Box()
    b = Box()

    def render(self):
        self.b.translate([1, 0, 0])


class Holder(AssemblyNode):
    pair = Pair()


def fresh(kind):
    os.environ["SOLID_BUILD_DIR"] = tempfile.mkdtemp(dir=SCRATCH,
                                                     prefix="build-")
    return kind()


def content(fusion):
    with open(fusion.stl_file, "rb") as handle:
        return _digest_bytes(handle.read())[:8]


def regenerate(fusion):
    os.remove(fusion.stl_file)
    fusion.generate_stl()
    return content(fusion)


def fusion_of(model):
    return model if isinstance(model, Pair) else model.pair


def facade(model):
    snap = ModelSnapshot(model)
    snap.occurrences
    occurrence = next(o for o in snap.occurrences
                      if o.model_type is Pair)
    return snap.geometry(occurrence).content_id[:8]


def report(label, model, extra=""):
    fusion = fusion_of(model)
    print(f"{label:<34} b.operations={len(fusion.b.operations)} "
          f"render()-> b ops={len(fusion.b.operations)} {extra}")


for kind in (Pair, Holder) if __name__ == "__main__" else ():
    print(f"--- {kind.__name__} ---")
    m = fresh(kind)
    cid = facade(m)
    report("facade-only", m, f"content={cid}")

    m = fresh(kind)
    m.trigger_stl()
    report("lifecycle-only", m, f"content={content(fusion_of(m))}")

    m = fresh(kind)
    facade(m)
    m.trigger_stl()
    report("facade-then-lifecycle", m, f"content={content(fusion_of(m))}")

    m = fresh(kind)
    m.trigger_stl()
    before = content(fusion_of(m))
    ModelSnapshot(m).occurrences
    after_render = len(fusion_of(m).render()[1].operations)
    report("lifecycle-then-facade", m,
           f"content before={before} regenerated={regenerate(fusion_of(m))}"
           f" render()[1] ops={after_render}")
```

`<scratch>/repro_assemble.py`, the same doubling after `assemble()`:

```python
"""The doubling after assemble() (presentation) rather than trigger_stl()."""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["SOLID_BUILD_DIR"] = tempfile.mkdtemp(
    dir=os.path.dirname(os.path.abspath(__file__)), prefix="build-")

from repro_doubling import Pair, Holder  # noqa: E402
from machinome.model import ModelSnapshot  # noqa: E402

for kind in (Pair, Holder):
    model = kind()
    fusion = model if kind is Pair else model.pair
    model.assemble()
    before = len(fusion.b.operations)
    prepared = fusion.__dict__.get("_prepared_rendered")
    ModelSnapshot(model).occurrences
    print(f"{kind.__name__}: assemble() then facade: b.operations "
          f"{before} -> {len(fusion.b.operations)}; "
          f"_prepared_rendered set: {prepared is not None}")
```

`<scratch>/repro_missing.py`:

```python
"""Reproduce: a missing input file at binding escapes Production(model) as
the facade's own changed-input error."""

import os
import tempfile
import traceback

SCRATCH = os.path.dirname(os.path.abspath(__file__))
os.environ["SOLID_BUILD_DIR"] = tempfile.mkdtemp(dir=SCRATCH, prefix="build-")

from machinome.node.assembly import AssemblyNode  # noqa: E402
from machinome.node.leaf import LeafNode  # noqa: E402
from machinome.components import Standard  # noqa: E402
from machinome.model import ModelSnapshot  # noqa: E402
from machinome.production.profile import Production  # noqa: E402
from machinome.production.item import Item  # noqa: E402
from machinome.production.process import Sourced  # noqa: E402

MISSING = os.path.join(SCRATCH, "never-existed.txt")


class Nut(LeafNode):
    def render(self):
        raise AssertionError("never rendered")


class Root(AssemblyNode):
    nut = Nut()


class RootProduction(Production[Root]):
    nut = Item(Root.nut, Sourced(Standard("DIN 934", designation="M4x0.7")))


for label, build in (
    ("root files", lambda m: m.files.add(MISSING)),
    ("child files", lambda m: m.nut.files.add(MISSING)),
):
    model = Root()
    build(model)
    for what, bind in (("Production(model)", RootProduction),
                       ("ModelSnapshot(model)", ModelSnapshot)):
        try:
            bind(model)
            print(f"{label}: {what}: no error")
        except Exception as error:
            print(f"{label}: {what}: {type(error).__module__}."
                  f"{type(error).__name__}: {error}")
            if label == "root files" and what == "Production(model)":
                traceback.print_exc()
```

The overlay, `<scratch>/curta-overlay/`: a copy of the production slice's
`production/` package from `<project>/WTs/production-layer-3x` (`7c9121e`),
its `__pycache__` directories removed and the one line
`from machinome.node import AssemblyNode, StepNode` of
`production/test_production.py` rewritten as
`from machinome.node.assembly import AssemblyNode` and
`from machinome.node.step import StepNode`; beside it, symbolic links
`simulation`, `pyproject.toml` and `CAD` to the same names in `<project>`
(the test hashes those sources by its own file's location). Checked before
the first run: `diff -r -x __pycache__ <project>/WTs/production-layer-3x/production <scratch>/curta-overlay/production`
reports that one line and nothing else (exit 1):

```
10c10,11
< from machinome.node import AssemblyNode, StepNode
---
> from machinome.node.assembly import AssemblyNode
> from machinome.node.step import StepNode
```

The Curta command, `<curta>`:

```sh
env -C <scratch>/curta-overlay PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH="<bench>:<project>:<scratch>/curta-overlay" \
  SOLID_BUILD_DIR=<scratch>/curta-build \
  /usr/bin/time -f 'wall %e s' /home/asa/devel/machinome/.venv/bin/python \
  -m pytest -q -p no:cacheprovider --basetemp=<scratch>/curta-basetemp \
  --rootdir=<scratch>/curta-overlay \
  <scratch>/curta-overlay/production/test_production.py
```

### 1.2 The doubling

`repro_doubling.py`:

```
--- Pair ---
facade-only                        b.operations=1 render()-> b ops=1 content=f435a10c
lifecycle-only                     b.operations=1 render()-> b ops=1 content=f435a10c
facade-then-lifecycle              b.operations=1 render()-> b ops=1 content=f435a10c
lifecycle-then-facade              b.operations=2 render()-> b ops=2 content before=f435a10c regenerated=fd3b003d render()[1] ops=2
--- Holder ---
facade-only                        b.operations=1 render()-> b ops=1 content=f435a10c
lifecycle-only                     b.operations=1 render()-> b ops=1 content=f435a10c
facade-then-lifecycle              b.operations=1 render()-> b ops=1 content=f435a10c
lifecycle-then-facade              b.operations=2 render()-> b ops=2 content before=f435a10c regenerated=fd3b003d render()[1] ops=2
```

Identical to Stage P's `repro_doubling.before.out`. `repro_assemble.py`:

```
Pair: assemble() then facade: b.operations 1 -> 2; _prepared_rendered set: True
Holder: assemble() then facade: b.operations 1 -> 2; _prepared_rendered set: True
```

### 1.3 The missing file

`repro_missing.py` (`<scratch>` abbreviated; every message names the full
path twice):

```
root files: Production(model): machinome.model.ModelInputChangedError: input observation failed: <scratch>/never-existed.txt: [Errno 2] No such file or directory: '<scratch>/never-existed.txt'
root files: ModelSnapshot(model): machinome.model.ModelInputChangedError: input observation failed: <scratch>/never-existed.txt: [Errno 2] No such file or directory: '<scratch>/never-existed.txt'
child files: Production(model): machinome.model.ModelInputChangedError: input observation failed: <scratch>/never-existed.txt: [Errno 2] No such file or directory: '<scratch>/never-existed.txt'
child files: ModelSnapshot(model): machinome.model.ModelInputChangedError: input observation failed: <scratch>/never-existed.txt: [Errno 2] No such file or directory: '<scratch>/never-existed.txt'
```

The traceback printed for the first line ends `FileNotFoundError: [Errno 2]
No such file or directory` / "During handling of the above exception,
another exception occurred" / `machinome.model.ModelInputChangedError`.

### 1.4 The slice's own README command

`env -C <project>/WTs/production-layer-3x PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="<bench>:<project>/WTs/production-layer-3x" SOLID_BUILD_DIR=<scratch>/curta-build .venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=<scratch>/curta-basetemp production/test_production.py`:

```
production/test_production.py:10: in <module>
    from machinome.node import AssemblyNode, StepNode
<bench>/machinome/node/__init__.py:192: in __getattr__
    raise ImportError(
E   ImportError: module 'machinome.node' has no attribute 'AssemblyNode': the root of machinome.node exports nothing, and 'AssemblyNode' is imported from its module, 'machinome.node.assembly'. Write `from machinome.node.assembly import AssemblyNode`.
ERROR production/test_production.py
1 error in 0.10s
```

The slice at `7c9121e` predates the 0.8 root cleanup, so it cannot be
collected against this bench; that is why the overlay is used.

### 1.5 The Curta production slice through the overlay

`<curta>`, warm build directory:

```
......                                                                   [100%]
6 passed in 117.56s (0:01:57)
wall 119.19 s
```

(Stage P: `6 passed in 119.02s`, wall 120.10 s.)

### 1.6 The focused suites

`pytest -q -p no:cacheprovider <focused>`: `52 passed, 4 warnings in
7.15s` (wall 8.26 s).

## 2. Red tests on the unmodified code

Added: in `tests/test_model_consumption.py`, after
`test_rigid_rest_placements_reused_by_normal_lifecycle`, the fixtures
`MeshBox`, `OffsetPair`, `HeldPair`, the test
`test_binding_after_a_build_keeps_rest_placements` parametrized over
`OffsetPair` and `HeldPair`, `test_missing_source_is_refused_at_construction`
and `test_source_deleted_after_binding_is_still_a_change`; in
`tests/test_production.py`, after
`test_bad_constructor_inputs_fail_immediately`,
`test_missing_model_source_is_refused_at_binding`. All as design.md
Decision 4 gives them; `os`, `Path` and `_digest_bytes` are imported inside
the test that uses them, as the module's other tests import theirs.

`pytest -q -p no:cacheprovider tests/test_model_consumption.py::test_binding_after_a_build_keeps_rest_placements tests/test_model_consumption.py::test_missing_source_is_refused_at_construction tests/test_model_consumption.py::test_source_deleted_after_binding_is_still_a_change tests/test_production.py::test_missing_model_source_is_refused_at_binding`
on the unmodified code: `4 failed, 1 passed in 1.57s`.

```
FAILED tests/test_model_consumption.py::test_binding_after_a_build_keeps_rest_placements[OffsetPair]
E       assert [<machinome.n...7bd799c29190>] == [<machinome.n...7bd7efb99250>]
E         Left contains one more item: <machinome.node.operations.Translation object at 0x7bd799c29190>
tests/test_model_consumption.py:375: AssertionError
FAILED tests/test_model_consumption.py::test_binding_after_a_build_keeps_rest_placements[HeldPair]
E         Left contains one more item: <machinome.node.operations.Translation object at 0x7bd799c2a2a0>
tests/test_model_consumption.py:375: AssertionError
FAILED tests/test_model_consumption.py::test_missing_source_is_refused_at_construction
E       machinome.model.ModelInputChangedError: input observation failed: /tmp/pytest-of-asa/pytest-25/test_missing_source_is_refused0/never-existed.txt: [Errno 2] No such file or directory: '…/never-existed.txt'
FAILED tests/test_production.py::test_missing_model_source_is_refused_at_binding
E       machinome.model.ModelInputChangedError: input observation failed: /tmp/pytest-of-asa/pytest-25/test_missing_model_source_is_r0/never-existed.txt: [Errno 2] No such file or directory: '…/never-existed.txt'
```

Line 375 is the first operations comparison after `ModelSnapshot(model)`
(`assert fusion.b.operations == operations`). The guard
`test_source_deleted_after_binding_is_still_a_change` passed. Four red for
the reasons named, one green.

## 3. The change

- `machinome/model.py`, `ModelSnapshot.occurrences`, the non-assembly
  branch of `walk`: a node without `_production_rest` takes
  `node.__dict__.get("_prepared_rendered")` as its children; only when that
  is `None` is `render()` called, under the structure-only flag;
  `node.validate(children)` runs for both, outside the flag; the result is
  cached as `_production_rest` as before.
- `machinome/model.py`: `import errno`; in
  `ModelSnapshot._capture_existing`, before `observe_input(path)`, a path
  not in `self._inputs` that does not exist raises
  `FileNotFoundError(errno.ENOENT, f"{type(node).__name__} '{node.name}'
  names an input file that does not exist", str(path))`.
- `machinome/production/profile.py`, `Production.__init__`: the `except
  OSError` branch raises
  `ProductionExportError(f"{type(self).__name__} cannot bind: {reason}")`,
  `reason` being `f"{error.strerror}: {error.filename}"` when the error
  carries a filename and `str(error)` otherwise. It used to read `cannot
  observe profile inputs: {error}`; no test, page or spec quoted that
  message (`grep -rn "cannot observe profile inputs"` over `tests`,
  `machinome`, `docs` and `openspec/specs` found only the line itself).

No divergence from design.md.

The five new cases after the change: `5 passed in 1.39s`. `<focused>`:
`57 passed, 4 warnings in 7.35s` (wall 8.39 s), 1.6's 52 plus five.
`git -C <bench> status --short`: ` M machinome/model.py`,
` M machinome/production/profile.py`, ` M tests/test_model_consumption.py`,
` M tests/test_production.py` (the change directory is committed and was
unchanged at that point).

## 4. The reproductions and the originating project after the change

### 4.1 The doubling

`repro_doubling.py`:

```
--- Pair ---
facade-only                        b.operations=1 render()-> b ops=1 content=f435a10c
lifecycle-only                     b.operations=1 render()-> b ops=1 content=f435a10c
facade-then-lifecycle              b.operations=1 render()-> b ops=1 content=f435a10c
lifecycle-then-facade              b.operations=1 render()-> b ops=1 content before=f435a10c regenerated=f435a10c render()[1] ops=1
--- Holder ---
facade-only                        b.operations=1 render()-> b ops=1 content=f435a10c
lifecycle-only                     b.operations=1 render()-> b ops=1 content=f435a10c
facade-then-lifecycle              b.operations=1 render()-> b ops=1 content=f435a10c
lifecycle-then-facade              b.operations=1 render()-> b ops=1 content before=f435a10c regenerated=f435a10c render()[1] ops=1
```

`repro_assemble.py`:

```
Pair: assemble() then facade: b.operations 1 -> 1; _prepared_rendered set: True
Holder: assemble() then facade: b.operations 1 -> 1; _prepared_rendered set: True
```

### 4.2 The missing file

`repro_missing.py`:

```
root files: Production(model): machinome.production.errors.ProductionExportError: RootProduction cannot bind: Root 'Root' names an input file that does not exist: <scratch>/never-existed.txt
root files: ModelSnapshot(model): builtins.FileNotFoundError: [Errno 2] Root 'Root' names an input file that does not exist: '<scratch>/never-existed.txt'
child files: Production(model): machinome.production.errors.ProductionExportError: RootProduction cannot bind: Nut 'nut' names an input file that does not exist: <scratch>/never-existed.txt
child files: ModelSnapshot(model): builtins.FileNotFoundError: [Errno 2] Nut 'nut' names an input file that does not exist: '<scratch>/never-existed.txt'
```

The traceback printed for the first line: `FileNotFoundError: [Errno 2]
Root 'Root' names an input file that does not exist: '…'` / "The above
exception was the direct cause of the following exception" /
`machinome.production.errors.ProductionExportError: RootProduction cannot
bind: …`.

### 4.3 The Curta production slice through the overlay

`<curta>` again, the same warm build directory:

```
......                                                                   [100%]
6 passed in 117.04s (0:01:57)
wall 118.70 s
```

Before: 6 passed in 117.56 s, wall 119.19 s. After: 6 passed in
117.04 s, wall 118.70 s. `git -C <project> status --short` listed the same
four untracked entries before and after; `git -C <project> rev-parse
--short HEAD` printed `1f3dc22`.

## 5. Records

- 5.1 `docs/project/changelog.rst`: design.md Decision 5's bullet appended
  to the one `Unreleased` section, after the `clocked-snapshot-identity`
  bullet.
- 5.2 `grep -rn "ModelSnapshot\|ModelInputChangedError\|ProductionExportError" docs --exclude-dir=adrs --exclude-dir=releases`
  (changelog excluded) finds only `docs/reference/api.rst:144`, the Model
  consumption section. Its paragraphs stay true: "Rest-only structural
  reading preserves the running state", and "A source, instruction,
  evidence or consumed artifact replacement invalidates the whole shared
  production with `ProductionInputChangedError`" (a replacement of an
  observed file, which this change leaves as it is). `grep -rln missing`
  over the same tree lists `architecture.md`, `reference/sphinx.rst`,
  `reference/cli.rst`, `reference/api.rst`, `concepts/running.rst` and the
  changelog; the one production line among them is `api.rst:91`, "A
  missing instruction file refuses requested steps or export without
  producing a partial bundle", unchanged and still true. `render()` near
  "once" (`grep -rn -i "render().\{0,60\}once\|once.\{0,60\}render()"`)
  finds `api.rst:193` (an assembly's `render()` that reads no driver runs
  once per instance), `concepts/rest-and-motion.rst:91`,
  `tutorial/02-input.rst:76` and `tutorial/04-relations.rst:43`, all about
  rest and motion, none about consumption; all stay true.
  `docs/architecture.md`, "Independent production consumption", says the
  facade reads "without running simulation or preparing the tree" and
  "Any observed change invalidates all bindings": the walk reads
  preparation's result without invoking it, and a missing file was never
  observed, so both stay true. No manual change.

## 6. Warts

- 6.1 The two items, from "- **Defect: binding a production after a build
  doubles the placements of" to its "**Untriaged.**" and from "- **A
  missing input file at binding escapes `Production(model)` as the
  facade's own error.**" to its "**Untriaged.**", moved verbatim from
  `workflow/warts.md`, section "Findings from the adversarial review of the
  framework cycle `production-layer` (4 October 2026)", to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md` under
  `` ## `production-reads-once` ``, after the `clocked-snapshot-identity`
  entry, with the "From …, items 1 and 2:" line and a "What shipped"
  paragraph. The section's introduction and its other seven items stay in
  `warts.md`.
- 6.2 New section "## Findings from the framework cycle
  `production-reads-once` (2026-10-07)" in `warts.md`, after the
  `clocked-snapshot-identity` findings, two bullets, each **Untriaged.**,
  confirmed after the change by `<scratch>/probe_open_questions.py`
  (copied below), run as
  `pytest -q -s -p no:cacheprovider --basetemp=<scratch>/probe-basetemp <scratch>/probe_open_questions.py`
  from the bench (`2 passed in 0.22s`; each test prints what it met):

  ```
  ModelSnapshot.occurrences: machinome.model ModelInputChangedError input observation failed: /nonexistent/render-made.txt: [Errno 2] No such file or directory: '/nonexistent/render-made.txt'
  Production.bom: machinome.production.errors ProductionInputChangedError input observation failed: /nonexistent/render-made.txt: [Errno 2] No such file or directory: '/nonexistent/render-made.txt'
  Production(model): machinome.model ModelInputChangedError input validation failed: Project source changed at production model read: /tmp/machinome-generation-rbaikp55/generation_fixture_…/dimensions.py (expected SourceObservation(…, size=10, mtime_ns=1791336971574304284, …), found SourceObservation(…, size=10, mtime_ns=1791336971606304858, …))
  ```

  ```python
  """Confirm the two neighbouring cases production-reads-once leaves alone.

  1. A missing source on a child that only render() creates is met by the
     lazy structural walk, not at construction.
  2. A source changed between a verified load and binding escapes
     Production(model) as ModelInputChangedError.
  """

  from machinome.model import ModelSnapshot
  from machinome.node.assembly import AssemblyNode
  from machinome.node.leaf import LeafNode
  from machinome.production.profile import Production

  from tests.test_source_generation import ScratchLoadProject


  class Nut(LeafNode):
      def render(self):
          raise AssertionError("never rendered")


  class Spawner(AssemblyNode):
      def render(self):
          made = Nut()
          made.files.add("/nonexistent/render-made.txt")
          return [made]


  class SpawnerProduction(Production[Spawner]):
      pass


  def test_render_created_child_missing_input_at_first_read():
      snapshot = ModelSnapshot(Spawner())
      try:
          snapshot.occurrences
      except Exception as error:
          print("ModelSnapshot.occurrences:", type(error).__module__,
                type(error).__name__, error)
      production = SpawnerProduction(Spawner())
      try:
          production.bom
      except Exception as error:
          print("Production.bom:", type(error).__module__,
                type(error).__name__, error)


  class ChangedBeforeBinding(ScratchLoadProject):
      def test_changed_executed_source_binding_a_production(self):
          node = self.load_generation()

          class ModelProduction(Production[type(node)]):
              pass

          self.write("dimensions.py", "VALUE = 2\n")
          try:
              ModelProduction(node)
          except Exception as error:
              print("Production(model):", type(error).__module__,
                    type(error).__name__, error)
          else:
              print("Production(model): no error")
  ```

  The review answered design.md Open Questions 2 and 3 as "filed as a
  finding"; both are filed so.

## 7. Sync and archive

- 7.1 By hand. In `openspec/specs/model-consumption/spec.md`, "Structure
  reading preserves running state" and "Facts and artifact copies use a
  coherent generation" each take the delta's added sentence at the end of
  their statement and the added scenario after their existing one; in
  `openspec/specs/production-assets/spec.md`, "Independent typed bound
  productions" takes its added sentence before "Production SHALL expose
  lazy bom, …" and its added scenario after "Two profiles share a model".
  Before the edit, `python <scratch>/diff_delta.py <bench>
  <bench>/openspec/changes/production-reads-once` (it splits each spec into
  requirement blocks and prints a unified diff of each delta requirement
  against its baseline) showed, for each of the three, only the one
  statement line replaced by itself plus the added sentence and four added
  scenario lines. After it, the script prints the three requirement
  headers and no diff lines. `git diff --stat -- openspec/specs`:
  `model-consumption/spec.md | 12 ++++++++++--`,
  `production-assets/spec.md | 6 +++++-` (15 insertions, 3 deletions).
  `openspec validate production-reads-once`: "Change
  'production-reads-once' is valid". `openspec validate model-consumption`
  and `openspec validate production-assets`: each "Specification … is
  valid".
- 7.2 `openspec archive production-reads-once --yes --skip-specs` (the
  specs were synced by hand in 7.1, so the CLI's own sync was skipped):
  "Change 'production-reads-once' archived as
  '2026-10-07-production-reads-once'". Its warnings: the Why section's
  length, and 23 of 26 tasks complete (7.2 to 7.4, done after it and
  ticked in the archived copy). `openspec validate --specs`: `Totals: 45
  passed, 0 failed (45 items)`.
- 7.3 On `machinome/model.py`, `machinome/production/profile.py`,
  `tests/test_model_consumption.py` and `tests/test_production.py`, on the
  working tree and on the four files as they are at HEAD (extracted with
  `git show HEAD:<file>` into `<scratch>/head/`):
  - `flake8 --max-line-length=89` (pyenv shim, flake8 7.3.0): no finding,
    exit 0, after and at HEAD.
  - `black --check` (26.5.1, default line length): all four files "would
    reformat" at HEAD and after; the four files follow black at line
    length 79, not the default. At `-l 79 -t py311` the first check after
    the change found one line, the new `with pytest.raises(FileNotFoundError,
    match="Compound 'compound'") as refused:` (83 characters), which was
    wrapped in the file's style. After that, `black -l 79 -t py311 --diff`
    changes 2 lines after and 2 lines at HEAD, the same pre-existing slice
    `local[index + 1:]` in `profile.py`; nothing in a line this change
    wrote. flake8 rerun after the wrap: exit 0.
- 7.4 `<focused>`, on the final tree: `57 passed, 4 warnings in 7.90s`
  (wall 9.01 s). The full suite, on the final tree, alone (`ps` showed no
  run of ours), `pytest -q -p no:cacheprovider` at the bench root: exit 0,
  wall 635.06 s, `4677 passed, 4 skipped, 55 warnings, 6665 subtests
  passed in 632.62s (0:10:32)` (cycle 9 closed at 4672 passed; this change
  adds five). No failure, no `Too many open files`.

Nothing is committed. `git -C <bench> status --short` lists the changed
`docs/project/changelog.rst`, `machinome/model.py`,
`machinome/production/profile.py`,
`openspec/specs/model-consumption/spec.md`,
`openspec/specs/production-assets/spec.md`,
`tests/test_model_consumption.py`, `tests/test_production.py`,
`workflow/warts.md`, `workflow/archive/fix-warts-3-2026-10-06/resolved.md`
and `workflow/ongoing/fix-warts-3.md`, the change's directory moved to
`openspec/changes/archive/2026-10-07-production-reads-once/`.
