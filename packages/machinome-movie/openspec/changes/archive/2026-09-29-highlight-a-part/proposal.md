## Why

The Leonardo release film *Revolutions* (`projects/Leonardo/videos/machinome-revolutions`)
shows what is inside the sawmill by hiding it: the `stroke` shot hides five layers
to "uncover the shaft, crank, rod and saw", the `pawls` shot hides four, and the
timber structure disappears in eight of its sixteen shots. Hiding removes the
context the narration relies on. The film's didactic draft
(`machinome-revolutions-v2`, shot `rotation-to-stroke`) says it outright: "Do not
hide the very supports that the narration is explaining." The pilot's stated
wish for the next film is highlighting a part with the rest dimmed or ghosted,
so the housing can be seen through instead of removed. Today the only
visibility control Videomaker has is `hiddenLayers` (the viewer's `setVisible`).

Viewer API 28 (proposed in parallel in machinome-viewer) adds
`highlight(paths, {color, others})`: it tints the named parts and keeps, dims or
ghosts the rest, and returns a function restoring every material. This change is
the Videomaker half: the screenplay field and its deterministic application.

## What Changes

- Shots gain optional `highlight` cues: shot-local `from`/`to`, the `parts` to
  lift (layer names or assembly paths), what happens to `others` (`keep`, `dim`
  or `ghost`) and an optional `color`, defaulting to the production accent.
- The page applies the active cue and restores at its boundaries and at every
  cut, so each frame depends only on its video time; preview proves the effect is
  visible and that restoring returns identical pixels.
- `hiddenLayers` keeps its meaning: hidden parts stay hidden while others are
  dimmed or ghosted, and highlighting a part the same shot hides is refused.
- Uses episode format `machinome-video-draft/0.3` and requires Viewer API 28,
  refused explicitly by `check`, `preview` and `render` against older viewers;
  0.2 episodes and episodes without highlights are unchanged.

## Capabilities

### New Capabilities

- `part-highlighting`: lift named parts and dim or ghost the rest for a timed interval.

### Modified Capabilities

None in baseline (`openspec/specs/` is empty). The visibility behaviour of the
unarchived production spec ("start with all parts visible, then hide those
layers") is preserved and composed with, not changed.

## Impact

`src/episode.mjs`, `src/timeline.mjs`, `src/film.js`, `src/render.mjs`
(preview checks), tests, `docs/FORMAT.md`, `README.md`. Needs machinome-viewer
API 28 (`highlight`). Shares the format 0.3 and viewer-requirement decisions with
`annotate-a-part` and `move-up-and-field-of-view`. Leonardo authors the consuming
shot in its own repository. No simulation, CAD or viewer code changes here.

## Non-goals

No outline or glow styles beyond the viewer's tint, no per-part choice of dim
versus ghost (one `others` mode per cue), no fading into or out of a highlight
(roadmap item 6), no simultaneous overlapping cues, no change to what
`hiddenLayers` means. No publication.
