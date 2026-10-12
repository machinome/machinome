# Root planning review — 29 September 2026

Approved as a narrow prerequisite for the commissioned Videomaker campaign,
under the pilot's delegated Sol proposal/apply/evidence and root review
discipline. This is not a claim that the pilot individually reviewed this
implementation detail. No main integration, push or publication is included.

The named consumer is Leonardo's 70-frame source/fractional-grid film. Root
independently checked all frames across three cold captures: two differ from
the cached variant at one geometry pixel in frame 10; one matches. Five
visits to the same time within one mount are stable. No mechanical source or
export changed. Exact cache equivalence remains a held gate.

The controlled two-STL overlap diagnostic demonstrates a viewer-owned
load-order defect independently of the real film's still-conditional cause.
Root checked Sol's 20 production-flag PNGs and independently repeated all four
ABBA mounts/five captures each. Reversing only response completion switches
the full PNG between `069361614c03ad12e160cdf1e77fbd4ff1547d2ae7db1b3407b6403d8442a2eb`
and `529fc85e7466dc46b25f5bc293303c8614b03a0fe3597f7348bc43a9908f31cb`.
There were no page/console errors. Reports and images are preserved in
`/mnt/data/machinome-projects/Leonardo/videos/demo-incremental-source-grid/_build/evidence/`
under `load-order-diagnostic-production-flags/` and
`root-load-order-diagnostic/`; the earlier wrong-flag preliminary run is
retained separately, not represented as the production-environment proof.

Review boundaries:

- Reserve identities before the asynchronous load; preserve concurrent
  fetches, physical depth, geometry, material properties and marking bias.
  Do not impose a global render-order override or geometry offset.
- The cold constructor's load starts follow document traversal. Reconciliation
  contains nested awaits: no universal reload-history equivalence follows
  from the proposed fix, and none is promised.
- Clean up resources newly owned by an individual failed load. Pre-existing
  aggregate sibling/reconciliation cleanup is not an originating requirement
  and was removed from the proposed correction.
- A new viewer-owned browser assertion must genuinely fail before code.
  The existing diagnostic's unequal PNGs are evidence, not a false claim of
  its process having failed an assertion.
- Both real films and repeated cold captures must pass exact full-frame
  comparison after repair. The controlled test alone cannot establish the
  cause of Leonardo's one pixel or close the Videomaker cycle.
- Keep API 28, document/package versions and the public host interface
  unchanged. Return any wider requirement to review before implementation.

Root read the complete proposal/design/delta/tasks and relevant source,
viewer baseline, README/changelog and ADRs 012, 037 and 056. Runtime source
is unchanged at this planning gate.

## Implementation review and independent controlled verification

Root reviewed the complete runtime diff and new unit/browser regressions.
The correction reserves mesh and material identity before awaiting STL bytes;
it leaves fetch concurrency, ready-only attachment, physical geometry/depth,
marking policy and targeted-update orchestration intact. Cleanup remains
local to the newly reserved load. No API/document/package version or global
render-order override changed. The five unit reds and the viewer-owned
exact-PNG ABBA red occurred before the runtime edit; the additional real-depth
regression was added after it, not retrospectively described as red-first.

Root independently reran the 61 focused tree tests and both Python browser
tests; all passed. Root also ran the separate evidence script against the
repaired worktree bundle, SHA-256
`5280a86be7cbe532dabac8cfc99d4b78822275686c8f6fe1356c796148bcc413`.
All four fresh browsers had the verified intended ABBA completion order,
without page or console errors. Root rehashed every saved PNG: all 20
captures equal
`069361614c03ad12e160cdf1e77fbd4ff1547d2ae7db1b3407b6403d8442a2eb`.
The report and images are preserved beside the earlier failures under
`root-fixed-load-order-diagnostic/`. This independently establishes the
controlled fix, not universal cross-environment reproducibility. Real-film
repeatability and cache-equivalence gates remain pending with the separate
Sol empirical worker.

## Real-film acceptance

Sol reran both consumers with the repaired bundle and frozen Videomaker
runtime. Root independently hashed every assembly PNG, every saved manifest
and MP4, and every referenced generation index. The 80-frame local-title
edit reused A+D (40 frames), captured B+C (40), and matched its separate
cold render at all 80 indices. The 70-frame source/fractional-grid camera
edit reused A+D (25), captured B+C (45), and matched all 70 indices of
each of three separate cold mounts: 210 exact frame comparisons.

The previously unstable frame 10 is now identical in the baseline, warm,
incremental and three cold runs: SHA-256
`198ed28cbc3ff0238bb83cab729d88bec46ddbe886441fda00400470e665d8e2`,
pixel (487,262) RGB [25,33,37]. Root inspected the encoded contact sheets
and the full-resolution source frame; the source, model, joins and ending
remain present. The mechanical source, kinematics, export and original
46-second film retain their recorded hashes. No paid speech was generated.

Reports are project-owned, under each of `videos/demo-incremental-rendering-fixed/`
and `videos/demo-incremental-source-grid-fixed/`, at
`_build/evidence/fixed-viewer-revalidation.json`; encoded review images are
beside them in `fixed-viewer-review/`. All old failures remain intact.
The narrow correction eliminates the controlled defect and passes the
originating consumer's held gate in this environment. It does not establish
universal GPU/browser reproducibility or arbitrary reconciliation-history
equivalence. Root accepts the implementation for spec sync and archive;
no main integration or publication is authorized.
