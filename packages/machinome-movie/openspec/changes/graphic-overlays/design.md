## Context

- A frame is a pure function of video time. `frameAt(e, t)` in `src/timeline.mjs`
  emits, for 0.3 and later frames, `annotations`: the shot's active cues
  (`from <= local < to`) as data (`index`, `kind`, `text`, the target resolved
  to `{paths}` or `{point}`, `place` for an arrow or `offset` for a label, and
  the safe inset). No screen position is computed in Node.
- `src/film.js` (`drawAnnotations`) rebuilds `#annotations` from nothing on every
  frame after the viewer is posed: one shared SVG for strokes, one
  `div.annotation-text` plate per text. A part's anchor is the centre of its
  on-screen `rect` from `viewer.partOnScreen(path)`, the union of rects for a
  multi-path layer (`annotate-a-part`, as ratified); a point's anchor is
  `viewer.project(point)`. The arrow's shaft is a `line` of width `W·0.0024`
  from the text plate's edge nearest the anchor to the head's base, and its head
  a filled triangle of length `W·0.012`, both in `style.accent`; `W` is the frame
  width. `setFrame` returns each annotation's anchor, rect, tail and text box.
- `render.mjs`'s `pose` refuses an active annotation whose anchor is null or
  outside the stage rectangle, or whose text box leaves the frame, naming the
  shot, the annotation's zero-based index and its text or kind, and the video
  time. `preview` samples every annotation at `from`, its quarters and midpoint,
  and the last output frame before `to`; the exact pixel-replay check poses one
  instant, another, and the first again.
- `validateAnnotations` (`src/episode.mjs`) already refuses unknown annotation
  fields in every format (`Unknown annotation field: palce`), a hidden target, a
  missing safe inset and annotations in 0.2.
- Ratified siblings this change builds on, by name:
  - `keyframes-and-easing` (implemented): format 0.4, `ease(name, u)` over
    `linear`, `smooth`, `in`, `out`, `in-out` (clamping `u` to `[0, 1]`, exactly 0
    at 0 and 1 at 1, never overshooting), its refusal message, and closed 0.4
    field lists that later cycles extend.
  - `shot-transitions` (being applied before this change): an outgoing shot's
    cues whose `to` equals the shot's duration continue past its end through the
    transition, and annotations keep being resolved and refused there; its
    preview proofs decode captures and compare pixels (a dissolve's midpoint is
    the blend within 2 levels of 255).
  - `text-animation` (applied after this change): titles take
    `enter`/`leave: {kind: fade, duration, ease}`, default `smooth`, and adopt
    whatever spelling this change ratifies, so that 0.4 has one.
  - `stills-and-clips` (applied after this change): a picture refuses any
    annotation of the same shot that overlaps it; pictures fade with
    `fadeIn`/`fadeOut: {duration, ease}`.
- The evidence (proposal, Why): *Revolutions* `pawls`, *Revolutions v2*
  `two-rope-reduction` and `whole-machine`, and the campaign demo
  `demo-feed-mechanism` `name-the-pawls`. Every mark those shots ask for is aimed
  at a part the export contains, two of them under a moving camera.

## Goals / Non-Goals

Goals: let an author ring a part, with no words, as it moves; let every
annotation arrive by a fade or by drawing itself on, and leave by a fade, with
the campaign's easing names; keep each frame a function of its video time; refuse
what cannot be drawn truthfully; prove entrances and exits in pixels; keep every
0.2 and 0.3 frame and pixel, and every 0.4 frame without the new fields.

Non-goals: shapes, placements and entrances no shot asks for (D9); a new list
beside `annotations`; any change of the arrow's look; any viewer change.

## Decisions

### D1. One list, one new kind; a callout is an arrow with words

The marks go into the existing `annotations` list. A second list of "graphics"
would repeat the targets, the timing, the anchor rule, the hidden-part and
off-screen refusals and the drawing layer that annotations already have.

- **`ring`** is the one new kind (D2). It is the mark the evidence asks for: a
  part singled out without words, following it while the camera moves.
- **A callout is an arrow with `text`.** Words on a plate, fixed at `place`, with
  a leader from the plate's nearest edge to what they name, is exactly what
  `annotate-a-part` built. A `callout` kind would be a second spelling of that
  one thing, so there is none; FORMAT.md says "a callout is an arrow with text"
  where an author will look for the word.
- `box`, `line` and fixed-place shapes are left out (D9).

### D2. The ring

```yaml
# format machinome-video-draft/0.4 — Revolutions pawls, restaged
  - id: pawls
    start: 39.5
    end: 49.5
    ...
    hiddenLayers: [structure, foundation, water, carriage]
    overlays:
      - {from: 0, to: 5.366, text: Pull · advance one tooth, position: top}
      - {from: 5.366, to: 10, text: Return · hold that progress, position: top}
    annotations:
      - from: 0
        to: 5.366
        kind: ring
        part: [Feed mechanism, Driving pawl]
        enter: {kind: draw, duration: 0.8}
        leave: {kind: fade, duration: 0.4}
      - from: 5.366
        to: 10
        kind: ring
        part: [Feed mechanism, Holding pawl]
        padding: 0.02
        enter: {kind: draw, duration: 0.8}
```

- **Target.** `part` only: a production layer name or one assembly path, as for
  arrows and labels. A layer holding several paths is one target, ringed as one
  (a `pawls` layer holding both pawls gets one ring around both). A ring on a
  `point` is refused: a point has no extent to ring (D9).
- **Geometry.** Let the part's on-screen rectangle (the same `rect`, or union of
  rects, that places an arrow's tip) have centre `(cx, cy)`, width `w` and height
  `h`, and let `P = padding · Ws`, where `Ws` is the safe area's width in pixels
  (`W · (1 − 2·safeInsetFraction)`). The ring is the ellipse centred on
  `(cx, cy)` with semi-axes `rx = √2·(w/2 + P)` and `ry = √2·(h/2 + P)`: the
  ellipse through the four corners of the rectangle grown by `P` on every side.
  It therefore encloses the whole rectangle for any `P > 0` and stays clear of a
  slender diagonal part whose ends reach the rectangle's corners (a pawl), and
  its proportions follow the part's (a long rope section gets a long ring).
- **`padding`** (optional): a number in `[0, 0.25]`, in safe-area widths so it
  is measured as `place` and `offset` are, the same pixel distance on every
  side. Default `0.01` (about 16 pixels at 1920 wide with an inset of 0.08), so
  that a ring does not pass through the tips of a part that fills its
  rectangle's corners. The default is emitted explicitly by the timeline, so
  the page never decides it.
- **Look.** A stroke in `style.accent` of width `W·0.0024`, the arrow shaft's,
  with no fill; drawn in the annotation layer in annotation order, above the
  model and below the text overlays, like every annotation.
- **Fields.** `text`, `place` and `offset` are refused on a ring: a ring carries
  no words (the evidence's point), and words beside it are a `label` or an
  `arrow` in the same list. `padding` is refused on an arrow or a label.

### D3. Entrances and exits: the fields

```yaml
# format machinome-video-draft/0.4 — demo-feed-mechanism name-the-pawls, restaged
    annotations:
      - {from: 0.2, to: 9, kind: arrow, part: [Feed mechanism, Driving pawl],
         place: [0.1, 0.3], text: Driving pawl, enter: {kind: draw, duration: 0.8, ease: out}}
      - {from: 1.9, to: 9, kind: label, part: [Feed mechanism, Holding pawl],
         offset: [0.12, -0.03], text: Holding pawl, enter: {kind: fade, duration: 0.5}}
```

- `enter` and `leave` are optional on every kind, each a mapping
  `{kind, duration, ease?}`.
- `enter.kind`: `fade` or `draw`. `leave.kind`: `fade` only (D9 on draw-off).
  `kind` is kept although `leave` has one value, so that the entrance, the exit
  and `text-animation`'s title fades share one shape that can grow.
- `duration`: video seconds, finite, at least two output frames
  (`2 / output.fps`), the rule `shot-transitions` and `stills-and-clips` use,
  so an entrance always has a frame between its first and its end.
- `ease`: one of the five names; default `smooth`, the campaign's default for
  every transition-like curve (`shot-transitions`, `text-animation`,
  `stills-and-clips`).
- The entrance occupies `[from, from + enter.duration)`, the exit
  `[to − leave.duration, to)`. Both lie inside the cue: `from` and `to` keep
  their meaning, so a mark that fades out is gone at `to` exactly as a mark
  without an exit is.
- **Spelling.** `enter`/`leave` with `kind` is the spelling `text-animation`
  proposed and defers to this change for; ratifying it here gives 0.4 one
  spelling for "how a cue arrives and leaves". Pictures' `fadeIn`/`fadeOut`
  (`stills-and-clips`) are a second spelling of a cue's fade; see Open Questions.
- No presets in `production.yaml`: an entrance is three short words, and its
  duration belongs to the screenplay's timing, which is read beside the
  narration (the reasoning `shot-transitions` gives for its own fields).

### D4. What an entrance or exit does, as a function of the cue's local time

For local time `l` in the cue and `ease` from `src/easing.mjs` (which clamps its
argument to `[0, 1]`):

- `uIn = (l − from) / enter.duration`, `uOut = (l − (to − leave.duration)) / leave.duration`.
- **Opacity** `a = min(fadeIn, fadeOut)`, where `fadeIn = ease(enter.ease, uIn)`
  if the entrance is a fade, else 1, and `fadeOut = 1 − ease(leave.ease, uOut)`
  if there is an exit, else 1. The whole mark (stroke, head, text plate and its
  words) takes that one opacity.
- **Drawn fraction** `f = ease(enter.ease, uIn)` if the entrance is a draw-on,
  else 1.

So a fade-in's first frame (`uIn = 0`) shows nothing of the mark, a draw-on's
first frame shows none of its stroke, and from `from + enter.duration` on the
mark is drawn exactly as it would be without an entrance; an exit's first
instant shows the mark exactly as without an exit, and its opacity then falls to
reach 0 at `to`, where the cue ends in any case. `ease` is exactly 1 at 1, and
`1 − ease(name, 0)` is exactly 1, so these identities hold in floating point.

What each kind means:

- **fade**, every kind: the mark at opacity `a`. Nothing moves or changes size.
- **draw** on a **ring**: the ellipse's stroke is revealed along its length from
  its top point (`(cx, cy − ry)`), clockwise on screen, to the fraction `f` of its
  perimeter, measured as the browser measures the path's length.
- **draw** on an **arrow**: the words and their plate are shown in full from
  `from` (they are where the stroke leaves from); the shaft and head are
  revealed from the tail towards the tip, everything of them within `f·L` of the
  tail along the shaft being drawn, with `L` the tail-to-tip distance, so the
  head appears last, as the reveal reaches it. An arrow without text reveals
  the same way.
- **draw** on a **label**: refused at `check` (a label has no stroke; use `fade`).
- The mark keeps following its part through its entrance and exit: `f` and `a`
  shape how much of it is drawn, never where. The ring's ellipse and the arrow's
  tip are recomputed from the part every frame, as without an entrance.

For the restaged `pawls` shot above (default `smooth`): the driving pawl's ring
is half drawn (`f = 0.5`, the right half from the top round to the bottom) at
0.4 s and complete at 0.8 s, and fades from 4.966 s to nothing at 5.366 s, the
instant the holding pawl's ring begins to draw.

### D5. The timeline carries the numbers; the continuation of a transition

`frameAt` stays pure data. In a 0.4 frame, an active ring is emitted as
`{index, kind: 'ring', target: {paths}, padding, safeInset}` (padding defaulted
explicitly). A cue that declares `enter` or `leave` additionally carries
`opacity: a` and `drawn: f` (D4), both numbers in `[0, 1]`. A cue that declares
neither is emitted exactly as today, field for field, so a 0.4 episode without
the new fields keeps the frames the earlier 0.4 cycles pinned, and no new
frame-level key is added.

`shot-transitions` continues an outgoing shot's cues whose `to` equals the
shot's duration past that end. A cue with a `leave` has finished leaving at `to`
(opacity 0), so it is not continued: it is absent from the continued frames, and
is neither drawn nor resolved there. A cue without `leave` continues as
`shot-transitions` says, with `a` and `f` at their end values (1).

### D6. The page

- **Rings.** `drawAnnotations` draws a ring as an SVG path (two half-ellipse arcs
  from the top point, clockwise) with the D2 geometry, `fill: none`,
  `stroke: style.accent`, width `W·0.0024`.
- **Opacity.** Each cue that carries `opacity` has its strokes drawn in one SVG
  group with that group opacity, and its text plate given the same CSS opacity.
  Group opacity composites the group as one layer, so where the shaft meets the
  head, or where a ring crosses its own antialiasing, the faded mark is exactly
  the blend of the mark drawn in full and not drawn, which is what D8 proves.
  The plate and the strokes do not overlap (the shaft leaves the plate's edge).
- **Draw-on.** A ring is revealed with a dash over its path's own length (the
  path given a unit length, a dash of `f` and a gap of 1, butt caps, so `f = 0`
  draws nothing). An arrow's strokes are revealed by a clip to the half-plane
  within `f·L` of the tail along the shaft.
- **Unchanged cues are drawn by today's code, unchanged.** A cue without the new
  fields is drawn exactly as now (no group, no opacity attribute), so 0.3 and
  plain 0.4 pixels are unchanged; a cue at `a = 1`, `f = 1` is drawn in a group
  at opacity 1 whose pixels D8 proves equal to the plain drawing.
- **Report.** `setFrame` adds to each drawn annotation, where they apply: the
  ring `{cx, cy, rx, ry}`, `opacity`, `drawn`, and, while `0 < f < 1`, two
  stroke points measured on the drawn path: `inside`, at half the drawn length,
  and `outside`, at the middle of the undrawn length (for a ring, the points at
  `f/2` and `(1 + f)/2` of the perimeter; for an arrow, at `f·L/2` and
  `(1 + f)·L/2` from the tail).
- The layer is still rebuilt from nothing every frame; nothing depends on the
  previous frame.

### D7. Refusals

At `check`, naming the shot and the annotation (`annotation #i`):

- In 0.2: the existing `Annotations need format machinome-video-draft/0.3`.
  In 0.3: `kind: ring`, `padding`, `enter` or `leave`:
  `Rings, entrances and exits need format machinome-video-draft/0.4: shot pawls`
  (without it, 0.3's closed annotation list would refuse them as unknown fields
  or an unknown kind, which does not tell the author what to do).
- In 0.4: a kind other than `arrow`, `label` or `ring`
  (`kind must be arrow, label or ring`); a ring with `point`
  (`a ring is drawn around a part; give part, not point`); a ring with `text`,
  `place` or `offset` (`a ring carries no text or place; add a label or an arrow
  beside it`); `padding` outside `[0, 0.25]` or on an arrow or label; `enter` or
  `leave` that is not a mapping; an unknown field in either
  (`Unknown entrance field: durration (annotation #0 in shot pawls)`,
  `Unknown exit field: ...`); an entrance kind other than `fade` or `draw`, an
  exit kind other than `fade`; `draw` on a label
  (`a label has no stroke to draw; enter with fade`); an easing name outside the
  five (the vocabulary's message, with `(entrance of annotation #0 in shot pawls)`);
  a duration that is not finite or shorter than two output frames; an entrance or
  exit longer than the cue (`the 1.2 s entrance is longer than the cue (1 s)`);
  an entrance and exit together longer than the cue
  (`Entrance and exit overlap in annotation #0 in shot pawls: 0.8 s in and 0.6 s out exceed its 1.2 s`).
- Unchanged and applying to rings: an unknown layer or missing assembly path, a
  target the same shot hides, a missing safe inset, times outside the shot, and
  (with `stills-and-clips`) a cue overlapping a picture.

At every posed frame in `preview` and `render` (including the continued frames
of a transition), for an active ring, in addition to today's anchor check:

- its part's rectangle not wholly inside the model stage:
  `Ring target is not wholly on screen: pawls #0 (ring) at 44.87 s`. A ring
  around a part that is partly out of view would enclose what the audience
  cannot see; the viewer reports the unclipped projected rectangle, so this is
  known exactly.
- its ellipse's bounding box (`cx ± rx`, `cy ± ry`) leaving the frame:
  `Ring leaves the frame: pawls #0 (ring) at 44.87 s`. Reduce the padding or
  reframe.

The target checks apply for the whole cue, entrance and exit included: a mark
fading in is still a claim about where the part is.

### D8. What `preview` proves

For each annotation with an entrance or exit, `preview` samples and saves as
stills: the entrance's first frame (`from`), midpoint and end
(`from + enter.duration`); the exit's start (`to − leave.duration`), midpoint and
last output frame before `to`. These join the existing annotation samples (the
cue's start, quarters, midpoint and last frame).

Then, posing each instant of a check with the cue as authored ("composed"), with
that one cue's `enter` and `leave` removed ("full") and with that one cue removed
("without"), and comparing decoded pixels with the comparison `shot-transitions`
uses:

- **Fade midpoint** (entrance or exit): every channel of every pixel of composed
  is within 2 levels of 255 of `(1 − a)·without + a·full`, with `a` the frame's
  opacity for that cue. Recorded vacuous if full and without are identical.
- **Draw-on midpoint**: in the 3×3 neighbourhood of the reported `outside` point,
  composed is within 2 levels of without, and full differs from without by more
  than 2 levels somewhere (the stroke would be there when complete); in the
  neighbourhood of the `inside` point, composed differs from without by more
  than 2 levels somewhere (part of the stroke is there). So the midpoint shows
  part of the stroke and not the rest.
- **Entrance start**: composed at `from` equals without exactly for a fade (the
  first frame shows nothing of the mark); for a draw-on on a ring likewise; for a
  draw-on on an arrow with text, composed differs from without only inside the
  reported text box.
- **Entrance end and exit start**: composed equals full exactly (the entrance
  never changes where the mark ends up; the exit starts from the mark as drawn).
- **Replay**: the existing exact replay check is unchanged; in addition, the
  entrance's midpoint is posed, then another instant, then the midpoint again,
  and the two captures of the midpoint must be identical.

A failure keeps `entrance-<shot>-<index>-<check>-{composed,full,without}.png` in
`preview/` and names the shot, annotation, check and time, e.g.
`Annotation fade does not blend as its easing predicts: pawls #0 leave at 45.07 s (largest difference 9 levels); inspect preview/entrance-pawls-0-leave-{composed,full,without}.png`.
The report gains `entranceChecks: [{shotId, index, phase, kind, time, opacity,
drawn, largestDifference, vacuous}]`.

These checks prove what is drawn and that it replays. Whether a ring reads well,
whether a draw-on is too quick, and whether a fade is soft enough are the
pilot's review on the stills and the demo clip.

### D9. What is left out, and what each would mean

Each is a small addition once a named shot asks for it; none is built now.

- **`box`**: the rectangle grown by `P`, stroked in the accent; a draw-on from
  its top-left corner clockwise. No shot asks for a rectangular mark rather than
  a ring; the drafts' "frame both pawls" is camera framing, and a layer holding
  both pawls already gets one ring (D2).
- **Fixed-place shapes** (a ring, box or line at `place` in safe-area units with
  a size in the same units): they would be truthful only while the camera and
  the thing marked both hold still, and every mark the evidence asks for is on a
  part, two of them under a moving camera. They would need their own refusals
  (size and place inside the safe area, at `check`).
- **`line`**: a stroke between two places or two targets. No shot asks; tracing
  a rope route is the model's rope, lifted with `highlight`.
- **Rings on a world `point`**: would need a size, since a point has no extent.
  The kerf the draft names is a part (`Uncut wood at the kerf`).
- **`scale` entrance**: the mark grown about its anchor (the arrow's tip, the
  label's anchor, the ring's centre) from 0 to 1. No shot asks, and a growing
  text plate passes through unreadable sizes that would need their own frame
  refusals.
- **Draw-off exits** (a stroke withdrawn): no shot asks; the restaged `pawls`
  shot fades its first ring as the second draws on.

### D10. Format, closed list, viewer, frame cache

- The new fields exist only in 0.4 (D7). The 0.4 annotation field list, closed
  in every format already, becomes `from, to, kind, part, point, text, place,
  offset, padding, enter, leave`; `enter` and `leave` each accept
  `kind, duration, ease`. No shot field is added, so the shot list is unchanged.
- 0.2 and 0.3 frames and pixels are untouched: the new code paths are reached
  only by cues declaring the new fields, which only 0.4 accepts.
- Viewer: unchanged. A ring is an annotation, so an episode using one needs
  Viewer API 28 for `annotations (shot <id>)` exactly as today; entrances add
  nothing.
- Frame cache: the render identity already hashes `timeline.mjs`,
  `src/easing.mjs` and the served page (`film.js`); a new Node module on the
  frame path, if the implementation adds one, is added to it.

## Risks / Trade-offs

- **Exact pixel proofs of group opacity and dashes.** D8's fade proof relies on
  the whole mark compositing as one layer; if Chromium blends a group's elements
  separately, the proof fails at the shaft-head seam. The implementer stops and
  brings the finding back rather than widening the tolerance, as
  `shot-transitions` requires of its proofs.
- **The ellipse can be large.** For a part seen along a diagonal, the
  rectangle is much larger than the part and the ring larger still; the frame
  refusal catches a ring that leaves the frame, but not one that is merely too
  big to read as pointing at the part. Review the stills; a smaller layer or a
  different view is the remedy.
- **The ring follows the rectangle, not the silhouette.** As a part turns, its
  rectangle changes shape and the ring breathes with it. For the pawls this is
  small; for a turning crank it may show. Review in motion.
- **A strict "wholly on screen" rule** stops a render when a ringed part brushes
  the stage edge, where an arrow would still pass. That is the truthful rule for
  a mark that claims to enclose the part; preview samples every cue's quarters,
  so most failures surface there.
- **Two spellings of a cue's fade in 0.4** if pictures keep `fadeIn`/`fadeOut`
  (Open Questions).

## Migration Plan

Additive and opt-in by format 0.4 and the new fields. Every existing episode,
including every Leonardo episode and the 0.3 demos, parses and renders with
identical frames and pixels. Reverting the tool commit makes an episode that
uses rings or entrances refused (unknown kind or annotation field), never
rendered without them.

## Open Questions

- **One spelling for a cue's fade.** This change ratifies
  `enter`/`leave: {kind, duration, ease}` for annotations, and `text-animation`
  adopts it for titles. `stills-and-clips` (ratified, applied later) spells a
  picture's fade `fadeIn`/`fadeOut: {duration, ease}`, the spelling
  `shot-transitions` uses for the film's head and tail. The film's head and tail
  are not cues, but a picture is: the orchestrator may want pictures to take
  `enter`/`leave: {kind: fade, ...}` so that 0.4 has one spelling for a cue's
  fade, keeping `fadeIn`/`fadeOut` for the film's head and tail only. This change
  does not touch pictures.
- **Message wording for the shared shape.** `text-animation` wrote
  `Unknown fade field` for its `enter`/`leave`; this change writes
  `Unknown entrance field` / `Unknown exit field`. One wording is better; the
  orchestrator picks.
- **The arrow's look.** The pilot found the present arrow plain (a thin shaft and
  a small head). Its restyle is not this change's to make; it would be a separate
  small change, and rings take the shaft's width and colour, so they would follow
  it.
- **Ring defaults.** The ellipse through the grown rectangle's corners, the
  default padding of 0.01 safe-area widths and the start of a draw-on at the top,
  clockwise, are proposals for the pilot's review on the demo.
- **`box`, fixed places, `line`, `scale`** (D9): left out for lack of a shot. The
  pilot may name one at ratification; the semantics are written above.

## Ratification (29 September 2026)

Ratified by the orchestrating agent as the campaign's review gate, under the
pilot's delegation, with these resolutions:

- **One spelling for a cue's fade across 0.4.** `enter`/`leave: {kind, duration,
  ease?}` is the spelling for every cue that arrives or leaves: annotations
  (here), titles (`text-animation`) and pictures (`stills-and-clips`, whose
  `fadeIn`/`fadeOut` on a picture are replaced by `enter`/`leave: {kind: fade}`
  in its own Ratification section). `fadeIn`/`fadeOut` remain only for the
  film's head and tail (`shot-transitions`).
- **Message wording.** `Unknown entrance field: …` and `Unknown exit field: …`
  everywhere; `text-animation` adopts them.
- **Scope stands as cut** (D9): ring only, fade and draw-on entrances, fade
  exits. The roadmap's boxes, lines, fixed places and scale entrances wait for a
  shot; the pilot may name one. The arrow's look is untouched (a separate small
  change if the pilot asks).
- **Order.** Applied after `shot-transitions`, before `text-animation` and
  `stills-and-clips`, as the campaign note orders.
- **Ring defaults** (ellipse through the grown rectangle's corners, padding
  0.01, draw-on from the top clockwise) stand for the pilot's review on the demo.
