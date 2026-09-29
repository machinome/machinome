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
