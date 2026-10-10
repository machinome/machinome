# Spikes: the measurements behind this proposal

Run from the FRAMEWORK WORKTREE ROOT, one job at a time (the host
filesystem runs out of descriptors under parallel CAD jobs):

```
WT="$PWD" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH="$PWD" \
    python openspec/changes/cut-at-the-kink/spikes/<probe>.py
```

The three Curta probes run from the PROJECT instead, read-only, with the
project and this worktree both on `PYTHONPATH` and `WT` naming the
worktree.

| probe | what it answers | where |
| --- | --- | --- |
| `kink_baseline.py [rounds]` | ticks/s and `GraphValue.evaluate` calls per tick for `Train`, `Clearing`, `CurtaInterface` — the `read-the-driven-coordinate` evidence.md §14 probe | worktree |
| `classify.py` | the prototype three-valued classifier (`shape_of`), plus `blame()` naming the nodes that make a graph unclassifiable. Imported by the others; not run alone | — |
| `classify_fixtures.py` | how many skeletons and jump levels of each fixture program are affine / kinked / unclassified | worktree |
| `attribute.py` | charges every graph evaluation to the SEARCH call site that caused it and to the classification that sent it there. Imported by the two `attribute_*` probes | — |
| `attribute_fixtures.py` | the same for `CurtaInterface` and `Clearing`: 84.5 % of the former's cost is in the two sites this change replaces | worktree |
| `exactness.py` | how far the recorded crossing of `result0`'s rack sits from the closed-form answer: 9.3e-14 | worktree |
| `corpus_flip.py` | which corpus machines get a reclassified determiner, and which jump levels change class (none) | worktree |
| `classify_curta.py`, `blame_curta.py` | the same classification over the real `OperatingCurta`, and what blames its 41 unclassified skeletons (`sin`, `cos`, a product of movers, a moving divisor) | project |
| `attribute_curta.py` | where three of the Curta's own ticks actually spend their evaluations: 100 % under an UNCLASSIFIED skeleton, none under a kinked one | project |

`classify.py`'s `shape_of` is a PROTOTYPE of design.md §4.1, written to
measure the blast radius before proposing. The implementation belongs in
`solid_node/simulation/program.py`; this copy is evidence, not a plan.
