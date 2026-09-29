# Implementation evidence

## Authority and scope

Ratified by the pilot on 29 September 2026 with the sibling changes; the viewer
contract is reconciled as recorded in `design.md` ("Ratification and
resolutions"). Planning commit `da2f5a5` precedes implementation, which builds
on `annotate-a-part` and `highlight-a-part`. No viewer, simulation or CAD
changes; nothing committed to Leonardo, pushed or published.

## Red / green

Baseline pin (task 1.1), run before the change: `constant up and field of view
are unchanged` passes, pinning the full `frameAt` objects at 0, 0.5, 1, 1.5, 2
and 3 s (`up` `[0,1,0]`, `fov` 37). It stays green after the change.

Red, before implementation (`node --test`, 33 tests, 28 pass, 5 fail):

- `field of view eases ...`, `up interpolates ...`: the 0.3 fixture was refused
  by the old rule (`Changing FOV/up within a shot is not supported`).
- `impossible or unsupported camera moves are refused ...`: the 0.2 message did
  not name the shot or format 0.3.
- `any change of up or field of view requires Viewer API 28 ...`:
  `requiredViewerApi` returned 21.
- `field of view and up reach the viewer at API 28 ...` (real browser): preview
  of the fov-sweeping shot passed with the API 28 double, without any lens
  check (`Cannot read properties of undefined (reading 'map')` on
  `cameraChecks`): before this change the page never set a later field of view.
- `below API 28 the page calls setView exactly as before` passed before and
  after, as a regression pin.

Green after implementation: `node --test`, 33 tests, 33 pass, 0 fail. With the
API 28 double (pinhole `project` from the field of view it was given): the lens
check passes at 0 s (fov 37) and 1.5 s (fov 20) within 2 %; `setView` at 0.75 s
receives `{camera, target, up: [0,0,1], fov: 28.5}`; an up change passes the
"above" check at both keys; a double ignoring `fov` is refused (`Viewer did not
adopt the requested field of view`); the API 27 double is refused (`needs
Viewer API 28 for camera up/field of view (shot pawls)`) and, for a 0.2 episode,
receives `setView` calls with exactly the keys `camera` and `target`.

## Unchanged episodes with the Viewer API 27 bundle (task 3.1)

Bundle: the primary machinome-viewer checkout's 0.7.1 build, `viewer API 27`,
SHA-256 `3e2cfb3dcb70e48c5edd89d82e267467b5db75508a323c9c618609cc56e8f5ab`,
not modified. Episodes: the sawmill rehearsal and *Revolutions*, from a scratch
clone of Leonardo `28b43bc` re-pinned to the current export (see
`annotate-a-part` evidence), previewed at 960 px into scratch build directories
with the pre-change tree (`da2f5a5`) and with this change's tree.

- Sawmill: 24 of 24 stills byte-identical before and after.
- *Revolutions*: the first run after the change matched 47 of 48 stills; the
  48th (`11-stroke`) differed in one pixel by 3 levels. Repeating showed the
  baseline itself is not byte-reproducible across processes: three further
  pre-change runs each differed from the first pre-change run in one or two
  stills, each by a single pixel (`47-invitation` at (467, 143), `03-river`,
  `14-pawls` at (591, 418) by up to 14 levels), and the post-change runs
  flickered at the same pixels. The third post-change run matched all 48 stills
  of the first pre-change run byte for byte. Within one process, pixel replay
  is exact in every run, as the preview's own check requires.

The requirement "stills are byte-for-byte identical" therefore holds as far as
the unchanged baseline can reproduce itself: this change introduces no
difference that the baseline does not also show between its own runs.

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

Lens results (from the preview report), shot `narrow`: at 10.00 s (fov 37) the
offset beside the target measures 5.080764 px against 5.080764 px expected; at
13.00 s (fov 20) 9.641179 px against 9.641179 px: the projected size follows
the requested field of view within 1e-12 relative, far inside the 2 % bound.
Every frame of the preview and of the 140-frame render read back the requested
field of view and up. Stills `15-narrow.png` (`c6111ac5b910b7b7`, fov 37) and
`17-narrow.png` (`e34bd9d1780536b7`, near fov 20) show the pawls growing with
the camera unmoved. No shot with a changing up was run on the real viewer; up
changes are covered by the double only.

Consumer verification in the Leonardo repository (task 3.2) was not done: this
run was forbidden to commit to Leonardo. Whether the zoom reads well in motion
(4.1) awaits the pilot.

## Findings out of scope

- Cross-process single-pixel nondeterminism of the real viewer under
  SwiftShader (above): same bundle, same code, same episode, different process.
  The frame cache and exact in-process replay are unaffected; a byte-for-byte
  comparison across processes must be repeated or allow for it. Not a
  Videomaker fix; worth recording for the viewer.
