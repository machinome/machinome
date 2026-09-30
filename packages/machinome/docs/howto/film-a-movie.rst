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
study. Episodes in the draft format 0.3 that point at parts (`annotations`),
highlight them (`highlight`) or change field of view or up between cameras
need Viewer API 28, available in the machinome-viewer source checkout but not
yet declared by a published release; `check`, `preview` and `render` refuse them against an
older bundle. Format 0.4 needs no newer viewer than the cues it uses: easing
and transitions between shots run on Viewer API 21, and rings, being
annotations, need Viewer API 28 as annotations do. Text animation is page-only
and adds no viewer requirement. Stills and clips are page-only too; FFprobe
checks their frames and timestamps, while FFmpeg extracts clip frames for
preview and render. Linux/Chromium software rendering is the tested environment.

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
In draft format 0.4, a shot with pinned `code` may opt into `layout: source-only`
to fill the existing main picture area with that literal, typed source instead
of the usual source/model split. Without the opt-in, both old layouts remain
unchanged. The film's current style and chrome remain; this is not a dark-theme
or multi-range source mode. Source-only refuses model-target annotations,
highlights and covering pictures rather than silently hiding them.

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
  duration, and the export's source revision. For a 0.3 episode that needs
  Viewer API 28 it also reads the selected bundle's `viewer API` banner. An
  episode with spoken reveals or source emphasis needs its cached speech first:
  run `speech` before `check`. `check` reads the verified alignment but never
  generates speech. For format 0.4 pictures it also reads the project media,
  refuses unsafe or unfilmable assets, and prints each peak enlargement and
  allowance plus clip rate and dropped/repeated cadence. It does not extract
  clip frames or start a browser.
- `speech` generates narration through ElevenLabs, caches each segment and its
  character timestamps, checks it fits, then mixes audio and writes captions.
  It makes chargeable requests only for missing cached segments.
- `preview` creates three stills per shot, a midpoint for each typing cue, and
  a contact sheet. It also
  checks real-browser pixel replay, requested camera readback, visible canvas
  layout on model/split shots and positive fitted source visibility on source-only
  shots, without calling projection through a hidden canvas visible lens proof. It also checks
  invalid camera refusal. Annotated shots add stills at each arrow or label's
  start, quarters and end; every posed frame refuses an annotation whose part
  is off screen or whose text leaves the frame. Each highlight cue is posed
  with and without its cue and must change the pixels and restore them exactly.
  Each transition between shots (format 0.4) adds stills at its first frame,
  quarters, midpoint and last frame, and is proved in pixels against the plain
  pictures it is made of: a dissolve blends them within 2 levels, a wipe and a
  slide reproduce them exactly, a fade reaches exactly its colour, and a
  revisited instant replays exactly. A ring (format 0.4) is refused on any
  frame where its part is not wholly on the model stage or the ring leaves the
  frame. Each annotation's entrance and exit adds stills at its first frame,
  midpoint and end while the cue is active, and is proved in pixels against the same instant with the
  mark drawn plainly and not drawn: a fade's midpoint is the blend its easing
  predicts within 2 levels, a draw-on's midpoint shows part of its stroke and
  not the rest, an entrance starts from nothing, its end and an exit's start
  are the mark drawn plainly, and a half-drawn instant replays exactly. No
  speech generation occurs. Format 0.4 text animation also reports
  `revealChecks`, `fadeChecks` and `emphasisChecks`: it verifies drawn word
  counts, same-instant title fade states over the moving model, source marks,
  title bounds and exact replay. Its `pictureChecks` save keyed still views and
  clip frames, verify page geometry and source frame identity, replay a visible
  still/clip exactly, and compare picture fades at the same model instant.
- `render` requires cached speech and renders the film. Add
  `--width 960 --fps 10 --silent` for a quick silent video. Measured text still
  requires the cached take with `--silent`; neither render
  nor silent build purchases speech. An FPS override that skips a revealed word
  is refused. A frame inside a transition is composed from captures of the same instant: a fade costs one
  pose and capture, a dissolve, wipe or slide two, each several times a plain
  frame's time. A picture with `n` simultaneous partly faded annotations needs
  `2^n` same-instant captures to preserve exact text pixels; schedule review
  renders accordingly. Picture fades similarly compose opaque and absent
  same-instant captures. `render --width` rechecks any authored `upscale`
  allowance before opening the browser.
- `build` combines speech generation/cache reuse and final rendering.

Without `--viewer`, the bundle beside the model manifest is used. Older
exports must be regenerated with the new viewer or use the explicit bundle.
Paths are arguments, not assumptions about a neighboring workspace. The
loopback asset server exposes the selected model assets, film page and, for
format 0.4 pictures, the referenced project media and extracted clip frames.

## Output

Each episode's ignored `_build/` contains:

- `rehearsal.mp4`: H.264 video and AAC narration, no burned or embedded subtitles.
- `rehearsal.srt`, `captions.srt` and `captions.json`: separate timed subtitles.
- `narration.wav` and `audio/`: mixed audio, cached segments and alignments.
- `thumbnail.png`, `storyboard.jpg`, `preview/`: presentation review assets.
- `description.md`: draft release copy with missing public URLs explicitly marked.
- `rehearsal-manifest.json`: resolved screenplay/settings, model and viewer
  hashes, audio hashes, browser/encoder versions, font record, encoded checks,
  and picture provenance/cadence with `pictureReleaseIssues`.
- `clips/<content-hash>/`: lossless extracted source frames and their index;
  unchanged source files and decoder settings reuse an extraction.
- `shot-cache/shot-v1/`: complete, integrity-checked shot generations, plus
  assembled global-frame sequences for encoding. A first render captures every
  shot. Later renders reuse complete shots whose actual frame requests and
  reached visual inputs are unchanged; a changed shot and a following shot
  that composites it as outgoing may be recaptured. The manifest's `cache`
  record lists each shot's key, generation, originating capture and frame
  counts. A hit verifies every PNG's hash and dimensions before reuse. An
  interrupted or damaged shot is recaptured whole, while other completed shots
  remain reusable. Old `frames/<content-hash>/` directories are left untouched
  but are not imported into this cache.

The shared cache key includes the mounted first frame, so changing the first
shot can conservatively recapture all shots. It also includes the model, viewer,
film page, rendering code, browser, the known regular/bold film and mono font
faces in the tested environment, style, dimensions, FPS and duration. Only
media actually reached by a shot enters that shot's key;
unused stills/clips and release copy do not force a visual recapture. Captions
remain external, so SRT/audio-only changes reuse PNGs and produce a fresh MP4.
The output manifest is authoritative only when its `outputSha256` matches the
MP4 at `output`; a publication interrupted between those two paths leaves a
visible hash mismatch and a recoverable prior film at
`<label>.mp4.previous-<id>`. Preflight and measured-take checks rerun on
every render; a reused shot inherits its frame-level browser pose checks from
its identical-input, attested capture.

The final encode is checked for its frame count, dimensions and audio stream.
Generated media stays out of Git. Missing public URLs make `releaseReady`
false but do not prevent a rehearsal. Nothing uploads or publishes.
Shown pictures whose credit or rights are unresolved, whose files are not
committed, or whose description template lacks `{{pictureCredits}}` also make
`releaseReady` false. The placeholder expands to `name: credit` lines (with
an explicit pending marker for missing credit); it is not a rights judgement.

## Timing and revisions

Model seconds are independent of video seconds. Linear spans or explicit model
keyframes can slow a mechanism or align a stroke with a word. In format 0.4 a
model keyframe or a camera key can name an easing curve (`linear`, `smooth`,
`in`, `out`, `in-out`) for the segment that ends at it, so a mechanism can leave
a hold gently or settle into a pause while every key stays exact. The sawmill's
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
