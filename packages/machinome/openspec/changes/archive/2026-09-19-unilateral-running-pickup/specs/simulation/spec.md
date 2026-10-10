## ADDED Requirements

### Requirement: A running play law collects and releases a retained coordinate

For each admitted monotonic source segment ending at `x'`, a play edge with retained start `y` SHALL end at `max(x' - high, min(y, x' - low))`.  It SHALL use the run's existing bank as the only history, apply no tolerance, retain the follower throughout the clearance, collect it at either flank, and release it immediately when the source reverses away from that flank.

#### Scenario: Forward pickup and immediate reversal
- **WHEN** `Play(low=-329, high=3)` starts at source and follower zero, the source advances through `3` to `1590`, and then reverses to `1580`
- **THEN** the follower reaches `1587` and remains exactly `1587` during the reversal

#### Scenario: The opposite flank picks up after clearance
- **WHEN** the same source continues backward across the 332-degree clearance
- **THEN** the follower remains retained until `source - follower == -329` and then follows the source backward at that offset

#### Scenario: Exact and non-integer contacts need no tolerance
- **WHEN** either exact endpoint or a finite non-integer contact offset is reached and reversed in either direction under different positive `dt` values
- **THEN** collection and release follow the same projection exactly, with no epsilon-dependent branch or cadence-dependent answer

#### Scenario: Split commands equal one monotonic command
- **WHEN** one monotonic travel is issued as one request or as arbitrary consecutive partial requests with the same path
- **THEN** every final play coordinate agrees under the run's existing numeric agreement contract and snapshot replay reproduces the same bank; a follower retained without motion keeps its held float exactly

### Requirement: A play source path is proved before it runs

The compiler SHALL admit a play source only when it is a run-owned driver or the unique output of another play edge rooted transitively at one run-owned driver.  It SHALL refuse cycles, ambiguous writers, ordinary law, wiring, formula, or otherwise potentially reversing sources before a tick runs. Each coordinate SHALL source at most one play edge; ordinary downstream observers do not count as play branches.

#### Scenario: Play fan-out is refused
- **WHEN** one coordinate sources two different play edges
- **THEN** construction refuses the branching play graph by relation identity, while ordinary downstream observers remain permitted

#### Scenario: Three wheels form a play chain
- **WHEN** a driver feeds three play edges in sequence
- **THEN** compilation orders one linear chain and a monotonic driver request projects through all three edges

#### Scenario: A source can reverse inside a tick
- **WHEN** a play edge reads an ordinary law or formula whose path can rise and fall while its net increment is zero
- **THEN** simulation construction refuses the play edge by identity rather than applying its endpoint projection to the net increment

#### Scenario: An invalid initial state is not teleported
- **WHEN** simulation construction finds the retained value outside `[source-high, source-low]`
- **THEN** construction refuses with the relation, source, retained value, and admissible interval, and changes no state

### Requirement: Stops through play chains locate the originating request

A stop on a coordinate produced by a play chain SHALL be located by replaying the complete chain from the originating driver's requested path.  The run SHALL atomically commit the originating input and every play coordinate at the located fraction, block the request only when it pushes the stopped coordinate, and preserve its existing rollback on refusal.

#### Scenario: A downstream stop is located through both clearances
- **WHEN** source `x=0` drives two play gaps of `10`, `x` requests `100`, and the second follower has a high stop at `20`
- **THEN** the request stops with `x=40`, the first follower `30`, and the second follower `20`, rather than locating from the first follower's net delta

#### Scenario: A released follower does not block its source
- **WHEN** a bounded follower stands at contact and the source reverses into the clearance so that the follower remains still
- **THEN** the source request remains free and the follower's bound reports no pushing stop

#### Scenario: A refused tick is atomic
- **WHEN** play propagation or a stop invariant refuses a tick
- **THEN** the bank, tick, crossing and stop records, and posed tree remain exactly as before the tick, and commands that attempted travel retire `refused` with no travel admitted, preserving the existing running refusal contract

#### Scenario: Reset and restore retain no hidden play state
- **WHEN** a play simulation is snapshotted, advanced, restored, and reset
- **THEN** subsequent answers derive only from the restored ordinary bank and program identity and match a fresh simulation at that state
