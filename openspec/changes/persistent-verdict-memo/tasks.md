## 1. Baseline before any code change

- [ ] 1.1 Write the counting probe of design.md §12 into the session
  scratchpad, not the bench. It wraps `_memoized` (keyed asks, in-process
  hits, uncacheable asks), `intersect_shapes` and `_faceted_verdict`
  (computations), and, once it exists, the store lookup (store hits). It runs
  `machinome.cli.manage()` and writes one JSON line of counts and wall time
  to stderr at exit. Keep it as the tool for §6 and §9.
- [ ] 1.2 The flexible evidence slice, on the bench's unmodified tree
  (bf24687), with the bench on `PYTHONPATH`, the workspace venv and the
  probe of 1.1. Run it from `projects/Vibecoded-demos/v8-engine` on its
  checked-out branch, `declarative-api` at fdf624b (`main` carries the same
  tests; `master` predates the springs and asks no spring pair).
  - **Choosing the slice.** Read the v8-engine test files that carry
    spatial assertions and confirm which tests put a molejo spring into a
    pair. The files are `v8_engine/test_v8_engine.py` (32),
    `valvetrain/test_bank_valvetrain.py` (8),
    `cylinders/test_cylinder_unit.py` (6), `crankshaft/test_crankshaft.py`
    (5), `final_drive/test_timing_drive.py` (2) and
    `valvetrain/test_valve_motion.py` (2). At fdf624b the tests are:
    - `v8_engine/valvetrain/test_valve_motion.py`,
      `ValveMotionTest.test_fully_compressed_spring_clears_the_stack_on_exact_solids`,
      at the lobe's peak (t = 0.9375). It calls
      `assertNotIntersecting(motion.spring, motion.valve)` and
      `assertNotIntersecting(motion.spring, motion.retainer)`, two flexible
      pairs on one bare stack;
    - `v8_engine/test_v8_engine.py`,
      `EngineTest.test_valve_springs_clear_head_stem_and_retainer_on_exact_solids`,
      at t = 0.125: each of the 16 springs against its valve, its retainer
      and its bank's head, 48 pairs. The `assertNoPairwiseIntersections`
      sweeps of that file and of `test_bank_valvetrain.py` also walk the
      springs as leaves.

    `machinome test` selects a companion file, not a single test, so the
    slice is the smallest file:
    `machinome test v8_engine/valvetrain/test_valve_motion.py`. Its seven
    other tests read mesh bounds, vertices and constructor guards, and ask
    no pair. `test_v8_engine.py` is not the slice, because it runs the whole
    root suite.
  - **Both kernels.** Both paths leave a flexible pair unkeyed today:
    `_fast_geometry` returns `None` for it, and the exact branch's
    `shape_identity` finds nothing for an evaluated shape. Run the slice
    twice:
    - once at the checkout's default, which its `.env`
      (`SOLID_TEST_KERNEL=faceted`) makes the faceted kernel. Its summary
      line must carry the faceted label;
    - once with `--exact` passed explicitly.
  - **Record for each run:** uncacheable asks (expected > 0; the test asks
    two spring pairs), keyed asks, computations, wall time, and the
    verdicts: passed and failed counts, and every failing test's message.
  - If either run records zero uncacheable asks, the slice asks no flexible
    pair on that kernel. Stop and return to the pilot before any code
    change. The flexible evidence would then be a fixture pair in the
    framework's own tests (task 3.3), and the proposal and design would stop
    citing v8-engine as the flexible evidence run.

  Run one CAD process at a time on this machine; never two suites at once.
- [ ] 1.3 Cite the clock 2 and strandbeest baselines already recorded in
  `workflow/warts.md` (cold 1348.9 s and 246.9 s, warm floors 18.35 s and
  11.97 s). They are not re-run at base.
- [ ] 1.4 Record, on the unmodified tree, which of `importlib.metadata`,
  `platform`, `cadquery`, `OCP`, `manifold3d`, `trimesh` and `molejo` a
  fresh-interpreter `machinome build -h` dispatch loads, through
  `tests/import_probe.py`. When this plan was revised at bf24687, it loaded
  `importlib.metadata` and `platform`, and no kernel. The recorded set is
  the ceiling task 6.7 asserts.

## 2. Red first: the store, in process

- [ ] 2.1 Add a store test module with a fixture that:
  - gives each case a temporary project build root, with the store switched
    on by an explicit `ComparisonPolicy`;
  - provides a `fresh_process()` helper that flushes, then clears
    `_verdict_cache`, `_verdict_observations`, the store's loaded index,
    pending records and digest memo, the exact shape cache and the Manifold
    cache. That is exactly what a new interpreter starts with.

  Reuse the `FakeNode`, `ExactFakeNode` and `Parent` shapes of
  `tests/test_intersection_memo.py`. Name the originating finding in the
  module docstring: wall_clock_02 and strandbeest, with the numbers and the
  `workflow/warts.md` citation.
- [ ] 2.2 A decided verdict is served after a fresh process. For one faceted
  and one exact pair, the first ask computes once. After `fresh_process()`
  the same ask computes zero times and returns an `IntersectionStats` equal
  bit for bit, including the volume's IEEE bits. RED on the current tree.
- [ ] 2.3 An artifact rewritten with identical bytes under a new inode and
  mtime (copy, `os.replace`, new `utime`) is served after a fresh process.
- [ ] 2.4 A content change under a preserved timestamp is recomputed:
  - for the faceted path, swap an STL for one of equal byte size and
    different geometry (a binary STL's size depends only on its face count,
    so a translated copy of the same box qualifies) and restore the old
    mtime;
  - for the exact path, rewrite the BREP with different geometry and
    restore its mtime.

  After a fresh process each pair is recomputed, and its verdict is the new
  geometry's.
- [ ] 2.5 A moved project is served: copy the build root with its artifacts
  and `.verdicts` to a new directory and point the fixture there. After a
  fresh process the verdicts are served. Also assert that no persisted key
  or record contains the old or the new absolute path (scan the segment
  bytes).
- [ ] 2.6 The stamp invalidates. Change each stamp component in turn by
  patching the stamp's inputs: `machinome.__version__`, the package digest,
  one kernel distribution version, the platform token. After a fresh process
  nothing is served. The foreign-stamp segment is left on disk until
  eviction. Computing the stamp imports none of `cadquery`, `OCP`,
  `manifold3d`, `trimesh` or `molejo`: assert it through
  `tests/import_probe.py` in a fresh interpreter. The stamp may load
  `importlib.metadata` and `platform`; importing the module may not
  (task 6.7).
- [ ] 2.7 The quantum is part of the persisted key. A verdict kept at
  quantum `q` is not served at quantum `2q` for a placement chosen so that
  the integer cells coincide. Assert both at the key function and by
  behaviour.
- [ ] 2.8 A flush contact survives the store. The flush fixture of
  `FlushContactThroughTheCache` is decided, then served after a fresh
  process as non-empty with exactly 0.0 mm³, and `assertNotIntersecting`
  still fails at the strict default.
- [ ] 2.9 Nothing is persisted for what the memo does not cache. The store
  receives no record for:
  - a `MeshOnlyNode` pair;
  - the virtual floor of `assertAssemblySupported`;
  - a pair with a non-finite relative matrix;
  - a compute that raises (patch `intersect_shapes` to raise
    `RuntimeError`, and separately `ExactCommonInconsistency`);
  - an exact shape with no `shape_identity`;
  - an artifact rewritten after its geometry was read (exact: after
    `cached_shape`; faceted: after the Manifold was built).

  Count records and pending entries to prove it.
- [ ] 2.10 The digest memo is keyed on the full observation. In one process,
  a same-size rewrite of an artifact with its mtime restored yields a new
  digest. This is the case a `(path, mtime_ns, size)` key would get wrong.
- [ ] 2.11 A corrupt store is ignored. Each of the following yields computed
  verdicts, no exception and unchanged output:
  - a truncated segment;
  - a segment of random bytes;
  - a wrong magic;
  - a foreign format version;
  - a checksum mismatch;
  - `.verdicts` being a regular file;
  - a read-only `.verdicts`.

  The next compaction deletes the invalid segments, and never a file whose
  name is not the store's own pattern.
- [ ] 2.12 Two writers lose nothing, and neither does a reader whose load
  overlaps a compaction (design.md §7).
  - Two `multiprocessing` (spawn) processes flush synthetic records into
    one store at the same time behind a barrier, while a third forces a
    compaction. Afterwards a fresh load holds the union, with no exception
    in any process.
  - A reader whose load overlaps a compaction holds the union. Make the
    interleaving deterministic, not timed: wrap the store's directory
    listing so that, after the reader's first listing and before it opens
    the listed segments, a spawned process compacts the directory, merging
    those segments and deleting them. The reader's index then holds every
    record of the deleted inputs. This case must fail if the re-listing is
    removed.
  - The same, with the merged segment also deleted between the reader's
    second listing and its open. The reader skips it, raises nothing, and
    serves misses for those keys.

  No CAD runs in this test: this machine must not run two CAD processes at
  once.
- [ ] 2.13 The bound and eviction. With the record limit patched small:
  - foreign-stamp segments go first, oldest first;
  - then the current stamp's least recently used records go, down to three
    quarters of the limit;
  - a record touched by a store hit outlives an untouched older one;
  - compaction triggers above 64 segments and deletes exactly the merged
    inputs;
  - a temporary older than an hour is removed.
- [ ] 2.14 Location and sharing:
  - with no project manifest above the working directory and no absolute
    or anchored build directory, no store and no `_build` are created;
  - under `machinome test --all`, every declared model shares the root's
    `.verdicts`, and a single-model run of the same project uses that same
    store, because it anchors on the same root;
  - a verdict kept by a run of one declared model is served to a run of
    another declared model of the same project that asks the same question.
    Reuse the two-model fixture of `tests/test_named_models.py`. Give both
    models one identical pair of parts at one relative placement, with a
    companion test comparing it. First assert that the two models'
    artifacts of that pair are byte-identical: that is the scenario's
    premise, not an assumption. Test model A alone, call `fresh_process()`,
    then test model B alone. Its ask is a store hit and computes nothing.
    After another `fresh_process()`, `--all` computes nothing for either
    model's ask;
  - an absolute `SOLID_BUILD_DIR` holds the store.

## 3. Red first: flexible state identity

- [ ] 3.1 In `tests/test_flexible_cache_performance.py`, invert
  `test_flexible_verdicts_are_not_memoized_after_geometry_reuse`. The second
  comparison at one binding is served by the in-process memo and
  `_faceted_verdict` runs once; a third at another binding runs it again.
  RED on the current tree.
- [ ] 3.2 The exact path. Under the exact kernel, a molejo spring against an
  exact part, compared twice at one binding and relative placement, runs one
  OCCT boolean, and a different binding runs another. RED on the current
  tree, because `shape_identity` of a flexible solid is `None` today.
- [ ] 3.3 Across a fresh process, on both paths: the equal binding is served
  from the store, and the different binding is computed.
- [ ] 3.4 The identity carries nothing absolute and no metadata. The
  identity at one binding is unchanged after the project directory is moved,
  and after its source is rewritten with identical bytes (a new
  fingerprint). It changes when the source content, the spec or a bound
  value changes.
- [ ] 3.5 Override rules:
  - a subclass overriding `base_mesh` (the existing `TranslatedMeshSpring`
    fixture) stays uncached on the faceted path;
  - a subclass overriding `shape` stays uncached on the exact path.

  Both are computed every time, and nothing is kept in either tier.
- [ ] 3.6 Coherence:
  - the identity recorded with an exact flexible solid is the identity of
    the snapshot that built it;
  - a faceted miss evaluates the one snapshot that supplied its identity
    (mirror `test_miss_evaluates_the_one_shape_that_supplied_its_identity`);
  - two bindings forced to share a shortened `binding_hash` do not share a
    verdict.
- [ ] 3.7 An unobservable source gives no identity, and the pair is computed
  every time (mirror `test_unobservable_source_is_never_retained`).
- [ ] 3.8 Every other test in `test_flexible_cache_performance.py`,
  `test_flexible_node.py` and `test_molejo_adapter.py` stays green as
  written. That includes the per-instance last-binding exact memo test.

## 4. Red first: policy and command line

- [ ] 4.1 `ComparisonPolicy('exact', 0.0).verdict_store` and the 3-argument
  form both mean "store on". Every existing positional construction keeps
  working unedited. Widen `ComparisonKernelSelectionTest`'s policy EQUALITY
  assertions to 4-tuples: that is the intended visible break. RED on a
  mandatory fourth field.
- [ ] 4.2 `--verdict-store` / `--no-verdict-store` parse to
  `args.verdict_store` as `True`, `False`, or `None` when absent, outside
  the `--exact`/`--faceted` group.
- [ ] 4.3 Resolution:
  - the flag beats `SOLID_TEST_VERDICT_STORE`, which beats on, both ways
    round;
  - `on` and `off` are accepted, and the empty string counts as unset;
  - any other value is an error naming the variable and both values,
    raised before any node is built;
  - the switch is accepted and read under both kernels.
- [ ] 4.4 The summary line:
  - at the defaults, the exact current string;
  - with the store off, `(verdict store off)`;
  - with `--faceted --volume-epsilon 0.5 --placement-quantum 1e-6
    --no-verdict-store`, one parenthesis in the order faceted and epsilon,
    then quantum, then store.

  No pre-build line in any case.
- [ ] 4.5 Off means off. With the store off, a run neither creates nor
  reads `.verdicts`, and a store left on disk is untouched: listing and
  mtimes are unchanged.

## 5. Red first: the sweep

- [ ] 5.1 A project whose build directory holds `.verdicts/` with segments
  is rebuilt and publishes. The directory and every file in it survive. RED
  on the current tree: the sweep deletes them today.
- [ ] 5.2 A declared model's sweep, in an interpreter whose
  `SOLID_BUILD_DIR` is that model's directory, spares a `.verdicts/` inside
  it.
- [ ] 5.3 The existing sweep scenarios stay green: a renamed node's
  artifact is gone, `.brep` survives, and markings are kept and dropped by
  reference.

## 6. Red first: across processes, end to end

- [ ] 6.1 Add a small fixture project under `tests/meta_project/` (or a
  temporary copy of one): two exact parts and one faceted STL part, a
  `@testing_steps` sweep, `assertNoSolidInterference` and
  `assertNotIntersecting`. Run `machinome test` on it twice as child
  processes through the probe of 1.1, with `SOLID_TEST_VERDICT_STORE=on`
  overriding the suite's pin. The first run computes N > 0. The second
  computes 0, its store hits equal N, and its stdout equals the first's
  apart from the timing figure. The proof is by count, not timing. RED on
  the current tree.
- [ ] 6.2 Between the two runs, tamper with one built artifact's bytes and
  restore its mtime. The second run recomputes exactly the pairs involving
  it, and its verdicts are those of the tampered geometry.
- [ ] 6.3 Between the two runs, move the fixture project directory together
  with its build directory. The second run computes 0.
- [ ] 6.4 A third run with `--no-verdict-store` computes N, leaves the
  segment listing unchanged, and ends its summary with the store note.
- [ ] 6.5 Kill a child run with SIGKILL after its first flush. The next
  run reads the store without error and reaches the same verdicts.
- [ ] 6.6 In a fresh interpreter with the store on, a faceted run of an
  all-exact fixture imports no `cadquery`. Extend the existing faceted
  import check rather than add a parallel one. With `manifold3d` made
  unimportable (the `tests/mesh_engine_absent.py` technique), an all-exact
  fixture run twice is served on the second run.
- [ ] 6.7 Import weight, in `tests/test_cli_lazy_imports.py`, through
  `tests/import_probe.py` in a fresh interpreter (design.md §5, §6):
  - importing the store module adds none of `importlib.metadata`,
    `platform`, `cadquery`, `OCP`, `manifold3d`, `trimesh` and `molejo`.
    RED on the current tree, where the module does not exist;
  - a `machinome build -h` dispatch imports the build command and the
    builder at module level. It loads no store module, and of those seven
    modules only the ones task 1.4 recorded. This case is green at base and
    must stay green: it is a guard, not a red-first test.

## 7. Implementation

- [ ] 7.1 Add a new private store module (design.md §5):
  - its top-level imports are cheap standard-library modules only (`os`,
    `struct`, `hashlib`, `time`, `logging` and the like) and
    `machinome._artifact`;
  - `importlib.metadata`, `importlib.util.find_spec`, `platform`, the
    `sys.implementation` read and the package-source digest happen inside
    the stamp function at the first store use, never at import;
  - it imports no kernel or evaluator (`cadquery`, `OCP`, `manifold3d`,
    `trimesh`, `molejo`) at any time;
  - it takes the directory name from `machinome._artifact` (task 7.5).

  It holds:
  - the stamp (§5), computed once per process at the first store use;
  - the digest memo, keyed on the full `ArtifactObservation` and evicted
    per realpath (§3);
  - the persisted-key encoding (§2);
  - the segment format and its validation;
  - load and merge, pending records and touches;
  - the flush triggers (10 s, end of run, `atexit`);
  - compaction and eviction (§7), and disabling on any failure;
  - private counters and a reset seam for tests.
- [ ] 7.2 `machinome/exact.py`: `cached_shape` observes the BREP before and
  after `importBrep` and records the load observation only when the two
  agree. `_evict` drops it with the shape. Add a private accessor from a
  shape key to its load observation. The in-process key stays
  `(path, mtime)`.
- [ ] 7.3 `machinome/node/flexible.py` exposes one private coherent state
  snapshot, `(identity, rendered, values)`, built from the design.md §4
  components with no realpath and no fingerprint.
  - `_faceted_cache_snapshot` keeps its current key for the Manifold cache.
  - `_exact_solid` records the identity of the snapshot it built from,
    beside `(shape, tolerance)`.
  - The public `shape()` and `shape_tolerance` are unchanged.
- [ ] 7.4 `machinome/test.py`:
  - `ComparisonPolicy` gains `verdict_store`, with
    `defaults=(DEFAULT_PLACEMENT_QUANTUM, True)`, and
    `resolve_comparison_policy` resolves it before the kernel branch;
  - `_memoized` gains the tier of §1;
  - add the persisted identity derivation for exact, faceted and flexible
    identities;
  - `_flexible_manifold` returns the verdict identity, and `_fast_geometry`
    stops returning `None` for a stock leaf;
  - the exact branch of `_engine_intersection_stats` takes a flexible
    node's recorded identity;
  - `_settled` stays after the memo.

  Rewrite the "Verdict memo" comment block, the `_flexible_manifold_cache`
  comment ("remains deliberately uncached"), and the `_memoized`,
  `_verdict_key` and `_fast_geometry` docstrings to say what is now true.
- [ ] 7.5 `machinome/_artifact.py` gains the store's directory name
  constant, `.verdicts` (design.md §6). `machinome/core/builder.py` takes
  it from there, beside the `ArtifactChanged` it already imports, and
  `_sweep_unreferenced_artifacts` prunes that directory from its walk at the
  top of the swept directory. The builder imports nothing new.
- [ ] 7.6 `machinome/manager/test.py`:
  - add the flag pair and pass it to the resolver;
  - add the summary note, including the `ComparisonPolicy` fallback in
    `report()`;
  - flush the store in a `finally` around the run in `handle`.
- [ ] 7.7 Extend the existing `tests/conftest.py` (design.md §11). Keep its
  `collect_ignore = ['meta_project', 'vet_projects']` and its comment as
  they are. Add a session-wide `SOLID_TEST_VERDICT_STORE=off`, set before
  any test runs so that subprocesses inherit it. The store's own tests
  switch the store on explicitly.
- [ ] 7.8 Run the new and touched test modules. Then run
  `tests/test_intersection_memo.py`, `tests/test_exact_placement_cache.py`,
  `tests/test_broad_phase_culling.py`, `tests/test_meta.py`,
  `tests/test_manager_test.py` and `tests/test_cli_lazy_imports.py`. Then
  run the whole suite. Run one suite at
  a time: they share `tests/_build`.

## 8. Documentation

- [ ] 8.1 Read `/home/asa/devel/machinome/skills/write-the-manual/SKILL.md`
  before touching a page a reader is sent to.
- [ ] 8.2 `docs/howto/fast-tests.rst`: add a section "Verdicts kept between
  runs", per the user-documentation delta. It explains:
  - what is kept and where (`<build dir>/.verdicts`);
  - what identifies a question: artifact content, a flexible part's
    values and spec, the quantised placement;
  - that framework and kernel changes start it afresh;
  - that no verdict changes;
  - `--no-verdict-store` / `SOLID_TEST_VERDICT_STORE=off`;
  - that deleting the directory is always safe.

  Revise "Every intersection verdict is asked once per run and remembered"
  in the placement-quantum section to match.
- [ ] 8.3 `docs/reference/cli.rst`: the flag pair in the `machinome test`
  synopsis and option list, and `SOLID_TEST_VERDICT_STORE` in the
  environment section.
- [ ] 8.4 `docs/project/changelog.rst`: the next unreleased section records
  the capability, naming the originating projects.
- [ ] 8.5 `workflow/warts.md`: mark the 2026-09-29 finding as taken up and
  fixed by this cycle, with the measured numbers from §9. Record
  `cached_shape`'s `(path, float mtime)` in-process key, weaker than every
  other artifact cache, as a new finding for triage (design.md Non-Goals).

## 9. Evidence in the originating projects (one CAD process at a time)

- [ ] 9.1 3DPrintedClocks, from `projects/3DPrintedClocks`, with the bench
  on `PYTHONPATH` and the probe of 1.1: delete `_build/.verdicts`, run
  `machinome test wall_clock_02` as one cold process, then again as one warm
  process. Record for each:
  - wall time;
  - keyed asks, in-process hits, store hits, computations, booleans and
    uncacheable asks;
  - the store's size on disk;
  - the passed and failed counts and the failing tests' messages, including
    volumes.

  The verdicts must be identical, and identical to the baseline's 16 passed
  and 6 failed.
- [ ] 9.2 strandbeest, from `projects/strandbeest`: the same cold and warm
  pair for `machinome test`, then a third process with `--no-verdict-store`.
  The third run's cost is cold-like, its summary carries the store note, and
  its verdicts are the same.
- [ ] 9.3 v8-engine, from `projects/Vibecoded-demos/v8-engine` on the
  same branch as 1.2: the slice of 1.2
  (`machinome test v8_engine/valvetrain/test_valve_motion.py`) on the
  changed tree, under each kernel of 1.2 in turn: first the checkout's
  faceted default, then `--exact`. For each kernel, delete
  `_build/.verdicts`, then run one cold process and one warm process.
  Record for each of the four runs: uncacheable asks, keyed asks,
  computations, store hits, wall time and the verdicts.
  - Uncacheable asks are 0 on both kernels, where 1.2 recorded more than 0.
  - Each cold run has no store hits, and keeps a verdict for each spring
    pair it asks.
  - Each warm run computes nothing: every ask its in-process memo misses is
    a store hit, the spring pairs among them.
  - Every run's verdicts are identical to 1.2's for the same kernel.
- [ ] 9.4 Write `openspec/changes/persistent-verdict-memo/evidence.md`:
  - the baseline citations and the §9 tables, with one v8-engine table per
    kernel;
  - the raw result lines and the probe script as used;
  - one honest sentence on how each warm process compares to the measured
    warm floor, recorded whatever it is, with no key widened to chase it
    (ADR-070's consequence);
  - the statement that the verdicts are identical.

  Nothing is committed in any project repository. The `.verdicts`
  directories the runs leave are ignored build state and stay.

## 10. Decision record, synthesis, companion and close

- [ ] 10.1 After implementation and evidence, write
  `docs/adrs/TEST-FRAMEWORK/ADR-156-a-decided-verdict-outlives-the-run.md`
  from the outline at the end of design.md, using the next free number if
  156 is taken. It is **Accepted** and **Amends** ADR-070, and it states
  that ADR-090's restatement of "flexible parts remain uncacheable" is
  superseded with it. Put the §9 numbers in its Consequences.
- [ ] 10.2 `docs/adrs/README.md`: add the new row in the TEST-FRAMEWORK
  section, and append "amended by 156" to ADR-070's row.
- [ ] 10.3 `docs/architecture.md`, Test framework section. Rewrite the memo
  paragraph ("Verdicts are memoized within a run ...") to cover the
  persistent tier beneath it: state identities, the stamp, `.verdicts`
  under the build root, the sweep's exemption, the run switch, and the miss
  as the failure direction. Replace "flexible intersection verdicts remain
  uncached: the per-instance final binding can still change between
  comparisons" with the state-identity statement.
- [ ] 10.4 Companion change, not made here: the studio repository's
  `shop-skills/machinome-api/SKILL.md` must list `--verdict-store` /
  `--no-verdict-store` and `SOLID_TEST_VERDICT_STORE`. Report it to the
  pilot as a machinome-studio change. Do not edit the studio from this
  cycle.
- [ ] 10.5 `openspec validate persistent-verdict-memo --strict` passes. Sync
  the modified baseline specs (`test-framework`, `flexible-parts`, `cli`,
  `build-pipeline`, `user-documentation`) and archive the change, per the
  workspace's framework-change skill (commit 2).
