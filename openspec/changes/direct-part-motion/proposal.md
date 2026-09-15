## Why

The pilot wants to operate `projects/Calculators/Curta-Type-I-3x` by touching
its actual selectors, crank, carriage, clearing ring and markers. The current
public controls cannot express a sliding gesture and refuse a control on the
crank or carriage because each body both slides and turns (ADR-112).

## What Changes

- Add a prismatic `Slide` control alongside `Button` and `Turn`.
- Allow a control to explicitly select one existing, single-coordinate joint
  on its part or an ancestor, so a body may be handled independently along
  each of its physical freedoms.
- Publish enough information to recover that joint's current interaction
  frame within composed motion, deriving it from the existing placements.
- Preserve the run as the owner of movement, stops, retained state and command
  outcomes. A control adds no operation sequencing or automatic repositioning.
- Provide reproducible export fixtures for the separately owned viewer change
  `slide-and-turn-parts`, including a crank that both lifts and turns.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `simulation`: sliding controls and explicit selection of a posing coordinate.
- `export`: publication of sliding controls and the selected joint's placement
  within composed motion, retaining existing document compatibility.

## Impact

Framework control declarations, validation, compilation, serialization, public
documentation and tests. The viewer implements the pointer interaction in its
own repository; the Curta implements its mechanical laws and control bindings
in its project. Neither package imports the other, and no viewer code enters
this Apache-2.0 repository.

This is a standalone prerequisite, based on main
`3519c61bf6d79e2be5df7a5972411358c9ae2371`, with worktree
`solid-node/WTs/direct-part-motion` and branch `direct-part-motion`.
Local integration target is framework `main`, subject to explicit pilot
authority and verification that its recorded base has not moved. No sprint
membership, push, publication, or release is implied. Planning awaits
ratification; the Curta interaction intent is already approved.
