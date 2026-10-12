# Implementation evidence

## Authority and scope

Ratified by the pilot on 29 September 2026 with the sibling changes; the viewer
contract is reconciled as recorded in `design.md` ("Ratification and
resolutions"). Planning commit `54ab2ec` precedes implementation, which builds
on `annotate-a-part` (format 0.3 and the shared viewer requirement). No viewer,
simulation or CAD changes; nothing committed to Leonardo, pushed or published.

## Red / green

Red, before implementation (`node --test`, 24 tests, 20 pass, 4 fail):

- `the active highlight is emitted ...`: `frameAt(...).highlight` was absent
  (`Expected values to be strictly deep-equal`).
- `invalid highlights are refused ...`: empty `parts` accepted
  (`Missing expected exception: /parts/`).
- `highlights require Viewer API 28`: `requiredViewerApi` returned 21.
- `test/render.test.mjs` failed to load: no `browserSession` export. To see the
  browser case itself fail, it was run against the pre-change tree `e8abc1c`
  with only that export added: preview passed without any highlight check and
  the test failed reading `highlightChecks` (`Cannot read properties of
  undefined (reading 'map')`).

Green after implementation: `node --test`, 26 tests, 26 pass, 0 fail. With an
API 28 double whose `highlight` recolours the canvas and whose `restore` puts
it back: preview passes the plain/lit/plain/lit checks and exact pixel replay;
posing 0, 0.6, 1, 1.6, 0.6 and 0 s records exactly `highlight, restore,
highlight, restore`, every call carrying `[['Feed','Pawl']]` and
`{color:'#bf531f', others:'ghost'}`. A double whose `restore` leaves the colour
changed fails (`Highlight did not restore exactly: pawls #0 at 1.00 s`); one
whose highlight changes nothing fails (`Highlight did not reach the pixels`);
the API 27 double is refused (`needs Viewer API 28 for highlight (shot
pawls); the selected viewer declares API 27`). The double also throws on a
second `highlight` while one stands, as the reconciled viewer does, and no
case triggered it.

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

Highlight results (from the preview report): both cues pass all three checks
on the real viewer: `ghost #0` at 6.50 s and `ghost #1` at 8.50 s, each
`changed`, `restored` and `reapplied`, as plain/lit/plain/lit captures. Stills:
`11-ghost.png` (`050ec51b02555d7b`), the ghost cue: the driving pawl and
ratchet in the accent tint, the timber frame, carriage and log translucent
around them; `13-ghost.png` (`0ec5f13146abf79a`), the dim cue: the holding pawl
tinted `#237c86`, the rest visibly darker than the unhighlighted
`14-ghost.png`. The water layer, hidden in that shot, stays hidden through the
ghost cue. Every rendered frame of the silent clip passed.

Consumer verification in the Leonardo repository (task 3.1) was not done: this
run was forbidden to commit to Leonardo. Whether the ghosted structure reads
as context and the tint draws the eye (4.1) awaits the pilot.
