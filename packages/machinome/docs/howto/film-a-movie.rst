# Videomaker

Build narrated educational videos from a project's YAML screenplay and
Machinome simulation. The first working consumer is Leonardo's hydraulic
sawmill: an 84-second rehearsal with scripted cameras, assembly reveals,
AI narration and aligned captions. The release-film source study adds real
Python typing beside the animation and expressive feminine narration.

This is a local production tool, not a publishing service. It supports posed
models with a normalized animation timeline; running/clocked machines are
refused. The viewer executes the actual mechanical model.

## Set up

Requires Node 22+, FFmpeg/ffprobe, and a Machinome Viewer API 21 bundle with
`setView` and on-demand rendering. Viewer API 27 is used by the release-film
study. Linux/Chromium software rendering is the tested environment.

```sh
npm ci
npx playwright install chromium
```

Put the ElevenLabs key in this repository's ignored `.env`:

```dotenv
ELEVENLABS_API_KEY=your_key
```

The key is read only by the speech command and is never sent to the browser,
written into episode sources or included in build manifests. A key with text
to speech permission is enough; listing voices is not required when a voice ID
is supplied. The first episode uses George / `eleven_multilingual_v2`.
The source study uses Jessica / `eleven_v3` with lossless `pcm_24000` input.

## Produce an episode

Every consuming project owns `videos/<episode-id>/episode.yaml` and
`production.yaml`. Read the screenplay directly: narration and plain-language
directions appear together in each shot. See [the source contract](docs/FORMAT.md).

From this repository in the development workspace:

```sh
node bin/videomaker.mjs check ../projects/Leonardo/videos/hydraulic-sawmill/episode.yaml

node bin/videomaker.mjs speech ../projects/Leonardo/videos/hydraulic-sawmill/episode.yaml

node bin/videomaker.mjs preview ../projects/Leonardo/videos/hydraulic-sawmill/episode.yaml \
  --viewer ../machinome-viewer/machinome_viewer/widget/dist/machinome-viewer.js

node bin/videomaker.mjs render ../projects/Leonardo/videos/hydraulic-sawmill/episode.yaml \
  --viewer ../machinome-viewer/machinome_viewer/widget/dist/machinome-viewer.js
```

- `check` validates YAML, timelines, named cameras/layers/evidence, the real model
  duration, and the export's source revision.
- `speech` generates narration through ElevenLabs, caches each segment and its
  character timestamps, checks it fits, then mixes audio and writes captions.
  It makes chargeable requests only for missing cached segments.
- `preview` creates three stills per shot, a midpoint for each typing cue, and
  a contact sheet. It also
  checks real-browser pixel replay, requested camera readback, canvas layout and
  invalid camera refusal. No speech generation occurs.
- `render` requires cached speech and renders the film. Add
  `--width 960 --fps 10 --silent` for a quick silent video.
- `build` combines speech generation/cache reuse and final rendering.

Without `--viewer`, the bundle beside the model manifest is used. Older
exports must be regenerated with the new viewer or use the explicit bundle.
Paths are arguments, not assumptions about a neighboring workspace. The
loopback asset server exposes the selected model assets and film page only.

## Output

Each episode's ignored `_build/` contains:

- `rehearsal.mp4`: H.264 video and AAC narration, no burned or embedded subtitles.
- `rehearsal.srt`, `captions.srt` and `captions.json`: separate timed subtitles.
- `narration.wav` and `audio/`: mixed audio, cached segments and alignments.
- `thumbnail.png`, `storyboard.jpg`, `preview/`: presentation review assets.
- `description.md`: draft release copy with missing public URLs explicitly marked.
- `rehearsal-manifest.json`: resolved screenplay/settings, model and viewer
  hashes, audio hashes, browser/encoder versions, font record and encoded checks.
- `frames/<content-hash>/`: reusable frames; rerunning an unchanged render
  resumes capture. Inputs include the model assets, viewer, screenplay, captions
  and renderer. Changing visual inputs starts a new frame cache.

The final encode is checked for its frame count, dimensions and audio stream.
Generated media stays out of Git. Missing public URLs make `releaseReady`
false but do not prevent a rehearsal. Nothing uploads or publishes.

## Timing and revisions

Model seconds are independent of video seconds. Linear spans or explicit model
keyframes can slow a mechanism or align a stroke with a word. The sawmill's
completed pass is 296 seconds; the 84-second film uses seconds 8–80.
That was the first rehearsal export; the current release-film export records
1460 seconds. Production always verifies the selected manifest's duration.

If speech overruns a shot, the command stops after caching it and names the
needed duration. Edit YAML timing and cues, then rerun. Audio is never truncated
or silently stretched. Cached segments are keyed by voice/model, text, neighbor
text, voice settings and pronunciation replacements; editing narration may
regenerate adjacent segments to preserve delivery continuity.

The narrator says “mah-SHEEN-ohm,” as confirmed by the pilot. The episode uses
a speech alias while keeping “Machinome” in captions. Beat timestamps come
from actual synthesized speech, not estimated reading speed.

## Validation and boundaries

`npm test` covers parsing refusals, stale model duration, timeline continuity,
camera interpolation, visibility reset, model keyframes and speech timestamps.
The originating sawmill's browser preview exercises the real viewer and pixels.
See [production evidence](docs/first-rehearsal.md) for the actual run.

Behavioral changes use this repository's OpenSpec records. The inaugural
[`first-narrated-rehearsal`](openspec/changes/first-narrated-rehearsal/proposal.md)
change was adopted during implementation at the pilot's request. It records
what was already built and how it was verified, not prior spec-first approval.
Future behavioral changes start with a proposal before implementation.

Original CAD, evidence and video sources belong to each project repository.
The viewer's public API and tests belong to its separate repository. This
tool neither modifies mechanical geometry nor implements a second simulation.
No remote is configured. A distribution license for Videomaker itself remains
unselected; the Leonardo sources follow the gallery's AGPL-3.0-only license.
