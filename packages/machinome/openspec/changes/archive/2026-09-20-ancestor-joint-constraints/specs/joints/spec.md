## ADDED Requirements

### Requirement: An assembly constrains an existing descendant joint

The system SHALL accept `path.to.joint.constrain(range=(lo, hi))` in an
assembly class body as an additional constraint on that existing scalar
joint. The target SHALL be an explicitly named one-coordinate joint reached
through child declarations. The constraint SHALL preserve its target's
owner, axis, anchor, unit, placement frame, joint order, source geometry,
qualified coordinate path and original range. It SHALL create no new joint,
input or retained value.

Each side SHALL use the existing range-side vocabulary: `None`, a numeric
or parameter-derived value, an expression of the target's own coordinate,
or `Bound(expression, reads=(...))`. Structural values and read references
SHALL resolve against the assembly declaring the additional constraint.
Its implicit first expression argument SHALL remain the target coordinate.

Declarations SHALL be recorded in written order and inherited additively;
this surface SHALL provide no removal or named-replacement operation.
Each instance SHALL resolve its own endpoints. Invalid inherited
paths SHALL be refused rather than silently ignored or redirected.

Targets that are a whole node, input, state, plain or derived port, grouped
end, broadcast, or multi-coordinate joint/component SHALL be refused by name.
Statements outside an assembly class body, malformed or wholly unbounded
ranges, out-of-scope references and reads of the target itself SHALL be
refused. Existing duplicate and unused read checks SHALL remain effective.

#### Scenario: Curta's ancestor states an installed locking obstacle

- **WHEN** an assembly constrains `main_drive.crank.turn` with a bound reading
  `transmission.result.ones.turn`
- **THEN** the target and read resolve to those actual descendant joints,
  and the crank's stationary siblings, node tree and controls remain unchanged

#### Scenario: Two instances do not share a resolved constraint

- **WHEN** two instances of the same nested assembly have different read
  values and constraints
- **THEN** each constraint evaluates its own instance's coordinates and
  neither instance changes the other's joint metadata or admitted travel

#### Scenario: An inherited constraint cannot vanish after a child override

- **WHEN** a subclass replaces a constrained child with a class lacking the
  targeted joint
- **THEN** the system refuses the invalid constraint by its target path
  instead of constructing an unconstrained machine

#### Scenario: Inherited constraints remain effective

- **WHEN** a subclass adds another constraint on a descendant already
  constrained by its base
- **THEN** both constraints and the target's own range remain effective

#### Scenario: Unsupported targets and self reads are diagnosed

- **WHEN** a constraint targets a plain port or repeated broadcast, or names
  its own target in `reads`
- **THEN** declaration is refused with the offending target/read identified
  and no fake banked coordinate is introduced

### Requirement: Installed constraints narrow but never replace joint travel

Every additional constraint SHALL intersect with the target's own range and
every other applicable constraint. The effective lower limit SHALL be the
maximum of present lower limits and the effective upper limit the minimum
of present upper limits. `None` SHALL contribute no limit on its side. An
empty numeric intersection SHALL be refused with target and limits named.
An invalid bound contribution SHALL be refused even when another constraint
would be tighter.

An untimed enumeration SHALL judge available added constraints after its
relations finish, using each contribution's own declaration scope, without
depending on sibling order. An unknown or symbolic read SHALL defer only
its contribution; other known limits SHALL remain enforceable. Existing
run-owned and clocked-request-owned exemptions SHALL remain in force.

#### Scenario: A wide installation limit does not remove a part's own stop

- **WHEN** a descendant joint has range `(0, 90)` and its ancestor adds
  `(-10, 120)`
- **THEN** its permitted travel remains `(0, 90)`

#### Scenario: Independent scopes contribute both sides

- **WHEN** a joint, its parent and a higher ancestor each declare limits
  reading coordinates in their respective scopes
- **THEN** all limits constrain the same actual coordinate and each read
  resolves in the scope where that contribution was written

#### Scenario: An unknown read does not disable a known stop

- **WHEN** an untimed pose exceeds the joint's own numeric upper limit while
  an ancestor constraint has an unbound read
- **THEN** the known limit still refuses the pose and identifies the joint

#### Scenario: A scoped obstacle refuses an impossible untimed pose

- **WHEN** an untimed enumeration finishes with a target beyond a bound
  declared in an ancestor and all its reads are numeric
- **THEN** the joint range error names the target, evaluated limit and reads,
  regardless of the order in which sibling relations bound them
