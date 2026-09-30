## Context

Leonardo's inspected `machinome-dark-sequence` and `machinome-syntax-study` used a disposable renderer to alternate an actual moving sawmill with full-screen pinned Python, with no side-by-side competition. The supported 0.4 tool has a model-only layout when a shot lacks `code` and a fixed left-code/right-model split when it has `code`; it cannot express that middle source-only picture. The historical syntax recipe pin `844c723…` used line 376, while the current export/source pin `28b43bce1b88446995f0ff231dd9075d1a839ab3` has the relevant drive relationship at `model.py` line 415. A supported proof must use the current pin, not copy the old coordinates.

`frameAt` currently returns a shot's code and, for a join, a separately resolved outgoing frame. The film page infers split layout from `Boolean(frame.code)`. `browserSession.show` always checks the viewer canvas fills `#stage`, and picture geometry picks the split stage whenever `f.code` exists. The shot cache fingerprints ordered global frame requests, including transition outgoing requests. Those are the seams this one opt-in must address without changing unchanged frames. The accepted working presentation assumption is current Videomaker styling/chrome; the pilot has not approved promoting the experiment's charcoal CSS or chrome-free look.

## Goals / Non-Goals

**Goals:**

- A format-0.4 author can opt one code-bearing shot into a source-only picture; absent opt-in keeps model-only/no-code and split/code frames pixel-identical to the present renderer.
- Keep pinned literal source, typing, cursor and optional measured emphasis, as well as current style, series/masthead, progress, captions, timing and overflow refusal.
- Preserve each side's own presentation through transitions and shot-cache reuse, with source visibility and bounds checked even though its model canvas is intentionally not on screen.

**Non-Goals:**

- No general layout/theme engine, dark-film aesthetic, chrome removal, noncontiguous source ranges, initial-prefix declaration, source rewriting, new viewer capability, mechanical behavior or paid speech generation.
- No rule that a dissolve/wipe/slide between model and source must avoid showing both at once; that would change existing joins. A film requiring strict visual separation can use a hard cut or fade through the existing colour plate.

## Decisions

### D1 — One optional source-only value; absent requests retain their old shape

Accept only `layout: source-only` on a 0.4 shot with `code`; no field means the current behavior. Do not add `model-only` or `split` author values merely to complete a table. A 0.2/0.3 use is a named format refusal; unknown layout values and the 0.4 closed shot-field list refuse by name. The current required `simulation`, camera and export pin remain required even on source-only shots; this is presentation, not a second kind of episode or model timeline.

Resolve the explicit value into that shot's frame request; do not add a new property to unchanged legacy/default requests simply to restate what `code` already says. The page interprets absence exactly as before. This minimizes compatibility risk, and the new request value gives the shot cache the visual dependency it needs. The existing renderer/timeline source hashes will still invalidate old cache generations when product code changes; no special migration/import is claimed.

**Alternative rejected:** infer source-only whenever `code` exists. It would silently change every split-screen episode. Three author-facing layout modes would add unused states; a shot-level source-only opt-in is enough for the named film.

### D2 — A source-only picture fills the existing film content area, not a new theme

Use a distinct source-only page state rather than the existing `with-code` split state. Put the source panel in the main content rectangle presently occupied by the plain model stage (5% horizontal inset, 16% top, 21% bottom) beneath the current masthead/series and above the current progress rule. Preserve current film background/foreground/accent/font and syntax styling; the exact font fit should be judged on the current Leonardo excerpt and normal output aspect, without an author-facing geometry control. The source-only *shot picture* has no visible viewer canvas. Keeping a mounted/posed viewer behind it is an internal continuity choice, not evidence that the model is visible.

On source-only frames, replace the visible-canvas-fill assertion with positive assertions that the source panel is visible in the intended rectangle, its literal text matches the pinned excerpt, and it neither clips nor overflows at every posed frame, including emphasis and outgoing continuation. Retain the canvas-fill assertion on model-only and split frames. Preserve ordinary overlay positioning and external subtitles; an overlay that obscures the source remains an editorial review issue under existing bounds checks, not a new layout API.

The current preview lens-change loop also projects points through the viewer
and dereferences `#stage canvas` to claim a changed FOV/up reached the
**picture**. A source-only shot intentionally hides that canvas. Keep its
authored camera/model timing, Viewer API requirements, resolved lens requests
and internal pose checks, but do not project a hidden canvas, dereference a
missing visible stage, or report source-only changes as visible lens evidence.
The positive source-panel checks above are its picture evidence. Every
model-only/split lens-change frame retains the existing visible projection and
up/FOV assertions, without loosened tolerances.

**Alternative rejected:** reuse the disposable experiment's `stage.html` or hardcode its charcoal styling. That would create two renderer paths and silently promote an unapproved aesthetic. Merely skipping every canvas/layout check on source-only would make a blank or clipped source appear valid.

### D3 — Refuse cues that would target or cover the absent model

In a source-only shot, refuse nonempty `annotations`, `highlight` and `pictures` cue lists at `check`, before browser or extraction. An annotation/highlight would assert a visible model target when its own picture has none. A picture would cover the source or inherit the current `code`-means-split stage calculation; supporting picture-over-source needs separate evidence. Empty lists remain harmless. Keep every existing split/model picture, target and viewer-API rule untouched. No special restriction is added to ordinary overlays, which retain their current screen-label semantics.

**Alternative rejected:** accept then suppress incompatible cues at render. Silent omission would misrepresent the authored screenplay and could still pollute cache identity or preview checks.

### D4 — Continuation and composition use each shot's resolved frame

`shotFrame`/`frameAt` carry the source-only value on the relevant incoming or outgoing request; transition composition uses those requests independently. Do **not** invent new source-end behavior: use current `codeAt` continuation and existing transition rules. On a source-only → model join, the outgoing source picture is whatever the current time mapping yields after the shot end (currently completed text without cursor); model → source joins continue the outgoing model as the existing rule requires. `pictureOnly` captures still omit chrome and the composed frame restores it once. Fades, dissolves, wipes, slides and cuts keep their existing timing and pixel rules. A model can be visible during an incoming source-only dissolve/wipe/slide because it is the **outgoing** picture, not because a model is drawn beside the new source panel.

The shot-cache key must distinguish an opted-in frame from an otherwise identical split frame, and a following incoming join whose outgoing frame changed must recapture under existing whole-shot dependency rules. No new keying framework is needed. Verify source-only requests on fractional global frame boundaries as well as ordinary cuts.

**Alternative rejected:** derive outgoing layout from the incoming active shot or from `Boolean(code)` after flattening the transition. That would show the wrong picture on one side and could reuse stale join frames.

### D5 — Named Leonardo proof and compatibility

Before implementation, author a short project-owned format-0.4 fixture with real model → source-only → real model shots, current pinned export/source and a contiguous excerpt containing line 415 (`water_drive.waterwheel.spin.drives(water_drive.crankshaft.spin)`). It may use a silent render or a verified existing cached take; this cycle does not authorize a new purchase. Include one join in each direction, using authored kinds that keep the chosen editorial look readable. Separately test all four transition kinds on synthetic frames so no join variant silently falls back to split. Source typing and optional emphasis keep existing timing/refusal tests; real measured emphasis is exercised only if the fixture's verified cached take actually matches.

Capture exact pre-change pixels for unchanged model-only/split 0.4 and legacy 0.2/0.3 consumers under a pinned viewer/browser, and compare after implementation. The new source-only film must be previewed and rendered, inspect source/canvas/chrome/fit/transition evidence, verify exact seek replay and cold-versus-incremental PNG equality, and be reviewed by root on the encoded MP4. Pixel proofs cannot approve the look by themselves.

Include a source-only shot with changed FOV and up in the red browser matrix:
the original unconditional lens check must fail or falsely claim visible
evidence before implementation, then the scoped check must prove the resolved
internal requests and visible source without a null canvas access. Also keep
a changed-lens model/split control whose projection still must pass.

## Risks / Trade-offs

- **The content rectangle or unchanged syntax sizing may not read well at the real aspect** → inspect decoded output and adjust only the source-only CSS in review; no dark theme or new author control by default.
- **A hidden viewer can fool existing positive model checks** → branch on the resolved presentation and assert source visibility, literal text and bounds, while retaining canvas checks where the model is meant to show.
- **Hidden FOV/up changes could be misreported as visible lens proof** → retain source-only camera requests and pose checks but omit its hidden-canvas projection claim; preserve the full projected-pixel assertion for visible model/split pictures.
- **An outgoing join may render the wrong layout or reuse stale frames** → carry both resolved requests independently, test both directions and compare exact cold/incremental global-frame pixels.
- **The old experiment's collage is not representable as one excerpt** → use current line 415 for the smallest real proof; revisit multi-range/initial-prefix only on a separate named film need.

## Migration Plan

No source migration: absent `layout` is the current renderer. Format 0.4 episodes may opt individual code shots in; 0.2/0.3 retain their old frames and refuse the new field. New code hashes force a cold cache generation as current cache rules require. Rollback means removing the opt-in field and using the unchanged split view; no media/source file is rewritten.

## Open Questions

None that requires a broader product decision for this cycle. Root's proposal review must confirm the exact source-only content rectangle and the new-opt-in cue refusals before implementation; the pilot retains final aesthetic authority over any later dark/chrome-free direction.
