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
