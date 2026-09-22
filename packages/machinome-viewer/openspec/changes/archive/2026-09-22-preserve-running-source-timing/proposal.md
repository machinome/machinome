## Why

Curta Type I's corrected Python carry reaches 3.5 in the compact landed-source
case while this viewer reaches 2 on the identical exported document. The full
eleven-station project now passes its unchanged bulk request in Python; it
needs browser execution that preserves the same source timing, rather than
silently restoring the endpoint-chord bug.

## What Changes

- Preserve physical source timing through selected blocks and affected ordinary
  running chains, including dwell, kink, landing and curved-source motion.
- Use those same paths for stops, contacts, crossing records and replay, retaining
  existing tolerances, transactional refusals and Play's clearance-aware path.
- **BREAKING:** correct old endpoint-approximation results on affected legacy
  running documents too; do not maintain a second, knowingly incorrect solver.
- Identify support as viewer API 24 and document versions 1–11. Version 11 is
  the producer-owned semantic gate for newly exported running programs; it
  prevents old viewers from accepting corrected exports with wrong arithmetic.
  No new document field or authoring syntax is proposed.
- Add producer-generated timing fixtures, unchanged Curta diagnostic replays,
  worker/fallback browser proof, and an old-viewer rejection check. Do not
  rewrite old corpus expectations merely to pass.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: source-timed integration, selected execution, stops and
  document-v11 compatibility with producer/browser parity evidence.
- `viewer-distribution`: consistent API 24 and v1–11 capability reporting.

## Impact

Viewer-owned TypeScript running engine, loader, fixtures/tests, capability
metadata and compatibility documentation. No framework imports, new solver,
fixed correctness microsteps, Play topology expansion or clocked behavior change.

Standalone viewer worktree `WTs/preserve-running-source-timing`, branch of the
same name, based on main `c8da56e77f7653a06b335459e7759c6b24152e69`.
The companion framework change is `preserve-carry-across-graph-expansion` on
base `e6a42c8`, planning commit `5f90739`, with an uncommitted tested candidate.
Producer v11 publication and fixture generation belong to a separately recorded
amendment in that framework worktree, not to this repository.

The pilot explicitly authorized autonomous evidence-led fixes on 2026-09-22,
replacing per-issue approval stops. This authorizes implementation and necessary
paired compatibility work, not push, publication or destructive cleanup.
Neither candidate is integrated at proposal creation. Existing unrelated viewer
changes and worktrees are preserved.
