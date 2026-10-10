# Spikes: design evidence for `pin-the-block-order`

Design evidence, not implementation. Nothing in `solid_node/` or
`tools/` is edited: `_Block._order` is monkeypatched at RUNTIME inside
`order.py` and `CORPUS` is replaced in memory inside `regenerate.py`.
Run each from the framework worktree root:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH="$PWD" \
  ../../../.venv/bin/python \
  openspec/changes/pin-the-block-order/spikes/<name>.py
```

| script | question | answer |
| --- | --- | --- |
| `order.py` | does the corpus's `ShiftedCarry` scenario discriminate the block order, and does the candidate script? | no and yes: the committed script replays GREEN under listing order with no crossing in 20 ticks; the candidate (crank `2.0` over `0.3 s`) diverges on 21 readings, `higher.turn` by one sixth from tick 2 and never healing, and records one in-block gate crossing at `t = 0.49999999999999994` of tick 2. Also the module the other spikes import the patch and the comparison from. |
| `patched_corpus.py` | what does the WHOLE committed corpus do under listing order? | every scenario reproduces its bank exactly; the only disagreement anywhere is `RangedBlock` tick 1's crossing COUNT (2 against 3) |
| `alternatives.py` | which scripts would work, and at what `dt`? | `0.2` and `0.4` both land the detent on a tick boundary and diverge on nothing; `0.15` diverges but puts its crossing in tick 1, where the feature has no preceding bank; `0.3` is the chosen one. At `dt = 1.0` the same document gives `higher.turn = 1.0` against listing order's `0.0` |
| `gate_survey.py` | does any committed machine supply the new feature today? | none: `[]` |
| `regenerate.py` | is the script change contained? | yes: `removed: []`, `added: []`, `changed: [('ShiftedCarry', 0.05, 20)]`, order preserved, 356 ticks |
| `gates_debug.py` | why can't the feature be derived from the primitive alone? | the higher wheel's selector `_j2` and its in-block gate `_j4` are both `>=`, so the symmetric rule `_selection` uses is empty for that member under every script |
| `crossings_dump.py` | the raw crossings and banks of both scripts | the committed script records none; the candidate records two, both in tick 2 |
