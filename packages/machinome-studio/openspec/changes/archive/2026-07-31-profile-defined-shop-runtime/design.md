## Context

The runtime currently derives its complete team from `floor.app.ROLE_LABELS`, and the orchestrator imports that constant to open three sessions. Broker validation names `maker` and `foreman`; conversation routes name both participants; backend event filters publish only Foreman output. Each backend then reconstructs a role contract differently: Codex reads `.codex/agents/<role>.toml`, Hermes points at `agents/<role>.md` and `skills/`, and Claude parses model/tools from that Markdown card. This has already allowed `model: sonnet` to affect Claude while Codex silently selected an unrelated model and Hermes inherited its process model.

The profile boundary must remain above ADR 0006's `AgentBackend` seam. Profiles describe portable participants and authority plus explicit backend runtime knobs; they do not expose vendor session identifiers to the broker. The selected profile is trusted shop configuration, not project data. A mechanical project must not be able to redefine agent authority or expand runtime skills.

The first two profile packages are:

- `builder`: Builder is the sole standing and user-facing agent and performs direct project work.
- `fordesmac`: Foreman is user-facing and assigns standing Designer, Machinist, and Librarian agents, which report only to Foreman.

Profiles and backends are orthogonal: each profile must open through Codex, Claude, or Hermes. Profile validation precedes the existing fail-closed project preparation so an invalid configuration cannot scaffold, build, or modify a project.

## Goals / Non-Goals

**Goals:**

- Add, remove, or rearrange runtime agents through a declarative profile package without profile-specific Python.
- Make the broker generic over stable user identity, the configured user-facing agent, declared agents, and broker-enforced assignment/report edges.
- Make `builder` the default and preserve the existing delegated pipeline as `fordesmac`, adding Librarian as a regular standing specialist.
- Keep runtime prompts and skills separate from the skills and adapters used by agents developing the shop repository.
- Make every selected backend/model/effort/tool choice explicit or explicitly inherited.
- Reject incomplete, escaping, ambiguous, or unsupported profiles before any side effect.
- Preserve the current backend ownership, steering, shutdown, project isolation, and shop-owned model watcher contracts.

**Non-Goals:**

- Project-local, external-path, downloaded, or user-home profile discovery.
- Run-level overrides for the human label, profile topology, models, tools, prompts, or skills.
- Optional, ephemeral, or dynamically spawned profile agents. Every declared agent is standing.
- Multiple user-facing agents or direct user controls for specialists.
- A portable universal tool vocabulary where a backend cannot enforce one.
- Per-session Hermes model/tool selection before ACP exposes such controls; `inherit` is explicit in the initial profiles.
- Persisting a selected profile across runs or in a mechanical project.
- Preserving hard-coded Maker/Foreman HTTP endpoint names as public compatibility aliases; the shop is private and experimental.

## Decisions

### D1 — A profile is a trusted, self-contained directory selected by stable ID

A run accepts `--profile <id>`, defaulting to `builder`, and resolves only `<primary-shop-root>/profiles/<id>/profile.toml`. IDs are lowercase kebab-case and path resolution may not escape `profiles/`. The broker-only entry point accepts the same option so browser and lifecycle testing runs against the same profile contract.

The profile owns `profile.toml`, every standing agent prompt, and a `skills/` allowlist. There is no profile search path and no project-local override.

*Why:* run-level selection lets one project be exercised through different teams without storing harness policy in the project. Repository ownership makes authority reviewable and prevents project content from expanding agent powers.

*Alternative considered:* infer a profile from project files or accept `--profile /path`. Rejected because an ordinary mechanical repository would then control the identities, prompts, tools, and authority of processes the shop launches.

### D2 — `profile.toml` is strict topology and runtime data

The schema is versioned and rejects unknown keys. Its conceptual shape is:

```toml
schema_version = 1
user_label = "Maker"
user_agent = "builder"
work_mode = "direct" # or "delegated"

[[agents]]
id = "builder"
label = "Builder"
prompt = "builder.md"
assigns = []
# reports_to is omitted for a root agent

[agents.backends.codex]
model = "gpt-5.6-terra"
effort = "medium"
tools = "inherit"

[agents.backends.claude]
model = "sonnet"
effort = "medium"
tools = ["Bash", "Read", "Write", "Edit", "Glob", "Grep"]

[agents.backends.hermes]
model = "inherit"
effort = "inherit"
tools = "inherit"
```

Agent IDs and labels are unique; prompt paths are relative regular files contained in the profile; exactly one declared ID equals `user_agent`. `assigns` references declared agents. A specialist's `reports_to` references exactly one declared assigner, and the assignment/report graph is acyclic and internally consistent. `direct` mode requires one agent and no assignment/report edges. `delegated` mode requires every non-root agent to have one reporting parent.

Backend entries are required for Codex, Claude, and Hermes. A setting is concrete or the literal `inherit`; effort is accepted only where the backend supports the chosen value, and a concrete tool list is accepted only where the backend can enforce it. Unknown or unavailable selected-backend values are errors, not warnings.

*Why structured TOML rather than `claude:sonnet[medium], codex:...` in frontmatter:* the loader can validate backend completeness, supported effort, list-valued tool policy, and duplicate keys without inventing a string grammar. Prompt Markdown remains behavioral authority rather than provider configuration.

### D3 — Profile resolution is a pre-preparation fail-closed gate

The launcher loads and validates the complete selected profile before calling `prepare_project`, binding a listener, or starting a backend. Validation includes schema, IDs, paths, prompt frontmatter, topology, all three backend declarations, and selected-backend compatibility.

Prompt frontmatter declares `name`, `description`, and `skills`. `name` must equal the TOML agent ID. Every skill name must resolve through `profiles/<id>/skills/<name>/SKILL.md`.

A profile-local skill is a contained ordinary directory. A shared skill entry is an individual symlink whose resolved target is one directory directly beneath `shop-skills/`. Broken links, links to files, links into repository `skills/`, links to another profile, and transitive escapes fail validation. A prompt cannot load an undeclared skill by addressing another repository path; the backend bootstrap names only validated profile paths.

*Why before project preparation:* profile errors are operator configuration errors and must not create a project repository or run its build as a side effect.

### D4 — The broker owns a resolved profile, not global role constants

A validated immutable `RuntimeProfile` is passed to broker, app, and orchestrator composition. The broker validates all participants and relationships against it:

- Internal human participant ID is always `user`; `user_label` is presentation and prompt context.
- User conversation input always becomes `direction` to `user_agent`.
- Only the declared user-facing agent's backend output enters the user conversation.
- An `assignment` is accepted only when its sender's `assigns` includes the recipient.
- A `report` is accepted only from an agent whose `reports_to` equals the recipient.
- Undeclared agents and undeclared edges are rejected.

The HTTP and browser representations expose `profile_id`, `user_label`, user-agent ID/label, and the declared roster. Conversation routes become participant-neutral. Agent CLI commands continue to carry stable agent IDs but no longer synthesize Foreman as sender/recipient; their caller supplies an edge the broker validates. The Foreman-only publish CLI is retired because backend `role_message` capture is the one output path for whichever agent is user-facing.

*Alternative considered:* leave broker rules permissive and rely on prompts. Rejected because prompts cannot enforce authority, and malformed or compromised agent output must not bypass the declared topology.

### D5 — Direct and delegated work are two declarative profile modes

In `direct` mode, a user direction starts or steers the user-facing agent. `turn_started` marks that agent active and `turn_completed` returns it to waiting. Assignment lifecycle operations are invalid because the profile has no assignment edges. Builder communicates through ordinary backend output; it does not call report or complete against itself.

In `delegated` mode, current assignment semantics remain: a specialist becomes active after acknowledging assigned work and returns to waiting after matching completion. Backend turns do not replace that acknowledged-work state. The user-facing Foreman remains available for user direction and specialist reports while specialists work.

*Why explicit mode rather than topology inference:* it makes the state contract reviewable and prevents a later topology edit from silently changing how the roster interprets backend turns.

### D6 — Backends receive resolved agent contracts

`AgentBackend.open_role()` is generalized to receive a portable resolved agent definition in its context: stable ID, prompt path, validated skill paths, selected backend model/effort/tool policy, user and profile labels, and the active project/shop roots. The orchestrator still knows no native session or turn identifiers.

- Codex passes the selected model, `config.model_reasoning_effort`, and composed profile-contract instructions to `thread/start`; it no longer opens `.codex/agents/<role>.toml`. Codex 0.146.0's generated `ThreadStartParams` schema accepts per-thread `config`, and `model_reasoning_effort` is the repository's recognized Codex configuration key.
- Claude passes the selected model, `--effort`, and concrete tool list (or intentionally inherits) and names validated profile prompt/skill paths in its system contract. Claude Code 2.1.220 exposes `--effort` with `medium` among its accepted values.
- Hermes names the same validated paths in its bootstrap prompt. Initial profiles explicitly inherit model, effort, and tools because implemented ACP `session/new` exposes none of them.

Backends do not parse profile files independently. One loader and one resolved definition prevent divergent interpretation.

The initial model matrix is:

| Agent | Claude | Codex | Hermes |
|---|---|---|---|
| Builder | `sonnet`, medium | `gpt-5.6-terra`, medium | inherit |
| Foreman | `sonnet`, medium | `gpt-5.6-terra`, medium | inherit |
| Designer | `opus`, medium | `gpt-5.6-sol`, medium | inherit |
| Machinist | `sonnet`, medium | `gpt-5.6-terra`, medium | inherit |
| Librarian | `sonnet`, medium | `gpt-5.6-terra`, medium | inherit |

The pilot explicitly selected this initial matrix during proposal shaping on
2026-07-31. These are operational profile values, not behavioral requirements:
the profile schema and fail-closed enforcement are ratified, while later knob
changes may update profile data without changing the behavioral specs. The
selection intentionally replaces the stepped-down evaluation defaults recorded
for the old global adapters and prevents a backend from silently choosing an
unrelated model.

Claude tool lists migrate from the current prompts, with Builder receiving its engineering set. Codex and Hermes initially declare `tools = "inherit"` unless implementation evidence proves a concrete supported allowlist. No backend may silently substitute another configured model for a concrete declaration.

### D7 — Runtime prompts and skills are separate from repository-agent configuration

Authoritative runtime prompts move into their profile directories. `agents/*.md` and `.codex/agents/<runtime-role>.toml` cease to be runtime lookup locations and are removed once no repository-development surface depends on them.

`solid-node-api` and `solid-node` move to `shop-skills/`. Each profile exposes each shared skill with a separate relative symlink in its own `skills/` directory. The repository-level `skills/` remains the namespace for agents developing, operating, or changing the shop. `skills/running-the-shop` stays there; it is not exposed to runtime agents. The complete delegated pipeline procedure is incorporated into `profiles/fordesmac/foreman.md` so Foreman does not spend a tool call loading its own basic role.

*Why not duplicate skills:* two authoritative copies drift. *Why not symlink all of `shop-skills/`:* adding a shared skill would silently expand every profile's available capabilities.

### D8 — Builder is promoted from the spike but follows current architecture

Builder owns the whole reversible mechanical loop and uses the shared API and machining skills. It does not delegate, use the Designer/Machinist drawing handoff, or create OpenSpec changes during product work. It does not run `solid develop --callback`; ADR 0010's watcher owns refresh.

For each new leaf, Builder first creates and wires the leaf in a deliberately disassembled position. The first red fit/assembly test is then written against that existing leaf and must fail because its current relationship is wrong, never because a class, node, function, or artifact is absent. Builder then assembles or refines the leaf until the test turns green. There is no mandatory visual-inspection tool call between creating the disassembled leaf and adding the test; visual and regression evidence remain completion requirements.

### D9 — `fordesmac` preserves the delegated pipeline and regularizes Librarian

The existing Foreman, Designer, and Machinist contracts move into the profile and are path/lifecycle updated. Foreman's prompt absorbs the full runtime pipeline discipline formerly shared through `running-the-shop`. Librarian becomes a fourth standing, token-free session, is assigned only by Foreman, and reports only to Foreman. No optional or dynamic agent concept is introduced.

### D10 — Profile identity and participant labels are data, not new branding

The run payload and browser expose the stable profile ID for verification. There is no separate profile display label. Agent labels and `user_label` render the roster, transcript attribution, event summaries, and accessibility text. API identities remain `user` and stable agent IDs.

## Risks / Trade-offs

- **Strict validation makes profile evolution deliberate and may reject harmless unknown metadata.** → Version the schema and fail on unknown keys so authority typos cannot degrade silently; evolve the version intentionally.
- **Symlink behavior differs on some packaging or Windows setups.** → This repository currently targets its checked-out filesystem; tests exercise real relative links and errors explain the required target. A future packaged-profile mechanism can replace links without weakening the allowlist contract.
- **Moving skills can break repository instructions that still name `skills/solid-node*`.** → Search all tracked references, update runtime and operator documentation by ownership, and test that repository agents no longer rely on the moved paths accidentally.
- **Direct and delegated activity use different state sources.** → Keep the mode explicit, cover both state machines independently, and avoid blending backend-turn completion with delegated assignment completion.
- **Claude, Codex, and Hermes cannot enforce identical runtime controls.** → Require explicit concrete or `inherit` values and test the exact command/protocol frames each backend emits; never claim inherited tools are restricted by the profile.
- **Removing legacy endpoints and adapters breaks scripts outside the repository.** → The shop is private and experimental; update every tracked caller atomically and report the breaking seam in the proposal and ADR.
- **Promoting the stale Builder spike could restore superseded callback behavior.** → Treat current main and ADR 0010 as authority; port only the role discipline and explicitly test that no profile prompt names `solid develop --callback`.

## Migration Plan

1. Add profile model/loader and fail-closed tests without changing the active runtime.
2. Add both complete profile packages, move the two runtime skills to `shop-skills/`, and update tracked references and symlinks.
3. Generalize broker, APIs, orchestration context, backends, and frontend behind the resolved profile.
4. Make `builder` the CLI default only after both profiles pass lifecycle and backend fixture tests.
5. Remove global runtime prompt/adapters and Foreman/Maker-specific routes after all tracked callers use generic seams.
6. Run both profiles through all fake backend fixtures, frontend checks, browser E2E, and at least one real direct Builder smoke run plus one real delegated `fordesmac` smoke run.
7. Accept ADR 0011, rewrite the architecture overview to the implemented state, synchronize baseline specs, and archive the OpenSpec change.

Rollback before integration is branch removal. After integration, rollback requires reverting the complete implementation commit because profile paths, skill ownership, broker contracts, and defaults change atomically; a partial rollback would leave prompts or skills unresolved.

## Open Questions

None blocking. Implementation fixtures must assert the exact Codex
`thread/start.config.model_reasoning_effort` value and Claude `--effort`
argument so later runtime changes cannot silently drop an explicit profile
setting.
