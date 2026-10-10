# Spikes: the measurements behind this proposal

Run ONE at a time (the host filesystem runs out of descriptors under
parallel jobs). From the FRAMEWORK WORKTREE ROOT:

```
WT="$PWD" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH="$PWD" \
    python openspec/changes/evaluate-only-what-moves/spikes/<probe>.py
```

The Curta probes run from the PROJECT
(`projects/Calculators/Curta-Type-I-3x`, branch `direct-operation`, HEAD
`9fb725f`), READ-ONLY, with the project and the worktree both on
`PYTHONPATH` and `WT` naming the worktree:

```
cd <curta> && WT=<worktree> PYTHONPATH="<curta>:<worktree>" \
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 <venv>/python <probe>.py
```

| probe | what it answers | where |
| --- | --- | --- |
| `path_baseline.py [rounds]` | ticks/s, `GraphValue.evaluate` calls per tick and NODE VISITS per tick for `Train`, `Clearing`, `CurtaInterface` — cycle 1's probe plus the unit this cycle moves | worktree |
| `split_curta.py [ticks]` | a Curta tick and its construction split into expression evaluation, port enumeration and the rest, with the sizes of the graphs evaluated | project |
| `callsites_curta.py` | every one of a tick's evaluations charged to its caller chain, by COUNT and by SECONDS — which is how the 39 % of evaluations ADR-123 left "elsewhere" turns out to be 1 % of the time | project |
| `cone_curta.py` | for every searched crossing, how many nodes of the skeleton and of the level actually MOVE along the path: 11.2 % and 2.0 % | project |
| `proto_eval.py` | the current walk, a path evaluation and a compiled path compared on 2 600 captured evaluations of the Curta's own graphs, with a byte-for-byte equality check | project |
| `endtoend_curta.py [plain\|patched\|plain-ports\|patched-ports] [ticks]` | the real machine with `_Walk`'s two evaluation sites replaced by a path evaluation and nothing else: tick seconds and the SHA-256 of the committed snapshot. `NOSTRUCT=1` drops the cross-tick structure cache; `SNAPDIR=<dir>` writes the snapshot out | project |
| `perpiece_curta.py` | the alternative this cycle rejects, measured: how many searched skeletons a per-PIECE classification would solve (192 of 200) | project |

`endtoend_curta.py`'s `PathEvaluation` is a PROTOTYPE of design.md §3,
written to measure the mechanism and prove the answers unchanged before
proposing it. The implementation belongs in
`solid_node/simulation/program.py`; these copies are evidence, not a
plan, and they monkeypatch the framework at import time — never import
them from anything but a probe run.
