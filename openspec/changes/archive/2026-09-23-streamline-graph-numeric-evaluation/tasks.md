## 1. Pin the unchanged numeric contract

- [x] 1.1 Add a red-first allocation-path test showing that simple scalar leaves and a valid binary node still execute the evaluator's child-list comprehension; require no such per-node comprehension after the change.
- [x] 1.2 Add baseline-parity characterization tests for repeated signed-zero/nonfinite results, custom operand/mapping callbacks, missing inputs, competing left/right errors, malformed arity, unsupported nodes and live operator replacement between evaluations; pin exception type, text and first-error position.

## 2. Streamline only the full-graph loop

- [x] 2.1 Avoid materializing a child-value list for scalar leaves and valid two-child binary nodes while retaining the original postorder, live per-call operator table and malformed-arity splat fallback.
- [x] 2.2 Run the focused expression/simulation tests, confirm no API/schema/viewer change, and inspect the diff for any changed operand or error ordering.

## 3. Verify the originating caller and finish the cycle

- [x] 3.1 On the pinned installed Curta request, compare all ordered `GraphValue` result IEEE bytes, full 214-coordinate bank, status and stop data against the recorded baseline; repeat paired CPU timing and report variance.
- [x] 3.2 Run proportionate broad framework tests and strict OpenSpec validation; synchronize the clarified requirement, archive the change and record evidence in the final implementation commit, with no ADR unless a consequential architecture decision actually arises.
