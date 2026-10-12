## Context

Ratified for implementation by the pilot on 2026-09-22 (see proposal).
Read `evidence.md` for the pinned Curta failure.
ADR-043 establishes a page-scoped hash-consed DAG with cache reclamation;
ADR-044 adds generation-aware document-local binding roots. Both promise
that reclamation cannot change evaluation results.

At viewer commit `1995aa1`, `prepare()` resets the entire store before a
new expression when the node count reaches 50,000. Its comment assumes one
document cannot reach that threshold. `BindingTable.roots()` prepares all
entries sequentially and stamps the finished map with the final generation,
without detecting resets within that preparation. In `run/program.ts`,
`classify()` obtains a root, then the binding map, then traverses both.
The real Curta document changes generation between those two acquisitions.
An old integer can name either no node or a different node after reset.
Checking whether that integer exists is therefore insufficient.

The existing single-entry reset test covers a reset BETWEEN uses, not
within a complete binding-table preparation or a root-plus-table operation.
Classification also retains kink-level node references; fixing only the
observed call order would leave their lifetime unproved.

## Goals / Non-Goals

Goals: open and operate the originating Curta document correctly; make
preparation and use generation-coherent; preserve page-scoped sharing,
document-local bindings and reclamation across repeated publications.

Non-goals: Python speedups, a new expression grammar or document format,
changes to contact mathematics, higher cache limits as the fix, viewer UI
changes, adoption of the Curta trial into its production model, or release.

## Decisions

### 1. Protect a complete preparation-and-use operation

Introduce an internal, nestable synchronous expression-store scope. A
reclamation requested by the existing threshold is performed only at a
safe outer boundary, before roots are acquired, never while a consumer
holds node IDs for that operation. Always release the scope in `finally`.
Binding-map construction and acquisition of the expression root it is
used with belong to the SAME scope, including classification and traversal.
Memo arrays and binding maps remain generation-qualified.

The threshold remains a reclamation trigger, not a maximum supported model
size. A single operation may need more nodes than that trigger. Do not
retry preparation until it happens to fit: a larger working set could
otherwise reset forever. Do not suppress resets for an entire mounted
session: that would retain obsolete publication history indefinitely.

### 2. Audit every retained node reference at the boundary

Before implementation, inventory holders in expression evaluation, binding
maps, program root caches, kink levels, path values, clocked execution and
posing. A holder that outlives a scope must retain reconstructible source
and its generation, and rebuild derived IDs inside the next coherent scope
before use. Derived shapes can remain cached only where they contain no
store IDs; kink operands cannot be assumed generation-independent.

No raw reference may escape under the assumption that a later caller will
probably prepare the same nodes in the same order. Test reuse of an index
by a DIFFERENT node, not only a missing index. Keep reset ownership in the
expression subsystem rather than duplicating ad-hoc reset logic at each
consumer. No public host API is introduced.

This preserves the shared DAG architecture. A per-document DAG, permanent
pinning of all historic generations, and a raised/disabled node ceiling
are rejected as broader changes or failures to preserve reclamation.
If the reference audit makes this scoped repair insufficient, return the
specific evidence and revised design for approval before changing ownership
architecture.

### 3. Acceptance proves correctness AND reclamation

Use the existing mutable test-only threshold for small deterministic
fixtures. Prove red first for reset during multi-entry roots construction,
root-before-bindings classification, and retained references after a later
reset. Test a working set larger than the threshold without hangs, missing
nodes, wrong values, or changed shape/kink results. A warm unrelated cache
must not change results. Multiple documents must retain their own bindings.

Measure retained node counts over repeated alternating publications and
failed preparations: after reclamation, count is bounded by the current
working set plus threshold headroom, not the number of past publications.
Final disposal must still release all expression state. Exception tests
must show no leaked scope that disables future reclamation.

Replay existing numeric, running and clocked conformance fixtures without
changing expected outputs. Test the real exported Curta through the built,
uninstrumented bundle: mount, initial/idle state, the existing hundreds and
eighth-station blocked requests, relief/retry and full 213-coordinate bank
comparison wherever the Python oracle is captured. Capture and inspect
pixels after successful mount; screenshots alone do not prove parity.

Viewer regression fixtures are self-contained and must not import the
framework. Keep a small committed synthetic regression here and use the
project-owned full export as cross-repository acceptance evidence; record
its hash and exact command. Any copied project artifact needs provenance
and license review before entering this repository.

## Risks / Trade-offs

- Larger live working sets require memory above the threshold → report peak
  node counts and bound history retention separately; do not claim a hard
  50,000-node memory limit or arbitrary-size support.
- Re-preparation can be expensive → record Curta mount and first-step times,
  but no speedup target or unrelated optimization belongs in this repair.
- A scope applied too narrowly leaves stale derived IDs → holder inventory,
  generation-pressure tests and both execution paths are acceptance gates.
- A scope applied too broadly defeats reclamation → repeated publication,
  failure-cleanup and disposal tests are mandatory.
- A later Curta acceptance failure may be independent → report it separately;
  do not weaken mechanics or silently expand the change to make it pass.

## Migration Plan

After pilot approval, commit the ratified planning record, establish failing
tests, implement the scoped repair, build and test the package, then run
Curta acceptance. Amend ADR-043/044 only to explain the corrected lifetime
boundary, sync the accepted delta and archive only after all gates pass.
No migration, API version change or document rewrite is expected. Keep a
focused implementation commit so it can be reverted if validation regresses.
Do not integrate, publish or push without the pilot's required authority.

## Open Questions

No additional product choice is required to review this proposal. The
node-reference inventory and memory measurements are implementation gates,
not evidence already collected. A materially different lifetime architecture
requires a revised proposal and renewed approval.
