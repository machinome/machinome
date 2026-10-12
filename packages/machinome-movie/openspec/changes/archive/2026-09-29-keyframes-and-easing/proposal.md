## Why

The pilot's first wish for the next films (transitions, arrows, highlights)
named general keyframes with easing as the foundation (roadmap item 6): as soon
as anything but the camera moves, it needs a curve. Today only the camera
eases, always with one smoothstep, and model keyframes (`simulation.keyframes`)
interpolate linearly, so every change of mechanical speed is a jolt.

The release film *Revolutions* (`projects/Leonardo/videos/machinome-revolutions`)
shows both jolts in two adjacent shots:

- `machinome` (80.5–94.5 s): "Restore the complete assembly in the same held
  pose, then resume motion." Its keys hold model second 453 until 3.733 s and
  then run linearly to 461, so the machine leaps from rest to full speed in one
  frame. It wants to start gently: an `in` curve on that segment.
- `genome` (94.5–107 s): "Move briefly, then freeze at an intermediate phase as
  the voice says pause." Its keys run linearly from 461 to 466.8 at 6.899 s and
  then hold, so the mechanism stops dead at full speed. It wants to settle into
  the pause: an `out` curve. The same shot's camera travels from `mechanism` to
  `linkage` starting at the cut; smoothstep leaves the first second after the cut
  almost still (3 % of the move), so the cut reads as a held frame before the
  move begins. A move that is already travelling and settles on the linkage is
  an `out` curve on the camera.

The draft *Revolutions v2* asks for the same camera settle in
`ratchet-and-pawls` ("then settle on both pawls"), and the campaign demo
`demo-feed-mechanism` asks its `establish` shot to "push in slowly over the
shot", a steady `linear` push that smoothstep turns into a start and a stop.

Items 5, 7, 8 and 9 of the film motion campaign will each need a progress
curve or a keyed value. This change gives them one vocabulary and one helper
instead of four inventions.

## What Changes

- A shared module `src/easing.mjs`: five named curves (`linear`, `smooth`,
  `in`, `out`, `in-out`), refusing any other name, and a keyframe helper that
  interpolates a number or a vector between keys with a per-segment easing.
  `smooth` is today's smoothstep, bit for bit.
- Camera keys take an optional `ease`: the curve of the move that ends at that
  key, default `smooth`. Position, target, field of view and up follow it.
- Model keyframes take an optional `ease`: the curve of the segment that ends
  at that key, default `linear`. Keys stay exact; model time still never
  decreases, because none of the five curves overshoots.
- Episode format `machinome-video-draft/0.4` is accepted beside 0.2 and 0.3,
  with everything 0.3 means. `ease` is accepted only in 0.4; a 0.2 or 0.3
  episode carrying one is refused, naming the shot. In 0.4 a shot, its
  `simulation`, its model keyframes and its camera keys refuse unknown fields,
  so a misspelled `eas`, or a field of a later campaign cycle this build does
  not know, is never silently ignored.
- 0.2 and 0.3 episodes keep their exact frames; a test pins them literally.
- No new Viewer API: easing changes only the values the page already sends.

## Capabilities

### New Capabilities

- `keyframe-easing`: named easing of camera moves and model time, the shared
  easing vocabulary, and format 0.4.

### Modified Capabilities

None. The baseline `camera-up-and-field-of-view` requirement that field of view
and up change "with the same easing as position and target" stays true: they
follow the key's `ease` exactly as position does.

## Impact

`src/easing.mjs` (new), `src/timeline.mjs` (camera weight, model time through
the helper, 0.4 frames carry the 0.3 cues), `src/episode.mjs` (format 0.4,
the format comparisons that today test "is 0.3", validation of `ease` and of
closed field lists), `src/render.mjs` (frame-cache identity includes the new
module), tests, `docs/FORMAT.md`, `README.md`. `src/film.js`, `src/film.html`,
`bin/videomaker.mjs` and the viewer are unchanged. The Leonardo project authors
the consuming demo episode in its own repository; whether *Revolutions* itself
moves to 0.4 is the pilot's decision.

## Non-goals

No `spring`, `bounce`, `hold`, stepped or overshooting curves, custom curve
presets or per-key tangents or speeds: no episode asks for them, and an
overshooting curve would break "model time never decreases". No `ease` on a
plain `simulation: {from, to}` span (two keys already say it), on typing cues,
overlays, annotations or highlights (see design D6). No transitions, entrances,
text animation or stills: campaign items 5, 7, 8 and 9 build on this change in
their own proposals. No viewer change. No publication.
