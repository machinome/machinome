## ADDED Requirements

### Requirement: The running engine executes published play edges

The viewer SHALL load a version-9 program edge with `kind: "play"`, ordered `needs: [source, retained]`, `gives: [retained]`, finite `low < high`, and the producer's descriptive fields. For each monotonic source segment ending at `x'`, it SHALL set the retained endpoint to `max(x' - high, min(y, x' - low))` from the segment's retained start `y`, using the ordinary bank as its only history and no tolerance.

This SHALL extend "One loader reads either published document" to document
version 9: it is a running document carrying a compiled program, not a
version-8 clocked machine. `play` SHALL be an additional known edge kind;
its explicit retained-coordinate semantics SHALL NOT change the existing
law-edge self-read validation or execution.

#### Scenario: Pickup and reversal execute in the browser engine
- **WHEN** a play follower is collected at either flank and its source reverses into the clearance
- **THEN** it follows while pushed, releases immediately on reversal, and remains exactly retained until the opposite flank reaches it

#### Scenario: A three-wheel chain executes in order
- **WHEN** one driver feeds three play edges in a linear chain
- **THEN** every edge projects the endpoint produced by its predecessor and worker and in-thread execution return the same bank

#### Scenario: Existing self-read edges keep their meaning
- **WHEN** a version-6 or version-7 program carries comparison-based self-read laws and no play edge
- **THEN** the viewer executes its existing retained walk unchanged and does not infer play behavior

### Requirement: A malformed play program is refused before execution

The loader SHALL refuse a play edge unless its source and retained ids, give, finite ordered offsets, initial interval, unique writers, driver-rooted linear chain, and absence of play fan-out match the producer contract. Refusal SHALL name the edge and violated field or relationship and create no running engine.

#### Scenario: A play edge has the wrong shape
- **WHEN** its needs are not exactly source then retained, its give differs from retained, an id is undeclared, or an offset is non-finite or unordered
- **THEN** loading fails by edge identity before any tick can run

#### Scenario: Initial retention is physically inconsistent
- **WHEN** the initial retained bank value lies outside `[source-high, source-low]`
- **THEN** loading refuses rather than projecting or teleporting it

#### Scenario: A play source path is unsupported
- **WHEN** a play edge is rooted in an ordinary edge, participates in a cycle, has an ambiguous writer, or branches to two play followers
- **THEN** loading refuses the unsupported path by the participating edge identities

### Requirement: Stops replay a play chain from its original input

The viewer SHALL locate a stop reached through a play chain by evaluating the whole program prefix from the originating driver's candidate request fraction. It SHALL atomically commit that prefix at the located fraction and SHALL block only an input that pushes the stopped follower.

#### Scenario: A downstream ranged follower clips at the physical input
- **WHEN** `x=0` drives two play gaps of 10, requests `x=100`, and the second follower has high stop 20
- **THEN** the viewer blocks the request at `x=40`, with the first follower at 30 and second at 20

#### Scenario: Release-side travel is free
- **WHEN** a bounded follower stands at contact and its source reverses into the clearance while the follower remains still
- **THEN** the source is not blocked by that follower's bound

#### Scenario: A refused request is atomic
- **WHEN** propagation or a stop invariant refuses a play request
- **THEN** bank, tick, records, and posed tree remain exactly as before it, while commands attempted by that tick retire `refused` with unchanged admitted travel

### Requirement: The producer corpus pins play parity

The viewer SHALL commit the framework's regenerated running corpus byte-for-byte, replay every recorded play step under the corpus's numeric contract, and refuse a copied corpus whose coverage omits play retention, either-flank pickup, reversal, non-integer contact, split requests, cascade, downstream stop, or snapshot replay.

#### Scenario: The regenerated corpus replays completely
- **WHEN** the committed version-9 corpus is tested in-thread
- **THEN** every recorded play state, status, stop, and snapshot result agrees and the coverage census names every required play behavior

#### Scenario: A mounted version-9 page runs
- **WHEN** a real browser mounts a valid play document and submits a driver request
- **THEN** its running handle advances, poses the retained coordinate from the resulting bank, and reports no schema refusal
