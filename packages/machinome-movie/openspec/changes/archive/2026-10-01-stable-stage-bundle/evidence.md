# Implementation evidence

## Authority and scope

Cycle 10 of Videomaker's addition-warts campaign, finding 15 of
`workflow/warts.md` (met by *Addition* through the cycles
`serve-what-the-viewer-reads` and `honest-provenance`), on branch
`stable-stage-bundle` (worktree `WTs/stable-stage-bundle`), cut from
`addition-warts` at `500ebca`. The planning commit is `0a0faa3`. Nothing was
pushed or published; no network or paid request was made; nothing was
installed. Only `src/stage-build.mjs` changed in the tool; no schema,
contract page, Python, stage runtime, renderer or viewer source was
changed, and the shot cache's key composition is untouched. The viewer was
reached only through the API 29 bundle selected by path
(`machinome-viewer/machinome_viewer/widget/dist/machinome-viewer.js` of the
workspace), never written into the repository. Nothing was written in the
Curta project. Integration into `addition-warts` is the orchestrator's.

Environment: Linux, Node v24, vitest 5.0.3, esbuild 0.28.2, Playwright's
Chromium, Python 3.12 from the workspace venv. Other campaign agents ran
suites and the film in other worktrees at the same time; durations are not
comparable across runs.

## How esbuild prints names (read before designing)

A throwaway build in the session's scratch directory, a CommonJS module
and a stylesheet in a directory named `açaí dir`, then one named
`q"d x/y 😀 ł`, showed the three places and the literal's forms:

    // ../açaí dir/c.cjs
    var require_c = __commonJS({
      "../a\xE7a\xED dir/c.cjs"(exports, module) {
    ...
      '../q"d x/y \u{1F600} ł/c.cjs'(exports, module) {
    ...
    /* ../açaí dir/s.css */

and that esbuild names files relative to the real path of its working
directory (a build whose working directory was reached through a link
named its inputs from the link's target). Hence D1's real roots and D2's
decoding of either quote and of `\xHH`, `\uHHHH`, `\u{…}`.

## Red

`test/stage-types.test.mjs` (layer 4, pure), the two new tests, on the
base code (the planning commit's `src/stage-build.mjs`):

     × two checkouts bundle two copies of a project, at different places, to the same bytes 594ms
     × the bundle's key is the same from another checkout, which reuses the bundle this one built 516ms

    FAIL  |pure| test/stage-types.test.mjs > bundle > two checkouts bundle two copies of a project, at different places, to the same bytes
    AssertionError: stage.js differs between the checkouts: expected [ …(27) ] to deeply equal []

The 27 differing lines, 20 for React's packages (a comment and a
CommonJS wrapper's name each, differing by the depth of the copy) and 7
for the runtime (differing by the checkout), of which:

    "33:   // ../../../../../../home/asa/devel/machinome/videomaker/node_modules/react/cjs/react.production.js  |    // ../../../../../../../../home/asa/devel/machinome/videomaker/node_modules/react/cjs/react.production.js",
    "35:     \"../../../../../../home/asa/devel/machinome/videomaker/node_modules/react/cjs/react.production.js\"(exports) {  |      \"../../../../../../../../home/asa/devel/machinome/videomaker/node_modules/react/cjs/react.production.js\"(exports) {",
    "14577:   // ../../../../../../home/asa/devel/machinome/videomaker/WTs/stable-stage-bundle/stage/runtime.tsx  |    // ../../../../../../other-checkout/stage/runtime.tsx",
    "14581:   // ../../../../../../home/asa/devel/machinome/videomaker/WTs/stable-stage-bundle/stage/components.tsx  |    // ../../../../../../other-checkout/stage/components.tsx",
    "14961:   // ../../../../../../home/asa/devel/machinome/videomaker/WTs/stable-stage-bundle/stage/runtime.tsx  |    // ../../../../../../other-checkout/stage/runtime.tsx",

    FAIL  |pure| test/stage-types.test.mjs > bundle > the bundle's key is the same from another checkout, which reuses the bundle this one built
    AssertionError: expected { …(8) } to match object { reused: true, …(3) }
    -   "cssSha256": "83c6443700da2fdc55835a1b84fa5d152ade9adaa94ced9bebf64b306f0b847c",
    -   "reused": true,
    -   "sha256": "f1bfbdb20e26b42dd5b3c75ef5f9deedee803c1320b9a2f40eb0d80c5ede99b4",
    +   "cssSha256": "861fb12db02bb8ba26b04fba7c5c5e43af22f7b27570df4ad9fe942789849e24",
    +   "reused": false,
    +   "sha256": "71f02d7f8a3b3af738be0d9ce7f66fa68fa0e8efeeacd74604e7abdabd4f91bc",
          Tests  2 failed | 8 passed (10)

The second checkout rebuilt (its key hashed its own absolute runtime
paths) and wrote other bytes over the first one's bundle.

A first draft of the test copied only the tool's `src/` and `stage/`; with
no `package.json` above the copied runtime, esbuild no longer treated it as
an ES module in Node's sense and wrote `__toESM(require_react())` where the
checkout writes `__toESM(require_react(), 1)`. The test copies
`package.json` too, as every checkout has it; the observation is why the
namespace-plugin alternative (design D2, ADR-013) was not built.

The layer 9 pin (`test/repository.test.mjs`, "the manual and the records
say the stage bundle is the same bytes from any checkout") was written
after the pages; its red was shown with `docs/stage.md`, `README.md`,
`CHANGELOG.md` and `docs/adrs/README.md` stashed (`git stash push --`, then
`git stash pop`, the files restored unchanged):

     × the manual and the records say the stage bundle is the same bytes from any checkout (stable-stage-bundle) 9ms
    AssertionError: stage.md: the bullet
          Tests  1 failed | 8 skipped (9)

The unit test of the rewrite over the escaped and singly quoted forms ("a
name esbuild escaped or quoted singly is found and renamed; nothing else
is touched") was written after the code, as a guard; no red is claimed
for it.

## Green

    ✓ |pure| test/stage-types.test.mjs (11 tests) 3457ms
      ✓ two checkouts bundle two copies of a project, at different places, to the same bytes 703ms
      ✓ the bundle's key is the same from another checkout, which reuses the bundle this one built 401ms
     Test Files  1 passed (1)
          Tests  11 passed (11)

The bundle now reads, for example (the fixture tour's in the pipeline
run, lines 33 to 35; the Curta film's, built below, the rest):

      // videomaker/node_modules/react/cjs/react.production.js
      var require_react_production = __commonJS({
        "videomaker/node_modules/react/cjs/react.production.js"(exports) {
    ...
      // videomaker/stage/runtime.tsx
    ...
      // project/videos/addition/stage.tsx

    /* videomaker/stage/stage.css */
    ...
    /* project/videos/addition/stage.css */

and neither file of the Curta bundle contains `home/asa` or `/tmp/`.

## The pixels did not move

`test/pipeline/movie-pipeline.test.mjs` (layer 8: the YAML episode, the
tour, the clocked count and the minimal movie rendered with the viewer
double) was run cold with `KEEP_VIDEOMAKER_TEST=1` on the base code before
any source change, and again on the change; every shot generation's
`index.json` in the kept fixture copies was read (shot, size, frame index,
frame SHA-256), the lists sorted and compared:

    before: 14 passed, 222.18 s, 0 from the memo
    763 frames from 14 fixtures; sha256 of the sorted list 9db9db5738d8d524ff50684de111ec35b5eec91ba7d8225229062f8ff66ab160
    after:  14 passed, 222.60 s, 0 from the memo
    763 frames from 14 fixtures; sha256 of the sorted list 9db9db5738d8d524ff50684de111ec35b5eec91ba7d8225229062f8ff66ab160

identical, frame for frame, at 640×360 (tour, count, minimal) and 320×180
(the YAML fixture). During the "after" run one character class in
`quote()` was rewritten from a literal U+FFFF to `[^\x00-\x7e]`, an
equivalent spelling that changes nothing for an ASCII name (every name in
the fixtures is); the whole suite below ran on the final content. The kept
copies were removed afterwards.

## Suites on the final content

The whole Node suite, with `VIDEOMAKER_VIEWER_BUNDLE` naming the API 29
bundle (the viewer layer ran: `real-viewer.test.mjs` 7 tests,
`take.test.mjs` 5 tests):

     Test Files  40 passed (40)
          Tests  391 passed (391)
       Duration  916.35s (tests 98%, import 1%)
    Test memo: 29 passed from the memo, 362 run

The 29 memoized passes were `test/pipeline/pictures.test.mjs` (16),
`speech.test.mjs` (8) and `source-scenes.test.mjs` (5), whose keys do not
reach `src/stage-build.mjs`; every slow test that reaches it ran fresh.
Those three files were then run cold:

     ✓ |slow| test/pipeline/pictures.test.mjs (16 tests) 7371ms
     ✓ |slow| test/pipeline/speech.test.mjs (8 tests) 1722ms
     ✓ |slow| test/pipeline/source-scenes.test.mjs (5 tests) 526ms
     Test Files  3 passed (3)
          Tests  29 passed (29)
       Duration  11.65s (tests 92%, setup 4%, transform 2%, import 1%)
    Test memo: 0 passed from the memo, 29 run

The Python suite (`python -m pytest -q` in `python/`, the workspace venv):

    286 passed in 16.70s

The specs after the archive: `openspec validate --specs --strict`,
`Totals: 16 passed, 0 failed (16 items)`.

## The film

`check` of *Addition* (`node bin/videomaker.mjs check
<Curta>/videos/addition/_build/movie.json --viewer <API 29 bundle>`), once
from `WTs/addition-warts` (at `500ebca`) and once from this worktree, both
exit 1 in 1.4 s, before the stage is bundled, with the same refusal:

    chapter machinome, shot inputs, cues[1].actions[0], words[0].token: the token 'Driver' is absent from line 52 of the excerpt drivers (found 0 times, bounded by anything but a letter, a digit or an underscore)

The film's `_build/movie.json` was evaluated at 03:15; the project's
`movie.py` and `takes.py` were rewritten at 09:04 and its working tree
holds staged changes to `pyproject.toml` and many `simulation/` files
(another agent's work, not this cycle's), so the source line the document
pins its token to has moved. Re-evaluating would rewrite the film's shared
`_build/movie.json` under the agents using it, so it was not done (finding
1 below). Since a refused `check` writes nothing, neither run touched the
film's `_build/`.

The stage `check` would build was built instead with each checkout's own
`buildStage`, called as `buildFilmStage` calls it (root the document's
`root` resolved and real, modules and stage block the document's, project
the repository's top level), from the film's `movie.json` and its
`stage.tsx` and `stage.css`, into build directories in the session's
scratch directory, never in the project:

    == this worktree
    bundled …/ssb-b-mine/stage/stage.js (sha256 9edf3c2082ac) and stage.css (sha256 7979fc5a71f2); typechecked true; 0.39 s
      stage.js 9edf3c2082ac4a3934b50740a89e0044241495241282175fa66861dd8bed1e9b
      stage.css 7979fc5a71f2225cd73af14973d11a00008eee7d94a74e57ff78bc91f2687fda
    == a second checkout of the same content (a copy of src/, stage/, package.json, node_modules linked), its own build dir one level deeper
    bundled …/ssb-b-twin/deeper/stage/stage.js (sha256 9edf3c2082ac) and stage.css (sha256 7979fc5a71f2); typechecked true; 0.41 s
    == the second checkout, on this worktree's build dir
    reused …/ssb-b-mine/stage/stage.js (sha256 9edf3c2082ac) and stage.css (sha256 7979fc5a71f2); typechecked true; 0.05 s
    == addition-warts (base code)
    bundled …/ssb-b-aw/stage/stage.js (sha256 baac6d9658a7) and stage.css (sha256 4c1f514550ba); typechecked true; 0.38 s

`cmp` of the two bundles: `stage.js` and `stage.css` identical. One
`stageSha256` for the Curta film from two checkouts in two places, and the
second checkout reuses the first one's bundle; the base code gives yet
another hash for the same content, a fourth beside the three the finding
recorded (`e5c7bccec003`, `c82a3718550a`, `6298cd57909a`; the film's
`_build/stage/stage.js` read `23c450c09474` at the time, a fifth, from
whichever agent bundled it last). The scratch copies were removed.

## The shot cache's key

Its composition is unchanged (out of scope). Every input of `commonKey`
other than the bundle is already a content hash or a version (the page,
the viewer, the model, the renderer's modules, the fonts, the browser), so
with the bundle's bytes independent of the checkout, the key is too; this
was not proved by rendering from two checkouts (below). Every film's
`stage.js` changes bytes once with this change, so every film recaptures
once on its next render, as for any change of the runtime.

## Findings

1. **The Curta film's document is stale against its project's working
   tree.** `check` of *Addition* refuses from any checkout: the token
   `Driver` of shot `inputs` is no longer on line 52 of the excerpt
   `drivers`, because the project's `movie.py`, `takes.py` and simulation
   files changed after the film was evaluated (staged, uncommitted, at
   09:04). Project work, not the tool's: re-evaluate the film once the
   project's change settles. A neighbour of finding 16 (a shared `_build/`
   and a project edited under concurrent agents).
2. **A file a stage module imports from outside both the tool and its
   repository keeps a machine-dependent name** (design D1, case 5). No
   film does it; recorded in the manual and the ADR, not refused.
3. **`metafile.json` beside the bundle still holds esbuild's machine
   paths.** It is the build's own record and no longer read for reuse or
   hashed; kept for diagnosis.

## What was not done, and why

- No render of a fixture from two checkouts to show a second checkout
  capturing nothing: the shot cache's key composition is out of scope,
  and its only checkout-dependent input was the bundle, whose bytes the
  layer 4 tests and the film's two builds prove equal. Such a test would
  copy the whole tool into a Git work tree per run.
- `check` of the Curta film did not reach its `Stage:` line from either
  checkout (finding 1); the film was not re-evaluated, since that rewrites
  the shared `_build/movie.json`. The stage was built as `check` builds it,
  outside the project.
- No change to `docs/movie-document.md` or the schema: no statement there
  about the bundle's bytes changed.
- No minification, no source map, no change of what the browser runs.
- The ADR number reserved (ADR-013) was used.
