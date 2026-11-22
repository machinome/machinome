# ADR-084: A model's app is a script the viewer starts inside mount(), through a framework-neutral contract

**Status:** Accepted

**Date:** 2026-11-22

**Change:** [show-a-models-own-app](../../../openspec/changes/archive/2026-11-22-show-a-models-own-app/) (design Decisions 1 to 5 and 8 to 10)

**Builds on:** [ADR-076: A part's presented look has one owner](ADR-076-a-parts-presented-look-has-one-owner.md),
[ADR-080: A continuous viewer draws a frame only when its picture has changed](ADR-080-a-continuous-viewer-draws-a-frame-only-when-its-picture-has-changed.md)

## Context

The Enigma I reconstruction is operated through the panel the viewer builds
from its declarations: a side rail of dozens of handles, readouts and
buttons. A reader cannot type on it. The pilot asked for the model to carry
its own app, a React application kept beside the model, shown in place of
that panel wherever the viewer shows the model. Every page that shows a
model goes through `mount()`: the export page, the development page, the
Studio and the Enigma's public page. The viewer has been React-free since
ADR-052.

## Decision

**A document may name its model's app; where it does, `mount()` loads it
and the app takes the place of every automatic panel. The contract between
the viewer and an app is a classic script, an event and a function, and the
viewer's bundle carries no React.**

1. **Where.** The app is shown when the document names one, the chrome is
   presented (`driverControls: 'inline'`, the default) and the render mode
   is continuous. `driverControls: 'none'` and every on-demand mount get
   neither the app nor the panel, and no file of the app is fetched. No new
   option. (The render-mode clause is redundant with `resolveOptions`,
   which already requires `'none'` on demand; it stays as a statement of
   the rule.)
2. **The record.** `app: { script, stylesheet? }` or `app: { refusal }`
   at the document's top level, additive and gated on no document version.
   It is validated with the document whatever the mount presents: exactly
   one of `script` and `refusal`; relative paths with no `..` segment,
   no leading `/`, no backslash and no scheme; a non-empty refusal; and,
   as decided in the implementation, **an unknown key, a backslash and a
   stylesheet beside a refusal are refused** too. A malformed record refuses
   the document by name, as a malformed `markings` list does: an app read
   in part would be shown as if it were the one its author published.
3. **The contract.** The viewer attaches the stylesheet, awaits it, then
   attaches the script; the script dispatches `machinome:app` with
   `{ contract: 1, start }` on its own element; on load the viewer calls
   `start({ contract, element, viewport, viewer, refuse })` and keeps the
   disposer it returns. No global name is claimed. `mount()` awaits the
   start or its refusal and never rejects for an app's failure.
4. **The picture.** Only when an app is to be shown, a viewport is made:
   the canvas moved into it and placed absolutely, the resize observer moved
   to it, the corner full-screen control anchored on it. **The viewport stays
   once made:** when a republish removes the record, or the app is refused,
   it fills the container again with the canvas inside; a document that
   never names an app never makes one, and keeps today's DOM.
5. **What stays.** The inspector's rail, sidebar and navigator, orbit, part
   controls, the outcome label, `$t` playback, and the whole handle.
6. **Refusals.** A refusal record, a file that does not load (named with its
   HTTP status, fetched once more after the error), a script that starts no
   app or speaks another contract, a start that throws, and an app's own
   `refuse` each show the model filling the area with a notice, "This
   model's app is not shown: <reason>", and the same sentence on the
   console. No automatic panel is shown in the app's place.
7. **Republish.** The same files keep the running app, which hears the
   change like any subscriber; other files replace it with the picture
   standing; a removed record restores the panel; an added one removes it.
8. **Disposal.** Full screen first, then the app (its disposer while the
   handle still answers, its stylesheet, its element, the viewport), then
   everything else. A load still pending is abandoned and never started.

## Alternatives

- **An option of its own** (`app: 'inline' | 'none'`): no host asks for
  the app without the panel switch or the reverse.
- **An ES module through `import()`:** fails on `file:` and needs CORS.
- **A global registry by URL:** a global name for a contract that needs none.
- **React elements across the boundary:** makes the viewer import React.
- **The panel shown when the app fails:** presents the interface the author
  replaced as if it were the model's.

## Consequences

- Viewer API 31; document versions stay 1 to 14. An older viewer ignores the
  record and shows the automatic panel, a truthful rendering of the machine.
- An app's stylesheet applies to the whole page; the manual tells authors to
  scope it.

## Proof

`src/app.test.ts` (A1 to A9), `tests/test_model_app.py` (B1 to B6, in
Chromium), and the mutation sweep of the change's `evidence.md`.
