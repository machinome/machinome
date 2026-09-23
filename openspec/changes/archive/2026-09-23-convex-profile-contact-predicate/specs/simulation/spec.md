## ADDED Requirements

### Requirement: Profile contact is a numeric term in an existing running Bound

Under a running root, a `Bound` expression SHALL accept the pointwise `profile_overlap` result as numeric `0.0` or `1.0` in ordinary arithmetic that returns an absolute lower or upper coordinate limit. It SHALL resolve the call's motion operands from the `Bound`'s declared reads, and SHALL preserve the existing frozen-own-value rule, evaluated numeric span shape, 64-subinterval search, bisection, first-error behavior, stop attribution, atomic refusal and snapshot/replay contract. A **symbolic** profile contact operation outside a supported running `Bound` SHALL be refused by name rather than emitted as an unevaluable pose, law or clocked expression. A plain numeric `profile_overlap` call SHALL remain usable for standalone probes and numeric bind-time range evaluation; the framework SHALL NOT claim to identify the origin of an ordinary numeric result.

#### Scenario: Contact selects an axial plane without becoming a bound
- **WHEN** Curta's running reverser `Bound` uses the contact flag to select an absolute held-side axial limit from its existing lower or upper plane arithmetic
- **THEN** the compiled constraint still has the ordinary numeric limit and blocks the same held coordinate through the existing search and attribution path

#### Scenario: A moving angular contact is sampled under the existing limit
- **WHEN** a moving read changes the profile flag during a tick
- **THEN** the surrounding Bound is evaluated at the same samples and bisected under the same limit and tolerance as any other dynamic Bound; no continuous collision guarantee is added

#### Scenario: A quiet bound remains quiet
- **WHEN** neither the bounded coordinate nor any declared read moves during a stretch
- **THEN** the existing quiet-stretch rule evaluates neither the bound nor the contact predicate

#### Scenario: Unsupported expression context is refused
- **WHEN** a symbolic profile operation is returned by a clocked bound, a running law, or a pose operation rather than a running Bound
- **THEN** that context refuses it by name rather than publishing or silently changing its solver

#### Scenario: Standalone numeric check is still available
- **WHEN** an author evaluates `profile_overlap` with plain numeric placements or a numeric bind-time range consumes its result
- **THEN** it returns the same numeric 0/1 predicate without a symbolic-context refusal

## MODIFIED Requirements

### Requirement: A range bound may read other coordinates

Under a running root a `Bound(expression, reads=(...))` stated as either
bound of a banked joint coordinate's range SHALL be compiled once, at
simulation construction, exactly as a one-argument bound is: its reads
resolved against the joint's declarer to the qualified ids the bank keys
by, the expression applied to a symbolic token for the joint's own
coordinate and one per read in declared order, and the graph walked for
raw text and for calls outside the symbolic vocabulary. The sole added
symbolic call allowed by this change is `profile_overlap` within a running
`Bound`; it is not added to the general law, pose, clocked or SCAD vocabulary.
A read SHALL be a coordinate the run banks — a joint coordinate or a
declared input; a read resolving to a plain port or a derived coordinate
SHALL be refused at construction by joint and node identity, saying that
a bound reads the state and naming the joint the port follows. Jumps SHALL
be admitted with no plan, because a bound is evaluated and never integrated.

The compiled program SHALL carry, for each such bound, the ids it reads,
the SUB-PROGRAM — the compiled edges that determine the bounded
coordinate and every read, in program order — and the candidate inputs
reaching any of them. `Program.spans` SHALL keep its shape, each such
bound a graph in it like any other, and the program's described listing
and therefore its identity SHALL change with the reads, so a snapshot
cannot restore into a machine whose constraints moved.

A stop located by such a bound SHALL be recorded like any other: the
bounded coordinate, the side, the bound evaluated at the committed state,
the fraction of the tick and the inputs blocked, sorted.

#### Scenario: A read is resolved to the id the bank keys by

- **WHEN** a running root's `Plug` body declares `p1 = Pin()` and
  `turn = Revolute(..., range=(0, Bound(..., reads=(p1.lift,))))` and the
  plug is held as `plug`
- **THEN** the compiled bound's graph reads `plug.p1.lift`, the same id
  `sim.state` holds, and the program's described listing names it in the
  span line

#### Scenario: A read of a plain port is refused at construction

- **WHEN** a `Bound`'s `reads` names a port an author's `simulate()`
  binds rather than a joint coordinate
- **THEN** construction is refused by joint and node identity, naming the
  port and saying a bound reads the state

#### Scenario: A read the expression never uses is refused at construction

- **WHEN** a `Bound` declares `reads=(p1.lift, p2.lift)` and its
  expression reads only the first, or returns a plain number
- **THEN** construction is refused by joint and node identity, naming
  the read the expression never uses, because a bound reads every
  coordinate it names

#### Scenario: A bound over other coordinates changes the identity

- **WHEN** two roots differ only in the window a bound reads its pins
  against
- **THEN** their program identities differ and a snapshot of one is
  refused by the other

#### Scenario: A read of a driver is an input of the bank

- **WHEN** a `Bound` on a class-declared joint reads a driver of the same
  class
- **THEN** the compiled bound's graph reads that driver's qualified id
  and evaluates it along the path as an input's admission scaled by the
  fraction

#### Scenario: Only a running Bound gains the contact call

- **WHEN** the same symbolic `profile_overlap` expression is offered to
  a running Bound and to an ordinary running law or pose expression
- **THEN** only the Bound compiles it; the other symbolic contexts refuse
  it by name, without widening the general math vocabulary
