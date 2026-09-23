## Why

The production OperatingCurta's five ordinary 0.1-second crank ticks still consume about 4.6–4.7 CPU seconds in the viewer after the Follow prefix-replay cache. A pinned V8 profile attributes 33% of samples to kink-break computation. In those same ticks, 155,267 of 421,392 kink-level calls (36.8%) repeat an identical kink and fraction inside one break search; a read-only in-memory prototype cut CPU time to 3.7 seconds without changing any of the 768 ordered Bound samples or five complete 214-coordinate bank hashes. The project needs a faster ordinary operation now, without reducing its prescribed searches or altering mechanics.

## What Changes

- Reuse successful, bit-identical kink-level probes within a single search only when the viewer has proved the expression-backed callback deterministic. Leave arbitrary callbacks and uncertain graphs on the original eager path.
- Preserve kink ordering, cuts, numeric operations, failures, Bound samples, replay and bank outcomes. Add adversarial tests and a pinned production Curta benchmark.
- No document, host API, timestep, tolerance, geometry or published bundle contract changes.

## Capabilities

### New Capabilities

- `kink-probe-throughput`: Observationally equivalent, search-local reuse for certified deterministic kink levels, with fallback for unsafe callbacks.

### Modified Capabilities

None.

## Impact

Private TypeScript running-expression/cut evaluation and tests in this viewer repository, plus OpenSpec evidence. No framework or Curta project source change. This is a standalone viewer cycle under the pilot's standing autonomous framework/viewer-fix direction; no design-specific pilot ratification is claimed.
