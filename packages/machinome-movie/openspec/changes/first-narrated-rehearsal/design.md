## Context

The first consumer is Leonardo's hydraulic sawmill, an existing posed simulation
with a completed 296-second pass. The 84-second landscape rehearsal shows model
seconds 8–80. Implementation began with the pilot's authorization before OpenSpec
was requested; this record captures that design and the remaining verification.

## Goals / Non-Goals

Goals: readable project-owned sources; deterministic presentation of the actual
model; measured synthetic narration; educational captions, labels and credit;
resumable local production with inspectable evidence.

Non-goals: video publishing, hosting the simulation, changing CAD, photorealistic
text-to-video, running/clocked machine replay, a web editor, multiple speech
providers, or a general video-editing language.

## Decisions

1. YAML screenplay and separate production settings follow `docs/FORMAT.md`.
   The user explicitly rejected executable episode modules; JSON is less
   pleasant for paragraphs and comments. YAML is parsed as restricted data,
   with no anchors, aliases, custom tags or duplicate/non-string keys.
2. Node CLI commands separate validation, speech, still preview and rendering;
   `build` composes speech and render. An interactive editor is unnecessary for
   the named consumer. Dependencies are locked in package-lock.json.
3. A pure timeline maps frame number to model time, camera and full shot
   visibility. Explicit model keyframes align cut/advance phases with actual
   spoken words. No wall-clock recording or second mechanical animation is used.
4. A loopback server exposes only the film page and selected model/viewer assets.
   Playwright controls the public Viewer API 21 (`setTime`, `setView`, visibility)
   and captures the composed page. A separate viewer change owns camera setting
   and on-demand rendering; Videomaker does not reach into Three.js internals.
   Continuous rendering was tested but unnecessarily consumed software-rendering
   capacity. On-demand capture reduced the 960px silent run to about 75 seconds.
5. ElevenLabs timestamped TTS uses a configured synthetic voice and a server-side
   key in ignored `.env`. Each shot caches MP3, request settings and character
   alignment, keyed by text, adjacent text, voice/model and settings. Estimates
   cannot align mechanical phases precisely; measured timestamps can. The pilot
   confirmed mah-SHEEN-ohm; a speech alias preserves Machinome in written captions.
6. Speech overflow is an editorial error, not permission to truncate or stretch.
   Delayed segments are mixed and loudness-normalized with FFmpeg; captions use
   character alignment. Frame PNGs are content-addressed and written atomically;
   FFmpeg encodes H.264/AAC with burned-in captions. MP4 dimensions and frame count
   are checked with ffprobe. Regeneration from a changed TTS service is not
   promised to produce identical speech; cached audio is the reproducible input.
7. Outputs remain in the consuming episode's ignored `_build/`. Provenance records
   resolved inputs, asset/audio hashes, browser/encoder/font and source revisions.
   Missing public links are explicit; rendering a rehearsal does not publish it.

## Risks / Trade-offs

- Software rendering is slow and frame caches are large → preview at 960px/10fps
  before full 1080p/30fps capture; reuse unchanged audio and frames.
- A model export can be stale → compare its duration and source-revision record,
  resolve assembly paths and keep the originating project's validation evidence.
- A numeric timestamp is not proof of a correct educational explanation → inspect
  actual pixels and compare half-strokes with audio cues. The pilot reviews final
  pronunciation and delivery; automated alignment is not a listening review.
- Browser/font changes can alter pixels → record versions and font hash; pixel
  replay is verified in the tested environment, not promised across machines.
- Cached frames currently check existence/size, not each image checksum → cache
  corruption remains a limitation, while interrupted writes use atomic rename.
- Public URL presence is not live verification → final release requires manual
  link verification. No upload command exists.
- First production ran before implementation commits → its manifest includes
  scaffold Git HEAD plus actual renderer/asset hashes; evidence must name this
  provenance limitation rather than imply HEAD contains the implementation.

## Migration Plan

Keep the existing draft 0.2 sources. Install locked dependencies and build the
local Viewer API 21 bundle, then run check, speech, preview and render. Prior
exports can use an explicitly supplied viewer bundle. Reverting the local tool
does not mutate project CAD or remove generated media. Archive this adoption
change only after verification and the pilot's spec-sync/archive decision.

## Open Questions

- Verified public source and simulation URLs are still owed before publishing.
- Videomaker's own distribution license remains the pilot's decision.
- Vertical Shorts framing is separate editorial work, not part of this landscape
  rehearsal; no aspect-ratio switch can substitute for that review.
