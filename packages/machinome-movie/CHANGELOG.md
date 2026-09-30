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
