# Episode source contract — draft 0.2

Status: an authoring format exercised by one screenplay, not a working renderer.
The user reads and edits the same YAML that the future production tool consumes.
No executable episode code, imports, expressions or generated screenplay copy.

## Read the screenplay first

`videos/<episode-id>/episode.yaml` is the entry point. Its `format` is
`machinome-video-draft/0.2`. It contains `id`, `title`, `status`, `learningGoal`,
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
- `audio`: provider/model/voice, direction, pronunciation notes and timing notes.
- `style`: background, foreground, accent, font, caption placement and safe inset.
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
Equal endpoints hold a pose. For the first episode, `timeMode: normalized-loop`
means the viewer gets `simulationSeconds / expectedDurationSeconds`. The future
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
`top`, `lower-third`, or `center`. These are screen labels, not world-tracked
annotations. Narration captions occupy the bottom safe area separately.
Framing and text placement need visual review at the final aspect ratio.

Narration timing remains an editorial target until speech is generated and
measured. Align speech and captions, then revise shot timing and affected cues
together. Never truncate narration or silently stretch it to fit. Silent tails
are allowed. Mechanical cut/advance cues must stay tied to model time.

## Evidence and provenance

Every evidence name must resolve to a project file. Sources support the claim
or visual intent; they do not certify the current model. Before final rendering,
pin the tested model revision and record the export, viewer version, episode
revision, audio settings, generated audio hashes and output settings in a build
manifest. Cached audio is the reproducible input; regeneration may differ.
