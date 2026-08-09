# ADR 0012: Use a bounded adapter-owned OpenCode compatibility policy

**Status:** Accepted (amended by ADR 0017)

**Date:** 2026-08-01

**Amends:** ADR 0006 backend mapping and ADR 0011 profile-explicit runtime policy

**Origin:** OpenSpec change `add-opencode-backend`

## Context

ADRs 0006 and 0011 establish a portable backend seam and require each profile
agent to declare backend model, effort, and tool policy. OpenCode is a useful
fourth transport because it provides a persistent headless HTTP server,
sessions, asynchronous prompts, abort, deletion, and SSE events. OpenCode
1.18.11 does not, however, expose an integration surface equivalent to the
existing profile mappings.

The 2026-08-01 isolation probe launched `opencode serve --pure` on authenticated
loopback with generated configuration and
`OPENCODE_DISABLE_PROJECT_CONFIG=true`. Version 1.18.11 became healthy, exposed
authenticated provider defaults, and created a persistent session rooted at the
test project. The observed defaults were `openai/gpt-5.6-terra-fast` and
`opencode/big-pickle`; these identify that operator environment and are not shop
defaults.

The same probe showed that `OPENCODE_CONFIG` and `OPENCODE_CONFIG_DIR`
supplement, rather than replace, user-global configuration. Isolating the
configuration home would also hide the operator-managed authentication and
defaults the adapter needs. Project configuration can be disabled separately.
The probe did not establish generated prompt composition, permission behavior,
SSE correlation, or exactly-once steering; those remain acceptance gates.

## Decision

The shop SHALL add OpenCode as a selectable backend through one shop-owned,
password-protected loopback HTTP/SSE server and one persistent session per
profile role. Existing profiles SHALL remain unchanged and valid; they SHALL
not require OpenCode tables.

For now, the OpenCode adapter SHALL own a compatibility policy:

- inherit the authenticated operator model, variant, and configuration;
- run in `--pure` mode so external plugins do not execute;
- own temporary model/variant/tool compatibility defaults;
- generate one shared primary OpenCode agent with deny-by-default permissions;
- carry each role's exact profile prompt and exact profile-allowlisted skill
  instructions in every delivery's system contract; and
- admit only the tool classes needed by shop roles rather than reading
  permissions from profile manifests.

The server SHALL disable native project configuration. The adapter SHALL
manually append the exact active-project root `AGENTS.md` only when it is a
regular non-symlink file, after explicit framing that makes it subordinate to
the profile role and shop authority. It SHALL not search parents, siblings, the
shop checkout, or the user home for project guidance. Operator-global OpenCode
configuration remains inherited for authentication and provider defaults, but
external plugins SHALL not execute. Effective non-secret configuration SHALL be
recorded in real-runtime evidence.

This is a temporary, bounded exception to ADR 0011's profile-explicit runtime
policy. It is not a claim that OpenCode exposes equivalent model, variant,
effort, tool, permission, or isolation controls. A later change may replace the
exception with profile-declared controls only when their semantics and
enforcement have been measured and designed explicitly.

## Consequences

- ADR 0006's portable protocol remains unchanged; OpenCode-native identifiers
  and transport details stay below the backend seam.
- ADR 0011 continues to govern profile topology, prompts, skill allowlists, and
  Codex, Claude, and Hermes runtime tables. OpenCode alone uses the bounded
  adapter-owned exception.
- Builder and Fordesmac remain valid without manifest edits.
- OpenCode behavior can vary with authenticated operator model, variant, and
  global configuration even though external plugins are disabled. Documentation
  and evidence must state that boundary rather than promising isolation or
  cross-backend equivalence.
- Native project OpenCode customization remains disabled, while one exact root
  `AGENTS.md` can be included under explicit subordinate framing.
- Fake-server acceptance coverage and authenticated real-runtime evidence are
  retained in the archived change, including native message-ID and steering
  findings discovered only against OpenCode 1.18.11.
