## ADDED Requirements

### Requirement: A path may reuse its immediately preceding successful identical bind

A running numeric path SHALL return its previous successful first-point value without repeating that numeric walk only when the *same path instance* receives bit-identical finite values for every graph-referenced input and its graph and moving-name set remain identical. It SHALL preserve the path's standing state and evaluate every later sample at its original point. Changed, missing, nonnumeric, custom, NaN, infinite or otherwise uncertain inputs SHALL take the complete eager bind with its original first error and operation order. A failed bind SHALL NOT seed or replace a successful entry. This reuse SHALL introduce no persistent cross-path or cross-run state and SHALL change no result, search point, crossing, stop, refusal, bank value, document or author declaration.

#### Scenario: A Curta path repeats the same first-point input

- **WHEN** one Curta crank path is rebound to the same finite input bits during the same ordinary tick
- **THEN** it returns its proven result without a second numeric walk, while all required later samples and the ordered Bound levels and full bank remain bit-identical to complete binds

#### Scenario: A source changes or returns to an earlier input

- **WHEN** the same path is rebound after any referenced input changes, including a change only in the sign of zero
- **THEN** it performs the complete eager bind and preserves the original value or first error; a later return to a previously successful input is reused only while that exact entry remains the last proven one

#### Scenario: An uncertain input or failed bind

- **WHEN** an input is missing, custom-converting or nonfinite, or a changed finite input produces an arithmetic or domain error
- **THEN** the original eager walk determines the value or earliest error, and an unsuccessful walk does not publish a new reusable result

#### Scenario: A new or restored path

- **WHEN** a new path instance is created, a run is reset or restored, or a different run owns the model
- **THEN** no prior path-instance bind result is trusted; each first successful bind establishes only that instance's bounded entry
