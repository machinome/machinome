## Why

Curta Type I's selector mate migration exposes phantom X/Y axis components
when a pure Z -95.6-degree rest rotation is converted to axis-angle, causing
an unchanged physical-basis comparison to differ by about `1.0524e-8` mm.
This violates numerical pose equivalence; no physical fit failure is claimed.

## What Changes

- Stabilize internal matrix-to-axis-angle recovery to avoid square-root
  amplification of cancellation residue into false small axis components.
- Preserve genuine small axis components, signed principal rotations above
  90 degrees, near/exact half-turns and existing equal-component symmetry.
- Keep the `1e-9` snap, caller tolerances, rotation/translation order and
  identity omission unchanged. Add red-first matrix and public-mate tests.
- No author API, coordinate semantics, schema, viewer or Studio change.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `mates`: explicitly pin stable rest-rotation conversion under the existing
  whole-triad placement requirement.

## Impact

`machinome/motion/mates.py::_axis_angle`, focused numerical and mate placement
tests, and unchanged originating caller evidence in Curta's
`simulation/test_selector_mates.py` (project content `4b2ea5ad`, saved candidate
`_build/selector-mates-candidate.patch`). No new dependencies or global
numerical rewrite. The finding and pre-spec intent are recorded in
`workflow/warts.md` and `workflow/ongoing/stable-mate-rotation-conversion.md`.

The pilot explicitly ratified this no-interface-change numerical fix and the
empirical ratification rule for such fixes; interface changes still come to
the pilot first. Standalone branch/worktree `stable-mate-rotation-conversion`
at `machinome/WTs/stable-mate-rotation-conversion` uses clean framework main
base `6ca6061f576a512fb31d6412815c38bd6c1e6485`, integration target `main`.
This proposer writes planning only; root reviews and commits, a separate Sol
applies. No additional ADR is expected for a nonarchitectural numerical fix.
