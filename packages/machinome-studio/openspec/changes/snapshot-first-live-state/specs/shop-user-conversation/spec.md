## MODIFIED Requirements

### Requirement: The active profile conversation survives browser reload
While the service remains running, the shop floor SHALL restore the active
conversation after browser reload with original order, stable internal author
IDs, and labels from the active profile. The restored transcript SHALL arrive
with the browser's live connection rather than through a separate conversation
request, and SHALL likewise be restored when a live connection is
re-established without a reload.

#### Scenario: The browser reloads during an active conversation
- **WHEN** user or user-facing-agent messages have been recorded and the browser reloads
- **THEN** the transcript restores those messages in original order with the active profile's participant labels

#### Scenario: A message is recorded while the browser is disconnected
- **WHEN** a conversation entry is recorded while a browser's live connection is down, and that connection is re-established
- **THEN** the transcript shows that entry in its original order, exactly once, without a page reload
