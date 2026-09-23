## ADDED Requirements

### Requirement: A non-finite running law evaluation refuses its request

When executing a running step, the viewer SHALL refuse a law evaluation it performs if that law's result is `NaN`, positive infinity, or negative infinity. It SHALL name the offending law, its author class, and output coordinate; retain the existing `law` refusal kind; and leave the bank, tick, records, and pose as they stood before that step. Earlier successful steps of the same command SHALL remain committed, and a command that moved in the failing step SHALL retire `refused` with only its previously admitted travel. This SHALL also apply to a non-finite authored-start value in an accepted document even when the requested destination is finite, without evaluating a law at any additional point merely to seek an error.

#### Scenario: A valid authored start reaches a non-finite endpoint

- **WHEN** a version-5 running document starts at `feed=0, slide=sqrt(0.1)` with `slide = sqrt(0.1 - feed)`, and an immediate request moves `feed` to `0.2`
- **THEN** the request is refused as a law error naming `slide`, its law and author; the bank remains at its valid rest values at tick zero, and no record or pose change is published

#### Scenario: A non-finite authored start is not subtracted into the bank

- **WHEN** a version-5 running document starts at `feed=0.2, slide=0` with `slide = sqrt(0.1 - feed)`, and an immediate request moves `feed` to `0.1`
- **THEN** the request is refused as a law error naming `slide` and its law, and the bank remains `feed=0.2, slide=0` at tick zero with no new record or pose change

#### Scenario: A non-finite second step retains the first step

- **WHEN** a two-step move from `feed=0` to `0.2` commits a finite first step at `feed=0.1` and its second step evaluates `sqrt(0.1 - feed)` to `NaN`
- **THEN** the command is refused with the first step's travel admitted; the bank, tick, record, and pose retain the first successful step and no part of the second step is committed

#### Scenario: A non-finite evaluated interior refuses its step

- **WHEN** an existing running law path evaluates an interior point of a moving step and obtains `NaN` or either infinity
- **THEN** that step is refused without committing its bank, crossings, or stops, while any earlier successful steps stand

#### Scenario: A finite square-root boundary remains admissible

- **WHEN** a running law `slide = sqrt(0.1 - feed)` starts at `feed=-0.2` and a request reaches the valid boundary `feed=0.1`
- **THEN** the request retains its existing admitted travel and finite bank result, without a new refusal
