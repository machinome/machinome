## Why

Thor's GT2 flexibles and Open Robot Actuator's AT3 layout independently derive
pulley pitch radius from tooth count and linear tooth pitch. Printer timing
modules repeat it before applying their own pitch-line offsets. A named helper
keeps the circumference relationship distinct from those surface corrections.

## What Changes

- Add and document `pulley_pitch_radius(teeth, pitch)` in a belts family.
- Test circumference identities, numeric/symbolic parity and arithmetic limits
  red-first; preserve project-owned fitting and pitch-line offsets.
- Sol agents migrate natural project consumers and record independent
  comparisons, affected contracts and representative visual evidence.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `mechanisms`: pulley pitch radius from tooth count and linear pitch.

## Impact

Additive pure arithmetic API, tests and manual. No new dependency, tooth
geometry, integral-count validator or dynamic simulation. At least Thor and
Open Robot Actuator must validate before archival and local integration.
Pilot authorizes autonomous per-helper cycles; no push or publication.
