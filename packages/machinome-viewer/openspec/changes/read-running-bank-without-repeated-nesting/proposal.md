## Why

The OperatingCurta higher-counter export needs about 22 CPU seconds for the first 48 of 480 normal-duration crank ticks. A V8 profile attributes about 3 seconds of that window to repeatedly nesting the same qualified bank names for expression evaluation, plus associated garbage collection. The actual project needs a responsive crank without changing its two-second declared duration or any numerical behavior.

## What Changes

- Resolve exact qualified running-bank names from their flat values when safe, avoiding construction of a nested driver tree at each expression sample.
- Preserve the existing nested lookup for partial names and the existing `$t`, binding, context, member-access, pass-identity, and error rules.
- Accept the change only if a pinned OperatingCurta export retains all sampled/committed values and shows a material same-host CPU improvement.

## Capabilities

### New Capabilities

- `efficient-running-bank-resolution`: A running document can evaluate a qualified bank without rebuilding a nested driver scope for each sample, with exact observable equivalence.

### Modified Capabilities

None.

## Impact

Internal TypeScript evaluator and running-program adapter only. No document format, viewer API, framework, project source, dependency, CSP policy, or public control changes.
