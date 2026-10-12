# Evidence: go-fullscreen

## 0.2 Desktop Safari's unprefixed Fullscreen API support

Checked against MDN's compatibility data (via `caniuse.com/fullscreen`,
which republishes `mdn/browser-compat-data`) and corroborated by a web
search of WebKit's own release notes, 2026-09-24:

- **Safari on macOS (desktop):** the unprefixed `Element.requestFullscreen()`
  and `Document.fullscreenEnabled` shipped in **Safari 16.4** (March 2023).
  The compatibility table shows unprefixed support continuous from 16.4
  through the current 26.x line (checked to 27.1 and later) -- there is no
  later regression or re-prefixing.
- **Safari on iPadOS:** shares macOS Safari's WebKit engine and version
  numbering (has presented as desktop Safari's UA since iPadOS 13), so it
  carries the same unprefixed support from 16.4. `caniuse` does not break
  iPadOS out as its own column; this is the design's own stated inference,
  not separately measured here.
- **Safari on iOS (iPhone):** shown as "partial support" from version 12
  through the current line -- the video-only fullscreen the design already
  accounts for ("iPhone Safari has no element full screen, only video").
  `document.fullscreenEnabled` is `false` there, so `fullscreenAvailable`
  already answers correctly: no button, `f` does nothing, no CSS imitation.

**Conclusion:** current desktop Safari does not need a `webkit`-prefixed
fallback. None was added, per design D5's own instruction ("add `webkit`
fallbacks only if a current desktop Safari still needs them"). This is a
compatibility-data check, not a live test on a Safari device.

## 1. Red runs

### 1.1 / 1.2 `src/fullscreen.test.ts` against a missing module

With `fullscreen.ts` moved aside, `npx vitest run src/fullscreen.test.ts`:

```
FAIL  src/fullscreen.test.ts [ src/fullscreen.test.ts ]
Error: Failed to resolve import "./fullscreen" from "src/fullscreen.test.ts".
Does the file exist?
Test Files  1 failed (1)
     Tests  no tests
```

Every one of the 30 cases in the file failed for the same reason: the
module the test imports does not exist yet.

### 1.3 `src/inspector.test.ts` registration test, against `inspector.ts`
before the registration call was added

With only the new test added and `inspector.ts` reverted to its
pre-change state (`git stash` on that one file), `npx vitest run
src/inspector.test.ts`:

```
FAIL  src/inspector.test.ts > mounting > registers the viewer pane with
      the layout root as the full-screen root before mounting the viewer
      (OpenSpec go-fullscreen, design D1)
AssertionError: expected null to be <div class="machinome-inspector">…
Test Files  1 failed (1)
     Tests  1 failed | 21 passed (22)
```

Exactly the one new test failed, for the stated reason: nothing had
registered the viewer pane yet.

### 1.5 `tests/test_capture.py::FullscreenCaptureTest`, run red after 2.3
and before 2.5 (button exists, capture's mount page not yet hiding it)

With the widget bundle rebuilt (button now exists) but `capture.py`'s
hiding rule reverted:

```
FAILED tests/test_capture.py::FullscreenCaptureTest::test_the_mount_page_shows_no_visible_fullscreen_control
AssertionError: 1 != 0
FAILED tests/test_capture.py::FullscreenCaptureTest::test_the_photograph_has_a_transparent_bottom_right_corner
AssertionError: Items in the first set but not the second: 160, 33, 166, …
2 failed, 24 deselected, 1 warning in 2.65s
```

The button was visible on the capture mount page (not hidden), and its
opaque pixels showed up in the photographed corner -- both for the
stated reason.

### 1.4/1.6 `tests/test_widget_e2e.py::FullscreenE2ETest`

Written and run only after the implementation existed (task order: 1.4's
own text places this suite's write together with `support.py`'s new
staging helpers, and it needs the button to assert placement against).
Confirmed green on first implementation pass; see the Green runs section.

## 2. Green runs

### 2.4 `npx vitest run` (widget), full suite

```
Test Files  60 passed | 1 skipped (61)
     Tests  1614 passed | 2 skipped (1616)
```

`src/fullscreen.test.ts`: 30/30. `src/inspector.test.ts`: 22/22 (the new
registration test included). No other file regressed.

### 2.5 `tests/test_capture.py`, full file

```
26 passed, 8 warnings in 8.53s
```

Including both `FullscreenCaptureTest` cases, now green with the hiding
rule in place.

### `tests/test_widget_e2e.py::FullscreenE2ETest`, full class (12 tests)

```
12 passed, 33 deselected in 16.69s
```

- placement: last on `.animation-controls` (spinner), last on
  `.run-transport` (touched), corner outside any bar (marked, calculator)
  -- each exactly one button;
- `f` on the spinner export enters full screen on `.machinome-inspector`,
  the root and the canvas height match the viewport, and the label reads
  "Exit full screen";
- exiting (Escape, falling back to `document.exitFullscreen()` -- see
  below) restores the canvas size and the "Full screen" label;
- the sidebar toggle is reachable and narrows the canvas in full screen;
- a plain `mount()` into a host SMALLER than the viewport (200x150 of
  800x600) grows to fill it in full screen -- the direct proof that
  entering full screen changes anything, since the standalone export page
  already fills its viewport before `f` is ever pressed;
- `f` in a clocked value field, and Ctrl+F, do not enter full screen;
- a genuinely CROSS-ORIGIN iframe (a different loopback port; see the
  finding below) without `allowfullscreen` shows no button and ignores
  `f`; one with it shows the button.

## The Escape finding (design, Risks)

Measured directly (script driving the same spinner export as the suite):
pressing a synthetic `Escape` through Playwright's keyboard API does
**NOT** exit full screen natively in this headless Chromium
(`--headless --no-sandbox --disable-gpu --use-angle=swiftshader`). One
and a half seconds after the key, `document.fullscreenElement` is still
the root.

This is the fallback path the design names: the viewer never listens for
or prevents Escape (proved directly in `fullscreen.test.ts`'s "never
prevents Escape" case, and structurally true -- `fullscreen.ts` installs
no `keydown` handling for any key but `f`/`F`), and
`test_exiting_restores_the_canvas_size_and_the_label` falls through to
calling `document.exitFullscreen()` itself, which does work and does
restore the canvas size and the "Full screen" label. A real desktop
browser's own Escape handling was not re-tested here (no headed browser
or display is available in this environment); this headless finding is
what task 1.4/2.6 asked to be recorded.

## The cross-origin iframe finding

Measured directly before writing the iframe tests: a **same-origin**
iframe (same host and port) reports `document.fullscreenEnabled === true`
inside it whether or not it carries `allowfullscreen` at all -- the
Fullscreen API's default permissions-policy allowlist for the `fullscreen`
feature is `'self'`, so a same-origin embed already has the permission.
Only a genuinely **cross-origin** iframe (a different loopback port
counts) shows the attribute's effect:

```
cross-origin no-attr:   fullscreenEnabled = False
cross-origin with-attr: fullscreenEnabled = True
```

`FullscreenE2ETest` therefore serves its iframe harness pages from a
second `ThreadingHTTPServer` on its own port, embedding the spinner
export served from the first -- a real cross-origin embed, the case the
`viewer-package` spec's "An iframe that does not permit full screen"
scenario is actually about.

## 2.6 Screenshots (headless, no display available)

Taken with headless Chromium (`--no-sandbox --disable-gpu
--use-angle=swiftshader`) at 900x650, since this environment has no
display for a headed run. Saved under `evidence/`:

- `spinner-before.png` -- the spinner export's inline animation timeline,
  the full-screen button ("enter", four outward corner brackets) as the
  bar's last control, after the slider.
- `spinner-fullscreen.png` -- after clicking the canvas and pressing `f`:
  the same layout, the button now shows the "exit" glyph (four inward
  brackets).
- `marked-before.png` -- the drivers-only marked bench: the driver panel
  in the left rail (`Bench` / `angle`), no timeline, and the full-screen
  button as a permanent 36px square overlay in the bottom-right corner.
- `marked-fullscreen.png` -- after clicking the corner button: the same
  layout, corner button now showing the "exit" glyph, confirming the
  click path (not only the `f` key) enters and that the state read from
  `fullscreenchange` is correct.

Both exports show exactly one button, in the position design D2 states
for that export's own control surface, and the glyph swap confirms the
button's state always follows `document.fullscreenElement` rather than
which input entered full screen.

## Deviations from the design

None. `togglesFullscreen`, `fullscreenPlacement`, `fullscreenAvailable`
and `fullscreenBackground` are implemented and tested exactly as D2/D4-D6
state. No `webkit` fallback was added (0.2, above). The Escape and
cross-origin findings are the two empirical results the design and tasks
asked this cycle to establish, not deviations from it.

## A pre-existing, unrelated test failure noted during validation

Running the full `pytest` suite surfaced
`tests/test_widget_e2e.py::MarkedDocumentPixelsTest::test_the_decals_are_drawn_and_the_twin_shows_none`
failing with "4 != 0" (four unexplained near-white pixels on the
unmarked twin). Checked against the unmodified baseline (this change's
diff stashed out): the SAME failure reproduces identically, with the
full-screen button not present in the DOM at all. It is therefore a
pre-existing environmental flake (most likely a swiftshader/software-GL
antialiasing artifact at this bench's fixed camera), not a regression
this change introduced, and it is left for the pilot rather than
adjusted here. `MARKED_HARNESS`'s stylesheet was still given a
`.machinome-fullscreen { display: none }` rule as a matter of hygiene --
this bench's pixel assertions are about the model, and the corner
button now legitimately overlaps its clipped canvas shot -- but that
rule measurably does NOT change the four-pixel reading either way.

## `git status --short` after this cycle's implementation (before archive)

See the final report; nothing is committed, pushed, tagged or uploaded
by this cycle.
