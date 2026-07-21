## MODIFIED Requirements

### Requirement: The shop floor provides a structured browser workspace
The shop floor SHALL present the maker with one full-height browser workspace
containing a left shop-menu column and a right content column at the shop-floor
browser location. The content column SHALL contain the artifact area above the
conversation area, with each area receiving half of the available content
height in a desktop browser.

#### Scenario: A maker opens the shop floor
- **WHEN** the maker opens the running shop-floor browser location
- **THEN** the page shows the menu as a left column and the artifact and conversation areas as vertically stacked right-side panes

#### Scenario: A maker views the desktop workspace
- **WHEN** the maker opens the shop floor in a desktop browser window
- **THEN** the artifact and conversation areas are both visible and receive equal shares of the right-side content height

#### Scenario: A maker uses a narrow browser window
- **WHEN** the maker opens the shop floor in a narrow browser window
- **THEN** every workspace area remains reachable without horizontal page overflow
