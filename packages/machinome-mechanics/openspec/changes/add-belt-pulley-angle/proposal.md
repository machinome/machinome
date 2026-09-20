## Why

Prusa3-vanilla and Kossel independently subtract belt travel from a contact
angle to orient a pulley; Metamaquina2 repeats the same law, reversing its
sign for the Y loop's backward bend and accounting for that pulley's station.
The shared operation is a tooth-reference angle from belt material position,
not merely rolling rotation without a reference.

## What Changes

- Add `belt_pulley_angle(belt_position, pitch_radius, contact_angle,
  contact_station=0.0, sense=1)` for signed, unwrapped pulley phase in the
  belt plane. Senses match the existing tangent/path helpers.
- Keep contact construction, global belt-position bookkeeping, radius fitting,
  tooth profile, machine-axis transforms and project guards in consumers.
- Use Sol agents to migrate Prusa3-vanilla, Kossel and Metamaquina2, verifying
  independent numeric/deferred comparisons, affected CAD and representative
  images before sync, archive and local integration.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `mechanisms`: Pulley angle referenced to a belt contact and path station.

## Impact

Independent mechanics belts module/flat export/tests/manual/distribution smoke;
separate project commits. No framework/viewer/molejo changes or dependency.
The pilot authorized autonomous cycles on 2026-09-20; no per-cycle ratification
is needed. Kossel's already-recorded anchor-axis defect is not silently fixed.
