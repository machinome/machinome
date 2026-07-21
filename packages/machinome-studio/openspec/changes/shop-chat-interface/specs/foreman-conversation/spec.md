## MODIFIED Requirements

### Requirement: The maker and foreman share an ordered conversation
The shop floor SHALL let the maker submit a text message to the currently
running foreman conversation. The conversation SHALL show maker and foreman
messages in their recorded order in a compact, independently scrollable chat
transcript that attributes each message to its participant without a visible
foreman-specific conversation title. The composer SHALL present a message field
without visible foreman-directed wording and a submit control labelled `Send`.
The shop floor SHALL not provide a direct-conversation control for another
agent.

#### Scenario: A maker directs the foreman
- **WHEN** the maker submits a non-empty message through the chat composer
- **THEN** the message appears in the transcript as a maker message available to the foreman

#### Scenario: The foreman communicates with the maker
- **WHEN** the foreman publishes a conversation message
- **THEN** the message appears in the transcript as a foreman message without requiring a browser reload and the transcript scrolls to reveal its newest message
