## Context

ADR-105 requires a running simulation to bind every joint coordinate through
`set_state` using its qualified bank ID, making the bank, slot and pose one
fact. The Curta Type I 3x operating model at checkpoint `1aaad6c` violates
that contract: moving the carrier to 20 degrees can leave a nested ring whose
bank is 0 degrees bound at 20, and moving the ring to -90 can leave it bound at
the ancestor's value. A geometry-free three-level reproduction proves that
mapping order, not Curta mechanics, chooses the wrong pose.

State delivery strips one qualified path segment per tree level. At each node,
`CoordinateDelivery` consumes entries naming that node's own coordinates, but
the child projection no longer knows whether a now-local `turn` was originally
the qualified `carrier.turn` or was written as bare `turn`. It therefore
offers both to descendants. The former overwrites descendants and makes
reversed bank insertion order reverse which write wins; the latter is existing
tree-wide discovery needed to diagnose ambiguity.

The compatibility probe is decisive: bare `turn` on the nested reproduction
is refused as ambiguous naming `carrier.turn`, `carrier.ring.turn` and
`carrier.ring.wheel.turn`, with its previous bank and pose restored. Joint
coordinates are accepted by qualified ID under a running root, and a root
coordinate's qualified ID is necessarily bare. Bare declared drivers likewise
propagate and become an ambiguity refusal when more than one declaration
claims the name; `time` is the sole globally reserved snapshot entry. Those
behaviors are compatibility constraints.

### Cycle identity and authority

This is a standalone framework cycle based on
`c62319e1974b88d8cfd2dd13fd205c7bf2533991`, selected from the clean primary
`main` checkout at
`/home/asa/devel/machinome-studio/machinome-framework`. Its branch is
`bind-retained-coordinates-by-owner` and its isolated worktree is
`/home/asa/devel/machinome-studio/machinome-framework/WTs/bind-retained-coordinates-by-owner`.
The intended future integration target is `main`, but integration is not yet
authorized.

The pilot approved the bounded correction and directed a Sol proposal agent,
a separate Sol implementation agent, and adversarial review before spec sync
and archive. The cycle restores an accepted contract and presents no new API
or architecture choice requiring separate ratification; the complete planning
artifacts still require the framework cycle's planning review and commit before
implementation begins.

## Goals / Non-Goals

**Goals:**

- Restore ADR-105 so every retained coordinate binds and poses only its owner.
- Make full-bank binding deterministic regardless of mapping insertion order.
- Cover parent/child independence, rebinding, restore/reset and every joint
  declaration shape implicated by the delivery rule.
- Preserve symbolic export and the numeric pose around publication.
- Prove the correction on the originating Curta geometry without changing it.

**Non-Goals:**

- No new public state-binding spelling, simulation behavior or architecture.
- No change to bare driver propagation, global `time`, ambiguity or ownership
  refusals, joint solving, bank compilation, export schema or viewer behavior.
- No Curta arithmetic, reverser, source geometry, performance or unrelated
  mechanical correction.

## Decisions

### Preserve qualification provenance through child projection

Carry the internal provenance that says whether an entry was originally
qualified while its path segments are stripped during descent. When
`CoordinateDelivery` consumes a QUALIFIED coordinate at its owner, omit that
entry from child projection. When it consumes an ORIGINALLY BARE name, keep
projecting it so every matching declaration is discovered and the existing
ambiguity judgement remains possible. A name no coordinate consumes keeps its
existing behavior, so bare drivers and `time` still propagate.

Two simpler alternatives are rejected. Suppressing every consumed name fixes
the bank but silently makes formerly ambiguous bare `turn` select the first
ancestor owner. Keeping today's dotted-name heuristic preserves ambiguity but
cannot distinguish a stripped qualified single-coordinate name from an
originally bare name. Reclassifying every name during projection duplicates
declaration knowledge and could diverge for class-declared, site-declared or
future joint forms.

### Prove the fault red at the framework boundary before correction

Add a focused nested fixture with repeated local joint names and distinct
retained values. Before changing delivery, prove the existing normal-order and
reverse-order disagreement. Assertions cover both bound coordinate values and
pose operations/matrices so a correct slot with stale geometry cannot pass.
Extend the fixture or a focused companion to class/site declaration and
multi-coordinate ownership.

### Exercise every route that re-delivers a complete bank

The same fixture covers direct complete-bank rebinding, a snapshot restore and
reset. These are not separate implementations, but they are distinct public
promises and protect against a caller accidentally supplying a differently
ordered mapping.

### Treat export as preservation coverage, not a format change

Symbolic publication already delivers each coordinate directly at its owner,
then restores saved slots and joint placement. Add regression coverage with
nested same-named coordinates to verify owner-qualified expressions and exact
numeric pose restoration. No schema, version, viewer or serializer contract
changes.

### Validate with unchanged originating-project evidence

After framework suites pass, run the Curta project's existing minimal retained
pose probe and `simulation.tools.test_retained_pose_probe`, then the unchanged
`simulation/test_running_motion.py` carriage-shift and clearing tests. Capture
and inspect visual evidence for the corrected carriage and clearing poses; do
not weaken tolerances or alter project laws or geometry.

## Risks / Trade-offs

- [Qualification is lost while path segments are stripped] -> Carry explicit
  internal provenance and test both a qualified owner entry and the same local
  spelling supplied bare, including coordinate/coordinate and
  coordinate/driver ambiguity with rollback.
- [Slot values become correct while operations remain stale] -> Assert joint
  values and rendered transforms after movement, rebind, restore and reset.
- [The narrow running fix perturbs publication restore] -> Run focused
  serializer/export preservation tests and broader export regressions.
- [Curta mesh evidence is expensive or environment-sensitive] -> Keep the
  geometry-free framework reproduction authoritative for the defect, report
  environmental failures honestly, and retain visual inspection as required
  caller evidence rather than replacing unit proof.

## Migration Plan

No migration is required. The change corrects existing retained-state behavior
without changing accepted input or serialized output. Rollback is the single
implementation cycle if regression evidence contradicts the design.

## Open Questions

None. The observable contract and the owner boundary are already settled by
ADR-105; implementation must not introduce a broader binding policy.
