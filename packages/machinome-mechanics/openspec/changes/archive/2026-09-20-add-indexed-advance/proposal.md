## Why

Pascaline-module's carry and Deepseek's sawmill ratchet repeat completed-turn
accumulation and phase extraction around different mechanical strokes. Both
need the same signed, unwrapped accounting, including Pascaline's shifted
325-degree origin, while retaining their own cam/contact geometry and reset.
The source evidence and broader candidate audit are in
`workflow/helper-candidate-review.md`.

## What Changes

- Add one pure `indexed_advance(angle, increment, stroke, phase_origin=0)`
  helper, exported flat and from a new indexing family.
- Call the caller's stroke once at the absolute within-turn phase, add
  completed-turn increments, and preserve numeric/deferred parity.
- Document callback purity, phase interval, units, signed turns and the
  caller-owned seam continuity condition; no continuity or contact promise.
- Sol agents migrate and validate Pascaline and the sawmill separately,
  preserving existing mechanics, controls, geometry and reset policy.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `mechanisms`: add completed-turn accumulation with a caller-authored stroke.

## Impact

Indexing module, flat exports, independent tests, manual, distribution smoke
and this package's baseline specification. No new dependency, framework code,
registry, declared face, arbitrary period, cam profile, or reset engine.
Consumer changes belong to their own repositories. Pilot waived ratification
for this campaign; empirical gates and local integration remain mandatory.
