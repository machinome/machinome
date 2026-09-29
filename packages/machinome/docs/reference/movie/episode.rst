# Episode source contract — drafts 0.2 and 0.3

Status: 0.2 is implemented and used by every Leonardo episode; 0.3 is a draft
that adds cues needing Viewer API 28 (see "Format 0.3" below). Both remain
provisional formats.
The user reads and edits the same YAML that the production tool consumes.
No executable episode code, imports, expressions or generated screenplay copy.

## Read the screenplay first

`videos/<episode-id>/episode.yaml` is the entry point. Its `format` is
`machinome-video-draft/0.2` or `machinome-video-draft/0.3`. It contains `id`, `title`, `status`, `learningGoal`,
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
to model seconds, interpolating linearly between them. The first key is at zero
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
keys interpolate position and target with smoothstep easing. The first is at
zero, keys increase strictly, and the last cannot exceed the shot's duration.
Hold the last key to the end. This episode keeps up and field of view constant.
Shot boundaries are hard cuts; no crossfade or automatic framing is implied.

`hiddenLayers` describes the complete shot visibility state: start with all
parts visible, then hide those layers. Do not accumulate state from earlier shots.

Overlay `from`/`to` values are shot-local, half-open intervals. Positions are
`top`, `lower-third`, or `center`. Overlays are screen labels, fixed on the frame;
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

## Format 0.3 and the viewer it needs

`machinome-video-draft/0.3` accepts everything 0.2 does, with the same meaning,
plus the cues below. They are accepted only in 0.3: a 0.2 episode carrying one is
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
- `kind`: `arrow` or `label`.
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
the model by wall-clock time. Named cameras currently share a fixed up and FOV.

## Evidence and provenance

Every evidence name must resolve to a project file. Sources support the claim
or visual intent; they do not certify the current model. Before final rendering,
pin the tested model revision and record the export, viewer version, episode
revision, audio settings, generated audio hashes and output settings in a build
manifest. Cached audio is the reproducible input; regeneration may differ.
