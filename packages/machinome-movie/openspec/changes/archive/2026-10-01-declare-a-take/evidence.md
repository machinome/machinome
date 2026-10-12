# Implementation evidence

## Authority and scope

Cycle 1 of Videomaker's curta-video campaign, on branch `declare-a-take`
(worktree `WTs/declare-a-take`), cut from `curta-video` at `4ecbc51`, which
carries the orchestrator's take contract (`docs/movie-document.md`, "The
take"; the schema's `take` block). The spike's note was not on the base and
was not read. The contract page and the schema were not changed. Nothing
was pushed or published; no network or paid request was made; nothing was
installed. The framework was reached through its public `Sim` and its
`machinome export` command, run once from the fixture project; its tutorial
counter was read to be copied. Integration into `curta-video` is the
orchestrator's. Two other agents (the spike and `reframe-join`) worked in
their own worktrees at the same time; the machine's load is given with each
timed run.

Environment: Linux, 16 cores, Python 3.12 from the workspace venv
(framework editable at `6a575f0`), Node v24.11.1, vitest 5.0.3, Playwright's
Chromium, the viewer bundle
`machinome-viewer/machinome_viewer/widget/dist/machinome-viewer.js` (API 28)
passed in the environment.

## Red

The tests were written first: `python/tests/test_take.py` (layer 1:
declarations, refusals, the recording, purity, and the document check of
take documents), the count movie and its take in the fixture project,
`count` registered in `fixtures/manifest.json`, and layer 2 and 9 pins in
`test_fixtures.py`, `test_cli.py` and `test_repository.py`. Run on the
unchanged package (`python -m pytest -q -p no:cacheprovider
--continue-on-collection-errors` in `python/`, about 01:15):

    ERROR tests/test_declarations.py
    ERROR tests/test_evaluation.py
    ERROR tests/test_take.py
    14 failed, 76 passed, 3 errors in 11.49s

    E   ImportError: cannot import name 'Mark' from 'machinome_movie' (.../python/machinome_movie/__init__.py)
    FAILED tests/test_fixtures.py::test_the_take_fixtures_are_there - AssertionEr...
    E         Extra items in the left set:
    E         'take-block-missing'
    E         'take-bank-differs'
    E         'take-identity-differs'
    E         'take-model-time-past-the-end'
    E         'take-step-input-unknown'
    FAILED tests/test_fixtures.py::test_document_is_the_evaluation_of_its_movie[count]
    E       FileNotFoundError: [Errno 2] No such file or directory: '.../python/tests/fixtures/project/export/counter/source-revision.txt'
    E       AssertionError: assert ('models/counter.py' in 'Fixture project of the Videomaker test suite. It grants nothing and carries\nno licence of its own; ...')
    E       AssertionError: assert '(`declare-a-take`' in '# Changelog ...'
    E       AssertionError: assert '\n## The take, clocked\n' in '# Declaring a movie in Python ...'
    E       assert 'running machines are refused' in "# Videomaker Build narrated educational videos ..."

Layer 1's red is the missing declarations (the fixture take imports `Mark`,
`Move`, `Take`, `Trigger`, so the seesaw's tests fail to import too); the
`minimal`, `tour` and CLI failures are the same import through the fixture
project's `videos/takes.py`. Layer 2's and layer 9's are the behaviour they
pin. Because layer 1's first red is an import, the behaviour behind it was
proved by removing checks one at a time (below).

Green after the change: `273 passed in 11.68s`; the layer 1 tests went green
at the first run of the implementation (`177 passed`), except the model
block, which needed the counter export's revision the pin script then wrote.

## Mutations (task 3.4), each restored byte for byte

A scratch script outside the repository replaced one check at a time,
ran `tests/test_take.py` and `tests/test_fixtures.py`, restored the file
and compared its sha256 (every restore matched):

| check removed | went red |
|---|---|
| the replay comparison (`document.py`) | `4 failed, 143 passed`: the three replay mutations of `test_a_take_document_is_refused_naming_its_fault` and the invalid fixture `take-bank-differs` |
| the stop refusal (`evaluate.py`) | `1 failed`: `test_a_step_the_machine_stops_before_it_travels` |
| the framework-refusal wrapping (`evaluate.py`) | `1 failed`: `test_a_request_the_framework_refuses` |
| the document's model-time check | `3 failed`: two document mutations and the invalid fixture `take-model-time-past-the-end` |
| the class-creation model-time check (`take.py`) | `3 failed`: `test_model_time_outside_the_take` for 9, 8.5 and 8.25 |
| the input check against the export | `2 failed`: the document mutation and `take-step-input-unknown` |
| the identity check | `2 failed`: the document mutation and `take-identity-differs` |
| the refusal of a missing take block | `2 failed`: the document mutation and `take-block-missing` |
| the refusal of two marks at one instant | `1 failed`: `test_two_marks_at_one_instant` |

## The fixture

- `models/counter.py`: the tutorial's chapter 9 with the classes of
  chapters 3, 4 and 8 it imports, unchanged but for imports; header naming
  `docs/tutorial/counter/`, framework commit `6a575f0` and the framework's licence;
  `models/digits.svg` byte-identical (`cmp`). `NOTICE` says both keep their
  licence.
- `export/counter/`, written by `machinome export counter -o export/counter
  --no-widget` from the fixture project in 5.5 s: `manifest.json` (version
  8, drivers `crank`, states `units` and `tens`, instruction `Turn once`,
  `clocked.identity`
  `d46d4f1ee76199bce9aa9924e34a97020fd28bd3073939a2a85ec0eceb1111d6`) and
  four meshes, 134 KB together. A probe confirmed the identity the `Sim`
  computes over `models.counter.Counter` equals the export's (read on the
  private attribute once, for this evidence only; the package does not).
- `Turns` records 8 s: step-1 `Turn once` (0 to 360, one commit, units 1),
  step-2 `Move(Counter.crank, to=3240, over=4)` (360 to 3240, eight
  commits at fractions 1/8 to 1, units 2 to 9), step-3 `Turn once` (3240 to
  3600, the carry: units 0, tens 1); marks `one` 2, `nine` 6, `ten` 8.
- The pin script wrote revision `80da5915b97a8dc2397ecf6693bff4a19b41ac99`
  to both exports; `minimal` and `tour` changed only in `sourceRevision`,
  and `scripts/pin-resolved.mjs minimal tour` changed only that line in each
  resolved pin (reviewed: `2 insertions(+), 2 deletions(-)`). The pin script
  then reported every revision and document unchanged.
- `fixtures/takes/count/counting.json` follows the recipe (0.06 s a
  character, duration plus 0.1 s, one-space indentation); the generator was
  checked first against `minimal/only.json` and three of the tour's takes,
  byte for byte (`balance` differs by its replacement, as it should).
- The five invalid documents are mutations of `count.json`, written in the
  format of the existing ones (a round trip of `unknown-part.json` through
  the writer reproduced its bytes).

Evaluating `count`: 0.176 s the first time in a process (the clocked
executor's import included), 0.016 s again; `tour` 0.020 s (01:2x, load
about 9, the Node suite running).

## The suites on the final content

- **Python**, `python -m pytest -q` in `python/` (01:39, load 17.7):
  `273 passed in 15.82s`.
- **Node**, `VIDEOMAKER_VIEWER_BUNDLE=<bundle> npm test` (started 01:25:38,
  load rising from 0.7 to about 17 with the other agents' work), on the
  final content but `tasks.md` and this file, which no key reads:

      Test Files  1 failed | 31 passed (32)
           Tests  2 failed | 325 passed (327)
        Duration  776.83s (tests 99%, import 1%)
      Test memo: 0 passed from the memo, 327 run

  Every slow test ran cold (the fixture project changed, so every key
  missed); the viewer layer ran: `✓ |viewer| test/viewer/real-viewer.test.mjs
  (6 tests) 138519ms`.

### The Node red, by design (task 5.2)

Both failures are in `test/movie-document.test.mjs`, the shared-fixture
tests of layer 2:

    FAIL  |pure| test/movie-document.test.mjs > every registered document validates, passes its checks and resolves to its pin, twice identically, on the frame grid
    AssertionError: fixture count has no pinned resolution fixtures/resolved/count.json

    FAIL  |pure| test/movie-document.test.mjs > every invalid fixture is refused by the static checks, naming every word it must
    AssertionError: take-bank-differs.json was not refused

- The first: Node's static `checkMovie` *accepts* `count.json` (it knows no
  take rule and does not look at `timeMode`; only `loadMovie`'s project
  check refuses a non-loop document), and the pin is absent because no
  resolution of a take document exists yet. `pose-a-take` writes
  `resolved/count.json` once Node resolves a take (the bank per frame), for
  a person to review.
- The second stops at the first take fixture. Run alone through
  `checkMovie` (a scratch script, not the suite), **none** of the five is
  refused by Node today: `take-bank-differs`, `take-block-missing`,
  `take-identity-differs`, `take-model-time-past-the-end` (Node's model-time
  range check is in `loadMovie`, against `animation.loop`, not in
  `checkMovie`) and `take-step-input-unknown` each print `NOT REFUSED`.
  `pose-a-take` makes the static checks refuse each with its words.

No Node source was changed. `scripts/pin-fixture-project.mjs` (a fixture
tool) now writes every export's revision.

## Archive

`openspec archive declare-a-take --yes` warned that the proposal's Why
exceeds 1000 characters (non-blocking) and that 2 of 17 tasks are open (0.2,
the orchestrator's review; 6.1, owed to `pose-a-take`), then applied
`declarative-movie` `+ 2 added, ~ 1 modified` and `movie-document`
`+ 2 added`. Checked: the modified requirement is replaced in place, the
added ones are appended at each file's end, nothing else moved, and each
file still ends as it did. `openspec validate --specs --strict`:
`Totals: 16 passed, 0 failed (16 items)`.

## Findings

1. **The brief and the contract disagree on a mark before every step.** The
   brief asks to refuse "a mark before any step"; the contract says "a mark
   at 0 is the initial bank". The contract was built: `Mark("rest")` first
   is `rest` at 0 with `initial` as its bank, and a test pins it. Smallest
   correction, if the refusal is wanted: delete the parenthetical in
   `docs/movie-document.md` and refuse in `Take._time` when `schedule` is
   empty at a mark (one line); otherwise nothing.
2. **The framework's `Sim` does not publish its machine identity.** It is on
   `sim._clocked.identity`, private; the brief's "refuse a `Sim` whose
   identity differs, if the framework exposes it" is therefore not done.
   The document check compares the recorded bank's ids with the export's
   drivers and states instead (a test copies the export and drops `tens`:
   refused naming `take.initial` and `tens`); a law changed with the same
   ids is caught only where the viewer restores with the document's
   identity (`pose-a-take`). Smallest correction: a public `Sim.identity`
   (a framework change, for the pilot), then one comparison in `_record`.
3. **Python did not and does not check a loop's model time against its
   period**; Node does, at load. The new range check is the take's only, to
   leave the posed loop unchanged.
4. **Node's static check accepts every take fixture today** (above), so the
   red is wider than the absent pin: `pose-a-take` owes the five refusals
   in `checkMovie`, not only the resolution.
5. **The counter export's mesh names hold commas and `=`**
   (`counter-Base,bore=8.2,post_height=36.0,post_offset=28.0-8ba03b76c773.stl`),
   as the framework names parametrised parts. The layer 6 asset server of
   `pose-a-take` must serve them; the seesaw's names never tested that.
6. **Step ids are `step-<n>`**, not the contract example's authored ids
   (`set-3`, `stroke-23`); the contract fixes only that an id is a slug. A
   refusal at class creation names the step as written instead.
7. **The framework's `Stop` fields are recorded under their own names**
   (`coordinate`, `side`, `bound`, `value`, `input`, `fraction`); the schema
   leaves a stop open, so `pose-a-take` should read these names (the
   fixture `count` has no stop; `test_a_step_stopped_part_way_is_recorded_with_its_stop`
   shows one: crank 50 back by 30 lands at 36, admitted -14).
8. **Constructing the `Sim` reads the project's `pyproject.toml` about
   thirty times** (and looks for `models/pyproject.toml`); harmless, and the
   purity test allows exactly those files besides the evaluation's own.
9. **A zero-travel step is admitted and recorded** (no stop, `admitted` 0,
   origin equal to end): a hold the film may use; only a step the machine
   *stopped* at zero travel is refused.
10. **The brief's name `Tally` for the fixture take collides** with the
    tour's project element `Tally`, which the manual teaches; the take is
    `Turns`.

## What was not done, and why

- The Node side: loading `timeMode: "take"`, the bank per frame, the
  stage's `restore`, the viewer double's machine, the five refusals in
  `checkMovie`, the resolved pin of `count`, and layer 6 parity: the
  `pose-a-take` change.
- No identity comparison with the `Sim` (finding 2) and no framework change.
- No trigger of an instruction declared on a part: its qualified name is
  the tree's, the film's instruction is its root's (a move can name a
  part's driver by its qualified id).
- No refusal of a mark before every step (finding 1).
- The spike's note was not on the base and was not read.
- The narration of the count fixture was not spoken: its take is the
  recipe's double, as every fixture's is.
