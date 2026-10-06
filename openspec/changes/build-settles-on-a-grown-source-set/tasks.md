Bench: `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch
`fix-warts-3`. Every framework command runs as
`env -C <bench> PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/<tool> ...`.
`<scratch>` is the campaign scratchpad's `cycle2/` directory, holding
`trace_one_generation.py` and `grown_set_probe.py`; a scratch build
directory is any fresh directory under it. `<hexapod>` is
`/home/asa/devel/machinome/projects/Robots/hexapod_spiderbot_model`. One
test run or build of ours at a time (the suites share `tests/_build`).
Every test marked RED in section 2 is run and seen red, for the reason it
names, before the code that turns it green. Record every command and its
result in `evidence.md` as you go, in the shape of
`openspec/changes/archive/2026-10-04-scad-presentation/evidence.md`.

## 1. Baseline on the unmodified tree

- [ ] 1.1 Create `evidence.md` with the bench commit (`git -C <bench>
  rev-parse HEAD`) and the interpreter check (`python -c 'import
  machinome; print(machinome.__file__)'` prints a path under the bench).
- [ ] 1.2 Record the fixture's timestamps: `stat -c '%y %n'
  tests/scad_where_read_project/*`. Do not touch them, now or later.
- [ ] 1.3 With a fresh scratch `SOLID_BUILD_DIR` each, from the bench:
  `timeout 30 machinome build tests/scad_where_read_project/native.py:StlBench`
  and `timeout 30 ... machine.py:Machine`; record exit code (124), the
  count of `START` lines and wall time.
- [ ] 1.4 Run `<scratch>/trace_one_generation.py
  tests/scad_where_read_project/native.py:StlBench` from the bench (fresh
  scratch `SOLID_BUILD_DIR`); record its last lines: the source set before
  and after `_prepare`, the joined files, "assembled files not in it: []",
  and `SOURCE_CHANGED` after lines 391, 392, 393. Copy the sources of both
  scratch scripts into `evidence.md` (the scratchpad is not durable).
- [ ] 1.5 Run `python <scratch>/grown_set_probe.py <bench> <scratch>/probe-before`
  (cwd `<scratch>`); record both lines (timed out, ~36 `START` lines each).
- [ ] 1.6 The focused builder set, alone:
  `pytest -q -p no:cacheprovider tests/test_retained_builder_generation.py
  tests/test_builder_lifecycle.py tests/test_source_generation.py
  tests/test_builder_reload_resilience.py tests/test_build_lock.py`;
  record counts and wall time (Stage P: 85 passed, 7 subtests, 57.7 s).
- [ ] 1.7 Catalogue baseline: `git -C <hexapod> status --short` (record it);
  `git -C <hexapod> worktree add --detach <hexapod>/WTs/build-settles`
  (no branch is created); `git -C <hexapod>/WTs/build-settles rev-parse
  --show-toplevel` names the worktree; record `stat -c '%y %n'` of
  `simulation/spiderbot.py`, `simulation/printed.py`, `stl/Frame.stl`,
  `stl/Tip.stl` there. Then, with a fresh scratch `SOLID_BUILD_DIR`,
  `env -C <hexapod>/WTs/build-settles PYTHONPATH=<bench> timeout 120
  /home/asa/devel/machinome/.venv/bin/machinome build`; record exit (124),
  `START` count and wall time (Stage P: 34 in 120 s). Leave the worktree
  in place for 5.3.

## 2. Red tests

All in `tests/test_retained_builder_generation.py` (design.md, Decision 3).

- [ ] 2.1 RED `JoinedContributorTest::test_a_newer_contributor_joining_during_assembly_builds`:
  the in-process builder with a real source generation; a joiner dated
  1 ms and 1 s after the module, and an hour after the present (subtests);
  `_start()` returns `CURRENT` and `_write_viewer_snapshot` is called once.
  Red today: `SOURCE_CHANGED` in every subtest.
- [ ] 2.2 GUARD `JoinedContributorTest::test_a_contributor_replaced_after_joining_stands_down`:
  the joiner replaced beneath its own mtime after `track_sources`;
  `SOURCE_CHANGED`, `generate_stl` not awaited, `_write_viewer_snapshot`
  not called. Green before and after.
- [ ] 2.3 RED `FreshCheckoutBuildTest::test_a_mesh_newer_than_its_module_builds_in_one_generation`:
  `Build().build` spawning real builders for a project whose `tab.stl` is
  1 ms and 1 s newer than its module (subtests, own project and package
  each), a second spawn refused with an `AssertionError` naming the first
  child's exit code; expect status 0, one child exiting 0, `viewer.json`
  naming the mesh's artifact. Red today: "the first exited 11".
- [ ] 2.4 Run 2.1-2.3 on the unmodified tree; record 2.2 green and the
  failure lines of 2.1 and 2.3.

## 3. The change

- [ ] 3.1 `machinome/core/builder.py`, `Builder._start`: the post-assembly
  comparison gains `self._source_generation is None and`, and its comment
  becomes design.md Decision 2's. Nothing else in the file changes; the
  lock-wait comparison stays.
- [ ] 3.2 Run 2.1-2.3: all green. Run the focused set of 1.6: every
  existing test passes unedited; record counts.
- [ ] 3.3 `black --check` and `flake8 --max-line-length=89` on
  `machinome/core/builder.py` and `tests/test_retained_builder_generation.py`.

## 4. Framework validation

- [ ] 4.1 Repeat 1.3 (bound raised to 120 s): both exit 0 with one `START`;
  record wall time.
- [ ] 4.2 Repeat 1.4 for `StlBench` and for `machine.py:Machine`: `CURRENT`,
  and every assembled file in the assembly census.
- [ ] 4.3 Repeat 1.5 into `<scratch>/probe-after`: both lines exit 0, one
  `START`, `viewer.json True`.
- [ ] 4.4 Run the whole of `tests/test_scad_presentation.py`, alone, the
  fixture's files as 1.2 recorded them; record counts and wall time, and
  that the seven tests cycle 1 deselected (`WithoutTheEngineTest::test_native_projects_build_without_each_module`,
  `WrittenOnlyWhereReadTest::test_a_build_writes_only_the_scad_authored_leafs_scad`,
  `SweepTest::test_presentation_scad_and_a_renamed_leafs_scad_are_swept`,
  `SnapshotOnDemandTest::test_the_openscad_renderer_draws_the_roots_scad_for_its_pose`,
  `::test_the_renderer_removes_the_roots_scad_after_drawing_it`,
  `::test_the_renderer_removes_the_roots_scad_when_drawing_fails`,
  `::test_a_build_removes_a_root_scad_a_killed_render_left`) passed.
  (They are not run red: each would wait out its runner's 600 s timeout;
  1.3 and cycle 1's evidence §4.3 stand for the red.)

## 5. Validation in Robots/hexapod_spiderbot_model (read only)

- [ ] 5.1 In the worktree of 1.7, a fresh scratch `SOLID_BUILD_DIR`:
  `env -C <hexapod>/WTs/build-settles PYTHONPATH=<bench> timeout 900
  /home/asa/devel/machinome/.venv/bin/machinome build`; record exit (0),
  `START` count and wall time.
- [ ] 5.2 Run `<scratch>/trace_one_generation.py
  simulation/spiderbot.py:Spiderbot` there against a fresh scratch build
  directory: `CURRENT` (or `RENDERED` passes ending `CURRENT`), every
  assembled file in the census; record its last lines.
- [ ] 5.3 `git -C <hexapod>/WTs/build-settles status --short` (nothing);
  `git -C <hexapod> worktree remove <hexapod>/WTs/build-settles`; remove
  the then empty `<hexapod>/WTs` with `rmdir`; `git -C <hexapod> worktree
  list` and `git -C <hexapod> status --short` match 1.7's.

## 6. Words

- [ ] 6.1 `docs/project/changelog.rst`, under the existing `Unreleased`:
  design.md Decision 5's bullet, after the cycle-1 bullet. Run
  `tests/test_release_records.py`.
- [ ] 6.2 `grep -rn -i "stand down\|stands down\|SOURCE_CHANGED\|maximum mtime\|aggregate" docs/ --include=*.rst --include=*.md`
  outside `docs/adrs/`: no page states the removed comparison (Stage P
  found only `docs/architecture.md`'s source-generation paragraphs, which
  describe the census and stay as they are).

## 7. Findings record

- [ ] 7.1 In `workflow/warts.md`, "Findings from the framework cycle
  `lean-install` (3 October 2026)": move the addendum paragraph
  "*4 October 2026, the framework cycle `mesh-engine`:* ..." verbatim to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md` under a heading
  naming `build-settles-on-a-grown-source-set`, with the entry's first
  line quoted for context and a "What shipped" paragraph (the mechanism
  in two sentences; the fixture, the probe and the hexapod's fresh
  worktree now build in one generation). In `warts.md`, replace the
  addendum with a "**Remaining (2026-10-06)**" note: the restart loop is
  closed by `build-settles-on-a-grown-source-set` (see the resolved
  record); the three-hour hang itself is not claimed, since its STEP was
  copied in after the checkout (the mechanism is plausible) but its
  recorded observations — no child process, no artifact — are not the
  loop's; not repeated (design.md, Open Question 1).
- [ ] 7.2 Update `workflow/ongoing/fix-warts-3.md`'s "Progress" with one
  line for this cycle.

## 8. Sync, archive, full suite

- [ ] 8.1 Sync the two MODIFIED requirements into
  `openspec/specs/build-pipeline/spec.md` and
  `openspec/specs/one-shot-build-and-notification/spec.md`
  (`openspec archive build-settles-on-a-grown-source-set --yes`, or by
  hand and then `--skip-specs`); check every carried scenario is present
  once.
- [ ] 8.2 `openspec validate --specs` passes after the archive, and the
  archived folder is
  `openspec/changes/archive/2026-10-06-build-settles-on-a-grown-source-set/`.
- [ ] 8.3 Run the focused set of 1.6 once more; record.
- [ ] 8.4 Run the full suite (`pytest -q -p no:cacheprovider` at the bench
  root), alone, with nothing deselected; record counts and wall time.
  Leave everything uncommitted and report.
