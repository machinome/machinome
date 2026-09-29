## Why

Almost all of a `machinome test` run goes into verdicts the project has
already reached in an earlier run. The ADR-070 memo keeps them only until
the process ends, and the studio floor starts a fresh `machinome test`
process for every run, so every floor run starts cold. Measured at framework
`main` bf24687 (`workflow/warts.md`, "3DPrintedClocks wall clock 02 and
strandbeest (2026-09-29, verdict memo across runs)"):

- 3DPrintedClocks `wall_clock_02` (22 tests, exact kernel): 1348.9 s cold,
  95% of it inside verdict-memo misses (1138 misses, 643 OCCT booleans at
  1.93 s each). With the memo already warm, the same run in the same
  interpreter took **18.35 s**: all 4238 asks were served and the verdicts
  were identical.
- strandbeest's walking demo (3 tests): 246.9 s cold, 92% inside misses
  (1055 booleans). Warm, it took **11.97 s**.

In the pilot's words: "something that hashes the whole set of meshes and
final positions, so that between runs, things that haven't changed won't have
to be reprocessed". On flexible parts: "we don't want cache for geometries,
we want cache for result of calculation based on state." ADR-070 measured
where flexible cost lies on the v8-engine root suite, on the exact kernel:
of the 1622.8 s left after its memo, 1499 s went to flexible-part
comparisons that the memo will not key at all.

## What Changes

- **A persistent tier beneath the per-run verdict memo.** When the in-process
  memo misses, the verdict is looked up in a per-project store before any
  boolean runs. A verdict that is computed goes into both tiers. The store
  holds the engine's raw verdicts: emptiness, volume and whether the exact
  kernel produced it. It holds no geometry. The run's volume epsilon is still
  applied after the memo is read.
- **A persisted key is state, never a path or a timestamp.** It is made of
  the content digest of each rigid solid's artifact (the BREP for the exact
  path, the STL for the faceted path), the evaluation path, the placement
  quantum, and the quantised relative placement cells (exactly ADR-090's
  key). It also carries an invalidation stamp. Nothing absolute is persisted.
  A rebuild that reproduces identical bytes still hits, and so does a project
  moved or copied together with its build directory. A byte change hidden
  under a preserved mtime misses.
- **Flexible pairs become cacheable in both tiers.** A flexible leaf is
  identified by its state: technology, defining module, the project-relative
  digest of its sources, its structural identity, its bound values and the
  digest of its serialized spec. That is the identity its Manifold cache
  already computes, without the absolute source path and without the metadata
  fingerprint. It is used on the exact path as well as the faceted one. A
  subclass that overrides the stock evaluation seam stays uncached. This
  amends ADR-070's "flexible parts are uncacheable by construction": that
  argument was against keying on names, where two bindings at one relative
  placement collide, and a state key has no such collision.
- **Invalidation needs no maintainer.** Every persisted key carries a stamp:
  the store format, the machinome version, a digest of every Python source of
  the running `machinome` package, the installed versions of the kernels and
  evaluators on the verdict path (`cadquery-ocp`, `cadquery`, `manifold3d`,
  `trimesh`, `molejo`), and the platform. A record written under any other
  stamp is never served.
- **The store lives at `<build root>/.verdicts/`.** It is excluded from Git
  along with the build directory. A project has one store: every declared
  model shares it, whether a run tests one model or all of them with
  `--all`. The builder's sweep spares it, because otherwise the next build
  would delete it. The format is lock-free: immutable, checksummed segment
  files, published by atomic rename and merged on read. Two runs of one
  project at once are therefore normal and lose nothing, and a run that
  starts reading while another merges the store still sees every verdict.
  If the store is corrupt, foreign, unreadable or unwritable, it is
  ignored and never raises. Its size has a fixed limit, and when the store is
  full the least recently used verdicts are evicted first.
- **Run policy, in ADR-073/ADR-090's shape.** `ComparisonPolicy` gains
  `verdict_store`, and `machinome test` gains
  `--verdict-store`/`--no-verdict-store` and reads `SOLID_TEST_VERDICT_STORE`
  (`on`/`off`) through the CLI's `.env` rule. A flag beats the environment,
  which beats the default. The default is on. The default run's output is
  unchanged byte for byte. A run with the store off says so on its summary
  line, in the same parenthesis as the faceted label and the quantum.
- **No verdict changes.** The persistent tier makes the assumption the
  in-process memo already makes: a verdict is a function of its key. It adds
  one more assumption, stability across processes, and the stamp covers that.
  If an identity cannot be established, a file has changed since it was
  loaded, or any other doubt arises, the result is a miss, and the miss costs
  what a cold run costs today.
- **One ADR amending ADR-070** records the persistent tier, the state
  identities and the stamp. It is written after implementation, with the
  measured numbers.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `test-framework`:
  - "An intersection verdict is computed once per run": a flexible leaf is
    now keyed on its state, and only identity-less nodes stay uncached.
  - "Run-level comparison kernel": the run's comparison policy gains the
    verdict-store switch, its resolution order, its error and its summary
    note.
  - New requirement, "A decided verdict is kept between runs of a project",
    for the persistent tier itself.
- `flexible-parts`: "Flexible faceted geometry has a bounded multi-binding
  working set". Flexible verdicts stop being "uncached". The geometry cache
  keeps geometry, and the verdict memo keys a flexible pair on the leaf's
  state.
- `cli`: "Test command" gains `--verdict-store`/`--no-verdict-store` and
  reads `SOLID_TEST_VERDICT_STORE`.
- `build-pipeline`: "A successful build sweeps unreferenced artifacts" now
  spares the verdict store.
- `user-documentation`: "The comparison kernels are documented". The fast
  tests guide explains the store, the switch and how to discard it, and the
  CLI page lists the flag and the variable.

## Impact

**Framework code.**
- `machinome/test.py`: `ComparisonPolicy`, `resolve_comparison_policy`,
  `_memoized`, the persistent form of `_verdict_key`, flexible identities
  through `_flexible_manifold`/`_fast_geometry` and the exact branch of
  `_engine_intersection_stats`.
- A new private module holds the store, its stamp and its digest memo. At
  its top level it imports only cheap standard-library modules and
  `machinome._artifact`. The stamp's metadata, platform and source reads
  happen at the first store use, and it never imports a kernel.
- `machinome/_artifact.py`: the store's directory name, so the builder's
  command path imports nothing new.
- `machinome/exact.py`: `cached_shape` records the observation it loaded
  from.
- `machinome/node/flexible.py`: one coherent state snapshot serves the
  faceted and exact identities.
- `machinome/core/builder.py`: the sweep prunes the store directory.
- `machinome/manager/test.py`: the flags, the summary note and the
  end-of-run flush.

Nothing the build produces changes, and neither does the published document
or the viewer.

**Tests.**
- Extended: `tests/test_intersection_memo.py`,
  `tests/test_flexible_cache_performance.py` (its "verdicts are not memoized"
  test is inverted), `tests/test_manager_test.py` and
  `tests/test_cli_lazy_imports.py` (neither the store module nor a
  `machinome build` dispatch adds a metadata, platform or kernel import).
- New: store tests, including cross-process runs.
- The framework suite's existing `tests/conftest.py` keeps its
  `collect_ignore` and gains a session pin that turns the store off, so
  boolean-counting tests keep their meaning. The store's own tests switch it
  on explicitly.

**Docs.**
- `docs/howto/fast-tests.rst`, `docs/reference/cli.rst`,
  `docs/project/changelog.rst`.
- `docs/architecture.md` (the Test framework memo paragraph and its flexible
  sentence).
- The new ADR and `docs/adrs/README.md`.
- `workflow/warts.md`.

**Projects.** The originating projects are where the evidence is measured,
one cold process then one warm process each:
- 3DPrintedClocks `wall_clock_02`;
- strandbeest's walking demo;
- for the flexible identity, the smallest `Vibecoded-demos/v8-engine`
  slice that puts a molejo valve spring into a pair:
  `v8_engine/valvetrain/test_valve_motion.py`, whose
  `test_fully_compressed_spring_clears_the_stack_on_exact_solids` compares
  a spring with its valve and with its retainer. It runs once under the
  checkout's own kernel, which its `.env` makes faceted, and once with
  `--exact`, because both paths leave a flexible pair unkeyed today. It
  proves the keying. It does not re-measure ADR-070's whole-suite 1499 s.

Nothing is committed to any project.

**Downstream.** The studio's `shop-skills/machinome-api/SKILL.md` lists the
`machinome test` options. It needs `--verdict-store`/`--no-verdict-store` and
`SOLID_TEST_VERDICT_STORE` as a companion change in the machinome-studio
repository, which this change does not edit. Where the floor runs tests, it
needs no change: its fresh `machinome test` subprocesses are exactly the
runs this serves.
