## Why

The browser chat is difficult to follow because it receives only 40% of the
workspace and presents every message as a padded card inside a titled panel.
The conversation needs to work as a compact, continuously readable chat
surface as the shop later adds messages from more participants.

## What Changes

- Give the desktop chat area half of the right-side workspace height, without
  retaining a browser test that asserts an exact percentage or pixel split.
- Replace the titled, card-based foreman panel with a compact scrollable chat
  transcript that distinguishes participants without centering the experience
  on the foreman.
- Simplify the composer to the message field and a `Send` button; remove the
  visible foreman-specific title and field/button wording.
- Let Enter send a message and Ctrl+Enter add a line break without sending it.
- Scroll the chat transcript to its newest message when the foreman publishes
  a new message.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `foreman-conversation`: The live conversation gains chat-oriented transcript
  presentation, generic keyboard composer behavior, and
  newest-foreman-message auto-scroll behavior.
- `shop-browser-workspace`: The browser workspace gives conversation a 50/50
  desktop share with artifact inspection and removes the exact-ratio acceptance
  assertion.

## Impact

The React conversation component, workspace and chat CSS, browser acceptance
coverage, and the two affected OpenSpec baseline capabilities are updated. The
conversation broker and its HTTP API remain unchanged.
