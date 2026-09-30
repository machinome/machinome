## Why

Leonardo's `videos/demo-all-features` is a nine-shot, 46-second film whose local camera, title and timing corrections currently change one whole-episode frame identity. Its short real-model [incremental-rendering baseline](/home/asa/devel/machinome/projects/Leonardo/videos/demo-incremental-rendering/evidence.md) measured 31.67 s for 80 cold frames, 1.70 s for an unchanged rerun, and 32.11 s with all 80 recaptured after one label edit; only frames 21–42 changed pixels. The author needs a corrected shot without recapturing unrelated shots, while the final frames remain pixel-identical to a fresh render. These are baseline observations, not predicted post-change timings.

## What Changes

- Cache output PNGs by their actual shot-level visual dependencies and global output-frame positions, reusing only verified frames whose inputs still match. An edited shot, its dependent incoming transition, shifted frame grid, changed whole-film chrome, or changed shared renderer/model dependency invalidates exactly the affected shot caches or more conservatively all shots where the dependency is global.
- Seal completed frames with integrity and provenance records, so interrupted or corrupt partial caches cannot silently pass as valid. Report captured and reused frames by shot and identify their originating cache records in the render manifest.
- Keep the existing episode format, CLI, narration cache and final MP4/SRT behavior. A cache hit never buys speech or bypasses episode and measured-word refusals. Old whole-episode cache directories are not assumed compatible with the new key or silently imported.
- Prove selective reuse and exact output-frame equality against a fresh render on Leonardo's short, real-model `demo-incremental-rendering` consumer, including a transition, source/text and a fractional-grid fixture, while preserving the original `demo-all-features` film and caches.

## Capabilities

### New Capabilities

- `shot-level-incremental-rendering`: Sound reuse, invalidation, interruption recovery and observable provenance of rendered shot frames.

### Modified Capabilities

None. Existing shot, picture, speech, transition and episode-format meanings remain unchanged.

## Impact

Changes the internal frame cache and render report in Videomaker's `render` path, with focused tests and real Leonardo consuming-film evidence. No new YAML field, format version, paid narration, viewer API, or publishing step is required. Existing `_build/frames/<episode-hash>/` PNGs remain untouched but are not trusted as the new cache.
