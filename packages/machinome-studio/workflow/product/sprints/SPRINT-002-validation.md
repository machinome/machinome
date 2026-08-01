# SPRINT-002 validation matrix: one model viewer

Status: Ratified by the pilot on 2026-08-01 before the first feature cycle.

This matrix defines the sprint-level proof that the shop floor, an exported
directory, Sphinx documentation, and the live development loop use one
framework-owned viewer without regressing their existing behavior. Cycle
proposals own their detailed requirements and tests, but their combined tasks
must cover every row here.

Every command states its working directory. Every recorded result names the
exact shop and framework content commits tested. Generated verification
artifacts live outside every Git worktree under
`${XDG_CACHE_HOME:-$HOME/.cache}/hermes/verification/sprint-002/<run-id>/`, use
one task-scoped rolling manifest there, and are cleaned separately after results
are reported.

## Gates

1. A cycle proposal may not be ratified while one of its rows lacks an exact
   test home, negative path where applicable, and the exact commands that cycle
   will execute. This sprint matrix names command families; each owning proposal
   resolves its focused selectors and package paths against its cycle worktree.
2. Producer contracts are ratified before dependent consumers are proposed.
   Downstream cycles consume the integrated contract rather than guessing it.
3. A cycle is not integrated merely because its own suite passes. Dependencies,
   repository identity, two-commit shape, archive, and paired validation remain
   separate gates.
4. The final sprint is not ready to archive until every row is green against
   the final paired content commits and the visual evidence has been inspected.
5. A passing suite never substitutes for visible model inspection, and a
   screenshot never substitutes for a structural or behavioral assertion.

## Contract and behavior matrix

| ID | Outcome and proof obligation | Owning cycle | Canonical automated proof | Negative or boundary proof | Final evidence |
| --- | --- | --- | --- | --- | --- |
| V1 | `manifest.json` and `viewer.json` use one node-tree walk and name the same nodes for the same assembly. | F1 `unified-node-serializer` | Framework export and builder tests compare both documents from one fixture, including linked child names, operations, colour, rigid short-circuiting, and model rooting. | List/tuple render results, linked child naming, and invalid/non-rigid paths retain their current behavior. | Focused framework tests plus complete framework Python suite. |
| V2 | The two documents converge additively without being renamed: `viewer.json` gains `format`; `manifest.json` gains `mtime`; their distinct rooting and portability remain. | F1 | Framework export, builder, Sphinx, and publication tests assert exact document fields and path roots. | Existing document names remain required; build publication is not made portable or self-contained. | Canonical examples from one build and one export retained in the verification manifest. |
| V3 | A framework cycle worktree can use every viewer frontend package without installing dependencies inside that worktree. | S1 `viewer-bench-symlinks` | `tests/dev-env-test.sh` creates fixtures with multiple frontend packages and verifies discovery, exact package-relative links to the primary framework checkout, conflicts, setup, and teardown. F2's preimplementation gate proves its package path has a primary counterpart and its lockfile is compatible with the shared install. A package rename is not assumed; if F2 proposes one, it must first ratify and prove a dependency-source/refresh path. | Missing primary counterpart, incompatible lockfile/install, missing dependency/generated source, escaping paths, stale/wrong links, dirty base, and manifest collision fail closed. | From the shop sprint worktree: `bash tests/dev-env-test.sh`; the fixture asserts resolved targets before cleanup. F2 records lockfile compatibility before its frontend commands run. |
| V4 | Shared heavy frontend directories are used safely and their writes have attributable source. | S1 and sprint dependencies | Dev-env tests prove each link resolves to the same package-relative directory in the exact primary framework checkout and never to another package, worktree, or workspace. The durable sprint graph serializes framework viewer build cycles: F2, then F3, then F4. | Wrong-package, cross-worktree, cross-workspace, and escaping targets are rejected. No second framework cycle that can write the shared target may open before its predecessor integrates. | Resolved-target assertions, cycle dependency/integration evidence in `current.md`, and final clean-checkout distribution proof under V10. |
| V5 | The private framework viewer exposes the one imperative API needed by all consumers while retaining `solid-widget.js`, `data-solid-widget`, and `SolidNodeWidget`. | F2 `viewer-package` | Viewer Vitest and typecheck coverage for mount options, handle methods, auto-mount, API version, and unchanged published names. | Unknown/invalid options and malformed snapshots produce defined failures; no React dependency enters the package. | From the integrated viewer package directory resolved by F2: `npm run typecheck`, `npm test`, and `npm run build`. |
| V6 | One loader accepts either published document and resolves model URLs from the supplied source/base without changing either document's rooting. | F2 | Viewer tests load representative `manifest.json` and `viewer.json` fixtures and assert identical scene trees and resolved model requests. | Missing root, missing model, malformed operations, and failed model fetch cannot leave a partially accepted scene. | Browser network trace or request assertions for both document forms. |
| V7 | Viewer parity covers degree-based expressions, transform composition, inherited colour, normal material without inherited colour, lighting, Z-up camera fit, and model bounds. | F2 | Focused evaluator/tree/scene tests plus widget browser E2E. | Expression and model-load failures are surfaced rather than rendering an unexplained blank pane. | Widget E2E screenshot of a fixed coloured and uncoloured animated fixture. |
| V8 | Animation supports none, inline bar, compact persistent `Timeline` toggle, and externally driven time, including initial time and autoplay. | F2 | Viewer tests cover every mode, `0..1` time, autoplay, repeated updates, and toggle state. Existing export and Sphinx tests cover their public query behavior. | Out-of-range or malformed time follows the ratified normalization/failure contract; hidden controls remain absent from accessibility interaction. | Export, Sphinx, and floor browser assertions against the same animated fixture. |
| V9 | The handle supports `dispose()`, `view()`, and `reload()`; reload and remount preserve a captured camera when requested. | F2 | Viewer lifecycle tests prove listener/renderer disposal, camera capture/restore, reload replacement, and stale asynchronous-load rejection. | A stale load cannot reattach an old mesh after reload or disposal. | Programmatic camera comparison plus before/after screenshots. |
| V10 | Wheel and sdist contain a freshly built viewer bundle produced from their exact framework content commit, and a clean development checkout can obtain it through the framework. | F3 `viewer-bundle-delivery` | Export the exact integrated framework content commit into a disposable full checkout outside every worktree, initialize/install frontend dependencies there, build distributions into a disposable output directory, inspect both archives, install the wheel into a disposable environment, and invoke the accessor. | Missing Node/npm, failed frontend build, missing bundle, stale incompatible bundle, and archive omission fail the build or accessor explicitly. | Disposable checkout commit identity, command log, archive member lists, installed accessor output, bundle checksum, and cleanup status. No source-stamp capability is added to the viewer. |
| V11 | The CLI accessor has one exact machine-readable contract for bundle path and API version. | F3 | Framework CLI tests compile/validate the exact output schema and test the canonical installed-package example. | Unknown arguments, missing bundle, stale or incompatible bundle, malformed metadata, path escape, and incompatible internal metadata return specified non-zero statuses and stderr. | Raw accessor stdout/stderr/status from source and installed wheel. |
| V12 | The shop refuses preparation with one actionable error when the framework viewer is absent, malformed, or below the required API version. | S2 `floor-uses-framework-viewer` | `tests/test_project_preparation.py` covers real and fake CLI contracts; `tests/fixtures/fake_solid.py` emits every supported success/failure response. | Missing executable/bundle, malformed JSON, unknown fields as specified, inaccessible/escaping path, and incompatible version all fail before listener bind or backend startup. | Focused preparation tests and one black-box failure invocation. |
| V13 | Floor serves and mounts the framework bundle, deletes its renderer copy, and drops direct `three`, `@types/three`, and `jokenizer` dependencies. | S2 | Frontend typecheck/build, static-route API tests, dependency/lockfile assertions, and browser network assertions prove the served bundle comes from the accessor result. | No fallback to a vendored or stale committed renderer is allowed. | `scripts/test-e2e`, full shop suite, static bundle inventory, and browser network evidence. |
| V14 | Floor retains its functional-model chrome and camera across model rebuilds: class `functional-model`, canvas role/label, timeline expanded state, and captured view. | S2 | Browser E2E asserts DOM/accessibility state, model-change handling, and programmatic camera state before and after rebuild/remount. | Failed rebuild retains the prior inspectable model and does not reset its view. | Fixed-viewport screenshots before and after successful and failed rebuilds. |
| V15 | `solid develop` consumes the shared package and no longer uses the per-node HTTP tree or the retired flat-scene implementation. | F4 `dev-viewer-on-shared-package` | Framework manager/viewer tests assert snapshot serving, reload signaling, shared-package mounting, and retirement of per-node routes/walks. | Requests to retired per-node interfaces are absent/rejected as specified; no second serializer or renderer remains in source. | Source/inventory assertion plus development-loop browser network trace. |
| V16 | Development reload survives successful rebuilds, server offline/reconnect, build errors, and stale in-flight model loads while preserving the last valid model and view. | F4 | Development app tests cover the reload state machine; framework integration test drives success, error, offline, and recovery transitions. | Old asynchronous results cannot reappear after generation change; build failure cannot erase the previous valid scene. | Ordered event log, programmatic camera comparison, and screenshots for normal/offline/error/recovered states. |
| V17 | Sphinx documentation embeds the shared viewer and the V8-engine example builds with warnings treated as errors. | F2, confirmed after F3/F4 | In the framework sprint worktree, initialize the exact pinned `docs/examples/v8-engine` submodule; from `solid-node/WTs/sprint-002/docs/examples/v8-engine`, generate the export at `docs/_exports/v8-engine`; then from the framework sprint root run `python -m sphinx -b html -W docs docs/_build`; deinitialize the submodule before bench teardown. `tests/test_sphinx_ext.py` remains the focused test home. | Missing submodule, missing bundle, or malformed export fails preparation/build rather than silently emitting a broken iframe. | Submodule commit, generation command, built page screenshot, network assertion, warning-free output, and deinitialization status. |
| V18 | No duplicate production renderer or serializer remains, including `SnapshotNodeAPI`. | F1, S2, F4 | Each proposal names executable repository searches and dependency assertions for the retired serializer functions, floor `viewer.ts`, development `node.ts` renderer, `SnapshotNodeAPI`, and renderer-only dependencies, followed by the canonical suites that would detect live references. | Purposeful adapters and shells may remain, but no second evaluator, tree walk, scene builder, or bundled three.js copy may satisfy a consumer. | Recorded search commands and zero-match/allowed-match inventory against both final content commits. |
| V19 | Existing public names and excluded behavior remain unchanged. | All affected cycles | Export, Sphinx, CLI, and browser tests assert `manifest.json`, `viewer.json`, `solid-widget.js`, `data-solid-widget`, and `SolidNodeWidget`; recorded repository searches prove no registry publication configuration or compatibility alias was introduced. | No compatibility alias for a renamed public surface is needed because no public surface is renamed. | Exact test selectors, recorded searches, and canonical export host page. |
| V20 | All four user surfaces demonstrably consume the one framework viewer implementation. | Sprint paired validation | Export, Sphinx, and floor network/file evidence identify the distribution bundle, compare its bytes/checksum, and assert its API version. The development app may rebundle the package; its build dependency graph, source inventory, package API-version import, and browser behavior instead prove that it imports the shared package and contains no second renderer. | A vendored alternative, second evaluator/scene builder, or unexplained distribution-bundle mismatch fails identity proof. No new checksum-reporting viewer capability is required. | One summary table containing surface, consumed package/bundle path, applicable checksum or build-dependency evidence, API-version evidence, shop commit, and framework commit. |
| V21 | Shop behavioral specifications and architecture records permit and describe the framework viewer used by the floor. | S2 | OpenSpec delta/sync validation plus exact review of the effective `openspec/specs/functional-model-inspection/spec.md`; ADR index/overview checks cover the amendment or superseding ADR for ADR-0004. | The effective baseline must not retain the retired `SHALL NOT use the separate export widget` mechanism or an architecture statement excluding the implemented shared viewer. | Archived S2 change, synchronized baseline requirement, ADR disposition, strict OpenSpec validation, and recorded effective-scenario comparison. |

## Cycle integration gates

### After F1 and S1

- Run both complete repository suites affected by the cycles.
- Re-run an export and build snapshot from the same framework fixture.
- The F2 proposal chooses a package path that satisfies S1's already integrated
  package-discovery contract. Its preimplementation review proves that mapping
  and shared-install compatibility before F2 ratification; S1 does not depend on
  a future F2 path. If F2 proposes renaming the package directory, it returns to
  the pilot with an executable dependency-source/refresh design before
  ratification.

### After F2

- Run viewer typecheck, unit tests, build, widget E2E, export tests, Sphinx tests,
  and a warning-free documentation build.
- Record the exact viewer API/version contract used by F3 and F4.
- Do not propose either consumer against an unintegrated or inferred contract.

### After F3

- Build and inspect wheel and sdist from a clean disposable output location.
- Install the wheel into a disposable environment and invoke the accessor.
- Record the exact accessor schema and canonical response before proposing S2.

### After S2 and F4

- Run the complete shop and framework suites and both frontend suites.
- Exercise the floor against the linked framework sprint worktree.
- Exercise `solid develop` from the framework sprint worktree.
- Capture the fixed model on export, Sphinx, floor, and development surfaces.
- Verify bundle identity, camera preservation, reload, offline, and build-error
  behavior before final sprint archival.

## Final command families

Cycle proposals must resolve package paths and exact focused test selectors. The
final paired run includes at least these command families, with the exact final
commands and working directories recorded in `current.md`:

- Shop: `python -m pytest tests/`
- Shop bench lifecycle: `bash tests/dev-env-test.sh`
- Shop frontend/browser: `bash scripts/test-e2e`
- Framework Python, from `solid-node/WTs/sprint-002`:
  `PYTHONPATH="$PWD" ../../../.venv/bin/python -m pytest tests/`
- Viewer package: `npm run typecheck`, `npm test`, `npm run build`
- Development app: its ratified typecheck/test/build commands after F4
- Distribution: `python -m build` into a disposable output directory, archive
  inspection, disposable wheel installation, and accessor invocation
- Documentation: from `solid-node/WTs/sprint-002`, initialize the pinned
  `docs/examples/v8-engine` submodule; from its
  `docs/examples/v8-engine` directory, generate the V8-engine export at
  `docs/_exports/v8-engine`; return to the framework sprint root and run
  `PYTHONPATH="$PWD" ../../../.venv/bin/python -m sphinx -b html -W docs docs/_build`;
  deinitialize the submodule before teardown

## Visual evidence procedure

1. Use one fixed, committed representative model that contains nested transforms,
   inherited and absent colour, animation, and bounds that expose camera fit.
2. Fix browser engine, viewport, device scale, initial time, and autoplay.
3. Capture export, Sphinx, floor, and development-loop views.
4. For floor and development, capture camera state, trigger a successful rebuild,
   and compare the restored position and orbit target before taking the second
   screenshot.
5. Capture the floor after a failed rebuild and development during offline,
   build-error, and recovered states.
6. Inspect screenshots for geometry, transform, material, light, camera, animation
   chrome, clipping, and stale-scene artifacts. Do not use pixel equality as the
   sole oracle.
7. Record screenshot paths and generating commands in the task-scoped manifest;
   report results before deleting them in a separate cleanup step.

## Final sprint evidence record

Before archival, `current.md` records:

- every integrated cycle and its two commits;
- final shop and framework content commits;
- exact commands and exit results;
- wheel and sdist bundle membership;
- installed accessor output and bundle checksum;
- the four-surface bundle identity table;
- visual evidence disposition;
- any accepted limitation explicitly within ratified scope; and
- cleanup status for disposable environments, servers, worktrees, and visual
  artifacts.
