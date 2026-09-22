## Context

The originating Curta graph and read-only executor traces are recorded in
`evidence.md`. The same first lever moves from -4.2 to 0 in six-, seven-, and
eleven-station graphs. `_Block.increments` passes only each predecessor's
piece-total increment to a downstream law. The downstream law therefore sees
a linear ramp, not the predecessor's timed motion, including its dwell and
landing. Later stations introduce selector cuts and change those artificial
ramps. Injecting the seventh station's cut into the six-station graph alone
reproduces its loss exactly.

There is a second endpoint handoff at the block boundary: the upstream ones
shaft is supplied as total motion over the whole request, and restricted by
linear interpolation on every selector piece. Correcting only the lever-to-
tens handoff would retain this upstream timing loss. The dependency cone that
feeds the carry, not merely the SCC's internal edges, bounds this proposal.

The current simulation spec simultaneously prescribes endpoint-increment
handoff and promises partition agreement. This proposal changes the former,
explicitly, to serve the latter. ADR-107 jump removal, ADR-121 self-read walks,
ADR-122 selected ordering, ADR-124 tick-scoped evaluation and ADR-136 relative
contacts remain constraints, not licenses to approximate them differently.

## Goals / Non-Goals

Goals: preserve physical source timing through the selected carry chain;
make the unchanged Curta bulk request succeed with all result stations and
the original contact observation; retain transactional execution and replay;
preserve exact affine behavior while correcting timing in affected ordinary
chains as well as selected blocks. The pilot approved this expanded scope
after the measured frozen-twin conflict in `apply-findings.md`.

Non-goals: a general coupled/ODE solver, another tolerance, fixed microsteps,
new authoring declarations, modifying Curta's laws or default operating model,
whole-machine acceptance, viewer implementation, or publishing a release.

## Decisions

### 1. Compose motion paths, not endpoint chords

Represent demanded determined coordinates internally as tick-local paths over
the original request fraction. Inputs retain the commanded linear path; a held
coordinate retains its constant path. A driven coordinate's path is its banked
start plus its law's integrated motion along the paths of its active sources,
with the existing jump subtraction and self-read landing semantics.

Locate selectors using those source paths, order each selected piece as today,
and let a downstream member read its predecessor's path restricted to that
piece. Restriction must not construct a new chord or re-time a landing. A
switched-out dependency remains held and cannot cause recursion. A genuinely
active cycle still refuses transactionally; there is no iterative fixed point.

Reuse existing expression, crossing and walk machinery, extending their source
evaluation seam where necessary. Carry exact piecewise-affine segments and
their event positions where available; retain the existing bounded crossing
search for other supported expressions. Event boundaries belong to the common
request coordinate so restriction does not introduce a new tolerance. Reuse
evaluations only within the request/tick and distinguish forced branches,
restriction interval and starting bank. Querying a path must be pure, not advance
the live bank or duplicate history records.

Materialize trajectories for demanded sources in affected ordinary chains as
well as selected blocks. Preserve the existing affine fast path where it is
exact, not the blanket promise to preserve every no-block result and cost:
the existing frozen Curta carry also loses timing and must be corrected. Stop
location, admitted travel, crossing records and final banking must consult the
same path; do not repair only final endpoints while leaving contact probes on
the old trajectory.

Alternative rejected: omit unrelated selector cuts or partition each member
independently while retaining endpoint ramps. That could make six and seven
agree on an accidental answer but does not restore physical timing or the
one-tick/many-tick contract. Also rejected: subdividing pilot commands, shrinking
`dt`, or introducing a fixed internal sampling schedule as the correctness fix.

### 2. Keep the physical oracle outside the implementation

First add a small CAD-free framework regression for a landed/dwelling source
feeding a gated successor, with and without an otherwise irrelevant selector
cut. Include a nonlinear/piecewise upstream source outside the block, to expose
both handoffs. Prove red on the recorded base. The fixture must use the public
machine declarations; internal cut injection remains diagnosis, not acceptance.

Require the existing ordinary FixedZero carry and its selected twin to give
3.5 rather than 2 for one crank 0..4 request, agreeing with their partitioned
runs. Then require the unchanged project regressions at six, seven and eleven
stations, including the constrained eleven-station request. The expected tens
position stays `-16 + 9*72 + 72 = 704`. One successful prefix is insufficient;
so is agreement between two equally wrong executions. Compare full banks,
command statuses, admitted travel and discrete readings, not just tens.

The current trace establishes the failure mechanism, not that a proposed path
implementation already passes. If implementation cannot preserve these laws
without a broader architecture or a changed physical oracle, stop and return
the evidence to the pilot; do not relax acceptance.

### 3. Treat consumer parity as a repository boundary

The viewer independently executes published laws. Its measured result of 2
instead of 3.5 on the corrected producer's compact export confirms the same
defect. Independent viewer change `preserve-running-source-timing` owns its
implementation and API 24/v1–11 capability; this change owns producer exports.
The pilot's autonomous evidence-led direction authorizes this amendment.

Emit document v11 for every newly exported running program, including ordinary,
selected, Play and time-drive programs. Keep posed/looping and clocked versions
unchanged. No field or expression syntax changes: this is a semantic version
gate, like the self-read and selected-order gates before it. API 24 alone
cannot protect exports: old consumers do not read a required API from the
document, and the producer checks the consumer's documentVersions. An old
viewer must reject v11 before operation. Conservative running-wide selection
avoids inventing a static detector of which graph might need source timing.

Include `source-timing version=11` in the running program's canonical identity
listing. This intentionally supersedes prior identity/byte-preservation
promises for newly compiled running programs, including unaffected affine
ones: restoring an endpoint-era bank into corrected semantics must refuse
before mutation. Legacy exports remain readable by the corrected viewer, with
corrected physics; an already exported old file cannot retroactively prevent
an old consumer from executing its old bug. Re-export is the migration.

Generate provenance-labelled compact and unchanged Curta diagnostic exports
and records here. Viewer tests consume committed JSON copies without importing
the framework. Keep existing corpus bytes as controls; classify changed exact
expectations against physical evidence rather than regenerate them wholesale.
Do not claim parity, integrate or adopt either worktree until the pair passes.

## Risks / Trade-offs

- Path composition may multiply evaluation cost → memoize demanded tick-local
  paths, measure six/seven/eleven stations and replay/stop probes; do not use
  endpoint approximation to hide a performance regression.
- Existing tests may encode endpoint-chord behavior → classify failures against
  physical expectations and accepted contracts, never regenerate goldens just
  to pass. A conflicting consequential behavior returns to the pilot.
- Near-coincident events can change branch ownership → retain current tolerance
  and boundary rules, test forward/reverse travel and landing followed by motion.
- Geometry and arithmetic trials are independent evidence → neither a native
  clearance pass nor the collar trial proves this executor fix or authorizes
  adopting a new operating model.
- A viewer fix may be necessary → hold integration and export compatibility
  claims until its owner-scoped work is explicitly resolved.

## Migration Plan

Ratify this planning state before implementation; validate and make planning
commit 1 on the isolated branch. Implement red-first without intermediate
implementation commits. After proof, document the accepted architecture in a
new ADR superseding only the affected handoff decision, synchronize the spec,
archive and make completion commit 2. Primary integration needs separate pilot
authority and a fresh state check; the unrelated untracked primary directory
remains untouched. Until integration, rollback is simply not adopting this
isolated branch. No project source migration is planned.

## Open Questions

- Which existing path primitives can carry restricted source trajectories with
  the least extension, and what is the measured cost? Resolve under the ratified
  design with red-first tests; a materially different solver needs re-ratification.
- API 24/v11 and source-timing snapshot identity are now chosen; paired tests,
  old-consumer refusal and provenance remain evidence gates before adoption.
