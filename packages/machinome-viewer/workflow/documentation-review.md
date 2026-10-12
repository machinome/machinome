# Viewer user documentation — review evidence

Date: 2026-09-20. Status: **pilot approved; specifications synchronized and
change archived** at `openspec/changes/archive/2026-09-20-user-documentation/`.
OpenSpec change: `user-documentation` (pre-ratified proposal/implementation).
Planning commit: `6a056cb`; base: viewer main
`4d575f3768587c515cdcaac426c84d507187b600`.
Worktree: `WTs/viewer-user-docs`, branch `user-documentation`.
No runtime/interface/version changes; no new ADR is warranted.

## What is ready

- Fourteen Sphinx pages, using the same pinned Sphinx 9.1.0 and RTD theme 3.1.0
  as the approved mechanics manual.
- Maker installation/operation/sharing guides, embedding, compatibility,
  troubleshooting and complete public browser/CLI reference.
- All four browser mounts, handle members and nested options have reference
  entries; the tests derive 106 coverage checks from TypeScript interfaces.
- A working, click-to-load spinner from the committed export and current bundle.
  The HTML source/script shown in the manual are the actual running example.
- Python metadata, source manifest and `.readthedocs.yaml` point to/support the
  manual. The independent viewer remains explicitly unreleased.
- Thirty-five development records moved byte-for-byte from `docs/` to
  `workflow/` (34 decision-log files and one release-preparation file). Their
  status and authority are preserved. README/current links are updated.

## Red before green

Before implementation, `pytest tests/test_documentation.py` failed all four
original checks: missing manual/configuration, workflow records under `docs/`,
missing documentation metadata and missing source-manifest entries.
`npm test -- src/documentation.test.ts --reporter=dot` failed all 106 public
interface checks. Those checks now pass. Two additional checks verify every
CLI option and the describe example's versions against source metadata.

## Validation

- Strict viewer HTML build: 14 pages, no warnings. Executed with documentation-
  only Python dependencies; isolated import lookup confirmed neither Machinome
  nor the viewer runtime is installed in that environment.
- Widget suite: **1,350 passed** across 47 files, including all 106 reference
  coverage checks. TypeScript `tsc --noEmit` passed.
- Python suite: **186 passed, 18 subtests passed, 2 skipped**. The skips require
  separately prepared real Curta builds and are not claims of full-Curta
  acceptance. Existing dependency/Pillow deprecation warnings remain.
- Final focused documentation checks: **6 passed**; all CLI flags and package/
  API/document versions are covered.
- `scripts/check-dist`: source distribution and wheel build; wheel installs
  and describes itself in a throwaway environment outside the checkout.
  No upload. The existing locked npm dependencies report 3 moderate audit
  findings during packaging; this documentation change does not update them.
- Extracted the final source distribution outside the checkout and built its
  complete manual with the documentation-only environment, warning-free.
  Verified inclusion of configuration, all page/example sources, review script
  and committed spinner assets. Generated HTML, npm dependencies and test
  screenshots are excluded. The screenshot-exclusion check was added red-first
  after the packaging smoke exposed the pre-existing broad test-file glob.
- `git diff --check` passed. Git blob comparison verified every relocated
  development record is byte-identical to its original.

## Browser evidence

`python scripts/check-docs-browser.py` checks the actual built site:

- 14 pages at 1440×1000 and 390×844; no page-wide horizontal overflow.
- 201 local links/anchors resolve; search and mobile menu work.
- The real spinner loads, accepts timeline input and opens its assembly tree.
- The exact running-reference snippet executes a one-second, 240-tick request
  on the committed Pascaline fixture and returns `completed`, admitted 1.
- The exact clocked-reference snippet admits a 360-degree stroke and restores
  the saved calculator-fixture bank.
- No JavaScript page errors or failed HTTP responses.

Screenshots/report: `_build/docs-review/`. Desktop/mobile landing, reference,
search and interactive screenshots were inspected. Narrow screens can collapse
the sidebar to maximize model space; the mobile example uses a narrower tree.

Framework links are owned by its separate `viewer-documentation-links` cycle,
planning commit `089d488`. Four distinct framework-to-viewer targets and five
viewer-to-framework targets resolve against the local builds. The framework
manual preserves its existing embedding guide and corrects the immediate-move
versus drawn-trigger distinction. A one-line shop maintenance commit `0705d5e`
on `viewer-doc-record-path` updates its decision-log pointer; it follows this
approved relocation into the shop's primary branch.

## Review gate and previews

- Viewer: <http://localhost:8022/>
- Framework links: <http://localhost:8023/viewer.html> and
  <http://localhost:8023/embedding.html>

The pilot requested review **before sync/archive**, then approved the rendered
site and explicitly directed synchronization, archival and integration on
2026-09-20. All three requirements are synchronized into the new baseline
user-documentation spec. The completed implementation commit contains the
archive and this approval record. Final focused Python checks (6), browser
reference coverage checks (106) and strict viewer/framework HTML builds passed
again before completion. Integration is authorized into each repository's
`main`; nothing has been pushed or published.
The earlier mechanics change and its framework link change were separately
approved, synced, archived and committed (`ae7901e`, `832d84c`).

Read the Docs configuration is ready; the hosted project/import/webhook and
actual remote build have not been created or verified. See `documentation.md`
for the one-time setup before a push can trigger a hosted build.
