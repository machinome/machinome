# Adversarial review and independent checks

Coordinator-owned review record. Both checkpoints, live validation and final
record reconciliation are approved. Entries below retain the chronological
findings and rework evidence leading to that decision.

## Baseline and spike reproduction

- At planning head `58fa947`, before product integration, the existing backend
  probe, runtime profile and scoped-tool tests passed (37 tests).
- Independent credential-free rerun of the carried isolation spike passed all
  23 cases on installed Codex CLI 0.157.1, including native-tool rejection,
  empty-role registry, model change, guarded restart/resume and the positive
  control that detects native patching when an environment is present.
- The coordinator also ran the new qualifier with all five actual shipped
  role schemas plus an empty role: Builder 31 tools, Foreman 28, Designer 29,
  Machinist 29 and Librarian 27. All 196 cases passed against the installed
  binary without credentials or external model requests. This is draft-policy
  evidence; final adapter integration still requires its final-content rerun.
- Frontend dependency installation, TypeScript test and production build
  passed. npm reported six existing dependency vulnerabilities (one low,
  three moderate, two high); no dependency versions were changed here.
- The first broad test attempt lacked generated frontend assets and failed
  dependent API/browser startup. After building, the original 341-test suite
  had one skip and one failure: the carried spike's two Python scripts lacked
  repository licence headers. The coordinator added those headers and reran
  the licence test successfully. Existing subprocess/resource warnings remain.

## Authentication and process ownership checkpoint — approved

Findings returned for implementation/rework:

1. Copied refresh tokens are not a safe durable auth strategy. The pilot
   approved a separately provisioned Studio login; no normal CLI credentials
   are to be copied, read or updated by the new adapter.
2. A parent-only advisory lease is insufficient: an orphaned native process
   could continue refreshing after the parent dies. Native app-server and
   native login must inherit the lease descriptor. Independent testing with
   the actual binary confirmed a second lease remains blocked after releasing
   the parent's descriptor and becomes available after the native child exits.
3. Codex announces bundled native skills by default, even without execution
   environments. Qualification must check unwanted instructions as well as
   registered tools. The implementer reports actual outbound verification
   with the new skill-discovery controls; final independent validation remains.
4. Private-state cleanup must follow native process reap, including cancellation.
   Cached qualification must not skip effective production policy checks.
5. Experimental tool settings omitted from typed effective config need exact
   raw launch-layer provenance plus actual forced-call semantic checks. Missing
   launch provenance must fail, not pass vacuously.
6. Metadata/version/schema subprocesses must also use isolated configuration
   and environment, even when their requested operation is read-only.
7. Native delete failure must not pin a project reference and prevent sibling
   or final-owner cleanup. Malformed native event parameters must produce a
   visible transport failure, not silently end routing. Coordinator tests in
   `tests/test_codex_adversarial.py` proved both failures red (one assertion
   failure and one timeout); the inherited-lock regression passed.
   After implementation rework, the coordinator reran all 17 current
   auth/policy/service/adversarial tests successfully, including both cases.
8. A journal written only after native thread creation has a crash window.
   Verify atomically marked native threads and exact marked-group cleanup;
   unrelated/unmarked native records must not be deleted.
9. Coordinated restart must account for pristine siblings whose native rollout
   has not yet been persisted; one unused role must not force loss of every
   used sibling's retained conversation. Verify the actual native record
   format as well as the mocked recovery path.
10. Hub shutdown must continue across reference cleanup failures, not only
    project shutdown. A third coordinator regression proved that failure of
    the first native delete left the sibling reference, shared process and
    auth lease alive. Implementation rework fixed it; the coordinator's
    30-test rerun passed, including policy/qualification negatives, pending
    preflight cleanup and this all-project shutdown regression.
11. Later project borrowers must qualify the same executable/policy contract
    as the already-running shared process. Replacing the cached launch
    fingerprint with a newly qualified but different binary would misstate
    which runtime actually serves those roles; reject that mismatch.

The coordinator repeated all 196 actual-binary cases after strict experimental
schema fingerprints and native owner-group qualification were added. They
passed with binary SHA-256
`3e2584f3f3829a43a0495011a1cecb2facbe64a2403e2b682351fd9c2983f970`
and qualification contract
`a699ef07f108983541c8efcf4c3deabe61a7759b431a7fffb34a228b4936d13b`.
This remains checkpoint evidence, not final adapter approval.

Checkpoint one is approved to proceed to selectable adapter/UI implementation.
The final focused rerun passed 32 tests, including rejection of a changed
second-borrower contract and discard/tagging of stale generation events.
Authenticated floor behavior, long-lived native refresh/revocation handling,
full adapter cancellation and browser validation remain second-checkpoint work.

## Full adapter checkpoint — approved

Adversarial cases to verify include cross-project and same-role overlapping
handle routing, stale failure/completion events, duplicate call IDs with new
RPC IDs, broker sender spoofing, explicit large image transport, cancelled
worker shutdown, pre-preparation failure, concurrent project closure, idle
runtime rollback, and coordinated guarded recovery.

The existing orchestrator retries a failed retained delivery by opening a new
role. Codex must prevent that fallback from silently discarding a used
conversation when resume/auth/policy fails. A service-level exception alone
does not enforce this; verify the real orchestration recovery path.

Independent worker checks in `tests/test_codex_worker_adversarial.py` pass:

- A blocked worker launches a SIGTERM-ignoring descendant that attempts a
  delayed mutation. Cancelling the close awaiter still leaves owned cleanup
  running; the worker/group are killed and reaped, private state is removed,
  and no delayed mutation occurs. A positive control replacing group cleanup
  with parent-only cleanup fails on the expected late-write assertion.
- The actual MCP subprocess reads a PNG payload exceeding 96 KiB and preserves
  every byte through native `inputImage` conversion. The read-only role worker
  refuses an undeclared write and an absolute `/proc/self/environ` read. Only
  the original fixture file remains in its synthetic project.

These prove the worker seam, not yet model-visible authenticated image delivery
or the complete adapter's close ordering. Existing orchestration tests also
pass (74 tests; previously observed cleanup/resource warnings persist).

The first independent adapter-boundary run added five cases in
`tests/test_codex_adapter_adversarial.py`. Three failed red: a valid qualified
`functions` callback was rejected; a lifecycle call with another role's sender
reached the worker; and duplicate completed message events were both published.
The same-call-ID/new-RPC-ID mutation deduplication and changed-arguments
rejection case passed, as did cross-thread/turn/generation/schema rejection.
Those three failures were returned for implementation rework. Shared-transport
failure must also terminate old workers/callbacks before native recovery, and
a generic steer rejection must not be misclassified as a completion race.

The coordinator reran the adapter and orchestration tests after rework: all
three initial defects passed. A further red case showed native
`commandExecution` notifications were ignored; the implementation now
invalidates the shared owner and quiesces its borrowers. The subsequent
25-test root/service/orchestration run passed, including that native-event
regression. A new mixed-owner orchestration check also passes: an initial
context-unrecoverable delivery fails only its role/envelope, and the next
sibling-backend delivery succeeds.

Further coordinator regressions pass for an immediately retried confirmed
steer/completion race and terminal failed activity when a blocked tool is
cancelled on close. After removing duplicate imported test-case discovery,
the independent Codex discovery run passed 59 tests (before later additions).

A further coordinator regression demonstrated a queued failure poisoning a
new delivery on the same opaque handle after waiting for its delivery lock.
The implementation now correlates receipt-bearing failures with the latest
delivery and rechecks a pure adapter-owned validity predicate after that lock.
This also invalidates an already-yielded pristine failure after shared recovery,
without leaking native identifiers across the portable seam. Terminal cancelled
activities remain deliverable so their previously published running entries
settle. The coordinator's adapter/orchestration/Git-identity/refresh rerun passed
18 tests after this rework.

The independent full Python discovery subsequently passed 410 tests in
152.746 seconds with one skip: the optional development-workspace machinome
installation acceptance test could not find that installation. Frontend
TypeScript checks passed again. An existing ignored asyncio subprocess
destructor warning remains after suite shutdown. The final
credential-free actual-binary qualification passed all 196 cases, including
strict retained-thread readback and delete postconditions, with contract
`5a61647fe805a3f8111e14f5f75c5da82ef6a5375163915f630495750c912886`
and fingerprint
`411855633e23bbfade6e4ba052906dca330b71cb9ceca5231ff036f4543b4748`.
The binary SHA-256 is unchanged from checkpoint one.

Checkpoint two code review is approved to proceed to authenticated synthetic
validation using only the dedicated login. Final cycle approval, archival and
commit remain gated on that evidence and final regression checks. Worker-group
cancellation proves cleanup of owned ordinary descendants, not containment of
hostile project code that escapes its process group; OS isolation is deferred.

A final reader-path review found that malformed native notification data could
end the role reader without stopping its running worker. This was returned for
a focused regression and quiescence-before-failure correction. The implementer
verified the new regression red with only that correction removed; the
coordinator independently reran 22 backend/adapter-adversarial/result tests
successfully after restoration.

The proposal agent's final read-only consistency audit found a signing-policy
gap, confirmed by the coordinator: `openspec_setup` directly committed its
new record without the signed-commit refusal added to `git_commit`. The private
worker therefore could lose global signing intent on that second commit path.
The implementer verified its regression red, then added a shared signing guard
before initialization/staging. An existing-record no-op remains allowed. The
coordinator's 12 Git-identity/backend tests and 47 existing scoped/OpenSpec-tool
tests passed after correction.

The coordinator also added unsupported-content, malformed-image, item-count and
size-limit checks, preserved-error conversion, and actual partial-worker-start
reaping/private-state cleanup. All five worker/result adversarial tests passed.
These are verification additions against the existing result/cleanup code, not
newly reproduced defects.

## Browser review

The first 760-pixel screenshot showed the chat pane covering the runtime
controls and unavailable-login explanation even though the existing document
overflow assertion passed. The coordinator approved a narrow active-Agents-only
responsive correction. The implementer demonstrated the bounding-box assertion
red before correction. An independent frontend build and focused Agents E2E
rerun passed; the coordinator inspected the new 760-pixel remedy and 1440-pixel
activity screenshots. Controls and the complete login remedy are now readable,
with chat stacked below at narrow widths. The coordinator also inspected the
subsequent image-result activity and retained-context role-failure screenshot;
both are visible in the central activity pane. This is fixture-driven browser
evidence, not a claim that an authenticated model has received an image.

Dedicated login is provisioned only through the new explicit operator flow.
Do not use the historical live spike harness: its copied-credential approach
was rejected in review. No credentials or device codes belong in this record.

The pilot completed the new native device-authorization flow. The reviewed
`python -m floor.codex_auth login` command exited successfully after its
credential-free preflight, using the dedicated Studio store. This proves
provisioning, not yet authenticated adapter behavior or long-lived refresh.

## Authenticated validation and final checkpoint approval

The coordinator read the new `studio_live.py` harness before authorizing its
dedicated-login run. Review required a blind image question (no expected colors
in model input), used and pristine roles in the same restart, exact lifecycle
session routes, non-vacuous history cleanup, and shutdown before temporary
project removal. Only disposable synthetic projects and their fixture HTTP
peer were used; this is not a full production-broker acceptance test.

The first authenticated run passed image observation, actual image/error
activity, steering and notices, then correctly refused a second borrower when
new native bookkeeping files appeared. The observed pinned runtime emits
`.sandbox_migration`, `thread-writer-locks` and `thread_history_1.sqlite` with its
WAL/SHM companions. After checking their native purpose, the coordinator
approved only these exact entries with ownership/type/symlink checks, fixed
marker contents and bounded canonical empty lock files. Unknown configuration
and native skills remain rejected. The independent follow-up auth/ownership/
refresh suite passed 14 tests.

The reviewed harness then exited successfully with all 22 authenticated checks:
blind observation of the actual >64-KiB floor image; real tool error; active
steering and notice; late notice refusing a new turn; concurrent Astra memory
recall and Sol Foreman assignment; used Builder/Foreman native identities
retained after shared restart; pristine Machinist native thread recreated under
the same opaque handle; actual acknowledge/report/complete calls; sibling
delivery after closing the other project; native owner reaped and nonempty
owned rollout inventory removed; dedicated login preserved; synthetic projects
otherwise unchanged. No authenticated owner was left running.

The independent full regression rerun passed 415 tests in 154.056 seconds with
the same optional development-workspace acceptance skip and existing ignored
subprocess-destructor warning. This run preceded only the native-bookkeeping
refinement covered by the subsequent 14-test rerun. Native refresh ownership,
sanitized revocation handling and persistence have deterministic coverage and
the live owner uses native account refresh; no multi-day expiry or real account
revocation experiment is claimed.

Both code checkpoints and authenticated behavior are approved. Final durable
record review and strict validation gate archival and the implementation commit.

Final record review and independent strict change validation passed. Archival
and the implementation commit were withheld pending one pilot decision:
ADR 0027 and the existing runtime-location spec literally allow only OpenSpec
as an ambient-PATH dependency, whereas this approved Codex design resolves and
qualifies the installed native executable. The coordinator requested a narrow
Codex-only exception. The pilot explicitly answered “Accept the narrow Codex
exception”; only that qualified-Codex exception is authorized, not a broader
relaxation. Retained-history refusal was separately reconciled into the
existing recovery requirement to preserve the already-approved no-replacement
behavior. No primary integration, push or publication has occurred.

The coordinator read the final synchronized exception in the baseline, ADRs
0027/0032 and architecture, and independently validated all 25 baseline specs
strictly. The change is approved for archival and its focused implementation
commit on the existing isolated branch. Primary integration remains outside
this approval.
