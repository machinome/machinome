## Context

### The reproduction, at bench `2acba68`

Every command ran with the bench's own code
(`python -c 'import machinome; print(machinome.__file__)'` printed
`/home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py`),
as `env -C <dir> PYTHONPATH=<bench> SOLID_BUILD_DIR=<scratch build dir>
timeout <bound> /home/asa/devel/machinome/.venv/bin/machinome build
<reference>`. `<scratch>` below is the campaign scratchpad's `cycle2/`
directory.

| what was built | bound | exit | `START` lines | wall |
|---|---|---|---|---|
| `tests/scad_where_read_project/native.py:StlBench` (bench as cwd) | 30 s | 124 | 9 | 30.0 s |
| `tests/scad_where_read_project/machine.py:Machine` | 60 s | 124 | 17 | 60.0 s |
| `tests/scad_where_read_project/native.py:ExactBench` | 60 s | 0 | 1 | 6.5 s |
| `tests/scad_where_read_project/machine.py:Mixed` | 60 s | 0 | 1 | 6.7 s |
| `tests/scad_where_read_project/legacy.py:LegacyBench` | 60 s | 1 | 1 | 6.4 s (refused by design: "node bracket (Bracket) produced no STL") |
| `Robots/hexapod_spiderbot_model`, its manifest's model, in a fresh detached worktree of `7ef1e36` | 120 s | 124 | 34 | 120.0 s |
| scratch project, one `StlNode` whose mesh is 1 ms newer than its module, every file an hour old (`<scratch>/grown_set_probe.py`) | 45 s | timed out | 36 | 45.0 s |
| the same, mesh 1 s newer | 45 s | timed out | 36 | 45.0 s |

The fixture's files were written by the bench's checkout on 6 October at
14:10:31: `bracket.stl` at `.478951896`, `native.py` at `.479951928`,
`tab.stl` at `.480951959`. The hexapod worktree's, on 6 October at
15:31: `pyproject.toml` `10.958`, `simulation/printed.py` `10.967`,
`simulation/spiderbot.py` `10.969`, `stl/Frame.stl` `11.008`, `stl/Tip.stl`
`11.031`. A checkout writes in path order; whatever sorts after the modules
is newer than they are.

### The mechanism

`<scratch>/trace_one_generation.py` runs one builder generation in-process
(`Builder(reference, watch=False, lifecycle=True)._start()`), traces the
lines `_start` executes with `sys.settrace`, and wraps the loaded node's
`_prepare` to print the source set before and after assembly and whether
every assembled file is in the assembly phase's census. It edits nothing.

| root | sources after load (largest) | after `_prepare` (largest) | joined during assembly | assembled files missing from the census | outcome, last lines of `_start` |
|---|---|---|---|---|---|
| `StlBench` | 1, `native.py` `1791295831479951928` | 3, `tab.stl` `1791295831480951959` | `bracket.stl`, `tab.stl` | none | `SOURCE_CHANGED` after 391, 392, 393 |
| `Machine` | 2, `machine.py` `1791295831479951928` | 4, `tab.stl` `1791295831480951959` | `bracket.stl`, `tab.stl` | none | `SOURCE_CHANGED` after 391, 392, 393 |
| `ExactBench`, `Mixed` | unchanged by assembly | | none | none | `CURRENT` |
| hexapod `Spiderbot` | 7, `simulation/spiderbot.py` `1791300670969425286` | 30, `stl/Tip.stl` `1791300671031427224` | 23 meshes | none | `SOURCE_CHANGED` after 391, 392, 393 |

Lines 389-393 of `machinome/core/builder.py`:

```python
            # Assembly discovers the complete source union. An edit during it
            # invalidates the loaded classes before any later publication.
            if (assembly_failure is None and
                    self.node.mtime_ns != loaded_source_mtime_ns):
                return BuildOutcome.SOURCE_CHANGED
```

`loaded_source_mtime_ns` is taken at lines 337-348, right after load, over
the root's `files` as they are then: the root module's import closure.
`InternalNode.materialize` (`machinome/node/internal.py`) then unions every
child's `files` into the root's during `_prepare`, and an `StlNode` carries
its mesh in its own `files` from construction (`machinome/node/stl.py`).
`AbstractBaseNode.mtime_ns` is the largest mtime over the current `files`, so
when a mesh newer than every module joins, the comparison differs although
nothing changed. The assembly phase had just closed without a
`SourceChanged`: its census, which observed each joiner when its node's
`_prepare` called `track_sources` and re-observed every one at
`checkpoint('assembly post')`, found them all unchanged. The generation is
coherent; only the aggregate disagrees. Every fresh generation repeats it,
and the supervisor (`machinome/manager/build.py`, `Build.build`) retries
`SOURCE_CHANGED` forever; the development loop respawns the same way.

### How the comparison came to be wrong

- `c9b7669` (22 August 2026) introduced `loaded_source_mtime_ns`, taken
  after `self.node.assemble()`, over the complete source union.
- `769486f` (7 September 2026, "fix: lock artifact-producing assembly")
  moved assembly under the build lock, after the moment
  `loaded_source_mtime_ns` is taken, and added the comparison above. From
  then on the remembered maximum covers only the loaded closure.
- `8d6bfed` (8 September 2026, ADR-084) introduced the source generation and
  its per-contributor census, and kept the comparison beside them.

### What the generation already guarantees

ADR-084 and the baseline requirement "One fresh builder owns one stable
source generation": a project module is observed before execution and
after load; a contributor discovered during assembly joins the assembly
phase's census when its node's `_prepare` declares it (`track_sources`), or
through `consumed_source` and `coherent_read` when it is read; the phase's
exit re-observes every path it holds, uncached, and raises `SourceChanged`
on any difference of device, inode, size, mtime or ctime; every later phase
(`artifact_currency`, each `artifact_pass`, `publication`) enters by
re-observing every contributor the generation remembers, the joiners
included, and publication checks again immediately before the manifest is
written. A contributor appearing after the census is sealed is itself a
source change. The aggregate comparison adds nothing to this but its false
positive.

## Goals / Non-Goals

**Goals:**
- A build whose files do not change while it runs completes in one
  generation, whatever the order of their timestamps.
- An edit to any contributor after the build observed it, a joiner
  included, still stands the build down before anything stale is published.
- The seven `tests/test_scad_presentation.py` tests finish on a fresh
  checkout, so the full suite runs on this bench without deselection.

**Non-Goals:**
- The three-hour hang of the Cycloidal actuator (Open Question 1).
- The lock-wait comparison, the no-generation branch's semantics, artifact
  currency, stamps, and the census itself.

## Decisions

### 1. A contributor is compared with its own observation

The rule: a source contributor is current while a fresh, uncached
observation of it equals the observation taken when it joined this
generation — `(device, inode, size, mtime_ns, ctime_ns)`, ADR-081's
identity. A contributor in the loaded closure joins at load; one a part
brings joins during assembly, when its node's `_prepare` declares it or
when it is read. No timestamp is compared with another file's, with the
build's start or with the clock.

Why a file written 1 ms after the module, long before the build, is
current: the build observes it before using it, reads it, and observes it
again at the phase's close; the artifacts derived from it are derived from
exactly the bytes on disk, and they are stamped with the node's largest
source mtime over the grown set, so artifact currency already counts it.
A file edited before the build first observed it is read in its edited
state: nothing loaded is stale. A file edited after it joined fails the
next observation and stands the build down. Build artifacts are not
contributors: they are written under the build directory and never enter
`files` (the traces' assembled sets hold only project sources), so a build
writing its own artifacts cannot trip the rule.

### 2. The code: the comparison applies only without a generation

`machinome/core/builder.py`, `Builder._start`, the post-assembly check:

```python
            # Without a source generation -- reached only through a patched
            # loader, since a reference outside a project does not load --
            # the loaded maximum is this branch's only record of what was
            # loaded. With one, the assembly phase's closing check has
            # already compared every contributor with its own observation,
            # those that joined during assembly included (ADR-084): a newer
            # file joining moves the grown set's maximum without any source
            # having changed, and must not stand the build down.
            if (assembly_failure is None and
                    self._source_generation is None and
                    self.node.mtime_ns != loaded_source_mtime_ns):
                return BuildOutcome.SOURCE_CHANGED
```

Nothing else in the file changes. The lock-wait comparison above it
(`if self.node.mtime_ns != loaded_source_mtime_ns:` after
`checkpoint('after_lock')`) compares the same set the loaded maximum was
taken over, so growth cannot reach it; with a generation it is redundant
with `after_lock`, without one it is the branch's guard pinned by
`test_source_moving_under_a_waiting_build_stands_it_down`. It stays.

`project_source_generation` returns a generation or raises
`ProjectManifestError`; `_start` falls back to no generation only on that
error, and `load_node` then fails for the same reason before any assembly,
unless a test patches it. Every real build therefore takes the generation
branch.

### 3. Tests, red first

In `tests/test_retained_builder_generation.py`:

- **RED** `JoinedContributorTest` (in-process, `_InProcessBuilderTest`):
  a real project directory (`pyproject.toml` declaring `model.py`, as
  `FilesystemGenerationRaceTest` does), its `model.py` dated an hour back,
  and a joiner `part.stl`. A node double whose `mtime_ns` is computed from
  its current `files` on every read (the real rule; `_StableNode` stores a
  fixed value), `files = {model.py}`, and a `_prepare` whose side effect
  calls `machinome.source_generation.track_sources([joiner])` and adds the
  joiner to `files`, as a real child's `_prepare` and its parent's union do.
  The real `project_source_generation`; `load_node` patched to return the
  double; `_published_model_is_current` returning `False`, `generate_stl`
  an `AsyncMock` returning `CURRENT`, `_write_viewer_snapshot` a `Mock`
  returning `True`. Subtests for the joiner dated 1 ms and 1 s after the
  module, and an hour after the present: `_start()` returns `CURRENT` and
  `_write_viewer_snapshot` is called once. Red today: `SOURCE_CHANGED`,
  the snapshot never written.
- **GUARD** in the same class: the side effect, after `track_sources`,
  replaces the joiner with different bytes beneath its own mtime
  (`os.replace` of a sibling stamped with the old mtime). `_start()`
  returns `SOURCE_CHANGED`, `generate_stl` is not awaited and
  `_write_viewer_snapshot` is not called. Green before and after: the
  assembly phase's closing check catches it either way.
- **RED** `FreshCheckoutBuildTest` (the supervisor and real spawned
  builders, in the shape of `FreshProcessBatchTest`): one project per
  subtest, its package named for the subtest (`checkout_ms`,
  `checkout_s`: names no other test's project uses, because `Build.build`
  resolves the model in the test's own process first and its module
  cache must not serve one subtest the other's classes), with `parts.py`
  declaring `class Tab(StlNode): stl_source = 'tab.stl'` and
  `class Bench(AssemblyNode)` rendering `[Tab()]`, a `tab.stl` written
  with `trimesh.creation.box()`, and `pyproject.toml` declaring
  `<package>.parts:Bench`; every file dated an hour back and `tab.stl`
  1 ms (one subtest) or 1 s (the other) after the module.
  `Build().build('<package>.parts:Bench')` in the project
  (`chdir`, `SOLID_BUILD_DIR` and `PYTHONDONTWRITEBYTECODE` as
  `FreshProcessBatchTest.project_environment` sets them), with
  `machinome.manager.build.Process` wrapped to record each child and to
  raise `AssertionError` naming the first child's exit code when a second
  is spawned: the bound is the test's own, and it ends the red run after
  one generation instead of a timeout. Expect status 0, one child, exit
  code 0, and a `viewer.json` naming the mesh's artifact. Red today:
  "a second builder was spawned ... the first exited 11".

Existing stand-down tests stay green unedited:
`test_builder_lifecycle.py::RedundantAndSupersededBuildTest`,
`test_retained_builder_generation.py::RetainedGenerationRaceTest` and
`::FilesystemGenerationRaceTest`, `test_source_generation.py`.

### 4. No ADR

ADR-084 already decided that "source correctness now has an explicit
generation and phase boundary rather than depending on aggregate mtime or
post-load discovery", and rejected identifying a generation by aggregate
maximum mtime. This change removes a leftover that contradicts it; it
decides nothing new.

### 5. Words

- `docs/project/changelog.rst`, under `Unreleased`, one bullet:

  > **A build of a fresh checkout finishes.** `machinome build` and
  > `machinome develop` no longer start over without end when a file a
  > part reads, such as an ``StlNode``'s mesh, is newer than the module
  > declaring it, as a fresh clone or worktree leaves a mesh checked out
  > after its module. Each source is compared with what the build first
  > saw of it, so a build stands down only for a file that changed after
  > the build read it (build-settles-on-a-grown-source-set).

- No manual page states the aggregate comparison (searched: `docs/` for
  "stand down", "SOURCE_CHANGED", "maximum mtime", "aggregate");
  `docs/architecture.md`'s source-generation paragraph already describes
  the census as the authority and stays as it is.

## Alternatives considered

- **A. Compare a joiner with the time the build started.** Rejected. A
  file's mtime is set by whoever wrote it — the guest, a virtiofs or NFS
  host, `tar`, `rsync -t`, `cp -p` from another machine — and the build's
  start by the builder's clock; a source dated in the future (a host clock
  ahead of the guest, an archive from a machine with a fast clock) would
  stand every generation down: the same endless loop. It would also be
  weaker than the census it would sit beside, which compares the whole
  identity, inode and ctime included.
- **B. Take the loaded maximum after assembly again** (the order before
  `769486f`). Assembly now runs under the lock, after the lock-wait
  check, so the maximum would have to be retaken there; the comparison it
  then guards is the assembly phase's own closing check. It adds nothing.
- **C. Compare only the loaded set's maximum, in both branches.** Correct,
  but it needs the builder to keep the loaded set and stat it (the node
  doubles of the lifecycle tests have no paths to stat), and with a
  generation it repeats the census's check over a subset.
- **D. Delete the comparison in both branches.** Equally small in the
  generation branch. In the no-generation branch it removes the only
  post-assembly guard of a path no real build takes; keeping it there
  keeps that branch exactly as it was. Open Question 2.

## Risks / Trade-offs

- [A contributor reaches the root's `files` without being declared to the
  assembly census] → it would then be first observed when the
  `artifact_currency` phase opens, after the assembly that read it. Every
  child declares its `files` at the start of its `_prepare`, and the root's
  set is the union of its children's, so the traces found every assembled
  file in the census (the tables above); the applier repeats that check on
  the fixture and on the hexapod.
- [The no-generation branch keeps a comparison that a growing set can
  move] → reachable only with a patched loader; recorded in the comment and
  in Open Question 2.

## Proof plan

1. Baseline on the unmodified tree: the bounded builds of the table above
   for `StlBench` and `Machine`, the probe, and the trace, recorded in
   `evidence.md` with the probes' sources (the scratchpad is not durable).
2. The three tests of Decision 3: the two RED ones seen red for the reason
   named, the GUARD green.
3. The change; the three tests green; the focused builder set green
   (Stage P on the unmodified tree: `tests/test_retained_builder_generation.py
   tests/test_builder_lifecycle.py tests/test_source_generation.py
   tests/test_builder_reload_resilience.py tests/test_build_lock.py`, 85
   passed, 7 subtests, 57.7 s).
4. The fixture: `machinome build` of `StlBench` and `Machine` exits 0 with
   one `START`; the whole of `tests/test_scad_presentation.py`, the seven
   tests included, passes with the fixture's files as the checkout dated
   them. (Run red, each of the seven would take its runner's 600 s timeout;
   cycle 1's evidence §4.3 and the bounded builds stand for the red.)
5. The catalogue: a fresh detached worktree of
   `Robots/hexapod_spiderbot_model`, built against the bench before (bounded,
   restarts) and after (exits 0), then removed.
6. The full suite, alone, with nothing deselected.

## Open Questions

1. **The three-hour hang** (the orchestrator, at the campaign's
   investigations cycle). Its project read a 35 MB STEP copied into the
   worktree after the checkout, the newest file there, so this mechanism is
   plausible; but the recorded observations — no child process and no
   artifact after three hours, 4 s of CPU in the parent — are not what the
   loop shows (a child per generation; assembly-time artifacts written).
   This change does not claim it. Recommendation: keep the entry in
   `warts.md` with a "Remaining (2026-10-06)" note, and move only the
   `mesh-engine` addendum, which this change closes, to the resolved
   record.
2. **The no-generation branch** (the orchestrator, at review). Recommended:
   gate the comparison to it (Decision 2), leaving the branch as it was.
   The alternative is to delete the comparison outright (Alternative D),
   one line smaller, at the cost of that branch's only post-assembly guard.
   Neither changes a documented promise or any real build.
3. **The brief's suggested rule** (the orchestrator). The cycle brief
   proposed comparing a joiner with the build's start; this design does not
   (Alternative A) because the census already answers the question
   without a clock and the clock rule loops on a future-dated file. No
   documented promise depends on the choice; it is recorded here so the
   divergence is reviewed rather than discovered.
