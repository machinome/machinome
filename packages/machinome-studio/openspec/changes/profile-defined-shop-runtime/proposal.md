## Why

The shop runtime hard-codes one Foreman/Designer/Machinist topology, routes the human conversation through role names such as `maker` and `foreman`, and loads role prompts and skills from the same global directories used by agents developing the shop itself. That prevents the pilot from selecting a simpler one-agent build loop, makes adding a team require Python changes, and lets backend-specific model handling silently change an agent's runtime.

## What Changes

- Add declarative runtime profiles under `profiles/<profile-id>/profile.toml`. A run selects one with `--profile`; omitting the flag selects `builder`.
- Ship `builder` and `fordesmac` profiles. `builder` has one user-facing Builder that receives direction and builds directly. `fordesmac` has standing Foreman, Designer, Machinist, and Librarian agents; Foreman is user-facing and is the only agent allowed to assign the three specialists, which report only to Foreman.
- Make the broker profile-driven: stable agent IDs, display labels, the one user-facing agent, the human label, assignment edges, and reporting edges come from the validated profile instead of role-name conditionals. The protocol uses stable human identity `user`; `Maker` is profile presentation.
- Add a direct-work lifecycle for Builder. User direction starts or steers Builder's backend turn, and turn state controls its waiting/active state without self-assignment, assignment IDs, acknowledgement, reports, or completion commands. The delegated assignment lifecycle remains for `fordesmac`.
- Make profile directories own their authoritative agent prompts. Agent prompt frontmatter declares the subset of skills available through that profile's `skills/` allowlist.
- Separate runtime engineering skills from repository-agent skills. Move `solid-node-api` and `solid-node` to `shop-skills/`; profiles expose shared runtime skills with individual symlinks. Keep `skills/running-the-shop` as the user-piloted operator skill, and place the complete `fordesmac` pipeline contract in Foreman's prompt.
- Make profiles and backends orthogonal. `profile.toml` explicitly selects each agent's model, effort, and tool policy per Codex and Claude, and explicitly inherits Hermes process configuration until ACP supports per-session selection. Backends load the resolved profile prompt and skills rather than global role adapters.
- Preserve Builder's disassembled-leaf-first TDD: create and wire an existing leaf in a deliberately disassembled position, write the first red fit/assembly test against that existing leaf, then assemble it and turn the test green. The first red state must not be a missing class, node, function, or artifact.
- Validate profiles, paths, skill links, topology, prompt metadata, and selected-backend settings before project preparation or any other side effect.
- Expose the active stable profile ID and profile-provided participant labels through run state and the browser.
- **BREAKING:** the default runtime topology changes from Foreman/Designer/Machinist to Builder; the hard-coded `/conversation/maker` and `/foreman/publish` seams, global `agents/*.md` runtime lookup, `.codex/agents/<role>.toml` runtime adapters, and global runtime-skill lookup are replaced by profile-neutral equivalents.

## Capabilities

### New Capabilities

- `shop-runtime-profile`: selection, loading, fail-closed validation, skill isolation, topology, and backend runtime configuration for declarative profiles.
- `shop-user-conversation`: an ordered conversation between stable internal user identity `user` and the profile's one declared user-facing agent.

### Modified Capabilities

- `shop-agent-lifecycle`: manifest the selected profile's declared standing agents and derive direct-agent activity from backend turns while preserving delegated assignment state.
- `shop-agent-messaging`: enforce profile-declared assignment/report relationships and route user direction and agent output through the declared user-facing agent.
- `shop-agent-backend`: open arbitrary profile-defined agents with resolved prompt, skill, model, effort, and tool configuration without global role-name adapters.
- `shop-floor-lifecycle`: select and validate a profile before project preparation, then open and close exactly its declared agent sessions on any supported backend.
- `named-project-bootstrap`: give every standing agent declared by the selected profile the same verified mechanical-project repository root.
- `shop-browser-workspace`: show the active profile ID and profile-provided participant labels without hard-coded Maker or Foreman presentation.
- `foreman-pipeline-coordination`: scope the delegated pipeline to the `fordesmac` profile and include Librarian as a standing Foreman-assigned specialist.
- `foreman-conversation`: retire the hard-coded Maker/Foreman conversation requirements in favor of `shop-user-conversation`.
- `foreman-conversation-bridge`: retire Foreman-specific receive/publish operations in favor of profile-neutral user-facing-agent delivery and backend output capture.

## Impact

- New profile loading and schema code under `floor/`; profile packages under `profiles/`; shared runtime skills under `shop-skills/`.
- Broker, orchestrator, backend protocol/context, Codex, Hermes, Claude, CLIs, HTTP routes, run-state payloads, frontend source, and built static assets change.
- Existing role cards move into profile packages and are revised for their profile lifecycle. The Builder role is promoted from the earlier spike but updated for the shop-owned model watcher and the ratified first-red rule.
- Tests and fake backends must cover both profiles across all three backends, direct and delegated lifecycle, strict pre-side-effect rejection, filesystem containment and skill symlinks, model/tool mappings, generic conversation routing, and frontend profile/label rendering.
- ADR 0011 will supersede ADR 0006's global role-card/configuration ownership while preserving its backend-neutral orchestration seam. The architecture overview, ADR index, operating contract, README, operator skill, and baseline OpenSpec specs require synchronization.
- No new third-party runtime dependency is required; Python 3.11 provides TOML parsing.
