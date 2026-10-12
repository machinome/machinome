## ADDED Requirements

### Requirement: Deterministic kink probes preserve the running outcome
The viewer SHALL preserve the existing kink cut sequence, prescribed Bound evaluations, first error, complete bank state and replay outcome when it reuses a successful deterministic kink-level value within one search. It SHALL leave arbitrary or uncertified callbacks on the ordinary evaluation path.

#### Scenario: Repeated certified probe
- **WHEN** a running law evaluates the same certified kink at the same exact fraction more than once in one cut search
- **THEN** it returns the same cuts and full running outcome as the uncached search while avoiding duplicate expression evaluation

#### Scenario: Uncertain or stateful expression
- **WHEN** a callback or binding can be stateful, custom or indirectly called
- **THEN** every scheduled probe evaluates normally and any error appears at the original probe

#### Scenario: Distinct identities and exceptional values
- **WHEN** fractions differ by signed-zero bits, a kink identity differs, or an input or result is nonfinite
- **THEN** no earlier value is incorrectly reused and the uncached numeric/error behavior is preserved

#### Scenario: Separate searches and replay
- **WHEN** a later piece, tick, new run or restored replay repeats a formerly cached probe
- **THEN** it evaluates against that search's actual inputs and reproduces the uncached bank and stop result
