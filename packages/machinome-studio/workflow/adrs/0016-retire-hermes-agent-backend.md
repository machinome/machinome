# ADR 0016: Retire Hermes as a shop agent backend

**Status:** Accepted

**Date:** 2026-08-09

**Deciders:** Pilot

**Origin:** OpenSpec change `retire-hermes-backend`

**Supersedes:** [ADR 0007](./0007-hermes-second-prompt-steering.md)

**Amends:** [ADR 0006](./0006-pluggable-agent-backend-orchestration.md)
and [ADR 0011](./0011-profile-defined-shop-runtime.md)

## Context

ADR 0006 introduced Hermes as the first second backend and used it to establish
the portable `AgentBackend` seam. ADR 0007 then accepted a dependency on
Hermes 0.19.0's undocumented second-prompt steering behavior because ACP had no
steer primitive and cancellation left sessions unusable.

That integration proved backend neutrality, but it also accumulated a large
Hermes-specific ACP client, fake server, timing behavior, content filtering,
and version-sensitive cancellation and steering rules. Hermes is a different
class of tool from the persistent agent runtimes that fit this backend seam.
Maintaining it as though it were another equivalent backend now costs more than
the capability justifies.

The original reason for adding Hermes was multi-provider support. OpenCode now
provides that path with a cleaner password-protected HTTP/SSE server and
persistent session integration under the bounded compatibility policy in ADR
0012.

## Decision

The shop SHALL retire Hermes as an agent backend. `hermes` SHALL no longer be a
valid `--backend` value, the Hermes ACP adapter and its dedicated fixtures and
tests SHALL be removed, and runtime profiles SHALL no longer declare Hermes
model, effort, or tool policy.

Codex, Claude, and OpenCode are the supported backend set. Codex and Claude
continue to consume profile-explicit runtime policy. OpenCode continues to use
the bounded adapter-owned compatibility policy established by ADR 0012 and
serves as the shop's multi-provider route.

The portable `AgentBackend` protocol remains an architectural boundary. Hermes
helped prove that boundary; retiring one implementation does not collapse the
orchestrator back into a vendor-specific design.

Hermes-specific active specifications and product documentation SHALL be
removed. Historical ADRs, archived OpenSpec changes, sprint records, and
empirical traces SHALL remain as evidence of the decisions and behavior that
existed at the time.

If Hermes returns, it SHALL require a new decision defining an integration
boundary appropriate to its actual tool class. This decision does not reserve
or design that future boundary.

## Alternatives considered

### Continue maintaining Hermes beside the other backends

Rejected. The undocumented ACP steering dependency, cancellation behavior,
adapter code, and bespoke fixture impose high continuing cost without adding a
provider path that OpenCode does not already cover more cleanly.

### Rework Hermes until it fits the existing backend abstraction

Rejected. The pilot's finding is that Hermes is a different class of tool, so
further investment in making it resemble an equivalent persistent backend
would preserve the category error rather than resolve it.

### Retire Hermes and use OpenCode for multi-provider execution

Accepted. This keeps the capability that motivated Hermes while reducing the
maintained integration surface.

## Consequences

### Positive

- The shop loses the ACP client, fake ACP server, off-spec steering behavior,
  and the tests and documentation needed to maintain them.
- Profiles and their validation contract become smaller and clearer.
- Multi-provider execution remains available through OpenCode.

### Negative and trade-offs

- Existing commands using `--backend hermes` fail and must select Codex,
  Claude, or OpenCode.
- The shop no longer provides a Hermes ACP session integration or its measured
  in-turn correction behavior.

### Neutral

- The portable backend seam and remaining adapters do not change.
- ADR 0007 and its archived empirical evidence remain available as historical
  records, but its decision is no longer operative.
- A future Hermes integration remains possible only through a separately
  ratified boundary suited to its tool class.
