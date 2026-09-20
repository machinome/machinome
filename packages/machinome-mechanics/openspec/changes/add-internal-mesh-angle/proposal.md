## Why

Thor's shoulder uses a moving 60-tooth internal ring with fixed 10-tooth
pinion centers; OpenTorque's planets mesh with a fixed 126-tooth ring while
their carrier moves. Both projects need the same positive relative internal
mesh law, expressed today through separate ratio or external-mesh derivations.

## What Changes

- Add one helper for unwrapped common-axis internal mesh angular increments,
  with a caller-supplied carrier increment and caller-owned source phases.
- Migrate Thor's actual four shoulder bindings through the shared coefficient
  and OpenTorque's actual three planet bindings through a carrier-local adapter.
- Preserve mounting signs, hierarchy, counts, independent legacy oracles and
  controls; validate numeric/deferred motion, bounded CAD, builds and pixels.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `mechanisms`: internal ring/pinion angular increments in a common frame.

## Impact

Independent package gears module, exports, tests, manual and distribution smoke;
two separate consumer commits. No framework/viewer changes, generated gear
geometry, inverse API, tooth registration, publication or contact certification.
Pilot has authorized this empirical cycle without another ratification prompt.
