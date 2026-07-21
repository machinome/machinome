## Context

Shop-floor is a local FastAPI broker with a browser workspace and an SSE stream
for live agent-state updates. Its foreman-conversation pane is deliberately an
empty state. The `shop-ui-spike` branch demonstrated an append-only event
ledger and a command that blocks until an event addressed to an agent arrives.

The porter is the Codex CLI agent that starts and stops shop-floor and launches
or ends the foreman and its specialist agents. The foreman is a distinct agent
launched by the porter; within shop-floor work, it manages the other agents.
The porter is not a conversation relay. Instead, the foreman directly uses the broker:
it waits for maker messages, handles the returned message(s) in its normal
agent context, publishes any message it elects to send, and starts waiting
again.

## Goals / Non-Goals

**Goals:**

- Make the browser and the active foreman surfaces of one conversation.
- Preserve ordered conversation history across browser reloads while the
  running shop-floor process remains available.
- Allow the foreman to decide when it communicates, without encoding an
  acknowledgement, progress, or one-reply-per-message policy.
- Drain messages that arrive while the foreman is handling earlier ones when
  the listener next runs.

**Non-Goals:**

- Persisting a conversation across shop-floor process restart.
- Direct maker conversation with specialist agents.
- Giving the porter shop-work decision authority or making it a conversation
  relay.
- Adding a general orchestration-event protocol or project browsing.

## Decisions

### Use an in-process ordered conversation ledger

The broker will hold ordered maker and foreman conversation entries for the
active run and expose them to the browser. This makes history available after
a browser reload without making restart durability a product promise.

Alternative considered: browser-only storage. Rejected because the foreman and
browser need one shared record, and browser storage cannot
reliably represent messages sent while the page is closed.

Alternative considered: SQLite persistence from the spike. Deferred: it is a
reasonable future implementation option, but restart recovery is deliberately
outside this story and a durable schema would prematurely define that
behavior.

### Give the foreman direct broker operations

The broker provides the foreman with one blocking receive operation for maker
messages and one publish operation for foreman messages. Receive accepts the last handled
conversation sequence and returns every later maker message that is queued
once at least one is available, together with the new sequence. The foreman
carries that cursor into its next listener invocation. This avoids treating
delivery as acknowledgement: a message is not skipped merely because a
previous listener invocation ended. Publish appends an independently chosen
foreman message to the same conversation. The porter launches the
foreman, but does not wait for, forward, or publish these messages.

Alternative considered: a browser request that waits for a model response.
Rejected because it falsely makes foreman communication request/response and
would prevent the foreman from reporting at the moment its work warrants it.

### Name the routine lifecycle role the porter

The Codex CLI agent that opens and closes the shop-floor door and launches or
ends agents is named the **porter**. It obeys routine lifecycle instructions,
but does not make project, design, or shop-work decisions. The foreman remains
the manager of shop-floor agents and directly communicates with the broker.

Alternative considered: *shop runner*. Rejected because it obscures the
foreman's distinct role in running the shop. *Gatekeeper* was also rejected:
it suggests authority to decide who or what may proceed. *Porter* conveys
arrival, departure, and routine access without management authority.

### Stream conversation updates through the existing run stream

The broker publishes conversation-entry events on the existing per-run SSE
stream. The browser loads the current conversation first, then applies new
entries from that stream. This keeps the existing live-workspace transport and
gives reload recovery a clear snapshot-plus-stream sequence.

Alternative considered: frontend polling. Rejected because the workspace
already has a live run stream and polling adds delay and duplicated state
paths.

## Risks / Trade-offs

- [The foreman does not resume the listener] → Messages remain visibly queued
  in the shared conversation record; this change makes no false guarantee of
  automatic foreman wake-up.
- [An in-process broker loses history on restart] → The UI states that the
  active conversation is unavailable after the service stops; durable recovery
  remains a later decision.
- [A slow browser misses stream events] → Reload obtains the full current
  conversation snapshot before reconnecting to the run stream.
- [Unbounded local message history] → This first active-run slice has no
  retention promise; limits or archival require a later, explicit policy.
