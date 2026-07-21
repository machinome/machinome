# foreman-conversation Specification

## Purpose

Let the maker and active foreman share an ordered conversation in the local
shop-floor workspace.

## Requirements

### Requirement: The maker and foreman share an ordered conversation
The shop floor SHALL let the maker submit a text message to the currently
running foreman conversation. The conversation SHALL show maker and foreman
messages in their recorded order in a compact, independently scrollable chat
transcript that attributes each message to its participant without a visible
foreman-specific conversation title. The composer SHALL present a message field
without visible foreman-directed wording and a submit control labelled `Send`.
Pressing Enter in the message field SHALL submit its non-empty draft. Pressing
Ctrl+Enter SHALL insert a line break in the draft without submitting it.
The shop floor SHALL not provide a direct-conversation control for another
agent.

#### Scenario: A maker directs the foreman
- **WHEN** the maker submits a non-empty message through the chat composer
- **THEN** the message appears in the conversation as a maker message available to the foreman

#### Scenario: A maker sends with Enter and composes with Ctrl+Enter
- **WHEN** the maker presses Ctrl+Enter while composing a message
- **THEN** the message field gains a line break and no message is submitted
- **WHEN** the maker then presses Enter
- **THEN** the full multiline message is submitted to the conversation

#### Scenario: The foreman communicates with the maker
- **WHEN** the foreman publishes a conversation message
- **THEN** the message appears in the conversation as a foreman message without requiring a browser reload and the transcript scrolls to reveal its newest message

### Requirement: The active conversation survives browser reload
While the shop-floor service remains running, the shop floor SHALL restore the
active foreman conversation when the maker reloads the browser page.

#### Scenario: A maker reloads during an active conversation
- **WHEN** the maker reloads the shop-floor page after maker or foreman messages were recorded
- **THEN** the conversation shows those recorded messages in their original order
