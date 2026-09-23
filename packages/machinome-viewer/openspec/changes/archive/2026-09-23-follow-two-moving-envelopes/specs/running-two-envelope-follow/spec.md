## ADDED Requirements

### Requirement: A retained follower moves only when either authored envelope pushes it

For a valid version-12 running Follow declaration, the viewer SHALL retain one bank coordinate between independently moving lower and upper authored boundary paths. It SHALL move the follower to the lower boundary when that boundary overtakes it, move it to the upper boundary when that boundary overtakes it from the other side, and otherwise leave the follower at its last admitted value. It SHALL consider the complete certified paths, including interior extrema and jump sides, not only request or tick endpoints. The follower's exact absolute landing SHALL be committed to the bank and reused by bound search, snapshot, restore and replay.

The first Follow contract SHALL be terminal: no downstream compiled edge may read its retained target; its matched dynamic Bounds may read it.

#### Scenario: Bell pushes and releases
- **WHEN** an outward boundary overtakes a standing follower and later retreats without the opposite boundary touching it
- **THEN** the follower moves outward at contact and retains that value through the retreat

#### Scenario: Collar pushes inward
- **WHEN** the upper boundary moves inward across a standing follower while the lower boundary remains clear
- **THEN** the follower moves inward to the upper contact and can move outward later when the lower boundary reaches it

#### Scenario: Interior excursion
- **WHEN** a certified boundary pushes the follower inside a tick or request and returns to its initial value by the endpoint
- **THEN** the follower retains the admitted push rather than being reset by an endpoint-only projection

#### Scenario: Signed-zero tie
- **WHEN** lower, retained and upper values include opposite signed zeros at a projection tie
- **THEN** the committed follower has the same IEEE-754 sign bit as the producer's ordered first-operand min/max result

### Requirement: Incompatible envelopes stop the source before penetration

The viewer SHALL apply the producer's dynamic Bounds to the complete Follow path and SHALL stop a pushing input at the first interval where the lower boundary would exceed the upper boundary. It SHALL report the admitted fraction and the stopping bound, commit only an inside state, and allow a later relieving input. The same request after snapshot restore SHALL reproduce its outcome and full bank.

#### Scenario: Raised carriage blocks crank
- **WHEN** the Curta collar is raised and a crank would carry the bell's lower boundary through the collar's upper boundary
- **THEN** the crank is blocked after its positive admissible travel, the ball remains inside both bounds, and carriage elevation remains unchanged

#### Scenario: Relief and retry
- **WHEN** the blocking collar is lowered and the crank request is retried
- **THEN** the relieved request completes and the ball follows the bell without an impossible-state refusal

#### Scenario: Restore reproduces contact
- **WHEN** a stopped request is replayed from a snapshot taken before it
- **THEN** the admitted travel, stop report and complete retained bank are the same

### Requirement: Unsupported Follow paths are refused, never approximated

The viewer SHALL validate the producer Follow shape and initial interval before ticking. It SHALL certify that both boundary paths can be represented as the supported piecewise-affine path with all needed cut and jump sides; it SHALL refuse malformed, curved, ambiguous or uncertifiable cases by name without committing partial state. It SHALL NOT reinterpret a legacy self-read law or Play edge as Follow.

#### Scenario: Curved or unresolved boundary
- **WHEN** a Follow boundary cannot be certified over the requested path
- **THEN** the request is refused without an endpoint clamp or sampled guess

#### Scenario: Downstream reader is rejected
- **WHEN** a compiled edge other than the required Bounds reads a retained Follow target
- **THEN** the document is refused at load rather than feeding that edge a net-delta approximation of swept motion

#### Scenario: Legacy document
- **WHEN** a valid version-1–11 document contains its existing self-read law or Play edge
- **THEN** it loads and runs with its existing semantics and no Follow behavior
