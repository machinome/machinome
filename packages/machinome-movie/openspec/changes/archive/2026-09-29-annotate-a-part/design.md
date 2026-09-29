## Context

A frame is a pure function of video time: `frameAt(e, t)` in `src/timeline.mjs`
returns the model time, camera, hidden paths, active overlays and code; the page
(`src/film.js`) poses the paused on-demand viewer with it and Playwright captures
the page. Text overlays are DOM elements in `#overlays` at three fixed positions.
The viewer is mounted with API 21 or later; the preview's real-browser checks
compare replayed pixels exactly.

Viewer API 28, proposed in parallel, adds (the contract this design uses):

- `viewer.partOnScreen(path)` -> `{rect:{x,y,width,height}, point:{x,y}|null} | null`,
  viewport CSS pixels for the current pose; null when not visible or wholly off
  screen; throws for a nonexistent path; reading never renders.
- `viewer.project([x,y,z])` -> `{x,y} | null`, null behind the camera.

Screen positions depend on the posed camera, the stage layout (`with-code`
moves the viewport) and the part's pose, so they can only be read in the page,
after the viewer is posed.

## Goals / Non-Goals

Let an author point at a part, or keep a short label beside it, while it moves,
written as readable YAML beside the narration. Keep frames reproducible on seek
and resume. Refuse what cannot be drawn truthfully. Not goals: entrances, rings,
boxes, automatic layout, easing of annotation properties (roadmap items 6, 7).

## Decisions

### D1. The field

```yaml
    annotations:
      - from: 0.4
        to: 5.366
        kind: arrow
        part: [Feed mechanism, Driving pawl]
        place: [0.18, 0.22]
        text: Pulls one tooth
      - {from: 5.366, to: 10, kind: arrow, part: [Feed mechanism, Holding pawl],
         place: [0.82, 0.22], text: Holds it}
      - {from: 0, to: 10, kind: label, part: rope-1, offset: [0.04, -0.05], text: Rope 1}
```

(`rope-1` would be a production layer holding `[Feed mechanism, Ratchet to
reduction shaft]`; the path form and the layer form are interchangeable.)

- `from`, `to`: shot-local seconds, half-open like overlays, `0 <= from < to <= duration`.
- `kind`: `arrow` or `label`. Nothing else in this change.
- Target, exactly one of:
  - `part`: a string names a production `layers` entry; a list is one
    root-relative assembly path, spelled as a `layers` path is (exact sibling
    names, the document root excluded). A layer holding several paths is one
    target: its bounds are the union of theirs.
  - `point: [x, y, z]`: a world point in the model's units and frame, the same
    frame the named cameras use. It does not move with any part.
- `text`: the words shown. Required for `label`; optional for `arrow` (a bare pointer).
- `place` (arrow only, required): `[x, y]` in safe-area units where the arrow's
  tail and its text sit. `[0, 0]` is the top-left and `[1, 1]` the bottom-right of
  the safe area: the frame inset on every side by `style.safeInsetFraction`.
- `offset` (label only, optional, default `[0, 0]`): `[dx, dy]` in safe-area units
  from the target's screen anchor to the label's centre, each within `[-1, 1]`.

`place` is fixed on screen and the tip moves; a label moves with its target. This
is the smallest pair the evidence asks for: the pawls want pointers from fixed
words; "Rope 1 / Rope 2" wants words riding with the ropes.

An episode that uses annotations must declare a finite `style.safeInsetFraction`
in `[0, 0.5)`. Both Leonardo productions already declare `0.08`; FORMAT.md today
calls it an unimplemented hint, and annotations are its first operational use.
No default is invented.

### D2. The anchor

The anchor of a `part` target is the viewer's visible `point` when it returns one,
otherwise the centre of `rect`. For a multi-path layer, the rect is the union of
the non-null rects and the point is the first non-null point in the layer's
order. The anchor of a `point` target is `project(point)`. An arrow's tip is the
anchor; its shaft runs from the text box edge nearest the anchor to the tip,
with a head sized to the frame width. The tip is drawn at the anchor, not stopped
at the rect edge, so an arrow touches the part it names.

### D3. The timeline stays pure; the page resolves

`frameAt` adds `annotations`: the active cues with their target resolved to data
(`{paths:[...]}` from the layer or path, or `{point:[...]}`), `kind`, `text`,
`place`/`offset` and the safe inset. No screen position is computed in Node.

`film.js` resolves annotations **after** `setView` has posed and rendered the
viewer, reading `partOnScreen`/`project` (which never render), then draws an
inline SVG layer `#annotations` above the stage and below the text overlays:
shaft and head in `style.accent`, text in `style.foreground` on a
`style.background` plate like the lower third, sizes in `vw` so the 960-pixel
preview and the 1920-pixel render keep proportions. The layer is rebuilt from
scratch every frame, as `#overlays` is, so no drawn state survives a seek.
`setFrame` returns the resolved geometry: each annotation's anchor, its target
rect (part targets), the stage rectangle and the text box.

### D4. Refusals

At `check` (before any browser): unknown `kind`; both or neither of `part` and
`point`; unknown layer; an assembly path absent from the exported manifest (the
same walk `loadEpisode` uses for layers); a non-finite point; `from`/`to` outside
the shot or not increasing; `arrow` without `place`, `place` outside `[0, 1]`;
`label` without non-empty `text`; `offset` outside `[-1, 1]`; `place` on a
label or `offset` on an arrow; a `part` target equal to or inside a path the same
shot hides with `hiddenLayers` (the viewer would report it invisible; the author
must choose); `annotations` in a 0.2 episode; a missing safe inset.

At every posed frame in `preview` and `render`, in `render.mjs`'s `pose`: an
active annotation whose anchor is null or outside the stage rectangle is refused
with the shot id, the annotation's index and text, and the video time
("Annotation target is not on screen: pawls #1 'Holds it' at 44.87 s"). A text
box that leaves the frame is refused the same way. A moving part that leaves the
frame therefore stops the render; the author shortens the cue. Drawing nothing
silently was rejected: it would hide an authoring error in a released film.

### D5. Format 0.3 and the viewer requirement (shared)

These two decisions are shared with `highlight-a-part` and
`move-up-and-field-of-view`. Whichever of the three is applied first implements
them; the others extend the list of fields.

- `loadEpisode` accepts `machinome-video-draft/0.2` and `/0.3`. 0.2 keeps its
  exact semantics. The new fields are accepted only in 0.3. The bump is needed,
  not cosmetic: today's validator ignores unknown shot keys, so an older
  Videomaker would render a film with its arrows silently missing; with 0.3 it
  refuses "Unsupported episode format" instead.
- A pure `requiredViewerApi(e)` returns 21, or 28 with the reasons (field and
  shot ids). `preview`/`render` pass it to the page, which refuses on mount:
  "This episode needs Viewer API 28 for annotations (shot pawls); the selected
  viewer declares API 27. Select a newer machinome-viewer bundle with --viewer."
  `check` has no browser; it reads the declared API from the selected bundle's
  banner comment (`viewer API <n>`, present in the 0.7.1 bundle) and refuses the
  same way, or refuses "cannot confirm the viewer API" when the bundle or banner
  is missing. An episode requiring only 21 does not touch the bundle in `check`,
  as today. The runtime `apiVersion` is authoritative in `preview`/`render`.

### D6. Frame cache and provenance

The render identity already hashes the served page files and `timeline.mjs`;
any new Node module on the frame path is added to that identity. The manifest
records `requiredViewerApi` and its reasons beside the viewer hash.

## Risks / Trade-offs

- The viewer's visible point is found by ray casting; if it moves to another
  place on the part between frames, the tip jumps. Mitigation: preview samples
  each arrow at a quarter and three quarters of its cue, and the pilot inspects
  the motion in a rendered clip. If jumps appear, the fallback is a later change
  (for example an author option to aim at the rect centre), not a silent smoothing
  that would make a frame depend on its predecessors.
- The rect is the projected bounding box, so for a slender diagonal part
  (a rope) its centre may lie off the part; the visible point avoids that when
  the viewer finds one.
- Label placement is manual; a label can cover the part. Visual review at the
  final aspect ratio is required, as for overlays today.
- A strict off-screen refusal can stop a long render late. Preview samples every
  annotation's start, midpoint and end first, so most failures surface there.

## Migration Plan

Additive. 0.2 episodes, including all Leonardo episodes, parse and render
unchanged and keep working with a Viewer API 21 bundle. Authors opt in by
changing `format` to 0.3. Reverting the tool commit removes the field; a 0.3
episode is then refused by format, never rendered without its arrows.

## Open Questions

- Visible point versus rect centre as the anchor (D2): chosen to touch the part;
  the pilot may prefer the steadier centre after seeing a moving arrow.
- Whether `ring` is wanted: no shot asks for one yet, so it is left out.

## Ratification and resolutions (29 September 2026)

The pilot ratified this change with the sibling changes `highlight-a-part` and
`move-up-and-field-of-view`. D5 is implemented here, the first of the three
applied. Where the ratified implementation departs from the text above:

- **D2 amended; first open question resolved.** The anchor of a `part` target is
  the centre of the part's on-screen `rect`, the union of rects for a multi-path
  layer. The viewer's ray-cast `point` is not used: its grid search can land on
  a different place of a moving part from frame to frame and make the tip jump.
  The risk noted for slender diagonal parts (the rect centre may lie beside the
  part) is accepted and left to visual review; FORMAT.md says so.
- **Reconciled viewer contract.** The viewer (API 28) returns `rect` as the
  unclipped projected box and `null` only when nothing is visible or the part is
  wholly off screen; `project` returns off-canvas coordinates for a point in
  front of the camera and `null` only at or behind the camera plane. The page
  therefore refuses an anchor outside the stage rectangle itself (D4), not only
  a null one. Coordinates are viewport CSS pixels; the page subtracts its
  annotation layer's origin when drawing.
- **Unknown annotation fields are refused** (`Unknown annotation field: palce`),
  a small addition to D4 so that a misspelled optional `offset` cannot silently
  fall back to its default.
- **Annotation indices are zero-based** in messages and reports, as in D4's
  example (`pawls #1 'Holds it'` is the second annotation).
- **Frame shape.** `frameAt` adds `annotations` only to format 0.3 frames (always,
  empty when none is active), so 0.2 frame objects stay identical field for field.
- **Preview samples** each annotation at `from`, its quarters and midpoint, and
  the last output frame before `to`; each sample in the preview report carries
  the drawn anchors, part rectangles, arrow tails and text boxes.
- **`check`** reads the first 4 KiB of the selected bundle for `viewer API <n>`.
