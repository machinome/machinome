## Why

Hermes is a different class of tool from the persistent agent backends that
fit the shop's `AgentBackend` seam. Its undocumented ACP behavior and bespoke
fixtures impose disproportionate maintenance cost, while OpenCode now provides
the intended multi-provider path through a cleaner integration.

## What Changes

- **BREAKING** Remove `hermes` from the supported `--backend` values.
- Delete the Hermes ACP adapter, its fake ACP fixture, and Hermes-specific
  acceptance and profile tests.
- Remove Hermes runtime tables from the built-in profiles and simplify profile
  validation to require only Codex and Claude tables; OpenCode retains its
  bounded adapter-owned compatibility policy.
- Remove active Hermes behavior from baseline specifications, runtime guidance,
  the reference architecture, and product documentation.
- Record the retirement in ADR 0016, superseding ADR 0007 and amending the
  Hermes-specific portions of ADRs 0006 and 0011.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `shop-agent-backend`: Reduce selectable and test-fixture backends to Codex,
  Claude, and OpenCode and remove the Hermes ACP requirements.
- `shop-runtime-profile`: Remove Hermes runtime policy from the strict profile
  schema and built-in profile validity contract.
- `shop-agent-lifecycle`: Remove Hermes from the backends covered by the
  profile-driven role lifecycle contract.
- `shop-floor-lifecycle`: Remove Hermes from the backends covered by the floor
  startup and lifecycle contract.

## Impact

The change removes `floor/backends/hermes.py`, Hermes registration and CLI
selection, profile schema entries, built-in Hermes profile tables, the fake ACP
server, and Hermes-only tests. It updates active OpenSpec baselines, ADR status
and index entries, architecture and README guidance, the running-shop skill,
and the reference design's backend catalogue. Existing callers using
`--backend hermes` must select Codex, Claude, or OpenCode instead.
