## Why

Two defects of the production layer, both recorded by the adversarial review
of the framework cycle `production-layer` in `workflow/warts.md`, section
"Findings from the adversarial review of the framework cycle
`production-layer` (4 October 2026)":

> **Defect: binding a production after a build doubles the placements of
> children positioned in a rigid internal node's `render()`.** The
> `model-consumption` spec's scenario "Read an advanced machine" promises
> that structural reading leaves established operation values unchanged.
> It holds when the facade reads first and fails when the lifecycle ran
> first: `ModelSnapshot.occurrences` (`machinome/model.py:354-365`) calls
> `render()` on every non-assembly internal node unless its own
> `_production_rest` cache exists, and a node already rendered by
> `_prepare()` or `assemble()` has no such cache, so the author's `render()`
> runs a second time and re-applies every `translate`/`rotate` to the same
> declared children. The doubled structure is then cached and returned by
> every later `render()` (`machinome/node/internal.py:39-42`); nothing
> raises. [...] Remedy shape: the walk reuses the node's
> `_prepared_rendered` when the lifecycle already rendered it and renders
> once otherwise, pinned by a red test in the lifecycle-first order that
> compares operations and the regenerated content id. **Untriaged.**

> **A missing input file at binding escapes `Production(model)` as the
> facade's own error.** A node whose `files` names a path that does not
> exist makes the constructor raise
> `machinome.model.ModelInputChangedError("input observation failed: …")`:
> `Production.__init__` (`machinome/production/profile.py:281-288`) wraps
> only `OSError`, so the production error taxonomy is bypassed, and the
> message says a file changed when it never existed. **Untriaged.**

**Reproduced on the bench `fix-warts-3` at `3fc3fc1`**, with the
interpreter check printing
`/home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py`.

The first defect, with the review's fixture: a faceted `FusionNode` of two
self-materializing boxes (a `LeafNode` whose `render()` returns a trimesh box
and whose `materialize()` publishes it), the second box translated by
`[1, 0, 0]` in the fusion's `render()`, alone and inside an assembly. Each
order runs in its own build root. "Lifecycle" is `trigger_stl()`, the build's
own preparation; "facade" is `ModelSnapshot(model).occurrences`:

```
--- Pair ---
facade-only            b.operations=1 render()-> b ops=1 content=f435a10c
lifecycle-only         b.operations=1 render()-> b ops=1 content=f435a10c
facade-then-lifecycle  b.operations=1 render()-> b ops=1 content=f435a10c
lifecycle-then-facade  b.operations=2 render()-> b ops=2 content before=f435a10c regenerated=fd3b003d render()[1] ops=2
--- Holder ---
(the same four lines)
```

`assemble()` in place of `trigger_stl()` doubles the same way (`b.operations
1 -> 2`), and in both cases the fusion's `_prepared_rendered` is set when the
facade reads it. The fused STL regenerated after the doubling has another
content identity: the second box moved by 2 mm, not 1.

Why it happens: `_prepare()` (`machinome/node/base.py:891-916`) renders an
internal node once and keeps the result in `_prepared_rendered`; `assemble()`
reaches the same render through `_prepare()` and `_require_rendered()`. The
facade's walk (`machinome/model.py:353-365`) looks only for its own
`_production_rest` and, finding none, calls `render()` again. A declarative
`render()` that positions children re-applies its `translate` to the same
child instances, and the wrapper in `machinome/node/internal.py:67-70` then
returns the doubled `_production_rest` to every later `render()`. Assemblies
do not double: their rest is cached in `_rest` on first render
(`machinome/node/assembly.py:40-77`) and `_rest_children` reuses it.

The second defect, with a `Production[Holder]` whose model's child `nut`
names a file that does not exist in its `files`:

```
root files:  Production(model):    machinome.model.ModelInputChangedError: input observation failed: <path>: [Errno 2] No such file or directory: '<path>'
root files:  ModelSnapshot(model): machinome.model.ModelInputChangedError: input observation failed: <path>: [Errno 2] ...
child files: Production(model):    machinome.model.ModelInputChangedError: input observation failed: <path>: [Errno 2] ...
child files: ModelSnapshot(model): machinome.model.ModelInputChangedError: input observation failed: <path>: [Errno 2] ...
```

`ModelSnapshot.__init__` observes every existing node's sources in
`_capture_existing` (`machinome/model.py:144-156`); `observe_input`
(`:205-227`) turns any failure of a first observation, a missing file
included, into `_fail("input observation failed: …")`, which raises
`ModelInputChangedError` (`:235-237`). `Production.__init__`
(`machinome/production/profile.py:281-288`) catches only `OSError`. The
error names the path but not the node, and calls it a change.

## What Changes

- **The facade reads a built rigid internal node from the build's render.**
  In `ModelSnapshot.occurrences`, a non-assembly internal node without
  `_production_rest` whose `_prepared_rendered` is set takes those children
  as its rest, validates them and caches them as `_production_rest`; only a
  node the lifecycle never rendered is rendered, once, under the
  structure-only flag, as today. The author's `render()` therefore runs at
  most once per instance whichever of the facade and the lifecycle reads
  first. Nothing else in the walk changes.
- **A missing input file is refused at binding as missing.**
  `ModelSnapshot._capture_existing` checks each source path of each existing
  node before observing it: a path not yet observed by this snapshot that
  does not exist raises `FileNotFoundError` whose message names the node
  (`Nut 'nut'`) and whose `filename` is the path. A path that was observed
  and later changed or vanished is still refused by `validate()` and
  `observe_input()` with `ModelInputChangedError`, as today.
- **`Production(model)` refuses it with `ProductionExportError`.** The
  constructor's existing `except OSError` branch already maps an input it
  cannot observe to `ProductionExportError`; its message is reworded so it no
  longer calls every such input a profile input:
  `HolderProduction cannot bind: Nut 'nut' names an input file that does
  not exist: <path>`.
- **Tests.** In `tests/test_model_consumption.py`: the lifecycle-first
  fixture of the reproduction (the fusion alone and inside an assembly),
  comparing child operations and the regenerated content identity (red
  today); the facade's missing-file refusal (red today); a guard that a
  file deleted after binding is still a changed input (green today). In
  `tests/test_production.py`: the binding refusal (red today).
- **Records.** A changelog bullet under `Unreleased`; the two warts items
  move to the campaign's `resolved.md`; the two neighbouring cases this
  change leaves alone are filed as new findings (design.md, Open Questions
  2 and 3).

**Deliberately out**, with the reason:

- **The other items of the review's section** (the bundle's absolute paths,
  the Markdown gate, the overlap scope, declaration-path shape,
  `check_status`, the facade's copy of the lifecycle, the bytes held in
  memory) belong to the next cycle, `production-reports-in-scope`, or stay
  untriaged.
- **The lifecycle is not changed.** `_prepare()`, `assemble()` and the
  `_declarative_render` wrapper keep their behaviour; `_prepare()` already
  reuses the facade's `_production_rest` when the facade read first (the
  wrapper returns it), which is why the facade-then-lifecycle order holds.
  Making every internal node's `render()` run at most once in the wrapper
  would change a contract every tree walker relies on, for a defect only
  the facade's walk has.
- **`observe_input` keeps its contract.** A consumer that observes a
  missing evidence path through the public `observe_input` still gets
  `ModelInputChangedError`; production checks its instruction and evidence
  paths for existence before observing them
  (`machinome/production/profile.py:937-939`) and refuses a missing one at
  `steps` or `export` with `ProductionExportError`, as the spec says.
  Changing `observe_input` would also change the lazy walk's failure for a
  child created inside `render()` (design.md, Open Question 2).
- **A source changed between a verified load and binding** also escapes
  `Production(model)` as `ModelInputChangedError`, because the constructor
  catches only `OSError`. The brief keeps the facade's error for a file
  that did change as it is; the case is filed as a finding (design.md, Open
  Question 3).
- **No ADR.** ADR-175 already says structural reads never invoke
  preparation and that consumption preserves the operations; this change
  makes the facade do so when preparation ran first. The binding error is
  the existing taxonomy's.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `model-consumption`: two requirements are modified.
  - "Structure reading preserves running state": a sentence states that a
    rigid internal node the lifecycle already rendered is read from that
    render, so `render()` runs at most once per instance in either order.
    One scenario is added, "Read a machine the lifecycle already built".
    The existing scenario "Read an advanced machine" is carried unchanged.
  - "Facts and artifact copies use a coherent generation": a sentence
    states that a source a node names that does not exist when the snapshot
    is constructed is refused with `FileNotFoundError` naming the node and
    the path, never reported as changed, and that an observed input that
    later changes or vanishes still invalidates the generation. One
    scenario is added, "Bind a model naming a missing file". The existing
    scenario "Artifact replaced during copying" is carried unchanged.
- `production-assets`: one requirement is modified.
  - "Independent typed bound productions": a sentence states that a file
    the supplied model names that does not exist is refused at binding with
    `ProductionExportError` naming the node and the path. One scenario is
    added, "A model names a file that does not exist". The existing
    scenario "Two profiles share a model" is carried unchanged.

## Impact

- **Code:** `machinome/model.py`: the non-assembly branch of `walk` inside
  `ModelSnapshot.occurrences` (`:353-365`) and
  `ModelSnapshot._capture_existing` (`:144-156`), plus `import errno`.
  `machinome/production/profile.py`: the message of the `except OSError`
  branch of `Production.__init__` (`:285-288`). No other function changes.
- **Tests:** `tests/test_model_consumption.py` gains a mesh box, a fusion
  that positions one of two boxes, an assembly holding it, and four tests;
  `tests/test_production.py` gains one test. The fusion fixture needs the
  mesh engine (the `mesh` extra), as every mesh-fusion test of the suite
  does.
- **Public surface:** `ModelSnapshot(model)` raises `FileNotFoundError`
  instead of `ModelInputChangedError` for a node source that does not exist
  at construction; `Production(model)` raises `ProductionExportError`
  instead of `ModelInputChangedError`. No new name. A search of every `*.py`
  under `projects/` finds `ModelSnapshot` only in the Curta production
  slice's test, which binds an existing model.
- **Manual:** `docs/reference/api.rst` says a missing instruction file
  refuses steps or export, and that a replacement invalidates the binding
  with `ProductionInputChangedError`; both stay true. No page says what a
  missing model source does. No manual change; the changelog gets one
  bullet.
- **Projects:** the Curta production slice
  (`projects/Calculators/Curta-Type-I-3x`, worktree
  `WTs/production-layer-3x`, branch `production-layer-3x`, `7c9121e`)
  prints leaves, so it cannot meet the first defect, and binds a model whose
  files exist, so it cannot meet the second; it validates that nothing
  regresses. At `7c9121e` it cannot be collected against this bench: its
  test imports `from machinome.node import AssemblyNode, StepNode`, which
  the 0.8 root refuses, and its simulation predates the Curta's 0.8
  migration (`2a47f72` on `main`). The validation therefore runs the
  slice's unchanged `production/` package, copied into the scratchpad with
  that one import line rewritten to the 0.8 modules, over the Curta's
  `main` (`1f3dc22`), with the scratchpad's `SOLID_BUILD_DIR` and nothing
  written in the project. At Stage P it passes 6 tests in 119.02 s (wall
  120.10 s, warm build directory) against the bench, and the Curta's
  `git status --short` is the same before and after. The slice's own README command at `7c9121e`
  fails with that `ImportError` before and after this change.

## Authorization

The pilot's mandate of 6 October 2026 for the fix-warts-3 campaign
(`workflow/ongoing/fix-warts-3.md`, "Mandate"): "work on the items you can
autonomously, orchestrating opus subagents and using empirical evidence
from projects to validate, other than your adversarial review. if
something needs my input, record and defer, you'll go unsupervised." This
change is the campaign table's cycle 10, `production-reads-once`, validated
in the Curta-Type-I-3x production slice. design.md's three Open Questions
each carry a recommendation, and none blocks the fix.
