## 1. Red-first conformance tests

- [ ] 1.1 Add a public `loadProgram` + `Run.move` test of the producer-compatible valid-start/invalid-endpoint version-5 reproduction; assert named `law` refusal, refused command, and unchanged bank, tick, rings, and snapshot. Run it red against unchanged source.
- [ ] 1.2 Add focused red-first cases for the accepted invalid-start document, an actually evaluated path interior, `NaN` and both infinities where reachable, and a two-step command whose first step remains committed when its second fails. Keep the valid `sqrt(0.1 - feed)` boundary from `-0.2` to `0.1` green. Record cases already green or unreachable by the published evaluator rather than manufacturing an evaluation point.

## 2. Narrow runtime correction

- [ ] 2.1 Audit existing direct and path law-evaluation seams, then check each computed law result for finiteness before propagation using the existing `UnsupportedLaw` refusal kind and a message naming law and output; do not add evaluation points or change finite arithmetic.
- [ ] 2.2 Verify that a refused immediate or moving step retires commands that moved in that step, publishes no part of that step, and retains previously committed ticks and admitted travel. Do not broaden command retirement to zero-travel or unrelated exceptions without separate evidence and review.

## 3. Validation and integration gate

- [ ] 3.1 Run focused Vitest, the full widget suite and corpus replay, TypeScript typecheck, and bundle build; inspect source diff for unrelated numeric, bound-sentinel, endpoint, and API-version changes.
- [ ] 3.2 Once the independent running-target-endpoint cycle is settled, rebase or merge safely into this isolated worktree, rerun combined conformance and endpoint tests, sync the accepted delta spec, archive the change, and request integration review. Do not push or alter another worktree.
