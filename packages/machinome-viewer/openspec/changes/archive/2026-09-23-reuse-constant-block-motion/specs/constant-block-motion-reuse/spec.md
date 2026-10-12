## ADDED Requirements

### Requirement: Repeated certified constant blocks retain exact motion

The viewer SHALL avoid recomputing a previously successful cyclic block only when its actual incoming motion paths are constant, all values and path metadata affecting the block are the same finite IEEE-754 values, and the earlier block evaluation emitted no crossing or landing. A reused result SHALL reproduce the ordinary block's increments and fresh output motion paths bit-for-bit without changing branch, cut, search or numeric operator semantics.

#### Scenario: Curta lever moves while the crank-side block stands
- **WHEN** the pinned asymmetric Curta document holds the crank at 90° and advances the reversing lever in 48 default-timestep ticks
- **THEN** the repeated constant block is evaluated once for an unchanged input signature, while each tick preserves the same full 214-coordinate bank, command admission, status and stop as ordinary execution

#### Scenario: A source leaves and returns
- **WHEN** a block source has zero net movement but a nonconstant interior path or different cut or terminal metadata
- **THEN** the viewer executes the ordinary block path and preserves the interior crossings and subsequent contact result

#### Scenario: Signed zero and terminal-target metadata differ
- **WHEN** an otherwise equal block input or constant output differs in `+0` versus `-0`, or its exact terminal-target metadata differs
- **THEN** no incompatible result is reused, and the output path and complete bank retain the ordinary evaluation's IEEE-754 bits

### Requirement: Reuse cannot hide an error or event

The viewer SHALL use ordinary eager block evaluation when deterministic numeric provenance or full input equivalence cannot be certified. Eligibility inspection SHALL NOT raise an error ahead of the original scheduled expression. Only a fully successful, effect-free result SHALL enter the reuse state, and a hit SHALL NOT suppress required crossings, landings, first errors or Bound evaluations.

#### Scenario: A custom or stateful expression
- **WHEN** a block expression can call `random`, a shadowed function, a caller-supplied function or a coercing operand
- **THEN** the block evaluates normally on every invocation and any error appears at its original point

#### Scenario: Failed or effectful block attempt
- **WHEN** a block attempt throws, produces a crossing or landing, or belongs to an integration that refuses before commit
- **THEN** it does not publish a reusable result, and retry evaluates the original block in the original order

### Requirement: Reuse belongs to one running engine

The viewer SHALL keep no more than one successful result for each compiled block in one `Run`. A new Run, successful restore or reset SHALL start without those results; snapshots and published documents SHALL contain no reuse state.

#### Scenario: Restore and replay
- **WHEN** a run is restored to a prior snapshot and a command is replayed
- **THEN** it evaluates against the restored state and produces the same ordered records and complete bank as an uncached replay

#### Scenario: Independent runs
- **WHEN** two engines load the same document and execute different histories
- **THEN** neither can observe or reuse the other's private block result
