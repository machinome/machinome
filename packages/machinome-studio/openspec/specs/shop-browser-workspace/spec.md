# shop-browser-workspace Specification

## Purpose

Provide the maker with one structured shop-floor workspace for live shop
context, artifact inspection, and foreman conversation.

## Requirements

### Requirement: The shop floor provides a structured browser workspace
The shop floor SHALL present the maker with one full-height browser workspace
containing a left shop-menu column and a right content column at the shop-floor
browser location. The content column SHALL contain the artifact area above the
foreman-conversation area, with the artifact area occupying 60% and the
foreman-conversation area occupying 40% of the available content height.

#### Scenario: A maker opens the shop floor
- **WHEN** the maker opens the running shop-floor browser location
- **THEN** the page shows the menu as a left column and the artifact and foreman-conversation areas as vertically stacked right-side panes

#### Scenario: A maker views the desktop workspace
- **WHEN** the maker opens the shop floor in a desktop browser window
- **THEN** the artifact area occupies 60% and the foreman-conversation area occupies 40% of the right-side content height

#### Scenario: A maker uses a narrow browser window
- **WHEN** the maker opens the shop floor in a narrow browser window
- **THEN** every workspace area remains reachable without horizontal page overflow

### Requirement: The workspace menu preserves live shop context
The full-height workspace menu SHALL show the current shop lifecycle status,
active run identity, and manifested-agent state using the existing live
shop-floor data.

#### Scenario: An agent changes work state
- **WHEN** a manifested agent's state changes while the maker is viewing the workspace
- **THEN** the corresponding agent state in the workspace menu updates without a page reload

### Requirement: Deferred workspace areas are truthful
Until artifact inspection is available, the artifact area SHALL show that no
artifact is selected. Once a functional model is available, it SHALL present an
interactive, correctly materialled browser viewer. The foreman-conversation
area SHALL show the active foreman conversation and a control for directing the
foreman; it SHALL not claim that a foreman conversation is unavailable.

#### Scenario: The workspace has no selected artifact
- **WHEN** the maker opens the Story 3 workspace before artifact inspection is implemented
- **THEN** the artifact area shows its empty state and the foreman-conversation area remains available for conversation

#### Scenario: The workspace has a built functional model
- **WHEN** the shop floor has successfully built the project's functional model
- **THEN** the artifact area presents the current completed `_build` model as an interactive browser viewer instead of the empty state
