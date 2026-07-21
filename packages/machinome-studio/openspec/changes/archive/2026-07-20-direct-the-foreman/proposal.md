## Why

The shop-floor workspace currently presents a truthful empty conversation
state. A maker still has to leave that workspace to give the foreman an
instruction or see the foreman's response. The next slice makes the browser a
second surface of the same live foreman conversation, so the foreman can
continue to coordinate the shop without the maker addressing specialist
agents directly.

## What Changes

- Add a local, queued conversation bridge between the browser workspace and
  the foreman through the shop-floor broker.
- Give the foreman direct broker operations that wait for maker messages,
  return queued messages in order, and publish foreman messages to the
  conversation.
- Replace the conversation empty state with an accessible transcript and
  message composer.
- Keep the active conversation available after a browser reload while the
  shop floor remains running. Shop-floor restart persistence is not a
  requirement of this change.
- Keep the foreman in control of when and whether to send a message; the
  bridge does not impose request/response or progress-acknowledgement
  behavior.
- Name and delimit the porter: the routine agent that starts and stops
  shop-floor and launches or ends agents without making shop-work decisions.

## Capabilities

### New Capabilities

- `foreman-conversation`: A maker and the active foreman can
  exchange ordered messages through the local shop-floor workspace.
- `foreman-conversation-bridge`: The foreman directly receives queued maker
  messages from, and publishes its own conversation messages to, the local
  shop-floor broker.

### Modified Capabilities

- `shop-browser-workspace`: The foreman-conversation area becomes an
  interactive conversation surface rather than a deferred empty state.

## Impact

- `floor/` broker API and its event/state handling.
- `floor/frontend/` conversation UI and built static assets.
- The internal broker interface used directly by the foreman listener and
  publisher.
- Shop role documentation and architecture record for the porter boundary.
- Python API tests and browser acceptance coverage.
