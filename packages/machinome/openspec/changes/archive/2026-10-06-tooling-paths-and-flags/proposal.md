## Why

Three commands the framework composes for another tool are commands that
tool does not accept. None of them changes a verdict, a document or an
identity; each makes a documented command fail.

**1. The parity fixture generator cannot run from a worktree.**
`workflow/warts.md`, "Expression math and mechanisms (2026-09-06)",
Framework item 9:

> **`tools/generate_parity_fixture.py` cannot run from a worktree.** Its
> default output path resolves to `ROOT/../machinome-viewer/...`, which
> from `machinome/WTs/<name>/` is a directory that does not exist. Resolve
> through the Git common directory, as the shop contract prescribes for
> workspace paths, or require the output argument. Evidence:
> `expression-math` task 5.4.

**2. `machinome snapshot --preview` hands OpenSCAD a bare `--preview`.**
Same file, "Internal-Cycloidal-Actuator (2026-09-06, project refactor
pass)", item 14:

> **`machinome snapshot --preview` passes a bare `--preview` to OpenSCAD
> 2021.01**, which rejects it with a usage dump
> (`OpenScadRenderer.build_command` emits it unconditionally). Seen in
> 3DPrintedClocks.

Voron-2 reproduced it ("Voron-2 — native contact measurements and
snapshot arguments (5 October 2026)": "the bare OpenSCAD `--preview`
consuming the following filename").

**3. A camera whose up direction begins with a negative component is
refused at the viewer's command line.** Same Voron-2 section, "A
negative-leading camera vector is rejected at the viewer subprocess
boundary":

> `machinome snapshot --renderer web --autocenter --viewall --imgsize
> 1400x1100 --camera 0,0,0,65,0,35,1400` fails with `argument --up:
> expected one argument`. The tested framework's `viewers/browser.py`
> emits `--up` and its comma tuple as separate tokens. This camera
> produces `(-0.242403876506104, 0.34618861305875415,
> 0.9063077870366499)`; the negative-leading tuple is rejected by the
> viewer argument parser. The same construction is used for `--view`.
> [...] **Triage.** Framework subprocess argument construction, not a
> new camera API.

The 2026-09-14 standing triage planned the first two as the change
`tooling-paths-and-flags`, which was never started; the campaign adds the
third because it has the same shape.

**Reproduced on the bench `fix-warts-3` at `47cfc89`** (design.md,
Context, gives every command and its output):

- From the bench, a worktree, `python tools/generate_parity_fixture.py`
  with no argument builds the whole fixture and then fails with
  `FileNotFoundError: ... '/home/asa/devel/machinome/machinome/WTs/machinome-viewer/machinome_viewer/widget/src/parity-fixture.json'`.
- `machinome snapshot tests/web_snapshot_project.py --viewall --autocenter
  --imgsize 800x600 --preview` exits 1 with `OpenSCAD rendering failed:`
  and nothing after it; the same command without `--preview` writes the
  image. In 3DPrintedClocks, the documented
  `machinome snapshot wall_clock_11 --time 0 --imgsize 1200x1000
  --autocenter --viewall`, with `--preview` added, fails the same way after
  71 s; without it, it writes the clock. OpenSCAD 2021.01's own grammar
  is `--preview arg  [=throwntogether] -for ThrownTogether preview png`: a
  bare `--preview` takes the next token, the `.scad` path, as its value,
  and OpenSCAD prints its usage on standard output.
- `machinome snapshot tests/web_snapshot_project.py --renderer web
  --autocenter --viewall --imgsize 1400x1100 --camera
  0,0,0,65,0,35,1400` exits 1 with the viewer's `argument --up: expected
  one argument`.

## What Changes

- **The generator finds the viewer checkout through Git's common
  directory.** With no argument, `tools/generate_parity_fixture.py` asks
  Git for the common directory of the checkout it sits in. The primary
  framework checkout is that directory's parent, and the viewer's fixture
  is `machinome_viewer/widget/src/parity-fixture.json` in the
  `machinome-viewer` checkout beside it. The primary checkout and every
  worktree under `WTs/` therefore resolve to the same file, the one the
  viewer repository commits. When Git cannot answer, or no such directory
  exists, the tool refuses before building anything, naming where it
  looked and saying that the output path may be given as the argument. An
  argument is used as given, as today. The resolution moves from module
  level into a function, `default_fixture()`, called from `main(argv)`,
  so the existing test module can load the tool without its result
  depending on pytest's own arguments. The tool's docstring, which gives
  a stale path (`machinome/viewers/widget/tools/...`), says how to run it
  and where it writes.
- **`--preview` reaches OpenSCAD as `--preview=throwntogether`.** That is
  the value OpenSCAD 2021.01 documents for the ThrownTogether preview,
  which is what `machinome snapshot --preview` has always been documented
  to select ("ThrownTogether preview (faster, may show artifacts)"). One
  token, so it can never take the `.scad` path as its value.
- **The web renderer hands the viewer `--view=<eye,target>` and
  `--up=<x,y,z>` as one token each.** Python's argparse accepts
  `--option=value` whatever the value begins with, and the viewer's
  `capture` parser already accepts it (design.md, Context). `--fov`,
  `--imgsize` and `--time` are unchanged. Their values are plain numbers,
  which argparse already accepts after a minus sign, or are validated
  upstream so that they never begin with one.
- Tests that pin the old token shapes are updated:
  `SnapshotCommandBuildingTest.test_preview_flag` (`tests/test_snapshot.py`)
  and `CaptureDelegationTest`'s two camera tests
  (`tests/test_browser_renderer.py`).
- Records: two changelog bullets under `Unreleased`, items 9 and 14 and
  the Voron-2 camera entry moved to the campaign's `resolved.md`, and
  two related findings this cycle made filed in `warts.md` (below).

**Deliberately out**, with the reason:

- **`--render`.** `machinome snapshot --render` is accepted and never
  forwarded: `build_command` does not read it. The help and the manual
  call it "the default ... full render". OpenSCAD 2021.01's PNG default
  is the OpenCSG preview, and its full render needs `--render=<value>`.
  Forwarding it would change what an existing flag draws (a CGAL render:
  slower, and without per-part colour). Correcting only the wording
  would choose the other answer. Either way it is a choice about
  appearance that no sighting asks for. Filed as a wart, and design.md
  Open Question 1 gives a recommendation.
- **The empty failure message.** When OpenSCAD fails, the snapshot prints
  `OpenSCAD rendering failed:` followed by its standard error only.
  OpenSCAD's usage dump goes to standard output, so the reproduction above
  prints nothing after the colon. This is a defect in reporting, not in
  composing the command, and it is filed as a wart (design.md, Open
  Question 2).
- **`machinome snapshot --camera -100,20,30,0,0,0`** is refused by
  machinome's own parser (`argument --camera: expected one argument`).
  This is the user's own spelling and the standard argparse rule, and
  `--camera=-100,...` works. No sighting asks for a change, and Voron's
  camera began with `0`.
- **OpenSCAD's `--camera`** with a negative-leading value as a separate
  token is accepted by OpenSCAD 2021.01 and renders (design.md, Context).
  Nothing changes there.
- **Refreshing the viewer's committed parity fixture.** Regenerated from
  the bench, it has the same 451 keys and the same expected values as
  the one `machinome-viewer` commits, but 249 expressions are rewritten
  over a 145-entry bindings table, where the committed one has 4 entries.
  That is the viewer repository's to refresh, and this change writes
  nothing there (design.md, Open Question 3).
- **The viewer's static-export stall** that Voron saw without a camera
  ("Failed to fetch") belongs to the viewer's own `workflow/warts.md`, as
  the entry says.
- **Projects.** 3DPrintedClocks is run, never changed. Voron-2 is not
  run: its camera is reproduced on the framework's own snapshot fixture.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `cli`: the requirement "Snapshot command" is modified. Under the
  OpenSCAD renderer, `--preview` draws the image with OpenSCAD's
  ThrownTogether previewer, and a snapshot with `--preview` writes its
  image as one without it does. One scenario is added, "A ThrownTogether
  preview". Every existing scenario is carried unchanged.
- `web-snapshot`: the requirement "A requested camera is honoured or
  refused, never approximated" is modified. A camera specification is
  honoured whatever the signs of its values, including one whose
  resolved eye or up direction begins with a negative component. One
  scenario is added, "A camera vector that begins with a negative
  component".
  The four existing scenarios are carried unchanged.
- `kinematics`: one requirement is added, "The parity fixture is
  regenerated from any checkout of the framework", with four scenarios:
  from a worktree, from the primary checkout, with no viewer checkout
  beside it, and with an explicit path. "The parity corpus covers every
  symbolic function" is not edited.

## Impact

- **Code:**
  - `machinome/viewers/openscad.py`: `OpenScadRenderer.build_command`,
    one line (`:180`).
  - `machinome/viewers/browser.py`: `BrowserRenderer.capture_command`,
    two lines (`:194-195`).
  - `tools/generate_parity_fixture.py`: `FIXTURE` at module level
    (`:77-79`) gives way to `default_fixture(root=None)`. `main()`
    becomes `main(argv=None)`. The docstring's run section and the
    comment at `:73-76` are revised.
- **Tests:**
  - `tests/test_snapshot.py`: `test_preview_flag` is rewritten, and one
    test is added.
  - `tests/test_browser_renderer.py`: two tests are revised, and two are
    added. One of the new tests runs the installed viewer as a process,
    under `needs_viewer`.
  - `tests/test_generate_parity_fixture.py`: a new class
    `DefaultFixturePathTest` over a temporary primary checkout, its
    worktree and a viewer directory beside them.
- **Projects:** 3DPrintedClocks' `wall_clock_11` snapshot with
  `--preview` writes its image after the change. Its tree is untouched
  (pre-existing dirt: ` M screenshots/wall_clock_03.png`, `?? WTs/`).
- **Documents, identities, published artifacts:** unchanged.
- **Manual:** `docs/reference/cli.rst` already says `--preview` uses the
  ThrownTogether preview and that `--camera` behaves the same under
  either renderer. With this change both statements become true, and
  neither is edited. The changelog gets two bullets. `CONTRIBUTING.rst`
  and `docs/architecture.md` name the generator without saying where it
  writes, so they stay correct.

## Authorization

The pilot's mandate of 6 October 2026 for the fix-warts-3 campaign
(`workflow/ongoing/fix-warts-3.md`, "Mandate"): "work on the items you can
autonomously, orchestrating opus subagents and using empirical evidence
from projects to validate, other than your adversarial review. if
something needs my input, record and defer, you'll go unsupervised." This
change is the campaign table's cycle 5, `tooling-paths-and-flags`,
validated in 3DPrintedClocks (`wall_clock_11`) and on the Voron-2 camera
command run against the framework's own snapshot fixture. design.md's
Open Questions 1 to 3 are left to the orchestrator's review. Each has a
recommendation, and none of them blocks the three fixes.
