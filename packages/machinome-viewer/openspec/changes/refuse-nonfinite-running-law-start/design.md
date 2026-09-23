## Context

The public `Run` accepts a compiled version-5 law and integrates commands both in-thread and through the worker. On `b976a17`, a valid rest `feed=0` moved to `0.2` makes `sqrt(0.1 - feed)` non-finite at the endpoint; the continuous-law subtraction produces `NaN`, and the step commits it. A separate accepted document with invalid authored start has the same failure, though the producer's rest render refuses that document. The existing running-step requirement at viewer-package ~1740–1900, ADR-045's one engine, and ADR-047's recorded corpus are the applicable authority. `UnsupportedLaw` is the existing `law` refusal class, and `integrateScoped` has a transactional catch for it. The producer's corresponding valid-start command currently raises a raw domain `ValueError` with unchanged bank but an active failed command; repairing that is a separate framework proposal.

## Goals / Non-Goals

**Goals:**

- Refuse a failing step at the existing law-evaluation point if an actually evaluated law result is `NaN` or either infinity; name the law and given coordinate, use `law` refusal kind, and commit no change from the state before that step. Earlier successful steps of the same command remain committed.
- Preserve the order and count of law evaluations, valid endpoint arithmetic, command admission, and the same behavior in-thread and in the worker.
- Demonstrate the producer-compatible valid-start/invalid-endpoint failure red first, then cover the accepted invalid-start document, path-interior, and moving-tick cases where the executor actually evaluates those values; keep a legal square-root endpoint green.

**Non-Goals:**

- Refusing a document at load merely because a law might be undefined in some future state; redesigning the expression language; changing a bound's legal sentinel representation; adding a tolerance, clipping, or changing the producer corpus.
- Repairing unrelated numeric paths, the running-target-endpoint cycle, or framework source.

## Decisions

1. Apply a law-specific finite-result check at the existing law evaluation seams, before a bad value is subtracted, propagated, or turned into a motion. Check direct continuous evaluation and any existing path evaluation that is actually reached. Do not put a catch-all finite check in the generic expression interpreter, bound solver, or final bank: those would change unrelated semantics and could miss a non-finite intermediate masked by later arithmetic.
2. Raise `UnsupportedLaw` with the law description, stated-by class, and output coordinate, matching the running step's existing named-refusal surface. The current step transaction catches that class, retires commands that moved in the failing step as `refused`, and leaves staged bank and rings unpublished. Do not catch or relabel unrelated exceptions. This is viewer conformance to its running-step contract, while the producer's raw domain-error retirement remains a separate discrepancy to resolve before a new parity corpus case can be claimed.
3. Preserve the current arithmetic and evaluation order for finite values. The guard only examines the result already computed. No public API or document version rises for a conformance correction to an existing requirement.

## Risks / Trade-offs

- **[Several law paths]** The direct law path and trajectory/path paths have distinct evaluators. → Audit each existing law-result evaluation seam and prove the relevant shapes with focused tests; avoid duplicating evaluation.
- **[Evaluation with legal discontinuities]** A guard at a newly sampled or unused point could reject a previously valid request. → Guard only results the executor already evaluates, and retain the existing valid source-to-boundary square-root control and corpus.
- **[Failed command not retired]** A zero-duration request with no admitted movement may not appear in `moved`. → Test the ordinary nonzero immediate request and a zero-travel error case separately; if the latter exposes a refusal-status gap, review the running contract before widening command retirement.
- **[Producer discrepancy]** The producer's raw domain `ValueError` currently leaves the failed command active even though its bank stands. → Keep a separate framework cycle and do not claim byte-for-byte parity for a new domain-error corpus case until both runtimes agree.

## Migration Plan

No data migration. After red-first tests, run focused Vitest, the full widget suite, typecheck, and a bundle build from this worktree; integration is only after the independent endpoint cycle settles and combined validation is reviewed. Rollback is the isolated implementation commit, not a schema conversion.

## Open Questions

No public interface choice remains. Implementation evidence may reveal a non-finite case outside an actually evaluated law path; record it separately rather than broadening this cycle silently.
