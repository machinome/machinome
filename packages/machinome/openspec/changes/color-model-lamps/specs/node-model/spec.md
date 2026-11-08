## MODIFIED Requirements

### Requirement: Color declaration

The system SHALL accept a class-level `color` in `#RRGGBB` form and reject
any other non-None value with `ValueError` during colorization, except the
validated symbolic two-color value returned by `machinome.color.color_when`
under the `state-color` capability.

A node's `color` remains one colour for the whole node and remains optional. A
**marking** declared on a rigid node under the `markings` capability carries
its own colour, validated in the same `#RRGGBB` form and rejected with the same
`ValueError`, and required rather than optional: a marking with no colour would
declare nothing. A marking's colour SHALL NOT change the node's own.

#### Scenario: Invalid color

- **WHEN** a node declares `color = 'red'`
- **THEN** assembling it raises `ValueError`

#### Scenario: A marking's colour is separate from the node's

- **WHEN** a node declaring `color = '#222831'` carries a marking declaring
  `color = '#FFFFFF'`
- **THEN** the node's published colour is `#222831` and the marking's is
  `#FFFFFF`

#### Scenario: A conditional color preserves the same whole-node semantics

- **WHEN** a node's color is the supported two-color choice rather than a fixed hex
- **THEN** it colors that same node as a whole, inherits through uncolored descendants as before, and does not change fixed marking colors
