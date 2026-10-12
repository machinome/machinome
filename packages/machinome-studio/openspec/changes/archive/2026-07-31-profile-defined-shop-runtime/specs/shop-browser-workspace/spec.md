## MODIFIED Requirements

> **Synchronization intent:** each MODIFIED requirement in this file replaces
> its complete baseline requirement block, including its scenario set.

### Requirement: The workspace menu preserves live shop context
The full-height workspace menu SHALL show current lifecycle status, run
identity, stable active profile ID, and every profile-declared agent's display
label and live state using broker run data. It SHALL NOT require or invent a
separate profile display label.

#### Scenario: The default profile is visible
- **WHEN** the user opens a default-profile workspace
- **THEN** the menu identifies profile `builder` and shows Builder's live state

#### Scenario: Fordesmac is visible
- **WHEN** the user opens a Fordesmac workspace
- **THEN** the menu identifies profile `fordesmac` and shows Foreman, Designer, Machinist, and Librarian

#### Scenario: An agent changes work state
- **WHEN** a declared agent's state changes while the workspace is open
- **THEN** that agent's state updates without a page reload

### Requirement: Deferred workspace areas are truthful
The artifact area SHALL present the current interactive functional-model viewer
when a complete model exists. The conversation area SHALL show the active
profile conversation and allow direction to its one user-facing agent without
role-specific composer wording or a direct control for another agent.

#### Scenario: The workspace has a built functional model
- **WHEN** the shop floor has successfully built the project's functional model
- **THEN** the artifact area presents the completed `_build` model as an interactive viewer

#### Scenario: The selected profile conversation is available
- **WHEN** either initial profile opens
- **THEN** the conversation area attributes the human and user-facing agent with profile-provided labels and accepts direction for that agent

## ADDED Requirements

### Requirement: Browser participant presentation comes from the active profile
The browser SHALL render the human label, user-facing agent label, roster
labels, conversation attribution, event-log participant summaries, and
accessibility text supplied in run state. It MUST NOT hard-code `Maker`,
`Foreman`, or another profile participant as the meaning of an internal author
ID.

#### Scenario: A profile changes the human label
- **WHEN** a valid profile declares a human label other than `Maker`
- **THEN** the transcript and relevant accessibility text use that configured label while API identity remains `user`
