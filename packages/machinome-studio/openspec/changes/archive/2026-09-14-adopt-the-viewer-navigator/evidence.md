# Evidence — adopt-the-viewer-navigator

The implementer fills this file in as the increments land; the reviewer reads
it instead of re-running the cycle. Every section below is required. A command
without its output, a count without its baseline, or a red step recorded only
as "failed" is not evidence.

## 0. Baseline

Worktree: `/home/asa/devel/libresolid-studio/WTs/viewer-navigator`, branch
`viewer-navigator`, starting head `042cc95214d676a14a328dbde113bbb00634cb17`
("openspec: propose adopting the viewer's navigator in the Model panel").

```
$ npm --prefix floor/frontend run test
> shop-floor-frontend@0.0.0 test
> tsc -b --pretty false
(no output; exit 0)
```

```
$ npm --prefix floor/frontend run build
> shop-floor-frontend@0.0.0 build
> tsc -b && vite build
✓ 763 modules transformed.
✓ built in 7.00s
(exit 0; floor/static written, untracked)
```

```
$ /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest tests -q
....................................................................................................................
....(160 subtests)...
1 failed, 339 passed, 1 skipped, 2 warnings, 160 subtests passed in 147.36s
FAILED tests/test_license_headers.py::LicenseHeaderTest::test_every_tracked_source_file_has_agpl_header
  AssertionError: source files missing AGPL headers: ['docs/motion-general-refactor/capture_poses.py']
```
Pre-existing, unrelated to this change: `docs/motion-general-refactor/capture_poses.py`
is an untracked leftover from earlier work in this worktree's ancestry (visible
in the git status at session start), not touched by this change. The 1 skip is
also pre-existing — see below.

```
$ /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest tests/test_project_open.py tests/test_project_preparation.py -q
55 passed, 1 skipped, 1 warning, 27 subtests passed in 12.18s
```
The 1 skip is `tests/test_project_preparation.py:564` ("development workspace
solid-node installation is unavailable") — pre-existing and unrelated to this
change; same skip persists after every increment below.

```
$ head -c 512 /home/asa/devel/libresolid-studio/solid-node-viewer/WTs/viewer-navigator/solid_node_viewer/widget/dist/solid-widget.js
/*!
 * solid-widget.js - the browser viewer for solid-node models
 * solid-node-viewer 0.2.0 - viewer API 11
 * Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
 * SPDX-License-Identifier: AGPL-3.0-only
 * Source: https://github.com/LibreSolid/solid-node-viewer
 *
 * Bundles three.js - Copyright 2010-2023 three.js authors
 *   MIT License - https://github.com/mrdoob/three.js/blob/dev/LICENSE
 * Bundles jokenizer - Copyright (c) 2018 Umut Özel
 *   MIT License - https://github.com/umutozel/jokenizer/bl
```
Size: 676009 bytes.

```
$ /home/asa/devel/libresolid-studio/.venv/bin/solid-node-viewer describe
{"path": "/home/asa/devel/libresolid-studio/solid-node-viewer/solid_node_viewer/widget/dist/solid-widget.js", "index": "/home/asa/devel/libresolid-studio/solid-node-viewer/solid_node_viewer/widget/index.html", "apiVersion": 8, "documentVersions": [1, 2, 3, 4, 5], "version": "0.1.0"}
```
The installed package (editable from the PRIMARY checkout) is API 8 — no
`mountNavigator` — confirming discovery alone would skip the real-bundle test
until `SHOP_E2E_VIEWER_BUNDLE` is exported (design D4).

## 1. The gate rises to the navigator API

### 1.1 Red

Command:
```
/home/asa/devel/libresolid-studio/.venv/bin/python -m pytest tests/test_project_open.py tests/test_project_preparation.py -q
```
Four failures, against unchanged production code (`REQUIRED_VIEWER_API` still
4, `solid-node-widget.d.ts` still API 4 with no `mountNavigator`):

```
FAILED tests/test_project_open.py::ProjectOpenTest::test_opening_several_projects_asks_the_framework_for_its_viewer_once
  AssertionError: 4 != 10   (alpha.prepared.viewer_api_version)

FAILED tests/test_project_preparation.py::ProjectPreparationTest::test_missing_project_is_scaffolded_committed_built_and_validated
  AssertionError: 4 != 10   (prepared.viewer_api_version)

SUBFAILED(environment={'FAKE_SOLID_VIEWER_API': '3'}) tests/test_project_preparation.py::ProjectPreparationTest::test_rejects_a_missing_or_incompatible_viewer_before_building
  AssertionError: 'viewer API 10 is required but installed viewer API is 3' not found in
  'project preparation failed during viewer: viewer API 4 is required but installed viewer API is 3'

FAILED tests/test_project_preparation.py::ProjectPreparationTest::test_required_viewer_api_matches_the_declared_widget_interface
  AssertionError: 'mountNavigator' not found in '...SOLID_NODE_VIEWER_API_VERSION: 4;...'

4 failed, 52 passed, 1 skipped, 1 warning, 26 subtests passed in 11.70s
```
Every failure is on the API number or the missing declaration, not an import
or a fixture error.

### 1.2 Green

Same command:
```
55 passed, 1 skipped, 1 warning, 27 subtests passed in 12.05s
```
Plus `npm --prefix floor/frontend run test` (`tsc -b --pretty false`): exit 0,
no output — the un-touched `AssemblyPanel`/`FunctionalModel` code in
`main.tsx` still type-checks against the re-vendored declaration (it uses
`ViewerHandle`, `AssemblyNode`, `AssemblyPath`, `ViewerView`, all still
declared).

### 1.3 What was vendored

Vendored from `solid-node-viewer` package version `0.2.0`, viewer API `11`
(`package.json`'s `solidNodeViewerApi`), viewer worktree commit
`644b504ca3431b8450ed98408d5e151cf7437ef5` ("openspec: archive
ship-the-inspector-layout; accept ADR-051 and ADR-052"), copied from
`widget/src/viewer.ts` (`ViewerHandle`), `widget/src/assembly.ts`
(`AssemblyNavigationState`, `AssemblyChange`, `AssemblyListener`),
`widget/src/tree.ts` (`AssemblyNode`, `AssemblyPath`) and
`widget/src/navigator.ts` (`NavigatorOptions`, `NavigatorHandle`). The
declared `SOLID_NODE_VIEWER_API_VERSION` is `10` — the capability version the
studio requires, not the `11` the vendored bundle happens to be built at.

`ViewerHandle` members deliberately left out: `setTime`, `speed`,
`setSpeed`, `drivers`, `driver`, `setDriver`, `onDriverChange`,
`instructions`, `trigger`, `run` — the driving, playback and run surfaces
the studio does not use.

## 2. The Model panel mounts the viewer's navigator

### 2.1 Red

The fake widget's `mountNavigator` (design D5) was added to
`tests/fixtures/fake_solid.py` first, so the red failure below is on `main.tsx`
not calling it, never on the fixture. To get a clean red, `main.tsx` was
temporarily reverted to its post-increment-1 content (`git show
HEAD:floor/frontend/src/main.tsx`), rebuilt, and the test run against that:

Command:
```
/home/asa/devel/libresolid-studio/.venv/bin/python -m pytest tests/test_shop_lifecycle_e2e.py -k mounts_and_disposes -q
```
Failure:
```
    def test_model_panel_mounts_and_disposes_the_viewer_navigator(self) -> None:
        ...
        history = self.page.evaluate("() => window.__solidNodeWidgetHistory")
>       self.assertEqual(len(history["navigators"]), 1)
E       KeyError: 'navigators'

tests/test_shop_lifecycle_e2e.py:570: KeyError
1 failed, 21 deselected in 2.38s
```
`navigators` is undefined because the still-rendered `AssemblyPanel` never
calls `mountNavigator`. `main.tsx` was then restored to the increment-2
implementation (`AssemblyNavigator` wrapper + render swap + `loadViewer`
check) before the green run below.

### 2.2 Green

Same command, after the fix in §2.3 below:
```
1 passed, 21 deselected in 2.93s
```
Plus `npm --prefix floor/frontend run test` (tsc, exit 0) and `npm --prefix
floor/frontend run build` (exit 0). The whole-file run, after 2.5 deletes the
two superseded tests, is recorded at the end of §2 below.

### 2.3 Coverage hand-off

A real bug turned up while making 2.2 green: the fake widget's `mount()` and
`mountNavigator()` both lazily initialise `window.__solidNodeWidgetHistory`
with `??=`, so whichever runs first "wins" the shape. `mount()`'s initializer
did not include a `navigators` key, and since it always runs first (the
functional model mounts before the navigator), `mountNavigator`'s own
`??=` never fired and `history.navigators.push(record)` threw
`Cannot read properties of undefined (reading 'push')` — a page error that
silently prevented anything from being appended to the DOM, which surfaced in
the test as a `wait_for` timeout, not as the thrown error itself. Fixed by
adding `navigators:[]` to `mount()`'s own initializer too, so both agree on
the shape regardless of which runs first. A second, smaller issue: the fake's
navigator tree is deliberately empty (design D5, no rows), so it has zero
height and Playwright's default `wait_for()` (which requires "visible", i.e.
a non-zero box) times out even though the element is correctly attached; the
test waits for `state="attached"` instead, which is what an empty structural
host actually promises.

Scenario map, `test_model_panel_navigates_the_viewer_assembly`
(`git show HEAD~1:tests/test_shop_lifecycle_e2e.py` lines ~561-668 before this
increment) → what carries it now:

| Scenario | Carried by |
| --- | --- |
| `MODEL` heading + tree named `Assembly` present | §2.2 `test_model_panel_mounts_and_disposes_the_viewer_navigator` |
| Root row `focused-root`/root label, `rgb(28, 33, 40)` background | §3.2 (root row `solid-nav-row--root`, `aria-selected`, computed background) |
| No "Show full assembly" while at the root | §3.2 ("`Show full assembly` appears in the navigator's toolbar only while a subtree is focused") |
| `aria-expanded` on collapsed/expanded rows, `Expand housing` reveals `Visibility for pin` | §3.2 ("`Expand housing` reveals `Visibility for pin`") |
| Checked/unchecked visibility chip colours (`rgb(204, 68, 68)`, `rgb(107, 114, 128)`) | §3.2 (coloured/colourless/hidden chip assertions) |
| Switching Code → Model leaves one mount, no remount | §2.2 (area-switch assertion, `navigators.length === 1`, `mounts === 1`) |
| `.assembly-row.selected` never present | **Dropped.** This asserted the absence of a class the studio's own code never applied even before this change (grep of the pre-change `main.tsx`/`styles.css` shows no `.assembly-row.selected` producer) — a vacuous assertion, not a behaviour. Nothing to carry. |
| Focus-button opacity 0 by default, 1 on row hover | **Moved, not carried.** This is the navigator's own hover-affordance CSS (`.solid-nav-focus` opacity rule in `navigator.ts`'s injected stylesheet), unchanged by the studio and not part of the studio's override surface (design D2 only overrides `--solid-nav-muted`/`--solid-nav-focus-ring` and the two named classes' colour, not opacity). It is the viewer package's own behaviour to test, per its own `viewer-assembly-navigation` capability. |
| Clicking a row's name sets active without moving `focused-root`; clicking `Focus <name>` moves it, updates `aria-selected` | **Moved, not carried** for the same reason — pointer-driven focus-setting is the navigator's own click handling. §3.2 proves the underlying capability (a subtree can become root, and the panel reflects it) via the keyboard path instead, which is the studio's own accessibility contract, not a re-specification of every input method. |
| `Show full assembly` restores the root | §3.2 ("`Show full assembly` ... restores the root") |
| Keyboard `ArrowDown`/`ArrowRight`/`Space` toggles visibility and updates the chip colour | §3.2 ("the keyboard contract moves and acts (Down, Right, Enter, Space)") |
| Desktop layout: both the tree and the viewer have a bounding box | **Dropped**, no direct successor. This asserted simultaneous layout of two panels already covered structurally by every other test that opens a project and checks both `MODEL` and the model viewport render (e.g. §2.2 itself, `test_workspace_mounts_the_project_scoped_viewer`); no navigator-specific claim was in it. |
| Responsive viewport (760×900) causes no horizontal overflow | **Dropped**, no direct successor for this specific test, but the same assertion (`document.documentElement.scrollWidth > window.innerWidth`) still runs in two other standing tests (`tests/test_shop_lifecycle_e2e.py:285`, `:551`), so the studio's responsive-layout guarantee remains proven; only the assembly-panel-specific instance of it is gone. |
| A republished document (root's `pin` child removed) leaves the panel usable, no stale `Show full assembly` | §3.2 ("a republished document with a node removed leaves the panel usable and the removed row gone") |

Scenario map, `test_model_panel_controls_the_supplied_framework_viewer`
(lines ~670-704 before this increment):

| Scenario | Carried by |
| --- | --- |
| Tree named `Assembly`; `Expand housing` reveals `Visibility for pin` | §3.2 |
| Checkbox toggles checked → unchecked | §3.2 (chip-colour assertions after the keyboard toggle prove the same underlying capability; the pointer-click path is the navigator's own input handling, moved per the row above) |
| `Focus pin` moves the focused root | §3.2, via the keyboard path (Enter) |
| `Show full assembly` restores the root | §3.2 |

Nothing above is silently dropped: every scenario is either carried forward by
name, or named as dropped/moved with the reason.

### 2.6 Green run (end of increment 2)

```
$ npm --prefix floor/frontend run test    # exit 0, no output
$ npm --prefix floor/frontend run build   # ✓ built in 7.36s
$ /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest tests/test_shop_lifecycle_e2e.py -q
20 passed, 5 subtests passed in 44.32s
```
(20 tests, down from the pre-change file's 22, matching the 2 deletions in
2.5 and the 1 addition in 2.2.)

### Deviation: `loadViewer`'s API check cannot import the declared constant

Design D3's pseudocode has the browser check compare against
`SOLID_NODE_VIEWER_API_VERSION` as if it were an importable runtime value.
`floor/frontend/src/solid-node-widget.d.ts` is a pure ambient declaration
file with no backing `.ts`/`.js` module, so `import {
SOLID_NODE_VIEWER_API_VERSION } from "./solid-node-widget"` type-checks
(tsc is satisfied by the ambient declaration) but fails at build time:
`vite build` cannot resolve the module (confirmed:
`Could not resolve "./solid-node-widget" from "src/main.tsx"`). `main.tsx`
instead declares a local `REQUIRED_VIEWER_API = 10` with a comment
explaining the mirror, used by a new `verifyLoadedViewer()` helper that
`loadViewer` calls after the widget script is confirmed present (both on
the already-loaded fast path and after `load`/existing-script events),
throwing so the rejection lands on the existing `viewerReady === false`
state exactly as D3 describes. This is a mechanical necessity, not a design
change: the comparison, the trigger points, and the outcome are exactly what
D3 specifies; only the literal's storage differs from the pseudocode.

## 3. The look, proved against the real bundle

### 3.1 Red

Added the bundle-discovery helper `_discover_real_viewer_bundle` (design D4)
and refactored `setUp`'s subprocess launch into a `_launch(extra_env)` helper
so the new test can stop the default process and relaunch with
`FAKE_SOLID_BUNDLE`/`FAKE_SOLID_VIEWER_API` set (the floor process's own
`resolve_viewer_bundle` call inherits its OWN environment, since it passes no
`extra_env` of its own — confirmed by reading `floor/sessions.py:531` and
`floor/preparation.py:1014-1027`).

Command:
```
SHOP_E2E_VIEWER_BUNDLE=/home/asa/devel/libresolid-studio/solid-node-viewer/WTs/viewer-navigator/solid_node_viewer/widget/dist/solid-widget.js \
  /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest \
  tests/test_shop_lifecycle_e2e.py -k presents_the_viewer_navigator -q
```
Failure — the real bundle loaded, the tree rendered, the root row and the
whole tree/class structure were already correct (proving discovery, the
fixture document, and the keyboard/click flow all work against the real
navigator), but the colours are the navigator's own neutral defaults, not the
studio's:
```
>       self.assertEqual(engine_row.evaluate("element => getComputedStyle(element).backgroundColor"), "rgb(28, 33, 40)")
E       AssertionError: 'rgba(128, 128, 128, 0.22)' != 'rgb(28, 33, 40)'
1 failed, 20 deselected, 1 warning in 8.67s
```
This is NOT a skip — the real bundle ran, and the failure is exactly the one
design D4 predicts (the neutral default, `--solid-nav-root-bg:
rgba(128,128,128,0.22)`, before the studio's override exists).

### 3.2 Green

`floor/frontend/src/styles.css` got the `--solid-nav-*` override block and the
two class rules of design D2, plus `.assembly-navigator-host { margin-top:
10px; }`, scoped to `.assembly-panel`; the old `.assembly-*` rules stay in
place (increment 4 removes them). After `npm --prefix floor/frontend run
build`:
```
SHOP_E2E_VIEWER_BUNDLE=/home/asa/devel/libresolid-studio/solid-node-viewer/WTs/viewer-navigator/solid_node_viewer/widget/dist/solid-widget.js \
  /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest \
  tests/test_shop_lifecycle_e2e.py -k presents_the_viewer_navigator -q
1 passed, 20 deselected, 1 warning in 9.40s
```
The SAME command WITHOUT the env var:
```
/home/asa/devel/libresolid-studio/.venv/bin/python -m pytest tests/test_shop_lifecycle_e2e.py -k presents_the_viewer_navigator -q -rs
SKIPPED [1] tests/test_shop_lifecycle_e2e.py:636: no viewer bundle at API 10
or newer is available: export SHOP_E2E_VIEWER_BUNDLE to name one, or install
a newer solid-node-viewer (installed viewer API: 8)
1 skipped, 20 deselected, 1 warning in 2.08s
```
The skip names the env var and the version discovery actually found (the
installed, editable-from-primary-checkout package, still API 8), exactly as
design D4 requires.

### 3.3 Pixels

Four screenshots of `.assembly-panel`, 1440×900 viewport, same fixture
document (`engine → [housing(#cc4444) → [pin], unpainted]`), housing expanded:

- `before.png` / `after.png` — unfocused (document root), planning head vs.
  this change's real-bundle navigator.
- `before-focused.png` / `after-focused.png` — `housing` set as the focused
  root (via its row's `Focus`/hover button).

"Before" was captured by temporarily checking out
`floor/frontend/src/main.tsx` and `styles.css` at the planning commit
(`042cc95214d676a14a328dbde113bbb00634cb17`), rebuilding, and screenshotting
against the e2e fake's default (non-navigator) `mount()`; the files were then
restored from a backup and rebuilt again before continuing (confirmed via
`git status`/`git diff` showing no unintended change to `main.tsx` afterward).
"After" used this increment's code against the same real bundle
(`SHOP_E2E_VIEWER_BUNDLE`'s file) via `FAKE_SOLID_BUNDLE`.

Unfocused (`before.png` vs `after.png`): visually identical — same root row
background, same red chips on `housing`/`pin`, same neutral grey chip on
`unpainted`, same row height/indent/font. No `Show full assembly` visible in
either (root is the document root already).

Focused (`before-focused.png` vs `after-focused.png`): the ONE visible
difference is exactly what design D2 predicts — `before-focused.png` shows
`Show full assembly` as a text button at the top-right of the panel, on the
same line as the `MODEL` heading; `after-focused.png` shows it right-aligned
on its own row, in the navigator's own toolbar, directly above the tree. The
twisty column's 1px width difference (13px → 12px) is not visually
distinguishable at this resolution but is confirmed in the CSS (design D2).
Nothing else differs: row colours, indentation, chip colours, and the
`ROOT`/`Focus` labels are pixel-identical between the two.

Files (not committed — pixel evidence, described here per AGENTS.md's "pixels
are evidence" without adding binary artifacts to the change), in this
session's scratchpad directory under `pixels/`:
`before.png`, `after.png`, `before-focused.png`, `after-focused.png`.

## 4. The deletion

Deleted from `floor/frontend/src/main.tsx`: `AssemblyPanel`, `assemblyRows`,
`allAssemblyPaths`, `pathKey`, the `AssemblyRow` type, the workspace's
`assembly` state, `onAssemblyChange` (the parameter on `FunctionalModel` and
its three call sites), and the four now-unused imports (`CSSProperties`,
`KeyboardEvent` from `react`; `AssemblyNode`, `AssemblyPath` from
`./solid-node-widget`). `ViewerHandle`/`ViewerView` stay imported;
`AssemblyNode`/`AssemblyPath` stay declared inside the `.d.ts` itself (needed
by `ViewerHandle`'s own methods). `npm --prefix floor/frontend run test`
(tsc) is clean after the deletion — nothing else in `main.tsx` referenced any
of it.

Deleted from `floor/frontend/src/styles.css`: `.assembly-panel > header`
(both rules), `.assembly-tree`, `.assembly-row` (all three rules),
`.assembly-disclosure`, `.assembly-spacer`, `.assembly-visibility` (both
rules), `.assembly-name`, `.assembly-root-label`, `.assembly-focus` (both
rules). Kept: `.assembly-panel h2, .agent-panel h2 …` (shared heading
rules), `.assembly-panel` (the panel shell), `.assembly-navigator-host`, the
increment-3 `--solid-nav-*` override block, `.solid-nav-badge`/
`.solid-nav-focus`, and `.empty`.

Grep proving nothing still names the removed DOM:
```
$ grep -rn "assembly-row\|assembly-tree\|focused-root\|assembly-visibility\|assembly-disclosure\|onAssemblyChange" floor tests docs --exclude-dir=static --exclude-dir=node_modules
```
Three kinds of hit remain, all expected:
- `floor/frontend/src/solid-node-widget.d.ts:63` —
  `onAssemblyChange(listener: AssemblyListener): () => void;`. This is the
  VIEWER's own `ViewerHandle` method name (vendored in increment 1), not the
  studio's deleted prop of the same name — a different thing that happens to
  share a name.
- `docs/adrs/0030-the-model-panel-is-the-viewers-navigator.md` — its own
  prose, describing the viewer's `onAssemblyChange(listener)` API and stating
  that the studio's plumbing of the same name "are deleted". Design
  reference/record prose, exactly what task 4.3 anticipates.
- `docs/design/build/floor/frontend/src/{main.tsx,styles.css}` — the
  reference-design prototype's OWN, separate copy of an older version of
  these files (under `docs/design/`, not the application source; unchanged
  by this decision per the ADR's References section and AGENTS.md's
  "Architecture documentation"). Out of scope for this change.
(Without the `--exclude-dir` flags, the same grep also matches unrelated
strings inside the built, untracked `floor/static/` bundle — vendor code, not
source — which is why those directories are excluded.)

### Green run

```
$ npm --prefix floor/frontend run test    # tsc -b --pretty false: exit 0, no output
$ npm --prefix floor/frontend run build   # ✓ built in 7.09s
```
```
SHOP_E2E_VIEWER_BUNDLE=/home/asa/devel/libresolid-studio/solid-node-viewer/WTs/viewer-navigator/solid_node_viewer/widget/dist/solid-widget.js \
  /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest \
  tests/test_shop_lifecycle_e2e.py -k presents_the_viewer_navigator -q
1 passed, 20 deselected, 1 warning in 9.59s
```
Full Python suite (`/home/asa/devel/libresolid-studio/.venv/bin/python -m
pytest tests -q`, no `SHOP_E2E_VIEWER_BUNDLE` set — an ordinary run),
compared against §0's baseline of `1 failed, 339 passed, 1 skipped, 160
subtests passed`:
```
1 failed, 338 passed, 2 skipped, 2 warnings, 160 subtests passed in 145.52s
FAILED tests/test_license_headers.py::LicenseHeaderTest::test_every_tracked_source_file_has_agpl_header
  (same pre-existing, unrelated failure as §0's baseline)
```
Every difference from the baseline is explained: 2 tests were deleted
(`test_model_panel_navigates_the_viewer_assembly`,
`test_model_panel_controls_the_supplied_framework_viewer`) and 2 were added
(`test_model_panel_mounts_and_disposes_the_viewer_navigator`, which passes
under this run's fake widget, and `test_model_panel_presents_the_viewer_navigator`,
which SKIPS under this run because `SHOP_E2E_VIEWER_BUNDLE` is not exported
and the installed viewer is still API 8 — design D4's intended behaviour for
an ordinary run). Net: passed count is baseline − 1 (338, since one of the
two new tests skips instead of passing in an ordinary run) and skipped is
baseline + 1 (2, the pre-existing skip plus this one) — exactly accounted
for, with the real-bundle-present run in §3.2/§3.4 above showing that same
test passing when the bundle is supplied.

## 5. Findings

### ADR re-read (5.1/5.2)

Re-read `docs/adrs/0030-the-model-panel-is-the-viewers-navigator.md` against
what was actually built. Every claim in its Decision and Consequences
sections matches the implementation exactly: the wrapper component and
disposal behaviour (D1), the theming seam limited to `--solid-nav-*` and the
two named classes (D2), the inspector layout not used, `Show full assembly`
deleted from the studio and left to the navigator's own toolbar, the gate at
10 plus the browser-side check (D3), the real-bundle test strategy and the
fake's minimal `mountNavigator` (D4/D5), and the two accepted pixel
differences (toolbar placement, twisty width) confirmed by the §3.3
screenshots. **No statement in the ADR was contradicted by the
implementation** — nothing to correct, so its Status stays `Proposed`
untouched, and its text is unmodified.

`docs/adrs/README.md`'s row for `0030` was already present at `Proposed` /
2026-09-14 from the planning commit; no edit needed.

### Deviations from the design's exact wording

1. **`loadViewer`'s API check (design D3).** The design's pseudocode compares
   against `SOLID_NODE_VIEWER_API_VERSION` as an imported value.
   `solid-node-widget.d.ts` is a pure ambient declaration file with no
   backing runtime module (confirmed: importing a value from it type-checks
   under `tsc` but fails `vite build` with "Could not resolve
   ./solid-node-widget"). `main.tsx` instead declares a local
   `REQUIRED_VIEWER_API = 10` with a comment explaining the mirror. The
   comparison, the trigger points (already-loaded / script `load` / existing
   script's `load` event), and the outcome (`viewerReady === false`) are
   exactly as D3 specifies; only where the literal `10` lives differs.
2. **`setUp` refactored into `_launch(extra_env)`** (not named by the design,
   which only says "the test passes the bundle to the shop subprocess"). The
   existing `setUp` launched one fixed-environment subprocess per test with
   no seam for a test-specific environment; `_launch` extracts that Popen
   call so `test_model_panel_presents_the_viewer_navigator` can stop the
   default process and relaunch with `FAKE_SOLID_BUNDLE`/
   `FAKE_SOLID_VIEWER_API`, which the floor process's own `resolve_viewer_bundle`
   call inherits (it passes no `extra_env` of its own). Mechanical, not a
   design change.

### A real bug the fixture work turned up (recorded fully in §2.3)

`fake_solid.py`'s `mount()` and the new `mountNavigator()` both lazily
initialise `window.__solidNodeWidgetHistory` with `??=`; `mount()`'s
initializer lacked a `navigators` key and always runs first, so
`mountNavigator`'s own initializer never fired and the first navigator mount
threw `Cannot read properties of undefined (reading 'push')` — surfacing only
as a `wait_for` timeout in the test, not as the underlying error, until
debugged with a standalone Playwright script capturing `pageerror` events.
Fixed by giving both initializers the same shape.

### What the reviewer should look at first

- The scenario-coverage table in §2.3, particularly the two rows marked
  "Dropped" (a vacuous `.assembly-row.selected` assertion, and the
  desktop-bounding-box/responsive-viewport checks specific to the assembly
  panel) and the rows marked "Moved, not carried" (pointer-driven focus/hover
  behaviour, now the viewer's own capability to test).
- The two deviations above (§5, "Deviations from the design's exact
  wording") — both are mechanical necessities forced by the `.d.ts`-only
  module and the single-process-per-test harness, not substitutions of a
  different design.
- `docs/architecture-overview.md`'s rewritten passage (~459-464) — check it
  against the promoted ADR's Decision section when promoting.
