## Context

The originating Voron-2 printer is a valid version-4 posed export with 1,636 assembly nodes, 1,565 model paths, 232,347 ordered bindings and a roughly 26 MB manifest. Chromium receives the page, bundle and manifest, then stalls without requesting a model. Existing project document replay is not a browser pass.

`assertRenderable` builds the binding closure, then checks every operation and flexible parameter. Each `note` obtains the complete binding root map inside an expression scope and separately calls `freeVariables`. The original root map creates 483,728 distinct nodes, above the unchanged 125,000-node reclamation trigger. Consequently the next outer operation reclaims the graph and a later `note` re-prepares the whole map. This is now observed, not inferred from binding count.

`inspectProfileExpression` independently expands aliases with a new visited set on each call. Protecting all validation alone leaves repeated large traversals: an instrumented unmodified walk did not complete within a 12-second fence, and another scoped observation still revisited more than 300,000 nodes per individual call before its 30-second fence. An experiment that retained successful negative structural checks for this one stable validation operation completed validation in 4.23 seconds, with 610,546 nodes and no generation change. Details and limits are in `evidence.md`.

The governing decisions are ADR-043 (page-scoped DAG, finite reclamation between synchronous operations), ADR-044 (document-local bindings with generation guards), and the current `viewer-package` expression-pressure, numeric-parity and malformed-table requirements. Existing profile validation is also governed by `finite-convex-profile-contact`. This correction implements those contracts; it does not change the numeric evaluator.

## Goals / Non-Goals

**Goals:** Complete the actual printer's browser mount with its full document and geometry; retain its default and Home/Center/Present poses; eliminate demonstrated repeated full-table preparation and repeated negative profile reachability during one validation; reject all malformed and unsupported content as before; preserve last-good-model behavior and independent document meanings.

**Non-Goals:** Producer changes, document pruning, numeric constant substitution, geometry decimation, larger cache thresholds, disabled validation, new host controls, generalized running performance work or resolving the separate capture fetch failure. No shared-venv installation or mutation is part of this cycle. No API or document-version bump.

## Decisions

### 1. Protect the complete synchronous validation operation

Make the public `assertRenderable` entry protect its full synchronous validation, including binding-table construction, program/clocked loading, tree-expression checks and final entry checks, with the existing nestable `withExpressions` mechanism. A private scoped implementation is a straightforward way to keep the entry readable. Nested existing scopes are safe. Validation may exceed the trigger; the next outer operation can reclaim as ADR-043 already permits. Error exit must release the scope in `finally` through that existing mechanism.

Keep this protection synchronous. Fetching/parsing happens before it and no async loading, mount lifetime or `await` belongs inside it. Protecting only each `note`, only `roots()`, or only the initial table construction leaves the demonstrated repeated work. Raising the trigger would fit this printer by accident and conceal the same failure for the next larger supported document.

### 2. Reuse only established absence of a profile call in this validation

Introduce an operation-owned structural inspection context for `note` that shares successful no-profile subgraph results across operation and flexible-parameter roots. Continue using the existing structural walk and error checks. After a complete successful inspection returns false, all nodes proved clear by that inspection may be marked clear; subsequent checks can skip them. Do not mark any subgraph from a positive or failed traversal as clear. Continue checking the reserved name's direct-callee context before any visited/clear shortcut, preserving rejection of a bare or indirectly called `profileOverlap`.

Bind this context to this exact document's binding map and expression generation, with disposal at the end of validation. No memo survives into another document, an async boundary, a reset or a different profile-table/index-validation context. A helper may enforce those keys explicitly if it can be used in more than one scope. The existing public-to-source `inspectProfileExpression` behavior used by running Bounds remains available; there is no reason to change that numeric path for this posed printer.

The negative-only strategy is deliberately smaller than a generalized graph analyser: it fixes the observed repeated absence checks and cannot turn a profile-containing subtree into a negative result. Keep node/argument traversal order and all reserved-call syntax/index errors intact. A public format/version shortcut or text search would skip semantic structure and is rejected.

### 3. Prove work and behavior separately

Use test-only counters or source-level seams for table preparations and structural node visits, without adding members to the host handle. A small synthetic ordered table plus a deliberately low reclamation trigger must demonstrate that one validation does not rebuild its table once per checked expression. A shared-prefix DAG, read from many operation and flexible-parameter expressions, must demonstrate that negative inspection work grows with distinct visited nodes rather than repeated transitive expansions. Timing alone cannot pin either regression.

Preserve numeric `Object.is` comparisons, including signed zero, eager structural refusal of dead-branch malformed profile calls, existing operator/short-circuit behavior and document-local scope. Run existing evaluator, binding, expression lifetime, document and profile suites, then the full widget suite, typecheck and relevant Python browser suites against the newly built worktree bundle. If the full printer uncovers a subsequent mounting failure, record its reproduction in this change and return to the reviewer before expanding this design; never call validation completion a mount.

### 4. Keep the acceptance document and resources intact

The integration gate uses `/mnt/data/machinome-projects/3D-Printers/Voron-2/_build_resume_main_browser_export` unchanged as its manifest/model source. Serve its actual portable page and assets through a read-only loopback server with the candidate bundle supplied at the bundle route. This substitution isolates the candidate viewer and is recorded; do not rewrite the page or manifest, regenerate geometry, hide nodes, or substitute fake meshes. Hash the input manifest, original bundle and candidate bundle; record all 1,565 model paths and all unique requested resource URLs.

First prove this same gate red with the base bundle under a bounded Chromium/SwiftShader run. With the candidate, require a completed mount, successful model responses, finite whole assembly bounds and an inspected whole-printer screenshot. An additional host harness against the same unchanged manifest/assets may expose the mount handle for full assembly counts and default/Home/Center/Present readback, independent sampled world-matrix comparisons and rest/moved screenshots. Capture screenshots only after readiness; merely creating a canvas or fetching all models is insufficient. Missing browser support or a skipped gate is not acceptance.

Every browser/server is owned by a dedicated process group, has an outer wall-clock fence and bounded graceful-close/forced-cleanup path, and is checked absent afterward. Logs and screenshots use distinct ignored scratch names; project shared cache/log files are untouched. Read `simulation/tools/browser_export_probe.py` for historical reproduction, but do not execute its shared-cache writer as the new harness.

## Risks / Trade-offs

- **The whole live graph remains in memory during validation** → This is the existing large-operation contract; measure browser peak RSS/heap as diagnostic evidence and keep later-operation reclamation and final-mount disposal tests. Do not claim a universal memory budget from this machine.
- **Cached negative inspection crosses binding meaning or generation** → Own it per synchronous validation and test two documents with identical alias text, reset/reload, and failed replacement. Keep direct-profile name checks before cache shortcuts.
- **A positive or failed profile traversal contaminates the negative set** → Publish negative facts only after a complete false result; adversarial tests place invalid calls behind shared prefixes, aliases, dead branches and flexible parameters.
- **Validation improves while geometry or pose still fails** → Actual complete export acceptance remains mandatory. The proposal has no successful browser result; later failures remain visible and gate archive.
- **Tests depend on a local printer checkout** → CI regressions use a small self-contained fixture and synthetic documents. The full-printer gate is separately recorded manual integration evidence, not an optional or silently skipped CI proof.

## Migration Plan

Review and ratify planning, strictly validate it, then the parent makes the planning commit. A different agent implements red-first in this worktree and builds its own bundle. Parent review repeats adversarial tests against the original full export before any baseline sync or archive. Record the reviewed cache-ownership and validation-boundary clarification in the existing ADR-043/044 records; the existing decisions already authorize synchronous scope and document-local ownership. After acceptance, sync/archive and commit implementation plus the completed evidence record as the second commit. The pilot authorized parent-controlled local rebase/merge only after those gates; this proposer performs no integration. No push or publication is authorized. Rollback is the focused viewer implementation commit; no data migration or producer rewrite is involved.

## Open Questions

The complete browser mount remains unmeasured with a corrected production implementation, including geometry resource pressure and interactive pose cost. Scratch validation and operation-value replay establish the two identified costs only. The applied cycle must resolve any new empirical mounting blocker through reviewer-approved scope rather than treating the prototype as a finished fix.
