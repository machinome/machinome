## Why

The Curta's setting selectors slide, and its crank and carriage both lift and
turn. A viewer that accepts only a press or a rotational drag cannot let the
maker operate those parts directly, as the pilot has requested.

## What Changes

- Read the framework's new sliding controls and selected-joint placements.
- Let makers drag a part along its actual sliding direction, with movement
  coming from the run's admitted commands.
- Make lifting and turning independently reachable when one part supports
  both, without choosing an operation order or repositioning another control.
- Keep the existing click-to-submit instruction behavior, so clicking the
  crank can request one revolution while dragging can request partial travel.
- Exercise stops, reversal, camera changes, occlusion and gesture cancellation
  with real pointer input on producer-generated fixtures and the Curta.
- Raise the viewer API capability version when the new interaction ships.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: direct sliding and independent handling of a part's sliding
  and turning freedoms; current-frame control geometry and capability reporting.

## Impact

The widget's control reader, interaction math, pointer handling, public types,
tests, README and changelog. Consumes framework change `direct-part-motion`;
fixtures are exported data and this AGPL-3.0-only package does not import the
framework. The worker's mechanical integration algorithm stays the same.

This viewer-owned change starts at main
`33ac0ad934ee5011f2085365134a640bd4544ee8`. It is a prerequisite of the
already approved Curta interaction redesign, not a claim that the Curta's
existing mechanical validation gaps are closed. No push or publication is
implied. The pilot subsequently requested review and correction of anything
missing in the producer implementation, then implementation of the approved
Curta interactions. This consumer prerequisite proceeds under that direction;
the reviewed producer now branches from merged main in `harden-direct-part-motion`.
