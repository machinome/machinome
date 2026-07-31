## ADDED Requirements

### Requirement: The user and configured user-facing agent share one ordered conversation
The shop floor SHALL let stable internal participant `user` submit text to the
selected profile's exactly one user-facing agent. The conversation SHALL show
user and user-facing-agent messages in recorded order, attributing them with
the profile's configured human label and agent display label in a compact,
independently scrollable transcript without a visible role-specific
conversation title. New output SHALL scroll the transcript to reveal its newest
message. The browser SHALL provide no direct-conversation control for another
agent.

The composer SHALL have no role-specific directed wording, SHALL label its
submit control `Send`, SHALL submit a non-empty draft on Enter, and SHALL insert
a line break without submitting on Ctrl+Enter.

#### Scenario: Maker directs Builder
- **WHEN** the `builder` profile's Maker submits a non-empty message
- **THEN** it is recorded under internal identity `user` and delivered as direction to Builder

#### Scenario: Maker directs Foreman
- **WHEN** the `fordesmac` profile's Maker submits a non-empty message
- **THEN** it is recorded under internal identity `user` and delivered as direction to Foreman

#### Scenario: The configured agent answers
- **WHEN** the selected profile's user-facing agent produces non-empty backend output
- **THEN** that output appears in the conversation under its configured display label without a browser reload and the transcript reveals the newest message

#### Scenario: A specialist produces output
- **WHEN** a non-user-facing agent produces backend output
- **THEN** the broker does not publish that output directly into the user conversation

#### Scenario: The user composes a multiline message
- **WHEN** the user presses Ctrl+Enter and then Enter in the composer
- **THEN** the draft gains a line break first and the complete multiline message is then submitted once

### Requirement: The active profile conversation survives browser reload
While the service remains running, the shop floor SHALL restore the active
conversation after browser reload with original order, stable internal author
IDs, and labels from the active profile.

#### Scenario: The browser reloads during an active conversation
- **WHEN** user or user-facing-agent messages have been recorded and the browser reloads
- **THEN** the transcript restores those messages in original order with the active profile's participant labels

### Requirement: User direction remains available while work proceeds
The configured user-facing agent SHALL continue receiving user messages and
producing conversation output while other profile agents work. Direction
received during its active tool call SHALL be queued or steered according to
the backend contract and SHALL reach the same active agent before its next task
action. Delivery MUST NOT cancel specialist work or predetermine the agent's
response.

#### Scenario: The user writes while delegated specialists work
- **WHEN** the `fordesmac` Maker writes while any specialist is active
- **THEN** Foreman receives the direction without stopping the specialist assignment

#### Scenario: The user steers Builder
- **WHEN** the `builder` Maker writes while Builder's direct turn is active
- **THEN** the orchestrator steers that same Builder turn under the selected backend's delivery contract
