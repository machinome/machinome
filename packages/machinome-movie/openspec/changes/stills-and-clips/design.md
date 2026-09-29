## Context

A frame is a pure function of video time. `frameAt(e, t)` (`src/timeline.mjs`)
returns the shot's model time, camera, hidden paths, overlays and code; in 0.3
and later it also returns annotations and highlight, and after the ratified
`shot-transitions` it returns `transition`. `render.mjs`'s `pose(t)` hands the
frame to `film.js`, which poses the paused viewer and rebuilds its layers from
nothing, and Playwright captures the page. The loopback asset server serves only
a fixed map of files (viewer, page, model assets), and their hashes enter the
frame cache identity together with the resolved episode `e`, `render.mjs`,
`timeline.mjs`, `code.mjs`, `easing.mjs` and the lock file.

Page layout (`film.html`): the model stage `#viewport` is inset `16% 5% 21%`
(90 % × 63 % of the frame). In a code shot it is inset `20% 2% 15% 56%`
(42 % × 65 %) beside the code panel. The masthead (`#brand`, `#series`) and the
progress rule belong to the film. `shot-transitions` D4 keeps them above its
transition layer.

The rulings this change builds on:

- `keyframes-and-easing`: format 0.4, `EASINGS`, `ease(name, u)`,
  `keyedValue`, `ease` on a key naming the segment that ends there (D3), the
  first key refusing `ease`, and 0.4 closed field lists that later cycles
  extend (D7).
- `shot-transitions`: `fadeIn`/`fadeOut` spelled `{duration, ease?}` with
  `ease` defaulting to `smooth`, durations of at least two frames; the outgoing
  shot continues past its end during a transition, and a cue whose `to` equals
  the shot's duration stays on through that continuation (D3). The continuation
  is `d` for a dissolve, wipe or slide and `d/2` for a fade (D7). Every 0.4 frame
  carries `transition`.
- `graphic-overlays` and `text-animation` are being proposed in parallel. This
  change needs only one thing from them: whatever they draw over the picture
  (graphics, titles, captions) stays above pictures, as text overlays do.

What the project holds (read-only survey, 29 September 2026):
`_reference/hydraulic_sawmill/` (ignored): `atlanticus-1078r.jpg` 1427×2048,
watermarked "for study purposes and consultation only"; `milan-overall.jpg`
1175×781, and others. `_evidence/hydraulic_sawmill/` (ignored): own renders at
1200×900 and 1440×1800. `screenshots/hydraulic_sawmill.png` (tracked): 640×360.
`export/hydraulic_sawmill-frame/carpentry/*.svg` (generated, ignored): own
carpentry drawings, declaring `width="420.0" height="240.0"` and no `viewBox`.
The project holds no video file. The one clip the evidence asks for is a
recording of the interactive simulation's controls, which does not exist yet.

## Goals / Non-Goals

Show a named still or clip in a shot, full stage or full frame. Move slowly
across a still with keyed pan-and-zoom. Insert a clip from an in-point. Keep
every frame a function of video time and the hashed media. Refuse what cannot
be drawn truthfully, before any browser where that can be known. Carry the
pictures' provenance into the manifest and the release gate. Not goals:
regions or picture-in-picture, clip sound, clip pan-and-zoom, rights judgement.

## Decisions

### D1. Named pictures in `production.yaml`

```yaml
stills:
  codex-1078r:
    file: ../../_reference/hydraulic_sawmill/atlanticus-1078r.jpg
    credit: null        # unresolved: blocks release readiness, not a rehearsal
    rights: null
  museum:
    file: ../../_reference/hydraulic_sawmill/milan-overall.jpg
    credit: null
    rights: null
    upscale: 1.4        # the author allows up to 1.4 output pixels per source pixel
  frame-joints:
    file: frame-joints.svg
    credit: Machinome carpentry drawing of the reconstruction
    rights: Own work, AGPL-3.0-only
clips:
  try-it:
    file: try-the-simulation.webm
    credit: Screen recording of the interactive simulation
    rights: Own work, AGPL-3.0-only
```

- `file` (required): a path relative to `production.yaml`. It must resolve,
  after following links, to a file inside the project's Git repository, as
  Python source must, and its extension must be `.png`, `.jpg`, `.jpeg`,
  `.webp` or `.svg` for a still and `.mp4` or `.webm` for a clip.
- `credit`, `rights` (both required keys, a non-empty string or `null`): the
  attribution line for the release description and the author's statement of
  the right to show it. `null` means unresolved. Following the house rule for
  null release fields, it is allowed in a rehearsal and blocks release
  readiness (D11). Videomaker never interprets `rights`.
- `upscale` (optional, raster stills and clips only, a finite number ≥ 1,
  default 1): the largest number of output pixels per source pixel the author
  allows (D6). On an SVG it is refused, because a vector picture has no source
  pixels.
- Closed lists: a still accepts `file, credit, rights, upscale`, and a clip
  accepts the same four. Anything else is refused:
  `Unknown still field: upsacle (still museum)`.

The maps are read and validated only for a 0.4 episode. A 0.2 or 0.3 episode
ignores them, as it ignores every production key it does not use today, so a
production file shared between formats cannot break an older episode.

A still is not an `evidence` entry. Evidence supports a claim, while a still is
something shown on screen. The same file may appear in both.

### D2. The shot field `pictures`

```yaml
# format machinome-video-draft/0.4
  - id: museum-reference
    ...
    pictures:
      - {from: 0, to: 17, still: museum, area: frame}
  - id: question-and-feedback
    ...
    pictures:
      - {from: 0, to: 6.2, still: museum, area: frame, fadeOut: {duration: 0.6}}
      # match-cut to the reconstruction at 6.2 s; the model has kept its timeline
      - from: 9
        to: 15
        clip: try-it
        inPoint: 3.5
  - id: studied
    ...
    pictures:
      - from: 0
        to: 9
        still: codex-1078r
        area: frame
        fadeIn: {duration: 0.8}
        view:
          - {at: 1, center: [0.5, 0.5], zoom: 1}
          - {at: 8, center: [0.5, 0.27], zoom: 1.9, ease: in-out}   # onto the saw sketch
```

- `from`, `to`: shot-local seconds, half-open, `0 <= from < to <= duration`.
  The pictures of one shot must not overlap; gaps show the model.
- Exactly one of `still` and `clip`, naming a `stills` or `clips` entry.
- `area`: `stage` (default) or `frame` (D4).
- `fit`: `contain` (default: the whole picture, never cropped) or `cover`
  (fills the area, cropping the excess). `contain` is the default because the
  evidence asks for "fitted without cropping", and a default that cropped would
  hide part of a historical document without the author choosing it.
- `fadeIn`, `fadeOut` (optional): `{duration, ease?}` (D9).
- `view` (still only): pan-and-zoom keys (D5). Without it the still shows
  fitted and centred (`center: [0.5, 0.5]`, `zoom: 1`).
- `inPoint` (clip only, default 0): the clip second shown at `from` (D7).
- Closed list: `from, to, still, clip, area, fit, fadeIn, fadeOut,
  view, inPoint`. A view key accepts `at, center, zoom, ease`, and a fade
  accepts `duration, ease`. The 0.4 shot field list gains `pictures`.

The word is "picture" because the field holds both kinds, and the craft calls
both pictures. `center` is spelled as the overlay position `center` already is.

### D3. What a picture covers, and the model beneath

A picture covers its whole area. The page draws a plate of `style.background`
over the area, the picture on the plate as its fit and view place it. With `contain`, the bands beside the picture are that plate:
"against the dark background" in a dark film, against the paper in a light one.
The plate and the picture fade as one (D9).

Covering only a region of the stage was considered and rejected. It is
picture-in-picture (roadmap items 4 and 12), no episode asks for it, and it
would reopen every question of annotations aimed at a half-visible model.

Beneath a picture the model keeps its shot's timeline exactly. Model time
advances, the camera moves and visibility holds. The page poses the viewer
every frame as it does without a picture. A picture that ends mid-shot
therefore cuts back to the model exactly where the shot's timeline is, and no
frame depends on an earlier one. Skipping the viewer's work under a covering
picture would save time, but it would make the page's state depend on the
history of poses, so it is left out.

While a picture is up (`from` to `to`, fades included), the same shot's
annotations and highlights are refused at `check`, naming both cues:
`Annotation #0 overlaps picture #1 in shot museum-reference; a picture covers the model`.
During a fade the model is partly visible, but an arrow aimed at a
half-dissolved part would draw attention to what the film is taking away.
Every refusal of `check` must also hold at the posed frame, and the preview's
highlight proof would fail on a covered highlight in any case. Camera moves and
`hiddenLayers` are unaffected.

Stacking, from bottom to top: model stage, code panel, annotations, pictures,
text overlays (and whatever `graphic-overlays` and `text-animation` draw),
the `shot-transitions` layer, then the masthead and the progress rule. A
`frame` picture therefore covers the stage and the code panel but not the
masthead or progress rule. This is forced by coherence with the ratified
`shot-transitions` D4. The transition layer sits below the masthead and must
sit above pictures, so that a fade or dissolve into a picture shot composes
like any other shot. A picture above the masthead would sit above the
transition layer too. (Open Questions.)

### D4. The two areas, in numbers `check` can use

`frame` is the whole output frame. `stage` is the model stage for that shot's
layout: `[0.05, 0.16, 0.90, 0.63]` (x, y, width, height as fractions of the
frame) without code, and `[0.56, 0.20, 0.42, 0.65]` in a code shot.
`src/pictures.mjs` declares these two rectangles as constants, because `check`
needs them without a browser (D6). `preview` measures the page's `#viewport`
on every picture sample and refuses a stage rectangle that differs from the
constant by more than one pixel:
`Film stage layout differs from the picture geometry: shot studied`.
A later layout change cannot drift silently from the enlargement check.

### D5. Geometry and pan-and-zoom

For a picture of intrinsic size `(Wi, Hi)` shown in an area of `(Wa, Ha)` output
pixels, the size comes from the decoded pixels for raster pictures (D10) and
from the `viewBox` for SVG:

- the fit scale is `s0 = min(Wa/Wi, Ha/Hi)` for `contain` and
  `max(Wa/Wi, Ha/Hi)` for `cover`;
- a view `{center: [cx, cy], zoom: z}` shows the picture at scale `S = s0·z`,
  with picture point `(cx, cy)` (fractions: `[0, 0]` top-left, `[1, 1]`
  bottom-right) at the area's centre. The drawn rectangle, in fractions of the
  area, is `w = S·Wi/Wa`, `h = S·Hi/Ha`, `x = 0.5 − cx·w`, `y = 0.5 − cy·h`.
  The frame carries this rectangle and the page multiplies it by the area it
  measures, so the preview's 960-pixel page and the render's 1920-pixel page
  draw the same composition.
- `center` values lie in `[0, 1]` and `zoom` is finite and at least 1. Zoom 1 is
  the fitted picture; nothing asks for a picture smaller than its fit.

View keys use shot-local `at`, strictly increasing, within `[from, to]`, like
camera keys. Before the first key the first view holds, and after the last key
the last view holds, as in `keyedValue`. A key's `ease` names the segment that
ends at it (default `smooth`, the camera's default, since a pan-and-zoom is the
still's camera move), and `ease` on the first key is refused
(`Nothing to ease before the first view key: picture #0 in shot studied`).
Within a segment from key `a` to key `b`, with `u = (local − a.at)/(b.at − a.at)`
and `w = ease(b.ease ?? 'smooth', u)`:

- `w === 0` gives `a`'s view and `w === 1` gives `b`'s, exactly;
- otherwise `z = za·(zb/za)^w` (exactly `za` when `za === zb`), and
  `c = ca + (cb − ca)·k` component-wise, where
  `k = (1 − za/z)/(1 − za/zb)`, or `k = w` when `za === zb`.

This is not `keyedValue`'s component-wise mix, for two reasons. First, zoom is
seen multiplicatively: a linear mix of zoom 1 → 4 spends most of its time on
the first doubling. Second, a linear mix of centre and zoom makes the detail
being approached drift outward before it comes back, whenever the zoom ratio
exceeds e (≈ 2.7). The formula above keeps fixed, on screen, the one picture
point that both keys put in the same place (`f = (cb·zb − ca·za)/(zb − za)`,
since `(f − c)·z` stays `(f − ca)·za`), so a push onto the saw sketch reads as a
steady approach, the way a camera dollies. A pure pan (`za === zb`) is linear in
`w`. The segment selection, the hold rules and the easing are the helper's and
the vocabulary's. Only the mix differs, and it is the only view mix defined.

Truthful framing is checked at every output frame of the interval at
`output.fps`, like the up-along-view sweep. On each axis:

- if the picture is at least as large as the area on that axis, the area must
  lie within the picture, so no plate shows beside a picture that overfills
  (this is the whole promise of `cover`);
- if it is smaller, the picture must lie within the area: nothing of a picture
  that underfills is cut off.

`Picture view leaves the picture in shot studied at 3.40 s (picture #0, codex-1078r); keep the view inside the picture or zoom in`.
Because this is a property of the drawn rectangle, it holds between keys too,
not only at them.

### D6. Enlargement: `check` refuses, and says how to allow it

The enlargement of a raster picture is `S` measured in output pixels per source
pixel, `s0·z` with the area in output pixels. Within a segment `z` moves
monotonically between the two keys' zooms, so the peak is `s0` times the largest
key zoom (or `s0` without `view`). It is known exactly from data, so `check`
decides it without a browser:

    Still museum would be enlarged 1.38× in shot museum-reference (1175×781
    source pixels in the 1920×1080 frame area); its upscale allowance is 1.
    Set upscale on the still, choose area: stage, or use a larger source.

`render --width W` multiplies every enlargement by `W / output.width` and
refuses the same way before capturing. `preview` renders smaller than the
output and never exceeds it. `check` prints each picture's peak enlargement and
allowance. The manifest records both.

It refuses rather than warns because:

- Videomaker has no warning channel: `check` passes or stops, and a warning
  printed before an eight-minute render scrolls away.
- The fact is exact and known at `check`, which is where the house rules put
  such refusals.
- The fix costs one field that records the author's decision. An enlarged
  picture in a finished film is then always a choice written in
  `production.yaml` and carried into the manifest, never an accident of a
  layout or a `--width`.

The default allowance is 1: a still is never enlarged unless the author says so.
The evidence needs the allowance at once. The museum photograph fills a
1080-pixel frame only at 1.38×, while in the `stage` area it fits at 0.87×.

Clips follow the same rule with their decoded frame size. For SVG the rule does
not apply, and `upscale` is refused.

### D7. Clips: which frame, and the rate rule

Clip seconds count from the clip's first frame. `check` lists the clip's frame
presentation timestamps with ffprobe (`t_0 = 0 < t_1 < ...`, sorted into
presentation order) and its end `E`, the last timestamp plus that frame's
duration (or, if the duration is not reported, plus the previous interval).
For video time `T` in a cue that starts at `Ts = shot.start + from`, the clip
instant is `c = inPoint + (T − Ts)`, and the frame shown is the latest `n` with
`t_n <= c + 1e-9`: the frame on screen at that instant. This mapping lives in
`frameAt` (the timestamp list is part of the loaded episode), so it is pure and
works for any instant, any `--fps` and every preview sample.

The rate rule is sample-and-hold, nothing else. A film frame shows exactly one
source frame, the one a player would be showing at that instant. Frames are
dropped when the clip is faster than the film and repeated when it is slower.
They are never blended, interpolated or retimed. Every shown frame is a real
frame, and its time is correct to within one film frame, which is the film's own
time resolution. That holds for any constant or variable rate, including a 25
or 29.97 fps capture in a 30 fps film, so no rate is refused as a ratio. What
cannot be resampled truthfully is a clip for which "the frame on screen" is
undefined, and those are refused:

- timestamps missing, or not strictly increasing in presentation order:
  `Clip try-it has no usable frame timestamps; re-encode it`;
- interlaced video (a frame holding two instants; deinterlacing invents
  pictures): `Clip try-it is interlaced; deinterlace it deliberately first`;
- non-square pixels or a rotation tag, where the decoded frame would not be
  the picture the file presents without a transformation Videomaker would
  have to invent.

The cadence is recorded instead of judged: the manifest and preview report give
each clip's average source rate, the film rate, and how many source frames of
the span are dropped or shown more than once. Whether a 25-into-30 cadence
reads smoothly is for review. Blending frames is the only way to avoid it, and
that would invent pictures.

`check` also refuses, naming shot and cue:

- `inPoint` that is not finite or not `>= 0`;
- a clip shorter than its interval from its in-point:
  `inPoint + (to − from) > E`
  (`Clip try-it ends at 7.97 s, before 3.5 + 6 s needed by picture #1 in shot question-and-feedback`);
- when the cue runs to its shot's end and the next shot enters by a
  `shot-transitions` transition, a clip too short for the continuation as well
  (`d` for a dissolve, wipe or slide, `d/2` for a fade), stated the same way.

Clip sound is not played. The film's soundtrack is narration only until roadmap
item 10. A clip with an audio stream is accepted, and the manifest records
`audio: "not played"`.

### D8. The caption line (withdrawn at ratification; see below)

`caption` is drawn where and as the frame's `lower-third` overlay is drawn
(same position, size, colour and background plate, and the code-layout variant
in a code shot). It is part of the picture, so it appears and fades with it and
names what is shown ("Leonardo, Codex Atlanticus f. 1078r"). It is refused if it
contains a line break or is empty. If a `lower-third` overlay of the same shot
overlaps the picture's interval, it is refused too, since the two would sit in
one place: `Picture #0 caption overlaps a lower-third overlay in shot studied`.
`preview` refuses a caption wider than its area. The caption is not the
credit. Attribution goes to the release description (D11), following the
Leonardo films' rule that creator, licence and photo attribution belong there.

### D9. Fades

`fadeIn` and `fadeOut` are `{duration, ease?}`, with `ease` one of the five
names and defaulting to `smooth`. This is the spelling and default of
`shot-transitions`. For `fadeIn`, the layer's opacity at `local` is
`ease((local − from)/d)` until `from + d`. For `fadeOut` it is
`1 − ease((local − (to − d))/d)` from `to − d`. The opacity is the smaller of
the two, and 1 between them. The first frame of a fade-in shows the plain model
(opacity 0). The frame at `to` has no picture. A duration must be finite and
at least two frames at `output.fps`, and the two durations together must not
exceed `to − from`. Without fades a picture cuts in and out. A fade dissolves
the whole layer (plate and picture) over the posed model, so the model
beneath is the continuing timeline of D3.

### D10. What a picture may be

At `check` (`loadEpisode`), for each still and clip that a 0.4 episode declares:

- the file resolves inside the repository (`contained`, after `realpath`) and
  has a supported extension;
- raster stills: ffprobe must decode exactly one frame whose codec matches the
  extension (`png`, `mjpeg`, `webp`). An animated PNG or WebP, or a file that
  is not what its name says, is refused: `Still museum is not a single PNG,
  JPEG or WebP picture`. An animated picture would change with wall-clock
  time in the page, and no still may. The width and height are the decoded
  pixels. The page draws with `image-orientation: none`, so a JPEG's
  orientation tag is not applied, and the author sees a sideways photograph in
  preview and saves it upright. Orientation is thus never applied in the
  browser while the enlargement check ignores it.
- SVG stills: the root element must declare a `viewBox` of four finite numbers
  with positive size, which gives the intrinsic size and the aspect. Without
  one, a browser need not scale the drawing with its box:
  `SVG still frame-joints needs a viewBox; for width 420 and height 240 add viewBox="0 0 420 240"`.
  A conservative text scan refuses scripts, `foreignObject`, animation
  (`animate`, `animateMotion`, `animateTransform`, `set`, CSS `@keyframes`,
  `animation`, `transition`) and any reference outside the file (an `href` or
  `url(` not starting with `#`, and `@import`). It names the construct found.
  The page shows SVG through an `<img>`, which runs no script and fetches
  nothing, but a drawing that animates or needs an external file would not
  show what the author sees in an editor.
- clips: ffprobe must find a video stream of codec `h264`, `hevc`, `vp8`,
  `vp9` or `av1`, together with the timestamps and properties of D7.

GIF is not accepted, since no evidence asks for it and it is usually animated.

### D11. Provenance, frame identity and release readiness

The picture files are served by the asset server at fixed paths
(`/pictures/stills/<name>`, `/pictures/clips/<name>/<n>.png`) and nothing
else. The content-type table gains `.jpeg` and `.webp`. The build manifest
gains `pictures`:

- per still: path relative to the repository, SHA-256, format, width and
  height, `committed`, `credit`, `rights`, `upscale`, and the peak enlargement
  per cue;
- per clip: the same, plus codec, frame count, average rate, the extraction
  key, the span of source frames and the ffmpeg version, the dropped and
  repeated counts, and `audio: "not played"`.

`committed` is true when the file is tracked at the project's HEAD and has no
change in the working tree.

The frame cache identity adds `src/pictures.mjs` and each still's hash (as a
served file). For each clip it adds the clip's hash, the extraction key and the
ffmpeg version line, because the decoder turns the clip into pixels. The
resolved episode already in the identity includes every picture cue and the
timestamp lists.

Extraction (preview and render, never `check`): the source frames from the
frame shown at `inPoint` to the frame shown at the last instant needed
(continuation included) are decoded once, with their own timing and no rate
conversion, into lossless RGB PNGs at
`_build/clips/<key16>/<n>.png` beside an `index.json`. `key` hashes the clip's
SHA-256, the span, the decoding arguments and the ffmpeg version line. The
decoded count must equal the listed frames of the span, or it is refused:
`Clip try-it decoded 181 frames where 180 were listed; re-encode it`.
An existing complete extraction with a matching key is reused. The `_build/`
directory is already ignored in the project.

This extracts the frames of the span, not frames at the output rate as first
suggested. One extraction then serves preview's arbitrary instants and any
`--fps`, and the choice of frame stays in pure Node data. The cost is one PNG
per source frame of the span (a 60 fps capture in a 30 fps film decodes twice
the frames it shows).

Release readiness: `releaseReady` is additionally false when any picture shown
has a null `credit` or `rights` or is not `committed`, or when pictures are
shown and the description template lacks `{{pictureCredits}}`. That placeholder
becomes one line per shown picture, `name: credit`, with
`[PICTURE CREDIT PENDING: name]` for a null credit, as the pending URLs are
written. The manifest lists each reason under `pictureReleaseIssues`. A
rehearsal proceeds with all of them, as with null release URLs.

### D12. Frames, format and the transitions interaction

- `frameAt` gives every 0.4 frame `picture`: `null` outside a picture, or
  `{index, kind: 'still'|'clip', name, area, rect: [x, y, w, h], opacity,
  }` with, for a still, `view: {center, zoom}`, and for a clip,
  `frame: n` and `clipSeconds: c`. The tests of `keyframes-and-easing` and
  `shot-transitions` that deep-compare 0.4 frames are amended in this cycle to
  expect `picture: null`. 0.2 and 0.3 frames are untouched.
- `pictures` in a 0.2 or 0.3 episode is refused:
  `Pictures need format machinome-video-draft/0.4: shot museum-reference`.
- `shot-transitions`: the outgoing shot's continued frame is computed by the
  same function, so a picture whose `to` equals its shot's duration stays on
  through the continuation (D3 of that change). A still holds its last view, a
  clip keeps playing (D7 checks that it can), and the opacity holds its value at
  `to`, which is 0 after a `fadeOut`. An incoming shot's picture is seen through
  the transition at its authored times. The transition proofs of that change
  apply unchanged to frames with pictures.
- No Viewer API is required. The viewer receives the same calls.

### D13. What `preview` proves

For every picture, preview poses and saves stills at `from`, at each view key
(clamped to the last frame before `to`), at the midpoint of each fade and at
the last frame before `to`, and for a clip at its first and last frames. At
every picture sample:

- geometry: the page returns the area rectangle it measured, the picture's
  drawn rectangle and, for SVG and raster alike, the image's natural size. The
  stage rectangle must match D4. The drawn rectangle must equal the frame's
  `rect` times the area within 0.5 px. A raster natural size must equal the
  probed size, and an SVG's aspect must equal its `viewBox` aspect within 0.1 %;
- clip frame: the page returns the source frame index it displays, which must
  equal the frame's `frame`, and the image's natural size must equal the clip's;
- replay: one sample per picture is posed, then another instant, then again,
  and the pixels must match exactly;
- the enlargement actually drawn (drawn width over natural width, scaled to the
  output width) must not exceed the allowance.

The report records each sample's picture data and measurements. In tests (task
1.4), pixels prove what the geometry claims on a synthetic still and clip.
`preview` in production cannot decode meaning from a photograph, so it proves
geometry and frame identity, and the pixel proof lives in the test.

## Risks / Trade-offs

- **Rights.** The research copies that would show the sawmill's references are
  ignored files. The *Codex* copy is watermarked for study and consultation
  only, and the museum photograph's rights are recorded as unverified. The
  design lets a rehearsal show them and keeps `releaseReady` false. Whether even
  a private demo should show them is the pilot's call. The demo can use the
  project's own renders and drawings instead (tasks 3.1).
- **Decoder and browser as inputs.** A clip's pixels depend on the ffmpeg
  version, and a still's on Chromium's decoder and colour management (embedded
  ICC profiles are applied). Both are recorded in the manifest and in the frame
  identity, as the browser version already is. The exact replay check catches
  any nondeterminism within one run.
- **Stage constants duplicate CSS.** Mitigated by preview's measurement (D4),
  which refuses drift rather than tolerating it.
- **The SVG scan is textual and conservative.** It may refuse a benign drawing
  that mentions `animation` in a comment. The message names the construct, and
  the author removes it. SVG text uses the system fonts, recorded as today.
- **The carpentry SVG exports lack a `viewBox`,** so an author must add one to a
  copy. Whether Machinome's carpentry export should write one is a framework
  finding, recorded here and not acted on.
- **Covered viewer work.** Frames under a picture still pose and render the
  model. A long full-frame picture costs render time for nothing visible. This
  is accepted for purity (D3).
- **Clip cadence** (25 fps in 30 fps) shows uneven holds. It is recorded, not
  refused (D7).
- **Stacking under the masthead** (D3) may put the `MACHINOME` mark over a
  full-frame photograph. The review of the stills decides whether the pilot
  wants the chrome to hide under pictures, which would first need
  `shot-transitions` to move its layer.

## Migration Plan

Additive and opt-in by format 0.4 and the new fields. Every existing episode
parses and renders unchanged. Production `stills`/`clips` are ignored by 0.2 and
0.3 episodes. Reverting the tool commit makes an episode with `pictures`
refused (unknown shot field in 0.4), never rendered without its pictures.

## Open Questions

- Should a `frame` picture cover the masthead and progress rule? Proposed: no,
  because it is forced by `shot-transitions` D4. *Revolutions v2* says "full
  screen", which the pilot may read strictly.
- Default `area`: `stage` (the briefing's reading) or `frame` (what both
  *Revolutions v2* scenes ask for)?
- Keep `caption` (D8), or drop it and let authors use a `lower-third` overlay,
  which does not fade with the picture?
- Is sample-and-hold with recorded cadence (D7) acceptable, or should `check`
  refuse sources slower than the film that do not divide its rate evenly? The
  proposal argues that refusing would push authors to launder the same judder
  through a conversion.
- The demo's use of the watermarked *Codex* copy and the unverified museum
  photograph, even privately (Risks).
- Release gating by `committed` and credits (D11) extends `releaseReady`. The
  pilot may prefer the gate to be only recorded.

## Ratification (29 September 2026)

Ratified by the orchestrating agent as the campaign's review gate, under the
pilot's delegation, with these resolutions:

- **D8 withdrawn: no `caption` field.** A line naming the picture is a
  `lower-third` overlay, which already exists and which `text-animation` may
  give an entrance; one spelling for one thing. The closed list, the frame
  shape, the refusals and the preview checks lose their caption items. The
  examples above are corrected.
- **Open questions settled for now**, the pilot may revisit on the demo: a
  `frame` picture does not cover the masthead and progress rule (coherent with
  `shot-transitions`); the default `area` is `stage`; sample-and-hold with the
  cadence recorded (D7) stands; the release gate of D11 stands as designed (a
  rehearsal proceeds, `releaseReady` records why not).
- **The demo shows only the project's own renders and drawings** (the tracked
  `screenshots/`, the ignored `_evidence/` renders, a carpentry SVG given a
  `viewBox` in a copy) and, for a clip, a Videomaker render of an earlier demo;
  never the watermarked *Codex* copy or the museum photograph, whose rights are
  the pilot's to judge.
- The extraction of the span's source frames (D11) and the geometric zoom mix
  (D5) stand as designed: both are purer than the briefing's suggestions.
- Every 0.4 frame carries `picture`; the deep-equality tests of the two earlier
  cycles are amended here to expect `picture: null` (D12).
