# Independent consumer and film review — 29 September 2026

Codex, as the pilot's delegated adversarial reviewer and video operator, authored
Leonardo `videos/demo-graphic-overlays/episode.yaml` and `production.yaml`, then
ran check, preview and a real video render. This records agent review, not pilot
approval of the film's taste or publication. The project sources remain untracked;
generated media are ignored under that episode's `_build/`.

## Real-model result

The episode is three five-second shots: two moving pawls ringed in turn; a
drawn-on pointer and fading label; then two rope sections ringed and labelled
during a camera move. It uses the existing export pinned to
`28b43bce1b88446995f0ff231dd9075d1a839ab3`, with no model changes.

The viewer is the API 28 source-worktree bundle at `f040f45`, SHA-256
`a3fe03f2db691ff46ed3e3624eee57c57445d526d29530835d0df1f00dda095c`.
Preview at 960 pixels wide passed with 66 stills, 36 entrance/exit checks,
zero vacuous comparisons, eight exact entrance replay checks and a maximum
blend difference of one channel level. The overall replay and camera checks
passed. `preview/report.json` retains every measurement.

Selected ring geometry in viewport pixels, written as `(cx, cy, rx, ry)`:

- Moving driving pawl: at 0 s `(423.643, 280.898, 66.620, 88.068)`;
  at 2.466667 s `(416.306, 290.210, 68.878, 86.630)`.
- Large-radius rope reserve during camera motion: at 10 s
  `(597.435, 300.022, 46.965, 49.342)`; at 12.466667 s
  `(553.453, 306.935, 57.289, 63.372)`.
- Small-radius take-up: at 12.5 s `(569.777, 291.942, 25.103, 26.453)`;
  at 14.966667 s `(500.131, 296.835, 29.581, 33.581)`.

## Render and vision

Command: `node bin/videomaker.mjs render <episode> --viewer <API-28-bundle>
--width 960 --fps 30 --silent` from the `film-motion` worktree.

Video: `videos/demo-graphic-overlays/_build/silent-preview.mp4` in Leonardo.
H.264, 960 × 540, 30 fps, exactly 450 frames and 15 seconds, no audio.
SHA-256: `73b68c0e403e0a2482113d43bfe02ddd6f75ae0976b7eff0752590e70cc36404`.
Render identity: `c1a8aa361ff3e579dfbf69ee341e71b99d95fbc3f56db80b2ea9fc9dd31e19c0`.
There are at most two simultaneously partial fades (four subset captures),
on 130 of 450 output frames. The CLI reached frame 361 at 75 seconds; this is
a measured production cost, not a claim of realtime rendering. Frame-file
timestamps span 103.08 seconds from the first captured frame to the last.

Codex decoded and visually inspected 60 film frames at quarter-second cadence
in `review-first-half.jpg` and `review-second-half.jpg`, plus the individual
full-resolution preview frames. The first ellipse draws clockwise from its top,
encloses the driving pawl, and breathes modestly with its motion. The second
ellipse fades around the holding pawl. The pointer grows from its fixed words
toward the moving part, and the nearby label fades without jumping. The two
rope rings and labels remain attached and readable through the camera move.
No ring is clipped; no text leaves the frame; the masthead and progress rule
remain stable. The close pawl shot intentionally crops unrelated wheel and
saw-frame geometry, while each ringed target stays wholly visible. No creator,
copyright, licence or release URL is rendered into the film.

The draw-on and fade durations are legible in this short study; the ring stroke
and default spacing distinguish the target without obscuring it. No additional
restyle is required to validate the ratified feature.

## Adversarial findings resolved

- CSS opacity changed HTML glyph antialiasing, defeating the strict fade proof.
  Same-instant opaque subset composition passes the original tolerance; plain
  cues retain their former rendering path. Overlap costs are documented.
- A cue at shot-local 0.2 s in a shot beginning at 10 s was absent at global
  10.2 s because of subtraction rounding. A red-first regression and a narrowly
  scoped boundary correction fixed the real preview; cue ends remain exclusive.
- An entrance ending exactly at the exclusive cue end has no active full-mark
  endpoint. Its skipped endpoint is explicit, not a claimed passing comparison.
- Documentation now limits the unchanged plain-0.4 promise to arrows/labels
  and qualifies entrance-end assertions by cue activity.

The final suite and fresh legacy before/after comparisons are recorded in
`evidence.md`. Those checks must pass before sync/archive.
