## Context

`frameAt` picks the camera keys around the shot-local time, eases
`u*u*(3-2*u)` and mixes `position` and `target`; it returns `up` and `fov` of the
left key's preset unmixed. `validateEpisode` refuses a shot whose successive
keys' presets differ in `fov` or `up`. `film.js` mounts the viewer with the first
frame's `up` and `fov` and afterwards calls `setView({camera, target})` only, so
`frame.up` and `frame.fov` are never used after mount, including across cuts.
`render.mjs`'s `pose` reads back `camera` and `target` and refuses a mismatch.

Viewer API 28 contract used here: `setView({camera, target, up?, fov?})` adopts
all four and renders; `view()` returns all four; `project([x,y,z])` gives the
viewport CSS pixel position for the current camera, or null behind it.

## Goals / Non-Goals

Let a named-camera move change the field of view and the up direction smoothly
within a shot, keep every constant-up/FOV episode pixel-identical, and prove the
change reaches the picture. Not goals: new camera vocabulary in the screenplay,
orbits, auto-framing, other easings.

## Decisions

### D1. No new screenplay field: presets carry it

```yaml
# production.yaml
cameras:
  pawls:       {position: [145, 410, 400], target: [135, 0, 332], up: [0, 0, 1], fov: 37}
  pawls-tight: {position: [145, 410, 400], target: [135, 0, 332], up: [0, 0, 1], fov: 20}
# episode.yaml, format machinome-video-draft/0.3
    camera:
      - {at: 0, preset: pawls}
      - {at: 4, preset: pawls-tight}   # hold position, narrow the view onto the pawls
```

Camera keys keep `{at, preset}`. Allowing `up`/`fov` numbers on a key was
considered and rejected: AGENTS.md keeps technical settings in `production.yaml`,
and a key override would be a second spelling of a camera that the named presets
already express. If the pilot wants overrides, they are a small later change.

### D2. Interpolation

Between keys `a` and `b` with ease `e` (the existing smoothstep):

- `fov = a.fov + (b.fov - a.fov) * e`. Presets already lie in `(0, 180)`.
- `up`: if `a.up` and `b.up` are identical arrays, the frame carries that array
  exactly as authored, unnormalized, so constant-up episodes produce the same
  frame data as today. Otherwise both are normalized, mixed component-wise with
  `e`, and the result normalized.
- `frameAt` keeps returning them in its existing top-level `up` and `fov`
  fields, now interpolated instead of the left key's values; `view` keeps only
  `camera` and `target`. A constant-up/FOV episode's frame objects are therefore
  identical to today's, field for field.

Component-wise mixing then normalizing is not constant angular speed; it is
the same easing the author already sees on position, the result is always a
unit vector, and with the refusal below it never passes through zero.

### D3. Refusals

At `check`:
- 0.2 episodes keep "Changing FOV/up within a shot is not supported", now adding
  "; use format machinome-video-draft/0.3 with Viewer API 28".
- 0.3: adjacent keys whose normalized up vectors have a dot product below -0.99
  are refused ("Camera up reverses between keys in shot <id>; add an intermediate
  preset"), since the mixed vector would pass near zero.
- 0.3: for shots whose up changes, every output frame is evaluated (pure, cheap)
  and a frame whose up is within about 0.5 degrees of the viewing direction is
  refused with the shot and time, before the viewer would refuse it mid-render.

### D4. The page and the viewer requirement

`requiredViewerApi(e)` (shared with the sibling changes; see `annotate-a-part`
D5) returns 28 with reason `camera up/field of view (shot <id>)` when any two
camera presets used by the episode's shots differ in `up` or `fov`, within a
shot or across a cut. This covers the cross-cut gap found in Context.

`film.js` calls `setView({camera, target, up, fov})` when the viewer declares API
28 or later, and `setView({camera, target})` exactly as today below it (the gate
guarantees such an episode needs no change after mount). `setFrame` returns the
read-back `up` and `fov` too; `pose` refuses a field of view differing by more
than 1e-6 degrees or an up direction differing (after normalization) by more than
1e-6, when the viewer is at 28 or later.

### D5. Proving the picture changed

For each shot whose field of view or up changes, preview poses the shot at each
key where a change starts and ends and, through the page, projects two world
points: the camera target `T` and `T + s·r`, where `r` is the camera's unit
right vector and `s` is 1 % of the camera-to-target distance. With viewport height
`H` in pixels, the measured pixel distance must equal
`(H / 2) · s / (d · tan(fov / 2))` within 2 % at each instant, `d` being the
camera-to-target distance: proving the projected size follows the requested
field of view. For an up change, `project(T + s·up)` must lie above `project(T)`
on screen at each instant. Failures keep the stills.

## Risks / Trade-offs

- A field-of-view change with a fixed position reads as a zoom, which the craft
  treats differently from a dolly; that is an editorial choice for review.
- Changing up rolls the horizon; motion review decides whether it is comfortable.
- The pinhole formula in D5 assumes a symmetric perspective camera with vertical
  field of view, as three.js uses; if the viewer ever used a different model the
  check would fail loudly rather than pass wrongly.

## Migration Plan

No existing episode changes: all use 37 degrees and `[0, 0, 1]`. For them the
frame data are identical (pinned by test), the page's calls are identical below
API 28, and preview stills under the unchanged API 27 bundle are compared
byte-for-byte before and after the change. Authors opt in with format 0.3 and a
second preset. Reverting the tool commit restores the within-shot refusal.

## Open Questions

- Which *Revolutions* shot uses the move; the proposal assumes the pawls
  close-up, and the pilot confirms at ratification or names another.

## Ratification and resolutions (29 September 2026)

The pilot ratified this change with `annotate-a-part` and `highlight-a-part`;
the shared D5 was implemented by `annotate-a-part`. The consuming *Revolutions*
shot remains the pawls close-up proposed above; authoring it is Leonardo's work
in its own repository. Where the implementation departs from, or sharpens, the
text above:

- **Up normalization per shot (D2 sharpened).** "Identical arrays carry
  exactly" is applied to the shot, not to the pair of keys: in a shot whose
  keys all share one `up` array it is carried as authored (constant-up
  episodes keep identical frame data); in a shot whose `up` changes, every
  frame's up is a unit vector, including the hold after the last key. Applied
  per pair, the hold would have jumped from a normalized to an unnormalized
  spelling of the same direction.
- **Reconciled viewer contract.** `view().up` returns exactly what was supplied,
  not normalized, so the readback in `pose` compares normalized directions
  (within 1e-6), as D4 already specified; `fov` within 1e-6 degrees.
  `setView` refuses an up parallel to the view direction and a field of view
  outside (0, 180); `check` refuses both earlier (0.5 degrees, presets in (0,
  180)). `project` returns off-canvas coordinates in front of the camera and
  `null` only at or behind the camera plane; the D5 check fails on a null.
- **D4's requirement** is computed against the first camera the episode uses
  (the page mounts with its up and field of view): every shot using a preset
  whose field of view or up direction differs from it is named, so a cut
  between lenses names the shot after the cut, and a shot holding the changed
  lens is named too.
- **The 0.2 refusal** now names the shot: `Changing FOV/up within a shot is not
  supported: shot <id>; use format machinome-video-draft/0.3 with Viewer API 28`.
- **D5's instants** are each changing pair's first key and its second key,
  clamped to the shot's last output frame when the key sits at the cut; the
  canvas height is the `H` of the formula; results are in the preview report
  as `cameraChecks`.
