# Spikes: design evidence for `select-the-source`

Design evidence, not implementation. Nothing in `solid_node/` is edited;
where a refusal is in the way it is monkeypatched at RUNTIME inside the
script. Run each from the framework worktree root:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  PYTHONPATH="$PWD:$PWD/openspec/changes/select-the-source/spikes" \
  ../../../.venv/bin/python openspec/changes/select-the-source/spikes/<name>.py
```

`pyproject.toml` is a copy of `tests/pyproject.toml`: the framework
discovers a model through a manifest, so a fixture outside `tests/` needs
one of its own.

| script | question | answer |
| --- | --- | --- |
| `reduced.py` | the note's fixture, the same cycle with NO self-read, and the ground truth with `shift` frozen at `0` | the refusal verbatim; `DoublyBound` with rest guards and `UnreachedCoordinate` without — both from the REST RENDER, before the compile (design.md facts 1 and 2). Also the module the other spikes import their fixtures from. |
| `membership.py` | do the resolved records exist before the rest render? | yes: all three, with resolved driven slot identities and `direction=None`, on an unrendered tree (design.md fact 3, §5) |
| `fold.py` | is the switched-source test computable? | yes: the skeletons, the selectors' levels, and the reads under one folded branch (design.md §2) |
| `arbitrary.py` | what does an arbitrary union order do? | `higher.turn` at `1.48` under declaration order and `0.0` under the reverse, against a ground truth of `1.5000000000000018` (proposal.md's table) |
| `pieces.py` | is piece-by-piece composition exact? | yes, with the in-block value advanced: `0.5 + 0.5 + 0.0 = 1.0`, the same landing float and the same crossing fraction as the whole stretch; `0.5 + 0.7 + 0.8 = 2.0` without, which is the negative control (design.md §3). It does NOT settle what a block reports when a landing is followed by further motion: its landing falls in the second piece and the third piece's increment is `0.0`, so "the last landing" and "the block-advanced absolute" coincide here. Task 4.7 is what pins that rule. |
