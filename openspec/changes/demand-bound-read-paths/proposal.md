## Why

The Curta-Type-I-3x `OperatingCurta` now completes an ordinary two-second crank turn in 59.11 CPU seconds on framework `acebc48`, but its anti-reversal Bound still replays a four-edge prefix at 65 fractions on each tick. The retained pawl's law can produce its actual motion path; the framework does not request it because `Program.deltas_of` counts only downstream edge inputs as path consumers, omitting Bound reads. A process-local, project-agnostic demand test preserved the Curta's complete 213-coordinate turn state and cut that turn to 27.87 CPU seconds.

## What Changes

- Treat each compiled running constraint's read coordinates as consumers of determined motion paths, alongside edge inputs, when preparing propagation demand.
- Let an already-determined Bound read use its actual law path at the existing search samples; retain full prefix replay where no path is available, especially Play and untraced sources.
- Preserve all sample fractions, float operations, bank/record/error behavior, source timing, laws, tolerances and viewer document format; accept only with exact Curta and framework-corpus parity.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `motion-expression-sharing`: A running Bound read participates in local motion-path demand so its existing search can use a determined path without inventing one.

## Impact

Private Python propagation demand and focused running constraint tests/spec only. No project, mechanical law, document or public API edit. Originating project: committed Curta-Type-I-3x runtime graph `7586002`; the existing physical `reverse_stop` Bound reads the own-read retained pawl.
