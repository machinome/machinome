# ADR-082: One reading of a model file is one geometry, held by count

**Status:** Accepted

**Date:** 2026-11-22

**Change:** [share-one-geometry-per-model-file](../../../openspec/changes/archive/2026-11-22-share-one-geometry-per-model-file/)

**Amends:** [ADR-078: Geometry admission is shared, and resources keep their owner](ADR-078-geometry-admission-is-shared-and-resources-keep-their-owner.md)
(its "each subscriber owns its own STLLoader parse, mutable geometry and
material", "Admitted subscribers use the real STLLoader and existing
normal/marking preparation", "Late or abandoned returned geometry is
disposed exactly once", and its consequence "Parsed geometry and scene
resources remain owner-local")

**Builds on:** [ADR-076: A part's presented look has one owner](ADR-076-a-parts-presented-look-has-one-owner.md)
(one holder of the materials per viewer, which is what tells one viewer
from another here),
[ADR-056: A marking is a decal in the part's own group](ADR-056-a-marking-is-a-decal-in-the-parts-own-group.md)
(a decal's geometry is its own, lifted from the file's)

## Context

One open copy of the Enigma I page was 4,214 MiB in Chromium, and 3,207 of
it was the model's triangles held twice: 1,603 MiB of typed arrays in the
tab and the same bytes again as WebGL buffers. The 2,868 parts read from
model files were 1,110 MiB of each 1,603. No geometry was used by more
than one mesh, and those parts name 993 files: 16.2 million triangles were
held where 7.8 million are distinct. One lamp cap of 118,850 triangles was
held 26 times.

ADR-078 had made the admission of requests shared and left everything
else with each subscriber: the file was fetched once, because three.js
folds overlapping requests for one URL, and parsed once a part. It set a
cache aside for freshness and for "mutable ownership changes beyond the
observed admission failure". The pilot asked where the page's memory goes,
then what one geometry a file would cost and how a changed file would be
handled, and ordered it.

## Decision

**A reading of a model file is one request and one parse, and within one
viewer every part and marking that joins it is drawn from its one
geometry, which each holds by a share and which is freed when the last
share is let go.**

1. **One reading per admission group.** The group ADR-078 defined for one
   URL sends one request through three.js's `STLLoader`, parses once and
   computes the normals once, before any part has the geometry.
2. **Joined while its request has not settled.** A load joins the open
   reading of its URL whatever update it belongs to, exactly when it could
   join a group before; the reading closes in the first reaction to its
   request's settlement. Nothing outlives a request: there is no table of
   geometries, no part joins a geometry already on screen, and ADR-078's
   "no permanent STL cache, geometry substitution" stands.
3. **A holding per viewer.** Within a reading the first viewer to take it
   is given the parse and each further viewer a copy. three.js keeps, per
   renderer, the buffers of every geometry it drew and a listener on it,
   until that geometry is disposed; one geometry held by two viewers would
   keep a disposed viewer's buffers alive and would delete the other's
   when the first let go. A viewer is told from another by its holder of
   materials (ADR-076).
4. **Shares.** A load that is admitted gets a share of its viewer's
   holding. A share is let go exactly once, however often cleanup runs. A
   holding is freed exactly once, when no share of it is held and its
   reading has retired, that is, when every load that joined the reading
   has settled. A load whose owner was cancelled when the reading arrives
   is given no share; a parse no one took is freed when the reading
   retires, never uploaded. A reading's failure fails every load that
   joined it.
5. **A mesh lets go where it disposed.** A mesh that shows a file's
   geometry holds its share; disposing the mesh lets go of the share and
   leaves the geometry to its other holders. A geometry that is a mesh's
   own (a placeholder, a decal, a flexible part) is disposed as before.
6. **A marking** is lifted from the file's geometry into a geometry of its
   own, as before, and lets go of the file's at once.
7. **A replacement prepared for a node that was removed meanwhile is let
   go, not attached.** Attached to a group nothing shows, it would hold
   its share for ever.
8. **Nothing writes a part's geometry after it is handed out** but
   three.js's own caches of its bounds, which are the same for every
   holder.
9. **What stands from ADR-078:** the budget of four groups and its FIFO
   order, queued work cancelled without a request, the slot held until
   every subscriber settles, readiness waiting for every asset, the last
   good model after a failure, idempotent cleanup, and no option, retry,
   cache or version change.

**Which bytes a part is given does not change.** An update that asks for a
file while an earlier request for it is in flight is given that request's
result, before as a parse of its own of the folded response and now as the
same geometry. That an update begun after a file changed can thereby show
the file as it was is a finding of its own (`workflow/warts.md`, "An
update that asks for a file still being fetched is given the earlier
request's bytes"), neither closed nor widened here.

## Consequences

- A page whose parts repeat files holds and uploads each file once. Parts
  that name a file no other part names gain nothing, nor do flexible
  parts, which are built from their shapes.
- A republish that adds a part naming a file already on screen reads the
  file again and holds a second copy until the next mount or reload. It
  costs a development session what every part cost before.
- A second viewer of the same files holds a copy of each, as before.
- The order of drawing, the picture, picking and bounds are untouched:
  none of them reads which geometry object a mesh holds.
- The viewer API stays 30 and the document versions 1 to 14.

## Alternatives

- **Joinable until the viewer is told the file changed** (an artifact
  notice or a moved `mtime`): a table that outlives requests, which is the
  cache ADR-078 set aside; only as fresh as the signals that reach it, and
  a reload is told nothing; and `mtime` is per part, not per file. Its
  gain is the second copy of a development session.
- **A request of its own for every update,** never joining one sent before
  the update began: it corrects the staleness named above, which is not
  this decision's subject; it costs requests whenever updates overlap, two
  viewers mounting together included. Proposed with this change and
  struck in review; recorded as a finding.
- **One geometry across viewers:** point 3.
- **A parse per viewer instead of a copy:** the same memory, more work.
- **Sharing a lifted decal among markings of one file:** 3.2 MiB on the
  page, and a decal is the viewer's own derived geometry.

## Proof

Two widget test files that drive the real tree and the real viewer with
three.js's own STL loader and file loader over a stubbed network, counting
requests, parses, geometries, holders and disposals: sixty tests,
twenty-seven red before the change, the rest guards of what must not
move. Generated sequences of mounts, republishes, artifact updates,
rewritten files, failed answers, reloads and disposals (300 of 40 steps
on trees, 40 of 25 on two mounted viewers) with a detector after every
step: every mesh holds a geometry that is not disposed, the geometries
alive are exactly those some mesh holds, the counts agree, no part holds
another reading's geometry, and nothing is alive at the end. In Chromium:
the WebGL buffers created and deleted across a mount, an artifact update
and a disposal (8, then 6 and 6, then all 14 before; 4, then 2 and 2,
then all 6 after); pixels against the same document with a copy of the
bytes per part; two viewers, one disposed. Eleven designed mutations and
twenty-five faults planted in review turn named tests red or are shown
equivalent or unreachable; five stood on the tests as handed over and
four tests were written for them. One departure from the design was made
by the implementation and accepted in review (point 7).

**Measured** on the Enigma I page (`enigma-i` at `081f4e6`) in Chromium,
draw calls counted and not executed, one run of each build: one open copy
3,034 MiB where it was 4,217; the tab 1,578 MiB where it was 2,167, its
typed arrays 1,039.1 where they were 1,612.6; the graphics process 1,334
where it was 1,931; 1,472 geometries for the same 3,347 meshes (993 for the
2,868 parts read from files); 2,997 WebGL buffers of 1,029.9 MiB where
there were 6,747 of 1,603.4. The typed arrays and the buffers are each
573.5 MiB less, the figure the files' census gave. The peak while the page
loads 3,265 MiB where it was 4,343; while `reload()` holds the old and the
new model together, 4,581 where it was 6,286. After a reload the same
counts again, with every buffer of the old model deleted; after
`dispose()` no buffer alive. The same draw calls. The time from the click
to a ready page did not move beyond its own spread: 10.5 to 12.4 s over
four loads where the base took 11.7 to 13.3. Really drawn in software, in
sixteen states (the mount, the case, the flap, a wheel, a pressed key,
after a reload and in two poses after it, the model seen from behind, a
highlight in each of its three modes and put back, and parts hidden and
shown again): what is on screen equals a forced draw, and equals the
previous viewer's picture pixel for pixel, 29.5 million pixels over
thirty-four pictures. Not measured: any GPU, where the graphics
process's share lives in the card's memory; another browser.

[Design](../../../openspec/changes/archive/2026-11-22-share-one-geometry-per-model-file/design.md) and
[evidence](../../../openspec/changes/archive/2026-11-22-share-one-geometry-per-model-file/evidence.md)
record the cases, the tests and the measurements. The pilot was told
before integration of what this record decides beyond what they were told
when they ordered it.
