## Why

Leonardo's hydraulic sawmill needs an educational film that explains its timed
carriage feed using the real 3D simulation, with AI narration and inspectable
project-owned sources. This is the first concrete consumer of Videomaker.

## What Changes

- Read a human-editable screenplay with narration, visual directions and exact
  presentation cues together; keep technical settings separate.
- Generate and cache ElevenLabs narration, align captions to generated speech,
  and expose speech overflow for editorial revision.
- Preview and render model-driven cameras, visibility, time and explanatory
  overlays into a narrated, credited local video with provenance.
- Keep unresolved public links explicit and never upload automatically.
- Adopt OpenSpec as this independent repository's behavioral change workflow.

Process note: the pilot authorized implementation before requesting OpenSpec on
19 September 2026. This change records and verifies work already in progress;
it is not evidence that these artifacts preceded implementation or were separately
ratified. Existing evidence is retained, not replaced with a fictional red run.

## Capabilities

### New Capabilities

- `educational-video-production`: Author, narrate, preview and render a
  reproducible educational rehearsal from an existing posed simulation.

### Modified Capabilities

None; this is the repository's first OpenSpec change.

## Impact

Videomaker owns its CLI, source parser, speech adapter, film page, capture and
encoding workflow, tests and records. Dependencies are Node, YAML, Playwright,
FFmpeg and ElevenLabs. Leonardo owns its episode sources and generated media.
The separate viewer owns API 21 camera setting and on-demand rendering under
its own `scripted-camera` change. No mechanical geometry, framework source,
hosting, remote publication or distribution license decision is in scope.
