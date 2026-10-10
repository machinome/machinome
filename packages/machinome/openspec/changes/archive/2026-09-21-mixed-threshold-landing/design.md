## Context

Standalone cycle based on clean framework main
`e63700e4fdb90e066d47f358e9de0ea935ac1be9`, branch/worktree
`mixed-threshold-landing` / `WTs/mixed-threshold-landing`. Intended integration
target is framework main; integration requires pilot authority and an unchanged
clean target. Existing unrelated worktrees are not part of this change.

Curta's `HigherOperatingTrial` adds a measured tens-stack bound while preserving
the full assembly and source carry laws. Raised withdrawal passes, but normal
input-9 preparation fails inside the constraint sub-program. Its faithful
CAD-free reduction completes without the bound and fails with it. At the cut,
the lever moves from −3.0518676393442643 to −3.051867639344261 mm, while the
moving threshold makes the comparison cross in the opposite relative direction.
The landing walk searches the wrong side and exhausts its existing 200 strides.

ADR-121 and the simulation baseline already require the branch the **level**
was moving toward, evaluated at fixed crossing-source values. Choosing a
coordinate-space search direction solely from that coordinate's displacement
does not satisfy this mixed-source case. ADR-113/135 constraint observation
must preserve valid upstream integration, not conceal that discrepancy.

The first correction exposes a second, pre-existing precision failure: Curta's
pin-following branch has constant relative position, but a rounded probe differs
by 2.22e−16 and falsely flips the reset, then refuses as chatter. A public affine
fixture reproduces this on unchanged main. On 2026-09-21 the pilot explicitly
extended this cycle to correct that refusal without clearance, tolerance
changes or suppression of genuine mechanical errors.

## Goals / Non-Goals

**Goals:** honor the existing far-side contract for a moving threshold that
overtakes a moving coordinate; preserve deterministic history and transaction
boundaries; pass the originating real Curta requests in Python and the matched
browser executor.

**Non-Goals:** new declarations, generalized dynamics, new tolerances, relaxed
invariant errors, changing source carry laws or print geometry, splitting user
requests, viewer code inside this repository, publication or pushing.

## Decisions

1. Determine the far side from the crossed level/branch at the located contact,
   not from the sign of the driven coordinate's net travel. Preserve the
   existing nearest-representable landing and absolute commit. Implementation
   must demonstrate which branch is requested and orient/bracket the local
   coordinate crossing accordingly. Do not catch an invariant error and accept
   the unlanded value, or blindly return an arbitrary opposite-side candidate.
2. Retain the current fixed-source landing evaluation, float-ordinal bisection,
   crossing budget and transactional refusal. A truly unlandable or sliding
   crossing remains a named refusal. Any need to widen admitted expressions,
   change the tolerance budget or replace this contract returns to the pilot.
3. Prove the failure through public `Sim` requests before editing the executor.
   Add a small analytic moving-threshold fixture with independently computed
   results, then exercise the original project reduction and complete Curta.
   Test both relative directions, negligible and zero driven displacement,
   unchanged stationary-threshold cases, later requests, restore/replay and
   constraint observation. Numerical edge fixtures must not replace real CAD.
4. Keep the document shape/version unchanged and extend conformance evidence.
   If the browser reproduces the fault, implement its corresponding correction
   in a separate viewer-owned change and validate the tested content pair.
   Extract/update an ADR only after implementation confirms the final rule.
5. Add a conservative algebraic certificate for constant relative level on an
   existing affine piece. Compose the skeleton's increment with the driven
   coordinate inside the level expression. Exact arithmetic over the finite
   binary input constants can prove cancellation without a tolerance. Certify
   only supported affine operations and continuous selections whose selected
   branch is valid over the entire checked interval; uncertainty, a crossed
   kink or a curved expression falls back to the existing search. A proved
   zero slope must not manufacture a crossing or branch flip from rounded
   point samples. Any nonzero relative slope, however small, keeps its normal
   treatment. Bank arithmetic, nearest-float landing and clocked execution
   remain unchanged. Test following contact, infinitesimal real departure,
   piece boundaries, unsupported curved cases and genuine atomic refusals.

Alternatives rejected: a smaller user tick or split request (hides the failure),
a project-specific carry rewrite (changes the mechanism to accommodate the
executor), an overlap epsilon (irrelevant to the branch failure), and accepting
the arithmetic landing after a failed search (violates retained-state guarantees).

## Risks / Trade-offs

- Mixed levels can have nonlinear or multiple surfaces → pin the requested
  branch and local crossing, retain refusals where no valid landing exists.
- A sign correction could change stationary-gate results → require existing
  fixtures unchanged, full focused/regression suites, and corpus review.
- Python/browser arithmetic can diverge → independent repository correction
  and the real exported Curta worker test, not only unit parity.
- Curta geometry and other channels remain unfinished → this cycle claims only
  removal of its reproduced software gate; project acceptance stays separate.

## Migration Plan

After pilot ratification, validate and commit planning only. Implement red-first
in this worktree, validate the project against it, synchronize the baseline,
archive, and commit the completed record. Integrate only under pilot authority
after rechecking the recorded base. Do not change the project's default model
merely because this diagnostic becomes green.

## Open Questions

The conservative certificate and local-orientation implementations must be
confirmed by analytic fixtures and Curta. General contact dynamics, a different
landing contract, and widening the admitted expression language remain outside
this plan.
