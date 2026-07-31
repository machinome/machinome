## 1. Prove profile behavior red

- [x] 1.1 Add `tests/test_runtime_profiles.py` cases for default/explicit selection, strict schema and unknown keys, stable IDs/labels, exact user agent, direct/delegated topology, backend mappings, contained prompt paths, profile-local skills, per-skill `shop-skills/` symlinks, broken/escaping links, and clear validation errors; run `python -m unittest tests.test_runtime_profiles -v` and record the intended failures before implementation.
- [x] 1.2 Extend `tests/test_broker.py` with red cases for profile-declared participants and edges, generic internal `user`, user-agent direction/output routing, rejected undeclared communication, Builder directions/turns carrying no assignment ID, Builder's unavailable assignment operations, direct turn activity, and preserved Fordesmac acknowledgement/completion state.
- [x] 1.3 Extend `tests/test_orchestrator.py` and backend fixtures with red cases that open one Builder or four Fordesmac agents through each backend, pass resolved prompt/skills/model/effort/tools, publish only the configured user-facing agent, isolate Claude sessions from both project-level and user-level assistant configuration, and never read `.codex/agents/<role>.toml` or global runtime role paths.
- [x] 1.4 Extend `tests/test_floor_entrypoint.py`, `tests/test_floor_api.py`, `tests/test_agent_cli.py`, `tests/test_project_preparation.py`, `tests/test_role_contracts.py`, and `tests/test_shop_lifecycle_e2e.py` with red cases for `--profile`, pre-preparation rejection, every profile agent receiving the verified project root, preserved configured-port opening, generic conversation seams, profile ID/labels, both rosters, migrated prompt contracts, and Builder direct steering.

## 2. Load and validate trusted profiles

- [x] 2.1 Add `floor/profiles.py` with immutable profile, agent, topology, and selected-backend runtime dataclasses plus strict Python 3.11 `tomllib` parsing for `profiles/<id>/profile.toml`.
- [x] 2.2 Implement explicit lowercase kebab-case profile selection, primary-checkout resolution, schema-version and unknown-key rejection, unique IDs/labels, exactly one user agent, contained prompt files, name/frontmatter agreement, direct/delegated mode invariants, internally consistent acyclic assign/report edges, and actionable field/path errors without flipping omission behavior to `builder` yet.
- [x] 2.3 Implement prompt skill-list parsing and the complete profile `skills/` allowlist boundary: contained local skill directories or individual symlinks to one direct `shop-skills/<skill>` target, with broken, file, cross-profile, repository-`skills/`, and transitive escape rejection.
- [x] 2.4 Validate required Codex/Claude/Hermes entries and concrete-or-`inherit` model, effort, and tool policies; validate selected-backend enforceability before returning a resolved agent contract.
- [x] 2.5 Wire profile validation before `prepare_project` in both `floor/orchestrator.py` and `floor/__main__.py`; prove an invalid profile with a missing project creates no files, build process, listener, or backend process.

## 3. Package the initial runtime profiles and skills

- [x] 3.1 Create `profiles/builder/profile.toml` and profile-owned `builder.md` with Maker/Builder direct topology, the ratified Claude/Codex/Hermes matrix, backend tool policies, no callback process, and the exact existing-leaf disassembled-first red/green sequence.
- [x] 3.2 Create `profiles/fordesmac/profile.toml` plus profile-owned `foreman.md`, `designer.md`, `machinist.md`, and `librarian.md`; incorporate the runtime pipeline into Foreman's prompt, make Librarian standing and Foreman-controlled, and remove global-path assumptions.
- [x] 3.3 Move authoritative `skills/solid-node-api` and `skills/solid-node` to `shop-skills/`; add individual relative symlinks from each profile's `skills/` allowlist and keep `skills/running-the-shop` in the repository-agent namespace.
- [x] 3.4 Update or remove every tracked reference to the moved skills and runtime prompts according to ownership. Remove obsolete global runtime role cards and `.codex/agents/<runtime-role>.toml` only after no shop-development adapter or documentation depends on them.
- [x] 3.5 Add contract tests proving each prompt names only available profile skills, Fordesmac Foreman names no pipeline skill, no runtime prompt addresses repository `skills/`, and Builder contains neither `solid develop --callback` nor a first-red missing-artifact instruction.

## 4. Generalize broker topology and work state

- [x] 4.1 Replace `ROLE_LABELS` and Foreman/Maker validation branches in `floor/app.py` with the immutable resolved profile, declared agent roster, stable internal `user`, and broker-enforced assign/report edges.
- [x] 4.2 Generalize agent manifest, inbox, delivery subscription, event summaries, acknowledge/report/complete handling, and error messages to profile agent IDs without weakening assignment correlation.
- [x] 4.3 Implement direct mode so Builder becomes active on matching `turn_started`, stays active across steering, and returns to waiting on matching `turn_completed`, without allocating or requiring assignment IDs and with every assignment lifecycle operation rejected.
- [x] 4.4 Preserve delegated mode so only acknowledgement activates specialists and only matching completion clears them; backend turn completion alone must not clear an assignment.
- [x] 4.5 Generalize `floor/agent.py` so callers provide stable sender/recipient IDs and the broker validates their profile edge; retire `floor/foreman.py` and Foreman-only publish/receive behavior after tracked callers are migrated.

## 5. Pass resolved contracts through orchestration and all backends

- [x] 5.1 Generalize `RoleContext`/the portable backend open contract to carry the resolved profile agent, validated prompt and skill paths, labels, selected-backend runtime policy, and active roots without exposing backend-native identifiers above adapters.
- [x] 5.2 Make `ShopOrchestrator` open agents in profile declaration order, build per-agent locks dynamically, route user-agent `role_message` output generically, and unwind/close arbitrary roster sizes in reverse order.
- [x] 5.3 Change `floor/backends/codex.py` to use the resolved prompt/skills and concrete model/effort/tool policy directly in supported app-server fields; remove `.codex/agents/<role>.toml` lookup and verify exact fake-server frames.
- [x] 5.4 Change `floor/backends/claude.py` to use resolved profile prompt/skills and selected model/effort/tools in its command and system contract while preserving safe mode isolation from project/user configuration, first-envelope trust framing, steering, and per-agent process ownership; verify exact fake-CLI arguments and frames.
- [x] 5.5 Change `floor/backends/hermes.py` to bootstrap validated profile prompt/skill paths and explicit inherited runtime settings while preserving ACP session, second-prompt steering, cancellation, timeout, and event semantics; verify exact fake-ACP frames.
- [x] 5.6 Assert in fixtures that Codex receives medium through `thread/start.config.model_reasoning_effort` and Claude receives `--effort medium`; retain the Codex 0.146.0 generated-schema and Claude Code 2.1.220 help probes as implementation evidence.

## 6. Generalize run APIs and browser presentation

- [x] 6.1 Replace hard-coded Maker/Foreman conversation routes and payload author union with generic user input and user-facing-agent output while preserving order, reload restoration, SSE updates, Enter/Ctrl+Enter behavior, and direct steering.
- [x] 6.2 Add stable `profile_id`, `user_label`, user-agent identity/label, and complete declared roster metadata to run-state/API payloads; keep protocol user identity `user` regardless of label.
- [x] 6.3 Update `floor/frontend/src/main.tsx` and styles to render profile ID, roster labels, transcript attribution, event summaries, and accessibility text from run data without adding a profile display label or hard-coding Maker/Foreman.
- [x] 6.4 Rebuild `floor/static/` from frontend source and verify generated assets are the only static changes.

## 7. Complete role and lifecycle acceptance

- [x] 7.1 Run focused profile, broker, CLI, API, orchestrator, role-contract, and backend-fixture suites; confirm both profiles work through Codex, Claude, and Hermes fixtures and all red cases from section 1 are green.
- [x] 7.2 Add/complete browser E2E scenarios using explicit `--profile builder` for Builder roster/profile ID/direct activity/conversation and explicit `--profile fordesmac` for the four-agent roster/profile ID/delegated lifecycle without page reload; preserve the compact independently scrollable, role-title-neutral transcript, newest-message reveal, configured event-log labels, and Enter/Ctrl+Enter behavior.
- [x] 7.3 Run a real Builder smoke project on each available backend: send Maker direction, confirm direct start/steer/complete, inspect the model watcher result, and verify no assignment ceremony or lingering process. Record unavailable external runtimes honestly rather than simulating them.
- [x] 7.4 Run a real Fordesmac smoke project on each available backend: confirm four token-free standing sessions, Foreman conversation, one specialist assignment/report/complete path, Librarian assignment, and bounded shutdown. Record unavailable external runtimes honestly.
- [x] 7.5 After both profile lifecycle and backend fixture suites pass, make omitted `--profile` select `builder` in both entry points and turn the default-profile red cases green.

## 8. Update architecture and operating records

- [x] 8.1 Add proposed ADR 0011 for profile-defined runtime topology, superseding ADR 0006's global role/configuration ownership while preserving its portable backend seam; after implementation evidence agrees, mark it Accepted and update ADR 0006 status and `docs/adrs/README.md`.
- [x] 8.2 Rewrite `docs/architecture-overview.md` after ADR acceptance to describe profile loading, generic broker identity/edges, direct/delegated modes, initial profiles, runtime skill namespace, resolved backend contracts, and the pilot-directed operational model matrix replacing the old stepped-down evaluation defaults, as implemented rather than as a transition note.
- [x] 8.3 Update `AGENTS.md`, `CLAUDE.md`, `README.md`, `skills/running-the-shop/SKILL.md`, Codex/Claude repository-development adapters, and layout/startup examples so user-piloted agents select profiles while shop-development skills remain separate from runtime skills.
- [x] 8.4 Remove or generalize stale Foreman/Maker capability names and tracked docs after synchronizing `shop-user-conversation`; verify no current source claims a fixed three-agent roster or global runtime prompt/skill path.

## 9. Final evidence and archive

- [x] 9.1 Run `python -m unittest discover -s tests -v` and retain the complete result.
- [x] 9.2 Run `npm --prefix floor/frontend run test`, `npm --prefix floor/frontend run build`, and `scripts/test-e2e`; inspect retained Playwright evidence for both profile scenarios.
- [x] 9.3 Run `openspec validate profile-defined-shop-runtime --strict` and review proposal promises, non-goals, delta requirements, and tasks for complete effective coverage.
- [x] 9.4 Promote ADR 0011 only after implementation evidence, then synchronize every modified/new baseline spec as an intentional complete replacement for each listed `MODIFIED` requirement rather than the sync skill's normal partial merge. Remove unlisted superseded fixed-role text and scenarios, including `The working team starts`, `The working team starts with the Hermes backend`, `The retired design role is addressed`, fixed Foreman/Designer/Machinist backend-session ordering, `Role capability comes from the role card`, fixed-role shop-open/backend scenarios, and the obsolete `No selected artifact` browser empty state that cannot occur after fail-closed project preparation. Apply the declared messaging-requirement rename. Synchronize `named-project-bootstrap` and `shop-user-conversation`; delete the retired `openspec/specs/foreman-conversation/` and `openspec/specs/foreman-conversation-bridge/` capability directories rather than leaving purpose-only files. Validate the resulting baselines, archive the OpenSpec change, and create the second cycle commit with test and real-runtime evidence.
