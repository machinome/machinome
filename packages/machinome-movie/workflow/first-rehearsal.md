# First narrated rehearsal — 19 September 2026

Consumer: `projects/Leonardo/videos/hydraulic-sawmill/episode.yaml` in the
Machinome Studio development workspace. The project owns this screenplay,
production settings, credits and all generated media; Videomaker owns the tool.

## Delivered workflow

`check → speech → preview → render` produces an educational film from the real
posed model, not an independently generated imitation of the mechanism. `build`
combines speech and render. The reusable human/machine template is documented in
`docs/FORMAT.md`; the sawmill is its complete first example.

The completed model revision is `0904386e9c5c876c51337d704da7b94304b2ee1d` with a
296-second full pass. The initial 108-second source assumption was superseded by
that project's completed simulation. This film uses model seconds 8–80 over
84 video seconds; Videomaker did not change CAD or cutting geometry.

## Evidence

- Five Node tests pass: restricted YAML, stale duration/gaps/unknown layers,
  camera/time mapping and visibility reset, timestamped captions, explicit
  model keyframes. Initial missing-module failures preceded implementation;
  the keyframe test separately failed numerically before the mapping was added.
- The originating project passes `check`: eight shots, 84 seconds, model duration
  296 seconds, source-revision and assembly/evidence references resolved.
- Twenty-four real-browser preview stills pass camera readback and pixel replay
  after jumping to another shot and back. An invalid camera request preserves
  the previous view. The report is in the episode's `_build/preview/report.json`.
- The first layout preview exposed an undersized canvas; a separate stage
  wrapper corrected it. Real canvas bounds are checked before capture.
- The separate viewer's camera-input tests failed six cases before implementation.
  Its on-demand option test also ran red first. Its completed suite passes
  46 files / 1,229 tests; TypeScript checking and bundle build pass. API 21 is
  local and unreleased. Evidence remains in that repository's `scripted-camera`
  OpenSpec change.
- A complete 960×540, 10fps silent preview captured 840 frames in about 75 seconds
  with on-demand rendering. The earlier continuously rendering approach was
  approximately ten times slower on this software-rendered environment.
- Eight ElevenLabs `eleven_multilingual_v2` / George segments were generated.
  Measured durations in shot order: 5.80, 7.55, 8.20, 8.39, 10.06, 7.76, 7.97,
  12.07 seconds. The first mix refused hold/rhythm overflow. YAML timing was
  revised and all cached speech reused; no visual revision requested new speech.
- Actual character timestamps informed the hold and cut/advance model keys.
  The pilot's pronunciation is mah-SHEEN-ohm; the spoken alias keeps Machinome
  in captions. Timestamp inspection is not a claim of a human listening review.
- The initial narrated MP4 passed encoded checks: H.264, 1920×1080, 30fps,
  2,520 frames, 84.000 seconds, stereo AAC at 48kHz. Extracted frames at 5, 41,
  64 and 78 seconds were inspected. The credit text crossed the dark model base;
  a browser assertion reproduced the missing opaque background before the fix,
  then passed after adding the background. The corrected closing preview was
  visually inspected; the corrected full encode is being verified separately.
- The initial encoded narration measured -16.92 LUFS integrated and -4.32 dBTP,
  with 4.50 LU loudness range. The visual correction does not regenerate speech.

## Reproduction

Follow the setup and commands in the repository README. Use the explicit API 21
viewer bundle until the project's export includes it. Captions and MP3 caches
are reusable inputs; newly synthesized audio need not be identical.

The manifest records asset hashes, audio hashes, the resolved episode, Chromium
151.0.7922.34, FFmpeg 6.1.1 and DejaVu Sans font hash. The initial render ran before
implementation was committed, so its scaffold HEAD alone does not identify the
implementation. The final corrected render is made from the committed tool;
its own manifest and output hash are authoritative for that artifact.

## OpenSpec adoption and remaining decisions

The pilot requested OpenSpec while implementation was underway. The
`first-narrated-rehearsal` change records that fact explicitly and captures
requirements, design, implementation verification and limitations. It is not
represented as a retroactive proposal/ratification. Future behavioral changes
start with OpenSpec; baseline promotion and archive await the pilot's decision.

Public simulation and source URLs remain unset. Generated description copy
marks both gaps and `releaseReady` is false. No upload or publication occurred.
The pilot should listen to narration and review the full edit before release.
This rehearsal is landscape, not a vertical YouTube Shorts export. Videomaker's
distribution license remains unselected; Leonardo sources credit the gallery
and its AGPL-3.0-only license.

Known limits: only posed timelines are supported; cached PNGs are checked for
existence/size, not per-image checksums; pixel identity is tested within this
environment rather than across browser/font versions. Public-link presence is
not live verification. HTTP failure handling and every malformed-input variation
do not yet have exhaustive automated coverage.
