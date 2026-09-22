## Why

The Curta-Type-I-3x `OperatingCurta` now has a physically restrained result bank and completes an ordinary two-second crank turn, but that turn takes 72.56 CPU seconds on the frozen `7586002` model with framework `3afb3f7`. One early tick makes 188,027 path-sample calls and evaluates 4.78 million moving expression nodes; 80,097 calls repeatedly interpret the same 51-node arithmetic path. This is a measured framework evaluation cost in the real machine, not a reason to alter its laws or search.

## What Changes

- Prepare private operation dispatch for a path's immutable moving-node program once after its first successful eager binding, rather than rediscovering node kinds and operators at each later sample.
- Keep the original postorder, operand values and order, operator calls, input/error behavior, standing-value refresh, path lifetime, and visit accounting.
- Retain every Curta event sample, replay, law, tolerance and bank value; keep the optimization only if a controlled before/after ordinary crank tick shows a material gain.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `motion-expression-sharing`: Repeated path samples reuse immutable operation dispatch while retaining exact numeric and error behavior.

## Impact

Private Python `_PathValue` evaluation, focused tests, and its existing expression-sharing spec only. No public API, document format, viewer implementation, CAD geometry, mechanical law, dt, constraint sample count or tolerance change. Originating project: Curta-Type-I-3x `OperatingCurta`, frozen committed runtime graph `7586002`.
