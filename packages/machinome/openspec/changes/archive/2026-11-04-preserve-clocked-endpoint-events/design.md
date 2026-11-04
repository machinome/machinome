## Context

The originating project is `/mnt/data/machinome-projects/enigma-i`, recorded at `cc57979df15bbc3e5d16ccc5729196afec652417` plus its ongoing controller work. Its `simulation/tools/probe_clocked_endpoint.py` uses only an empty AssemblyNode, a millimetre Driver, an integer State and public law factories. `sources/clocked-endpoint-reproduction.json` records start `6.442137473829186`, threshold `1.0571271006818843`, endpoint count 0, uninterrupted-to-zero count 1 and threshold-then-zero count 0. The independent project remains owned by the parent agent.

Read contracts: `docs/architecture.md` (clocked execution), accepted ADR-107, ADR-121 and ADR-125, `openspec/specs/simulation/spec.md` clocked request requirement, and relevant clocked solver implementation/tests. The current executor retains the target in `Clocked.move`, but passes `target-current` into event discovery. `Committing.next_event` and `JumpPlan._solved` evaluate endpoints through reconstructed `start+delta`. These operations can lose the exact requested target through subtraction/addition rounding. This is the first hypothesis to verify red-first, not an assertion that the final patch is already proven.

## Goals / Non-Goals

**Goals:** Restore the existing inclusive endpoint and request partition promises for the reproduced path; keep the authored expression arithmetic, exact float landings, rising-only events, simultaneous synchronous reads, ordering and whole-request atomicity.

**Non-Goals:** New API, epsilon, tolerance, rescaled physical threshold, Enigma-side event locator or fabricated stop; running-mode redesign; speculative locator abstraction; viewer implementation inside the framework.

## Decisions

1. Preserve the exact admitted endpoint as authoritative throughout clocked discovery, containment and resumption wherever reconstruction can change it. Verify which layers actually lose it before choosing the smallest parameter/data-flow change. Interior path arithmetic and `by=` semantics must remain unchanged; clipped endpoints must remain the admitted endpoint. A generic fallback that commits merely because the final predicate is true is rejected: it can skip intervening events, conflate rising/falling paths and violate state-dependent ordering.
2. Continue using the existing affine/kinked surface solver and branch-based far-side walk. Endpoint inclusion must use exact values without numerical slack. Strict comparisons must still land beyond a reached threshold and fire only in the request containing that float. Keep ties keyed by landing identity; do not clamp strict landings to the endpoint.
3. Add an empty-assembly regression using proper public `at`/`law` factories with the exact Enigma constants. Establish red failures for endpoint and split requests and a passing direct control. Cover equivalent reversed, negated, difference and power-of-two-scaled comparisons with authored arithmetic retained, plus upward/downward representative cases and a reconstructable control. Check bank, commit values/targets and concatenated event order; fractions are relative to each request and need not equal across partitions.
4. Reuse meaningful existing strict, simultaneous/one-ulp, ordering, atomic conflict/final-pose refusal, bound and clocked corpus tests; add focused cases where existing fixtures do not exercise exact-target arithmetic. Test zero continuation/no refiring and clipping so endpoint authority cannot admit a surface outside a stop.
5. Inspect published clocked document/corpus and separate viewer consumption for the same endpoint arithmetic. Document whether the corrected behavior is already expressible, whether corpus evidence needs extending and whether a separate viewer issue exists. No document/API bump is expected for restoring existing semantics. A proven viewer defect is reported for a separate cycle, not silently bundled.

## Risks / Trade-offs

- Endpoint plumbing can affect shared running consumers → prefer clocked-local changes; if shared solver changes are necessary, preserve default behavior and run its focused running/kinked regressions.
- A patch can make inclusive cases pass by destroying strict/adjacent event distinctions → retain exact nextafter and one-ulp tests, ties, synchronous state reads and declaration-order invariance.
- A project test can import the primary package accidentally → record Python executable and resolved module path, force the isolated worktree import, and run both public reproduction and `tests/test_loaded_control.py` with unchanged numeric thresholds. Parent owns any project evidence writes.
- The workspace venv has a reported EMFILE failure → use an isolated environment or the recorded project runtime with explicit worktree import paths; do not repair or mutate the workspace runtime.

## Migration Plan

No migration or authored model edit is needed. After red/green evidence, synchronize and archive the change, create completed commit 2, and integrate locally only if main is clean and still at the recorded base. Rollback is removal/reversion of this isolated correction under normal maintainer authority; no external publication occurs.

## Open Questions

Exact failing arithmetic and minimal affected call chain are resolved during apply and recorded with evidence. An architectural ADR is not expected for this conformance fix; reassess after implementation and record the disposition.

## Delegated proposal review

The proposal agent checked scope against the named Enigma evidence and the existing endpoint, strictness, tie, ordering and atomicity clauses. The plan preserves those contracts and explicitly avoids a new tolerance or project workaround. This is agent self-review under the pilot's advance authorization recorded in proposal.md, not human approval of the finished text. Apply must independently check the diagnosis and close any in-scope review findings before completion.
