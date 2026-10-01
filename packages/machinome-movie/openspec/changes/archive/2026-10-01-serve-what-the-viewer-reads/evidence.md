# Implementation evidence

## Authority and scope

Cycle 1 of Videomaker's addition-warts campaign, wart 1 of "Addition
(Curta, 1 October 2026)", on branch `serve-what-the-viewer-reads` (worktree
`WTs/serve-what-the-viewer-reads`), cut from `addition-warts` at `c8c6309`.
The planning commit is `e2c22b9`. Nothing was pushed or published; no
network or paid request was made; nothing was installed. No movie
document, schema, stage, Python or viewer source changed. The framework's
export specification (`openspec/specs/export/spec.md` of the framework
checkout) was read as the definition of the export document and not
written. The viewer was reached only through the bundle selected by path
(`machinome-viewer/machinome_viewer/widget/dist/machinome-viewer.js`, API
29), never written into the repository. Integration into `addition-warts`
is the orchestrator's.

Environment: Linux, Node v24.11.1, vitest 5.0.3, Playwright's Chromium,
Python 3.12 from the workspace venv. Other campaign agents ran their suites
and the film in other worktrees at the same time (`honest-provenance`,
`exact-take-times` at least); durations are not comparable.

## Red

### Pure (`test/export.test.mjs`)

The extension walk of `stage()` was first moved verbatim into
`src/export.mjs` (`exportFiles`, the URL map), `stage()` calling it, so the
red is the old behaviour and not a missing module. First run:

     ❯ |pure| test/export.test.mjs (5 tests | 5 failed) 41ms
       × the files of the fixture exports are their root models and markings, served as before 6ms
       × a provenance source the export does not hold is neither served nor opened 12ms
       × a model file lost from the export is refused by its field, its node and its path 6ms
       × a marking artifact lost from the export is refused by the marking's field 7ms
       × a model outside the export is refused by its field 8ms
     FAIL  |pure| test/export.test.mjs > the files of the fixture exports are their root models and markings, served as before
    TypeError: viewerFiles is not a function
     FAIL  |pure| test/export.test.mjs > a provenance source the export does not hold is neither served nor opened
    AssertionError: Expected values to be strictly deep-equal:
    + actual - expected
      [
        '/model/models/models/seesaw-Block-211d0bb8cf4f.stl',
    +   '/model/STLs/absent.stl',
    +   '/model/media/absent.png',
    +   '/model/docs/absent.svg'
      ]
     FAIL  |pure| test/export.test.mjs > a model file lost from the export is refused by its field, its node and its path
    AssertionError: was not refused
     FAIL  |pure| test/export.test.mjs > a marking artifact lost from the export is refused by the marking's field
    AssertionError: was not refused
     FAIL  |pure| test/export.test.mjs > a model outside the export is refused by its field
    + 'Model asset escapes export: ../outside.stl'
    - 'Export file outside the export: root.children[0].model (Base) names ../outside.stl, which lies outside the export /tmp/videomaker-export-uKROML; export the model again so its manifest names only files inside it'
          Tests  5 failed (5)

The first test's URL pins (`BASE`) were computed on the base with the
extension walk before the test was written; its `exportFiles` half passes
on the base by construction, and only its `viewerFiles` half was red.

### Layer 8 (`test/pipeline/movie-pipeline.test.mjs`)

The new test, cold (`VIDEOMAKER_TEST_COLD=1 npx vitest run --project slow
test/pipeline/movie-pipeline.test.mjs -t "serve the files the viewer
reads"`), on the moved but unchanged walk: the wart, reproduced on the
fixture.

     FAIL  |slow| test/pipeline/movie-pipeline.test.mjs > preview and render serve the files the viewer reads: a provenance source is ignored, a lost model refused by its field
    AssertionError: Minimal: 1 chapters, 1 shots, 1.2s; model 20s
    ENOENT: no such file or directory, open '/tmp/videomaker-movie-39hVbi/export/seesaw/STLs/absent.stl'
    1 !== 0

## Green

With `viewerFiles` and `exportFiles` (design D1, D2):

     ✓ |pure| test/export.test.mjs (5 tests) 37ms
          Tests  5 passed (5)
    Test memo: 0 passed from the memo, 5 run

     ✓ |slow| test/pipeline/movie-pipeline.test.mjs (13 tests | 12 skipped) 5726ms
       ✓ preview and render serve the files the viewer reads: a provenance source is ignored, a lost model refused by its field 5724ms
    Test memo: 0 passed from the memo, 1 run

The layer 8 test also asserts that the refused `preview` and `render` launch
no Chromium.

## The suites on the final content

Node, the whole suite with `VIDEOMAKER_VIEWER_BUNDLE` naming the API 29
bundle (the viewer project ran: `real-viewer.test.mjs` 7 tests,
`take.test.mjs` 5 tests), before the archive moved the records:

     Test Files  39 passed (39)
          Tests  378 passed (378)
       Duration  896.32s (tests 98%, import 1%, transform 1%)
    Test memo: 29 passed from the memo, 349 run

The 29 memoized passes are the tests whose reach does not include
`src/render.mjs` (the picture pipeline tests among them); every test that
reaches the renderer ran, since its key changed.

After the archive and this file, the same command on the final content
(the slow tests' keys unchanged since the run above, so their passes are
the memo's; the pure, stage and repository tests ran):

     Test Files  39 passed (39)
          Tests  378 passed (378)
       Duration  16.00s (tests 53%, import 22%, transform 11%, environment 11%, setup 2%, worker 1%)
    Test memo: 143 passed from the memo, 235 run

and the Python suite again: `279 passed in 13.82s`.

Python (`python -m pytest -q` in `python/`):

    279 passed in 23.42s

## The film

In the Curta project's untracked export, the workaround symlink
`export/clocked_curta/STLs -> ../../STLs` was renamed `STLs.aside` at about
08:14 and renamed back at 08:37:22 UTC: same name, same target
`../../STLs`, its own mtime (03:03:04) unchanged. Nothing was committed in
the project. With the symlink aside, from this worktree, with the API 29
bundle:

- `check`: exit 0, `Addition: 5 chapters, 13 shots, 126.23333333333333s;
  model 18.75s`, the take line (7 steps, eight marks, "the replay of its
  steps gives the recorded bank at every mark"), Viewer API 29 required and
  declared, `Stage: bundled …/stage.js (sha256 c82a3718550a) from stage.tsx;
  types checked`, both sets' layout and the reframe line. (`check` never
  served the export's files, so it passed before this change too.)
- `preview`: exit 0 after 839 s, `Storyboard: …/_build/storyboard.jpg`;
  `preview/report.json`: `pixelReplay` true, `takeReplay` `{steps: 7,
  matched: true}`, 269 frames checked. Before this change it stopped on the
  first `pieces[].sources` STL (`ENOENT … export/clocked_curta/STLs/…`), as
  the film's README records.

The served set, against the film's own records made before this change
(`preview/report.json` of 03:22 and `rehearsal-manifest.json` of 04:29,
both 166 hashes): the new preview serves 161. Exactly five entries left,
the five distinct `.stl` paths of the six `pieces[].sources` strings
ending in `.stl`:

    /model/STLs/37 - Clearing Cover/clearing cap teeth x2.stl
    /model/STLs/37 - Clearing Cover/clearing cap tooth segment spacer.stl
    /model/STLs/42 - Digit Cover & Upper Housing/digits cover.stl
    /model/STLs/42 - Digit Cover & Upper Housing/upper housing.stl
    /model/STLs/43 - Clearing Cover & Collar/crank collar.stl

None was added; every remaining model URL kept its hash and its order.
(`/stage.js` and `/stage.css` differ, for the reason in the findings.)

The film's `_build/` was not restored afterwards: `check` and `preview`
rewrote `movie-resolved.json`, `stage/`, `preview/` and `storyboard.jpg`,
and another agent was writing the same directory (findings). Copies of the
four as they were before this run are in the session's scratchpad
(`film-backup/`), not in either repository.

## The shot cache

- The served URLs and hashes of an export with no provenance file string
  are unchanged, in order (the fixture exports, pinned in
  `test/export.test.mjs`).
- The Curta film's served set lost five entries, so its `hashes` changed.
- Every film's common key changes once regardless, because the key holds
  `renderer: fileHash(src/render.mjs)` and this change edits that module.
  The Curta's 760 MB shot cache is therefore not reused at its next
  render. The planning design said only exports with provenance strings
  would change their key; that was wrong, and design D3 carries the
  correction as an implementation note. `src/export.mjs` is not added to
  the key: what it decides reaches the key as the served files' hashes.

## Findings

1. **The film's `_build/` is shared by every agent of the campaign.** While
   this cycle's `preview` ran on *Addition*, the `honest-provenance` agent
   rebuilt the same film's `_build/stage/` (08:20:42) and another run
   rewrote `movie-resolved.json` (08:36:38). Each agent's `check` and
   `preview` overwrite the others' build products, and an agent with the
   old `stage()` that previewed the film while the symlink was aside
   (08:14 to 08:37) would have met the wart. An orchestration finding, not
   a Videomaker one: two agents should not film one project's movie at
   once.
2. **The stage bundle's hash depends on the checkout it was built from.**
   The bundle embeds esbuild's path comments
   (`// …/videomaker/WTs/<worktree>/stage/runtime.tsx`), so the same runtime
   and the same `stage.tsx` bundle to different bytes from different
   worktrees: `e5c7bccec003` (the render, from `WTs/curta-video`),
   `c82a3718550a` (this cycle) and `6298cd57909a` (`WTs/honest-provenance`).
   With the checkout prefix (`videomaker/` or `videomaker/WTs/<name>/`)
   masked, the first and the last `stage.js`, and their `stage.css`, are
   identical byte for byte. Since `/stage.js` is in the common key, a film
   rendered from another checkout of identical content recaptures every
   shot, and `check`'s `Stage:` line differs by checkout. Smallest
   correction: bundle without the path comments, or with paths relative to
   something checkout-independent (a neighbour of `honest-provenance`'s
   finding 6; not done here).
3. **`README.md` of the film still documents the workaround.** Its "The
   export" section gives `ln -s ../../STLs export/clocked_curta/STLs` and a
   paragraph explaining why; both go when the orchestrator removes the
   symlink at the merge (project work, not committed here).

## What was not done, and why

- **No ADR.** The change applies a boundary the repository already holds
  (the framework is reached through the documents it publishes, by the
  fields that document defines) and adds one pure module; ADR-013 is
  released (design D4).
- **`check` does not open the export's model files.** It never served them;
  the refusal is made by `preview` and `render` before a browser opens,
  which is where the finding met it. Moving it into `check` would be a new
  check no film asked for.
- **`pieces[].models` are not served.** They name the same files the `root`
  tree names (on the Curta, all 149 are `root` models) and the widget
  renders the tree, not the inventory.
- **No restore of the film's `_build/`.** Another agent was writing it;
  restoring older copies over its products would have broken its run.
- **The workaround symlink stays.** The brief asks the orchestrator to remove
  it for good at the merge; it was put back exactly as it was.
- **No change to `experiments/dark-source/render.mjs`**, which carries its
  own copy of the extension walk: experiments are not part of the suite or
  the tool.
