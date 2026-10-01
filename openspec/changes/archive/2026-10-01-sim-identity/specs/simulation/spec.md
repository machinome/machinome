## ADDED Requirements

### Requirement: A clocked simulation publishes its machine's identity

The system SHALL provide a read-only `sim.identity` on a `Sim` constructed
over a clocked root. It SHALL be the compiled clocked machine's identity,
the same string every document producer publishes as `clocked.identity`
for the same model. A consumer that records requests through `Sim` can
therefore compare it with an export's `clocked.identity`, and refuse a
recording made over a machine that differs from the one the export carries.

The identity SHALL describe the machine and not its bank. A `Sim` opened
with `state=`, moved by requests, restored from a snapshot or reset SHALL
report the same identity as a `Sim` over the same model at its declared
rest. Two models whose compiled machines differ SHALL report different
identities, by the definition of the identity in the export requirement
that defines the `clocked` object.

On a `Sim` whose root is not clocked — an untimed root, or a root declaring
`Time.running()` — reading `sim.identity` SHALL be refused with a
`TypeError` that names `identity` and the model's class and says that
nothing in its tree declares a `State`. Under a running root the refusal
SHALL also name `sim.program.identity` as the member that carries that
root's compiled program identity. No value SHALL be returned in place of
the refusal.

The clocked snapshot's shape, `restore`'s comparison and every published
document SHALL be unchanged by this member.

#### Scenario: The identity is the one the export carries

- **WHEN** a clocked model is exported and a `Sim` is constructed over a
  fresh instance of the same model
- **THEN** `sim.identity` equals the manifest's `clocked.identity`

#### Scenario: The identity does not move with the bank

- **WHEN** a `Sim` over a clocked model is opened with `state=` naming a
  state away from its default, moved by a request, restored to an earlier
  snapshot and reset
- **THEN** `sim.identity` is the same string at every step, and equal to the
  identity of a `Sim` over the same model at its declared rest

#### Scenario: Different machines have different identities

- **WHEN** two clocked models whose compiled machines differ are each
  simulated
- **THEN** their `sim.identity` values differ

#### Scenario: A simulation that is not clocked refuses the identity by name

- **WHEN** `sim.identity` is read on a `Sim` over an untimed root and on a
  `Sim` over a root declaring `Time.running()`
- **THEN** each read raises `TypeError` naming `identity` and the model's
  class, and the running root's message names `sim.program.identity`
