# Viewer parity gate resolved in isolated worktrees

The initial mismatch below led to independently owned viewer change
`preserve-running-source-timing` under the pilot's autonomous direction.
The paired API-24/v11 producer and consumer pass compact, full Curta and
real-browser worker/fallback proof. See [completion-evidence.md](completion-evidence.md)
and [the exact paired hashes](evidence/paired-source-timing.json).
Integration and project adoption remain separate, not implied by parity.

## Historical initial finding (before viewer authorization)

2026-09-22. Read-only check against independent viewer HEAD
`c8da56e77f7653a06b335459e7759c6b24152e69`. Its worktree was clean before
inspection and remains untouched. This framework cycle does not authorize
viewer implementation, a capability change, or integration.

## Measured mismatch

The existing framework `tests.carriage_project.machine.ShiftedCarry` was
compiled with the existing `tests.test_running_document.document` helper.
The same document was passed to the viewer's `Engine.load` with `dt=.1`,
`record=32`; both engines received one `move('crank', to=4)` request.
The viewer's TypeScript engine was bundled with its installed esbuild into
memory and evaluated in Node; no bundle or source file was written anywhere.

| Coordinate | Candidate Python | Current viewer |
| --- | ---: | ---: |
| crank | 4 | 4 |
| lower.turn | 4 | 4 |
| carry.travel | 1 | 1 |
| higher.turn | 3.5 | 2 |
| clearing | 0 | 0 |
| shift | 0 | 0 |

The viewer reports `completed`, admitting 4. This is a behavioral disagreement
on identical published laws, not a loading error or a new document field.
Its `widget/src/run/jumps.ts` block handoff and `run/edges.ts` ordinary handoff
still supply endpoint increments, consistent with this result. The committed
old corpus passes in Python; it does not cover this bulk landed-source case.

## Separate owner-scoped proposal required

Ask the pilot to authorize a viewer-owned proposal for timed-source propagation
in its selected and affected ordinary chains, matching Python's jump removal,
landing, crossing-boundary, stop/contact, and replay behavior. Use the compact
landed/curved-source fixtures and unchanged Curta requests as parity evidence;
add agreed fixtures rather than regenerating old goldens to hide differences.
Keep Play's clearance-aware executor intact unless separately justified.

The proposal must settle how corrected runtime semantics are identified and
paired at export/load time. Do not assume unchanged syntax means an old viewer
is compatible, or invent a capability/version field in this framework cycle.
No AGPL viewer implementation belongs in the Apache framework repository.

Until that decision and parity proof, hold framework integration, export
compatibility claims, and adoption into the originating project's default
operating model. Framework completion records also remain unfinished here;
no ADR promotion, spec synchronization, archival, or completion commit yet.
