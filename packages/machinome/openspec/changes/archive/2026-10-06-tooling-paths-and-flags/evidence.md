# Evidence — `tooling-paths-and-flags`

Cycle 5 of the fix-warts-3 campaign (`workflow/ongoing/fix-warts-3.md`).
Bench `machinome/WTs/fix-warts-3`, branch `fix-warts-3`, planning commit
`87b24b0f1669067b0ffd3a9311c2718a7683b5b4` (`git -C <bench> rev-parse
HEAD`), with a clean tree. Every framework command ran as `env -C <bench>
PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/<tool> ...` (Python
3.12.3); `python -c 'import machinome; print(machinome.__file__)'` printed
`<bench>/machinome/__init__.py`. The project command ran as `env -C <Clocks>
PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/machinome snapshot
wall_clock_11 --time 0 --imgsize 1200x1000 --autocenter --viewall --preview -o
<scratch>/<stage>/<name>.png`, with `<Clocks>` =
`projects/3DPrintedClocks` (branch `solid-node-simulation`, `ec2a05d`), the
command its `simulation/early-clocks-2026-09-13.md` documents with `--preview`
added; its images went to the scratchpad, never into the project.
`<scratch>` is the campaign scratchpad's `cycle5/` directory; this stage's
outputs are in its `apply-baseline/` and `apply-after/` subdirectories, and
Stage P's are at its top level, left in place.

Binaries and tools: OpenSCAD 2021.01 (`/usr/bin/openscad --version`), git
2.43.0, `xvfb-run` on the PATH and no `DISPLAY`; the viewer package installed
editable from the workspace's `machinome-viewer` checkout at `24d9ad2`
(clean tree); `flake8` 7.3.0 (the pyenv shim; the venv has none), `black`
26.5.1, `openspec` 1.6.0. One test run, build or snapshot of ours at a time
throughout; before each heavy run the process table was checked for another
`pytest` or `machinome test|snapshot|build` of the campaign, and none was
running.

The viewer's committed fixture,
`machinome-viewer/machinome_viewer/widget/src/parity-fixture.json`, has
SHA-256 `74e9fbfc65e0e705f2c11d3a7ad2e1c6ef49b1df4ac8c55f22c94f0e8a5fce28`
before this stage; nothing in this stage writes it (section 4.4).

The two Stage P probe scripts, as they stand in the scratchpad (which is not
durable). Each patches a command builder in its own process only and then
runs `machinome.cli.manage()`.

`<scratch>/f2_equals_probe.py`:

```python
"""Stage P probe: does `--preview=throwntogether` carry `machinome snapshot
--preview` through OpenSCAD 2021.01? Patches the command builder in this
process only; the bench source is untouched."""

import sys

from machinome.cli import manage
from machinome.viewers import openscad

original = openscad.OpenScadRenderer.build_command


def joined(self, node, args, output):
    command = [
        '--preview=throwntogether' if token == '--preview' else token
        for token in original(self, node, args, output)]
    print('openscad command:', command, file=sys.stderr)
    return command


openscad.OpenScadRenderer.build_command = joined
sys.exit(manage())
```

`<scratch>/f3_equals_probe.py`:

```python
"""Stage P probe: does the `--opt=value` spelling carry a negative-leading
camera through the real viewer capture? Patches the command builder in
this process only; the bench source is untouched."""

import sys

from machinome.cli import manage
from machinome.viewers import browser

original = browser.BrowserRenderer.capture_command


def joined(self, staging, args, output):
    command = original(self, staging, args, output)
    out = []
    skip = False
    for index, token in enumerate(command):
        if skip:
            skip = False
            continue
        if token in ('--view', '--up'):
            out.append(f'{token}={command[index + 1]}')
            skip = True
        else:
            out.append(token)
    print('capture command:', out, file=sys.stderr)
    return out


browser.BrowserRenderer.capture_command = joined
sys.exit(manage())
```

## 1. Baseline on the unmodified tree (87b24b0)

### 1.2 Finding 1: the generator from a worktree

`env -C <bench> PYTHONPATH=<bench> .venv/bin/python
tools/generate_parity_fixture.py` (log `<scratch>/apply-baseline/f1.log`):
exit 1, wall 3.5 s, after the whole build, ending

```
  File "/home/asa/devel/machinome/machinome/WTs/fix-warts-3/tools/generate_parity_fixture.py", line 481, in main
    with open(path, 'w') as handle:
         ^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/home/asa/devel/machinome/machinome/WTs/machinome-viewer/machinome_viewer/widget/src/parity-fixture.json'
```

`/home/asa/devel/machinome/machinome/WTs/machinome-viewer` does not exist
(`ls`: "No such file or directory"), so nothing was written.

### 1.3 Finding 2: `--preview` on the framework's fixture

`machinome snapshot tests/web_snapshot_project.py --viewall --autocenter
--imgsize 800x600 --preview -o <scratch>/apply-baseline/f2-a1-before-preview.png`:
exit 1, wall 0.37 s, no image:

```
 INFO - viewers.openscad - Rendering .../tests/_build/web_snapshot_project-AsymmetricSnapshotPart-cbb97835ba9a.scad to .../apply-baseline/f2-a1-before-preview.png
OpenSCAD rendering failed:

```

The same command without `--preview`
(`-o <scratch>/apply-baseline/f2-a1-before-plain.png`): exit 0, wall 0.50 s,
`Snapshot saved to ...`, a 9386-byte PNG.

### 1.4 Finding 2 in 3DPrintedClocks

`git -C <Clocks> status --short` before:

```
 M screenshots/wall_clock_03.png
?? WTs/
```

The project command to `<scratch>/apply-baseline/f2-clock11-a1-before.png`
(log `f2-clock11.log`, 23 lines): exit 1, wall 7.5 s (the build was current
from Stage P), no image. Lines 4-6:

```
 INFO - viewers.openscad - Rendering /mnt/data/machinome-projects/3DPrintedClocks/_build/wall_clock_11/simulation/wall_clock_11/clock-WallClock11,facing=45.0,pendulum_period=1.0,plate_thick=6.0-a8d46459b123.scad to .../apply-baseline/f2-clock11-a1-before.png
OpenSCAD rendering failed:

```

The rest of the log is the clock's own printout (rod lengths, pendulum).
`git -C <Clocks> status --short` after: identical to before.

### 1.5 Finding 3: the Voron-shaped camera under the web renderer

`machinome snapshot tests/web_snapshot_project.py --renderer web --autocenter
--viewall --imgsize 1400x1100 --camera 0,0,0,65,0,35,1400 -o
<scratch>/apply-baseline/f3-a1-before.png`: exit 1, wall 1.0 s, no image:

```
Error: usage: machinome-viewer capture [-h] -o OUTPUT [--imgsize WxH] [--time TIME]
                                [--view EYE,TARGET] [--up X,Y,Z] [--fov FOV]
                                staging
machinome-viewer capture: error: argument --up: expected one argument
```

### 1.6 The three test modules

`pytest -q -p no:cacheprovider tests/test_snapshot.py
tests/test_browser_renderer.py tests/test_generate_parity_fixture.py`:

```
127 passed, 1 skipped, 2 warnings, 5 subtests passed in 6.04s   (wall 7.1 s)
```

The skip is `BrowserSnapshotEndToEndTest` ("set MACHINOME_WEB_SNAPSHOT_E2E=1
to photograph through the installed viewer"), opt-in by design.

## 2. Red tests, on the unmodified source (87b24b0)

New and revised tests:

- `tests/test_generate_parity_fixture.py`: a new class
  `DefaultFixturePathTest` (2.1). Its `setUp` makes, under a temporary
  `base` (resolved): `base/framework`, `git init` and one empty commit;
  `base/framework/WTs/bench`, made with `git worktree add -q`; `base/plain`,
  a directory outside Git; and
  `base/machinome-viewer/machinome_viewer/widget/src/`. Git runs, for the
  fixture and for the tool alike, with no inherited `GIT_*` variable,
  `GIT_CEILING_DIRECTORIES=base`, `GIT_CONFIG_GLOBAL=/dev/null`,
  `GIT_CONFIG_NOSYSTEM=1` and a fixture author and committer; the tool's
  call runs under `patch.dict(os.environ, <that environment>, clear=True)`.
  Six tests:
  `test_a_worktree_names_the_viewer_beside_the_primary_checkout`,
  `test_the_primary_checkout_names_the_same_file`,
  `test_no_viewer_checkout_is_refused_by_name` (the message names
  `machinome-viewer`, the directory looked for, and "argument"),
  `test_a_directory_outside_git_is_refused_by_name`,
  `test_the_refusal_comes_before_anything_is_built` (`ROOT` patched to the
  plain directory, `build` patched to raise; `main([])` exits and `build`
  is never called), and
  `test_an_explicit_path_is_written_wherever_the_checkout_stands` (`ROOT`
  patched to the plain directory, `build` patched to return an empty
  fixture; `main([<base>/out.json])` writes it).
- `tests/test_snapshot.py`, `SnapshotCommandBuildingTest` (2.2):
  `test_preview_flag` rewritten (`'--preview=throwntogether' in cmd`,
  `'--preview' not in cmd`); `test_preview_never_takes_the_scad_path_for_its_value`
  added (`cmd[-1]` ends `.scad`, `cmd[-2] == '--preview=throwntogether'`).
- `tests/test_browser_renderer.py`, `CaptureDelegationTest` (2.3-2.5):
  `test_a_negative_leading_vector_travels_with_its_option` added, with
  subtests for cameras `0,0,0,65,0,35,1400` and `-100,20,30,0,0,0`, checked
  against `parse_camera`, and asserting the first camera's up does begin
  negative; `test_the_viewer_parses_the_command_it_is_handed` added under
  `needs_viewer`, running the installed viewer as a process on a staging
  directory that does not exist; `test_a_requested_camera_is_resolved_here_and_handed_over`
  revised to read the one `--view=` and `--up=` token (through a helper,
  `_joined_value`) and to keep its `--fov` checks;
  `test_no_camera_means_no_camera_flags` revised to assert that no token
  starts with `--view`, `--up` or `--fov`.

One pytest process, `pytest -q -p no:cacheprovider
tests/test_generate_parity_fixture.py::DefaultFixturePathTest
tests/test_snapshot.py::SnapshotCommandBuildingTest::test_preview_flag
tests/test_snapshot.py::SnapshotCommandBuildingTest::test_preview_never_takes_the_scad_path_for_its_value
tests/test_browser_renderer.py::CaptureDelegationTest` (log
`<scratch>/apply-baseline/red-2.6.log`):

```
12 failed, 6 passed in 3.27s   (wall 4.4 s)
```

| test | reason, verbatim |
|---|---|
| the four `default_fixture` tests | `AttributeError: module 'generate_parity_fixture' has no attribute 'default_fixture'` |
| `test_the_refusal_comes_before_anything_is_built`, `test_an_explicit_path_is_written_wherever_the_checkout_stands` | `TypeError: main() takes 0 positional arguments but 1 was given` |
| `test_preview_flag` | `AssertionError: '--preview=throwntogether' not found in ['openscad', '-o', 'test_output.png', '--imgsize', '1920,1080', '--projection', 'p', '--colorscheme', 'Cornfield', '--preview', '/tmp/test_node.scad']` |
| `test_preview_never_takes_the_scad_path_for_its_value` | `AssertionError: '--preview' != '--preview=throwntogether'` |
| `test_a_negative_leading_vector_travels_with_its_option`, camera `0,0,0,65,0,35,1400` | `AssertionError: '--view' unexpectedly found in [... '--view', '727.7715070159583,-1039.3654271085456,591.6655664369792,0.0,0.0,0.0', '--up', '-0.242403876506104,0.34618861305875415,0.9063077870366499', '--fov', '22.5']` |
| the same, camera `-100,20,30,0,0,0` | `AssertionError: '--view' unexpectedly found in [... '--view', '-100.0,20.0,30.0,0.0,0.0,0.0', '--up', '0.0,0.0,1.0', '--fov', '22.5']` |
| `test_a_requested_camera_is_resolved_here_and_handed_over` (revised) | `AssertionError: 0 != 1 : [... '--view', '10.0,20.0,30.0,0.0,0.0,0.0', '--up', '0.0,0.0,1.0', '--fov', '22.5']` (no `--view=` token) |
| `test_the_viewer_parses_the_command_it_is_handed` | `AssertionError: 2 == 2 : usage: machinome-viewer capture [-h] -o OUTPUT [--imgsize WxH] [--time TIME] [--view EYE,TARGET] [--up X,Y,Z] [--fov FOV] staging` / `machinome-viewer capture: error: argument --up: expected one argument` |

The six passing tests are `CaptureDelegationTest`'s other five and the
revised `test_no_camera_means_no_camera_flags`, which passes before and
after, as planned.

## 3. The change

- `tools/generate_parity_fixture.py`: `import subprocess`; the module-level
  `FIXTURE` (read from `sys.argv` at import) replaced by `VIEWER_FIXTURE`, the
  fixture's path inside the viewer checkout; `default_fixture(root=None)`,
  which runs `git -C <root> rev-parse --git-common-dir`, joins its answer to
  `root`, takes the common directory's grandparent as the workspace and
  returns `<workspace>/machinome-viewer/machinome_viewer/widget/src/parity-fixture.json`,
  or exits naming `root` (no Git checkout, or git missing) or the directory
  looked for (no viewer checkout), each with "give the fixture path as the
  first argument"; `main(argv=None)`, which resolves the path before
  `build()`. The comment above `VIEWER_FIXTURE` and the docstring's run
  section are revised as design.md Decision 2 gives them.
- `machinome/viewers/openscad.py`, `build_command`: `--preview` becomes
  `--preview=throwntogether`, with a two-line comment.
- `machinome/viewers/browser.py`, `capture_command`: `--view=<eye,target>`
  and `--up=<x,y,z>` one token each, with a three-line comment; `--fov`
  unchanged.

The two sibling generators, `tools/generate_clocked_corpus.py` and
`tools/generate_running_corpus.py`, keep a module-level `FIXTURE` from
`sys.argv`, but their default is `ROOT/tests/...` inside the checkout they
run from, so a worktree resolves them correctly; they are not touched.
`tests/test_clocked_corpus.py` imports `tools.generate_parity_fixture` for
`vocabulary_cases` and reads no `FIXTURE`.

### 3.4 Green

Section 2's selection, the same command (log
`<scratch>/apply-after/green-3.4.log`):

```
16 passed, 2 subtests passed in 3.15s   (wall 4.2 s)
```

The three modules of 1.6 (log `<scratch>/apply-after/tests-3.4.log`):

```
136 passed, 1 skipped, 2 warnings, 7 subtests passed in 6.13s   (wall 7.2 s)
```

That is 1.6's 127 plus the nine new tests (six `DefaultFixturePathTest`,
`test_preview_never_takes_the_scad_path_for_its_value`,
`test_a_negative_leading_vector_travels_with_its_option`,
`test_the_viewer_parses_the_command_it_is_handed`), and 1.6's 5 subtests
plus the new test's 2. The skip is the same opt-in end-to-end test.

## 4. Real runs after the change

### 4.1 Finding 2 on the framework's fixture

1.3's command to `<scratch>/apply-after/f2-a1-after.png`: exit 0, wall
0.48 s, `Snapshot saved to ...`, an 800x600 RGB PNG. Read: the asymmetric
fixture in OpenSCAD's yellow on the Cornfield background, a long bar with a
small cube at its front-left end and a tall block standing at its back
right, framed whole. It is byte-identical (`cmp`) to Stage P's probe image
`<scratch>/f2-equals-probe.png`. Against 1.3's plain image it differs in 2
pixels (bounding box `(210, 457, 504, 496)`); two plain runs (Stage P's
`f2-before-plain.png` and 1.3's) differ in none. This fixture is a union of
boxes, which both previewers draw alike.

What the previewer changes shows on a subtracted volume. A throwaway project
in the scratchpad, `<scratch>/tt_project/` (`pyproject.toml` with `model =
"hollow_cube:HollowCube"`, and `hollow_cube.py`: a `Solid2Node` rendering
`cube(10, center=True) - sphere(6.5)`), snapshotted through the bench with
`env -C <scratch>/tt_project PYTHONPATH=<bench> .venv/bin/machinome snapshot
hollow_cube.py --imgsize 400x300 --autocenter --viewall [--preview] -o
<scratch>/apply-after/tt-{plain,preview}.png`: both exit 0. Read: the plain
image is the yellow cube with three round holes through which the sphere's
inner surface shows; the `--preview` image is the same cube with the
subtracted sphere drawn as a solid green body filling each hole, which is
OpenSCAD's ThrownTogether rendering of a difference. The two differ in
25811 pixels (bounding box `(97, 39, 311, 258)`), the same count as Stage
P's direct OpenSCAD probes (`probe__preview_throwntogether.png` against
`probe-default.png`).

### 4.2 Finding 2 in 3DPrintedClocks

`git -C <Clocks> status --short` before: ` M screenshots/wall_clock_03.png`,
`?? WTs/`. The project command to
`<scratch>/apply-after/f2-clock11-a1-after.png` (log `f2-clock11.log`):
exit 0, wall 8.6 s, `Snapshot saved to ...` at line 22, a 1200x1000 PNG.
Read: wall clock 11 seen from the front, on the Cornfield background,
small at the top of a tall frame: the movement with its coloured gears (red,
orange, green, cyan), the blue ring of the hand avoider, and a purple
cylindrical weight below it; the pendulum rod runs down the middle of the
image, broken by a short gap at mid-height, to a small purple bob near the
bottom. It is byte-identical to Stage P's probe image
`<scratch>/f2-clock11-probe.png`, and differs from Stage P's plain image
`f2-clock11-plain.png` in 2 pixels (bounding box `(591, 89, 599, 418)`).
`git -C <Clocks> status --short` after: unchanged.

### 4.3 Finding 3: the Voron-shaped camera

1.5's command to `<scratch>/apply-after/f3-a1-after.png`: exit 0, wall
2.3 s (the fixture's STL was rebuilt first: the test run of 3.4 had
changed `tests/_build`), `Snapshot saved to ...`. A 1400x1100 RGBA PNG; its
corner pixel is `(0, 0, 0, 0)` and its opaque pixels lie in `(695, 504,
769, 566)`. Read: on a transparent background, the asymmetric part small at
the centre (the camera stands 1400 mm away from a 32 mm part), seen from
above and in front, in the viewer's normal-coloured faces (blue, pink,
green): the long bar, the small cube at its front-left end, and the tall
block at its back right. It is pixel-identical to Stage P's probe image
`<scratch>/f3-equals-probe.png`.

### 4.4 Finding 1, without writing into the viewer

Loading the bench's tool with `spec_from_file_location` in a `python -c`
and printing `default_fixture()` and
`default_fixture('/home/asa/devel/machinome/machinome')` (exit 0):

```
/home/asa/devel/machinome/machinome-viewer/machinome_viewer/widget/src/parity-fixture.json
/home/asa/devel/machinome/machinome-viewer/machinome_viewer/widget/src/parity-fixture.json
```

`tools/generate_parity_fixture.py <scratch>/apply-after/parity-fixture-after.json`:
exit 0, wall 3.7 s, two `FutureWarning`s from the corpora (`Axis.render()`
and `Valvetrain.render()` read a driver), and

```
.../apply-after/parity-fixture-after.json: 451 expression cases (0 containing `^`, 155 from the vocabulary corpus, covering all 14 emitted builtins), 22 conversions, 4 flexible bindings of 3858 vertices (7 pinned)
```

`cmp` with Stage P's `<scratch>/parity-fixture.json`: identical.

`env -C <bench> GIT_DIR=<scratch>/no-such-git PYTHONPATH=<bench>
.venv/bin/python tools/generate_parity_fixture.py` with no argument: exit 1,
wall 2.96 s,

```
generate_parity_fixture: /home/asa/devel/machinome/machinome/WTs/fix-warts-3 is not a Git checkout, so no machinome-viewer checkout can be found beside it; give the fixture path as the first argument
```

Loading the tool alone (its module-level imports of the framework and the
corpora) takes 2.96 s wall, and `build()` alone 0.46 s, so the refusal costs
the import and nothing of the build; `test_the_refusal_comes_before_anything_is_built`
proves the order directly. No run without an argument and without the
forced refusal was made, since it would rewrite the viewer's committed
fixture. Afterwards `git -C /home/asa/devel/machinome/machinome-viewer
status --short` printed nothing, and the committed fixture's SHA-256 is
still `74e9fbfc...5fce28`.

## 5. Changelog and manual

- 5.1: design.md Decision 6's two bullets, verbatim, added to
  `docs/project/changelog.rst` after the existing bullets of its one
  `Unreleased` section (after `resolve-repeated-joints-per-copy`'s).
- 5.2: `grep -rn -- "--preview\|--up\b\|generate_parity_fixture"` over
  `docs/` and `CONTRIBUTING.rst`, leaving out `docs/adrs/`, `docs/releases/`
  and the changelog, finds four lines:
  - `docs/reference/cli.rst:285-289`, `--render` / `--preview`:
    "``--preview`` uses the ThrownTogether preview mode (faster, may show
    artifacts)", which is now true; the same entry's "``--render`` does a
    full render (OpenSCAD's default: slower, accurate)" was already wrong
    before this change and is filed as a finding (7.3), not edited;
  - `docs/reference/cli.rst:297`, the OpenSCAD-only options refused under
    `--renderer web`: unchanged behaviour;
  - `docs/architecture.md:3158` and `CONTRIBUTING.rst:144` name the
    generator and what it produces, not where it writes: still correct.

  `docs/reference/cli.rst:299`, "``--camera`` accepts both OpenSCAD camera
  forms under either renderer", is now true for a camera of any signs. No
  page is edited.

## 6. Checks

### 6.1 Lint, compared against HEAD

On the six touched Python files (`machinome/viewers/openscad.py`,
`machinome/viewers/browser.py`, `tools/generate_parity_fixture.py`,
`tests/test_snapshot.py`, `tests/test_browser_renderer.py`,
`tests/test_generate_parity_fixture.py`), and on the same six files as they
stand at HEAD (`git show HEAD:<file>` into `<scratch>/head-lint/`):

- `flake8 --max-line-length=89` (the pyenv shim): 13 findings now, the same
  13 at HEAD, each at its shifted line: three E501 and one F401 in
  `tests/test_browser_renderer.py`; F401 `MagicMock`, two E128, four E501
  and F401 `tests.flat_project` in `tests/test_snapshot.py`; E302 at
  `def sentinels(count)`, `tools/generate_parity_fixture.py:155` (`:150` at
  HEAD). None is on a line this change wrote.
- `black --check` (26.5.1): "6 files would be reformatted" now and at HEAD
  alike; the repository is not black-formatted and the CI step is
  `continue-on-error`, as the earlier cycles of this campaign record.

### 6.2 The full suite

Run once, alone, after the archive (8.2) rather than before section 7, so
that it ran on the final tree: the records written between the two places
are Markdown, but the archived tree is the one the orchestrator reviews.
Before it, the process table held no other `pytest` or `machinome
test|snapshot|build` of ours.

`pytest -q -p no:cacheprovider` at the bench root (log
`<scratch>/apply-after/full-suite.log`), exit 0:

```
4653 passed, 4 skipped, 55 warnings, 6644 subtests passed in 736.96s (0:12:16)   (wall 739.9 s)
```

No failure and no error; no EMFILE.

## 7. Warts

- 7.1: moved verbatim to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md`, under
  `` ## `tooling-paths-and-flags` ``, each with a "From ..." line: item 9
  of "Expression math and mechanisms (2026-09-06)", "Framework"; item 14 of
  "Internal-Cycloidal-Actuator (2026-09-06, project refactor pass)"; and
  from "Voron-2 — native contact measurements and snapshot arguments (5
  October 2026)" the whole subsection "A negative-leading camera vector is
  rejected at the viewer subprocess boundary" and the paragraph after it
  ("The same project also reproduced existing **item 14** ... evidence for
  that existing finding."). A "What shipped" paragraph names the
  generator's resolution through Git's common directory and its refusal
  before building, `--preview=throwntogether`, and `--view=`/`--up=` as one
  token each. All of it deleted from `warts.md`; the Voron-2 section keeps
  its opening paragraph, its two other subsections, the paragraph on the
  project's original archive and its main-branch recheck.
- 7.2: the "Standing triage", "Planned, never done" bullet naming item 9
  and item 14 deleted.
- 7.3: a new section after "Findings from the framework cycle
  `children-refuse-early-reads` (2026-10-06)", "Findings from the framework
  cycle `tooling-paths-and-flags` (2026-10-06)", with two bullets:
  `--render` accepted and never forwarded while its help calls it the
  default (the facts of design.md Open Question 1, with the triage line
  "Held for the pilot: forwarding changes what an existing flag draws", the
  orchestrator's answer at review having been to file it); and a failed
  OpenSCAD render reporting only its standard error (Open Question 2's
  facts and its candidate fix, print standard output when standard error
  is empty). The byte-identity of OpenSCAD's default image and
  `--preview=opencsg` was rechecked in this stage (`cmp
  <scratch>/probe-default.png <scratch>/probe__preview_opencsg.png`:
  identical).
- `workflow/ongoing/fix-warts-3.md`: a Progress line for this cycle, after
  cycle 4's.

## 8. Sync and archive

- 8.1: by hand. Into `openspec/specs/cli/spec.md`, "Snapshot command": the
  paragraph on `--preview` after the OpenSCAD-renderer paragraph, and the
  scenario "A ThrownTogether preview" after "Headless snapshot". Into
  `openspec/specs/web-snapshot/spec.md`, "A requested camera is honoured or
  refused, never approximated": the sentence on signs, and the scenario "A
  camera vector that begins with a negative component" after "A rotated
  camera". Into `openspec/specs/kinematics/spec.md`: the ADDED requirement
  "The parity fixture is regenerated from any checkout of the framework",
  with its four scenarios, after "The parity corpus covers every symbolic
  function". Before the sync, `diff` of each modified baseline requirement
  against its delta showed only the added paragraph or sentence and the
  added scenario (and the trailing blank line). After it, each of the
  three requirements, cut from the spec and from the delta up to the next
  heading, compares equal (a short Python check). `git diff --stat --
  openspec/specs`: cli +14, kinematics +41, web-snapshot +11 -2. `openspec
  validate cli`, `web-snapshot`, `kinematics`: each "Specification '<name>'
  is valid".
- `openspec validate tooling-paths-and-flags` before archiving: "Change
  'tooling-paths-and-flags' is valid".
- 8.2: `openspec archive tooling-paths-and-flags --yes --skip-specs` (the
  specs were synced by hand in 8.1, so the CLI's own sync, which would add
  the requirements a second time, was skipped): "Change
  'tooling-paths-and-flags' archived as '2026-10-06-tooling-paths-and-flags'".
  Its warnings: the Why section's length, and 27 of 30 tasks complete
  (6.2, 8.2 and 8.3, done after it and ticked in the archived copy).
  `openspec validate --specs`: `Totals: 45 passed, 0 failed (45 items)`.
- 8.3: 1.6's three modules, which hold section 2's tests, once more after
  the archive (exit 0): `136 passed, 1 skipped, 2 warnings, 7 subtests
  passed in 6.71s` (wall 8.0 s), as in 3.4.
- Nothing committed on the bench. Nothing written in 3DPrintedClocks (its
  status unchanged throughout) or in the `machinome-viewer` checkout
  (status clean, fixture hash unchanged). Voron-2 was not run.
