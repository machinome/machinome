## ADDED Requirements

### Requirement: One stream carries all live shop state to the browser
The shop-floor service SHALL deliver every live change in shop state to a
connected browser over one Server-Sent Events connection per page. Agent
lifecycle, work state, conversation entries, model changes, model build outcomes
and shop-open state SHALL all travel on that one stream. The browser SHALL NOT
open a second stream to learn whether the shop is open.

#### Scenario: A page connects to the open shop floor
- **WHEN** the maker opens the shop-floor browser location while the service is running
- **THEN** the page holds exactly one Server-Sent Events connection to the service

#### Scenario: Live state changes while the page is open
- **WHEN** an agent's state, the conversation, or the published model changes while the page is open
- **THEN** the change reaches the page over that one connection without a page reload

### Requirement: Every connection opens with a complete snapshot
The first event on every live-state connection SHALL be a snapshot carrying the
current run state and the complete ordered conversation, whether that connection
is the page's first or a reconnection. A connecting browser SHALL be able to
render the whole workspace from that snapshot alone, without issuing a separate
request for run state or conversation, and without reconciling the snapshot
against state it held previously.

#### Scenario: A page connects mid-run
- **WHEN** a browser connects after agents have manifested and messages have been recorded
- **THEN** the first stream event carries the current run state and every recorded conversation entry in original order

#### Scenario: The browser reloads during an active conversation
- **WHEN** the maker reloads the page during an active conversation
- **THEN** the restored transcript comes from the snapshot event and matches the original order and attribution

#### Scenario: An event is published while the snapshot is being prepared
- **WHEN** the broker publishes an event between a client's connection being accepted and its snapshot being sent
- **THEN** the client receives that event after the snapshot, and receives it exactly once

### Requirement: Reconnection restores complete current state
When a browser's live-state connection drops and is re-established, the service
SHALL restore the browser to the shop's complete current state through the
snapshot on the new connection. The browser SHALL NOT be required to track a
position in the event history, and SHALL NOT silently retain state that changed
while it was disconnected.

#### Scenario: A conversation entry is recorded while the browser is disconnected
- **WHEN** the user-facing agent records a conversation entry while the browser is briefly disconnected, and the browser then reconnects
- **THEN** the transcript shown after reconnection contains that entry exactly once

#### Scenario: An agent's state changes while the browser is disconnected
- **WHEN** a declared agent starts or completes work while the browser is disconnected, and the browser then reconnects
- **THEN** the agent panel shows that agent's current state, not the state it held before the disconnection

#### Scenario: The service restarts beneath an open page
- **WHEN** the shop-floor service restarts at the same browser location and the page reconnects
- **THEN** the page shows the restarted floor's state from the new connection's snapshot, with no state carried over from the previous connection

### Requirement: The browser does not poll for streamed state
The browser SHALL NOT re-request run state or conversation on a timer, and SHALL
NOT depend on periodic re-fetching to correct state the stream is responsible
for delivering. State the stream provides SHALL be requested at most once per
connection, as the snapshot.

#### Scenario: The page is open and idle
- **WHEN** the shop-floor page is open and no shop state is changing
- **THEN** the page issues no repeating requests for run state or conversation

#### Scenario: The stream is the only repair path
- **WHEN** the page has missed state changes because its connection dropped
- **THEN** the missed state is recovered through the snapshot on reconnection, not through a scheduled re-fetch
