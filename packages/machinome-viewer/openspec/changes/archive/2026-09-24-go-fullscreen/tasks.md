## 0. Before apply

- [x] 0.1 Settled 2026-09-24 (delegated review, repository precedent 27499a5): fold into the 0.7.0 record; the local tag is left for the pilot. The pilot settles design D11: fold into the 0.7.0 record (the
      default, and the tag move is the pilot's), or add an `Unreleased`
      section and amend `user-documentation` and `tests/test_documentation.py`.
- [x] 0.2 Check desktop Safari's unprefixed Fullscreen API support against
      MDN browser-compat-data (design D5). Record the answer in
      `evidence.md`, and add `webkit` fallbacks only if a current desktop
      Safari needs them.

## 1. Prove the failure

- [x] 1.1 `src/fullscreen.test.ts`: the pure decisions, red against a
      missing module:
      - `togglesFullscreen`: `f` and `F` toggle; Ctrl, Alt or Meta, repeat,
        `defaultPrevented`, and `input`, `textarea`, `select` or
        contenteditable targets do not; a target inside the root toggles; a
        body or html target toggles only for the sole viewer;
      - `fullscreenPlacement`: run transport, else inline animation bar,
        else corner;
      - `fullscreenAvailable`: `fullscreenEnabled` and continuous render
        mode;
      - `fullscreenBackground`: first opaque colour, else white.
- [x] 1.2 `src/fullscreen.test.ts` (jsdom, stubbed `requestFullscreen` and
      `exitFullscreen`), covering the controller:
      - no button and no key listener when unavailable;
      - label and title swap on `fullscreenchange`;
      - `f` on body requests the root, and `f` again exits;
      - Escape is never prevented;
      - with two controllers in one document a body `f` does nothing;
      - dispose exits when the root is full screen.
- [x] 1.3 `src/inspector.test.ts`: `mountInspectorWith` registers its
      viewer pane with the layout root as the full-screen root before
      calling `mount`.
- [x] 1.4 `tests/support.py`: export-shaped staging for the touched
      (running) and calculator (clocked) fixtures beside the existing
      spinner and marked helpers. `tests/test_widget_e2e.py`, a new
      `FullscreenE2ETest`:
      - the button is last in `.animation-controls` (spinner), last in
        `.run-transport` (touched), and in the corner outside any bar
        (marked, calculator), exactly one per page;
      - clicking the canvas then pressing `f` makes
        `document.fullscreenElement` the `.machinome-inspector` root, the
        canvas matches the viewport and the label reads "Exit full screen";
      - in full screen the sidebar toggle is on screen and opening the
        sidebar narrows the canvas;
      - a plain `mount()` harness page makes its host element the
        full-screen element;
      - pressing Escape: record whether headless Chromium exits (design,
        Risks). If it does, assert the exit; if not, assert the key is not
        prevented and that `document.exitFullscreen()` restores the
        canvas size and label;
      - `f` in a clocked value field and Ctrl+F do not enter;
      - a harness page iframing the export without `allowfullscreen` shows
        no button and ignores `f`, and one with it shows the button.
- [x] 1.5 `tests/test_capture.py`: the staged capture mount page shows no
      visible `.machinome-fullscreen`, and a capture of the marked fixture
      (no timeline, so a corner button) has a transparent bottom-right
      corner. This goes red only once the button exists, so run it red
      after 2.3 and before 2.5.
- [x] 1.6 Run 1.1 to 1.4 and see them fail for the stated reasons.

## 2. Implement

- [x] 2.1 `src/fullscreen.ts`: the pure decisions, the root registry
      (`WeakMap`, module-private apart from the register and resolve
      functions the inspector and viewer import), the per-document
      controller set, and the controller (button with SVG glyphs, `place`,
      key listener, `fullscreenchange`, background, dispose).
- [x] 2.2 `src/inspector.ts`: register `viewerPane -> root` before
      `mountFn`.
- [x] 2.3 `src/viewer.ts`: create the controller after the container is
      resolved; call `place(...)` after `refreshControls`,
      `rebuildRunChrome` and `rebuildClockedChrome` with the bars just
      built; dispose it first in `dispose()`.
- [x] 2.4 Run 1.1 to 1.4 green. Run 1.5 red.
- [x] 2.5 `machinome_viewer/capture.py`: the hiding rule on the mount page.
      Run 1.5 green.
- [x] 2.6 `npm run build` in `machinome_viewer/widget` (never `npm ci` or
      `npm install`, and not `scripts/check-dist`). Open the spinner and
      marked exports headed at 1440×900, enter and leave full screen by
      button, `f` and Esc, and keep screenshots in `evidence.md`.

## 3. Document

- [x] 3.1 `docs/using-the-viewer.rst`: the full-screen button (bar or
      corner), `f`, Esc, and that the button is absent where the browser or
      the embedding page does not permit full screen. Folded into the page's
      existing sections, not a section named after the change.
- [x] 3.2 `docs/embedding.rst`: add `allowfullscreen` to the iframe
      example and state that without it (or `allow="fullscreen"`) the button
      is hidden.
- [x] 3.3 `docs/reference/layouts.rst`: the stable class
      `machinome-fullscreen`, and that a host may hide it with CSS.
- [x] 3.4 `CHANGELOG.md`: per D11 as settled in 0.1. By default a bullet
      under 0.7.0 "What a maker gets", with no API or version number
      changed.
- [x] 3.5 `tests/test_documentation.py`: pin that the manual names the
      `f` key and `allowfullscreen`, and that the changelog records full
      screen in the section D11 chose.

## 4. Validate

- [x] 4.1 `npx tsc --noEmit` and `npx vitest run` in
      `machinome_viewer/widget`.
- [x] 4.2 `pytest` from the worktree root (never two suites at once), and
      report the browser tests it skips, if any.
- [x] 4.3 Build the manual (`make -C docs html`) warning-free.
- [x] 4.4 `openspec validate go-fullscreen --strict`.

## 5. Record

- [x] 5.1 `evidence.md`: the red and green runs, the Esc finding, the
      Safari finding and the screenshots.
- [x] 5.2 Sync the delta specs, archive the change, and commit the
      completed implementation record. Nothing is pushed, tagged or
      uploaded.
