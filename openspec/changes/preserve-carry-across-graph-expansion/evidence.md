# Curta carry: isolated proposal evidence

Date: 2026-09-22. Status: diagnosed; proposed correction ratified by the pilot's
“go on” after proposal review, still unimplemented at the planning boundary.
These are retained observations, not a claim that the design works.

## Identity and authority

- Framework source and bench HEAD:
  `e6a42c80e6dcc686c180b8a6d94037301c4213a5`.
- Branch: `preserve-carry-across-graph-expansion`.
- Bench: `machinome/WTs/preserve-carry-across-graph-expansion` inside the
  primary shop `/home/asa/devel/machinome-studio`.
- Standalone base and intended later integration target: framework `main`.
- Pilot approved an isolated proposal from committed HEAD while preserving
  untracked `machinome/docs/examples/v8-engine/`. `scripts/dev-env ... setup`
  still refused that dirty primary, so the approved exception was exercised
  through `git worktree add`, not a launcher modification or ignored dirt.
  This bench has no launcher manifest registration, `.env`, or assigned ports.
- An initially misplaced nested worktree was moved with `git worktree move`
  to the bench above; only newly created empty intermediate directories were
  removed. No primary or project content was removed.
- Project canonical root:
  `/mnt/data/machinome-projects/Calculators/Curta-Type-I-3x`; the workspace
  `projects/Calculators/Curta-Type-I-3x` resolves there. Branch `direct-operation`,
  checkpoint `8852677`; diagnostic regression introduced at `1c3dfde`.

## Reproduction

`evidence/trace_carry.py` imports the project's existing `result_graph` helper
and production laws. It prepares digit 0, height 9 and crank 90, then makes one
unchanged crank-to-180 request. Default instrumentation wraps `_Block._partition`
and `_integrated`, calls each original exactly once and returns its result
unchanged. The optional `--extra-cut` mode is explicitly a counterfactual
experiment, not an implementation or acceptance fixture.

From the bench (with the workspace virtualenv):

```sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
export PYTHONPATH="$PWD:/mnt/data/machinome-projects/Calculators/Curta-Type-I-3x"
/home/asa/devel/machinome-studio/.venv/bin/python \
  openspec/changes/preserve-carry-across-graph-expansion/evidence/trace_carry.py
/home/asa/devel/machinome-studio/.venv/bin/python \
  openspec/changes/preserve-carry-across-graph-expansion/evidence/trace_carry.py \
  --stations 6 --extra-cut 0.06666666666666667
```

Both completed successfully. `evidence/traces.json` retains their complete
JSON output, including loaded framework module path, starting/final banks,
cuts, and selected members' integration inputs/results. The ordinary trace
preceded addition of the optional argument, hence its records omit
`injected_cut`; it did not inject any cut.

| Graph / diagnostic | Internal cuts (request fraction) | Final tens.turn |
| --- | --- | ---: |
| Six stations | 0, 1 | 704 |
| Seven stations | 0, 1/15, 1 | 698.4639999999999 |
| Eleven stations | ten pieces; retained in JSON | 632 |
| Six, only 1/15 cut injected | 0, 1/15, 1 | 698.4639999999999 |

All four complete at crank 180. The same first lever starts -4.2 and ends 0.
Six stations supply its entire 4.2 travel as a ramp over crank 90..180.
Seven stations supply no lever travel over 90..96, then the same 4.2 as a
ramp over 96..180. The tens law's carry gate is at 61% of the lever stroke:
these artificial ramps place it at crank 144.9 and 147.24 respectively.
That is timing introduced by the handoff, not an observed physical lever path.
Seven's tens increments are 38.4 and 378.464 rather than six's 422.4 total.
Injecting only the later cut reproduces both those increments and the lost
5.536 degrees, establishing the causal partition sensitivity independently of
the seventh station's geometry, declarations, or arithmetic.

The source shows two timing-erasing handoffs: `_Block.increments` passes
`piece.get(key, 0.0)` as a linear predecessor delta, and restricts external
determined deltas with `delta * (right-left)`. The latter is visible in the
trace's ones shaft: 222.4 total degrees is spread uniformly over the request.
The proposed correction must address both, not merely arrange for the six-
station coincidence to survive more graph members.

## Existing red evidence and baseline blind spot

Project-owned `simulation/docs/evidence/result-carry-scope-2026-09-22.json`
retains source hashes, the 2..11 census and fresh-process 7→6→7 control.
Its regression results on the same framework base are:

- Six/seven prefix pair: one pass, one failure, 20.38 seconds.
- Full graph pair: two failures, 285.152 seconds. Unconstrained tens is 632;
  constrained request stops at crank 163.42595046793576, tens
  699.2537571367207, instead of reaching crank 180/tens 704.
- The physical oracle is unchanged: datum -16, nine direct 72-degree throws,
  one 72-degree carry: 704. Removing contacts or splitting the request is not
  acceptance.

In this isolated bench, existing `tests/test_running_selection.py` passes:
39 tests and 4 subtests, 2.82 seconds. It does not cover this failing graph-
extension/timed-source composition, so its green result is a blind spot rather
than evidence against the retained project failure.

Raw log SHA-256s (logs are ignored; their trace contents are retained in JSON):

- `trace-carry-final.log`:
  `495def94e247cecccc48dfed24314f2481e5284327f476c62d31f61270174ff2`
- `trace-carry-extra-cut.log`:
  `bb5360a004c3a6834af3dda101f80616c6cb57c15859df0bb09a8256cd80a0c6`
- `baseline-selection.log`:
  `308524bebca17d590859eba10c3fdad2e0f7fd99edfe22183f305d8f72e70563`

Two aborted trace attempts are not solver results: importing through the
workspace symlink produced a source/build-root mismatch and `/mnt/home`
permission error; canonical project imports resolved that. A diagnostic exact
float assertion then rejected 281.59999999999997 versus 281.6; using the
existing project's 1e-8 preparation tolerance resolved it. No engine code or
physical assertion was weakened.

## Independent project checks

The already-running native station-eight check completed with 23,556 checks
and zero failures (`_build_checks/result-station-8-profile-native-2026-09-22.log`).
The separate, unadopted result-bank collar arithmetic trial has passed manual
calibration carries and subtraction/undo. Its third case was still running
when this proposal was prepared. Neither check establishes a framework fix or
full-machine acceptance; no default operating model has been changed here.

## Proposal readiness

OpenSpec reports all four artifacts complete; `openspec validate
preserve-carry-across-graph-expansion --strict` passes. This is planning
validation only. The pilot subsequently ratified the design on 2026-09-22.
Planning commit 1 records that ratification before implementation. No framework
source or baseline specification was edited at this boundary.
