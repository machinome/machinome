# Tasks — name the missing file

Red first: every test in section 1 must fail against the current code, for
the stated reason, before anything in section 2 is written. One commit for
the planning artifacts, one for the implementation; no intermediate commits.

## 1. Prove the failure

- [x] 1.1 Extend `tests/stl_project/parts.py` with two classes that declare a
  source that is not a readable file: `AbsentBracket` (`stl_source =
  'no-such-bracket.stl'`) and `DirectoryBracket` (`stl_source` naming a
  directory the test creates beside the fixture). Extend
  `tests/step_project/parts.py` with the same pair for `step_source`
  (`AbsentPart`, `DirectoryPart`). Neither fixture module may be imported
  at collection time in a way that constructs them — they are classes. The
  directory each `Directory*` class names is created and removed by the NEW
  test module's own `setUpModule`/`tearDownModule` (reviewer's note 3):
  `tests/test_missing_source_file.py` must pass on its own, on a clean
  checkout, without `tests/test_stl_node.py` or `tests/test_step_node.py`
  having run.
- [x] 1.2 Add `tests/test_missing_source_file.py`. Against the current code
  each of these fails for the recorded reason:
  - constructing `AbsentBracket` raises `FileNotFoundError` whose message
    contains `AbsentBracket`, `stl_source`, `'no-such-bracket.stl'` and the
    absolute resolved path — RED today: it does not raise at all (it
    constructs, and only `mtime_ns` later raises a message with the path
    alone);
  - the same for `AbsentPart`/`step_source` — RED for the same reason;
  - the same for a `JScadNode` with an absent `jscad_source` and an
    `OpenScadNode` with an absent `scad_source`. There is no fixture project
    for either adapter — `tests/test_meta.py:778-780` writes an
    `OpenScadNode` as source text into a scratch project, and
    `tests/test_builder_reload_resilience.py:68-78` does the same for
    `JScadNode` — so declare both in this test's own scratch module rather
    than adding a project. RED: the JScad one does not raise at
    construction, the OpenScad one raises a message naming only the path;
  - constructing `DirectoryBracket` and `DirectoryPart` raises `ValueError`
    saying the path is not a file — RED today: both construct, and
    `mtime_ns` answers a NUMBER for them (`os.stat` succeeds on a
    directory), so nothing fails until trimesh says `string is not a file`
    or OCCT dumps a flex-scanner failure;
  - a declarative assembly whose class body declares `AbsentBracket` as a
    child IMPORTS cleanly, and instantiating the assembly raises that same
    `FileNotFoundError` — the first half is green today and must stay green
    (it is the deferral the declarative API depends on), the second half is
    RED;
  - a node constructed while its source EXISTS, whose file is then removed,
    still raises a plain `FileNotFoundError` from `mtime_ns` — green today,
    a guard that this change does not move that contract.
- [x] 1.3 Run the new file and record which assertions are red and why:
  `PYTHONPATH="$PWD" .venv/bin/python -m pytest tests/test_missing_source_file.py -x -q`.

## 2. Make it green

- [x] 2.1 Add `require_source_file(klass, attribute, declared, path)` to
  `solid_node/node/sources.py`: raises `FileNotFoundError` when `path` does
  not exist, `ValueError` when it exists and is not a regular file, returns
  `None` otherwise. Message elements per `design.md` §"The change" 3. Use
  `os.path` only — `tests/test_mesh_import_deferred.py` pins that no mesh
  library is pulled in by the node import path.
- [x] 2.2 Call it from each adapter immediately after the path is resolved
  and before `super().__init__`: `stl.py` (after line 170), `step.py` (after
  484), `jscad.py` (after 34), `openscad.py` (after 41, i.e. before
  `coherent_read` at 45).
- [x] 2.3 Re-run `tests/test_missing_source_file.py` green.

## 3. Prove nothing else moved

- [x] 3.1 `tests/test_stl_node.py`, `tests/test_step_node.py`,
  `tests/test_step_assembly.py`, `tests/test_import_step.py`,
  `tests/test_mesh_import_deferred.py`, `tests/test_content_verified_currency.py`,
  `tests/test_source_census.py`, `tests/test_scad_stl.py`,
  `tests/test_jscad_integration.py` — all green.
- [x] 3.1a `tests/test_builder_reload_resilience.py` — green, and read the
  result rather than trusting it: its `VANISHING_JSCAD_PIPE` fixture deletes
  its own source inside `__init__` after `super().__init__()` returns, so the
  new check must see a present file and that test's `FileNotFoundError` must
  still come from `mtime_ns` (`evidence.md`, measurement 5).
- [x] 3.1b Add to `tests/test_builder_reload_resilience.py` a variant of
  `test_missing_initial_foreign_source_reload_waits_for_repair` whose
  `.js` is ABSENT before the node is constructed (not deleted inside
  `__init__`): the builder's `load` wrapper (`builder.py:327-333`) must
  surface an error naming the class and `jscad_source`, stay alive, and
  build once the file appears. RED today only in the message assertion
  (the bare path); the wait-for-repair half is green today and is the
  guard (reviewer's note 4).
- [x] 3.2 `tests/test_cli.py` and `tests/test_manager_new.py` — green: the scaffold writes a `Solid2Node` and
  must be untouched.
- [x] 3.3 The whole suite once before the implementation commit.
- [x] 3.4 Re-run `evidence/run-probes.sh` and record the new messages beside
  the old ones in `evidence.md` under a "After" heading, so the before/after
  is one document.

## 4. Documentation and record

- [x] 4.1 `docs/leaf-nodes.rst`: one sentence in each of the four adapters'
  sections saying the declared file is checked when the node is constructed
  and what the failure names. Do not restate it five times — one shared
  sentence in the external-file discussion and a cross-reference is enough.
- [x] 4.2 `docs/changelog.rst`: one line.
- [x] 4.3 `workflow/warts.md`: mark the
  "# Internal-Cycloidal-Actuator (2026-09-06, STEP import cycles)" second
  bullet fixed, naming this change; add the out-of-scope findings as new
  entries so they are not lost: the builder's wrapper text, and ONE entry
  for the inconsistent missing-declaration refusals (`OpenScadNode` raises
  `TypeError` from `openscad.py:40`; `JScadNode` raises a bare `Exception`
  not naming the class, `jscad.py:28-30`; `StlNode`/`StepNode` raise
  `ValueError` naming it).
- [x] 4.3a (amendment, corrected) `solid_node/node/sources.py`: add
  `MissingSourceFile(FileNotFoundError)` per the design's Correction and
  raise it for the absent case; the `ValueError` for the directory case
  gets `error.filename = path` after construction.
  `solid_node/core/builder.py` `_on_reload_exception`: on the reload path,
  include `getattr(exc, 'filename', None)` in the sources given to
  `_watch_broadly`. Then `tests/test_builder_reload_resilience.py` fully
  green (the 3.1b test included), `tests/test_missing_source_file.py`
  green, and the full suite ONCE more, recorded in `evidence.md` under
  "## Reload-repair regression — fix" with the summary line and exit code.
- [x] 4.4 Sync the three spec deltas into `openspec/specs/` and archive the
  change.

## 5. Not in this change

- `OpenScadNode`'s missing `scad_source` `TypeError`.
- The builder's `failed to inspect initial sources project` wrapper text.
- `Internal-Cycloidal-Actuator`'s `source.require()` preamble: it still adds
  the extract command, which the framework cannot know. Leave it.
