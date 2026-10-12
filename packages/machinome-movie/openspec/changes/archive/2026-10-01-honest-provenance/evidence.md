# Implementation evidence

## Authority and scope

Cycle 2 of Videomaker's addition-warts campaign, warts 5 and 6 of
*Addition*, on branch `honest-provenance` (worktree `WTs/honest-provenance`),
cut from `addition-warts` at `c8c6309`. The planning commit is `edad255`.
Nothing was pushed or published; no network or paid request was made;
nothing was installed. No schema, contract page, Python source, stage
runtime or viewer source was changed. The viewer was reached only through
the API 29 bundle selected by path
(`machinome-viewer/machinome_viewer/widget/dist/machinome-viewer.js` of the
workspace), never written into the repository. Integration into
`addition-warts` is the orchestrator's.

Environment: Linux, Node v24, vitest, Playwright's Chromium, Python 3.12
from the workspace venv. Other agents ran suites in other worktrees at the
same time; durations are not comparable across runs.

## Red

Each red below was run cold (`VIDEOMAKER_TEST_COLD=1`) before the code it
proves was written.

### The `Stage:` line (layer 8, `test/pipeline/movie-pipeline.test.mjs`)

`check` the tour, append one rule to `videos/tour/stage.css`, `check` again:

     × check reports the stylesheet's hash beside the script's, so a stylesheet change shows in its Stage line 3461ms
    FAIL  |slow| test/pipeline/movie-pipeline.test.mjs > check reports the stylesheet's hash beside the script's, so a stylesheet change shows in its Stage line
    AssertionError: a stylesheet change shows in the Stage line
     ❯ test/pipeline/movie-pipeline.test.mjs:342:10
        342|   assert.notEqual(stageLine(second.out),stageLine(first.out),'a styles…
          Tests  1 failed | 12 skipped (13)

The two lines were identical: the bundle was rebuilt both times
(`bundled`) and the script's bytes did not move with the stylesheet.

### The trees (layer 8, `test/pipeline/provenance.test.mjs`)

First run (after giving the fixture episode the `audio` block a YAML
episode needs), at `check`'s first line:

    FAIL  |slow| test/pipeline/provenance.test.mjs > check, render and preview say whether the project tree was dirty, and a dirty render is not release-ready
    AssertionError: The input did not match the regular expression /^Project tree: clean at 91f7e50694bf$/m. Input:

    'Provenance test: 1 chapters, 1 shots, 2s; model 2s\n' +
      '  a: no cached take, chapter 2.00 s\n' +
      'Stage: bundled /tmp/videomaker-yaml-RN0jg2/_build/stage/stage.js (sha256 0c14742df066) from the runtime alone; no module to type-check\n'

Then, to show the record's red and not only the missing line, the test
was run once with its four line assertions of the clean `check` and
`render` removed (the file was restored afterwards, byte for byte):

    AssertionError: Expected values to be strictly equal:
    + actual - expected

    + undefined
    - false
     ❯ test/pipeline/provenance.test.mjs:66:10
         65|   assert.equal(first.provenance.projectHead,head);
         66|   assert.equal(first.provenance.projectDirty,false);

`projectHead` was the head; nothing said whether the tree was dirty.

### The manual pins (layer 9, `test/repository.test.mjs`)

Written after the manual pages; its red was shown by running it with
`README.md`, `docs/stage.md`, `CHANGELOG.md`, `docs/adrs/README.md` and
`.gitignore` put back to the planning commit's bytes, then restored:

     × the manual and the records say what provenance records of a dirty tree, and the Stage line's two hashes (honest-provenance) 19ms
    AssertionError: README: check's Stage line
          Tests  1 failed | 7 skipped (8)

## Green

The two pipeline files cold, after the change:

     ✓ |slow| test/pipeline/provenance.test.mjs (1 test) 10640ms
     ✓ |slow| test/pipeline/movie-pipeline.test.mjs (13 tests) 242825ms
     Test Files  2 passed (2)
          Tests  14 passed (14)
       Duration  256.60s (tests 99%)
    Test memo: 0 passed from the memo, 14 run

## Suites on the final content

The whole Node suite, with `VIDEOMAKER_VIEWER_BUNDLE` naming the API 29
bundle (the viewer layer ran: `real-viewer.test.mjs` 7 tests,
`take.test.mjs` 5 tests). Every slow verdict ran fresh, since
`src/render.mjs` and `bin/videomaker.mjs` are in every pipeline key; no
pass came from the memo:

     Test Files  39 passed (39)
          Tests  375 passed (375)
       Duration  971.69s (tests 98%, import 1%, transform 1%, environment 1%)
    Test memo: 0 passed from the memo, 375 run

The Python suite (`python -m pytest -q` in `python/`, the workspace venv):

    279 passed in 19.44s

The specs after the archive: `openspec validate --specs --strict`,
`Totals: 16 passed, 0 failed (16 items)`.

## The common key

The dirt enters no key: `commonKey` is computed from what it was computed
from before (page files, renderer sources, fonts, browser, style, sizes,
duration, the lock), and the provenance test renders a project clean, then
with an untracked `notes.txt`, and asserts the same `commonKey`, 0 frames
captured and 4 reused, the reused shots' origin still `projectDirty:
false`. The key's composition did not change. Its value changes once for
every film, because `src/render.mjs`, which this change edits, is itself
one of its inputs (`renderer`); the Curta film would recapture its 3 787
frames on its next render for that reason alone, as for any renderer
change of the campaign.

## The film: `check` of *Addition* from this worktree

`node bin/videomaker.mjs check <Curta>/videos/addition/_build/movie.json
--viewer <API 29 bundle>`, the project at `23c9e6f` (the head the brief
names), its tree dirty:

    Addition: 5 chapters, 13 shots, 126.23333333333333s; model 18.75s
      question: take 11.60 s, chapter 12.67 s, tail 0.87 s
      first: take 29.60 s, chapter 30.67 s, tail 0.87 s
      second: take 34.56 s, chapter 36.10 s, tail 1.34 s
      machinome: take 33.68 s, chapter 35.00 s, tail 1.12 s
      closing: take 10.16 s, chapter 11.80 s, tail 1.44 s
    Take: 7 steps, marks rest 0 s, units_3 1.5 s, set_23 3 s, added_23 9 s, units_5 10.25 s, tens_4 11.5 s, set_145 12.75 s, added_145 18.75 s, 18.75 s long; the replay of its steps gives the recorded bank at every mark
    Viewer API 29 required for clocked take, highlight (shot set-23), highlight (shot add-23), highlight (shot set-145), highlight (shot add-145); …/machinome-viewer.js declares API 29
    Stage: bundled …/Curta-Type-I-3x/videos/addition/_build/stage/stage.js (sha256 6298cd57909a) and stage.css (sha256 79e73c6bd55c) from stage.tsx; types checked
    Layout curta at 1920×1080: stage 1766.4×928.8 at 76.8,97.2; headline sized by what it holds; aside 345.6×324 at 1420.8,626.4
    Layout curta-split at 1920×1080: left 902.4×648 at 96,302.4; right 825.6×928.8 at 1017.6,97.2
    Reframe into inputs: machinome.curta from curta stage 1766.4×928.8 at 76.8,97.2 to curta-split right 825.6×928.8 at 1017.6,97.2
    Project tree: dirty at check, 5 paths differ from its head 23c9e6f48697 ("3D Printed Curta Calculator Assembly_720p.mp4", CREDITS, curta-2x-files/ and 2 more); a render now records a head that is not the content rendered and is not release-ready
    Videomaker tree: dirty at check, 7 paths differ from its head edad25509e35 (.gitignore, bin/videomaker.mjs, src/render.mjs and 4 more); a render now records a head that is not the tool that rendered and is not release-ready

The project's five paths (`git status --porcelain`): the reference video
`3D Printed Curta Calculator Assembly_720p.mp4`, `CREDITS`,
`curta-2x-files/`, `export/` and `screenshots/reverser_inspection.png`, all
untracked and unignored. The film's source itself is committed at
`23c9e6f`. Videomaker's tree was this change, uncommitted when `check` ran.
The film's existing manifest (`rehearsal-manifest.json`, rendered before
this change) records `projectHead` `1567439…`, the commit before the one
that committed the film's source, and stage hashes `e5c7bccec003` /
`3fdc0da6a4af`, neither of which the committed source now bundles to: the
finding, as the record shows it. The `check` rebuilt the project's ignored
`_build/stage/` and rewrote `_build/movie-resolved.json`; nothing tracked in
the project was touched and nothing was committed there.

## Findings

1. **The Curta project's export is untracked and not ignored.** Its film
   README calls `export/clocked_curta/` a build product that is not
   committed; Git lists `export/` as untracked, so every render of the film
   is now reported dirty until the project ignores it (or commits it). The
   same holds for `CREDITS`, `curta-2x-files/`, the reference video and a
   screenshot. A project finding, not Videomaker's; smallest fix: the
   project's `.gitignore` gains `/export/` and the reference media, and
   `CREDITS` is committed.
2. **`WTs/` was not ignored in Videomaker**, though `AGENTS.md` says it is:
   the primary checkout listed `?? WTs/` beside the pilot's untracked
   `workflow/ongoing/curta-video.md`. Fixed here (`/WTs/`, D8), because
   otherwise every render from the primary checkout with a worktree would be
   reported dirty for a directory that is no part of the tool. The pilot's
   untracked note still makes the primary checkout dirty, honestly.
3. **The stage bundle's key hashes the runtime's absolute paths**
   (`computeKey` in `src/stage-build.mjs` records `{path, sha256}` of every
   runtime file), so a film checked from another checkout of Videomaker is
   rebuilt (`bundled`, not `reused`) though the runtime's bytes are equal,
   as the Curta's `check` above shows. Harmless (the outputs are the same
   bytes when the inputs are); recorded, not fixed.
4. **The fixture project of the movie fixtures leaves `export/` and the
   viewer double untracked** (`test/support/fixture-movie.mjs`), so every
   fixture-movie render in the suite now records `projectDirty: true`. No
   test asserted otherwise; the provenance test uses the YAML fixture
   helper, whose `.gitignore` ignores the export and the build.

## What was not done, and why

- The review pack is unchanged: its index is bound to the manifest's
  SHA-256, and the manifest records the dirt (design, "Alternatives
  rejected").
- No refusal of a dirty tree, no hash of the dirt, no weighing of paths
  (design, "Alternatives rejected").
- The framework's export provenance and `source-revision.txt` are out of
  this cycle (the campaign's cycle `read-the-exports-source`).
- The Curta film was not rendered again; this change alters no picture
  input but the renderer's own hash.
- Task 0.3 (the orchestrator's review of the planning commit) is the
  campaign's gate and is not claimed here.
- The line `Project tree:` is printed by `preview` and `render` themselves
  (as `render` already prints `Encoding` and `Review pack`), so a test that
  calls them as functions sees the two lines on its console.
