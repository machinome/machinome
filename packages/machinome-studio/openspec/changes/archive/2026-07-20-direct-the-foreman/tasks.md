## 1. Conversation broker and bridge

- [x] 1.1 Add an ordered active-run conversation ledger and HTTP operations for submitting maker messages, reading the conversation, and recording foreman messages.
- [x] 1.2 Publish new conversation entries on the existing run SSE stream and preserve agent-state stream behavior.
- [x] 1.3 Add direct broker operations for the foreman: receive with a returned sequence cursor to block and drain later maker messages, and publish to record a foreman message.
- [x] 1.4 Document the foreman listener loop: receive from the broker, handle in the foreman agent, publish when warranted, and listen again.
- [x] 1.5 Promote the accepted porter role boundary to an ADR and align relevant shop role documentation.

## 2. Browser conversation workspace

- [x] 2.1 Replace the foreman-conversation empty state with an accessible ordered transcript and maker message composer.
- [x] 2.2 Load the active conversation on startup, submit maker messages to the broker, and apply live conversation entries without duplicate rendering.
- [x] 2.3 Rebuild the production frontend assets served by shop-floor.

## 3. Evidence and completion

- [x] 3.1 Add red-first broker-interface tests for ordered delivery, listener blocking and queue draining, independent foreman publishing, and reload-visible history.
- [x] 3.2 Extend browser acceptance coverage for directing the foreman, receiving a live foreman message, and restoring the transcript after reload.
- [x] 3.3 Run the focused Python and browser suites, inspect the browser evidence, and record any environment limitation honestly.
