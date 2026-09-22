## Why

The committed OperatingCurta `7586002` export needs 97,474 distinct expression nodes at load, already above the viewer's 50,000-node reclamation trigger. Its cache is therefore discarded before every selector and crank tick: the 48-tick crank segment takes 53.9 seconds without WebGL, with repeated parsing and interning prominent in a V8 CPU profile, although the same turn is declared to draw in two seconds.

## What Changes

- Give a live supported machine enough *finite* expression-cache capacity to reuse its prepared graph across adjacent operations when its measured working set fits. Preserve reclamation for publication history, final-mount disposal, and cache-pressure recovery.
- Keep expression evaluation, numeric results, event samples, command admission, error behavior, and the published host/document interfaces unchanged.
- Prove the improvement against the current OperatingCurta export and measure the real, current CounterTensOperatingTrial candidate before setting the smallest bounded capacity. Record both throughput and retained-memory cost.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: A supported large running document that fits inside the finite expression capacity reuses its prepared graph across consecutive ticks without reclaiming and reparsing it on every tick, while existing cache-pressure correctness and lifetime guarantees remain intact.

## Impact

The change is confined to the viewer's expression-store lifetime policy and its tests (`machinome_viewer/widget/src/expressions.ts` and `expression-lifetime.test.ts`), with a baseline-spec update and evidence. The viewer API remains 24, document format remains v11, and the framework and Curta project source are unchanged by this viewer cycle. A larger retained graph uses more memory while mounted; that cost must be measured and kept bounded rather than hidden.
