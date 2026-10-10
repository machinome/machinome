## ADDED Requirements

### Requirement: A reused-joint mate handle shares the child slot

Reading a reused-joint mate on an instance SHALL return the same bound coordinate slot as its referenced child's joint; assigning through either spelling SHALL use the same original joint binding and placement path. The handle SHALL create no port slot on its assembly and SHALL not be reported as an assembly-owned coordinate by declared_ports. The child's joint SHALL remain reported once under its original name. Domain and unit of declaration references to the handle SHALL come from that joint without renaming its port metadata. Existing one-binder, wiring and run-owned refusals SHALL apply to the physical child slot regardless of spelling.

The attachment SHALL add no wiring and SHALL not impose fresh-freedom mate-exclusive binding on the existing joint. If the joint already has an author wiring, that wiring SHALL remain the sole writer under the existing rules. Guarded initialization and unbound reads SHALL behave as they did before attachment. A fresh-freedom mate SHALL retain its separate assembly port and exclusive wiring unchanged.

#### Scenario: A handle reads and writes the original coordinate

- **WHEN** an assembly reads its reused-joint mate handle and child.turn, then binds one spelling in an otherwise permitted phase
- **THEN** both reads identify the same child slot and the original joint places the child once

#### Scenario: A guarded dial default remains permitted

- **WHEN** simulate tests dial.turn.value is None and initializes dial.turn before a running simulation owns it
- **THEN** the guard sees the original unbound state and the ordinary initialization succeeds without a mate-exclusive wiring refusal

#### Scenario: Existing wiring is not taken over

- **WHEN** a child joint already wired from an author coordinate is reused by an attachment
- **THEN** the original wiring remains, no mate wiring is added, and a conflicting assignment through the handle receives the same original wiring refusal

#### Scenario: The running owner is not bypassed

- **WHEN** an author's simulate attempts to bind a run-owned child joint through its reused-joint mate handle
- **THEN** the ordinary run-owned doubly-bound refusal occurs on the same physical coordinate

#### Scenario: Enumeration carries no assembly alias

- **WHEN** ports are enumerated on an assembly with one reused-joint mate and on its child
- **THEN** no coordinate entry appears for the mate on the assembly, and the child reports its original joint coordinate once
