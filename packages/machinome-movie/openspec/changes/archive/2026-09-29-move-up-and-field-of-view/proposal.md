## Why

The pilot's stated wish for the next Leonardo release film, *Revolutions*
(`projects/Leonardo/videos/machinome-revolutions`), includes camera moves that
change the field of view or the up direction: narrowing onto a part without
moving the camera, or leveling a view as it travels. Every camera the film uses
already carries `up` and `fov` in `production.yaml`, but `check` refuses a shot
whose keys differ in either ("Changing FOV/up within a shot is not supported"),
and the page only gives the viewer an up and field of view once, at mount.
No *Revolutions* shot has been authored with such a move yet; this change is cut
from the wish, and ratification should name the shot that will use it (the
pawls close-up, narrowing from the `pawls` view, is the proposed candidate).

Viewer API 28 (proposed in parallel in machinome-viewer) makes `up` and `fov`
settable on every `setView` call and returns them from `view()`.

## What Changes

- Within a shot, camera keys may name presets whose `fov` or `up` differ. The
  field of view interpolates with the same smoothstep as position and target;
  up interpolates by direction and is normalized.
- The page passes the frame's up and field of view on every `setView` when the
  viewer supports it, and preview reads them back and proves, by projecting
  world points, that a field-of-view change reaches the picture.
- A pure-constant up and field of view render exactly as today; a test pins it.
- Refusals: adjacent keys whose up directions are opposite; a frame whose up
  lies along the viewing direction; a 0.2 episode changing up or field of view
  within a shot (unchanged); any up or field-of-view change against a viewer
  below API 28.
- Episode format `machinome-video-draft/0.3` carries the lifted rule; 0.2 keeps
  its rule and semantics.
- Found while reading the code: the page never applies a later shot's up or field
  of view, so a 0.2 episode cutting between presets that differ would today render
  with the first shot's values without any error. No existing episode does this
  (all Leonardo cameras use 37 degrees and `[0, 0, 1]`). After this change such an
  episode renders correctly with Viewer API 28 and is refused with an older one.

## Capabilities

### New Capabilities

- `camera-up-and-field-of-view`: camera moves that change field of view and up.

### Modified Capabilities

None in baseline (`openspec/specs/` is empty). This lifts the constant up/FOV
statement recorded in the unarchived inaugural change and in FORMAT.md for 0.3.

## Impact

`src/episode.mjs` (validation), `src/timeline.mjs` (interpolation),
`src/film.js` (setView arguments and readback), `src/render.mjs` (readback and
projection checks), tests, `docs/FORMAT.md`, `README.md`. Needs machinome-viewer
API 28 (`setView` with `up`/`fov`, `view()` returning them, `project`). Shares
format 0.3 and the viewer requirement with `annotate-a-part` and
`highlight-a-part`. No new episode field.

## Non-goals

No per-key `up`/`fov` numbers in the screenplay (cameras stay named presets in
`production.yaml`), no orbit paths, no "frame this part" automatic framing, no
easing choice beyond the existing smoothstep, no multiple views (roadmap items
3's remainder, 4 and 6). No publication.
