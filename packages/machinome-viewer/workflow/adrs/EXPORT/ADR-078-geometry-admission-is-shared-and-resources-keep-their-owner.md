# ADR-078 — Geometry admission is shared, and resources keep their owner

- **Status:** Accepted
- **Date:** 2026-10-05
- **Change:** [mount-voron-export](../../../openspec/changes/archive/2026-10-05-mount-voron-export/)
- **Builds on:** [ADR-035](ADR-035-reusable-viewer-core-and-declared-api.md),
  [ADR-056](ADR-056-a-marking-is-a-decal-in-the-parts-own-group.md),
  [ADR-037](../VIEWER-WEB/ADR-037-targeted-in-place-viewer-updates.md)

## Context

After synchronous validation was corrected, the unchanged full Voron-2 portable
export requested all 1,565 model paths at once. Chromium 151.0.7922.34 rejected
290 with `net::ERR_INSUFFICIENT_RESOURCES`; the page displayed `Failed to fetch`
and did not mount. This actual-browser failure, not a speculative throughput
optimization, required the reviewed loading amendment to this change.

Pinned three.js r156 starts each distinct-URL fetch immediately. Its overlapping
same-URL callback sharing is not a request budget, but does parse separate
geometry for each STL subscriber. Early mesh/material reservation already keeps
render identity in document order and must survive queuing. Failed preparation
must preserve the last good model; disposal must not attach or leak late results.

A read-only network control consumed all 1,565 original model bodies (59,271,584
bytes) with peak four and zero failures in 1.9624 seconds. This grounded a
conservative initial budget, not a browser limit or optimum; actual parsing,
mounting, poses and pixels remained mandatory acceptance gates.

## Decision

Use a private FIFO admission queue shared by every viewer created by **this
bundle in this page**, with four active distinct-URL request groups. It covers
fresh mounts, reload candidates, reconcile children, model and marking loads,
and targeted artifact preparations. Separate bundle copies do not acquire a
new cross-bundle coordinator. There is no public host option, retry, permanent
STL cache, geometry substitution or document/API version change.

Reserve mesh/material identities synchronously in document traversal order
before admission. Admitted subscribers use the real STLLoader and existing
normal/marking preparation. Readiness still waits for every required asset;
a failed required asset rejects rather than admitting an incomplete tree.

Pending identical string URLs may join one queued or active group; each
subscriber owns its own STLLoader parse, mutable geometry and material. Close
join eligibility at the first actual subscriber settlement, while holding the
active slot until **all** subscribers settle. A later genuine artifact request
must read the current resource, not join a completed group. Canceling the last
queued subscriber closes its eligibility immediately: a later same-URL job gets
a new FIFO position behind existing jobs. Closing an older group cannot remove
a newer group's URL entry.

Each tree/load owner cancels only its queued jobs and resources. Those jobs
reject without issuing network requests. Pinned r156 offers no supported abort
for active loads, so disposal holds their slot through actual body/parse
settlement. Late or abandoned returned geometry is disposed exactly once,
including cancellation between promise continuations. Active rejection retains
its original load error; canceled queued work retains its cancellation error.
Other owners remain independent and continue as active slots retire.

Failed preparation batches dispose their new reserved, prepared and late
resources without committing over the previous model or camera. Commit routes
recheck disposal after aggregate preparation, before model or marking attachment.
Handle disposal also covers pending reload trees and runtimes starting after
disposal; readiness cannot trigger post-disposal posing or flexible allocations.
Cleanup is idempotent. Admission controls transport lifetime, never expression
scope or document numeric semantics.

Changing the private budget requires recorded actual-browser evidence, not a
guessed tuning sweep. Four is the accepted implementation candidate's measured
choice, not a claim that every browser has the same capacity or throughput.

## Alternatives considered

- **Unrestricted fan-out:** rejected by the 290-resource-failure printer run.
- **Per-node or per-mount budgets:** do not bound recursive trees or simultaneous
  old/new trees and viewers; the shared bundle queue covers those overlaps.
- **Permanent byte/geometry caching or retries:** introduce freshness and mutable
  ownership changes beyond the observed admission failure; not required here.
- **Early slot release on disposal:** would exceed the actual pending-request
  budget while non-abortable active loads still run.
- **Raising expression capacity or pruning the export:** neither fixes this
  transport failure and both evade the complete unchanged assembly gate.
- **A public concurrency option:** unnecessary to this demonstrated correction;
  it would broaden the host contract without originating evidence.

## Consequences and validation

Queued work trades some initial parallelism for bounded active geometry groups.
A disposed active owner can delay admission until its real request settles;
that is honest accounting, not an unbounded cancellation claim. Parsed geometry
and scene resources remain owner-local, while transient queue state is shared.

Counted tests changed 18 immediately started/peak 18 loads to four started/peak
four with all 18 completed. Retained red-first regressions cover abandoned FIFO
priority, microtask result leaks and late artifact attachment. Larger-than-budget
real-browser tests preserve exact completion-order pixels and simultaneous-owner
independence. The unchanged printer's final production-bundle gate records all
1,568 responses HTTP 200, all 1,565 models, zero request/page/HTTP errors and peak
four; the host verifies full node/model counts, finite bounds, declared
rest/Home/Center/Present/restored states and independent published-document
rigid/flexible geometry, followed by full reload checks.

[Implementation evidence](../../../openspec/changes/archive/2026-10-05-mount-voron-export/evidence.md)
and [parent acceptance](../../../openspec/changes/archive/2026-10-05-mount-voron-export/parent-review.md)
retain exact hashes, environment, full-suite results and cleanup. The full-page
probe's five-second graceful browser-close timeout remains recorded; bounded
owned-group termination leaves no survivors, not proof of graceful closure.
The supplemental small-test Chromium completed-body observation qualification
is test-only; the full-printer zero-request-error gate remains strict.

The separate web-capture fetch diagnosis and intended CoreXY signed-wrap geometry
defect remain open. Browser/published-document parity is not physical printer
qualification, and these measured runs are not a universal memory/performance
or cross-browser guarantee. The parent reviewed this complete ADR text after
the actual Voron adversarial acceptance and accepted it under the pilot's
advance authority on 5 October 2026.
