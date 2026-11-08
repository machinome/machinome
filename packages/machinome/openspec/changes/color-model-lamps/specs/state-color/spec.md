## Purpose

Select the existing body's unpowered/powered color from model state without changing its physical identity or introducing an appearance state machine.

## ADDED Requirements

### Requirement: A model selects between two fixed colors

The public helper `machinome.color.color_when(condition, *, on, off)` SHALL accept two required `#RRGGBB` strings and a finite numeric bool/real or supported framework symbolic scalar condition. Numeric zero SHALL select `off` and any other finite numeric value SHALL select `on`, returning the existing hex string. A symbolic input SHALL retain one condition graph and both validated strings without evaluating Python truth. Invalid colors, unsupported condition types and non-finite numeric conditions SHALL be refused by name. The result SHALL be assignable to the existing node `color` attribute; no new solid, model input or retained state SHALL be introduced.

#### Scenario: The same glass returns to its dark color

- **WHEN** an existing glass is assigned `color_when(energized > 0.5, on='#ffd978', off='#e5dfce')` at numeric observations 0, 1 and 0
- **THEN** its colors are exactly `#e5dfce`, `#ffd978` and `#e5dfce`, with the same body identity

#### Scenario: A symbolic observation stays deferred

- **WHEN** the same assignment is evaluated under ordinary symbolic driver publication
- **THEN** it retains the predicate and the two colors without `SymbolicTruthError` or a baked default color

#### Scenario: Invalid values do not become visual defaults

- **WHEN** either color is not a six-digit hex, or a numeric condition is NaN/infinite, or the condition has an unsupported type
- **THEN** the helper refuses it naming the invalid argument rather than selecting a fallback color

### Requirement: Color selection follows the standing model state

State-selected color SHALL be recomputed from the same numeric or symbolic model state that poses the node. Reset, restore and replay SHALL not require separate appearance state or host commands. Successful or failed symbolic publication SHALL leave the caller's prior numeric colors, state and pose standing. A color-only state change SHALL preserve geometry bytes, model references, piece identity, inventory and physical contract results for otherwise unchanged geometry.

#### Scenario: Reset and replay clear the lamp

- **WHEN** a sequence energizes a glass, clears the electrical observation on release or power loss, resets and replays, and restores a saved powered state
- **THEN** the same body's color follows those states identically on each replay and restore

#### Scenario: Publication is observational

- **WHEN** a numerically lit model is published, successfully or with a later deliberate publication failure
- **THEN** its prior lit color, bank and pose remain standing after publication exits

#### Scenario: The lamp changes look without changing the part

- **WHEN** the same glass changes only its color choice
- **THEN** its model path, mesh payload, printed-piece identity and physical assertions are unchanged
