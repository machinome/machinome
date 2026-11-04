# Exact clocked endpoint conformance evidence

## Independent apply review and diagnosis

The apply agent independently reviewed all four planning artifacts, the full simulation delta and baseline clocked request/clip requirements, architecture clocked execution synthesis, accepted ADR-107/121/125, the solver and existing tests. Scope and proof match the pilot's advance authorization. Planning commit `5166fd9d1341328eb1671ab375c493b0ff03bf1c` is planning-only, clean and exactly one commit above standalone base `b818376640e29bc51235c6b22f1962dad0fb2aa5`. No framework-local agent instruction was used.

For start `6.442137473829186` and target `1.0571271006818843`, `start + (target - start)` is `1.0571271006818845`: hexadecimal `0x1.0e9fe1b524dccp+0` instead of `0x1.0e9fe1b524dcbp+0`, one float above the descending inclusive threshold. Clocked.move preserved its target but discovery reconstructed the end through the delta. Thus `_solved` did not see the zero surface and containment also used the wrong endpoint. On continuation, the inclusive branch was already true at the start, so opening detection correctly did not refire it, leaving it lost.

The implemented correction passes the already clipped/admitted target into event discovery and containment. `_RequestSteps.along` supplies that exact endpoint at fraction one using the shared solver's existing evaluator protocol. Interior `start + delta*fraction` arithmetic stays unchanged; the existing branch-based far-side walk also starts at the exact target for a terminal crossing. No shared solver, public API, tolerance, document version, project threshold or project locator changes. Existing `by=` arithmetic still computes its target once before clipping. Subsequent solves retain the same admitted end.

## Red and green

`tests/test_clocked_endpoint.py` uses empty public AssemblyNode declarations and real at/law factories from `tests/clocked_project/endpoint.py`. Against planning commit source, four tests report eleven failing subcases: five equivalent inclusive comparison forms in each direction and independent partition-bank comparison. Direct-to-zero, reconstructable endpoint and both strict nextafter controls pass. With the correction all four tests pass, including zero continuation/no refiring, exact landing and targets/order equivalence. See `evidence/framework-red.log` and `framework-focused-green.log`. The baseline source was temporarily restored solely for the red run and then the patch restored; no implementation commit was created.

Final proportionate command:

```
/tmp/clocked-endpoint-apply-runtime/bin/python -m unittest tests.test_clocked_endpoint tests.test_clocked_solver tests.test_clocked_sim tests.test_clocked_bounds tests.test_clocked_refusals tests.test_clocked_corpus tests.test_clocked_time tests.test_clocked_document -q
```

This covers rising/falling and kinked surfaces, exact strict/non-strict landings, adjacent floats and tie identity, synchronous reads, declaration order, state-dependent relocation, atomic conflict and final-pose refusals, clipped bound paths, elapsed clock, published documents and exact corpus replay. Shared solver code is untouched, so additional running consumer changes/tests are unnecessary.

The pre-existing runtime `/tmp/enigma-validation-runtime.SJdnVd/environment/bin/python` has no pytest and its isolated subprocesses lack solid2. An initial broader run reported two environment-only failures out of 303 tests because import_probe replaces PYTHONPATH. No workspace runtime was repaired or packages installed. A separate standard-library venv at `/tmp/clocked-endpoint-apply-runtime` reads existing dependency site directories and this worktree's extension roots through a local .pth; both parent and subprocess now import the intended worktree. Final log records the complete passing rerun: **305 tests passed in 9.451 seconds** (`evidence/framework-final.log`). The exact resolved clocked module is this worktree's `packages/machinome/machinome/simulation/clocked.py`.

## Enigma I empirical validation

Parent owns `/mnt/data/machinome-projects/enigma-i`, HEAD `cc57979df15bbc3e5d16ccc5729196afec652417` plus its ongoing controller work; apply performed no project writes. Parent verified using `/tmp/enigma-validation-runtime.SJdnVd/environment/bin/python` and explicit worktree PYTHONPATH. Its JSON records the executable, resolved `Sim` module, framework planning HEAD plus dirty implementation state, controller/source hashes and actual outcomes. Original failing `sources/clocked-endpoint-reproduction.json` remains unchanged.

- Public minimal probe: endpoint/direct/partitioned counts become `1/1/1`, formerly `0/1/0`.
- `tests/test_loaded_control.py`: all five pass, formerly three pass/two fail.
- Public saved-history checker: six histories, 720 sampled banks, 30 ordered exact commit landings/target lists; uninterrupted, partitioned and snapshot replay agree.
- Existing `tests/test_pawl_cycle.py`: all seven pass, covering 27 strokes, repeated/partial requests, contact branches, snapshot replay, partitioning and actual bounds.

Copied project-owned result JSON and logs accompany this record. These prove the Python public execution contract over the recorded histories; they do not certify new geometry, all possible Enigma inputs or browser equivalence.

## Published corpus and separate viewer finding

Added EndpointRelease to the generator's normal public fixture registry and regenerated the exact corpus: 31 machines/scenarios and 86 steps. Its published document already expresses the same event with no format change; direct and split script records give a downstream consumer a durable regression. Existing corpus records remain unchanged.

Read-only inspection of separate viewer HEAD `bd2bf7536efc0a70731dd15a8fce7b02fd533cb7` found the matching reconstructed endpoint path in `widget/src/clocked/events.ts`. A scratch bundle of the actual viewer loader/machine reproduced the defect against the new published corpus entry: direct step zero commits once and matches; exact endpoint step two reports no commit versus the producer's one exact-threshold count-one commit. The zero and continuation requests do not recover the lost commit. This is an observed consumer defect, requiring its own viewer-owned cycle; no viewer file was changed. Browser equivalence is therefore explicitly not claimed.

Reproduce the read-only scratch script (archived as `evidence/viewer-endpoint.ts`) with the existing viewer tools:

```
/home/asa/devel/machinome/machinome-viewer/machinome_viewer/widget/node_modules/.bin/esbuild /tmp/clocked-endpoint-viewer.ts --bundle --platform=node --format=esm --outfile=/tmp/clocked-endpoint-viewer.mjs
node /tmp/clocked-endpoint-viewer.mjs
```

The archived script preserves the exact tested worktree/corpus paths. Copy it back to the stated scratch location before rerunning. Output is `evidence/viewer-endpoint.log`. No browser or viewer suite claim is inferred from this focused pure executor probe.

## ADR and completion disposition

No ADR: this restores existing accepted endpoint and partition semantics using an existing solver protocol; it makes no consequential architectural choice. The architecture synthesis and studio public contract need no revision. Synchronization adds the two measured scenarios to the existing requirement, preserving all previous text. Archive and final strict validation are performed before implementation commit two. Parent alone performs the separately authorized local fast-forward integration and worktree teardown; no push, tag, publication, PR or contact occurs.


Completion result: strict change validation passed before archive; the supported archive command `openspec archive preserve-clocked-endpoint-events --yes --skip-specs --json` moved the fully completed record to `2026-11-04-preserve-clocked-endpoint-events` after the installed sync workflow merged and verified both new scenarios. `--skip-specs` avoids reapplying an already synchronized delta; it does not mean synchronization was omitted. Post-archive `openspec validate simulation --strict --type spec --json` passes (only pre-existing informational long-requirement notices). Post-archive full test rerun passes all 305 tests; see `evidence/framework-postarchive.log`. Final diff whitespace check passes. No outstanding implementation task remains; commit/ancestry and clean-tree verification are reported in the apply handoff.
