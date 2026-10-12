## 1. Qualify and pin the runtime contract

- [x] 1.1 Read the installed 0.157.1 experimental schema, bundled supported-model metadata and effective-configuration endpoints; retain reviewed tool-affecting fixtures and validate their shapes without credentials.
- [x] 1.2 Write failing qualification cases for unsupported version/schema/model/effort, changed executable/catalog/config, extra advertised tools, forced native/undeclared calls, config-layer conflicts and bounded probe timeout; establish failures before implementing selectability.
- [x] 1.3 Implement credential-free real-binary qualification using private synthetic state and a local model fixture, checking actual per-role dynamic schemas/namespace registries, empty-role registry, subsequent turns, model changes and guarded restart/resume. Cache only unchanged executable/config/catalogue/tool-schema fingerprints within one Studio process.
- [x] 1.4 Implement effective-policy checks before real thread creation, deny conflicting managed settings without overriding restrictions, and verify no startup side effect launches inherited MCP/plugins/hooks. Record the limits of practical production attestation.
- [x] 1.5 Implement and verify the pilot-approved dedicated Studio login command, durable native auth store and exclusive process/login lease using the same stable XDG-state path resolver in provisioning and runtime; test absent/invalid/revoked login remedies, refresh persistence and zero normal-CLI credential access.

## 2. Shared authentication service checkpoint

- [x] 2.1 Add failing two-project and two-hub fixtures, then implement the injected hub-owned shared app-server manager, project adapter references, serialized lifecycle, exclusive auth lease, generation-aware thread/handle routing (including overlapping pristine handles), role-specific event queues, pre-preparation lease acquisition and cancellation cleanup before a Session exists.
- [x] 2.2 Prove closing/failed opening of one project preserves another project's delivery/tool work; last-reference and hub shutdown release the service exactly once; shared crash fans out role failures only to attached Codex roles while unrelated backends remain alive and stale callbacks reach none.
- [x] 2.3 Prove native thread records remain ephemeral while dedicated auth survives shutdown; verify orphan cleanup never reads/deletes unrelated auth or native state. Obtain adversarial review of this first checkpoint before selectable adapter/UI work.

## 3. Restore project selection and catalogue behavior

- [x] 3.1 Add red-first parser/profile/runtime regression cases for explicit Codex grammar, supported reasoning/model combinations, unchanged Claude defaults, omitted effort, mixed backends and error attribution before preparation.
- [x] 3.2 Add Codex factory/preflight wiring and explicit-only project selection, retaining Claude-only profiles and existing provider/idle/pristine gates.
- [x] 3.3 Expose qualified fixed-OpenAI runtime choices and structured per-backend unavailable reasons retained alongside other available choices through fresh/used catalogues; preserve revision-checked runtime publication and rollback behavior with tests.

## 4. Implement private app-server roles and dynamic floor tools

- [x] 4.1 Write failing fake app-server/MCP fixtures for role contracts and skill announcements, exact dynamic registration, unknown namespace/tool, bad schema, cross-thread/turn, stale callback, spoofed sender/role and duplicate request rejection before any operation.
- [x] 4.2 Implement owned private config/cwd/environment and the dedicated native authentication policy, with secret-redaction/cleanup tests and explicit unsupported-mode remedies; never bypass sandbox/approval checks.
- [x] 4.3 Implement persistent role creation with reviewed dynamic tools, read-only/deny settings and empty execution environments at creation and EVERY new turn, including after recovery/resume. Revalidate immutable registry metadata on resume.
- [x] 4.4 Bridge calls asynchronously to one owned MCP subprocess per role using the existing floor tool descriptions/schemas/operations and exact role skill registry. Validate live thread/turn/delivery/session/name/schema and lifecycle identity before dispatch, keeping the app-server reader responsive.
- [x] 4.5 Implement bounded text/structured/error/image result conversion against the installed schema; prove model-visible image bytes, unchanged project snapshot cleanliness and explicit unsupported-content failures.

## 5. Delivery, activity, recovery and teardown

- [x] 5.1 Add red-first cases and implement idle start, active steering, steer-only notices and completion races with portable delivery identity; notices never create replacement sessions or new turns.
- [x] 5.2 Normalize actual completed nonempty role messages, running/terminal tool activity, useful floor path/diff and native token usage; test tool-only/empty turns, duplicate/late events, errors and unexpected native execution/reroute/approval requests.
- [x] 5.3 Implement supported idle model/effort updates on the retained thread and safe adapter-local restart/resume; test first/subsequent guarded turns, retained registry, auth failure/re-login handling in the authoritative store and existing next-envelope recovery without replay or endless retry.
- [x] 5.4 Add a blocked tool worker with a descendant that would mutate after close; prove failure red, then implement bounded callback shutdown and process-group TERM/KILL/reap, partial-open cleanup and idempotent cancellation-safe/retryable close with no post-close mutation and no premature lease release.
- [x] 5.5 Exercise delegated Foreman/Machinist acknowledge/report/complete through trusted identities, independent concurrent roles and mixed backend ownership/failure regression fixtures.

## 6. Browser, live validation and durable record

- [x] 6.1 Add focused browser tests and implement Codex/OpenAI/model/reasoning choice rendering and unavailable reasons, retaining existing pristine/idle gates, persistence defaults and one session stream.
- [x] 6.2 Run Studio Python, frontend test/build and relevant browser E2E checks; inspect browser pixels for selection, activity, image-related tool output and role failure presentation.
- [x] 6.3 Run deterministic actual-binary qualification against the final adapter policy and role schemas; retain compact credential-free evidence for all tested rejection/registry/restart cases.
- [x] 6.4 After second-checkpoint adversarial review, run authenticated concurrent synthetic-project validation for direct Builder, delegated Foreman/Machinist lifecycle, real floor image result, active steering, tool error, idle Sol/Astra switch, restart/resume and teardown. Record exact versions, tested content, auth limitations and failures without tokens/raw requests.
- [x] 6.5 Under the pilot's ratification record, promote ADR 0032, supersede ADR 0025 and update relevant ADR indexes/amendments, architecture overview, README and operating contract for the actual verified support matrix without portability/publication claims.
- [x] 6.6 Validate the completed change, sync its three spec deltas, archive only when every task and required evidence is complete, and create the focused implementation commit. Leave integration, pushing, publication and worktree cleanup for the pilot's separately directed workflow.
