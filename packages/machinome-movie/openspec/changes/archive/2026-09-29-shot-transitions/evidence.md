# Implementation evidence

## Authority and scope

Ratified on 29 September 2026 by the orchestrating agent as the campaign's
review gate, under the pilot's delegation (`design.md`, "Ratification"): the
field `ease`, the end rate under eased model segments, `transition` on every
0.4 frame (and the `keyframes-and-easing` equality test amended to expect
`transition: null`), fades not covering the masthead, `smooth` as the default
easing, the outgoing shot continuing, and the demo joining source and machine
by `fade` and model shots by dissolve, wipe and slide. Planning commit `263a3e8`
on branch `film-motion`; applied on `7e4e810`, whose `src/` is that of
`bc13655` (`keyframes-and-easing` implemented and archived). Second cycle of the
film motion campaign applied. No viewer, simulation or CAD change; nothing
committed to Leonardo, pushed or published.

The ratified decisions were implemented as written, with two implementation
findings that change how the page draws a transition frame but none of D1–D9's
decisions; both are under "Findings during implementation" below.

## Red / green

Pins (task 1.2), green by design and untouched: `0.2 episodes are unchanged`,
`constant up and field of view are unchanged` and `0.2 and 0.3 frames are
unchanged` (`test/workflow.test.mjs`), and the 0.3 fixtures of
`test/annotations.test.mjs`, `test/highlight.test.mjs` and
`test/camera.test.mjs`: run on the base before any source change, 8, 3, 3 and 4
pass, 0 fail; green again after the change. The ratified amendment of
`test/keyframes.test.mjs` ("a 0.4 episode without ease gives the frames of the
same episode in 0.3" now expects `{...frame03, transition: null}`) is red on the
base: `+ transition: null` missing from every 0.4 frame, 5 pass, 1 fail.

Red, before implementation:

- `test/transitions.test.mjs` (1.1, Node only): 7 tests, 1 pass, 6 fail. Five
  fail on the fixture itself, `Unknown shot field: fadeIn (shot code)` (0.4's
  closed shot list does not know the fields); the refusal test reports
  `Missing expected exception: /^Transitions need format
  machinome-video-draft\/0\.4: shot code$/` (a 0.3 episode with `fadeIn` is
  accepted and would render with cuts). `transitions raise no viewer
  requirement` passes by design (`requiredViewerApi` never looked at them) and
  is kept as a pin. A test that each curve's end slope is its derivative was
  added with the implementation of `endSlope` (below).
- `test/render.test.mjs` (1.3, real Chromium, viewer double): 8 tests, 6 pass,
  2 fail. `shots joined by every kind pass preview ...` fails with `TypeError:
  Cannot read properties of undefined (reading 'map')` (the report has no
  `transitionChecks`); `an arrow that runs to the cut ...` fails with
  `preview refuses` (actual `null`: preview never posed the outgoing shot past
  its end). Because of the browser slot, this red run was taken after 2.1 and
  2.2 (validation and timeline, Node only) and before any change to the page or
  `render.mjs`, which is what the two tests exercise; the six existing cases
  pass unchanged. The double's canvas colour follows model time only behind
  the new `timeColor` option.

Green after implementation: `node --test`, 59 pass, 0 fail (49 before this
change: 8 new Node tests, 2 new browser tests). The suite takes about 38 s
instead of about 10 s, almost all in the two new browser tests.

## What changed

- `src/timeline.mjs`: one shot-local function, `shotFrame`, makes the frame of a
  shot at any local time, and past the shot's end continues it (D3): model
  seconds `to + r·u` with `r = endRate(shot)`, the last segment's average rate
  times its curve's end slope; camera held at its last key; the overlays,
  annotations and highlight whose `to` is the shot's duration stay on; code
  complete without a cursor; its own hidden layers. Inside the shot the frame is
  computed exactly as before (0.2 and 0.3 frames are bit-identical; the pins
  prove it). In 0.4 every frame carries `transition`, `null` outside one
  (ratification), otherwise the field, kind, shot, outgoing shot, duration,
  easing, and `progress` and `direction` (dissolve, wipe, slide) or `color`,
  `plate` and `picture` (fades), with `outgoing`, the outgoing shot's complete
  continued frame, while it is seen (D6). The bounds of a transition are compared
  in video time, as shots' are; a fade's midpoint and a fade-out's last frame are
  settled within 1e-9 of their exact value so that the rounding of `t − start`
  cannot leave them a hair short of the plain colour.
- `src/easing.mjs`: `endSlope(name)`, the curves' slopes at their end in units of
  the average rate (`linear` 1, `smooth` 0, `in` 3, `out` 0, `in-out` 0), as
  the ratification lists them; a test checks each against the curve's
  derivative.
- `src/episode.mjs`: `transition`, `fadeIn` and `fadeOut` join the 0.4 shot
  list; each has its own closed list; every D7 refusal, with the design's
  messages, after all shots are otherwise validated (a transition reads the
  shots on both sides). The continuation check uses `endRate` and the shown
  duration (`d`, or `d/2` for a fade).
- `src/film.html`, `src/film.js`: a `#transition` layer after the code panel;
  the masthead and progress rule are raised above it only while a transition is
  drawn (`in-transition`), and hidden in `picture-only` captures. A new
  `film.compose` draws a transition frame from captures (below). Every
  `setFrame` first clears the layer; a `fresh` pose ends with the whole page
  repainted (below). Frames outside transitions are posed exactly as before.
- `src/render.mjs`: `pose` composes a transition frame from poses of the same
  instant, each through every existing check: a fade poses its picture once, a
  dissolve, wipe or slide poses the outgoing and then the incoming picture; each
  is captured without chrome and `film.compose` draws the captures (edge or
  offset `round(p·W)`) and the fade's plate under the live masthead and
  progress rule. Preview adds each transition's stills and D8's proofs,
  decoding the captures with a small PNG reader (`src/pixels.mjs`, used by
  preview only, not on the frame path); the highlight and lens comparisons pose
  their shot with `transition: null`. The frame identity already hashed
  `easing.mjs`, `timeline.mjs`, `render.mjs` and the served page files; no new
  module is on the frame path.
- `docs/FORMAT.md`: status, the hard-cut rule in "Timing and rendering
  semantics", the 0.4 closed lists and viewer note, and a new section "Joining
  shots" (fields, example, placement, continuation, drawing, colour, refusals,
  proofs, cost). `README.md`: set-up, `preview` and `render` bullets.

## Findings during implementation

1. **Chromium's partial re-raster makes a code panel's pixels depend on the
   previous pose (pre-existing).** Posing the same code frame twice in a row
   changes 7 channel values in the panel's leftmost pixel column (the subpixel
   fringe of the first glyphs, up to 9 levels), against posing it after any
   other frame. Reproduced on the base source (`src/` of `bc13655`) with no
   transition involved. It means a resumed render of a code shot can already
   differ from a continuous one in that column. The transition proofs and the
   fresh-session frame check found it. Fix, confined to transitions: every pose
   inside a transition, and every comparison pose of the proofs, is *fresh*: the
   page ends it by repainting the whole page (the background set to another
   colour for two animation frames and back for two), so the text is rastered
   whole and the pixels no longer depend on history. Frames outside transitions
   are posed as before, so existing films keep their exact pixels, and the
   pre-existing resume flicker in plain code shots remains; making every frame
   fresh would change existing films and is left to the pilot.
2. **A live WebGL canvas under the transition layer strips the masthead's
   subpixel antialiasing.** The first implementation, the design's "pose B with
   A's image in the layer", passed every proof on the viewer double but failed
   the dissolve proof on the real sawmill (largest difference 89, all of it in
   the masthead and series label): with a composited WebGL canvas beneath the
   layer, Chromium composites the raised masthead separately and draws its text
   in greyscale, so the chrome changed look for the length of every
   transition. Hiding the live stage while the transition is drawn restores it
   exactly (measured 0). So the page now draws every transition frame entirely
   from captures of the same instant: the incoming picture is captured like the
   outgoing one, and a fade's picture is captured and drawn under the plate. D6's
   "compose inside the page from poses of that instant only" is unchanged; the
   cost is one pose for a fade and two for a dissolve, wipe or slide (the design
   estimated one, two and three).

## Unchanged episodes, before and after (task 3.2)

Bundle: machinome-viewer worktree `film-annotations`, banner `machinome-viewer
0.7.1 - viewer API 28`, SHA-256
`a3fe03f2db691ff46ed3e3624eee57c57445d526d29530835d0df1f00dda095c`, copied to
the session scratchpad before the first run. "Before" ran from a scratch
extract of `7e4e810`'s `src/`, `bin/` and lock file, "after" from the worktree;
stills at 960 px.

- `demo-feed-mechanism` (0.3: lens moves, highlights, annotations): `check`
  passes before and after; 26 of 26 stills byte-identical.
- `demo-annotate-a-part` (0.3): `check` passes; 6 of 6 identical.
- `demo-keyframes-and-easing` (0.4, no transitions): `check` passes; 6 of 6
  identical.
- Sawmill rehearsal, the scratch copy re-pinned to the current export by the
  `keyframes-and-easing` cycle (0.2, model keyframes): `check` passes; 24 of 24
  identical.
- In every case `report.json` differs only in the hashes of `/film.js` and `/`
  (the page files this change edits).
- Code shots, which none of those episodes has: a scratch 0.2 film and a 0.3
  film (code, a model shot, code again with a highlight and an arrow) on a
  viewer double: every one of their 60 frames posed in order, as `render` poses
  them, 60 of 60 and 60 of 60 identical (their preview stills, 11 and 13, were
  also identical on an intermediate version of the page).
- All the comparisons above were repeated with the final source after the
  page's composition changed (finding 2), with the same results.
- The sawmill rehearsal and *Revolutions v2* fail `check` in place before and
  after with the same messages (`Model duration differs from production
  settings`; `Pin model.sourceRevision ...`), as the earlier cycles recorded;
  re-pinning them is the Leonardo repository's work.
- A scratch copy of the demo declaring format 0.3 is refused by `check`:
  `Transitions need format machinome-video-draft/0.4: shot sawmill`.

## Consumer episode (tasks 3.1–3.3)

`/home/asa/devel/machinome/projects/Leonardo/videos/demo-shot-transitions/`
(untracked; generated media only in its ignored `_build/`): format 0.4,
1920×1080, 30 fps, 31 s, on the `demo-feed-mechanism` production (sawmill
export at `28b43bc`, loop 1460 s) with the architecture excerpt
`model.py` lines 197–211 (`class WaterDrive`) added as `sourceCode`. Six shots,
as the ratification settles the demo (source and machine joined by `fade`,
model shots by dissolve, slide and wipe; tasks 3.1's "dissolve into the source"
is superseded by it):

| shot | time | join | picture |
|---|---|---|---|
| `sawmill` | 0–5 | `fadeIn: {duration: 1.5}` | whole sawmill, moving |
| `source` | 5–13 | `fade`, 1.2 s | architecture source typed, split layout |
| `saw` | 13–18 | `fade`, 1.2 s | closer moving mechanism |
| `drive` | 18–22 | `dissolve`, 1 s | the drive |
| `feed` | 22–26 | `slide`, 0.8 s, left | the feed |
| `closing` | 26–31 | `wipe`, 0.8 s, right; `fadeOut: {duration: 2}` | whole machine |

Each shot's top overlay names its join and runs to its end, so the outgoing
label stays on the continued picture through the next join.

`check` passes with the API 28 bundle. `preview` with it: 50 stills (19 for
the shots and typing cues, 31 for the seven transitions: 3 for each fade in or
out, 5 for each join), pixel replay exact, viewer API 28, and every transition
proved:

| transition | kind | largest difference | pictures differ | full colour | replay |
|---|---|---|---|---|---|
| `sawmill` fadeIn | fade | 0.94 | — | exact at 0 s | exact |
| `source` | fade | 0.50 | — | exact at 5.6 s | exact |
| `saw` | fade | 0.50 | — | exact at 13.6 s | exact |
| `drive` | dissolve (p 0.5) | 0.50 | yes | — | exact |
| `feed` | slide (480 px) | 0 | yes | — | exact |
| `closing` | wipe (480 px) | 0 | yes | — | exact |
| `closing` fadeOut | fade | 0.98 | — | exact at 30.97 s | exact |

Silent render (3.3): `render --width 960 --fps 30 --silent` with the API 28
bundle, 930 frames posed and checked in about 5.5 minutes (plain frames about 3
a second, transition frames several seconds each), 960×540, 31 s, frame cache
`3b8183ec19c3540d`; `_build/silent-preview.mp4` SHA-256
`db49786d411563f76d1d620c20a7c2a49964118e9028191194c3ee3e1669c3d8`, 930 frames
at 30 fps by `ffprobe -count_frames`. Frames decoded and inspected on both
sides of and inside every transition (0–45; 149–186; 389–426; 539–570;
659–684; 779–804; 869–929): the film rises from the plain paper on frame 0;
the sawmill fades to paper and the typed source comes up from it, never on
screen together; the saw comes back through the paper, still moving; the
dissolve shows the two views of the moving machine together, the outgoing
`fade` label fading as `dissolve` arrives; the slide pushes the drive view out
to the left with the feed view butted against it and the masthead unmoved; the
wipe's edge travels right revealing the whole machine; the last frame, 929, is
plain paper with the masthead and the full progress rule. How each kind reads
in motion is task 4.1, for the pilot.

## Findings out of scope

- Finding 1 above, for plain code shots: a resumed render can differ from a
  continuous one in the code panel's leftmost column. Making every pose fresh
  would fix it at the cost of about 60 ms a frame and of changing existing
  films' pixels in that column; the pilot's decision.
- Node's test runner counts `test/frame-fixtures.mjs` as a file with no tests;
  harmless.
