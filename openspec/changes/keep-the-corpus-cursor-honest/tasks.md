Bench: `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch
`fix-warts-3`.

- Every framework command runs as
  `env -C <bench> PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/<tool> ...`.
- `<scratch>` is the campaign scratchpad's `cycle7/` directory
  (`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle7/`).
  It holds Stage P's `reproduce.py`, `compare_corpus.py` and
  `probe_tests.py`, their `.out` logs, and the two regenerations
  `running-corpus.as-is.json` and `running-corpus.reset.json`.
- `<corpus tests>` = `tests/test_running_corpus.py
  tests/test_clocked_corpus.py tests/test_time_drive_corpus.py`.

Rules for the whole cycle:

- Run one test run or generation of ours at a time, since runs share
  `tests/_build`.
- Every test marked RED in section 2 is run and seen red, for the reason
  it names, before the code that turns it green.
- Never write a committed corpus. `tests/running-corpus.json`,
  `tests/clocked-corpus.json` and `tests/time-drive-corpus.json` stay
  byte-identical. A generator is run only with an output path under
  `<scratch>`. If any task shows the change altering a value in a
  committed corpus, stop: record the diff in `evidence.md` and report.
- Do not run the Curta or any project. Write nothing in the
  `machinome-viewer` checkout.
- Record every command and its result in `evidence.md` as you go, in the
  shape of `openspec/changes/archive/2026-10-04-scad-presentation/evidence.md`.

## 1. Baseline on the unmodified tree

- [ ] 1.1 Create `evidence.md` with the bench commit (`git -C <bench>
  rev-parse HEAD`) and the interpreter check: `python -c 'import
  machinome; print(machinome.__file__)'` prints a path under the bench.
  Copy the source of `<scratch>/reproduce.py` into `evidence.md`, because
  the scratchpad is not durable.
- [ ] 1.2 Run `<scratch>/reproduce.py` from the bench. Expect design.md
  Context's output: step 1 records one crossing and one stop, step 2
  records none, and the run holds one of each after step 2.
- [ ] 1.3 Run `pytest -q -p no:cacheprovider <corpus tests>`, and record
  the counts and wall time (Stage P: `57 passed, 241 subtests passed`).

## 2. Tests

- [ ] 2.1 RED, the generator (`tests/test_running_corpus.py`). Add
  `RESTORE_AND_STOP` and `ONE_STEP` at module level, as design.md
  Decision 2 gives them. Add
  `test_the_generator_records_a_stop_made_in_the_step_that_restores` to
  `CorpusReplayTest`, after `test_every_step_is_present`. It asserts:
  - two ticks;
  - one crossing and one stop in the first;
  - the second equal to the first;
  - the second equal to `run_machine(ONE_STEP)[0]`.

  Red today, because the second tick's `crossings` and `stops` are `[]`.
- [ ] 2.2 RED, the replay (same class). Add
  `test_the_replay_refuses_an_entry_missing_a_record_made_after_a_restore`
  as design.md Decision 2 gives it: `self.replay` of the entry whose ticks
  are `[once, once]` passes, and the same entry with the second tick's
  `crossings` and `stops` emptied raises `self.failureException`. Red
  today: the honest entry is refused with `0 != 1 : StopAndJump tick 1`.
- [ ] 2.3 Run section 2's two tests on the unmodified tree. Record each
  one's failure line.

## 3. The change

- [ ] 3.1 `tools/generate_running_corpus.py::run_machine`: after
  `apply_action(...)` in the action loop, if the action restores, set
  `crossings_seen = stops_seen = 0`, with design.md Decision 1's comment.
- [ ] 3.2 `tests/test_running_corpus.py::CorpusReplayTest.replay`: the same
  two lines after `self.apply(...)`.
- [ ] 3.3 Run section 2's tests: both are green. Run `<corpus tests>`: the
  counts are 1.3's plus two tests.

## 4. The corpora after the change

- [ ] 4.1 Run `tools/generate_running_corpus.py
  <scratch>/running-corpus.after.json`. Expect exit 0 and the summary line
  (28 scenarios, 401 ticks). With a `python -c` that reads files only,
  compare it with Stage P's `<scratch>/running-corpus.as-is.json`: every
  scenario's `name`, `dt`, `steps`, `script` and `ticks` are identical.
  Record the result.
- [ ] 4.2 Run `<scratch>/reproduce.py` again. Step 2 now records one
  crossing and one stop, equal to step 1's.
- [ ] 4.3 `git -C <bench> status --short tests/` lists only
  `tests/test_running_corpus.py`, and no corpus file.

## 5. Changelog

- [ ] 5.1 Append design.md Decision 3's bullet to the one `Unreleased`
  section of `docs/project/changelog.rst`, after its existing bullets.
- [ ] 5.2 Grep `docs/` (excluding `adrs/` and `releases/`) and
  `CONTRIBUTING.rst` for `generate_running_corpus` and `running-corpus`.
  Confirm that no page says something this change makes wrong, and record
  the result.

## 6. Checks

- [ ] 6.1 Run `black --check` and `flake8 --max-line-length=89` on
  `tools/generate_running_corpus.py` and `tests/test_running_corpus.py`.
- [ ] 6.2 Run the full suite once, alone (`pytest -q -p no:cacheprovider`
  at the bench root), and record the counts and wall time. Run it after
  8.2, on the final tree. A failure that is not this change's is recorded
  and stopped on, not worked around.

## 7. Warts

- [ ] 7.1 Move the whole section "# Corpus record cursor across restore
  (2026-09-20)" of `workflow/warts.md` verbatim, from its heading's next
  line ("**Status: observed while validating Curta; ...") to "...to
  repair evidence collection.", to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md`. Put it under a
  heading `` ## `keep-the-corpus-cursor-honest` ``, after the last entry,
  with a line "From "Corpus record cursor across restore (2026-09-20)":".
  Add a "What shipped" paragraph. It says that the generator and the
  replay count a step's records from the cleared rings after a restore;
  that the two tests are red-first on `StopAndJump`, crossings and stops
  alike; and that no committed corpus changed. Delete the section from
  `warts.md`.
- [ ] 7.2 File design.md Open Question 2 in `warts.md`, after the section
  "## Findings from the framework cycle `name-solids-by-path`
  (2026-10-06)", as a new section "## Findings from the framework cycle
  `keep-the-corpus-cursor-honest` (2026-10-06)". It holds one bullet,
  **The crossing and stop rings are bounded in entries, not ticks**, with
  the facts of the Open Question: `_ring(record)` is `deque(maxlen=record)`
  for all three rings; a run with more than `record` crossings drops the
  oldest ones; a corpus counter cannot advance past a full ring; the
  generator sizes `record` as `steps + 1`; and the fullest committed
  scenario holds 3 entries in a ring of 9. Add the triage line "Not
  reached by any corpus; a generator guard or a change to the ring's unit
  is a decision of its own", unless the orchestrator's review answered
  otherwise.

## 8. Sync and archive

- [ ] 8.1 Sync the delta into `openspec/specs/export/spec.md`, replacing
  "The two runtimes share a conformance corpus". Diff the requirement
  against its baseline: only the added paragraph and the added scenario
  differ.
- [ ] 8.2 Archive the change to
  `openspec/changes/archive/2026-10-06-keep-the-corpus-cursor-honest/`.
  Then `openspec validate --specs` passes.
- [ ] 8.3 Run section 2's tests and `<corpus tests>` once more, and record
  the result. Leave everything uncommitted.
