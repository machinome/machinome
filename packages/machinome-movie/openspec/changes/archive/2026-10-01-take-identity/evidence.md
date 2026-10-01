# Evidence — `take-identity`

Worktree `WTs/take-identity`, branch `take-identity`, cut from the
`addition-warts` head 4833fef. Framework: the workspace venv's editable
install of the framework's `main` (096217f and after), which publishes
`Sim.identity`. Planning commit 8435f1e.

## The identity, probed

A scratch script (in the session's scratchpad, not the repository) built
`Sim` over the fixture counter and over edited copies of the fixture
project (export, `_build/` and `__pycache__/` left out):

| model | `Sim(...).identity` | bank ids |
|---|---|---|
| the export's `clocked.identity` | `d46d4f1ee761…1111d6` | `crank`, `tens`, `units` |
| `models.counter.Counter`, the fixture | `d46d4f1ee761…1111d6` | `crank`, `tens`, `units` |
| a copy, imported as `models.counter`, unchanged | `d46d4f1ee761…1111d6` | same |
| a copy, `advance` writing `(units + 2) % 10` | `87467a1b5ae2…dedc4b` | same |
| a copy, `tens` renamed `decades` throughout | `a6e5a4498298…e5d682` | `crank`, `decades`, `units` |
| the same unchanged file imported under another module name (`variant_same`) | `9f4e30b6a718…bcf5b` | same |

So the simulation's identity is the export's for the same model, changes
with a law while the ids stay, changes with an id, and depends on the
module the model is imported from (finding 1). A state added with nothing
committing it is refused by the framework at `Sim` construction, so the
"state added" variant the brief offered was replaced by the rename.

## Red first

Layer 1, `python/tests/test_take.py`, before any product code: the new
`test_a_model_changed_since_its_export_is_refused_naming_both_identities`
on a copy of the fixture project, evaluated by `python -m machinome_movie
evaluate <copy> count`:

```
E       assert 0 == 1
E        +  where 0 = CompletedProcess(args=[…, '-m', 'machinome_movie', 'evaluate', '/tmp/pytest...t.json'], returncode=0, stdout='/tmp/pytest-of-asa/pytest-122/test_a_model_changed_since_its0/count.json\n', stderr='').returncode
E           AssertionError: 'Take Turns' not named in: machinome-movie: take.initial lacks 'tens', a driver or state the export declares; the take was recorded against another machine
FAILED tests/test_take.py::test_a_model_changed_since_its_export_is_refused_naming_both_identities[law]
FAILED tests/test_take.py::test_a_model_changed_since_its_export_is_refused_naming_both_identities[state]
2 failed, 79 deselected in 17.03s
```

The law change was recorded and written (exit 0): a document carrying the
export's identity over banks another machine made. The rename was refused
by the stand-in, in words about `take.initial`. The new
`test_the_take_is_recorded_with_the_simulations_identity` passed on the
base too (the fixture's identities agree), as it should.

Layer 2, the new invalid fixture `fixtures/invalid/take-initial-incomplete.json`
(the evaluated `count` document with `tens` removed from `take.initial`;
`must_mention` `take.initial`, `tens`, `every driver and state`), red in
both runtimes on the old words:

```
E           AssertionError: 'every driver and state' not named in: take.initial lacks 'tens', a driver or state the export declares; the take was recorded against another machine
1 failed, 76 deselected in 0.25s
```

```
AssertionError: take-initial-incomplete.json: refused for another reason: "take.initial lacks 'tens', a driver or state the export declares; the take was recorded against another machine" does not name "every driver and state"
 Test Files  1 failed (1)
      Tests  1 failed | 21 skipped (22)
```

## Green

- `evaluate.py` (`_record`) reads `sim.identity` after the simulation is
  found clocked, refuses before the first step when it differs from the
  manifest's `clocked.identity`, and writes it as the take's `identity`.
  The refusal, verbatim, on the law-changed copy:

  ```
  machinome-movie: Take Turns: the model models.counter:Counter is not the machine the export ../../export/counter publishes: the framework's simulation of the model has the identity 87467a1b5ae2a0afb3e36053acecccaef77ac09d039295e8ef37d0eb51dedc4b, and the export's clocked.identity is d46d4f1ee76199bce9aa9924e34a97020fd28bd3073939a2a85ec0eceb1111d6; the model changed since it was exported, or the take declares another model than the export was made from: export the model again, or declare the model the export was made from
  ```

- `document.py` and `src/movie.mjs`: the two `take.initial` refusals say
  `a driver or state of the machine the export publishes; a take's bank
  holds every driver and state of its machine and nothing else`, the same
  words in both runtimes.
- The faked stale-export test (`test_an_export_older_than_the_model`, a
  manifest copy with `states.tens` deleted and its identity left) is
  removed: it described an export no framework writes, and with the ids
  rule kept it would still pass, now for the reason D2 keeps the rule, not
  for staleness.
- The matching counter evaluates as before: `test_fixtures.py`'s
  `test_document_is_the_evaluation_of_its_movie[count]` (byte-identical to
  `fixtures/documents/count.json`, whose take is the recipe's
  `fixtures/takes/count/counting.json`) and the twice-identical test pass
  unchanged; no fixture document, take, resolved pin or export moved, and
  the fixture project is unchanged (its recipe revision `10b189d…` stands).

## Both runtimes, each from its own source of truth

- Python evaluation compares the simulation that made the record
  (`Sim(model).identity`) with the export's `clocked.identity`, and
  refuses a take over another machine before recording it.
- The Node commands, which never run the simulation, compare the
  document's `take.identity` with the export's `clocked.identity`
  (`fixtures/invalid/take-identity-differs.json`, unchanged, refused by
  both suites), and the viewer's `restore` holds the viewer to the
  document's identity (ADR-012).
- Both hold `take.initial` to every driver and state of the export's
  machine, in the same words, which the new invalid fixture pins.

So a document Python writes now names the machine that made it, and both
runtimes refuse a document that names another machine than its export.

## Suites

Python, the whole suite on the final content
(`env -C python …/.venv/bin/python -m pytest -q`):

```
291 passed in 26.70s
```

(288 at the base: one test removed, two parametrized cases, one identity
test and one invalid fixture added.)

Node, the whole suite on the final content, with
`VIDEOMAKER_VIEWER_BUNDLE` naming the API 29 bundle; one other agent's
suite may have run in another worktree at the same time:

```
 Test Files  40 passed (40)
      Tests  405 passed (405)
   Duration  864.51s (tests 98%, import 1%)
Test memo: 0 passed from the memo, 405 run
```

Every test ran cold (none from the memo): `src/movie.mjs` is imported by
the slow tests, so this change gives each a new key. The `viewer` project
ran on the real bundle (its "counter's take is checked, previewed and
rendered with the real viewer" among the passes). No test reads
`openspec/`, so this record, written while the suite ran, is not among its
inputs.

## The film

Nothing to prove on the Curta until the orchestrator exports it again on
the renamed project. Read only: its take (`videos/addition/takes.py`) now
declares `simulation.event_driven:EventDrivenCurta` against
`../../export/event_driven_curta`, which does not exist; the only export
present is the untracked `export/clocked_curta/`, which records no
`source` (refused by `read-the-exports-source` before the take is
reached). Evaluation was not run on it. Once exported, evaluation compares
`Sim(EventDrivenCurta()).identity` with that export's identity; on a
matching export the document is unchanged.

## Findings

1. **The identity depends on the module the model is imported from.** The
   same `counter.py` imported as `models.counter` reports the export's
   identity; imported under another module name it reports another
   (`9f4e30b6…`). A take module that imports its model under a different
   name than the project's models table (for instance through a second
   `sys.path` entry) is refused as another machine. The refusal names the
   model as `module:Class` so the reader can see it, and
   `docs/declaring-a-movie.md` lists "the module it is imported from" among
   the causes. It is the framework's definition of the identity, not
   Videomaker's to change; worth the framework's note if a project meets it.
2. **The framework refuses a state nothing commits** at `Sim`
   construction, so a model edit that adds an uncommitted state never
   reaches the identity comparison: it is refused with the framework's
   words ("the framework does not simulate … as a clocked machine"), as
   before.
3. **The Node side's `take.initial` rule had no test** before this change
   (only Python's mutation tests reached it); the new invalid fixture is
   its first.
4. **A document evaluated before this change from a changed model** still
   carries the export's identity and passes `check`; only evaluating it
   again, or the viewer's `restore` at preview, catches it. No such
   document is known (the Curta's will be re-evaluated on its new export).

## What was not done, and why

- No ADR-020: no new architectural decision; ADR-011 is amended in place
  (its rejected option is now the decision), and the number is released.
- `docs/movie-document.md` and the schema are not changed: the contract
  already says `identity` is the machine identity the export's manifest
  publishes, which is what the document carries.
- The `take.initial` rule is kept, not removed (design D2): it refuses a
  document whose identity is right and whose bank is not every driver and
  state of the machine, which neither the identity nor the replay sees.
- No Node identity check beyond the document's: the commands do not run
  the simulation (non-goal).
- No movie-document spec delta: that requirement already lists the bank-ids
  refusal and its behaviour is unchanged; only its words changed.
- The Curta, the framework and the viewer are untouched; nothing was
  pushed, published or bought.
