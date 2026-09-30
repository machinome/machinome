# Changelog

Videomaker is private and unversioned; entries accumulate under `Unreleased`
until the pilot cuts a version. Each change adds its bullet in the cycle that
lands it.

## Unreleased

- The commands accept a movie document, `machinome-movie/0.1` (JSON, contract
  `docs/movie-document.md`), beside YAML episodes: narration in chapters, one
  take each across several shots; cuts, keys and cues anchored to spoken
  phrases and model times to named marks, resolved from the cached takes and
  written to `_build/movie-resolved.json`; the sets `paper`, `paper-split` and
  `source-only`; the schema `schema/machinome-movie-0.1.json` and shared
  fixtures under `fixtures/`. YAML episodes keep their frames, take keys and
  captions. (`movie-document`, ADR-001)
- A movie can be declared in Python and evaluated to the `machinome-movie/0.1`
  document: the `machinome-movie` package (`python/`) provides `Movie`,
  `Chapter`, `Shot`, `Narration`, `Cue`, the take `Loop` with its cameras,
  layers, source excerpts and stills, the `Paper`, `PaperSplit` and
  `SourceOnly` sets, the view and source-panel elements with their actions,
  titles, annotations, pictures and joins. Movies are listed under
  `[tool.machinome.movies]` and evaluated with `python -m machinome_movie
  evaluate`; mistakes are refused by name before speech. The document's JSON
  Schema is `schema/machinome-movie-0.1.json`, and the shared fixtures gain
  the `minimal` and `tour` documents and seven invalid documents
  (`declarative-movie`).
- The Node suite runs under vitest (`npm test`): pure tests first and in
  parallel, then the browser and pipeline tests one at a time on one Chromium
  and one asset server per run. Slow tests are memoized in the ignored
  `.test-memo/`: a pass is kept under the content of everything the test reads
  and the toolchain's versions, and reported as "passed from the memo" when
  reused; expensive input products are kept and verified on reuse.
  `npm test -- --cold` (or `VIDEOMAKER_TEST_COLD=1`) ignores the memo. The
  dark-source experiment's tests run on their own. `browserSession`, `preview`
  and `render` accept an already launched `browser` and a shared `assets`
  server; the command line is unchanged. (`one-runner`, ADR-003)
- Movies declared in Python evaluate to `machinome-movie/0.2`, the document
  that carries the stage's shape; nothing of 0.1 is emitted, checked or kept
  (`schema/machinome-movie-0.1.json` is gone). A project declares its own
  sets (`Set` subclasses with `module`, `Slot()`s and static props; a derived
  set inherits the chrome, not the layout) and elements (`Element` subclasses
  with `module` and typed `Action`s; an instance's keyword arguments are its
  props), drawn by its stage module. The tool's sets are `Frame` and `Split`;
  `Paper`, `PaperSplit`, `SourceOnly` and `Paper.style` leave the package for
  `Style`. `View` carries the marks `ring`, `label` and `arrow`; `Title` and
  `Picture` are elements shown on cue; `emphasize` pairs spoken words with
  source tokens on any line of the excerpt, which evaluation now reads to
  refuse a token absent or repeated; a source panel completed in a chapter
  needs no typing in its later shots. The shared fixtures are rewritten as
  0.2 documents, with 60 invalid documents naming every refusal
  (`declarative-stage`, ADR-005).
- The commands read `machinome-movie/0.2` and refuse any other format, 0.1
  included, by name; a document is checked against the schema, then
  statically, then resolved against the cached takes to the resolved
  document in `_build/movie-resolved.json`, into which YAML episodes (0.2,
  0.3, 0.4) load too, one chapter per shot, keeping every rule of their
  format. A React stage (`stage/`, contract `docs/stage.md`) replaces the
  fixed film page: the set a shot names, the project's own template or one
  the tool ships, owns the screen, with elements in its slots and its
  chrome marked by `Chrome`; `defineSet`, `defineElement`, `Slot`,
  `useMovie` and `useReport` are its authoring API; a view is one viewer
  instance kept across its chapter. Each movie gets one bundle, the runtime
  and its stage modules, with `movie.d.ts` generated from the stage block,
  TypeScript modules checked with `tsc --noEmit` by `check`, rebuilt only
  when its inputs' content changes, and hashed into the shot cache and the
  manifest (`stageSha256`). YAML episodes are drawn by the shipped sets
  `paper`, `paper-split` and `source-only`, which keep their layouts and
  masthead, the masthead's words now props; up to eight overlays or
  pictures of one position in a shot. No film draws a progress rule. Every
  readback check and pixel proof now reads what the stage reports per
  element and masks the chrome it reports; every film's pixels change once.
  Browser and pipeline tests move to `test/browser/` and `test/pipeline/`,
  and the stage's component tests sit beside it (`react-stage`, ADR-004,
  ADR-006).
- The test memo is one store for the whole repository, beside its common Git
  directory (`<git common dir>/videomaker-test-memo/`, found with
  `git rev-parse --git-common-dir`; `.test-memo/` at the root outside a Git
  work tree), so a worktree reuses the passes and products another worktree
  recorded for the same content, and two suites may write it at once. A slow
  test's key covers what it can reach: the modules its file imports,
  followed transitively, the files those modules serve or read (the stage
  sources and page the browser is served, the schema, the fixtures, the
  fixture project), the command line when a test runs it, and always the test
  support modules, the viewer double and the lock; a module that reads a
  repository file without declaring it fails the suite. A cold run keeps its
  products in one temporary directory it removes at the end, and the next run
  removes what a killed run left. A viewer refusal calls a movie a movie
  ("This movie needs Viewer API 28 ..."); an episode's is unchanged.
  `src/render.mjs` changed, so shot caches are recaptured once.
  (`test-memo-sharing`, ADR-003 amended)
