# Episode source contract — drafts 0.2, 0.3 and 0.4

Status: 0.2 is implemented and used by every Leonardo episode; 0.3 is a draft
that adds cues needing Viewer API 28 (see "Format 0.3" below); 0.4 is a draft
that adds named easing of camera moves and model time, transitions between
shots and fades at the film's head and tail, rings around parts and
entrances and exits for every annotation, and closes the field lists of
shots and keys (see "Format 0.4", "Easing", "Joining shots", "Rings" and
"Entrances and exits" below). All three remain provisional formats.
The user reads and edits the same YAML that the production tool consumes.
No executable episode code, imports, expressions or generated screenplay copy.

## Read the screenplay first

`videos/<episode-id>/episode.yaml` is the entry point. Its `format` is
`machinome-video-draft/0.2`, `machinome-video-draft/0.3` or
`machinome-video-draft/0.4`. It contains `id`, `title`, `status`, `learningGoal`,
the relative `production` settings path, and ordered `shots`.

Each shot contains its spoken narration and a plain-language visual direction.
Use folded paragraphs (`>-`) for speech and directions, literal blocks (`|-`)
for multiline on-screen text, and comments to mark readable time ranges.
The numeric timing fields are authoritative; comments are reading aids.

```yaml
format: machinome-video-draft/0.2
id: example
title: One wheel, two jobs
status: rehearsal-source-only
learningGoal: Explain how the carriage feed is timed.
production: production.yaml

shots:
  # 0:00–0:08 — The question
  - id: hook
    start: 0
    end: 8
    narration: >-
      A waterwheel can move a saw. But how does it feed the log forward
      at just the right moment?
    direction: >-
      Hold a close view of the moving blade and timber.
    simulation: {from: 8, to: 16}
    camera:
      - {at: 0, preset: saw}
    hiddenLayers: []
    overlays:
      - {from: 0, to: 8, text: "Who moves the log?", position: top}
    evidence: [reconstruction]
```

The snippet illustrates the screenplay; a complete episode also supplies its
production file and the named camera and evidence definitions.

`direction` is editorial intent for framing and review, not a prompt the renderer
may reinterpret on every run. Camera, visibility, time and overlay fields encode
the requested actions. If the prose and cues disagree, revise them together.
Narration lives only inside each shot; there is no separate script to keep in sync.

## Production settings

`production.yaml` carries settings that do not need to interrupt reading:

- `output`: `width`, `height`, `fps`, `durationSeconds`.
- `model`: relative `manifest`, `expectedDurationSeconds`, `timeMode`,
  `sourceRevision` and `readiness`. A null revision marks unpinned source.
- `audio`: provider/model/voice, direction, pronunciation notes and timing notes;
  optional `voiceSettings` passed to ElevenLabs and `replacements` mapping
  written terms to spoken aliases. Captions restore the written spelling.
- `series`: optional short series label for the top corner; defaults to the title.
- `sourceCode`: optional named Python excerpts, described below.
- `stills` and `clips` (format 0.4): named pictures with a project-relative
  `file`, required `credit` and `rights` keys (non-empty text or `null`), and
  optional raster `upscale` allowance (default 1). See “Showing stills and
  clips”. Older episode formats ignore these maps.
- `style`: background, foreground, accent, font and safe inset.
  Background, foreground, accent and font are applied by the current renderer;
  safe inset is an editorial hint for its fixed layout,
  not independently implemented layout controls.
- `cameras`: named world-space `position`, `target`, `up` and `fov`.
- `layers`: named lists of root-relative assembly paths. Each path is a list
  of exact sibling names, excluding the document root's name.
- `evidence`: readable names mapped to relative project files, referenced by shots.
- `credits`: creator, copyright, license, license file, historical references.
- `release`: public simulation/source URLs, description template and publish flag.

All file paths resolve relative to the YAML file that contains them. Parse as
safe YAML 1.2 data with unique string keys. Refuse duplicate keys, custom tags,
aliases, anchors and merge keys; the authoring format needs no executable types
or implicit inheritance. Quote colors and text containing `: ` or ` #`.
Use numbers for seconds, `true`/`false` for booleans and `null` for unknown values.
Null release URLs are valid in a draft and block a release bundle. Never
substitute localhost or an intended remote for a verified public address.

## Timing and rendering semantics

All times are seconds. Each shot has a unique `id`. `start` and `end` use the
video clock and cover `[0, output.durationSeconds)` contiguously, without overlap.
The final frame is at `(frameCount - 1) / fps`, not at the duration.

`simulation: {from, to}` maps the shot's video interval linearly to model seconds.
Optional `keyframes: [{at, seconds}, ...]` maps explicit shot-local video instants
to model seconds, interpolating linearly between them; in format 0.4 a key may
add `ease` to shape the segment that ends at it (see "Easing"). The first key is at zero
and matches `from`; the last is at the shot duration and matches `to`. Video
times increase strictly; model times never decrease. The sawmill uses these
keys to align the return stroke and cut/advance beats with measured speech.
Equal endpoints hold a pose. For the first episode, `timeMode: normalized-loop`
means the viewer gets `simulationSeconds / expectedDurationSeconds`. The
adapter must check the document's declared duration and disable autonomous
playback. Do not pass seconds to a normalized time setter or wrap to zero.
Machines with memory need a future replay/checkpoint contract; this format
does not pretend their state is an arbitrary time coordinate.

`camera` keys use shot-local `at` seconds. One key holds the view; multiple
keys interpolate position and target with smoothstep easing (the curve named
`smooth`); in format 0.4 a key may add `ease` to name another curve for the
move that ends at it (see "Easing"). The first is at
zero, keys increase strictly, and the last cannot exceed the shot's duration.
Hold the last key to the end. In format 0.2 every key of a shot must share one
up and field of view. From format 0.3 they may differ (see "Changing the lens and
the up direction" below).
In formats 0.2 and 0.3 every shot boundary is a hard cut. In format 0.4 a
boundary is a hard cut unless the shot that begins there declares a
`transition` (a fade, dissolve, wipe or slide; see "Joining shots"). No
automatic framing is implied.

`hiddenLayers` describes the complete shot visibility state: start with all
parts visible, then hide those layers. Do not accumulate state from earlier shots.
In format 0.3 a `highlight` (below) composes with it: hidden parts stay hidden
while the others are kept, dimmed or ghosted, and highlighting a hidden part is refused.

Overlay `from`/`to` values are shot-local, half-open intervals. Positions are
`top`, `lower-third`, or `center`, plus `title` in format 0.4. Overlays are screen labels, fixed on the frame;
in format 0.3, `annotations` (below) point at parts and follow them. Narration captions are external SRT files, never film pixels.
Framing and text placement need visual review at the final aspect ratio.

Narration timing remains an editorial target until speech is generated and
measured. `speechOffset` optionally sets a shot-local audio start (default 0.2 s).
Align speech and captions, then revise shot timing and affected cues
together. Never truncate narration or silently stretch it to fit. Silent tails
are allowed. Mechanical cut/advance cues must stay tied to model time.

`audio.outputFormat` supports `mp3_44100_128` (legacy default) and `pcm_24000`
(lossless mono 16-bit PCM, cached in WAV). `audio.model: eleven_v3` uses v3
defaults with stability 0.5 and omits previous/next-text stitching fields. Select
a voice ID explicitly. `audio.direction` remains editorial guidance, not a
provider instruction; punctuation, the chosen voice and voiceSettings influence
delivery. Plain narration is also the subtitle transcript; inline performance
tags are not an implemented separate direction channel.

Speech offsets preserve the complete cached clip. Leave a deliberate preroll
and enough tail, especially for a scene's opening. Mixing has no onset gate or
fade-in. This cannot restore a syllable already absent from provider audio:
review the raw clip and final mix and regenerate/revise if needed. Continuous
paragraphs avoid an independent synthesis restart at every sentence.

## Actual Python beside the animation

In production.yaml, select source lines rather than copying code into YAML:

```yaml
sourceCode:
  drive:
    file: ../../models/hydraulic_sawmill/model.py
    lines: [200, 206]
```

The inclusive, one-based range must exist in a `.py` file inside the consuming
Git repository. The entire file must match `model.sourceRevision`, a full commit
hash matching the export. Missing, modified or external files are refused.
Only common leading spaces are removed; source is never evaluated. File path,
revision, range, dedent and file/excerpt SHA-256 values enter the build manifest.

Add a code cue to the shot:

```yaml
code:
  snippet: drive
  typing:
    - {from: 0.8, to: 4.3, throughLine: 203}
    - {from: 6.5, to: 9, throughLine: 205}
    - {from: 11, to: 14, throughLine: 206}
```

Typing uses shot-local video seconds and absolute source line numbers. Each
cue reveals characters from the previous endpoint through that line. Gaps hold
the code already visible. Cues must not overlap, lines must increase, the last
cue must complete the excerpt, and all cues must fit the shot. Align these cues
after generating and measuring speech; automatic semantic matching is not
claimed. This is an editorial reveal, not a live coding session.

Code shots use a fixed split layout: highlighted Python left, actual 3D right.
Shots without code keep the full model stage. Select a short excerpt and inspect
the final aspect ratio; overflowing panels fail capture. Typing, cursor and
syntax colors follow video time, so seeking/resuming preserves exact frames.
Format 0.4 may also light source identifiers at measured speech onsets; see
"Source words lit as they are spoken" below.

## Format 0.3 and the viewer it needs

`machinome-video-draft/0.3` accepts everything 0.2 does, with the same meaning,
plus the cues below. They are accepted only in 0.3 and later: a 0.2 episode carrying one is
refused and asked to change its format, never rendered with the cue silently
missing. A 0.2 episode keeps its exact behaviour and any Viewer API 21 or later.

An episode that uses a 0.3 cue needs Viewer API 28 (the machinome-viewer source
that adds `partOnScreen`, `project`, `highlight` and `setView` up/field of view;
not yet a published release). `check` reads the `viewer API <n>` banner of the
selected bundle and refuses an older or unmarked one; `preview` and `render`
refuse on mount against the running viewer's `apiVersion`, before capturing:

    This episode needs Viewer API 28 for annotations (shot pawls); the selected
    viewer declares API 27. Select a newer machinome-viewer bundle with --viewer.

Episodes that use none of them are not held to API 28, and `check` does not read
the bundle for them.

## Pointing at parts

A 0.3 shot may carry `annotations`: timed arrows and labels aimed at a part or a
world point, which follow it on screen every frame.

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

- `from`, `to`: shot-local seconds, half-open like overlays, `0 <= from < to <= duration`.
- `kind`: `arrow` or `label`; in format 0.4 also `ring` (see "Rings" below).
  A callout (words on a plate with a leader to the part they name) is an
  `arrow` with `text`; there is no separate `callout` kind.
- The target is exactly one of `part` and `point`. `part` is a production layer
  name (a string) or one root-relative assembly path (a list, spelled as a
  `layers` path is); a layer holding several paths is one target, its bounds the
  union of theirs. `point: [x, y, z]` is a fixed world point in the model's units
  and frame, the frame the named cameras use.
- `text`: required for a label; optional for an arrow (a bare pointer).
- `place` (arrow, required): `[x, y]` in safe-area units where the arrow's text
  and tail sit, fixed on screen. `[0, 0]` is the top-left and `[1, 1]` the
  bottom-right of the safe area: the frame inset on every side by
  `style.safeInsetFraction`.
- `offset` (label, optional, default `[0, 0]`): `[dx, dy]` in safe-area units from
  the target's anchor to the label's centre, each within `[-1, 1]`.

An episode using annotations must declare `style.safeInsetFraction` in `[0, 0.5)`;
this is its first operational use, and no default is invented. Other fields in
an annotation are refused, so a misspelled `offset` cannot silently vanish.

The anchor of a part is the centre of its on-screen bounding rectangle (the
union of rectangles for a multi-path layer), as the viewer reports it for the
posed frame; the anchor of a `point` is its projection. An arrow's shaft runs
from the edge of its text nearest the anchor, and its tip is drawn at the
anchor. For a slender diagonal part the centre of its rectangle can lie beside
the part; choose a better part or layer, or a `point`, and review the stills.
Arrows are drawn in `style.accent`, text in `style.foreground` on a
`style.background` plate, sized to the frame width, above the model and below
the overlays. Annotations never change the model, the camera or visibility.

`check` refuses, naming the shot: an unknown kind or field; both or neither of
`part` and `point`; an unknown layer; an assembly path the export does not
contain; a non-finite point; times outside the shot or not increasing; an arrow
without `place` or with `place` outside `[0, 1]`; a label without text; `offset`
outside `[-1, 1]`; `place` on a label or `offset` on an arrow; a target equal to
or inside a path the same shot hides; a missing safe inset; annotations in 0.2.

`preview` and `render` refuse any frame on which an active annotation's anchor
is missing or outside the model stage, or its text leaves the frame, naming the
shot, the annotation's index and text, and the video time:
`Annotation target is not on screen: pawls #1 'Holds it' at 44.87 s`. A moving
part that leaves the view therefore stops production; shorten the cue or
reframe. `preview` samples every annotation at its start, quarters, midpoint and
last frame, and its report records each drawn anchor, part rectangle and text box.

### Rings

In format 0.4 an annotation of kind `ring` singles out a part without words: an
ellipse drawn around it, following it every frame as it moves and as the camera
moves. The *Revolutions* `pawls` shot, restaged, rings the pawl each caption is
about:

```yaml
# format machinome-video-draft/0.4
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
        enter: {kind: draw, duration: 0.8}      # draws itself round the pawl
        leave: {kind: fade, duration: 0.4}      # fades as the next ring begins
      - from: 5.366
        to: 10
        kind: ring
        part: [Feed mechanism, Holding pawl]
        padding: 0.02
        enter: {kind: draw, duration: 0.8}
```

- **Target**: `part` only, a production layer name or one assembly path, as for
  an arrow. A layer holding several paths is ringed as one: a layer holding
  both pawls gets one ring around both. `point` is refused (a point has no
  extent to ring).
- **Where it is drawn**: take the part's on-screen rectangle, the same one (or
  union of rectangles) whose centre places an arrow's tip, with centre
  `(cx, cy)`, width `w` and height `h`. Grow it by `P` on every side, where `P`
  is `padding` times the safe area's width in pixels. The ring is the ellipse
  through the four corners of the grown rectangle: centred on `(cx, cy)`, with
  semi-axes `rx = √2·(w/2 + P)` and `ry = √2·(h/2 + P)`. So it always encloses
  the whole rectangle, stays clear of a slender diagonal part whose ends reach
  the rectangle's corners, and takes the part's proportions (a long rope section
  gets a long ring).
- **`padding`** (optional, ring only): a number in `[0, 0.25]`, in safe-area
  widths as `place` and `offset` are, the same distance on every side. Default
  `0.01`, about 16 pixels on a 1920-pixel frame with a safe inset of 0.08.
- **Look**: a stroke in `style.accent`, as wide as an arrow's shaft (`0.0024` of
  the frame width), with no fill; drawn above the model and below the overlays,
  in annotation order, like every annotation.
- A ring carries no words: `text`, `place` and `offset` are refused on it. Put a
  `label` or an `arrow` beside it in the same list when words are wanted.

As a part turns, its rectangle changes shape and the ring breathes with it; for
a part seen along a diagonal the rectangle, and so the ring, is much larger than
the part. Review the stills; a smaller layer or another view is the remedy.

`preview` and `render` refuse, at every posed frame of the cue (its entrance and
exit included, and the frames a transition continues it into), in addition to
the anchor check every annotation has: a ring whose part's rectangle is not
wholly inside the model stage, `Ring target is not wholly on screen: pawls #0
(ring) at 44.87 s` (the ring would enclose what the audience cannot see; shorten
the cue or reframe); and a ring whose ellipse (`cx ± rx`, `cy ± ry`) leaves the
frame, `Ring leaves the frame: pawls #0 (ring) at 44.87 s` (reduce the padding
or reframe). A ring is never clipped or dropped silently.

## Entrances and exits

In format 0.4 every annotation (arrow, label or ring) may arrive and leave
instead of appearing and vanishing in one frame. Two optional fields do this,
each a short mapping on the annotation:

- `enter: {kind, duration, ease}`: how the mark arrives. `kind` is `fade` (the
  whole mark comes up from nothing) or `draw` (its stroke draws itself on).
- `leave: {kind, duration, ease}`: how it goes. `kind` is `fade`, the only
  departure.
- `duration`: video seconds, at least two frames at `output.fps`. Required.
- `ease`: optional, one of the five easing names (see "Easing"); default
  `smooth`.

The *demo-feed-mechanism* `name-the-pawls` shot, restaged:

```yaml
# format machinome-video-draft/0.4
    annotations:
      - {from: 0.2, to: 9, kind: arrow, part: [Feed mechanism, Driving pawl],
         place: [0.1, 0.3], text: Driving pawl, enter: {kind: draw, duration: 0.8, ease: out}}
      - {from: 1.9, to: 9, kind: label, part: [Feed mechanism, Holding pawl],
         offset: [0.12, -0.03], text: Holding pawl, enter: {kind: fade, duration: 0.5}}
```

The words "Driving pawl" are there from 0.2 s and the arrow grows from them to
the pawl, arriving at rest at 1.0 s; the label fades in between 1.9 s and 2.4 s.

### Where they sit in time

`from` and `to` keep their meaning. The entrance occupies the first `duration`
seconds of the cue, from `from`; the exit the last `duration` seconds, up to
`to`, so a mark that fades out is gone at `to` exactly as one without an exit
is. With `u` the progress through the entrance or exit, from 0 to 1, eased by
its curve:

- a **fade** shows the whole mark (stroke, head, text plate and words) at an
  opacity rising from 0 to 1 through an entrance and falling from 1 to 0
  through an exit. Nothing moves or changes size.
- a **draw**-on on a **ring** reveals the ellipse's stroke along its length from
  its top point, clockwise on screen, to the drawn fraction of its perimeter.
- a **draw**-on on an **arrow** shows the words and their plate in full from
  `from` (the stroke leaves from them), and reveals the shaft and then the head
  from the words towards the tip; an arrow without text reveals the same way
  from its tail.
- a **label** has no stroke, so `draw` is refused on it; enter it with `fade`.

An entrance's first frame shows nothing of a faded mark, and none of a drawn
stroke. An entrance or exit never changes where the mark is: from the end of
the entrance, if that instant is still inside the cue, and at the start of the
exit, the mark is drawn exactly as it is without one. Throughout the cue it
keeps following its part (a ring's ellipse and an arrow's tip are recomputed
from the part every frame).

Into a transition (see "Joining shots"), a cue with a `leave` has left by its
`to`, so if it runs to the shot's end it is not continued into the outgoing
picture; a cue without `leave` stays, as every cue that runs to the end does,
fully drawn.

### Refusals

`check`, `preview` and `render` refuse, naming the shot and the annotation:

- `ring`, `padding`, `enter` or `leave` in a 0.3 episode, which is asked to
  change its format, never rendered without them:
  `Rings, entrances and exits need format machinome-video-draft/0.4: shot pawls (kind: ring in annotation #0)`
  (0.2 keeps `Annotations need format machinome-video-draft/0.3`);
- a kind other than `arrow`, `label` or `ring` (`kind must be arrow, label or
  ring`, so `kind: callout` is refused too);
- a ring with `point` (`a ring is drawn around a part; give part, not point`),
  or with `text`, `place` or `offset` (`a ring carries no text or place; add a
  label or an arrow beside it`); `padding` outside `[0, 0.25]` or on an arrow or
  a label (`padding belongs to a ring`);
- `enter` or `leave` that is not a mapping; an unknown field in either
  (`Unknown entrance field: durration (annotation #0 in shot pawls)`,
  `Unknown exit field: eas (annotation #0 in shot pawls)`);
- an entrance kind other than `fade` or `draw`, an exit kind other than `fade`;
  `draw` on a label (`a label has no stroke to draw; enter with fade`); an
  easing other than the five (`Unknown easing: bounce; use linear, smooth, in,
  out or in-out (entrance of annotation #0 in shot pawls)`);
- a duration that is missing, not finite or shorter than two frames; an
  entrance or exit longer than the cue (`the 1.2 s entrance is longer than the
  cue (1 s)`); an entrance and an exit that together are longer than the cue
  (`Entrance and exit overlap in annotation #0 in shot pawls: 0.8 s in and
  0.6 s out exceed its 1.2 s`);
- as for every annotation: an unknown layer or assembly path, a target the same
  shot hides, a missing safe inset and times outside the shot.

A frame's target checks (anchor on the stage, text in the frame, and a ring's
two checks) apply for the whole cue, entrance and exit included: a mark fading
in is still a claim about where the part is.

### What preview proves

For each annotation with an entrance or exit, `preview` adds stills at the
entrance's first frame, midpoint and end, and at the exit's start, midpoint and
last frame before `to`, beside the annotation's usual samples. It then poses
each check's instant three ways, as authored ("composed"), with that one cue's
`enter` and `leave` removed ("full") and with that one cue removed ("without"),
and compares the decoded pixels:

If an entrance lasts the whole cue, its end is exactly the exclusive `to`
boundary. There is no active mark to sample there; the report records
`enter-end` as skipped with `cue ends at this exclusive boundary` and checks
the entrance's start and midpoint.

- at a **fade**'s midpoint, entrance or exit, every channel of every pixel of
  composed is within 2 levels of 255 of the blend `(1 − a)·without + a·full`,
  `a` being the frame's opacity for the cue;
- at a **draw**-on's midpoint, around the point halfway along the undrawn part
  of the stroke composed equals without (within 2 levels) while full does not,
  and around the point halfway along the drawn part composed differs from
  without: the midpoint shows part of the stroke and not the rest;
- at the entrance's first frame composed equals without exactly (for a draw-on
  arrow with words, everywhere outside its text box);
- at the entrance's end and at the exit's start composed equals full exactly;
- posing the entrance's midpoint (or, without an entrance, the exit's), another
  instant and the midpoint again gives identical pixels.

`report.json` records `entranceChecks`, one per check: the shot, the
annotation's index, the phase (`enter-start`, `enter`, `enter-end`,
`leave-start`, `leave`), the entrance or exit kind, the time, the frame's
opacity and drawn fraction, the largest difference found and whether full and
without were identical (`vacuous`: then the check shows nothing). A failed proof
stops preview, naming the shot, the annotation, the check and the time, and
keeps `entrance-<shot>-<index>-<phase>-{composed,full,without}.png` in
`preview/`:
`Annotation fade does not blend as its easing predicts: pawls #0 leave at 45.07 s (largest difference 9 levels); inspect preview/entrance-pawls-0-leave-{composed,full,without}.png`.
Whether a ring reads well, whether a draw-on is too quick and whether a fade is
soft enough are for review on the stills and in motion.

For a partly faded mark the film blends same-instant captures with that mark
fully drawn and absent. This preserves the exact opaque text pixels in the
blend, even where the browser changes text antialiasing under element opacity.
When several marks fade together, it blends every full/absent combination in
annotation order; `n` such marks require `2^n` captures per picture.

## Changing the lens and the up direction

In format 0.3 a shot may key between named cameras whose `fov` or `up` differ;
there is no new screenplay field, because the presets in `production.yaml`
already carry both.

```yaml
# production.yaml
cameras:
  pawls:       {position: [145, 410, 400], target: [135, 0, 332], up: [0, 0, 1], fov: 37}
  pawls-tight: {position: [145, 410, 400], target: [135, 0, 332], up: [0, 0, 1], fov: 20}
# episode.yaml, format machinome-video-draft/0.3
    camera:
      - {at: 0, preset: pawls}
      - {at: 4, preset: pawls-tight}   # hold position, narrow the view onto the pawls
```

The field of view eases with the same easing as position and target and
holds after the last key. In a shot whose keys share one `up`, it is used
exactly as written. In a shot whose `up` changes, the two keys' directions are
mixed with the same easing and normalized, so up is always a unit vector (this
is not constant angular speed; it follows the easing the position already has).
Episodes whose cameras all share one up and field of view produce the same
frames as before, in either format.

`check` refuses, naming the shot: in 0.2, keys of one shot that change field of
view or up; from 0.3, adjacent keys whose up directions are nearly opposite (add
an intermediate preset), and, in a shot whose up changes, any output frame whose
up lies within about half a degree of the viewing direction, with its time.

Any episode whose cameras differ in `fov` or `up` direction from the first
camera it uses, within a shot or across a cut, in either format, needs Viewer
API 28 and is refused against an older viewer; before API 28 a later shot's lens
could never be applied. From API 28 `preview` and `render` refuse a frame whose
viewer does not report back the requested field of view and up direction, and
`preview` proves each change by projecting two world points at the keys where it
starts and ends: a small offset beside the target must measure
`(H/2)·s/(d·tan(fov/2))` pixels within 2 %, and for an up change a point above
the target must appear above it. Whether the zoom or roll reads well in motion
is for review.

## Drawing attention to a part

A 0.3 shot may carry `highlight` cues: for a timed interval, the named parts are
tinted and every other part is kept, dimmed or ghosted (still drawn, translucent,
so what is behind it shows through). Use it to show a mechanism inside its
housing instead of hiding the housing.

```yaml
    highlight:
      - from: 0
        to: 5.366
        parts: [[Feed mechanism, Driving pawl], [Feed mechanism, Ratchet and slender winding axle]]
        others: ghost
      - {from: 5.366, to: 10, parts: [[Feed mechanism, Holding pawl]], others: dim, color: "#237c86"}
```

- `from`, `to`: shot-local, half-open, `0 <= from < to <= duration`. Cues in one
  shot must not overlap; gaps show the model plainly.
- `parts`: a non-empty list. A string entry is a production layer name; a list
  entry is one root-relative assembly path. So `parts: [saw, feed]` is two layers
  and `parts: [[Saw mechanism, Connecting rod]]` is one path. A bare path written
  without the outer list, `parts: [Saw mechanism, Connecting rod]`, reads as two
  layer names and is refused as unknown layers, never guessed.
- `others`: `keep`, `dim` or `ghost`; default `keep`.
- `color`: optional quoted `"#rrggbb"`; default `style.accent`, which must then be
  a quoted `#rrggbb` too. Both choices are always passed to the viewer
  explicitly, so the viewer's own defaults never decide a film.

A cue ends at its `to` and at the shot's cut; every material is restored exactly,
and each frame's look depends only on its video time. The viewer tints only parts
that declare a colour of their own; an undeclared-colour part is neither tinted
nor dimmed, though `ghost` still makes it translucent. Review the stills.

`check` refuses, naming the shot: empty parts, an unknown layer, a path the export
does not contain, an `others` outside the three words, a colour that is not
`#rrggbb`, unknown fields, times outside the shot, overlapping cues, a
highlighted part equal to or inside a path the same shot hides, and `highlight`
in a 0.2 episode. A highlighted ancestor of a hidden part is allowed; the hidden
part stays hidden, and `ghost` does not bring it back.

`preview` checks each cue at its midpoint: the same instant with the cue removed,
with it, without it and with it again. The cue must change the pixels, the two
captures without it must match exactly (restore is complete), and the two with
it must match (it re-applies identically). A failure keeps its before/after
images in `preview/`. Whether a ghosted frame reads as translucent context is a
judgement on the stills, not an automated claim.

## Format 0.4

`machinome-video-draft/0.4` accepts everything 0.3 does, with the same meaning:
a 0.4 shot may annotate, highlight and change lens exactly as a 0.3 shot does,
and a 0.4 episode that neither eases nor joins shots produces the same visible
result it would produce declared 0.3 (its frame data also carries null
`transition` and `picture`). It adds `ease` on camera keys and model keyframes,
`transition`, `fadeIn` and `fadeOut` on shots (see "Joining shots"), `pictures`
on shots (see “Showing stills and clips”), text
`reveal`, titles and source emphasis (see "Text animation"), and, on
annotations, the kind `ring` with its `padding` and `enter` and `leave` on
every kind (see "Rings" and "Entrances and exits"). A 0.4 annotation that uses
none of `padding`, `enter` or `leave` and is an arrow or label is drawn exactly
as in 0.3.

- `ease` is accepted only in 0.4. A 0.2 or 0.3 episode carrying one is refused
  and asked to change its format, never rendered with its curves silently
  replaced by the default:
  `Easing needs format machinome-video-draft/0.4: shot genome`. Likewise a
  ring, `padding`, `enter` or `leave` in a 0.3 episode:
  `Rings, entrances and exits need format machinome-video-draft/0.4: shot pawls (kind: ring in annotation #0)`.
- In 0.4 the field lists are closed. A shot accepts `id`, `start`, `end`,
  `speechOffset`, `narration`, `direction`, `simulation`, `camera`,
  `hiddenLayers`, `overlays`, `evidence`, `code`, `annotations`,
  `highlight`, `pictures`, `transition`, `fadeIn` and `fadeOut`; its `simulation` accepts
  `from`, `to` and `keyframes`; a model keyframe `at`, `seconds` and `ease`; a
  camera key `at`, `preset` and `ease`; a `transition` `kind`, `duration`,
  `ease`, `direction` and `color`; a `fadeIn` or `fadeOut` `duration`, `ease`
  and `color`. An annotation, whose list was closed in every format already,
  accepts `from`, `to`, `kind`, `part`, `point`, `text`, `place`, `offset`,
  `padding`, `enter` and `leave`; an `enter` or `leave` accepts `kind`,
  `duration` and `ease`. An overlay accepts `from`, `to`, `text`, `position`,
  `reveal`, `subtitle`, `enter` and `leave`; `reveal` accepts `timing` and
  `phrase` when spoken, or `timing`, `duration` and `ease` when even. A title's
  `enter` or `leave` accepts `kind`, `duration` and `ease`. `code` accepts
  `snippet`, `typing` and `emphasis`; a typing cue accepts `from`, `to` and
  `throughLine`; an emphasis cue accepts `line`, `phrase`, `words` and `hold`.
  A picture accepts `from`, `to`, `still`, `clip`, `area`, `fit`, `enter`,
  `leave`, `view` and `inPoint`; a view key accepts `at`, `center`, `zoom` and
  `ease`; a picture entrance or exit accepts `kind`, `duration` and `ease`.
  A still or clip entry accepts `file`, `credit`, `rights` and `upscale`.
  Anything else is refused, naming the field and the shot:
  `Unknown camera key field: eas (key #1 in shot genome)`,
  `Unknown model keyframe field: speed (keyframe #1 in shot genome)`,
  `Unknown simulation field: ease (shot genome)`,
  `Unknown shot field: transiton (shot genome)`. So a misspelled field, or a
  field that a later build of Videomaker defines and this one does not, is
  never silently dropped. 0.2 and 0.3 episodes keep ignoring unknown fields.
- Easing and transitions need no newer viewer: easing changes only the
  numbers the film page already sends, and a transition poses the viewer as
  every frame does. A 0.4 episode needs Viewer API 28 only for the 0.3 cues it
  uses (annotations, highlights, a change of lens or up); one that only eases
  or joins shots or only animates text or shows pictures runs on Viewer API 21 or later. A ring is an annotation, so it
  needs Viewer API 28 as every annotation does; entrances and exits add
  nothing.

## Easing

A curve shapes how a keyed value travels from one key to the next. There are
five, and only these names are accepted:

- `linear`: constant speed from key to key. The default for model keyframes.
- `smooth`: starts from rest, is quickest in the middle and arrives at rest. The
  default for camera keys, and the curve camera moves have always used.
- `in`: starts from rest and gathers speed, arriving at full speed.
- `out`: leaves at full speed and slows to rest on the key.
- `in-out`: starts and arrives at rest like `smooth`, but lingers visibly longer
  at each end and crosses the middle faster.

`ease` on a key names the curve of the segment that ends at that key: "arrive at
the linkage settling", "reach 461 gently". A key without `ease` takes the
default of its field. The first key of a shot ends no segment, so `ease` there
is refused: `Nothing to ease before the first camera key: shot genome` (and
`... before the first model keyframe: ...`). A hold (two keys with the same
preset or the same seconds) looks the same with any curve.

Every curve starts exactly at the earlier key's value, arrives exactly at the
later key's value, and never reverses or passes beyond either key. The `in`,
`out` and `in-out` curves are cubic: at their fastest they move at three times
the segment's average speed. Where that is too brisk, add a key and shorten the
eased segment.

A camera move that is already travelling at the cut and settles on the linkage
(the *Revolutions* `genome` shot, restaged):

```yaml
# format machinome-video-draft/0.4
    camera:
      - {at: 0, preset: mechanism}
      - {at: 9.615, preset: linkage, ease: out}   # already travelling at the cut; settles on the linkage
```

Position, target, field of view and up all follow the key's curve. A steady
push-in over a whole shot is `ease: linear` on its last key.

A mechanism that leaves a held pose gently, and one that settles into a pause
(the *Revolutions* `machinome` and `genome` shots, restaged):

```yaml
# format machinome-video-draft/0.4
  - id: machinome
    simulation:
      from: 453
      to: 461
      keyframes:
        - {at: 0, seconds: 453}
        - {at: 3.733, seconds: 453}              # held pose while the assembly is restored
        - {at: 14, seconds: 461, ease: in}       # the machine starts gently
  - id: genome
    simulation:
      from: 461
      to: 466.8
      keyframes:
        - {at: 0, seconds: 461}
        - {at: 6.899, seconds: 466.8, ease: out} # settles into the pause on "pause"
        - {at: 12.5, seconds: 466.8}
```

Easing model time changes the speed of playback within a segment, like slow
motion; it is never the machine's own dynamics, and every frame still shows a
real pose of the simulation at some model second. Narration and directions must
not present it as physics (a waterwheel does not brake). Keys stay exact: at
every key's `at` the model is at that key's `seconds`, whatever the curves, so a
beat keyed to a measured word stays on its word; an event inside a segment moves
in video time when the segment's curve changes, so put a key where one must be
exact. Model time never decreases and never passes beyond a segment's keys.
Each segment is eased on its own: `in` after a moving segment first returns the
machine to rest, and `out` into a moving segment arrives at rest, so these
curves read best with a hold on the other side, as in both shots above.

A plain `simulation: {from, to}` span takes no `ease`; write two keyframes with
`ease` on the second. Typing cues, overlays, highlights and speech offsets are
not eased; an annotation's curve names only how its entrance or exit runs (see
"Entrances and exits").

`check` refuses, naming the shot: an easing name other than the five
(`Unknown easing: bounce; use linear, smooth, in, out or in-out (camera key #1
in shot genome)`), including other spellings such as `ease-out` or `Smooth`;
`ease` on a shot's first camera key or first model keyframe; and `ease` in a 0.2
or 0.3 episode.

## Joining shots

In format 0.4 two neighbouring shots can be joined by a fade through a colour,
a dissolve, a wipe or a slide instead of a hard cut, and the film can fade in
at its head and out at its tail. Three shot fields do this; each is short YAML
written on the shot it belongs to:

- `transition`, on any shot but the first: how this shot comes in from the
  shot before it.
- `fadeIn`, on the first shot only: the film fades up from a colour.
- `fadeOut`, on the last shot only: the film fades down to a colour.

A shot without `transition` begins with a hard cut, as before; there is no
`kind: cut`, so a cut has one spelling.

```yaml
# format machinome-video-draft/0.4
shots:
  - id: machine
    start: 0
    end: 6
    fadeIn: {duration: 1.5}                     # up from the paper colour
    ...
  - id: source
    start: 6
    end: 18
    transition: {kind: dissolve, duration: 1}   # from machine
    ...
  - id: mechanism
    start: 18
    end: 26
    transition: {kind: fade, duration: 1.2}     # through the paper colour
    ...
  - id: pawls
    start: 26
    end: 32
    transition: {kind: slide, duration: 0.8, direction: left, ease: in-out}
    ...
  - id: closing
    start: 32
    end: 40
    transition: {kind: wipe, duration: 0.8, direction: right}
    fadeOut: {duration: 2}                      # down to the paper colour
    ...
```

The fields of `transition`:

- `kind`: `fade` (the outgoing picture fades to a colour, then the incoming
  one fades up from it), `dissolve` (the outgoing picture fades away over the
  incoming one), `wipe` (a straight vertical edge travels across the frame,
  the incoming picture behind it) or `slide` (the incoming picture pushes the
  outgoing one out of the frame). Required.
- `duration`: video seconds, at least two frames at `output.fps`. Required.
- `ease`: optional, one of the five easing names (see "Easing"); default
  `smooth`. `linear` gives an even dissolve.
- `direction`: `wipe` and `slide` only, `left` or `right`; default `left`. It
  names the way the motion goes: `left` means the incoming picture enters from
  the right edge and the edge (wipe) or both pictures (slide) travel leftward;
  `right` is the mirror.
- `color`: `fade` only, a quoted `"#rrggbb"`; default `style.background`.

`fadeIn` and `fadeOut` take `duration` (required), `ease` (default `smooth`)
and `color` (default `style.background`), and nothing else.

### Where a transition sits in time

A transition never changes `start` or `end`. It occupies the first `duration`
seconds of the shot that declares it, from its `start`, and that shot's own
timeline runs exactly as it would after a cut: its model time, camera,
overlays, annotations, highlights, code typing and speech offset keep the
times written for them, and are seen through the transition. Narration audio
and captions are untouched, so the incoming shot's narration may start while
its picture is still arriving; with `speechOffset` at its default 0.2 s it
does. `fadeIn` occupies the first `duration` seconds of the film; `fadeOut`
the last `duration` seconds, and it is complete on the film's last frame.

While a transition still shows the outgoing shot past its `end`, that shot
continues rather than freezing:

- its model runs on from its `to` at the rate model time had at its end: the
  last segment's average rate, times the end slope of its easing (`linear` 1,
  `in` 3, and 0 for `smooth`, `out` and `in-out`). A held shot, or one whose
  last segment eases to rest, stays held;
- its camera holds its last key;
- each overlay, annotation or highlight cue that ran to the shot's end stays
  on; every other cue has ended. An annotation keeps following its part on the
  moving model, and is refused if the part leaves the frame; an annotation
  with a `leave` has left by the shot's end and does not stay;
- its code panel shows the completed excerpt, without a cursor;
- its own `hiddenLayers` apply.

The outgoing shot is seen for the whole of a dissolve, wipe or slide, and for
the first half of a fade. The export must hold that far: `check` refuses a
continuation that would ask the model for a second past
`model.expectedDurationSeconds`.

### How each kind draws

With `p` the eased progress, running from 0 on the transition's first frame
(which shows the outgoing picture alone, the frame after its end) to just under
1 on its last, and `W` the frame width in pixels:

- **dissolve**: the outgoing picture lies over the incoming one at opacity
  `1 − p`.
- **wipe**: a hard vertical edge `round(p·W)` pixels in from the side the
  incoming picture enters from; outgoing on one side, incoming on the other.
- **slide**: the outgoing picture moves `round(p·W)` pixels in `direction`
  and the incoming one enters from the opposite edge, butted against it, so
  the frame is always covered.
- **fade**: a plate of the colour over the picture. In the first half the
  picture is the outgoing shot and the plate rises to fully opaque; the
  midpoint is the plain colour; in the second half the picture is the incoming
  shot and the plate falls away. Each half follows the easing. Code and machine
  are never on screen together in a fade.
- **fadeIn**: the plate falls from the plain colour on the film's first frame.
- **fadeOut**: the plate rises to the plain colour on the film's last frame, at
  `end − 1/fps` for the episode's `output.fps` (a quick render at another
  `--fps` may stop that last frame a fraction short of it).

Every kind acts on the picture, not on the film's chrome: the transition is
drawn above the model, annotations, overlays and code panel, and below the
masthead (`MACHINOME` and the series label) and the progress rule, which stay
in place. A slide never pushes the masthead out of frame, and a fade shows the
masthead and progress rule on the colour. A change of layout between a code
shot and a model shot needs nothing special: each picture keeps its own.

The default colour is `style.background`, which must then be a quoted
`"#rrggbb"`. On a paper film a fade to the background reads as the picture
leaving the page; on a dark film it is the conventional fade to black. For
black on a paper film write `color: "#000000"`.

### Refusals

`check`, `preview` and `render` refuse, naming the shot and the field:

- any of the three fields in a 0.2 or 0.3 episode:
  `Transitions need format machinome-video-draft/0.4: shot source`;
- a field that is not a mapping; an unknown field
  (`Unknown transition field: durration (transition in shot source)`);
- a kind other than the four (`kind must be fade, dissolve, wipe or slide; omit
  transition for a cut`), a direction other than `left` or `right`, an easing
  other than the five; `direction` on a fade or dissolve; `color` on a
  dissolve, wipe or slide; a colour that is not a quoted `"#rrggbb"`, or a
  defaulted colour whose `style.background` is not one;
- a duration that is missing, not finite, or shorter than two frames;
- a transition longer than either shot it joins
  (`Invalid transition in shot source: 5 s is longer than shot machine (4.5 s)`),
  or a `fadeIn` or `fadeOut` longer than its shot;
- `transition` on the first shot (use `fadeIn`), `fadeIn` on any other shot,
  `fadeOut` on any shot but the last (give the next shot a transition of kind
  `fade`);
- a shot whose incoming `transition` or `fadeIn` and its `fadeOut` together are
  longer than it (`Transitions overlap in shot closing: 1 s in and 2 s out
  exceed its 2.5 s`);
- an outgoing shot whose continued model would pass the export:
  `Shot machine cannot continue 1 s into the dissolve to shot source: its
  model would reach 1461.00 s, past the export's 1460 s; end its simulation
  earlier or shorten the transition`.

In `preview` and `render`, each picture a transition frame is made of passes
every check a posed frame has; an outgoing annotation whose part leaves the
frame is refused naming the outgoing shot and a video time past its `end`.

### What preview proves

For each transition `preview` adds stills at its first frame, quarters,
midpoint and last frame (a `fadeIn` or `fadeOut`: first, middle and last), and
proves from the plain pictures of the two shots at the same instant, decoded
pixel by pixel:

- a dissolve's midpoint is their blend at the eased progress within 2 levels
  of 255 on every channel of every pixel;
- a wipe's midpoint is exactly the outgoing picture on one side of the edge
  and exactly the incoming one on the other;
- a slide's midpoint, outside the masthead and progress rule, is exactly the
  two pictures at their offsets;
- a fade blends its colour with the picture as its easing predicts within 2
  levels at a quarter of each half, and is exactly the colour, outside the
  masthead and progress rule, at its midpoint; `fadeIn` on the film's first
  frame and `fadeOut` on its last are exactly the colour there too;
- posing the midpoint, another instant and the midpoint again gives identical
  pixels.

`report.json` records, per transition, the shot, field, kind, instants,
progress, the largest difference found and whether the two pictures differed
at all (if they did not, the proof shows nothing, and the report says so). A
failed proof stops preview, naming the shot and the time, and keeps
`transition-<shot>-{outgoing,incoming,composed}.png` (for a fade in or out,
`fadeIn-<shot>-…` or `fadeOut-<shot>-…`) in `preview/`. The highlight and lens
checks pose their shot with its transition removed, so a cue under an outgoing
picture is still proved on its own shot. Whether a kind reads well in motion is
for review.

A frame inside a transition depends only on its video time: the film page
composes it from poses of that instant alone, capturing each picture it is made
of without the masthead and progress rule and drawing the captures again inside
the page under them, so a resumed render reproduces it exactly. A fade frame
therefore poses the viewer once, and a dissolve, wipe or slide frame twice.

## Text animation

Format 0.4 adds word reveals and titles to overlays, and measured emphasis to
the source panel. All cues still use shot-local, half-open `from`/`to` times.
`reveal`, `subtitle`, `enter`, `leave`, `position: title` and `code.emphasis`
require 0.4; in 0.2 or 0.3 they are refused with
`Text animation needs format machinome-video-draft/0.4: shot judgment`.
An ordinary 0.4 overlay without these fields draws as it did in 0.3.

### Words that appear as they are spoken

```yaml
overlays:
  - from: 3
    to: 7.8
    position: top
    text: Propose. Inspect. Correct.
    reveal: {timing: spoken}
```

Words are maximal non-whitespace runs; spaces and newlines retain their exact
layout. Unshown words are invisible in place, so the text never reflows. A
lower-third's plate remains visible even before its first word. `phrase` may
name a passage of this shot's written narration when it differs from `text`
only in case or edge punctuation. It must occur exactly once in the narration,
and its spoken form exactly once in the cached character alignment. Displayed
and spoken words pair one-to-one after lowercasing and removing edge
punctuation. Punctuation-only words and ambiguous or missing phrases are
refused. `audio.replacements` affect the spoken phrase as they do the recorded
take; a replacement spanning words is refused.

Each word appears at its first spoken letter or digit, plus `speechOffset`
(default 0.2 s). A word spoken a whole output frame or more before the cue,
or with no global output frame before its end, is refused. `speech` must cache
the take before `check`; `check`, `preview`, `render`, and `render --silent`
only read its verified alignment. They never generate speech. If it is absent,
run `speech` first. A different `render --fps` must still give every word a
frame; otherwise that render is refused.

### Words at an even pace

```yaml
overlays:
  - {from: 0.4, to: 2.7, position: lower-third,
     text: Pause. Inspect. Test., reveal: {timing: even, duration: 1.8}}
```

The first word appears at `from`; the rest share the positive `duration`,
which must fit inside the cue. At progress `p = ease(name, elapsed/duration)`,
the count is `min(n, floor(n × p) + 1)`. The default curve is `linear`; an
optional `ease` names any of the five 0.4 curves. Every word must appear on
at least one delivered output frame, including with `render --fps`.

### Titles

```yaml
overlays:
  - {from: 2.941, to: 8.5, position: title, text: REVOLUTIONS,
     enter: {kind: fade, duration: 1}}
  - {from: 9, to: 12, position: title, text: REVOLUTIONS,
     subtitle: Digital reconstruction of a later museum interpretation,
     enter: {kind: fade, duration: 0.6},
     leave: {kind: fade, duration: 0.6, ease: in}}
```

`title` is an overlay over the running model, not a covering card. Its optional
non-empty `subtitle` sits beneath it. Two titles in one shot cannot overlap.
Only titles take `subtitle`, `enter` or `leave`; the latter accept `kind: fade`
with positive durations fitting together within the cue, and optional 0.4
easing (`smooth` by default). One opacity applies to title and subtitle.
At every posed frame a title leaving the picture is refused; preview compares
its fade to fully drawn and absent titles at that same moving-model instant.

### Source words lit as they are spoken

```yaml
code:
  snippet: coupling
  typing: [{from: 0, to: 0.8, throughLine: 415}]
  emphasis:
    - {line: 415, phrase: The waterwheel drives the crankshaft.,
       words: [waterwheel, drives, crankshaft], hold: 0.9}
```

The source line is absolute within the pinned excerpt; each distinct ASCII
identifier must occur once in that line and once in the phrase, in spoken
order. The phrase must occur once in the written narration and, after any
`audio.replacements`, once in the cached alignment. Identifiers light from
their measured onsets until the phrase's last character plus non-negative
`hold`; the marks accumulate and clear together. A word not yet typed when
spoken, a clear after shot end, overlapping emphasis intervals, or a missing
or ambiguous source token is refused. The mark keeps syntax colour and adds
the episode's accent tint and underline. Source characters, including `<`,
`&` and quotes, remain literal and safely escaped; source code is never run.

`preview` reports `revealChecks`, `fadeChecks` and `emphasisChecks` and verifies
visible word counts, title geometry, measured marks and exact replay. These
proofs establish that the cues reached pixels; pacing and readability still
need review of the rendered film.

## Showing stills and clips

Format 0.4 names media in `production.yaml` and places it with half-open,
shot-local `pictures` cues. For example:

```yaml
# production.yaml
stills:
  sawmill: {file: media/sawmill.png, credit: Own reconstruction render, rights: Own work, upscale: 1.25}
clips:
  controls: {file: media/controls.mp4, credit: Own screen recording, rights: Own work}

# episode.yaml, under one shot
pictures:
  - {from: 0, to: 4, still: sawmill, area: frame, fit: contain,
     enter: {kind: fade, duration: 0.4}}
  - {from: 5, to: 8, clip: controls, inPoint: 1.5, area: stage}
```

Exactly one of `still` and `clip` is required. Cues in a shot cannot overlap;
gaps uncover the continuously posed model. `area: stage` is the default: the
model stage is 90% × 63% of a plain frame, or 42% × 65% beside source code.
`area: frame` covers the whole frame below the masthead and progress rule.
The picture's background-coloured plate and image cover the area together;
text overlays remain above them, and film transitions remain above both.
Annotations or highlights overlapping a picture are refused because they
target a covered model: `Annotation #0 overlaps picture #1 in shot studied`.
Use an existing lower-third overlay for visible picture words; a picture has
no `caption` field.

`fit: contain` (default) shows the whole image, with bands of
`style.background` where the aspect differs. `fit: cover` fills and may crop.
A still's optional `view` keys move through it:
`{at: 1, center: [0.5, 0.5], zoom: 1}` followed by
`{at: 3, center: [0.5, 0.27], zoom: 1.9, ease: in-out}`. `at` is shot-local,
strictly increasing and inside the cue; the first view holds before its key,
the last after its key. The ending key names the easing of its incoming
segment. Zoom is multiplicative and the centre follows the fixed point of the
two keyed views, so a push toward a detail does not drift away before
arriving. At every output frame the picture must either fit wholly inside its
area or cover it wholly on each axis. A view exposing a gap or cropping an
underfilled image is refused, naming the shot, cue and second.

The raster enlargement factor is output pixels per source pixel at the
largest keyed zoom. `check` refuses a factor above `upscale` (default 1) and
prints the peak and allowance; `render --width` checks again for its actual
width. An SVG is resolution-independent and must not declare `upscale`.
Each picture may `enter` and `leave` with `{kind: fade, duration, ease?}`;
only `fade` is supported, each fade lasts at least two output frames, and
their durations cannot overlap. Its first fade-in frame is the uncovered
model; the picture is absent at its exclusive `to`. The whole plate and image
fade together, composited from same-instant opaque and absent captures so
their pixels replay exactly.

Clips have `inPoint` (default 0), no keyed `view`, and no sound in the film.
At film second `T`, the page shows the source frame whose presentation
timestamp is latest at or before `inPoint + T − cue start`. Clip timestamps
come from integer presentation ticks and the stream's time base, normalized
to the first frame. This samples and holds: faster clips drop frames, slower
ones repeat them; neither blends nor invents a frame. `check` reports source
rate, film rate, dropped and repeated counts. It refuses missing or
non-increasing timestamps, interlacing, non-square pixels, rotation tags and
a clip too short for its cue or its outgoing-transition continuation.
The cadence count uses the film's actual global frame grid, including a cue
whose `from` falls between frames and any outgoing-transition continuation.
An audio stream in a clip is accepted but never played; the film's soundtrack
remains its narration.

Raster stills must be one decoded PNG, JPEG or WebP frame matching their
extension; animated stills and GIF are refused. SVG stills need a `viewBox`
with positive size; a missing one with declared `width` and `height` gets a
suggested `viewBox` in the refusal. Scripts, `foreignObject`, SVG or CSS
animation and external references are refused. Every file resolves inside
the project Git repository, even after following symlinks. Both `credit` and
`rights` must be present; `null` allows a rehearsal but blocks release.

`preview` saves each picture's entrance, keyed views, fade midpoints and last
visible frame. It checks measured stage/drawn geometry and natural size,
exact source clip frame, enlargement and exact replay. At a fade it captures
the authored, fully opaque and absent states at one instant, proving the
first/end pixels and a visibly intermediate midpoint. A failed proof retains
its PNGs for inspection. `preview/report.json` records every picture check;
the storyboard includes its samples.

## Optional subtitles

Narration produces `captions.json` and UTF-8 `captions.srt`. A narrated render
also writes `rehearsal.srt` beside `rehearsal.mp4` (or the selected render label).
Upload the SRT separately to YouTube or load it in a player, for example
`mplayer rehearsal.mp4 -sub rehearsal.srt`. The MP4 has no subtitle stream and
no burned narration. This intentionally changes earlier draft-0.2 rendering:
old mastered files stay unchanged; new renders use external subtitles only.

The film stage mounts Viewer API 21 or later (28 for format 0.3 cues) with
external, paused, on-demand rendering and no interactive controls. The viewer's setters pose/render synchronously;
Playwright captures the composed frame. A rendered frame does not advance
the model by wall-clock time. Below Viewer API 28 the page gives the viewer an up
and field of view once, at mount; from API 28 it sets them on every frame.

## Evidence and provenance

Every evidence name must resolve to a project file. Sources support the claim
or visual intent; they do not certify the current model. Before final rendering,
pin the tested model revision and record the export, viewer version, episode
revision, audio settings, generated audio hashes and output settings in a build
manifest. Cached audio is the reproducible input; regeneration may differ.
The manifest also records each still's and clip's project-relative path,
SHA-256, dimensions, source codec/rate, committed status, credit, rights,
allowance and per-cue peak. Clips add their extracted frame span, decoder key,
FFmpeg version and dropped/repeated cadence; `audio` is `not played`.
`_build/clips/<key>/` holds the lossless source-frame PNGs used in preview and
render. A picture's unresolved credit or rights, uncommitted file, or a
description template without `{{pictureCredits}}` makes `releaseReady` false
and appears in `pictureReleaseIssues`. Rehearsals still proceed. The placeholder
becomes one `name: credit` line per shown picture, or a marked pending line
for a null credit; Videomaker records rights but does not judge them.

`render` caches complete shot generations under `_build/shot-cache/shot-v1/`.
Its output frames still use the film-wide `n / fps` clock, including progress
and an outgoing picture during an incoming transition. Each generation has an
index published only after all its frames are captured. Reuse verifies the
index, every PNG checksum and dimensions; missing, interrupted or damaged
generations are recaptured as whole shots. The output manifest records the
cache schema, common key, each shot's frame counts/key/generation/original
capture provenance, and the encoded MP4 checksum. A reused shot retains its
original capture provenance. The old `_build/frames/` cache is not imported or
deleted. A first render with this schema is cold.

The common key binds the first mounted frame, model/viewer/page/runtime,
the known regular/bold film and mono font faces in the tested environment,
global chrome/style, browser, viewport, FPS and film
duration. A first-shot edit may therefore invalidate all shots. A later edit
normally invalidates its shot and any following shot whose incoming transition
uses it as outgoing, not distant shots. Reached still bytes and selected clip
frame bytes/timestamps are per-shot; unused picture declarations, release
metadata, and external captions are not visual inputs. Spoken visual cues bind
their verified cached take and resolved timing; an even reveal does not.
Preflight validation and measured-take checks rerun before any cache hit is
used. A reused shot inherits frame-level browser pose checks from its
identical-input, attested capture. Audio and SRT are rebuilt for the current
render without generating speech. If an
interrupted publication leaves an old manifest beside a newer MP4, its output
checksum will not match: verify `outputSha256` against `output` before treating
it as a completed render. The prior MP4 remains recoverable at
`<label>.mp4.previous-<id>` until a successful publication removes that backup.
