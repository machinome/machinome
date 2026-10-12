# Implementation evidence

## Authority and scope

Ratified by the pilot on 29 September 2026 together with `highlight-a-part`
and `move-up-and-field-of-view`, with D2 amended (the anchor of a part is the
centre of its on-screen rect, not the viewer's ray-cast point) and the viewer
contract reconciled as recorded in `design.md` ("Ratification and
resolutions"). Planning commit `b506f8e` precedes implementation. This change
implements the shared D5 (format 0.3 beside 0.2, `requiredViewerApi`, refusal on
mount, `check` reading the bundle banner). No viewer, simulation or CAD code
changes here; nothing was committed to the Leonardo repository, pushed or
published.

## Red / green

Red, before any implementation (`node --test`, 20 tests, 17 pass, 3 fail):

- `test/annotations.test.mjs` failed to load: `The requested module
  '../src/episode.mjs' does not provide an export named 'confirmViewerApi'`.
- `0.2 episodes are unchanged`: the pinned 0.2 frames matched (the pin is green
  by design), and the 0.2 episode carrying `annotations` was accepted:
  `Missing expected exception`.
- `an arrow follows a moving part ...` (real browser, API 28 double): no
  annotation geometry in the preview samples: `preview samples the cue at its
  start, quarters and end`.

Green after implementation: `node --test`, 22 tests, 22 pass, 0 fail. The
browser case proves, with a viewer double whose part rect moves with model time
on a flat-colour canvas: preview passes with exact pixel replay; the arrow's
anchors at 0.875 s and 1.625 s differ and each lies inside that instant's rect;
the screenshot pixel two pixels back from the tip along the shaft is the accent
colour; a label on a world point sits above its projection; the same episode
with the double at API 27 is refused (`needs Viewer API 28 for annotations
(shot pawls); the selected viewer declares API 27`); a double whose rect goes
null mid-cue is refused (`Annotation target is not on screen: pawls #0 'Pulls'
at 1.25 s`).

## Real-browser evidence with the Viewer API 28 bundle

Bundle: machinome-viewer worktree `film-annotations` build declaring `viewer
API 28` (banner `machinome-viewer 0.7.1 - viewer API 28`), SHA-256
`a3fe03f2db691ff46ed3e3624eee57c57445d526d29530835d0df1f00dda095c`, built from
viewer commit `49e50f3` plus that worktree's uncommitted move-up-and-field-of-view
work, taken when its `API-28-READY` marker appeared (29 September 2026, 09:36
UTC) and copied to a scratch file so it could not change mid-run. It is the
viewer's source, not a published release.

Episode: a scratch test episode, `film-annotations-test`, in a scratch clone of
Leonardo `28b43bc` (never in the Leonardo repository): format 0.3, 1920×1080,
14 s, the current sawmill export by absolute path, production based on the
sawmill rehearsal's `production.yaml` plus the *Revolutions* `pawls` camera, a
`pawls-tight` preset (same position, fov 20) and the `feed`, `foundation`,
`carriage` and `rope-1` layers. Shot `pawls` (0–5 s, model 436–438 s, the
downstroke) carries an arrow "Pulls one tooth" at `[Feed mechanism, Driving
pawl]` (place `[0.12, 0.3]`) and a label "Rope 1" on `rope-1`; shot `ghost`
(5–10 s) highlights the driving pawl and ratchet with `others: ghost`, then the
holding pawl with `others: dim, color: "#237c86"`; shot `narrow` (10–14 s) keys
`pawls` to `pawls-tight` over 3 s. Preview at 960×540; stills and reports are in
the session scratch directory, not kept in Git.

- `check` with this bundle passes and prints `Viewer API 28 required for
  annotations (shot pawls), highlight (shot ghost), camera up/field of view
  (shot narrow); ... declares API 28`. With the API 27 bundle `check` refuses
  (`This episode needs Viewer API 28 for annotations (shot pawls), highlight
  (shot ghost), camera up/field of view (shot narrow); the selected viewer
  declares API 27. ...`) and `preview` refuses on mount with the same message
  before capturing any still.
- `preview` with this bundle passes: 18 stills, exact pixel replay, invalid
  camera preserved, viewer API 28.
- `render --width 960 --fps 10 --silent` passes: 140 frames posed and checked,
  `silent-preview.mp4` SHA-256
  `6f4adc8e92d7801295a36a2a4162b30cc99701156b40f381633ee65971a6eec0`.
- The unchanged sawmill and *Revolutions* episodes also preview with this
  bundle (from API 28 the page sets up and field of view on every frame and
  reads them back): sawmill 24 of 24 stills byte-identical to the API 27
  baseline; *Revolutions* 45 of 48, the other three differing in one pixel each
  at exactly the pixels where the API 27 baseline flickers between its own runs
  (see `move-up-and-field-of-view` evidence).

Annotation results (from the preview report):

- The arrow's anchor is the centre of the driving pawl's rect at every sample,
  and moves with the pawl: (423.5, 281.0) inside rect (384.5, 226.8, 78.1×108.4)
  at 0.30 s, (419.0, 286.8) at 1.25 s... (415.6, 291.1) inside (374.7, 238.1,
  81.8×106.1) at 4.67 s; start `01-pawls.png` (`b43ff9557239a7f5`), midpoint
  `04-pawls.png` (`9a49a1aaaec37da0`), last frame `07-pawls.png`
  (`e27eee0196c06b2e`). The tip lands on the pawl in the stills.
- Tip steadiness (design open question D2): posing every 10 fps frame of the
  cue (44 frames), the tip moves at most 0.43 px and on average 0.30 px per
  frame at 960 px, 12.8 px in all; no jump. The rect-centre anchor is steady.
- The label "Rope 1" on `rope-1` (`Ratchet to reduction shaft`, a long diagonal
  rope) sits at its rect's centre (849.6, 416.0) of a 659×311 rect, which lies
  off the rope, at the lower right of the frame. This is the risk the design
  foresaw for slender diagonal parts, now observed: such a label needs a
  `point` target or a shorter part. Recorded for the pilot's review.
- Every one of the 140 rendered frames passed the on-screen and text-in-frame
  checks.

Consumer verification in the Leonardo repository (task 3.1) was not done: this
run was forbidden to commit to Leonardo, so the scratch episode stands in for
the *Revolutions* pawls shot. Legibility, placement and motion (4.1) await the
pilot.

## Findings out of scope

- None of the Leonardo episodes passes `check` against the current sawmill
  export (Leonardo `28b43bc`): the export's source revision moved, the sawmill
  rehearsal's 296-second duration is stale (the intended guard), and its
  `structure` layer names `Frame and guides/Timber stand and guides`, renamed
  `Fixed timber structure` in the frames-and-mates refactor. For comparison the
  episodes were checked from a scratch clone with those three settings patched;
  the Leonardo repository was not changed. Re-pinning the episodes is the
  Leonardo repository's work.
