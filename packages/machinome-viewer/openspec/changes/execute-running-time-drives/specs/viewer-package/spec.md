## ADDED Requirements

### Requirement: A maker operates an autonomously powered running machine

The viewer SHALL execute a supported running machine's declared autonomous
motion when its run is played or stepped, without requiring an operator to
issue a synthetic motion command. Mounting SHALL preserve the existing paused
rest state. Elapsed seconds SHALL remain read-only and outside operator inputs.
Versions 1–9 SHALL retain their existing behavior.

#### Scenario: Astrarium advances without a startup input

- **WHEN** a maker mounts Astrarium's time-driven fixture and steps its run
- **THEN** the shaft and weight advance from declared state, while only enable
  and winding are exposed as operator inputs

#### Scenario: Stop, wind and restart preserve history

- **WHEN** the maker disables Astrarium, waits, winds and enables it again
- **THEN** the shaft holds while stopped, winding restores reserve without
  reversal, and subsequent running adds only newly elapsed travel

### Requirement: An autonomous mechanical stop does not stop elapsed time

A mechanical stop SHALL limit only the motion paths pushing it. Unrelated
autonomous mechanisms and relieving operator inputs SHALL continue. Elapsed
seconds SHALL continue advancing. A stopped autonomous path SHALL attempt the
next global interval without recovering missed travel, including nonlinear
time laws. Grouped outputs SHALL share their relation's stop. Save, restore,
reset and refused ticks SHALL preserve existing retained-state guarantees.

#### Scenario: One train exhausts while another runs

- **WHEN** one independently time-driven train reaches a travel bound
- **THEN** that train stops coherently at the boundary, the other keeps moving,
  and the elapsed clock completes the tick

#### Scenario: A curved input reaches a downstream stop

- **WHEN** a nonlinear time-driven shaft pushes a ranged follower to its stop
- **THEN** both commit the same admitted mechanical path at the located boundary
  rather than snapping only the follower

#### Scenario: A failed tick is atomic

- **WHEN** incompatible laws refuse a tick after an autonomous path has moved
- **THEN** its bank, clock and recorded history remain at the prior commit

### Requirement: Time-drive compatibility is checked before execution

The viewer SHALL accept well-formed producer document-v10 time-drive programs
and SHALL refuse malformed time-drive mappings, undeclared or writable clock
sources, reserved IDs used as physical state, and unknown admission candidates
before rendering or ticking, naming the document and offending field. The public
stop record SHALL retain real operator IDs in `inputs` and report independently
blocked time relations in `time_drives` only when nonempty. Legacy records SHALL
retain their previous shape.

#### Scenario: An invalid time-drive mapping is refused

- **WHEN** a document maps an invalid edge, duplicates a drive, or omits a
  mapping for an edge that reads the clock
- **THEN** loading fails by name instead of running an inert or coupled machine

#### Scenario: An autonomous stop has distinct provenance

- **WHEN** a purely autonomous train reaches its bound
- **THEN** its stop names the blocked time relation and reports no invented
  operator input or command

### Requirement: Producer time-drive parity includes browser acceptance

The viewer suite SHALL replay every recorded step of the unchanged producer
time-drive corpus, including bank, time, crossings, stops, command outcomes,
restore and reset. Floats SHALL use the corpus's own tolerance; discrete fields
and list order SHALL match exactly. Astrarium's published export SHALL additionally
be exercised in a browser through both normal worker and in-thread fallback
execution. No framework import SHALL be needed by the viewer or its tests.

#### Scenario: The originating clock works in both browser transports

- **WHEN** the Astrarium export is stepped, stopped, wound, exhausted and restored
  through the browser handle in each execution mode
- **THEN** its retained values agree with the verified project behavior and its
  rendered parts follow that bank
