## Why

machinome.org's Foundry pages embed every project's `machinome export` in an
iframe that already carries `allowFullscreen`, and the pilot wants to watch
those machines full screen there, the way a YouTube video is watched. The
viewer gives no way to do it. The export page offers no full-screen control
and no key, and a host page cannot put the iframe's content in full screen
for the reader. The requirement, from the pilot:

- every simulation on the site can be shown full screen;
- a model with a timeline carries a full-screen icon on that player bar;
- a model with no timeline carries the icon permanently in the bottom-right
  corner;
- while the simulation is shown, `f` goes full screen and Esc comes back;
- it works on every export.

Every export is the same `index.html` running the same bundle and mounting
the inspector layout, so one change in the widget covers all of them. The
change reaches the site on its next build, through exports made with the
new bundle.

## What Changes

- The viewer gains a full-screen control: a button with an inline SVG glyph
  that toggles between "enter" and "exit". It has an accessible name, a
  title that names the `f` key, and keyboard focus.
- Placement follows the control surface the viewer actually draws:
  - at the right end of the running machine's transport bar;
  - otherwise, at the right end of the inline animation timeline bar;
  - otherwise (static and drivers-only models, clocked machines whose
    transport lives in the side rail, and the toggled, external and hidden
    animation presentations), as a permanent overlay in the bottom-right
    corner of the viewer.
- The element that goes full screen is the widget's root, so the canvas,
  the machine chrome, the timeline and, in the inspector layout, the
  assembly rail and sidebar all come along. The canvas follows through the
  viewer's existing resize observer.
- `f` or `F` toggles full screen when the key is pressed inside the widget,
  or on a page with nothing focused that holds exactly one viewer. The key
  does nothing while the reader is typing in a field, when Ctrl, Alt or Meta
  is held, on auto-repeat, or when another handler has already consumed the
  key. Esc remains the browser's own exit and the viewer never intercepts
  it; the button follows `fullscreenchange`, whatever the exit path.
- Where the document cannot go full screen (`document.fullscreenEnabled` is
  false, as in an iframe without `allowfullscreen` or on iPhone Safari), the
  button is not shown and `f` does nothing. The viewer adds no imitation of
  full screen in CSS.
- While full screen, the root is painted with the page background it was
  seen on, so the model and the inspector's inherited text stay legible
  over the browser's black backdrop.
- A viewer in on-demand render mode (the still-capture mode, which already
  admits no interactive controls) draws no full-screen control. The
  `machinome-viewer capture` mount page hides the control's stable class, so
  no photograph contains it.
- The manual documents the button and the key (`using-the-viewer`), and
  states that an iframe needs `allowfullscreen` (or `allow="fullscreen"`)
  for the button to appear (`embedding`). The stable class is listed with
  the layout CSS hooks (`reference/layouts`).
- No new mount option, handle member, document field or query parameter.
  The viewer API stays 27, document versions 1 to 13, and the package
  version stays 0.7.0.
- The changelog records the capability in the 0.7.0 section, as the
  ratified `user-documentation` spec requires while 0.7.0 is not uploaded.
  This leaves the local `v0.7.0` tag behind the record. Moving the tag, or
  choosing an `Unreleased` section and amending that spec instead, is the
  pilot's decision (design D11).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: a maker can watch the model full screen from a control
  placed on the bar the model has, or in the corner, and with `f`. "Static
  models present no controls" becomes "no animation controls", because a
  static model now carries the full-screen control.
- `inspector-layout`: in the inspector layout, the whole layout goes full
  screen as one.
- `snapshot-capture`: a photograph never contains the full-screen control.
- `user-documentation`: the manual states full-screen viewing and the
  iframe permission it needs.

## Impact

- `machinome_viewer/widget/src/fullscreen.ts` (new) and
  `fullscreen.test.ts`: the pure decisions (does this key toggle, where does
  the button go, is full screen available, which background) and the small
  DOM controller.
- `machinome_viewer/widget/src/viewer.ts`: builds the controller per mount,
  places the button after each chrome rebuild, and disposes it.
- `machinome_viewer/widget/src/inspector.ts` and its test: registers the
  layout root as the viewer pane's full-screen root.
- `machinome_viewer/capture.py`: one stylesheet rule on its mount page.
- `tests/test_widget_e2e.py`, `tests/test_capture.py`, `tests/support.py`:
  browser acceptance.
- `docs/using-the-viewer.rst`, `docs/embedding.rst`,
  `docs/reference/layouts.rst`, `CHANGELOG.md`.
- Rebuilt `dist/machinome-viewer.js`.
- Nothing in the framework changes. The site already sets
  `allowFullscreen` and changes nothing. The site's own key handling on the
  parent page is out of scope: `f` reaches the viewer once the reader has
  interacted with the embedded model.
