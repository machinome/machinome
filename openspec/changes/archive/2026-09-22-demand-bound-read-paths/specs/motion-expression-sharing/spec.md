## ADDED Requirements

### Requirement: Running Bound reads demand their actual motion paths

A running constraint's declared read coordinates SHALL count as consumers of their determined motion paths during propagation. When a read's determiner can provide a path, the existing bound search SHALL sample that actual path at the same fractions and in the same order as its prefix replay would, with the bound's own coordinate held at its original tick-start value. All resulting level float bits, first errors, stops, records and committed bank values SHALL remain unchanged. A read for which propagation has no determined path, including an untraced Play descendant, SHALL retain the existing prefix replay; the engine SHALL NOT infer a chord from endpoint values.

#### Scenario: A retained own-read law feeds a crank Bound

- **WHEN** a retained law reads the coordinate it drives and its output is named only by a running Bound, not by another edge
- **THEN** the Bound receives the law's actual piecewise motion path and each existing search sample gives the same level float as prefix replay

#### Scenario: A read cannot supply a determined path

- **WHEN** a bound reads a Play descendant or another coordinate for which no actual motion path was determined
- **THEN** every existing search fraction still replays the complete required prefix and retains its result and refusal behavior

#### Scenario: Ordinary motion and a stopped withdrawal

- **WHEN** the same machine completes a free crank turn or reaches a moving-read physical stop
- **THEN** all search levels, stop attribution and bank values match the previous execution, with no change to dt, samples, tolerances or authored laws
