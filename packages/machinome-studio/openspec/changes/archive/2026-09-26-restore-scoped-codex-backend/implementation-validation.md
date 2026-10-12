# Implementation validation

## Checkpoint one: private native owner and qualification

Checkpoint-one implementation was uncommitted and not selectable. Claude-only construction
does not require HOME, Codex credentials, qualification, or a native process.

Red-first evidence: auth, policy and service tests initially failed importing the
not-yet-implemented modules. The coordinator's failed-delete, malformed-frame and
all-project-delete-failure regressions failed before their lifecycle corrections.
`test_recovery_discards_and_tags_previous_generation_events` explicitly failed on
the retained old queue before the generation-tagging/queue-draining correction.
The shared-owner contract mismatch regression verifies that a second borrower
cannot overwrite the active owner's qualified artifact/policy contract.

Passing command from this worktree:

```sh
/home/asa/devel/machinome/.venv/bin/python -m unittest tests.test_codex_auth tests.test_codex_policy tests.test_codex_service tests.test_codex_preflight tests.test_codex_adversarial tests.test_codex_qualification
```

Result: 32 tests passed. The preflight tests additionally passed together with
the 14 existing `tests.test_project_open` cases (17 total).

Credential-free negative coverage includes changed binary bytes, changed native
effective policy, changed role schemas, schema contract/type drift, bundled model
metadata drift, unadvertised namespaces and native skill instructions, failed
qualification caching, and bounded probe timeout. Production has no fixture
provider switch; synthetic HTTP fixtures live only inside the qualifier's private
credential-free temporary environment.

Actual pinned Linux Codex 0.157.1 measurements establish that effective config
contains exact sessionFlags, empty user/system layers, and the native-derived
allowedLoginMethods=[chatgpt] restriction. Any other managed restriction is refused.
Typed config/read omits experimental tools fields, so flag echo is not treated as
semantic proof: actual outbound model requests must contain only the exact dynamic
registry and no native skill instructions. Native skill discovery controls were
necessary; the historical no-env spike alone still announced bundled skills.

The final coordinator rerun passed 196 real-binary cases over all five shipped role
registries plus an empty registry, without authentication or external model calls.
Binary SHA256: 3e2584f3f3829a43a0495011a1cecb2facbe64a2403e2b682351fd9c2983f970.
Final checkpoint-two contract: 5a61647fe805a3f8111e14f5f75c5da82ef6a5375163915f630495750c912886.
Final fingerprint: 411855633e23bbfade6e4ba052906dca330b71cb9ceca5231ff036f4543b4748.
This rerun also measures completed-turn steering rejection with exact thread/read
state, and confirms deletion removes both native group inventory and rollout files.

Native ephemeral-state cleanup uses a Studio-owned idempotent project/create
group with roots=[] and exact metadata; thread/start records projectId atomically.
Actual thread/list reports sourceKind=vscode. Cleanup validates exact projectId,
pagination and archived inventories, never deletes unmarked threads or auth.
Persisted session_meta uses dynamic_tools (snake case), with function entries whose
schema is inputSchema. Pristine native threads lack rollout files until first turn;
recovery recreates only never-used handles and resumes verified used records.

The coordinator independently demonstrated the actual native app-server retains
the inherited lease descriptor after the wrapper releases its copy. Automated
coverage requires the second owner to remain blocked until the child exits.
All owner teardown remains shielded against caller cancellation; delete failures
retain orphan cleanup responsibility while releasing stopped project resources.

Dedicated native device login completed successfully under coordinator/pilot
control. Ordinary Codex credentials were not read, copied, or modified. This is
was not itself proof of final adapter refresh/revocation behavior. Those checks
were completed at checkpoint two below. No real mechanical project roles were launched.

## Checkpoint two: adapter, workers and portable integration

The coordinator conditionally approved code review before the authenticated
synthetic validation recorded below. Explicit Codex parsing and selection now coexist with
unchanged Claude defaults. Dynamic callbacks enforce exact immutable owning
session/role/handle/generation/turn/schema, lifecycle sender identity and callId
deduplication. Workers expose only the declared floor tools, return text/images,
and terminate their owned process group before temporary cleanup.

Focused discovery before the final reader/signing regressions passed 69 tests:
`python -m unittest discover -s tests -p 'test_codex*.py' -q` using the workspace
Python above. Coordinator full discovery subsequently passed 415 tests, one skip:
the workspace CLI acceptance fixture requires an unavailable development framework
installation. Existing ResourceWarning/loop-closed subprocess warnings remain.
Coordinator npm tests/build and focused Agents browser checks passed.
Final focused Codex discovery after the native bookkeeping correction passed
75 tests in 5.606s. `openspec validate restore-scoped-codex-backend --strict`
passed; `openspec validate --specs --strict` passed all 25 baseline capabilities,
and `git diff --check` passed after synchronization/documentation updates.

Red/green regressions include native namespace/sender/duplicate publication,
retained-history replacement refusal, mixed-backend delivery survival, old-handle
and same-handle queued failures, interrupted blocked callbacks, sibling recovery
quiescence, and large real-worker image results. Portable events now carry a pure
synchronous liveness predicate checked both before handling and after delivery
locks, including failures emitted while pristine and already yielded before
recovery. No native identifiers escape the adapter seam.

The narrow Agents workspace initially clipped the controls/remedy at 760px; a
scoped <=900px active-Agents layout change made the bounding-box regression green.
Reviewed deterministic screenshots show Codex/OpenAI/model selection, unavailable
remedy, locked used selection, image-result activity and retained-context failure.
These are browser fixture evidence, not authenticated model evidence.

Real worker Git identity tests first failed when identity existed only in a
synthetic operator-global config, then passed with explicitly resolved plain
author/committer values and no copied global config. Required signing is refused,
not silently downgraded. An additional red regression proved openspec_setup could
attempt initialization before signing refusal; a shared guard now rejects before
initializing/staging, while an already-existing record remains a harmless no-op.

A malformed token notification while an actual pending callback was blocked
previously emitted failure before stopping its worker. Temporarily removing only
the cleanup await reproduced RED (worker.close awaited zero times); restoring it
made GREEN and proves callback cancellation/join before the failed event. The
final targeted Git/backend command passed 12 tests after both corrections.

Owned-group descendant cleanup is measured, including SIGTERM-ignoring children
and cancelled close awaiters; arbitrary executable code deliberately escaping the
group through daemonization/setsid is not OS-contained by this implementation.
Executor identity/OS containment remains deferred.

The new safe `docs/spikes/codex-tool-isolation/studio_live.py` diagnostic is bounded
and temporary-project-only. It uses the production dedicated auth owner and actual
adapter/workers; its lifecycle HTTP peer is explicitly a synthetic fixture. It has
passed after coordinator read-only review and explicit execution approval. It does
not copy/read ordinary CLI credentials or print vendor frames.
Native refresh persistence and synthetic revocation/redaction tests are green, but
multi-day refresh longevity is not claimed. Actual authenticated adapter behavior
is recorded below. The real dedicated login was not revoked merely to test a remedy.

## Authenticated synthetic validation

Command from this worktree, using the newly provisioned dedicated Studio login:

```sh
PYTHONPATH=. /home/asa/devel/machinome/.venv/bin/python docs/spikes/codex-tool-isolation/studio_live.py
```

The first run passed direct image/steering/error checks, then correctly refused a
second borrower because the first authenticated turn emitted native bookkeeping
not observed by the credential-free fixture: `.sandbox_migration`,
`thread-writer-locks/` and `thread_history_1.sqlite` with WAL/SHM sidecars. No gate
was skipped. The pinned native source identifies exact marker `v1\n`, empty
coordination/UUID thread locks, and the lazy thread history database; these are
not configuration/skills. Narrow owned regular-file/directory and bounded lock
metadata validation was added red-first; unknown entries, symlinks, wrong types,
nonempty locks and altered marker remain rejected. Coordinator reviewed this
state-provenance refinement; the qualification contract remained unchanged.
Focused auth/adversarial/refresh tests passed 14 cases independently.

The approved second run exited zero with all 22 checks passing, enumerated in
`authenticated-validation.json`. Actual production
adapter and workers demonstrated blind image observation (a >64KiB valid PNG),
image-result activity, expected file-read error activity, active steering and
notices, late-notice rejection, concurrent project turns, idle Sol-to-Astra change
retaining context and thread, and native Foreman assignment followed by Machinist
acknowledge/report/complete under exact diagnostic session routes. The lifecycle
HTTP peer is a synthetic fixture, not a claim of a second full browser/broker
integration run. Existing broker/orchestrator and mixed-backend tests supply that
portable integration evidence.

Restart occurred while Builder/Foreman were used and Machinist pristine: used
native identities and remembered context survived guarded resume; the pristine
opaque handle survived while its native thread was recreated without replay.
Closing Builder preserved the sibling project's real delivery. Last-reference
close reaped the native owner, removed a nonempty set of owned rollout paths and
preserved the dedicated native auth file. Both temporary Git projects remained
unchanged except the intentionally supplied image fixture. Temporary projects
were removed only after owned adapters/service/workers stopped.

Production launch issued native account/read with refreshToken=true and the
dedicated auth file persisted across real restart/teardown. This proves the native
refresh request path and store preservation, not multi-day refresh longevity or
that refresh was needed during this short run. Synthetic refresh-store mutation
and revoked-response tests prove remedies/redaction without revoking the real login.
No real mechanical project roles or ordinary CLI credentials were touched.

## Final completion gate

All tasks are complete. The pilot explicitly ratified “Accept the narrow Codex
exception” on 26 September 2026. The synchronized runtime-location requirement
and ADR 0032 amendment of ADR 0027 now permit only fresh Codex availability
qualification, explicit selection or dedicated provisioning to discover and
retain the pinned qualified executable. Non-Codex behavior and package/framework
resolution remain unchanged. The coordinator approved final artifact review and
directed archive plus the focused implementation commit. Every delta requirement
was compared with its baseline and found synchronized. Strict change validation
passed immediately before archival; the complete record (including its original
`.openspec.yaml`) is archived at
`openspec/changes/archive/2026-09-26-restore-scoped-codex-backend/`.
This record accompanies the implementation commit. Integration, pushing,
publication and worktree cleanup have not occurred.
