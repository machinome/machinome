## Why

The Leonardo Machinome release-film review asks for actual Python source typing
beside the simulated machine, a more expressive feminine narrator, intact phrase
starts, and optional external subtitles instead of burned captions. The pilot
explicitly requested implementing these Videomaker features and one short scene.

## What Changes

- Load Python excerpts from the consuming repository at the exported model's
  pinned revision; render syntax-highlighted, deterministic timed typing beside 3D.
- **BREAKING**: narration captions become external SRT assets, never film pixels.
- Support lossless PCM speech acquisition and model-aware Eleven v3 requests.
- Preserve complete audio at authored offsets and measure onset integrity; do not
  call padding a repair for syllables already missing from a generated clip.
- Make preview/replay and thumbnails work for short scenes.

## Capabilities

### New Capabilities

- `narrated-source-scenes`: authentic typed source, separate subtitles and
  inspectable narration acquisition/mixing for release-film scenes.

### Modified Capabilities

None in baseline: the inaugural educational-video-production spec remains in an
unarchived change. This change explicitly supersedes its burned-caption promise;
it does not rewrite that historical production record.

## Impact

Videomaker source loader, timeline, stage, speech, renderer, tests and format docs;
one pinned highlighting dependency. Leonardo owns its new scene and build assets.
The simulation, viewer and existing release master remain unchanged.

## Non-goals

No full-film remake, live code execution, CAD edits, new viewer API, voice cloning,
publication, music platform or general-purpose editor.
