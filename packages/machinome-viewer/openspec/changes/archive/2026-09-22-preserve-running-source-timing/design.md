## Context

The originating project is Curta Type I 3x, checkpoint `8852677` on
`direct-operation`. Framework change `preserve-carry-across-graph-expansion`
now passes its unchanged six/seven/eleven-station and constrained regressions:
crank 180, ones 724, tens 704, first lever 0. The current viewer instead gives
2 rather than 3.5 on the existing ShiftedCarry export for one crank 0..4
request, with completed status and all 4 units admitted. This is the same
source-timing defect, not a missing command or a transport failure.

Read ADR-047's producer-owned corpus, ADR-054's derived constraints,
ADR-057's retained walk and ADR-058's selected blocks alongside their current
specifications. Their endpoint handoffs and blanket ordinary-chain preservation
conflict with the measured partition agreement. Only those decisions change;
the published edge order, active-dependency proof, retained landing and atomic
commit remain binding.

## Goals / Non-Goals

Goals: parity with the exact tested producer content, including timed ordinary
sources upstream of a block; one shared engine for worker and fallback;
observable old-consumer refusal for corrected exports; practical measured cost.

Non-goals: an ODE/coupled solver, a new tolerance, microstepping for correctness,
Curta-specific arithmetic, changing project laws or constraints, generalized
Play topology, a new parser, changes to clocked machines, publication, or a
whole-machine geometry acceptance claim.

## Decisions

### Preserve determined paths

Mirror the verified producer algorithm in viewer-owned TypeScript. A propagation
keeps deltas plus request-local motion evaluators, exact affine pieces where
proved and expression evaluators for curves. Restriction retains physical
timing; it never draws a new chord through the endpoints. Branches are forced
once per selector piece, inactive dependencies hold, and an actual active
cycle refuses atomically. Expose the existing retained walk's actual pieces
rather than approximating a walk by rerunning it at fixed sample times.

Classify affinity with current branch values and standing sources, through
bindings and the existing expression DAG. A compile-time affinity flag alone
does not certify a path through a nonlinear predecessor. Conversely, inactive
nonlinear terms must not make constant paths expensive curves. Cache only
within one request/segment; queries cannot advance the bank or append history.
An internal source boundary belongs to its preceding interval for crossing
recording. Keep whole-request crossing limits and existing float rules.

Ranges and contact samples read the same determined paths where available.
Candidate-only attribution still uses a fresh propagation. Preserve the
tick-start own argument in moving bounds and the first-contact bracket.
Play and every downstream observer stay on their existing clearance-aware
prefix replay, not an inferred affine path made from a net displacement.

Rejected: deleting irrelevant cuts while retaining endpoint chords; fixed
microsteps; changing the oracle; a second expression evaluator; a solver only
for selected blocks that disagrees with the same laws in an ordinary chain.

### Gate corrected exports with the existing document version

Use viewer API 24 and document v11, extending supported versions to 1–11.
The paired producer amendment will emit v11 for newly exported running roots
(ordinary, selected, Play and explicit-time programs), leaving posed/looping
and clocked schemas alone. This intentionally conservative selection avoids
a new speculative static analysis deciding which ordinary graph might need
source timing. No new key is needed: the version declares execution semantics,
as v6 and v7 already did. V11 validates time-drive mappings when present and
refuses clock reads with missing mappings; absence is valid for driver-only
programs. Current v10 validation remains intact for legacy documents.

The corrected viewer accepts legacy running documents and applies corrected
physics too; do not preserve the old defect behind a version branch. Exact
affine behavior and old corpus cases remain controls. A raw old document cannot
retroactively tell an old viewer about this fix; document that limitation.
Re-exporting from the corrected producer makes the compatibility requirement
portable. A current old viewer rejects v11 before mounting; a host may also
check API 24 before mounting. Snapshot identity/version compatibility must be
verified on the producer side, not inferred from unchanged law text.

Rejected: API 24 alone (the model carries no required API and the current
producer's export compatibility check only asks documentVersions); a new
minimum-API field (old viewers would ignore it); silently keeping v7 for a
program known to execute incorrectly in its old consumer.

This compatibility choice and fixture generation require an explicit amendment
of the existing framework change under its own workflow. The pilot's autonomous
empirical-work direction authorizes that follow-through; this viewer record
does not itself mutate or ratify a producer baseline. Keep both worktrees
unintegrated until the pair passes.

### Prove the algorithm and its browser use

Commit producer-generated, provenance-labelled JSON fixtures; viewer tests
import no framework or project modules. Keep the old corpus byte-identical
unless a measured physical correction requires a separately recorded producer
update. Compact fixtures cover landed, piecewise/curved upstream, irrelevant
later selector, ordinary frozen twin, range and contact probes, reverse,
restore and crossing-at-source-boundary. Compare every bank, command outcome,
admission, crossing and stop within the producer's published rules.

Export the unchanged project diagnostic programs and record six/seven/eleven
and constrained full-bank results. Run bulk and partitioned requests from the
same snapshot. Exercise a project export in Chromium through worker and
in-thread fallback and inspect pixels, without presenting a diagnostic bank as
a complete physical-machine validation. Record timings and bundle size; a
slow accurate run is not a real-time claim.

## Risks / Trade-offs

- Path closures can multiply work or retain memory → classify active pieces,
  cache within a propagation only, test replay lifetime and measure Curta.
- Boundary reassociation can change landings → shared producer fixtures,
  exact discrete records and unchanged tolerances, red-first edge cases.
- Existing fixtures may encode the defect → classify each failure against
  physical evidence; do not bless new goldens wholesale.
- v11 is cross-repository → producer amendment and old-consumer refusal proof
  precede adoption. Metadata advertises support only with passing implementation.
- Main README/changelog claim a later release than the supplied shop status →
  do not rewrite release history or infer publication authority; this change is
  explicitly unintegrated and unreleased throughout development.

## Migration Plan

Record/validate planning, implement red-first in this worktree, amend producer
compatibility independently, pin fixture provenance and test the pair. Extract
only implementation-confirmed ADR amendments, sync and archive completed
records locally. Integration and any dirty primary files must be accounted for
without absorbing or deleting unrelated work. No push or release.

## Open Questions

Implementation evidence determines exact DAG path plumbing and performance.
Any correction found in either runtime is recorded in its owning change and
proved red/green; the pilot has asked for continued autonomous progress rather
than per-issue approval stops.
