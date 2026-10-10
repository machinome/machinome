## ADDED Requirements

### Requirement: A play law states retained clearance contact

The system SHALL export `Play(low=, high=)` from `machinome.simulation` for use as the `law=` of one relation written `(source & retained).drives(retained, law=Play(...))`.  It SHALL require finite native-unit offsets with `low < high`, one scalar source, and one banked scalar driven coordinate named as the second source.  It SHALL preserve every callable `law=` relation unchanged.

The explicit `Play` declaration SHALL be the running-only exception to the
callable-factory protocol in "The law of a relation is an affine pair, or
project code passed in". It SHALL NOT be called as a factory or interpreted
as an ordinary stateless forward law; the existing callable protocol remains
unchanged for every other law.

#### Scenario: A dial states two contact flanks
- **WHEN** a running assembly states `(dial & wheel.turn).drives(wheel.turn, law=Play(low=-329, high=3))`
- **THEN** the relation records one play law whose source is `dial`, retained and driven coordinate are `wheel.turn`, and contact offsets are `-329` and `3`

#### Scenario: Invalid offsets are refused
- **WHEN** either offset is non-finite or `low >= high`
- **THEN** class construction fails naming `Play`, both values, and the finite ordered requirement

#### Scenario: An unsupported relation shape is refused
- **WHEN** `Play` is used with another number or order of sources, a different driven coordinate, a group, a non-banked end, or outside `Time.running()`
- **THEN** construction refuses the relation and states the exact `(source & retained).drives(retained, ...)` running shape

#### Scenario: Existing self-read syntax is unchanged
- **WHEN** a relation uses a callable law containing ADR-121 comparison gates and does not name `Play`
- **THEN** it is declared and integrated under the existing self-read rules without play behavior
