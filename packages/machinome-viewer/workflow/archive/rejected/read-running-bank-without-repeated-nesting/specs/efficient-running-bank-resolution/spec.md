## ADDED Requirements

### Requirement: Exact running-bank reads avoid redundant scope construction

When a running expression reads an exact coordinate in its flat bank, the viewer SHALL resolve that coordinate without rebuilding a nested driver scope. This optimization SHALL preserve binding and time precedence, the ordinary member-access and error behavior on other names, and bit-identical evaluator results, search decisions, committed bank, and replay for the same document and dt.

#### Scenario: Qualified coordinate is present
- **WHEN** a running expression reads an exact qualified coordinate in the bank
- **THEN** it obtains the same numeric value as nested member lookup without constructing that nested bank

#### Scenario: Name is not an exact bank coordinate
- **WHEN** a running expression reads a partial, context, or otherwise missing name
- **THEN** it follows the existing nested resolution and error semantics

#### Scenario: Bank value changes between samples
- **WHEN** a coordinate changes presence, signed zero, NaN, or numeric value between running evaluations
- **THEN** the evaluator invalidates any stale pass result and returns the same result as an independently nested evaluation

#### Scenario: OperatingCurta crank window
- **WHEN** the frozen 213-coordinate OperatingCurta export runs the first 48 default-dt crank ticks after selector 1 is set
- **THEN** every committed coordinate and the admitted travel remain unchanged while measured process CPU falls materially on the same host
