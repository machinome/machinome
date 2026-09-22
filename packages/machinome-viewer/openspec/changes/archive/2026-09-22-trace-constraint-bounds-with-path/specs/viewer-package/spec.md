## ADDED Requirements

### Requirement: A traced constraint search does not repeatedly resolve standing bound work

For a constraint whose read coordinates have determined paths, the viewer SHALL evaluate the bound at every published search sample with the same numerical semantics and result as full expression evaluation. Across those samples, work whose inputs stand SHALL be resolved once per search, not once per sample; only work affected by a moving read SHALL be re-resolved. This reuse SHALL NOT change sample locations or order, crossing and bisection choices, admitted travel, stop records, the complete coordinate bank, snapshot/replay, numeric edge cases, or refusal behavior. A bound the optimized path cannot represent SHALL use the ordinary evaluator without changing the machine's result.

#### Scenario: A large bound with few moving reads

- **WHEN** a determined constraint search samples a bound whose expression includes both standing and moving reads
- **THEN** each sampled bound value and the final machine result equal full evaluation exactly, while repeated samples do not re-resolve the standing subgraph

#### Scenario: A traced path has signed-zero endpoints

- **WHEN** a bound reads a traced coordinate whose start and end compare equal but differ as IEEE-754 values
- **THEN** the sampled bound values retain the correct endpoint signs and the search result is unchanged

#### Scenario: The bound is outside the path evaluator's supported shapes

- **WHEN** a determined constraint search samples a supported generic expression shape the path evaluator does not support
- **THEN** the search uses the ordinary evaluator and preserves its result and errors

#### Scenario: The path is not determined

- **WHEN** a constraint's read path is unavailable for determined evaluation
- **THEN** the viewer continues to sample the existing prefix replay at the same fractions and obtains the same bank, stop and outcome
