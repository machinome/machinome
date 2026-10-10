## Why

Curta-Type-I-3x `OperatingCurta` now needs a 126,032-node aggregate crank bound to restrain its result bank. During a real active stop, the run evaluates that entire graph at each searched level even though only two of its 23 reads—and 3,670 to 7,851 graph nodes—move. The exact traced-path prototype preserves every sampled argument and result bit in order while reducing the active-stop tick from roughly 7.9 to 5.6 CPU seconds, so the already-accepted moving-path evaluator should serve this additional measured caller.

## What Changes

- For a running constraint whose required read paths are already determined, bind its graph once per search to the first sampled arguments and evaluate only the moving cone at later samples in that search.
- Keep the nontraced prefix-replay path, own-coordinate tick-start reading, all 64 samples and bisection rounds, float/operator order, eager errors, and stop/rollback behavior unchanged.
- Prove exact sample and full-bank parity on the originating Curta graph, alongside signed-zero/NaN, fresh-search standing values, and source-timing/carry/stop regression tests.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `motion-expression-sharing`: Running traced constraint searches reuse a bound graph's standing subexpressions within one search while preserving its existing samples and results.

## Impact

Private Python running constraint search and expression-path use only. No public API, viewer document, mechanical project law/geometry, graph syntax, dt, tolerance, or search sample-count change. Originating project: committed Curta-Type-I-3x runtime graph `7586002`, including the higher-result-bank restraint.
