## Why

The originating OperatingCurta production Follow export makes its two ball Bounds replay the same three-edge prefix independently at the same sampled fractions. On viewer main `fe1a708`, five 0.1-second crank ticks made 768 prefix evaluations and took 6.84 seconds on one pinned CPU. This is avoidable repeated work in an operating control, not a request to reduce sampling or change the machine.

## What Changes

- Reuse a successful prefix propagation at the same exact sample fraction only within one reached-Bounds stretch, when the two Bounds have the same compiled prefix.
- Keep each Bound's own graph evaluation, sample order, bisection, error behavior, stop attribution, admitted travel and bank unchanged.
- Prove the reduction and exact replay on the real Curta export and focused synthetic cases.

## Capabilities

### New Capabilities

- `follow-prefix-replay-cache`: Bounded reuse of identical successful Follow Bound prefix work without changing observations.

### Modified Capabilities

None.

## Impact

Viewer running solver and tests only; no document, API, timestep, package dependency, framework or project source change. The cache is per-stretch and cannot survive a tick, snapshot, reset or restored run.
