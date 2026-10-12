## REMOVED Requirements

### Requirement: The maker and foreman share an ordered conversation
**Reason**: Conversation participants are no longer fixed to Maker and Foreman; `shop-user-conversation` defines stable user identity and the profile's declared user-facing agent.

**Migration**: Use the generic user-conversation API and render participant labels from active profile run state.

### Requirement: The active conversation survives browser reload
**Reason**: Conversation restoration now belongs to the profile-neutral `shop-user-conversation` capability.

**Migration**: Restore the generic active-profile conversation through the new conversation representation.

### Requirement: The foreman remains available while shop work proceeds
**Reason**: Availability and steering now apply to whichever agent the profile declares user-facing, including Builder.

**Migration**: Use `shop-user-conversation` direction delivery and `shop-agent-messaging` profile routing.
