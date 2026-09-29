## Context

A frame is a pure function of video time: `frameAt(e, t)` in `src/timeline.mjs`
finds the one shot whose `[start, end)` holds `t` and returns its model time,
camera, hidden paths, overlays, code, and (0.3) annotations and highlight.
`render.mjs`'s `pose(t)` hands that frame to the film page (`src/film.js`),
which poses the paused on-demand viewer, rebuilds the overlay and annotation
layers from nothing, and returns what it drew; Playwright then captures the
page. The page's cross-frame state (hidden paths, the standing highlight, the
code layout) is applied by comparison with the requested state, so posing
frames in any order gives the same pixels, which the preview's exact replay
check proves. The page chrome that belongs to the film rather than to any shot
is the masthead (the `MACHINOME` mark, the series label) and the progress rule.

Shots are contiguous and cover the film. `FORMAT.md` says boundaries are hard
cuts. The sibling change `keyframes-and-easing`, applied before this one, adds
format `machinome-video-draft/0.4` and the campaign's easing vocabulary
(`linear`, `smooth`, `in`, `out`, `in-out`) in `src/easing.mjs`; this change
uses both by name and redefines neither.

The evidence is the edit the dark-source sequence and the *Revolutions* draft
both make: moving machine, then source, then moving machine
(`machinome-dark-sequence` at 4.5 s and 20.5 s; `machinome-revolutions-v2`
from `machinome` into `wheel-class`, and from `mill-class` into
`early-invitation`). Both are outside the supported format today because they
show source full-screen (roadmap item 12). In the supported format the same
edit joins a code shot (the split layout) and a model shot, which also changes
the page layout at the boundary. The *Revolutions* README asks that code and
machine "never share the screen"; of the four kinds, only the fade through a
colour honours that, and the pilot chooses among them on the demo.

## Goals / Non-Goals

Goals: join two shots with a fade through a colour, a dissolve, a wipe or a
slide, and fade the film in and out, written as short readable YAML at the
shot that begins; keep every frame a function of video time; keep narration,
captions and shot timing exactly as authored; refuse what cannot be drawn
truthfully; prove each transition in pixels.

Non-goals, left out because no episode asks for them: transition presets in
`production.yaml` (a transition is two to four short words, and its duration
matters to whoever reads the screenplay's timing; presets can follow when an
episode repeats one); up, down, diagonal, iris, clock or soft-edged wipes;
slides other than left and right; transitions spanning more than two shots; a
freeze-frame alternative to continuing the outgoing shot; audio fades (item
10); a full-screen source layout (item 12).

## Decisions

### D1. The fields, and where they are declared

A transition belongs to the boundary it joins, and every boundary inside the
film has exactly one shot that begins there. So the join is declared on the
incoming shot, as how that shot comes in; the film's head and tail, which have
no second shot, get their own two fields.

```yaml
shots:
  - id: machine
    start: 0
    end: 6
    fadeIn: {duration: 1.5}                     # from the paper colour
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
    fadeOut: {duration: 2}
    ...
```

- `transition` (any shot but the first): `kind` is `fade`, `dissolve`, `wipe`
  or `slide`; `duration` in video seconds; `ease` optional, one of the
  campaign names, default `smooth`; `direction` (`wipe` and `slide` only)
  `left` or `right`, default `left`; `color` (`fade` only) a quoted `#rrggbb`,
  default in D5. Omitting `transition` is a hard cut; there is no `kind: cut`,
  so a cut has one spelling.
- `fadeIn` (first shot only) and `fadeOut` (last shot only): `duration`,
  optional `ease` (default `smooth`) and optional `color`.
- `direction` names the way the motion goes: `left` means the incoming picture
  enters from the right edge and the boundary (wipe) or both pictures (slide)
  travel leftward; `right` is the mirror. Two directions cover the evidence:
  going to the source and coming back.

`smooth` is the default because it is the easing every motion in the format
has had so far (camera moves) and the campaign makes it the default wherever a
smoothstep exists; `linear` is one word away for a classic even dissolve.
The field is spelled `ease`, the spelling `keyframes-and-easing` settled.

### D2. Where a transition sits in time

A transition occupies the first `duration` seconds of the shot that declares
it: `[B.start, B.start + duration)` for incoming shot B. `start` and `end`
never change, and the incoming shot's own timeline begins at its `start` as it
does after a cut, so its first `duration` seconds are seen through the
transition: model time, camera, overlays, annotations, highlights, code typing
and speech offset all keep their authored times. The outgoing shot A is shown
continuing past its `end` for as long as it remains visible (D3).

Rejected: centring the transition on the boundary, which needs both a
continuation of A and a pre-roll of B (model time before B's `from`, cues at
negative shot-local times); and placing it in A's last seconds, which needs B
pre-rolled or frozen and lets the declaring shot reach back into the previous
shot's narration. The chosen placement needs one extrapolation, forward in
time, of a shot whose content is complete: every cue of A ends by its end and
its typing must complete within it.

`fadeIn` occupies `[0, duration)` of the first shot. `fadeOut` occupies the
last `duration` seconds of the last shot and is complete on the film's last
frame (D4).

### D3. What the outgoing shot shows past its end

The outgoing shot continues, it is not frozen: a mechanism that stops dead
for the length of a dissolve reads as a stall, and these films are about
motion. For shot-local time `L = duration(A) + u` during the transition:

- **Model.** Model seconds continue from the shot's `to` at the rate model time
  has at the shot's end: `to + r·u`. Today every model segment is linear, so
  `r` is the last segment's rate (`(to − from)/duration`, or through the last
  two `keyframes`); a held shot (`from == to`, or a final hold) holds. If
  `keyframes-and-easing` lets a model segment ease, `r` is that easing's slope
  at the segment's end, so a segment that eases to rest holds. The viewer is
  never asked for a time beyond `model.expectedDurationSeconds`: `check`
  refuses a continuation that would pass it (D7).
- **Camera.** Holds its last key, as it already does after the last key.
- **Cues.** An overlay, annotation or highlight cue whose `to` equals the
  shot's duration (it runs to the end) stays on until A is no longer visible;
  every other cue has already ended and stays ended. Annotations keep being
  resolved on the moving model every frame, so the existing off-screen refusal
  applies to them.
- **Code.** The excerpt is complete (typing must finish inside the shot), so
  the panel holds its full text and no cursor.
- **Visibility.** A's own `hiddenLayers`.

### D4. How each kind draws

`u` is time since the transition began, `d` its duration, `ease` the named
easing; `p = ease(u/d)` runs from 0 on the transition's first frame (which
therefore shows A alone, the frame after its end) to just under 1 on its last.
`W` is the frame width in pixels. Edges and offsets are whole pixels, so the
proofs in D8 can be exact.

- **dissolve**: A over B at opacity `1 − p`.
- **wipe**: a straight vertical edge `e = round(p·W)` pixels from the side B
  enters from; A on one side, B on the other; a hard edge.
- **slide**: A moves `round(p·W)` pixels in `direction` and B enters from the
  opposite edge, butted against it, so the frame is always exactly covered.
- **fade** (between shots): a plate of the colour over the picture. In the
  first half the picture is A and the plate's opacity is `ease(2u/d)`; in the
  second half the picture is B and the opacity is `1 − ease(2u/d − 1)`. The
  midpoint is the plain colour; B's first `d/2` seconds are under the plate,
  so its narration may start while the picture is still arriving.
- **fadeIn**: plate opacity `1 − ease(local/d)`; the film's first frame is the
  plain colour.
- **fadeOut**: plate opacity `ease(min(1, (local − (D − d)) / (d − 1/fps)))`,
  with `D` the shot's duration and `fps` the episode's `output.fps`, so the
  film's last frame, at `end − 1/fps`, is the plain colour. A quick render at
  another `--fps` may stop that last frame a fraction short of it.

Every kind acts on the picture, not on the film's chrome: the transition is
drawn above the stage, annotations, overlays and code panel and below the
masthead and progress rule, which belong to the film and stay put. A slide
therefore never pushes the `MACHINOME` mark out of frame, and a fade in or
out shows the page's masthead on the colour. Whether fades should also cover
the masthead is an open question for the pilot.

### D5. The fade colour

Default: `style.background`, which must then be a quoted `#rrggbb` (as a
highlight's default colour requires of `style.accent`). The Leonardo films
are either cream paper (`#faf7ef`, `#f5f1e8`) or dark (`#111519`). On paper, a
fade through black would flash two large brightness swings into a light film,
and the page's masthead sits on the background colour, so fading to the
background reads as the picture leaving the page. On the dark films the
background is already near black, which gives the conventional fade to black.
An author who wants black on a paper film writes `color: "#000000"`.

### D6. Producing a transition frame

The timeline stays pure data. In 0.4 frames `frameAt` adds `transition`:
`null` outside transitions, otherwise the kind, `p` or the plate opacity, the
direction and colour, which picture a fade shows, and `outgoing`: A's complete
continued frame (D3) computed by the same shot-local function that makes B's
frame. The frame itself is still B's frame at local `u`, unchanged.

`pose(t)` in `render.mjs` produces the composed page, ready for the caller's
capture, from poses of that instant only:

- **fade, fadeIn, fadeOut**: one pose of the picture (A continued or B) with
  the plate at its opacity. No capture is needed.
- **dissolve, wipe**: pose A continued with the page in picture-only mode
  (masthead and progress rule hidden, transition layer empty), capture it, then
  pose B with that image in the transition layer at the opacity or clip `p`
  dictates.
- **slide**: capture A and then B, both picture-only, then pose B with both
  images in the layer at their offsets; B's live picture is fully covered.

The page rebuilds the transition layer from nothing on every `setFrame`, as it
does overlays and annotations, and waits for the images to decode before
returning. Each sub-pose runs `pose`'s existing checks (camera adopted, canvas
fills the stage, code fits, annotations on screen), so an outgoing annotation
that leaves the frame is refused naming the outgoing shot and the video time.
Nothing depends on the previous frame: the captured images come from the same
instant and the page's state is set by request. Overlays, annotations,
highlights, the code panel and a change of layout between a code shot and a
model shot are composed without any special case.

Rejected: compositing in Node or ffmpeg from separate captures, which adds a
second path for the film's pixels, needs a third capture for the masthead, and
leaves the page's checks blind to the composed frame; and a second viewer
instance for the outgoing shot, which doubles memory and could differ from the
first.

### D7. Refusals

At `check`, naming the shot (and the field: `transition`, `fadeIn`, `fadeOut`):

- any of the three fields in a 0.2 or 0.3 episode:
  `Transitions need format machinome-video-draft/0.4: shot source`;
- a field that is not a mapping, or an unknown field
  (`Unknown transition field: durration (transition in shot source)`);
- an unknown kind (`kind must be fade, dissolve, wipe or slide; omit transition
  for a cut`), direction (`left or right`) or easing (the vocabulary's message);
  `direction` on a fade or dissolve; `color` on a dissolve, wipe or slide; a
  colour that is not a quoted `#rrggbb`, or a defaulted colour whose
  `style.background` is not one;
- a duration that is not finite, or shorter than two frames at `output.fps`;
- a transition longer than either shot it joins
  (`Invalid transition in shot source: 5 s is longer than shot machine (4.5 s)`),
  or a `fadeIn` or `fadeOut` longer than its shot;
- `transition` on the first shot (`use fadeIn`), `fadeIn` on any other shot,
  `fadeOut` on any shot but the last (`give the next shot a transition of kind
  fade`);
- transitions that overlap: a shot whose `transition` or `fadeIn` and whose
  `fadeOut` together are longer than it
  (`Transitions overlap in shot closing: 1 s in and 2 s out exceed its 2.5 s`).
  Placement D2 makes this the only way two transitions can overlap: a
  transition lies inside the shot that declares it and is no longer than it;
- an outgoing shot whose continued model would pass the export's duration:
  `Shot machine cannot continue 1 s into the dissolve to shot source: its
  model would reach 1461.00 s, past the export's 1460 s; end its simulation
  earlier or shorten the transition`. The continuation checked is `d` for a
  dissolve, wipe or slide and `d/2` for a fade.

At the posed frame, in `preview` and `render`: every refusal a posed frame
already has, applied to each sub-pose, naming the shot that is posed, which
for the outgoing picture is the outgoing shot at a video time past its `end`.

### D8. What preview proves, and the frame cache

For each transition `preview` saves stills at its first frame, quarters,
midpoint and last frame (for `fadeIn`, `fadeOut`: first, middle, last), and
proves, by decoding the captures and comparing pixels:

- **dissolve**: at the midpoint, the composed frame equals `(1 − p)·A + p·B`
  within 2 levels of 255 on every channel of every pixel, where A and B are
  the plain frames of the two shots at that instant (the incoming frame posed
  with its transition removed, the outgoing continued frame posed alone);
- **wipe**: at the midpoint, every pixel on A's side of the edge equals A and
  every pixel on B's side equals B, exactly;
- **slide**: at the midpoint, outside the masthead and progress rule, the
  composed frame equals the two picture-only captures at their offsets,
  exactly;
- **fade**, **fadeIn**, **fadeOut**: at a quarter of the fade (or of each half
  of a between-shot fade), the frame equals the plate blend of the colour and
  the plain picture within 2 levels; at a between-shot fade's midpoint, at
  `fadeIn`'s first frame and at `fadeOut`'s last frame, every pixel outside the
  masthead and progress rule is exactly the colour;
- **replay**: posing the transition's midpoint, then another instant, then the
  midpoint again yields identical pixels.

The report records, per transition, the shot, kind, instants, `p`, the
largest difference found and whether the two plain pictures differed at all
(if they did not, the dissolve proof is vacuous and says so). A failed proof
keeps `transition-<shot>-{outgoing,incoming,composed}.png` in `preview/`.
The preview's existing highlight and lens comparisons pose the incoming frame
with its transition removed, so a cue that happens to lie under the outgoing
picture is still proved on its own shot.

The render's frame identity already hashes the episode, `timeline.mjs`,
`render.mjs` and the served page files; `src/easing.mjs` and any new module on
the frame path are added to it. Each cached frame is composed entirely within
its own `pose`, so resuming an interrupted render reproduces it exactly.

### D9. Format and viewer

The three fields exist only in format 0.4, on the pattern of 0.3: a 0.2 or 0.3
episode carrying one is refused and asked to change its format, and 0.2 and
0.3 frames keep their exact shape (`transition` is added only to 0.4 frames).
Transitions add no Viewer API requirement: they use `setTime` and `setView`
as every frame does, so a 0.4 episode needs whatever viewer its other cues
need.

## Risks / Trade-offs

- **Re-drawn captures must reproduce their pixels.** The wipe and slide proofs
  are exact, so any colour management or resampling Chromium applies to a
  re-drawn PNG shows up at once. If it does, the implementer stops and brings
  the finding back rather than widening a tolerance; the fallback is to draw
  the capture into a canvas without colour conversion.
- **Cost.** A dissolve or wipe frame poses twice and a slide three times, and
  each capture crosses into the page as an image (a few megabytes at 1080p). A
  one-second transition is 30 such frames; a film has a handful.
- **The outgoing camera stops.** Past its end the outgoing camera holds its
  last key. With `smooth` it is already at rest; a move that ends with an
  easing still at speed (`in`) stops abruptly inside the transition. Review
  the stills.
- **Double images.** A dissolve between two views of the same moving machine
  shows the machine twice, at two model times. That is what a dissolve is; the
  fade through a colour is the alternative that never shows two pictures.
- **Continuation truth.** The outgoing model runs on at the rate it ended with;
  it shows the machine doing what it was doing, never a pose the model did not
  compute, but those seconds were not in the authored range. The `check`
  refusal keeps them inside the export.

## Migration Plan

Additive and opt-in by format 0.4 and the new fields. Every existing episode,
including all Leonardo episodes, parses and renders unchanged. Reverting the
tool commit makes an episode that uses transitions refused (unknown fields or
format), never rendered with hard cuts in their place.

## Open Questions

- Should fades cover the masthead and progress rule? Proposed: no (D4); a
  fade to black on a paper film then leaves the masthead on black.
- Default easing: `smooth` for every kind is proposed for one rule across the
  campaign; the pilot may prefer `linear` for dissolves.
- Continue or freeze the outgoing shot (D3): continuing is proposed; if the
  pilot prefers the outgoing picture to hold still, freezing is simpler and
  needs no model check.
- Whether the demo's source-to-machine joins should use the fade (which keeps
  code and machine apart, as the *Revolutions* README asks) or a dissolve.

## Ratification (29 September 2026)

Ratified by the orchestrating agent as the campaign's review gate, under the
pilot's delegation, reconciled with the ratified `keyframes-and-easing`:

- **The field is `ease`** (D1), as on camera keys and model keyframes; the
  examples above are corrected. Its names and messages are `src/easing.mjs`'s.
- **D3's end rate under eased model segments.** `r` is the last segment's
  average rate, `(R − L)/(B − A)`, times the slope of its curve at its end:
  `linear` 1, `smooth` 0, `in` 3, `out` 0, `in-out` 0. A segment easing to rest
  therefore holds through the transition; a hold holds. `check`'s continuation
  refusal uses the same `r`.
- **0.4 frame shape.** Every 0.4 frame carries `transition` (`null` outside
  one). The `keyframes-and-easing` test that a 0.4 episode's frames deep-equal
  its 0.3 frames is amended in this cycle to expect the added
  `transition: null`; 0.2 and 0.3 frames are untouched.
- **Open questions settled for now**, the pilot may revisit on the demo: fades
  do not cover the masthead and progress rule; the default easing is `smooth`
  for every kind; the outgoing shot continues rather than freezes; the demo
  joins source and machine by `fade` and joins model shots by dissolve, wipe
  and slide so every kind is seen.
- The 0.4 closed field lists gain `transition`, `fadeIn` and `fadeOut` on the
  shot, and the three fields' own closed lists as D7 says.
