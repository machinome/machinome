# Verification complete — 19 September 2026

All six implementation/verification tasks are complete. Detailed evidence,
historical red runs, environment, output identity and limitations are in
[the first rehearsal record](../../../../docs/first-rehearsal.md).

- `npm test`: 8 passing tests; no paid speech requests in the suite.
- `check` against Leonardo: eight valid shots, 84-second video, 296-second model.
- Real `preview`: 24 stills, camera readback, deterministic pixel replay, invalid
  camera state preservation and opaque lower-third checks pass.
- The credit-background browser check failed before its correction and passed
  afterward. The corrected encoded credit frame was visually inspected.
- Final `render`: 2,520 frames at 1920×1080/30fps; 84.000-second H.264 MP4 with
  AAC narration at 48kHz. Speech reused eight cached generated segments.
- Final MP4 and source checksums match its manifest. Thirty caption intervals
  are ordered and fit inside the film; written Machinome is preserved.
- `openspec validate first-narrated-rehearsal --strict`: valid.
- Credential scan of staged implementation files: no API key present.

The pilot requested OpenSpec after implementation began; the change adopts and
verifies that work rather than inventing prior ratification. Baseline promotion
and archive remain for the pilot's decision. A full human listening/editorial
review and verified public URLs are still required before publication; these
are not falsely marked as completed implementation tasks. Nothing was uploaded.
