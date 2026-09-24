## Context

The export page (`widget/index.html`) auto-mounts the **inspector** layout
into `#machinome-viewer`, which fills the document. `mountInspectorWith`
builds `.machinome-inspector` (rail, sidebar, viewer pane) inside the host
element and mounts the viewer into its own pane. The development page mounts
the same inspector through `mountDevelopment`. Custom embeds call `mount()`
or `mountInspector()`. `machinome-viewer capture` writes its own mount page
calling `mount()` with `animation: 'external'`, `driverControls: 'none'` and
`partControls: 'none'`, then clips a screenshot to the canvas.

The viewer draws its chrome inside its container (`position: relative`):

| Surface | Built by | Where |
| --- | --- | --- |
| Inline animation bar `.animation-controls` | `buildControls`, when `controlPlan(...).bar && styled` (`animation: 'inline'`, model reads `$t`) | absolute, bottom, full width |
| Toggled animation bar | same, `animation: 'toggle'`, unstyled, starts hidden behind a "Timeline" button | in flow |
| Running transport `.run-transport` | `buildTransportBar` for a document carrying a `program` | absolute, bottom, full width |
| Clocked chrome `.clocked-controls`, including `.clocked-transport` | `buildClockedChrome` | inside the left side rail (`PANEL_STYLE`), not at the bottom |
| Posed driver chrome `.driver-controls` | `buildDriverChrome` | left side rail |

Static models, drivers-only posed models and clocked machines therefore
have no bar at the bottom. Every committed fixture declares an `animation`
object; whether a model *has a timeline* is `tree.animated` (something reads
`$t`), exactly the input `controlPlan` already takes.

The canvas follows its container through one `ResizeObserver` on the
container (`viewer.ts`, `resize`). A container grown to full screen, or a
flex pane inside a root grown to full screen, triggers it with no new code.

The widget has no document-level key handler today. The navigator's tree
handles arrows, Home/End, Space and Enter on its rows and calls
`preventDefault` for the keys it consumes; no letter key is used. The
driver readouts handle Enter, Space and Escape on their own elements.

## Goals / Non-Goals

**Goals:**

1. One full-screen control in every host that mounts the viewer
   interactively: the export page, custom embeds and the development page.
2. The control sits on the player bar a model has, and in the corner when
   it has none, as the pilot specified.
3. `f` toggles, Esc exits natively, and the control always shows the true
   state.
4. It is honest where full screen is impossible, and absent from
   photographs.

**Non-goals:**

- A mount option, handle method or query parameter for full screen. No
  host needs one now (see D8).
- A CSS "pseudo full screen" fallback for iPhone Safari or a
  non-permitting iframe.
- Keyboard shortcuts beyond `f` (YouTube's `k`, `j`, `l` and so on).
- Auto-hiding the chrome while full screen, or changing any control's
  behaviour.
- Anything on machinome.org. It already sets `allowFullscreen`.

## Decisions

### D1. The widget root goes full screen: the inspector root, or the host's container

The element passed to `requestFullscreen()` is the **full-screen root**:

- in the inspector layout (the export page, `mountInspector`, the
  development page), the `.machinome-inspector` element, so the rail and the
  sidebar come along with the viewer pane;
- in a plain `mount()`, the container the host gave the viewer.

The canvas alone is never used. It would leave the timeline, the machine
rail and the corner button behind, and they are what makes the full-screen
view operable, as YouTube's player keeps its bar.

**Seam.** `fullscreen.ts` holds a module-private
`WeakMap<HTMLElement, HTMLElement>` from a viewer container to its root.
`mountInspectorWith` registers `viewerPane -> root` before it calls
`mountFn`. `mount()` resolves `fullscreenRootFor(container)`, which returns
the registered root or the container itself. This adds nothing to the
public surface: no option, no attribute and no exported symbol from
`widget.ts`. The inspector's own jsdom test can assert the registration
with its stubs.

**Rejected:** a `fullscreenRoot` mount option, which is public surface no
host has asked for. Also rejected: `container.closest('.machinome-inspector')`,
which makes the viewer depend on a layout's class name. Also rejected:
full-screening only the viewer pane in the inspector. That is closer to
YouTube's hidden sidebar, but it strands the only on-screen way to focus a
child: the inspector hides the viewer's descendant buttons (inspector-layout,
"does not repeat its navigator"). The sidebar stays collapsed by default in
the export page, so taking it along costs nothing on screen.

### D2. Placement follows the bar the viewer actually draws

A pure function decides:

```
fullscreenPlacement({ runTransport, inlineAnimationBar })
  -> 'run-transport' | 'animation-bar' | 'corner'
```

- `'run-transport'` when a running transport bar is drawn: the button is
  the last child of `.run-transport`, after Reset.
- else `'animation-bar'` when the **inline, styled** animation bar is drawn
  (`plan.bar && plan.styled`): the button is the last child of
  `.animation-controls`, after the speed control when there is one.
- else `'corner'`: an absolutely positioned overlay at the bottom-right of
  the viewer container (`right: 8px; bottom: 8px`), always visible, in the
  bars' own translucent dark style.

The corner case covers static models, drivers-only posed models, clocked
machines (their transport is part of the left rail, not a bottom bar), and
the `toggle`, `external` and `none` animation presentations. A toggled bar
is hidden by default, and a button inside it would not be "permanent". The
corner never collides with the side rails, which are anchored top-left.

The button is one element per mount, owned by the controller. The chrome
rebuilds (`refreshControls`, `rebuildRunChrome`, `rebuildClockedChrome`)
remove and recreate the bars, so the viewer calls `controller.place(...)`
after each rebuild, and the decision is re-taken from what was just built.

### D3. One button, SVG glyph, state from `fullscreenchange`

The button is `<button type="button" class="machinome-fullscreen">` with
an inline SVG: four outward corner brackets for "enter" and four inward
brackets for "exit". Its `aria-label` is "Full screen" or "Exit full
screen", and its `title` is "Full screen (f)" or "Exit full screen (f)".
It is in the tab order. Its state is read from
`document.fullscreenElement === root` on every `fullscreenchange`, never
tracked from the click, so an Esc exit, a browser-UI exit or a host's
`exitFullscreen()` all update it. The glyph uses `currentColor`, sized 18px
in a bar and in a 36px square corner button. No dependency and no font glyph:
the run transport already avoids transport glyphs because a minimal font
renders them as boxes.

### D4. The key rule

One `keydown` listener per mount, on the root's owner **document**, in the
bubble phase. A pure predicate decides whether a key toggles:

```
togglesFullscreen(event, { insideRoot, bodyTarget, soleViewer }) -> boolean
```

It returns true only when every one of these holds:

- `event.key` is `f` or `F`;
- no `ctrlKey`, `altKey` or `metaKey` (Shift is allowed, so Caps Lock and
  `F` work);
- not `event.repeat`, so holding the key does not flicker;
- not `event.defaultPrevented`, so a handler that consumed the key keeps it
  (the navigator's contract is untouched, and it consumes no letters
  anyway);
- the target is not editable: `input`, `textarea`, `select`, or anything
  `isContentEditable`, including the driver readouts' exact-value field and
  the clocked value fields;
- **and** either the target is inside this mount's full-screen root, or the
  target is the document's `body` or `documentElement` (nothing focused)
  and this mount is the only live viewer with full screen available in that
  document.

The listener is on the document, not the root, for the export page. In
that page, clicking the canvas focuses nothing (the canvas is not
focusable), so keys arrive with `target === body`. A root-level listener
would never hear them. In the site's iframe this is the case that matters:
after the reader clicks or drags the model, the iframe document has focus
and `f` works.

**Several viewers on one page.** A key inside a widget toggles that widget
only. A key with nothing focused toggles nothing when more than one viewer
is mounted, because there is no honest way to say which one the reader
meant. A module-level set of live controllers per document gives the count.
**Rejected:** tracking the last widget pointed at, which is heuristic state
no requirement needs.

When the event toggles, the controller calls
`root.requestFullscreen()`, or `document.exitFullscreen()` when
`document.fullscreenElement === root`, and calls `preventDefault()` on the
`f` key only. It never listens for or prevents Escape. A keydown is a user
activation, so the request is permitted.

### D5. Availability is `document.fullscreenEnabled`, unprefixed

`fullscreenAvailable(doc, renderMode)` is
`renderMode === 'continuous' && doc.fullscreenEnabled === true`, read at
mount. When it is false, the button is not created and the key listener is
not installed. This is false in an iframe without `allowfullscreen`
(or `allow="fullscreen"`) and on iPhone Safari, which has no element
full screen, only video. No CSS imitation is offered there. A pinned
"full screen" that is not full screen would be a false claim, and it would
fight the host page's layout.

Only the unprefixed API is used. Desktop Safari has shipped the unprefixed
`requestFullscreen` and `fullscreenEnabled` since 16.4 (2023), and iPadOS
Safari has as well. **Not verified here:** this rests on recalled
compatibility data, not a test on a Safari device. Implementation re-checks
it against MDN's browser-compat-data, and adds `webkit` fallbacks only if a
current desktop Safari still needs them.

A rejected `requestFullscreen()` promise, for example when the browser
denies it, is caught and ignored. The button state is unchanged because
no `fullscreenchange` fires.

### D6. A background while full screen

The inspector root's default background is `transparent`, and the export
page's body sets none. In full screen the browser paints a black
`::backdrop` behind the element, so the navigator's inherited dark text
would disappear, and the model would sit on black where it was published on
the page colour. While the root is full screen, the controller sets its
inline `background-color` to the page background it was seen on: the first
non-transparent computed `background-color` from the root up to
`<html>`, else white, the browser's default canvas. On exit it restores the
root's previous inline value. `fullscreenBackground(colors)` is pure and
unit-tested. A host that styles its own root background keeps it, because
the walk starts at the root.

### D7. Resize needs no new code, only proof

The container's `ResizeObserver` already resizes the renderer and camera.
In the inspector the pane is `flex: 1` inside a root the browser sizes to
the screen. In a plain mount the container itself is sized by the UA
full-screen rules. The e2e test asserts that the canvas matches the
viewport in full screen and returns to its original size after exit.

### D8. Capture and on-demand: no button, no new option

- `renderMode: 'on-demand'` is the still-capture mode, and already requires
  "no interactive controls". D5 makes it draw no full-screen control.
- `machinome-viewer capture` does not use on-demand. Its mount page, which
  this package writes (`Capture.write_mount_page`), gains one rule,
  `.machinome-fullscreen { display: none !important; }`. The photograph is
  clipped to the canvas, and the corner overlay lies over the canvas, so
  without the rule it would be in the picture.

**Rejected:** a `fullscreen: 'inline' | 'none'` mount option matching
`driverControls` and `partControls`. Its only consumer today would be
capture, which owns its page and can hide a documented class. That is the
same seam `compact-clocked-controls` D2 chose for inspector-only
suppression. An option would be public surface raising the API to 28 for a
use nobody has. If a host later needs to suppress the control without
CSS, that host is the evidence for the option.

### D9. Disposal leaves full screen

`dispose()` removes the listeners, drops the controller from the
per-document set, and, if `document.fullscreenElement` is this root, calls
`exitFullscreen()` first. A plain mount's container is never left full
screen and empty after `replaceChildren()`.

### D10. API and version

The viewer API stays **27**. The repository's rule (`openspec/config.yaml`)
raises it "on incompatible interface changes or when a capability a host
may require is added". This change adds no option, handle member, event or
document field, so no host can require it through the interface. The
precedents agree:

- `compact-clocked-controls` changed on-screen chrome only, including a
  class-based suppression, with "no viewer API or document version change";
- `draw-at-the-declared-tempo` changed the drawn chrome with "no API bump";
- `real-time-playback` did raise the API, because it added the `speed`
  option and handle methods "a host may now require". Nothing comparable is
  added here.

The package version stays 0.7.0 and no document version changes.

### D11. Where the changelog records it: a pilot decision

The brief asked for an "Unreleased" changelog heading. The ratified
`user-documentation` spec and `tests/test_documentation.py` forbid that
while 0.7.0 is at released state but not uploaded:

- the scenario "A reader checks an unpublished release record" requires
  "no Unreleased section above the release";
- the tests assert `'## Unreleased' not in changelog`, require the first
  section to be `0.7.0 — 23 September 2026`, and refuse "unreleased" on every
  reader-facing page.

An Unreleased section is mandated only for work after a release is
*published*, and 0.7.0 is not uploaded.

This proposal therefore follows the ratified spec and the repository's
precedent (`27499a5`, "Fold selected-joint handles ... into the 0.7.0
record", made after the release state was reached). The capability is
folded into the 0.7.0 changelog section under "What a maker gets", and the
user-documentation delta pins it there. The local tag `v0.7.0` (at
`94cbf9c`) would then lie behind the record. Moving the tag is the pilot's
act, as it was for `73f0e21` in the shop.

If the pilot instead wants 0.7.0 to stay as tagged, the alternative is an
`## Unreleased` section naming viewer API 27. That also modifies the
"Makers have a viewer manual" requirement and the three test assertions
above. Either path is one edit to task 3.4 and to the user-documentation
delta, and the pilot chooses before apply.

## Risks / Trade-offs

- **`f` before the reader touches the iframe.** Keys go to the parent page
  until the reader interacts with the embedded model, so `f` does nothing
  there. The button always works. A parent-page shortcut would be site
  work, and is not requested.
- **The development page's build-error pane** is appended to `body`,
  outside the inspector root, so it is not visible while full screen. Exiting
  shows it. Accepted: the development page is not an export, and moving the
  pane is a separate change if the pilot wants it.
- **Esc in headless Chromium.** Esc exit is native browser behaviour.
  Whether Playwright's synthetic Escape exits full screen in headless
  Chromium is not yet established. Task 1.4 records what it does. If it does
  not exit, the acceptance proves that the viewer never prevents Escape and
  that the button follows an exit made through `document.exitFullscreen()`,
  and the manual Esc check is done in a headed browser, recorded in
  `evidence.md`.
- **Corner overlay over the model.** 36px in the corner, in the bars' style.
  It is the pilot's explicit placement.

## Validation

- vitest: `fullscreen.test.ts` for `togglesFullscreen`,
  `fullscreenPlacement`, `fullscreenAvailable` and `fullscreenBackground`,
  and a jsdom controller test with stubbed `requestFullscreen` and
  `exitFullscreen` for label and title swaps on `fullscreenchange`, no
  button when unavailable, and disposal exiting.
  `inspector.test.ts`: the registration of `viewerPane -> root`.
- Playwright (`tests/test_widget_e2e.py`): placement on the spinner
  (animated, timeline bar), marked (drivers-only, corner), touched
  (running, transport bar) and calculator (clocked, corner) exports; `f`
  entering with `document.fullscreenElement` being `.machinome-inspector`
  and the canvas matching the viewport; exit restoring size and label; `f`
  ignored in a clocked value field and with Ctrl held; an iframe without
  `allowfullscreen` hiding the button and ignoring `f`, and one with it
  showing the button.
- `tests/test_capture.py`: the capture mount page shows no visible
  `.machinome-fullscreen`, and the photograph's bottom-right corner is
  transparent.
- `npx tsc --noEmit`, `npx vitest run`, `pytest`, and
  `openspec validate go-fullscreen --strict`.
