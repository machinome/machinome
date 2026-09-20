## Why

Thor's flexibles.tangent and Prusa3-vanilla's timing._normals/_touch independently
solve the same signed-circle tangent before measuring belt spans and wraps.
Their distinct truthy/string turn markers hide the shared geometric contract.

## What Changes

- Add `belt_tangent_points(centre_a, radius_a, centre_b, radius_b,
  sense_a=1, sense_b=1)`, returning the two contact points in traversal order.
- Document explicit clockwise/counterclockwise senses in the caller's XY plane,
  domain failures and numeric/symbolic parity; test independent geometry red-first.
- Sol agents adapt existing belt consumers, retaining their marker semantics,
  wrapper errors, pitch surfaces, route order and mechanical behavior.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `mechanisms`: directed common tangent points between belt circles.

## Impact

Additive belts-family function, flat export, docs and tests. No geometry
objects, dictionary protocol, Molejo import or new dependency. No copied
project implementation or prose enters this Apache-2.0 package; the formula
is independently derived from unit-normal and perpendicular-contact identities.
At least Thor and Prusa3-vanilla validate before archival/local integration.
