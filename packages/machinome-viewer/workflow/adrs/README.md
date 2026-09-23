# Architecture Decision Records

This directory is solid-node-viewer's decision log. Each ADR records one
architectural decision — its context, the options weighed, and its
consequences — as a delta against the architecture that existed before it.
The behavioural contracts live in [`openspec/specs/`](../../openspec/specs/).

## Provenance

The viewer was designed and built inside the solid-node framework, and its
decisions were recorded in the framework's log under the framework's
numbering. When the viewer became this package (see
`openspec/changes/archive/2026-09-05-found-standalone-viewer-package/`), the
viewer-owned records were relocated here **unchanged**, keeping their
original numbers so a citation such as "ADR-035" means the same thing in
both repositories. Consequences:

- The numbers below are not contiguous and do not start at 001; a new ADR
  in this repository continues from the highest number here.
- Code paths inside these records are the framework's at the time of the
  decision (`solid_node/viewers/widget/…`); today the same files live under
  `solid_node_viewer/`.
- Links into records that stayed with the framework — the build pipeline,
  the FastAPI stack, the shared document schema — point at solid-node's
  repository. The decision that split the two packages is itself recorded in
  solid-node's log, beside the `optional-viewer-package` change.

## Discipline

- **One decision per ADR**, numbered sequentially, filed under the subsystem
  directory it primarily affects.
- **Statuses:** `Proposed` → `Accepted`; later decisions may mark an ADR
  `Superseded` (with a *Superseded by* link) or amend it in place with a
  dated *Amendment* section. Superseded ADRs stay in the log.
- The normal flow is an OpenSpec change ratified *before* implementation,
  with the ADR written alongside and linked from the archived change.

## Index

### VIEWER-WEB — development server and app
- [ADR-012](VIEWER-WEB/ADR-012-threejs-for-3d-rendering.md) — Three.js rendering — **Accepted**
- [ADR-013](VIEWER-WEB/ADR-013-react-frontend-framework.md) — React frontend — **Superseded** by 052
- [ADR-014](VIEWER-WEB/ADR-014-recursive-nodeapi-rest-pattern.md) — Recursive NodeAPI REST pattern — **Superseded** by 036
- [ADR-027](VIEWER-WEB/ADR-027-absolute-matrix-composition-for-viewer-transforms.md) — Absolute world-matrix viewer transforms — **Superseded** by 036
- [ADR-036](VIEWER-WEB/ADR-036-snapshot-served-shared-viewer-shell.md) — Snapshot-served shared viewer shell — **Accepted**, amended by 052
- [ADR-037](VIEWER-WEB/ADR-037-targeted-in-place-viewer-updates.md) — Targeted in-place viewer updates — **Accepted**
- [ADR-052](VIEWER-WEB/ADR-052-the-development-page-is-static.md) — The development page is a static page over the bundle — **Accepted**, supersedes 013, amends 036

### EXPORT — the widget and its host API
- [ADR-020](EXPORT/ADR-020-static-export-and-embeddable-viewer-widget.md) — Static export and embeddable widget — **Accepted**
- [ADR-035](EXPORT/ADR-035-reusable-viewer-core-and-declared-api.md) — Reusable viewer core and declared API version — **Accepted**
- [ADR-042](EXPORT/ADR-042-host-controlled-viewer-assembly-navigation.md) — Host-controlled viewer assembly navigation — **Accepted**
- [ADR-043](EXPORT/ADR-043-hash-consed-expression-evaluation.md) — Hash-consed expression evaluation — **Accepted**
- [ADR-044](EXPORT/ADR-044-a-binding-name-resolves-into-the-shared-dag.md) — A binding name resolves into the shared DAG — **Accepted**
- [ADR-045](EXPORT/ADR-045-the-run-executes-in-a-worker.md) — The run executes in a worker and the main thread only poses — **Accepted**
- [ADR-046](EXPORT/ADR-046-a-committed-bank-is-a-name-in-the-same-scope.md) — A committed bank is a name in the same scope as a driver — **Accepted**
- [ADR-047](EXPORT/ADR-047-the-corpus-makes-the-two-runtimes-one-algorithm.md) — The corpus is what makes the two runtimes one algorithm — **Accepted**
- [ADR-048](EXPORT/ADR-048-running-controls-submit-requests.md) — Running controls submit requests; nothing binds back — **Accepted**
- [ADR-049](EXPORT/ADR-049-the-viewer-publishes-its-navigation-state.md) — The viewer publishes its assembly navigation state — **Accepted**, amends 042
- [ADR-050](EXPORT/ADR-050-the-navigator-is-a-component-of-the-viewer.md) — The assembly navigator is a component of the viewer package — **Accepted**, amends 042
- [ADR-051](EXPORT/ADR-051-the-bundle-ships-an-inspector-layout.md) — The bundle ships an inspector layout, and the page selects it — **Accepted**, extends 050
- [ADR-053](EXPORT/ADR-053-a-pick-is-bound-to-a-declared-control.md) — A pick is bound to a declared control, and the part follows commits — **Accepted**, extends 048, consumes solid-node ADR-112
- [ADR-054](EXPORT/ADR-054-a-constraint-is-derived-from-the-published-document.md) — A constraint is derived from the published document, never published — **Accepted**, amended by 069, extends 045 and 047, consumes solid-node ADR-113
- [ADR-056](EXPORT/ADR-056-a-marking-is-a-decal-in-the-parts-own-group.md) — A marking is a decal mesh in the part's own group, and the bias over the surface is the viewer's — **Accepted**, extends 035, consumes solid-node ADR-120
- [ADR-057](EXPORT/ADR-057-a-self-read-edge-is-executed-from-the-retained-value.md) — A self-read edge is executed from the retained value, piece by piece — **Accepted**, extends 045 and 047, builds on 054, consumes solid-node ADR-121
- [ADR-058](EXPORT/ADR-058-a-block-is-ordered-per-piece-from-the-published-edges.md) — A block is ordered per piece from the published edges — **Accepted**, extends 045 and 047, builds on 057, consumes solid-node ADR-122
- [ADR-059](EXPORT/ADR-059-the-viewer-keeps-its-own-bundle-current.md) — The viewer keeps its own bundle current, and refuses what it cannot repair — **Accepted**
- [ADR-060](EXPORT/ADR-060-only-what-moves-along-a-step-s-path-is-walked.md) — Only what moves along a step's path is walked — **Accepted**, extends 043 and 046, builds on 047, 057 and 058, consumes solid-node ADR-124
- [ADR-061](EXPORT/ADR-061-a-kink-is-a-cut-in-the-viewer-too.md) — A kink is a cut in the viewer too, and the viewer derives the shape itself — **Accepted**, extends 045 and 046, builds on 047, 057, 058 and 060, consumes solid-node ADR-123
- [ADR-062](EXPORT/ADR-062-the-viewer-executes-a-clocked-machine-in-thread.md) — The viewer executes a clocked machine in thread, and a declared stop clips the request before any event — **Accepted**, extends 045 and 047, builds on 054, 057, 058, 060 and 061, consumes solid-node ADR-125, ADR-126 and ADR-128
- [ADR-063](EXPORT/ADR-063-the-clock-is-an-input-and-a-frame-advances-it.md) — The clock is an input a request moves, and one rendered frame is one request — **Accepted**, extends 062, builds on 045, 046, 047 and 048, consumes solid-node ADR-127 and ADR-128
- [ADR-064](EXPORT/ADR-064-a-clocked-instruction-is-one-request-drawn-over-its-duration.md) — A clocked instruction is one request, drawn over its duration — **Accepted**, amends 062, extends 063, builds on 045, 047 and 048, consumes solid-node ADR-129
- [ADR-065](EXPORT/ADR-065-every-request-the-clocked-panel-makes-is-drawn.md) — Every request the clocked panel makes is drawn, over a duration of the viewer's own — **Accepted**, amends 064, extends 062 and 063
- [ADR-066](EXPORT/ADR-066-the-viewer-host-contract-adopts-machinome.md) — The viewer host contract adopts Machinome — **Accepted**
- [ADR-067](EXPORT/ADR-067-a-play-edge-retains-contact-history-in-the-running-bank.md) — A play edge retains contact history in the running bank — **Accepted**, extends 045 and 047, builds on 054, consumes machinome ADR-130
- [ADR-068](EXPORT/ADR-068-time-drives-admit-independent-motion-without-bank-state.md) — Time drives admit independent motion without bank state — **Accepted**, extends 045 and 047, preserves 067, consumes machinome ADR-133
- [ADR-069](EXPORT/ADR-069-moving-stops-attribute-push-at-first-contact.md) — Moving stops attribute push at first contact — **Accepted**, amends 054, preserves 047 and 068, consumes machinome ADR-135
- [ADR-070](EXPORT/ADR-070-moving-contacts-use-relative-crossings.md) — Moving contacts use relative crossings with exact following-contact certificates — **Accepted**, amends 057, preserves 047/060/069, consumes machinome ADR-136

- [ADR-071](EXPORT/ADR-071-determined-sources-retain-their-motion-path.md) — Determined sources retain timing through running dependencies — **Accepted**, amends 058/061, preserves 057/060/067/070
- [ADR-072](EXPORT/ADR-072-source-timing-is-declared-as-api24-and-v11.md) — API 24 and v11 declare corrected source timing — **Accepted**, extends 035/047
- [ADR-073](EXPORT/ADR-073-a-gesture-is-drawn-at-the-declared-tempo.md) — A gesture is drawn at the tempo its input's declared instruction states — **Accepted**, amends 065, extends 064
- [ADR-074](EXPORT/ADR-074-a-path-piece-reuses-unchanged-bound-nodes.md) — A path piece reuses unchanged bound nodes — **Accepted**, amends 060
- [ADR-075](EXPORT/ADR-075-two-moving-envelopes-retain-a-free-follower.md) — Two moving envelopes retain a free follower — **Accepted**, extends 067, builds on 054/061
