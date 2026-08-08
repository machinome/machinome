## MODIFIED Requirements

### Requirement: The shop floor provides a structured browser workspace
The shop floor SHALL present the maker with one full-height browser workspace
at the shop-floor browser location. The browser document title and visible
workspace title bar SHALL identify the product as `SolidNode Studio`. On a
desktop browser, the workspace SHALL provide a title bar and status bar
surrounding an activity rail, an agent context panel, a central artifact area,
and a right conversation area. The activity rail SHALL show Model as selected
and SHALL show Files, Agents, Sheets, and Code as hoverable, non-interactive
deferred areas. The status bar SHALL be visible and need not contain status
content until that information is available.

#### Scenario: A maker opens the shop floor
- **WHEN** the maker opens the running shop-floor browser location
- **THEN** the browser and visible title bar identify `SolidNode Studio`, and
  the page shows the activity rail, agent context panel, artifact area, and
  conversation area within the desktop workspace shell

#### Scenario: A maker views the desktop workspace
- **WHEN** the maker opens the shop floor in a desktop browser window
- **THEN** the artifact area is the flexible central viewport and the
  conversation is a distinct right-side column

#### Scenario: A maker hovers a deferred activity area
- **WHEN** the maker hovers Files, Agents, Sheets, or Code in the activity rail
- **THEN** the item shows its hover treatment and does not navigate, select a
  panel, or change the model viewport

#### Scenario: A maker uses a narrow browser window
- **WHEN** the maker opens the shop floor in a narrow browser window
- **THEN** every workspace area remains reachable without horizontal page overflow
