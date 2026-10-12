## Why

The next Leonardo release film, *Revolutions* (`projects/Leonardo/videos/machinome-revolutions`
and its didactic draft `machinome-revolutions-v2`), explains parts that move.
Its `pawls` shot says "Pull · advance one tooth" and "Return · hold that progress"
in a caption at the top of the frame while the two pawls the words are about
move somewhere below it; the draft's `two-rope-reduction` shot asks to "Label
rope 1 / rope 2 if helpful", and the sawmill rehearsal's narration says "Follow
the rod". Today an overlay can only sit at `top`, `lower-third` or `center`, so
nothing on screen can point at a part or stay beside it as it moves. The pilot's
stated wish for the next film is arrows that follow a moving part.

Only the viewer knows where a part is on screen. Viewer API 28 (proposed in
parallel in machinome-viewer) reports a part's on-screen bounds and a visible
point on it, and projects a world point, for the current pose. This change is the
Videomaker half: the screenplay field an author writes beside the narration, and
the page that draws it.

## What Changes

- Shots gain optional `annotations`: timed `arrow` and `label` cues aimed at a
  part (a layer name or one assembly path) or a world `point`, with text placed
  in safe-area units. An arrow's tip and a label follow the target every frame.
- The timeline stays a pure function of video time: it emits the active cues;
  the page resolves their screen positions from the posed viewer and draws them.
- `check` refuses malformed or unresolvable annotations before rendering;
  `preview` and `render` refuse a frame whose annotation target is not on screen
  or whose text leaves the frame.
- The episode format becomes `machinome-video-draft/0.3`. A 0.2 episode still
  parses and renders exactly as before; a 0.2 episode carrying `annotations` is
  refused rather than silently rendered without them.
- Episodes that use annotations require Viewer API 28; `check`, `preview` and
  `render` refuse them against an older viewer with a message naming the field,
  the shot and both API numbers. Episodes that do not use them keep working at 21+.

## Capabilities

### New Capabilities

- `part-annotations`: arrows and labels that follow a part or a world point.

### Modified Capabilities

None in baseline: `openspec/specs/` is empty and the inaugural production spec
remains in an unarchived change. This change adds to the overlay behaviour; the
existing `top`/`lower-third`/`center` overlays are unchanged.

## Impact

`src/episode.mjs` (format, validation, path checks, viewer requirement),
`src/timeline.mjs` (active cues), `src/film.js` and `src/film.html` (resolution
and drawing), `src/render.mjs` (API gate, per-frame checks, preview samples),
`bin/videomaker.mjs` (`check` reads the selected bundle's declared API),
tests, `docs/FORMAT.md`, `README.md`. Needs machinome-viewer API 28
(`partOnScreen`, `project`). The Leonardo project authors the consuming shot in
its own repository. No simulation, CAD or viewer code changes here.

## Non-goals

No animated entrances (fade, draw-on, scale), rings, boxes or free-standing
graphics: those are roadmap items 6 and 7 and wait for their own episode need.
No automatic label layout or collision avoidance, no 3D text, no annotation in
the code panel, no general keyframing. No publication.
