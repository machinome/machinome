# Scripted camera evidence — 19 September 2026

Originating consumer: Leonardo hydraulic sawmill's 84-second educational film,
directed by the independent Videomaker tool. The project needs camera changes
without reloading, retaining its posed time and assembly reveals.

- Six camera tests failed before implementation, covering detached input copies,
  invalid vectors and coincident position/target. They pass after scriptedView
  validation was added. Invalid requests are validated before view mutation.
- The API 21 setView handle uses the existing camera framing path and synchronous
  render, with no Three.js renderer/scene exposed to the host.
- On-demand option validation was added with a red-first test. It requires an
  external paused noninteractive viewer and refuses running/clocked/instruction
  documents; ordinary viewers retain continuous rendering.
- Full widget suite passes: 46 files, 1,229 tests. Type checking and bundle build
  pass. `openspec validate scripted-camera --strict` passes.
- Videomaker's real Chromium preview captured 24 sawmill frames, checking camera
  and target readback at every sample. A bad camera call preserved the previous
  mounted view. Jumping from time 1 to 61 and back restored identical PNG bytes.
- A complete 960px/10fps silent 84-second film captured 840 frames in about
  75 seconds. Continuous rendering was approximately ten times slower on this
  software-rendering machine. The first 1080p/30fps narrated encode completed
  with 2,520 frames; frame inspection confirmed camera changes and restored layers.

The actual preview/report and MP4 belong to Leonardo's ignored
`videos/hydraulic-sawmill/_build/`, not this repository. Videomaker owns the film
layout, speech and publication copy. No framework mutation or package publication
is part of this viewer change. This API is local, not a released viewer version.
