## ADDED Requirements

### Requirement: Ancestor constraints stop the existing mechanical coordinates

A simulation SHALL enforce constraints declared on existing descendant
joints by their ancestors through the same stop semantics as the target's
own range. The own-coordinate argument SHALL retain the existing committed
tick/request-start reading and additional reads SHALL follow the attempted
motion. A running read SHALL be an actual banked coordinate or input;
ordinary and derived ports SHALL remain refused.

Blocked commands SHALL report admitted travel on the existing inputs and
actual constrained coordinate, with no retained backlog or automatic
resumption. Motion of a read that would invalidate a standing target SHALL
be stopped according to the existing cross-coordinate constraint rule.
Relieving or unrelated motion SHALL retain its existing admissibility.
Transaction, snapshot, restore and reset behavior SHALL remain unchanged.
Clocked constraints SHALL retain the clocked solver's existing supported
expression classes and refusals.

#### Scenario: A nested crank stops against a retained shaft

- **WHEN** an existing nested crank joint is constrained by an ancestor's
  bound reading a separately nested retained shaft, and a crank request
  crosses that limit
- **THEN** the request stops at the allowed boundary, reports blocked with
  its admitted travel, and neither moves the held shaft nor completes the
  rejected remainder

#### Scenario: A moving read cannot overrun a standing target

- **WHEN** the constrained target stands still and motion of a read would
  carry its constraint outward
- **THEN** the responsible input stops through the same dependency rule as
  an ordinary joint-local `Bound`, without snapping the target

#### Scenario: A blocked request is not queued for later relief

- **WHEN** a constraint blocks a crank request and a subsequent input relieves
  the obstacle
- **THEN** the old request does not resume; a new request is needed to move
  the crank, and restoring/replaying the same history reproduces the result

#### Scenario: An added constraint stops one running-time admission

- **WHEN** a nested joint driven by running time reaches an ancestor
  constraint while another independent time drive remains free
- **THEN** only the pushing admission stops for that tick, global time and
  the independent drive continue, and later ticks retry without catch-up

#### Scenario: A clocked request consumes the same effective limit

- **WHEN** a clocked request reaches an ancestor constraint whose level is
  supported by the existing clocked bound solver
- **THEN** it admits only travel up to that limit and the final pose does
  not reject an already judged boundary through a second authority

### Requirement: Composed constraints preserve publication and replay identity

Compiled publication SHALL represent the intersection using the existing
qualified coordinate ids, span shape and expression vocabulary. Additional
constraints SHALL add no state, proxy coordinate, driver or control entry.
Equivalent effective limits SHALL execute through the existing consumer
contract without a new document version. Changing an effective constraint
SHALL change the compiled program identity and refuse an incompatible
snapshot. Models declaring no additional constraints SHALL keep their
previous program identities, published documents and stop behavior.

#### Scenario: Publication describes the real nested crank

- **WHEN** a running Curta diagnostic adds a constraint to its existing
  nested crank and publishes its compiled program
- **THEN** the span names that crank and the actual shaft read, and the
  assembly/control paths are unchanged with no new banked value

#### Scenario: An existing consumer reproduces the nested stop

- **WHEN** the installed viewer consumes the published nested diagnostic
  and receives the same crank request through its public control API
- **THEN** its committed travel and stop agree with Python under the
  existing tolerances and retain the same assembly tree

#### Scenario: An incompatible snapshot is refused

- **WHEN** a snapshot is restored into a model whose effective ancestor
  constraint differs
- **THEN** the program identity check refuses the restore without committing
  a partial bank

#### Scenario: Old models do not acquire a new format or cost path

- **WHEN** an existing model declares no ancestor constraints
- **THEN** its compiled spans, identity, document version and bytes remain
  unchanged and it executes through the existing uncontributed-range path
