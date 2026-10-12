# Implementation evidence

## Authority and scope

Planning commit `489e658` (proposal, design, delta spec, tasks, ADR-002 as
Proposed). The orchestrator reviewed it and ratified it on 30 September 2026
with one correction to D13: install `jsonschema` from the package index into
the workspace venv (the no-network rule covers the package's code and tests,
not `pip`), declare it as a dependency, validate with it, and drop the
subset validator the first D13 had planned. Done before any code was
written: `pip install jsonschema` installed jsonschema 4.26.0 (with
referencing 0.37.0, rpds-py 2026.6.3, jsonschema-specifications 2025.9.1);
no subset validator was ever written. The package itself was installed with
`pip install --no-index --no-deps --no-build-isolation -e python`.

Nothing was written in the Leonardo repository, the framework, the viewer,
the studio or any other worktree. Nothing was pushed or published.

## Red / green chronology

All runs: `/home/asa/devel/machinome/.venv/bin/python -m pytest -q` from
`python/` (pytest 9.1.1, Python 3.12.3).

1. **R1.** `tests/test_declarations.py` written first, against an empty
   package: collection error, `ImportError: cannot import name 'Camera' from
   'machinome_movie'`.
2. **R2.** All five test modules written, package still empty: four
   collection errors (`test_declarations`, `test_evaluation`,
   `test_fixtures`, `test_repository`: `cannot import name 'Camera'` /
   `'dumps'`), and `test_cli.py` 5 failed, each `No module named
   machinome_movie.__main__`.
3. **G1.** After `names`, `anchors`, `take`, `stage`, `movie`, `evaluate`,
   `document`, `project` and `__main__`: `test_declarations.py` 29 passed.
4. **R3.** `test_evaluation.py`: 5 failed, 20 passed. Two were the fixture
   export lacking `source-revision.txt` (not yet pinned); three were test
   defects, corrected: a comparison of the evaluated dict's key order (key
   order is fixed only by `dumps`, so the test now compares the key set),
   and a `NameError` in a test helper whose class body assigned `export`
   from an enclosing `export` (a class body that assigns a name cannot read
   the enclosing one; the parameter was renamed).
5. **G2.** `source-revision.txt` pinned to `db6f30a503215756f57131c2287a7437e869f6b4`,
   the commit the fixture README's recipe makes; `test_evaluation.py` 25
   passed.
6. **R4.** `test_fixtures.py` and `test_cli.py` before any fixture document
   existed: 3 failed, 4 passed, 2 skipped (the two parametrized tests had no
   parameters): no registered documents, no `fixtures/invalid/`, and the CLI
   test's pinned `fixtures/documents/minimal.json` missing.
7. **G3.** `fixtures/documents/minimal.json` and `tour.json` written by
   evaluation (`out` = the fixture file), registered in
   `fixtures/manifest.json`; seven invalid fixtures written, each a one-field
   mutation of `minimal`.
8. **R5.** Full suite: 4 failed, 76 passed; the failures were the records
   (`docs/declaring-a-movie.md` absent, three tests; `CHANGELOG.md` absent).
9. **Green.** After the manual page, the README link and the changelog:
   **80 passed** (test_cli 5, test_declarations 29, test_evaluation 25,
   test_fixtures 11, test_repository 10), in about 10 s.

### Mutation spot-checks

Because the declaration tests' first red was the missing package, five
checks were then removed one at a time, the named tests run, and the source
restored byte for byte (verified with `cmp`):

- slot read returning one cached key: `test_slot_filled_twice` red (did not raise);
- the repeated-phrase check disabled: `test_phrase_repeated_in_the_narration` red;
- the project set/element guard disabled: `test_project_defined_set` and
  `test_project_defined_element` red;
- the export path check disabled: `test_part_path_the_export_lacks` red (the
  document check still refuses the path, but without the written spelling);
- a view's camera not carried to the next shot:
  `test_the_views_camera_persists_into_the_next_shot` and the `tour` fixture
  document red.

## Acceptance against the validation film's draft source

The "The Python source" block of the Leonardo project's
`videos/cut_and_advance/spec.md`, as it stood when checked (it had by then
received the `wide` view correction of design D3 upstream), was copied to
the scratch directory with only its seven relative paths made absolute
(export, source, still, two evidence files, licence, description) and
evaluated with the Leonardo project on `sys.path` and
`PYTHONDONTWRITEBYTECODE=1`, writing only in the scratch directory:

- importing the movie module (and so the model) took 4.8 s; evaluation took
  0.02 s; two evaluations were byte-identical (22 607 bytes);
- five chapters, eleven shots: `question` (`hook`, `question`), `drive`
  (`wheel`, `coupling-shot`, `stroke`), `feed` (`pawls-shot`), `ropes`
  (`shaft`, `carriage-shot`), `closing` (`rhythm`, `still`, `invitation`);
- `model.expectedDurationSeconds` 1460 and `sourceRevision`
  `28b43bce1b88446995f0ff231dd9075d1a839ab3`, read from the real export;
- parts resolved to export names, e.g. `Mill.feed.pawl` to
  `["Feed mechanism", "Driving pawl"]`, `Mill.water_drive.waterwheel` to
  `["Water drive", "Undershot waterwheel"]`; the layers equal the ones the
  project's hand-written `production.yaml` files carry;
- `lines.end()` became `{"spokenEnd": "moment"}`, `"stroke"`,
  `"progress"`, `"blade"`, `"description"` for the five narrations.

The four refusals the film's acceptance names, each on a mutated copy:

- misspelled part path `Mill.feed.pawll`: the framework refuses at the line,
  `'feed.pawll' names nothing: FeedMechanism declares no port, joint or child
  called 'pawll'`;
- unknown camera `Sawmill.pawlz`: Python refuses, `type object 'Sawmill' has
  no attribute 'pawlz'. Did you mean: 'pawls'?` (a camera of another take is
  refused by this package, naming both takes);
- absent phrase: `Drive.wheel: until: the phrase 'In the modle' is absent
  from the chapter's narration`;
- a project set: `Set Gears is declared by the project; a project's own set
  needs the React stage, which does not exist yet. Use Paper, PaperSplit or
  SourceOnly.`

## Not claimed

- The Node side's loading of these documents, the speech doubles under
  `fixtures/takes/` and `fixtures/resolved/`: the parallel `movie-document`
  change's.
- The film itself, its speech, preview and render: the campaign's cycle C.
- Slow layers (5 to 8) do not exist for Python and were not run; nothing in
  `src/` changed, so the Node suite was not rerun.
