# Implementation evidence

## Authority and scope

Ratified on 29 September 2026 by the orchestrating agent as the campaign's
review gate, under the pilot's delegation (`design.md`, "Ratification"): one
spelling `enter`/`leave: {kind, duration, ease?}` for every cue's arrival and
departure in 0.4, the wording `Unknown entrance field` / `Unknown exit field`,
and the scope as cut (ring only; fade and draw-on entrances; fade exits).
Planning commit `4edad8e` on branch `film-motion`; applied on `6417f97`, whose
`src/` is that of `2885a45` (`shot-transitions` implemented and archived after
`keyframes-and-easing`). Third cycle of the film motion campaign applied,
before `text-animation` and `stills-and-clips`. The pixel comparison that
`shot-transitions` added lives in `src/pixels.mjs` (`decodePng`,
`largestDifference`, `at`, `chromeMask`); this change reuses it and adds its
own proofs beside it, not a second comparison.

## Red / green

Pins (task 1.2), run on the base before any source change:
`test/annotations.test.mjs` 3 pass, and the Node-only suite (annotations,
workflow, keyframes, transitions, highlight, camera, easing, source-scenes,
speech) 47 pass, 0 fail. The whole `frameAt` objects of the annotated 0.3
fixture at 0.25, 1 and 1.5 s, and of the same fixture declared 0.4 (which adds
only `transition: null`), were printed from the base timeline and pinned
literally in `test/graphic-overlays.test.mjs` ("the annotated 0.3 frames, and
the same fixture in 0.4, are unchanged"): green on the base.

Red, before implementation:

- `test/graphic-overlays.test.mjs` (1.1, Node only): 11 tests, 3 pass, 8 fail.
  The four fixture tests fail on the fixture itself, `Invalid annotation #0 in
  shot pawls: kind must be arrow or label` (0.4 does not know a ring); the
  refusal test reports it where `kind must be arrow, label or ring` was
  expected; the format test reports that a 0.3 episode with a ring is refused
  as an unknown kind (`kind must be arrow or label`) instead of being asked for
  format 0.4; the three proof tests (1.3's Node part) fail with `TypeError:
  proveMark is not a function`. Passing by design: the pins above, "a 0.4 cue
  without enter, leave or padding is emitted exactly as the same cue in 0.3"
  and "rings and entrances need no newer viewer than annotations do", kept as
  pins.

- `test/render.test.mjs` (1.3, real Chromium): the first combined run had 70
  pass and 3 browser failures. A ring reached the old label-only `cue.offset`
  path in `film.js`; entrance proofs had no `entranceChecks`; and frame-time
  ring refusals were absent. These were implementation failures, not changes
  to the spec or pixel tolerance.

Green after implementation: `npm test` ran 75 tests, 75 pass, 0 fail on 29
September 2026. The new Chromium cases prove moving ring geometry and accent
pixels, a clockwise half-drawn ring, a drawn arrow whose words remain visible,
fade-in and fade-out blends within 2 levels, exact replay, both ring refusals,
and the exclusive cue boundary (a whole-cue entrance records `enter-end` as
skipped because `to` is not active). `test/annotations.test.mjs` and the literal
0.3/0.4 frame pins remained green. A following Node-only test of two
simultaneous overlapping fades with an opaque intervening label passed (12/12
overlay tests). The final `npm test` run passed 77/77 after the new
composition test, fractional-boundary regression and scope narrowing were
all present. `git diff --check` and `openspec validate graphic-overlays
--strict --json` also passed.

Chromium evidence changed one rendering mechanism while retaining the
ratified pixel promise: CSS opacity on an HTML label's plate/text switched its
glyphs from subpixel to grayscale antialiasing. Against the plain opaque mark,
the fade midpoint differed by up to 40 levels, above the 2-level limit.
`src/render.mjs` now captures the same instant with every partially fading
mark fully drawn or absent, keeping all other cues in authored order, and
`film.js` blends those opaque screenshots by their opacity weights. The
resulting browser fade proof passes at the original 2-level limit; no legacy
cue path or tolerance changed. A picture with `n` simultaneous partly faded
marks costs `2^n` captures. `stage()` hashes both `/film.js` and `/` (film.html)
into `info.hashes`, which the render identity includes; `pixels.mjs` is also
hashed explicitly. The Leonardo demonstration's actual overlap count and
render time are recorded with consumer verification, not inferred here.

The first Leonardo `preview` reached `ropes #1 enter-start at 10.20 s` and
found no cue: subtracting the shot's 10 s start from 10.2 s yielded a value
just below the authored `from: 0.2`. A regression proved that failure red,
then green in Chromium after settling the comparison within `1e-9` seconds
for rings and cues with new 0.4 fields only. The `to` boundary stays exclusive.
The 0.2, 0.3 and plain 0.4 annotation comparison path remains exactly as it
was. The consumer preview after this correction passed: 66 stills, 36 entrance
checks, largest blend difference 1 level, zero vacuous checks and 8 exact
midpoint replays.

## Consumer and legacy comparison

The 0.4 Leonardo `demo-graphic-overlays` preview passed against the API 28
bundle in `machinome-viewer/WTs/film-annotations`, commit `f040f45`, bundle
SHA-256 `a3fe03f2db691ff46ed3e3624eee57c57445d526d29530835d0df1f00dda095c`.
At most two marks fade partly at once; 130 of the 450 rendered video frames
contain a partial fade, so the largest subset is four captures for one picture.
The 15-second, 960×540, 30 fps silent feature film has 450 frames and SHA-256
`73b68c0e403e0a2482113d43bfe02ddd6f75ae0976b7eff0752590e70cc36404`;
frame capture took 103.08 seconds. The orchestrator's visual inspection is in
`root-review.md`, separate from the automated evidence here.

Using that same bundle and width 960, both older 0.3 demos passed `check` and
fresh `preview`. Numbered PNGs were compared by SHA-256 against the detached
`6417f97` base run recorded in the consuming project's ignored
`videos/demo-graphic-overlays/_build/legacy-6417f97.json`: all 6/6
`demo-annotate-a-part` and 26/26 `demo-feed-mechanism` stills were byte
identical. No unmatched numbered stills remained.

The optional 0.2 baseline attempt with `machinome-revolutions` could not reach
preview on the current content: `check` refuses, `Pin model.sourceRevision to
the export source-revision.txt before rendering`. That episode was left
untouched; this pre-existing refusal is not evidence of a 0.2 pixel difference.
