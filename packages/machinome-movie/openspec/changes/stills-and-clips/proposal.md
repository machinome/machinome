## Why

Leonardo's films talk about pictures they cannot show. Two episodes show the
gap:

- The draft *Revolutions v2* (`projects/Leonardo/videos/machinome-revolutions-v2`)
  has two scenes that the renderer cannot produce. `museum-reference` (330–347 s)
  asks for the "REAL MUSEUM PHOTOGRAPH, FULL SCREEN ... fitted without cropping
  important machinery, against the dark background ... Hold still; do not pan
  and zoom while viewers compare the details". `question-and-feedback` (347–369
  s) asks to "Start on the real reference photo through the question. Then
  match-cut to the reconstruction", and "On 'Try the simulation' show actual
  pause/scrub/inspection controls", which is a recording of the interactive
  simulation: a clip. Its README says the normal renderer "would show a model
  where this draft calls for source or the photograph" and that the "museum
  still and interactive viewer capture remain production work". Its production
  file already records the photograph (`credits.museumPhoto`, with
  `rights: Unverified for publication`) and its private research copy
  `_reference/hydraulic_sawmill/milan-overall.jpg`.
- The sawmill rehearsal (`projects/Leonardo/videos/hydraulic-sawmill`) says
  its machine is one "studied by Leonardo da Vinci" and cites
  *Codex Atlanticus* 1078r and the Milan museum model in
  `credits.historicalReferences`, but only as URLs. The films must never fetch
  them. The evidence names that its shots do carry (`reconstruction`, `model`,
  `kinematics`, ...) are documents and source code, not pictures, so nothing a
  viewer sees on screen comes from them. The project holds research copies of
  both references under the ignored `_reference/hydraulic_sawmill/`: the folio
  as a 1427×2048 JPEG, with the saw sketch in its upper half, and the museum
  photograph as 1175×781. It also holds its own renders under
  `_evidence/hydraulic_sawmill/` and `screenshots/`, and its own SVG carpentry
  drawings in the frame export. Moving from the whole folio onto the saw sketch
  is the pan-and-zoom this change adds. The *Revolutions v2* photograph, which
  the author wants held still, is its still without motion.

Roadmap item 9 (stills and clips) is the last cycle of the film motion
campaign. It builds on `keyframes-and-easing` for its keys and easing names and
uses the cue entrance and exit spelling ratified with `graphic-overlays`.

## What Changes

- `production.yaml` gains named `stills` (PNG, JPEG, WebP or SVG) and `clips`
  (MP4 or WebM). Each names a file inside the project repository, its `credit`
  and `rights` (text, or null while unresolved) and, for raster pictures, an
  optional `upscale` allowance.
- A 0.4 shot gains `pictures`: timed cues that show one still or clip for a
  shot-local interval over the model `stage` (the default) or the whole
  `frame`, with `fit: contain` (the default) or `cover`, and optional
  `enter`/`leave` fades spelled as every 0.4 cue spells them
  (`{kind: fade, duration, ease?}`). A still may carry `view` keys
  (`{at, center, zoom, ease?}`) for a pan-and-zoom, eased with the campaign's
  names and interpolated so that the zoom's fixed point stays still on screen.
  A clip carries an `inPoint`.
- A picture covers its whole area on an opaque plate of `style.background`.
  The model beneath keeps its shot timeline and is posed every frame, so
  cutting back mid-shot is seamless. Annotations and highlights are refused
  while a picture is up, text overlays stay above it, and the masthead and
  progress rule stay above it, as they do above transitions.
- A still is never enlarged beyond its source pixels unless the author allows
  it: `check` refuses a peak enlargement above the still's `upscale` (default
  1), computed at the output size, and `render --width` checks again.
- A clip frame is the clip frame on screen at that clip instant. Clip frames
  are chosen from the clip's own timestamps and never blended or retimed. The
  frames of the span in use are decoded once, losslessly, into
  `_build/clips/<key>/`, keyed by the clip's hash, the span and the decoder.
  Clip sound is not played; audio beyond narration is roadmap item 10.
- `check` refuses the new fields in 0.2 and 0.3 episodes, unknown names and
  fields, files outside the project, unsupported, animated or scripted
  pictures, intervals and keys outside the shot, views that would show plate
  inside a covered area or cut off an uncovered one, enlargement above the
  allowance, and clips too short for their interval (including the
  continuation `shot-transitions` shows past a shot's end).
- `preview` samples each still at its interval ends and view keys and each clip
  at its first and last frames, proves each picture's geometry and clip frame,
  and replays one instant of each picture exactly.
- The build manifest records each picture's path, hash, size, credit, rights,
  whether it is committed at the project's HEAD, and each clip's extraction.
  The frame cache identity includes them. `description.md` gains a
  `{{pictureCredits}}` placeholder. `releaseReady` stays false while a shown
  picture's credit or rights are unresolved or its file is not committed.

## Capabilities

### New Capabilities

- `stills-and-clips`: named stills and clips shown in a shot, pan-and-zoom on
  stills, clip insertion from an in-point, and their provenance.

### Modified Capabilities

None in baseline. `keyframe-easing` (implemented and archived) is used as it
stands. The 0.4 frame shape gains `picture`, as `shot-transitions` added
`transition`.

## Impact

`src/pictures.mjs` (new: loading, probing, validation, geometry, clip frame
choice, extraction), `src/episode.mjs` (production maps, shot field, 0.4 closed
lists, refusals), `src/timeline.mjs` (the active picture in 0.4 frames),
`src/film.html` and `src/film.js` (the picture layer), `src/render.mjs`
(serving, extraction, preview proofs, frame identity, manifest, release
readiness, description), `bin/videomaker.mjs` (`check` reports each picture's
enlargement), tests, `docs/FORMAT.md`, `README.md`. No Viewer API change. The
Leonardo project authors the demo episode in its own directory. ffmpeg and
ffprobe, already required, read and decode the pictures.

## Non-goals

- No picture-in-picture, split screen or picture over part of the stage. That
  is roadmap item 4 (multiple views) and item 12 (free layouts), and no episode
  asks for it: *Revolutions v2* wants the photograph "full screen" and the
  model "never side-by-side".
- No clip sound, music or ducking (item 10).
- No pan-and-zoom on clips, no rotation, no colour grading, filters, Ken Burns
  presets or picture presets beyond the named file declarations.
- No GIF or animated image, no fetching from URLs, no screen-capture tool
  inside Videomaker (a clip is a file the project holds).
- No decision on the rights of any image. Videomaker records what the author
  declares and withholds release readiness.
- No publication.
