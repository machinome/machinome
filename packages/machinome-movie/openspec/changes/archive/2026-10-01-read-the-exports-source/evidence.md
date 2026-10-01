# Implementation evidence

## Authority and scope

Cycle 8 of Videomaker's addition-warts campaign, `read-the-exports-source`:
wart 9 of *Addition*, its Videomaker side, and the pilot's ruling of
1 October 2026 that the framework's export records its source revision in
`manifest.json` (the framework's ADR-158, in its `main` at 096217f and
installed in the workspace venv). Branch `read-the-exports-source`
(worktree `WTs/read-the-exports-source`), cut from `addition-warts` at
`500ebca`; the planning commit is `3388afe`. Nothing was pushed or
published; no network or paid request was made; nothing was installed. The
framework, the viewer and the Curta and Leonardo projects were not
changed; the framework was reached only through its command
(`machinome export`, the workspace venv's) and its spec and ADR, read. The
viewer was reached only through the API 29 bundle selected by path, never
written into the repository. Integration into `addition-warts` is the
orchestrator's.

Two sentences of the planning commit were corrected during the
implementation, in this change's own records: the delta spec said the
refusals come "before any take, picture or browser is used", and the
design said the same of the loaders. `check` of a movie that shows a
picture or reframes measures its layout in Chromium before it loads the
film, and `speech` of a movie generates missing takes before it loads it,
as they did when the sidecar was read in the same load; the requirement now
says "when they load the film and before any frame is posed", and the
design says where each loader refuses (finding 3).

Environment: Linux, Node v24, vitest, Playwright's Chromium, Python 3.12
from the workspace venv, the framework at 096217f. Other agents ran suites
in other worktrees at the same time; durations are not comparable across
runs.

## The fixture exports, made again

`scripts/pin-fixture-project.mjs` now exports each model from the recipe
commit (design D6). Its first run refused, as it should, on the second
export: the first export's build had left `_build/counter/` untracked in
the recipe copy, so the framework recorded the seesaw's export dirty:

    export/seesaw: the framework recorded source {"revision":"10b189d1516c880a7fdab7370fa9d32866945db6","dirty":true}, not the recipe commit 10b189d1516c880a7fdab7370fa9d32866945db6 clean; the recipe copy must be a clean Git work tree when the model is exported

The copy now ignores `/_build/` in its own `.git/info/exclude`, outside
the commit (the recipe's hash is unchanged). The second run:

    node scripts/pin-fixture-project.mjs --python <venv>/bin/python --machinome <venv>/bin/machinome
    Export counter: made from 10b189d1516c880a7fdab7370fa9d32866945db6, manifest changed, written to python/tests/fixtures/project/export/counter.
    Export seesaw: made from 10b189d1516c880a7fdab7370fa9d32866945db6, manifest changed, written to python/tests/fixtures/project/export/seesaw.
    Revision: 10b189d1516c880a7fdab7370fa9d32866945db6, recorded by every export's source.
    Document minimal: unchanged.
    Document tour: unchanged.
    Document count: unchanged.

Both manifests differ from the committed ones by the parts' `mtime` (the
copy's files are new) and by the trailing record
`"source": {"revision": "10b189d1516c880a7fdab7370fa9d32866945db6", "dirty": false}`;
no STL changed, and both `source-revision.txt` files are deleted. The
fixture documents already pinned that revision, so none changed, and no
resolved pin moved (`scripts/pin-resolved.mjs` was not needed; the Node
suite's pins of `resolved/` pass unchanged).

## Red

Each red was run before the code it proves was written, on the fixtures
as they were (no `source` in either manifest, both sidecars present). The
Node reds ran cold (`VIDEOMAKER_TEST_COLD=1`).

### Layer 1 (`python -m pytest -q`)

    FAILED tests/test_evaluation.py::test_model_block_and_paths_relative_to_root
    FAILED tests/test_evaluation.py::test_evaluation_opens_only_the_manifest_and_emphasised_excerpts
    FAILED tests/test_evaluation.py::test_export_without_a_source_is_refused_by_name
    FAILED tests/test_evaluation.py::test_export_whose_source_revision_is_not_a_commit_is_refused
    FAILED tests/test_evaluation.py::test_a_dirty_export_is_evaluated_from_its_revision
    FAILED tests/test_repository.py::test_the_fixture_revision_is_a_reproducible_commit_of_the_project
    FAILED tests/test_take.py::test_the_model_block_and_the_marks - KeyError: 'so...
    FAILED tests/test_take.py::test_recording_reads_no_clock_randomness_network_or_cad
    8 failed, 280 passed in 18.75s

The assertions, verbatim: the refusal of an export without `source` (a
sidecar naming the pin beside it) did not happen, because the sidecar was
read instead,

    >       with pytest.raises(MovieError) as refusal:
    E       Failed: DID NOT RAISE MovieError

evaluation opened the sidecar,

    E       AssertionError: assert {PosixPath('/...s/seesaw.py')} == {PosixPath('/...s/seesaw.py')}
    E         Extra items in the left set:
    E         PosixPath('…/python/tests/fixtures/project/export/seesaw/source-revision.txt')

(and the counter's, in `test_take.py`), a dirty export's recorded revision
was not the one written,

    E       AssertionError: assert '10b189d1516c...9d32866945db6' == 'abababababab...babababababab'

and the fixture manifests recorded no source (`KeyError: 'source'`;
`assert None == {'revision': '10b189d1516c880a7fdab7370fa9d32866945db6', 'dirty': False}`).

### Layer 8, the movie's pin (`test/pipeline/movie-pipeline.test.mjs`)

`check` of the `minimal` fixture movie with the manifest's `source`
removed and a sidecar naming the pin beside it passed:

     × check reads the revision from the export's source: none is refused by name, a malformed one by its field, a differing pin naming both 1164ms
    AssertionError: Minimal: 1 chapters, 1 shots, 1.2s; model 20s
      only: take 0.64 s, chapter 1.20 s, tail 0.36 s
    Stage: bundled /tmp/videomaker-movie-UpuETZ/videos/minimal/_build/stage/stage.js (sha256 83ffe7b65133) and stage.css (sha256 3ae2d4954839) from the runtime alone; no module to type-check
    Project tree: dirty at check, 3 paths differ from its head 10b189d1516c (export/, videos/minimal/_build/, viewer-double.js); a render now records a head that is not the content rendered and is not release-ready
    Videomaker tree: dirty at check, 6 paths differ from its head 3388afe07f03 (…); a render now records a head that is not the tool that rendered and is not release-ready

    0 !== 1
     ❯ refusedWith test/pipeline/movie-pipeline.test.mjs:399:12

### Layer 8, the export's dirt (`test/pipeline/provenance.test.mjs`)

The clean export said nothing:

    AssertionError: The input did not match the regular expression /^Export: made from adefd1aab4eb, clean$/m. Input:
    'Provenance test: 1 chapters, 1 shots, 2s; model 2s\n' +
      '  a: no cached take, chapter 2.00 s\n' +
      'Stage: bundled /tmp/videomaker-yaml-JfNFS5/_build/stage/stage.js (sha256 6a6ea98f11d2) and stage.css (sha256 1bcc570d15aa) from the runtime alone; no module to type-check\n' +
      'Project tree: clean at 91f7e50694bf\n' +
      'Videomaker tree: dirty at check, …\n'

nor did the dirty one, at render:

    AssertionError: The input did not match the regular expression /^Export: made from adefd1aab4eb, dirty: Git listed changes in the project when the model was exported; the manifest's exportRevision is not the content exported, and the film is not release-ready$/m. Input:
    'Provenance test: 1 chapters, 1 shots, 2s; model 2s\n' +
      'Project tree: clean at 91f7e50694bf\n' +
      …

### Layer 9 (`test/repository.test.mjs`)

Written after the manual pages; its red was shown by putting `README.md`,
`docs/FORMAT.md`, `docs/declaring-a-movie.md`,
`docs/architecture-overview.md`, `fixtures/README.md`, `CHANGELOG.md` and
`docs/adrs/README.md` back to the planning commit's bytes, then restoring
them:

     × the manual reads the revision from the export's source and names no sidecar (read-the-exports-source) 28ms
    AssertionError: fixtures/README.md names no sidecar

## Green

The changed pipeline tests, cold, after the change:

     ✓ |slow| test/pipeline/movie-pipeline.test.mjs (15 tests | 14 skipped) 3571ms
       ✓ check reads the revision from the export's source: none is refused by name, a malformed one by its field, a differing pin naming both 3568ms
     ✓ |slow| test/pipeline/provenance.test.mjs (2 tests) 14920ms
       ✓ check, render and preview say whether the project tree was dirty, and a dirty render is not release-ready 7251ms
       ✓ check, render and preview say whether the export was made from a dirty tree, which is not release-ready, never refused and no key 7669ms
     Test Files  2 passed (2)
          Tests  3 passed | 14 skipped (17)
    Test memo: 0 passed from the memo, 3 run

## Suites on the final content

The whole Node suite (`npm test`), with `VIDEOMAKER_VIEWER_BUNDLE` naming
the API 29 bundle (the viewer layer ran: `real-viewer.test.mjs` 7 tests,
`take.test.mjs` 5 tests). Every slow verdict ran fresh, since
`src/render.mjs`, `src/provenance.mjs` and the fixture exports are in
their keys; no pass came from the memo:

     Test Files  40 passed (40)
          Tests  390 passed (390)
       Duration  903.43s (tests 98%, import 1%, transform 1%)
    Test memo: 0 passed from the memo, 390 run

The Python suite (`python -m pytest -q` in `python/`, the workspace venv):

    288 passed in 17.70s

The change validated strictly before the archive
(`openspec validate read-the-exports-source --strict`: valid, with the
warning that the proposal's "Why" exceeds 1000 characters). `openspec
archive read-the-exports-source --yes` (it warned of the one open task,
0.3, the orchestrator's review) applied one modified requirement to
`declarative-movie` and one added and one modified to
`educational-video-production`; the synced text was checked against the
deltas. The specs after the archive: `openspec validate --specs --strict`,
`Totals: 16 passed, 0 failed (16 items)`.

The suites ran before the archive; the archive moved only OpenSpec records
and this file, which no test reads (the pure project was run again after
it: `Test Files  24 passed (24)`, `Tests  243 passed (243)`; and the
Python suite again: `288 passed in 13.06s`).

## The common key

The export's `source` enters no key: `render` hashes the manifest for the
common key with `source` removed (`withoutSource`), and serves and records
the file as it is (`hashes['/model/manifest.json']`, `modelSha256`). The
provenance test renders a YAML fixture from a clean export, then from the
same export marked `dirty: true`, and asserts the same `commonKey`, 0
frames captured and 4 reused, while the recorded hash of the served
manifest differs. `src/render.mjs` changed, and it is one of the common
key's inputs, so the Curta film recaptures its frames on its next render
for that reason alone, as for every renderer change of the campaign.

## The film: `check` of *Addition* from this worktree

`node bin/videomaker.mjs check <Curta>/videos/addition/_build/movie.json
--viewer <API 29 bundle>`, the project at `f2ad951`, its untracked
`export/clocked_curta/` holding a manifest with no `source` and the
hand-typed `source-revision.txt` (`c214704a7a7588cee519674147a28ca517fe3d14`):

    The export /mnt/data/machinome-projects/Calculators/Curta-Type-I-3x/export/clocked_curta/manifest.json records no source, the revision it was made from (manifest field source.revision); export the model again with a machinome that records it, from the project's Git repository with a commit: a project outside Git cannot be filmed with a pinned revision

Exit status 1. That is the expected outcome: the export predates the
framework's change, and the orchestrator exports the Curta again at the
campaign's close. The check ran the movie's early steps before loading the
film (the stage bundle under the project's ignored `_build/stage/`, the
layout measurement for its reframe); the refusal came before the film's
`movie-resolved.json` is written. Nothing tracked in the project was
touched and nothing was committed there.

## Findings

1. **The fixture project's revision cannot be Videomaker's head**, as the
   brief expected: the head moves with every commit, the tree is dirty
   while a change is made, and the fixture movies' source panels read
   their excerpts with `git show <sourceRevision>:models/seesaw.py` in a
   copy committed by the recipe, where Videomaker's commits do not exist.
   The exports are made from the recipe commit instead (design D6), and
   the framework records that commit, clean.
2. **Exporting two models from one checkout makes the second export
   dirty** unless the project ignores its `_build/`: the framework builds
   each model under `<project>/_build/<model>/`, after taking the first
   record, so the next export finds it untracked. Correct by the
   framework's rule (an unignored build product is dirt); a project that
   exports more than one model must ignore `_build/`. The Curta project
   ignores neither its `_build/` nor its `export/` today (finding 17), so
   its next export will be recorded dirty until it does; the film will
   then say so in its `Export:` line and its release issues.
3. **`speech` of a movie generates missing takes before it loads the
   film**, so an export with no `source`, or a pin that differs, is
   refused only after the paid requests for missing takes are made. The
   same was true of the sidecar. Smallest correction: the speech command
   reads the manifest and holds the pin before `generateMovieTakes`.
   Recorded, not fixed: no film met it, and it is the speech command's
   order, not the revision's source.
4. **The schema still allows `"sourceRevision": null`**
   (`schema/machinome-movie-0.2.json`), which evaluation no longer writes
   and every load refuses (a null pin equals no recorded revision). The
   schema is the orchestrator's; smallest correction: `"type": "string"`.
   Recorded, not changed.
5. **The YAML format said "A null revision marks unpinned source"**
   (`docs/FORMAT.md`), which no load accepted: with the sidecar, a null
   pin differed from it, and without one the load failed with `ENOENT`.
   Corrected in the manual here, since the sentence named the revision's
   source.

## What was not done, and why

- The framework, the viewer, and the Curta and Leonardo projects: out of
  this cycle. The Curta's export, its hand-typed sidecar and Leonardo's
  gallery script are the orchestrator's; the Curta's refusal above is the
  proof that the film now needs its export made again.
- `Sim.identity` (the other half of wart 9): a later cycle, once its bench
  is in the framework's `main`.
- No fallback to `source-revision.txt`, no sidecar written anywhere, and
  no hand edit of a fixture manifest: the exports were made by the
  framework's command.
- No judgement of an export whose revision is not the project's head, and
  no path list for a dirty export: the framework records a boolean.
- The schema's `null` (finding 4) and the speech command's order
  (finding 3): recorded, not changed.
- The Curta film was not rendered; its `check` is refused, as expected.
- Task 0.3 (the orchestrator's review of the planning commit) is the
  campaign's gate and is not claimed here.
