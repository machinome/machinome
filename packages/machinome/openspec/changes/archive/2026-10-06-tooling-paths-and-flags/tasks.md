Bench: `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch
`fix-warts-3`.

- Every framework command runs as
  `env -C <bench> PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/<tool> ...`.
- `<Clocks>` = `/home/asa/devel/machinome/projects/3DPrintedClocks`. Its
  command runs as
  `env -C <Clocks> PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/machinome snapshot wall_clock_11 --time 0 --imgsize 1200x1000 --autocenter --viewall --preview -o <scratch>/<name>.png`,
  the command its `simulation/early-clocks-2026-09-13.md` documents, with
  `--preview` added. Its image is written to `<scratch>` and never into the
  project.
- `<scratch>` is the campaign scratchpad's `cycle5/` directory
  (`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle5/`).
  It holds `f2_equals_probe.py`, `f3_equals_probe.py`, `probe.scad`,
  `colour.scad` and the Stage P logs and images.

Rules for the whole cycle:

- Run one test run, build or snapshot of ours at a time, since runs
  share `tests/_build`.
- Every test marked RED in section 2 is run and seen red, for the reason
  it names, before the code that turns it green.
- Edit nothing in any project. Do not run Voron-2.
- Write nothing in the `machinome-viewer` checkout. In particular, never
  run the generator without an argument after the change, because that
  would overwrite the viewer's committed fixture.
- Record every command and its result in `evidence.md` as you go, in the
  shape of `openspec/changes/archive/2026-10-04-scad-presentation/evidence.md`.

## 1. Baseline on the unmodified tree

- [x] 1.1 Create `evidence.md` with the bench commit (`git -C <bench>
  rev-parse HEAD`) and the interpreter check: `python -c 'import
  machinome; print(machinome.__file__)'` prints a path under the bench.
  Record `/usr/bin/openscad --version` and `git --version`. Copy the
  source of `<scratch>/f2_equals_probe.py` and `<scratch>/f3_equals_probe.py`
  into `evidence.md`, because the scratchpad is not durable.
- [x] 1.2 Finding 1: run `tools/generate_parity_fixture.py` with no
  argument from the bench. Expect design.md Context §1's
  `FileNotFoundError` naming `.../machinome/WTs/machinome-viewer/...`,
  with exit 1. It writes nothing, because that directory does not exist.
- [x] 1.3 Finding 2: run
  `machinome snapshot tests/web_snapshot_project.py --viewall --autocenter --imgsize 800x600 --preview -o <scratch>/f2-a1-before.png`.
  Expect exit 1 with `OpenSCAD rendering failed:` and nothing after it.
  The same command without `--preview` exits 0.
- [x] 1.4 Finding 2 in the originating project: record `git -C <Clocks>
  status --short` (expected: ` M screenshots/wall_clock_03.png`, `?? WTs/`),
  then run `<Clocks>`'s command to `<scratch>/f2-clock11-a1-before.png`.
  Expect exit 1 with `OpenSCAD rendering failed:`. Record the wall time
  and the status again.
- [x] 1.5 Finding 3: run
  `machinome snapshot tests/web_snapshot_project.py --renderer web --autocenter --viewall --imgsize 1400x1100 --camera 0,0,0,65,0,35,1400 -o <scratch>/f3-a1-before.png`.
  Expect exit 1 with `argument --up: expected one argument`.
- [x] 1.6 Run `tests/test_snapshot.py tests/test_browser_renderer.py
  tests/test_generate_parity_fixture.py` with `pytest -q -p
  no:cacheprovider`, and record the counts and wall time.

## 2. Tests

- [x] 2.1 RED, finding 1 (`tests/test_generate_parity_fixture.py`). Add a
  class `DefaultFixturePathTest` with the `setUp` and six tests in
  design.md's Proof plan:
  - from the worktree;
  - from the primary checkout;
  - with no viewer directory;
  - from a directory that is no Git checkout;
  - the refusal before `build`;
  - an explicit path.

  The tool's git call runs under `patch.dict(os.environ, <the fixture's
  environment>, clear=True)`. Red today: `AttributeError` (no
  `default_fixture`) for the first four, and `TypeError` (`main()` takes
  no argument) for the last two.
- [x] 2.2 RED, finding 2 (`tests/test_snapshot.py`,
  `SnapshotCommandBuildingTest`). Rewrite `test_preview_flag` to assert
  `'--preview=throwntogether' in cmd` and `'--preview' not in cmd`. Add
  `test_preview_never_takes_the_scad_path_for_its_value`: with
  `preview=True`, `cmd[-2] == '--preview=throwntogether'` and
  `cmd[-1].endswith('.scad')`. Red today because the bare token is there.
- [x] 2.3 RED, finding 3 (`tests/test_browser_renderer.py`,
  `CaptureDelegationTest`). Add
  `test_a_negative_leading_vector_travels_with_its_option`, with subtests
  for camera `0,0,0,65,0,35,1400` (up begins `-0.2424`) and camera
  `-100,20,30,0,0,0` (eye begins `-100`). It asserts:
  - one token starting `--view=` and one starting `--up=`;
  - no token equal to `--view` or `--up`;
  - each value parses back to the resolved camera's numbers, compared
    with `parse_camera` from `machinome.core.camera`.

  Red today.
- [x] 2.4 RED, finding 3 at the process boundary. In the same file, add
  `test_the_viewer_parses_the_command_it_is_handed`, decorated
  `@needs_viewer`. It runs `BrowserRenderer().capture_command(<tmp>/missing,
  snapshot_args(camera='0,0,0,65,0,35,1400'), <tmp>/x.png)` with
  `subprocess.run(..., capture_output=True, text=True, timeout=60)`, and
  asserts:
  - the return code is not 2;
  - `expected one argument` is not in stderr;
  - `<tmp>/x.png` does not exist.

  Red today: exit 2 with `argument --up: expected one argument`.
- [x] 2.5 Revise the two camera tests that pin the old token shape:
  - `test_a_requested_camera_is_resolved_here_and_handed_over` reads the
    `--view=` and `--up=` tokens and keeps its `--fov` assertions;
  - `test_no_camera_means_no_camera_flags` asserts that no token starts
    with `--view`, `--up` or `--fov`.

  The first fails today once revised. The second passes before and after.
- [x] 2.6 Run section 2 on the unmodified tree. Record each RED test's
  failure line, and the revised no-camera test green.

## 3. The change

- [x] 3.1 `tools/generate_parity_fixture.py`, design.md Decision 2:
  - `import subprocess`;
  - `VIEWER_FIXTURE`;
  - `default_fixture(root=None)`;
  - `main(argv=None)`, resolving the path before `build()`;
  - the module-level `FIXTURE` removed;
  - the comment at `:73-76` and the docstring's run section revised.
- [x] 3.2 `machinome/viewers/openscad.py` `build_command`: emit
  `--preview=throwntogether`, with the comment of design.md Decision 3.
- [x] 3.3 `machinome/viewers/browser.py` `capture_command`: emit
  `--view=<...>` and `--up=<...>`, with the comment of design.md
  Decision 4. `--fov` is unchanged.
- [x] 3.4 Run section 2: every test is green. Run 1.6's three files, and
  the counts are 1.6's plus the new tests.

## 4. Real runs after the change

- [x] 4.1 Finding 2: rerun 1.3's command to `<scratch>/f2-a1-after.png`.
  Expect exit 0. Read the PNG and say what it shows.
- [x] 4.2 Finding 2 in the originating project: rerun 1.4's command to
  `<scratch>/f2-clock11-a1-after.png`. Expect exit 0. Read the PNG and
  say what it shows. Record the wall time, and `git -C <Clocks> status
  --short`, which is unchanged from 1.4.
- [x] 4.3 Finding 3: rerun 1.5's command to `<scratch>/f3-a1-after.png`.
  Expect exit 0 and a 1400x1100 PNG with a transparent background. Read
  it and say what it shows.
- [x] 4.4 Finding 1, without writing into the viewer:
  - load the bench's tool with `spec_from_file_location` in a `python -c`,
    and print `default_fixture()`. Expect
    `/home/asa/devel/machinome/machinome-viewer/machinome_viewer/widget/src/parity-fixture.json`;
  - print `default_fixture('/home/asa/devel/machinome/machinome')`. Expect
    the same path. This runs only `git rev-parse` in the primary checkout;
  - run the tool with `<scratch>/parity-fixture-after.json`. Expect exit 0
    and the summary line, and `cmp` the file with Stage P's
    `<scratch>/parity-fixture.json` (identical);
  - run `env GIT_DIR=<scratch>/no-such-git ... tools/generate_parity_fixture.py`
    with no argument. Expect a non-zero exit with the refusal message, in
    less time than a build. Then `git -C /home/asa/devel/machinome/machinome-viewer
    status --short`, which is unchanged.

## 5. Changelog

- [x] 5.1 Add design.md Decision 6's two bullets to
  `docs/project/changelog.rst`, after the existing bullets of the one
  `Unreleased` section.
- [x] 5.2 Grep `docs/` (excluding `adrs/` and `releases/`) and `CONTRIBUTING.rst`
  for `--preview`, `--up` and `generate_parity_fixture`. Confirm no page
  says something this change makes wrong. Record the result.

## 6. Checks

- [x] 6.1 Run `black --check` and `flake8 --max-line-length=89` on
  `machinome/viewers/openscad.py`, `machinome/viewers/browser.py`,
  `tools/generate_parity_fixture.py`, `tests/test_snapshot.py`,
  `tests/test_browser_renderer.py` and
  `tests/test_generate_parity_fixture.py`.
- [x] 6.2 Run the full suite once, alone (run after 8.2, on the final tree; evidence §6.2) (`pytest -q -p no:cacheprovider`
  at the bench root), and record the counts and wall time. A failure that
  is not this change's is recorded and stopped on, not worked around.

## 7. Warts

- [x] 7.1 Move these entries of `workflow/warts.md` verbatim to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md`, under a heading
  `` ## `tooling-paths-and-flags` ``. Each goes with a "From ..." line
  naming its section:
  - item 9 of "Expression math and mechanisms (2026-09-06)", "## Framework"
    (from "9. **`tools/generate_parity_fixture.py` cannot run" to
    "`expression-math` task 5.4.");
  - item 14 of "Internal-Cycloidal-Actuator (2026-09-06, project refactor
    pass)" (from "14. **`machinome snapshot --preview`" to "Seen in
    3DPrintedClocks.");
  - from "Voron-2 — native contact measurements and snapshot arguments (5
    October 2026)", the whole subsection "### A negative-leading camera
    vector is rejected at the viewer subprocess boundary", and the
    paragraph after it, from "The same project also reproduced existing
    **item 14**" to "evidence for that existing finding.".

  Add a "What shipped" paragraph naming:
  - the generator's resolution through Git's common directory, and its
    refusal before building;
  - `--preview=throwntogether`;
  - `--view=` and `--up=` as one token each.

  Delete the moved text from `warts.md`. The Voron-2 section keeps its
  opening paragraph, its other subsections, the paragraph on the
  project's original archive, and its main-branch recheck.
- [x] 7.2 In `warts.md`'s "Standing triage", "Planned, never done",
  delete the bullet "**`tools/generate_parity_fixture.py` cannot run from
  a worktree** (item 9) and **`machinome snapshot --preview` sends a bare
  `--preview`** (item 14)".
- [x] 7.3 File the two findings this cycle made, after the section
  "## Findings from the framework cycle `children-refuse-early-reads`
  (2026-10-06)", as a new section "## Findings from the framework cycle
  `tooling-paths-and-flags` (2026-10-06)". It holds two bullets:
  - **`--render` is accepted and never forwarded, and its help calls it
    the default.** Give the facts of design.md Open Question 1:
    - `build_command` never reads `args.render`;
    - the help and `docs/reference/cli.rst` call it OpenSCAD's default
      full render;
    - OpenSCAD 2021.01's PNG default is the OpenCSG preview, identical
      byte for byte to `--preview=opencsg`;
    - `--render=cgal` renders without the model's colours.

    Add its triage line, "Held for the pilot: forwarding changes what an
    existing flag draws", unless the orchestrator's review answered
    otherwise.
  - **A failed OpenSCAD render reports only its standard error.** Give the
    facts of Open Question 2: OpenSCAD 2021.01 prints its usage dump on
    standard output, so `OpenSCAD rendering failed:` is followed by
    nothing. Add its candidate fix: print stdout when stderr is empty.

## 8. Sync and archive

- [x] 8.1 Sync the deltas:
  - into `openspec/specs/cli/spec.md`, replacing "Snapshot command";
  - into `openspec/specs/web-snapshot/spec.md`, replacing "A requested
    camera is honoured or refused, never approximated";
  - into `openspec/specs/kinematics/spec.md`, adding the new requirement
    after "The parity corpus covers every symbolic function".

  Diff each modified requirement against its baseline. Only the added
  paragraph or sentence and the added scenario differ.
- [x] 8.2 Archive the change to
  `openspec/changes/archive/2026-10-06-tooling-paths-and-flags/`. Then
  `openspec validate --specs` passes.
- [x] 8.3 Run section 2's tests and 1.6's files once more, and record the
  result. Leave everything uncommitted.
