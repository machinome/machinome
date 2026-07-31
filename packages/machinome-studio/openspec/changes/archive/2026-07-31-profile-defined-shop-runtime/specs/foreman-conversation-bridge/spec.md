## REMOVED Requirements

### Requirement: The foreman directly receives queued maker messages
**Reason**: The orchestrator already delivers broker envelopes into persistent backend sessions; a Foreman-specific receive operation is incompatible with configurable user-facing agents and direct Builder steering.

**Migration**: Submit generic user direction to the broker; it routes the envelope to the active profile's declared user-facing agent and starts or steers that session.

### Requirement: The foreman directly publishes independently chosen messages
**Reason**: Backend `role_message` events from the profile's declared user-facing agent become the single generic publication path.

**Migration**: Remove the Foreman publish endpoint and CLI; record non-empty backend output from the configured user-facing agent in the generic conversation.
