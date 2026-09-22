## Why

The OperatingCurta result/counter contact laws evaluate measured multi-sector charts while searching a crank stop. A bounded 0.1-second tick made 5.85 million path-node evaluations and about 1.72 million numeric `min`/`max` calls; the latter repeatedly classify operands that the motion path has already resolved to numbers. This makes ordinary operation much slower than the requested motion.

## What Changes

- Use the existing numeric `min`/`max` operations directly when evaluating a compiled motion path's already-numeric call nodes.
- Keep the current graph traversal, every chart term and constraint sample, argument order, arithmetic, errors, branch decisions and output state unchanged.
- Prove exact Curta-bank parity and measure one bounded crank tick against an unchanged project graph.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `motion-expression-sharing`: Repeated path evaluation preserves numeric min/max selection and error behavior without needing symbolic/formula dispatch.

## Impact

Local to the Python framework's motion expression path evaluator and its tests/spec. No public API, viewer document, project law, dependency, search setting, or CAD geometry changes. Originating project: Curta-Type-I-3x `OperatingCurta` contact-stop operation.
