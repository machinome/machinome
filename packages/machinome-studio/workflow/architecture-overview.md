# Shop architecture overview

The solid-node shop is a local agent harness for mechanical CAD projects. A
human pilot owns intent and consequential choices; the runtime opens a
repository-owned, validated team profile for one named project. `AGENTS.md`
governs how this repository is changed. This document describes the running
system.

## Profile-defined runtime

Before project preparation, both floor entry points resolve the primary shop
checkout and load `profiles/<id>/profile.toml`. `--profile builder` is the
default; `--profile fordesmac` selects the delegated team. A profile is strict
trusted configuration: it declares the human label, one user-facing agent,
standing roster, direct or delegated work mode, prompt paths, allowed skills,
communication edges, and Codex, Claude, and Hermes model/effort/tool policy. A
project never supplies or overrides that configuration. OpenCode is the bounded
exception: existing profiles have no OpenCode tables and remain unchanged and
valid; its adapter owns temporary compatibility defaults.

The initial profiles are:

| Profile | Mode | Human-facing agent | Standing roster |
| --- | --- | --- | --- |
| `builder` | direct | Builder | Builder |
| `fordesmac` | delegated | Foreman | Foreman, Designer, Machinist, Librarian |

Runtime prompts live beside their profile. A prompt names only skills exposed
through its profile `skills/` allowlist. Shared runtime skills live under
`shop-skills/`; repository operator and development skills remain under
`skills/`. Each declared agent receives the exact verified project repository
root, while prompts and skills remain shop-owned outside that project.

## Runtime layers

```text
browser  <-->  Broker  <-->  Orchestrator  <-->  selected backend sessions
                   |               |                     |
             state, SSE,      resolved profile    Codex / Claude / Hermes /
             conversation     contracts only            OpenCode
```

`floor/app.py` is the in-memory broker and browser API. It uses stable internal
identity `user`, profile agent IDs, and profile labels. It validates every
sender, recipient, assignment edge, reporting edge, lifecycle operation, and
conversation author against the active profile. Browser run state contains the
stable profile ID, human label, user-facing agent, and full declared roster.
Only output from the selected profile's user-facing agent enters the user
conversation.

Direct profiles have no assignment identity or assignment lifecycle. A direct
user direction is delivered to the user-facing agent; only a matching backend
delivery's `turn_started` and `turn_completed` events change it between waiting
and active. Steering retains that delivery identity, and stale events cannot
activate or clear work.

Delegated profiles retain assignment state. An assignable specialist becomes
active only after acknowledging its matching assignment and becomes waiting
only after matching completion. Backend turn events neither activate nor clear
delegated assignment work.

`floor/orchestrator.py` is deterministic and backend-neutral. It opens profile
agents in declaration order, constructs a required `RoleContext` containing the
validated `ProfileAgent`, labels, shop root, and verified project root, and
closes the arbitrary roster in reverse order. It
uses `deliver_start()` for idle delivery and `deliver_steer()` only for the
currently active delivery. Native session and turn identifiers never enter the
broker.

## Backend seam

The portable `AgentBackend` protocol owns external processes and exposes
`open_role`, `deliver_start`, `deliver_steer`, `interrupt`, `close_role`, and
`close`. It emits portable role-message, turn, and failure events. It has no
generic compatibility delivery operation.

Codex translates a profile's selected model and effort into `thread/start`.
Claude launches one isolated CLI process per profile agent and translates the
selected model, effort, and permitted tools into its supported command fields.
Hermes explicitly inherits model, effort, and tools because ACP does not expose
per-session controls; it still receives the same validated profile prompt and
skills. These three adapters consume the selected profile runtime table and
never parse profile files or load global role adapters.

OpenCode owns one password-protected loopback HTTP/SSE server and one persistent
session per role. Its adapter does not require or read OpenCode profile tables.
It inherits the authenticated operator model, variant, and global configuration
and owns temporary model/variant/tool compatibility defaults. For each role it
uses one shared generated primary agent with a deny-by-default permission policy;
every role delivery carries the exact profile prompt and exact allowlisted skill
instructions as that session's system contract. This is a bounded exception to
profile-explicit runtime policy, not a claim that OpenCode exposes equivalent
controls.

OpenCode native project configuration is disabled. If the exact verified
project-root `AGENTS.md` is a regular non-symlink file, the adapter manually
appends it after explicit subordinate-guidance framing. It does not follow a
symlink or search another location. OpenCode 1.18.11 evidence confirms that
project configuration can be disabled while operator-global authentication and
provider defaults remain available. The server uses `--pure` so external
plugins do not execute. Archived authenticated verification proves exact role
contract composition and one corrected tool turn with native ancestry and one
portable completion on the tested 1.18.11 runtime.

The initial operational matrix is Builder/Foreman/Machinist/Librarian:
Claude `sonnet`, Codex `gpt-5.6-terra`, medium effort; Designer uses Claude
`opus` and Codex `gpt-5.6-sol`, also medium effort. Hermes explicitly inherits
all three controls. OpenCode instead inherits its operator model and variant
under its adapter-owned compatibility policy. These choices are backend
configuration, not broker semantics.

## Floor and browser

After profile validation, preparation creates or verifies the named independent
project repository and validates its initial build. Only then does the floor
bind a listener or the orchestrator start a backend. The browser renders
profile-provided roster labels, conversation attribution, and event summaries;
it does not encode a participant's role. The transcript is independently
scrollable, reveals newly appended messages, sends a non-empty draft on Enter,
and inserts a newline on Ctrl+Enter.

Floor serves only completed `_build/` artifacts. Its own watcher rebuilds
changed project source and publishes model-change events; agent sessions do not
run a callback process or expose project source through the browser service.

## Workspace boundaries

Each `projects/<name>/` directory is an independent Git repository. The
framework checkout belongs under `solid-node/`; framework worktrees belong
under `solid-node/WTs/`; shop worktrees belong under `WTs/`. Runtime agents use
only the active project's verified root plus their selected profile contract.
They do not inspect sibling mechanical projects.
