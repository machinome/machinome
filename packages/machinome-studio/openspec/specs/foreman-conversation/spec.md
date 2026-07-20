# foreman-conversation Specification

## Purpose

Let the maker and active foreman share an ordered conversation in the local
shop-floor workspace.

## Requirements

### Requirement: The maker and foreman share an ordered conversation
The shop floor SHALL let the maker submit a text message to the currently
running foreman conversation. The conversation SHALL show maker and foreman
messages in their recorded order, and SHALL not provide a direct-conversation
control for another agent.

#### Scenario: A maker directs the foreman
- **WHEN** the maker submits a non-empty message in the foreman-conversation area
- **THEN** the message appears in the conversation as a maker message available to the foreman

#### Scenario: The foreman communicates with the maker
- **WHEN** the foreman publishes a conversation message
- **THEN** the message appears in the conversation as a foreman message without requiring a browser reload

### Requirement: The active conversation survives browser reload
While the shop-floor service remains running, the shop floor SHALL restore the
active foreman conversation when the maker reloads the browser page.

#### Scenario: A maker reloads during an active conversation
- **WHEN** the maker reloads the shop-floor page after maker or foreman messages were recorded
- **THEN** the conversation shows those recorded messages in their original order
