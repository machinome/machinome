# Episode source contract — draft 0.1

Status: authoring proposal exercised by one source episode, not a working API.
The `.mjs` entry point default-exports a JSON-compatible object with
`format: 'machinome-video-draft/0.1'`. Importing it must not render, access the
network, generate speech, write files or manipulate a live viewer.

## Envelope

- `id`, `title`, `status`, `learningGoal`: editorial identity and intent.
- `output`: `width`, `height`, `fps`, `durationSeconds`.
- `model`: episode-relative `manifest`, `expectedDurationSeconds`, `timeMode`,
  `sourceRevision` and `readiness`. A null revision marks unpinned source.
- `credits`: creators, copyright, license, historical references.
- `release`: public simulation/source URLs and description template. Null URLs
  are allowed in drafts and block a release bundle. Do not silently substitute
  localhost or an intended remote for a public address.
- `style`: declarative colors, background, caption placement and credit lines.
- `audio`: requested voice style, unselected provider/model/voice, pronunciation
  notes. Provider selection and generation are separate later work.
- `cameras`: named world-space camera `position`, `target`, `up` and `fov`.
- `layers`: named arrays of root-relative assembly paths. Each path is an array
  of exact sibling names, excluding the document root's name.
- `narration`: ordered `{id, text}` beats.
- `shots`: ordered shot records defined below.

## Shot records

`{id, start, end, simulation, camera, hiddenLayers, narrationId, overlays, evidence}`

Times are seconds. Shots cover `[0, output.durationSeconds)` contiguously with
no overlap. The final frame is at `(frameCount - 1) / fps`, not at the duration.
Each shot is a complete visibility state: start from all parts visible, then
hide its named layers. Do not accumulate hidden parts across shots.

`simulation: {from, to}` maps video seconds linearly to model seconds inside
the shot. Equal endpoints hold a pose. The first episode uses a posed model:
`timeMode: 'normalized-loop'` means call the viewer's external time interface
with `simulationSeconds / expectedDurationSeconds`. The adapter must verify
the loaded document's loop duration. Never pass seconds directly to a normalized
time setter. Never use wall-clock playback or wrap the endpoint to zero.
Machines with memory need a future explicit replay/checkpoint contract; this
format does not pretend their state is an arbitrary time coordinate.

`camera: [{at, preset}, ...]` uses shot-local seconds. One key holds a camera;
multiple keys interpolate position and target linearly with smoothstep easing
between keys. The first key is at zero, the last cannot exceed shot length.
This episode keeps up and field of view constant. Shot boundaries are hard cuts;
there are no implied crossfades, orbits, refocusing or camera resets.

`overlays: [{from, to, text, position}]` uses shot-local seconds and half-open
intervals. Positions are `top`, `lower-third`, or `center`. Overlays are screen
text, not claims of world-space tracking. Narration captions occupy the bottom
safe area separately. Credit overlays may use line breaks. Do not obscure the
mechanism being discussed; framing needs visual review at the final aspect ratio.

`narrationId` references one narration beat. Shot timing is an editorial target,
not a claim that generated speech fits. Measure and align the actual speech,
then revise shot timing and all affected cues together. Never truncate a line
or silently stretch audio to make it fit. Silent tails are permitted.

`evidence` lists episode-relative project files supporting the visual or claim.
They document intent, not proof of current validation. Before a final render,
pin the tested model revision and record the export, viewer version, episode
revision, audio settings, generated audio hashes and output settings in a build
manifest. Cached audio is the reproducible input; regeneration need not be identical.
