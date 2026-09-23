## ADDED Requirements

### Requirement: Terminal retained follower

A Follow retained output SHALL be terminal among compiled program edges. A downstream edge reading it SHALL be refused at compilation rather than receiving an endpoint chord for a swept retained motion. Dynamic Bounds on the output remain valid readers.

#### Scenario: Downstream law is refused
- **WHEN** an ordinary law reads a retained coordinate written by Follow
- **THEN** compilation refuses that relation before a tick or export can misrepresent its interior motion

### Requirement: An explicit two-envelope retained Follow relation

The system SHALL export `Follow(lower=, upper=)` from `machinome.simulation` for a running relation written `(lower_source & upper_source & retained).drives(retained, law=Follow(...))`. Each envelope callable SHALL build a supported numeric expression over the two ordered source coordinates; neither SHALL read the retained coordinate. The relation SHALL have exactly two distinct scalar sources before one banked scalar retained coordinate and exactly that coordinate as its single driven end. Ordinary callable self-reads and `Play` SHALL keep their existing meanings.

#### Scenario: Curta radial positioning ball declares both measured surfaces
- **WHEN** the bell-turn and register-lift coordinates precede a banked ball slide in one `Follow` relation and its lower/upper callables produce the measured piecewise expressions
- **THEN** the running program compiles a distinct Follow relation without interpreting it as an ADR-121 switch or a fixed-offset Play

#### Scenario: Malformed or unsupported relation refuses by identity
- **WHEN** the relation lacks either source, names the retained coordinate in another position, drives a different or non-banked coordinate, uses an unsupported expression, has an ambiguous writer, or is declared outside a running root
- **THEN** construction refuses naming the offending relation and requirement rather than inferring a contact law

### Requirement: Follow requires matched physical bounds

The system SHALL accept a Follow relation only when its retained coordinate declares both a dynamic lower and a dynamic upper `Bound` whose source reads and compiled expressions structurally match the corresponding Follow envelopes and do not read the retained coordinate. It SHALL refuse an absent or mismatched pair before execution. It SHALL refuse a rest state whose finite retained coordinate is outside a finite ordered envelope interval.

#### Scenario: Missing or mismatched upper bound
- **WHEN** a Follow edge has its lower Bound but no upper Bound, or the upper Bound is a different expression or read set
- **THEN** program compilation refuses rather than allowing a later inverted interval to commit without a stop

#### Scenario: Invalid rest interval
- **WHEN** the lower envelope exceeds the upper envelope or the retained coordinate starts outside either envelope at rest
- **THEN** construction refuses before a command advances
