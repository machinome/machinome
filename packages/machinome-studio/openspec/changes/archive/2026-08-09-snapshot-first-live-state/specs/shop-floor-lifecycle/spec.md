## MODIFIED Requirements

### Requirement: The browser shows the shop lifecycle without a reload
The shop-floor service SHALL serve a browser page that displays `Shop is open`
while its live connection to the service is established, and `Shop is closed`
when that connection is lost. The page SHALL NOT maintain a second connection
for lifecycle status. If the service restarts at the same local browser
location, the already-open page SHALL reconnect, display `Shop is open` again,
and display the restarted shop's actual state — not merely the open indicator —
without a page reload.

#### Scenario: The browser opens while shop-floor is running
- **WHEN** a maker opens the shop-floor browser location while the service is running
- **THEN** the page displays `Shop is open`

#### Scenario: The service stops while the browser page remains open
- **WHEN** the shop-floor service shuts down while its browser page remains open
- **THEN** the page displays `Shop is closed` without a page reload

#### Scenario: The service restarts while the browser page remains open
- **WHEN** the shop-floor service restarts at the same browser location after the page displayed `Shop is closed`
- **THEN** the page reconnects, displays `Shop is open`, and displays the agents, work states, and conversation of the restarted shop without a page reload

#### Scenario: The restarted service publishes new work
- **WHEN** a page has reconnected to a restarted shop-floor service and that service manifests an agent or records a conversation entry
- **THEN** the page displays that change without a page reload
