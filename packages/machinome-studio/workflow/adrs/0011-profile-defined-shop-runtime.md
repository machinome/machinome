# ADR 0011: Define shop runtime topology with declarative profiles

**Status:** Accepted (amended by ADRs 0012, 0016, and 0017)

**Date:** 2026-07-31

**Amends:** ADR 0006 configuration ownership and global role topology

**Origin:** OpenSpec change `profile-defined-shop-runtime`

## Context

ADR 0006 established the correct portable seam between deterministic shop
orchestration and Codex, Hermes, or Claude agent backends. Above that seam,
however, the broker and orchestrator still hard-code Foreman, Designer, and
Machinist. The broker assigns special meaning to `maker` and `foreman`, and
each backend finds role prompts, skills, model, and tools through a different
global path.

That prevents a run from selecting a different working topology without Python
changes. It also mixes skills available to mechanical-project runtime agents
with skills available to agents developing or operating this repository. The
backend-specific configuration split has already made one role card's
`model: sonnet` control Claude while Codex uses unrelated adapter TOML and
Hermes inherits its process configuration.

The pilot wants Builder to become the default: one persistent agent talks to
Maker directly and owns the complete reversible design/build/test loop. The
existing delegated pipeline must remain selectable as `fordesmac`, with
Librarian regularized as a fourth standing specialist. Profiles and backends
must remain orthogonal.

## Decision

The shop SHALL load one trusted declarative runtime profile before project
preparation. A run selects it with `--profile <id>`; omission selects
`builder`. Profiles live only at `profiles/<id>/profile.toml` in the primary
shop checkout.

A profile SHALL declare:

- stable human presentation label with fixed protocol identity `user`;
- exactly one user-facing standing agent;
- all standing agent IDs, display labels, and profile-owned prompt paths;
- direct or delegated work mode;
- broker-enforced assignment and reporting edges; and
- explicit Codex, Claude, and Hermes model, effort, and tool policy for every
  agent, with `inherit` written when a backend owns the setting.

The broker SHALL own only the resolved profile. It SHALL route user direction
to the declared user-facing agent, publish only that agent's backend output to
the user conversation, and validate assignments and reports against declared
edges. No role name SHALL have architectural meaning in broker code.

The `builder` profile SHALL contain one user-facing Builder in direct mode.
Backend turn start/completion SHALL drive its active/waiting state; it SHALL
not assign, acknowledge, report, or complete work to itself. Builder SHALL use
disassembled-leaf-first TDD: create and wire an existing disassembled leaf,
write the first red fit/assembly test against that existing leaf, then assemble
it and turn the test green. A missing class, node, function, or artifact is not
the first red state.

The `fordesmac` profile SHALL contain standing Foreman, Designer, Machinist,
and Librarian agents in delegated mode. Foreman SHALL be user-facing and the
only assigner of the three specialists, which report only to Foreman. Existing
acknowledged-assignment lifecycle remains authoritative for specialist state.

Runtime prompts SHALL be owned by their profile. Agent prompt frontmatter SHALL
name only skills exposed through that profile's `skills/` allowlist. Shared
runtime engineering skills SHALL live under `shop-skills/`, and a profile SHALL
expose one only through an individual symlink. Repository-development skills
remain under `skills/`; runtime agents SHALL not use that namespace.

The profile loader SHALL produce one validated portable agent definition for
the selected backend. Codex, Claude, and Hermes adapters SHALL consume it
rather than independently finding global role cards or adapter files. ADR
0006's `AgentBackend` ownership, identifiers, steering, events, and shutdown
boundary remains in force.

Profile validation SHALL reject unknown schema keys, invalid IDs, escaping
paths, missing or mismatched prompts, unavailable skills, unsafe links,
invalid topology, and unsupported selected-backend settings before project
creation, validation, build, listener binding, or backend startup.

## Consequences

- The default shop changes from a delegated three-agent team to one Builder.
- `fordesmac` preserves the delegated approach and adds regular standing
  Librarian, increasing that profile to four sessions.
- A new runtime topology can be added as reviewed profile data without broker,
  orchestrator, or backend-specific Python changes.
- Broker APIs and browser payloads become participant-neutral and expose the
  stable selected profile ID plus profile participant labels.
- Global runtime `agents/*.md`, `.codex/agents/<runtime-role>.toml`, and
  `skills/solid-node*` lookup cease to be runtime authority.
- `solid-node-api` and `solid-node` move to `shop-skills/`; the operator-facing
  `running-the-shop` skill remains under repository `skills/`.
- Tool restriction remains honest rather than falsely portable: a profile uses
  a concrete setting where the backend can enforce it and explicit `inherit`
  otherwise. Initial Hermes settings inherit because implemented ACP cannot
  select them per session.
- The existing backend portability decisions remain valid, but ADR 0006's
  statement that global role cards, global skills, and broker role names are
  shared configuration is superseded if this ADR is accepted.
- The shop remains local and restart-ephemeral; there is no persisted profile
  migration or project-owned configuration.
