# Changelog

Videomaker is private and unversioned; entries accumulate under `Unreleased`
until the pilot cuts a version. Each change adds its bullet in the cycle that
lands it.

## Unreleased

- A take is recorded against the machine the export carries, or not at
  all. Evaluation reads the take's `identity` from the framework's
  simulation of the declared model (`Sim(model).identity`), the simulation
  it makes the steps through, where it copied the export's
  `clocked.identity` before; and before the first step it refuses a take
  whose identity differs from the export's, naming the take, the model as
  `module:Class`, the export, both identities and what to do: `export the
  model again, or declare the model the export was made from`. A model
  whose law changed since its export with the same drivers and states was
  recorded without a word, and is now refused; one whose drivers or states
  changed was refused in words about `take.initial`, and is now refused
  for its identity. The document check's rule that `take.initial` holds
  every driver and state of the machine and nothing else stays, in both
  runtimes, in words that name the rule rather than "another machine"; a
  new invalid fixture, `take-initial-incomplete`, holds both runtimes to
  them. A document evaluated from a matching export is unchanged.
  (`take-identity`, ADR-011 amended)
- `check` reports a continuation that crosses a mark. On a take, a shot
  that a dissolve, a wipe, a slide or the first half of a fade still shows
  past its end keeps running its take time at the rate it ended with;
  resolution follows it through the frames on which the join shows it, and
  when the take time on the last of them lies past a mark the shot ended on
  or before, the shot's resolved `model` records `crossing` (the join, the
  incoming shot, the mark, the step whose `at` is the mark, the take time
  reached, how far past) and `check` prints, after its take line, one
  sentence per crossing: `Continuation: shot nine runs on through the 0.5 s
  dissolve into shot carry and crosses the mark nine: its last frame there
  poses take time 6.76 s, 0.76 s past the mark, inside step-3, which moves
  crank by 360; hold the shot at the mark before it ends, or ease its model
  to rest there`. A report, not a refusal; a step boundary that is not a
  mark is not reported, and a continuation that would leave the take is
  still refused with its words. The fixture `count`'s resolved pin gains
  the crossing on `nine`. (`check-the-continuation`, ADR-014)
- A stage bundle is the same bytes from any checkout. The bundle names
  every file it read by the tool or by the project repository, never by
  where either lies on the machine: the runtime as
  `videomaker/stage/<file>`, React and React DOM as
  `videomaker/node_modules/<file>`, a project file as `project/<path in the
  repository>`. esbuild's own names, which ran from the build directory
  through the machine's directories into the checkout, are rewritten in
  the script's module comments, its CommonJS wrappers and the stylesheet's
  comments before the bundle is written; no code changes. The bundle's key
  is computed over those names and the files' content, and `inputs.json`
  records them by name, so another checkout of the same content reuses
  the bundle (`reused`) and gets the same `Stage:` hashes, the same
  `stageSha256` and the same shot cache key, where it rebuilt the bundle
  and recaptured every shot before. Every film's `stage.js` changes bytes
  once with this change. (`stable-stage-bundle`, ADR-013)
- A mark on a take is proved in the browser layer. The viewer double's
  clocked machine names the input its part rectangles follow,
  `follows: {input, range}`, and places them by that input's value in the
  bank it holds, as it places them by the loop's time without a machine; a
  double's machine that follows nothing, or an input its bank does not
  hold, is refused at mount naming the input. One assertion, a ring on the
  fixture counter's units drum posed at the take's start, at the mark `one`
  and at the start again, moving with the bank and returning exactly, runs
  in the browser layer on the double and in the viewer layer on the
  selected bundle; until now no layer posed a mark on a take. Tests only.
  (`double-poses-a-bank`)
- The model's revision is the one its export records. `machinome export`
  now writes, in the export's `manifest.json`, a `source` record: the
  commit the project was at (`source.revision`) and whether Git listed any
  change in it then (`source.dirty`). Both runtimes read the revision
  there, and nothing reads `source-revision.txt` any more: evaluation
  writes `source.revision` as the document's `model.sourceRevision`, and
  `check`, `speech`, `preview`, `render` and `build` refuse a film whose
  pin differs, naming both revisions. An export whose manifest records no
  `source` (made before the framework recorded it, or outside Git) is
  refused by name in both runtimes, naming the manifest and
  `source.revision` and saying to export the model again; evaluation no
  longer writes a `null` revision. The export's dirt is provenance: the
  commands print an `Export:` line after the tree lines (`made from
  <revision>, clean`, or `dirty` and what that means), the render
  manifest, every captured shot generation and the preview report record
  `exportRevision` and `exportDirty`, and an export made from a dirty tree
  is a `releaseIssues` entry, never a refusal. The shot cache keys the
  manifest without its `source`, so an export made again with only another
  revision or dirt reuses every shot. The fixture project's exports are
  made again from its recipe commit, which their manifests now record, by
  `scripts/pin-fixture-project.mjs` (new `--machinome` option); their
  sidecars are gone. (`read-the-exports-source`, ADR-019)
- A take's time is summed exactly. Evaluation adds a `Take`'s durations as
  the decimals written (a move's `over=`, an instruction's `duration`), in
  exact arithmetic, and writes each step's `at`, every mark and the length
  as the number nearest the exact sum: three moves of 1.2 s end at 3.6, not
  at 3.5999999999999996. Both runtimes hold a take document's sums to the
  written durations with no tolerance and refuse one summed in floats,
  naming the field (`take.steps[i]` and `at`,
  `model.expectedDurationSeconds`, or `marks.<name>` and `end of a step`;
  the invalid fixture `take-mark-summed-in-floats`). The Node side reads a
  step's end as written, the next step's `at` or the take's length, so a
  mark is posed on its recorded bank without a tolerance, a frame is on a
  mark only at its take time exactly, and `check`'s take line gives the
  length as written; `bankAt` takes the document. (`exact-take-times`,
  ADR-016)
- Provenance says whether each tree was dirty. `preview` and `render` read
  the project's Git tree and Videomaker's own once, before the first frame,
  and record beside `projectHead` and `workflowHead` whether each was dirty
  (a tracked file changed, or an untracked file Git does not ignore):
  `projectDirty` and `workflowDirty` in the render manifest's `provenance`,
  in every captured shot generation's `index.provenance` and in the
  preview's `report.json`; the manifest no longer reads the heads again
  after the encode. `check`, `preview` and `render` print a `Project tree:`
  and a `Videomaker tree:` line, `clean at <head>` or `dirty at <command>`
  with the paths that differ and what that means for the record. A film
  rendered from a dirty tree is not release-ready: the manifest's new
  `releaseIssues` lists every reason in words, the dirty tree's among them,
  and `releaseReady` is true exactly when it is empty. The dirt is no cache
  key: a dirty tree reuses the frames of a clean one. `check`'s `Stage:`
  line carries the stylesheet's hash beside the script's, so a change to
  `stage.css` alone shows. `WTs/` is ignored, as `AGENTS.md` said it was.
  (`honest-provenance`, ADR-015)
- `preview` and `render` serve from a model's export exactly the files the
  viewer reads, as the framework's export document defines them: each
  part's `model` and each marking's under the manifest's `root`. They no
  longer serve every manifest string that ends in `.stl` or an image
  extension, so the piece inventory's `sources`, provenance paths relative
  to the project, are neither served nor opened, and an export that names
  source files it does not hold is filmed without a workaround. A file the
  viewer reads that the export does not hold, or that lies outside it, is
  refused before a browser opens, naming its field in the manifest
  (`root.children[2].children[0].model`), its node and its path, and saying
  to export the model again, where a bare `ENOENT` stopped the command
  before. Every film's shot cache is recaptured once, since the renderer's
  module is part of its key. (`serve-what-the-viewer-reads`)
- The commands film a clocked machine's take. A movie document with
  `model.timeMode: "take"` loads; Node checks its `take` block against the
  export and replays its steps to the recorded banks, refusing the five
  take fixtures with Python's words, before any take of speech; a clocked
  export filmed as a loop and a running program are refused by name. A view
  on a take carries the machine's whole bank at its take time (the
  contract's rule, `src/take.mjs`) instead of a loop time; the stage
  restores it on the viewer's machine with the take's identity and sets the
  camera, refuses at mount a viewer with no machine or another, and reports
  the bank it posed. A movie on a take needs Viewer API 29. Before the first
  frame `preview` and `render` replay every step on the viewer and refuse a
  request that differs from the record, naming the step and the field; each
  posed frame refuses a view whose bank differs from its frame's, or at a
  mark from the take's. `check` prints the take's steps, marks and length.
  The stage waits for a view's canvas to shrink with its box as it waits
  for one to grow, and the renderer refuses a canvas larger than its view
  (`Viewer canvas exceeds its view`). The fixture `count` is resolved,
  posed with the viewer double's machine and, with a selected bundle, on
  the real viewer. (`pose-a-take`, ADR-012)
- A movie declared in Python can record a clocked machine's take. `Take`,
  beside `Loop`, declares the steps the machine is asked to make,
  `Move(input, to=|by=, over=)` and `Trigger(instruction)`, each drawn over
  its seconds, and the `Mark`s its shots cut on; its class refuses by name a
  step it cannot film, an input or instruction the model does not declare,
  a mark named twice or at another's instant, and a shot's model time
  outside the take. Evaluation constructs the framework's simulation of the
  model once, makes the steps through its own requests and writes the
  document's `take` block (`model.timeMode: "take"`): each request as the
  framework returned it, the bank before the first step and at every mark,
  the identity the export publishes; a request the framework refuses or
  stops before it moves is refused in the framework's words. Python's
  document check holds a take document to its export and to the replay of
  its steps. The fixture project gains the framework tutorial's clocked
  counter, exported for real, its take and the movie `count`, with five
  invalid take documents; the commands read a take document since
  `pose-a-take`. A loop's evaluation is unchanged. (`declare-a-take`,
  ADR-011)
- A shot can come in by a **reframe**: `transition=Reframe(d)` in Python,
  `{"kind": "reframe", "duration"}` in the movie document. For the join's
  duration the incoming shot is drawn live on its own set: each view element
  both shots place moves from its slot's box in the outgoing set to its
  slot's box in the incoming set, by the eased progress, its camera and its
  take running on (a `move` may run under it), while everything else the
  incoming shot places fades in; what only the outgoing shot placed is gone
  at the cut. A reframe whose two shots share no view element is refused
  before any take, by the declarations and by both runtimes, naming both
  shots and `no view element in both`. The slot boxes come from the stage:
  `check` now measures the layout of a movie with a reframe (as of one with
  a picture), prints a `Reframe` line per join and refuses a reframe through
  a slot sized by what it holds; every preview and render session measures
  them on its own page before its first frame. Every posed reframe frame is
  checked (the view within a pixel of its box, the rest at the progress),
  and `preview` proves its first frame, its end, which is exactly the
  incoming frame, and its replay. Each frame of a reframe waits for the
  view's canvas: about 100 ms a frame at 640 px against about 67 ms just
  after the join, with the real viewer as with the late-canvas double. The
  fixture tour's `question` now reframes from `Playbill` into
  `PlaybillSplit`. The stage runtime changes, so every film recaptures once.
  (`reframe-join`, ADR-010, for the Curta film's turn to its code)
- The chrome stays on screen while a picture or a mark fades. A frame with a
  fading picture or mark is composed from picture-only captures, and the
  stage left the page in its picture-only state after the blend, so the set's
  masthead vanished for every frame of every such fade (47 of the fixture
  tour's 567 frames; the still's fade-in of *Cut and Advance*). The blend
  request now says whether the frame is picture-only, like a transition's,
  and a browser test proves a blended frame differs from its picture-only
  capture in the chrome and nowhere else. Every film's stage bundle changes,
  so every film recaptures once. (`chrome-through-blends`, found by the
  `flaky-pixel-proofs` investigation)
- `check` measures a movie's layout before speech. When a movie document
  shows a picture, `check`, after bundling the stage and before reading any
  take, poses each set its shots use once, empty, in one headless Chromium
  served the bundle and a stub viewer (no `--viewer` needed), at the output
  size, and prints a `Layout` line per set. A still or clip enlarged beyond
  its allowance in its slot's measured box is refused before `speech` is
  run, in the words a YAML episode's picture is refused in, naming the
  slot's box and set; once the takes place the cues, a picture view that
  leaves the picture is refused naming the shot and the video time; the
  picture line prints the peak against the allowance instead of deferring
  to preview. A slot whose box depends on what it holds is still judged by
  preview and render. A YAML episode and a movie without pictures open no
  browser. On the fixture tour `check` takes about a second longer (a median
  1.96 s instead of 0.88 s on a loaded machine). The stage runtime and the
  renderer are unchanged, so no film recaptures. (`check-measures-the-stage`,
  ADR-009)
- The suite has a viewer layer: `test/viewer/`, the `viewer` project, run
  after the slow tests on the same Chromium with the machinome-viewer bundle
  `VIDEOMAKER_VIEWER_BUNDLE` names by path. It asserts the Viewer API the
  fixture tour needs from a mounted instance; proves that a view's canvas is
  its box's size on a fresh mount, after a change of set and when the view
  returns (the failure *Cut and Advance* met), that A, B, A gives identical
  pixels across a camera move, a ghosted highlight, a hidden layer and a
  leased instance, and that marks land on the real model; runs the tour
  through `check`, `preview` and `render`; and records Chromium's memory
  with one and two instances. Without the variable every test of the layer
  is reported skipped, "no viewer bundle selected", by the memo report too;
  a path that is not a viewer fails naming it. The bundle's bytes, never its
  path, are in the memo key. The fixture project's export is now the one
  `machinome export` writes (a 20 s loop in which the beam tips, blocks with
  a colour a highlight can tint), replacing the hand-written manifest the
  real viewer refused ("declares document version 4, which this viewer does
  not render"). (`viewer-integration-layer`, ADR-008)
- A film mounts no more viewer instances than one of its frames places
  views. Instances are leased: a view element keeps its instance while
  consecutive frames place it, an instance whose view a frame does not place
  is free for the next view without one, and a new instance mounts only when
  none is free; what an instance holds (hidden layers, a standing highlight)
  travels with it, so a leased instance draws what a fresh one would. A
  viewer below API 28, which keeps the up and field of view it mounted with,
  is leased only to a view with that lens. The fixture tour, posed in order,
  mounts one instance instead of four; a movie with six view elements whose
  frames show one view each mounts one instead of six; a YAML episode no
  longer mounts one per shot. `window.film.views()` gives each instance the
  view element it serves, or `null`. (`viewer-instances`, ADR-007)
- The speech command finds its ElevenLabs key when it runs from another work
  tree of the repository: it takes `ELEVENLABS_API_KEY` from the environment,
  then from the `.env` of the checkout it runs from, then from the `.env` of
  the repository's primary work tree (found through Git's common directory;
  a copy inside another repository, or a `GIT_DIR` a caller sets, is never
  followed). A film made from a work tree found no key until the primary's
  file was sourced. The refusal names every place it looked, in order, and
  never prints a key; the lookup no longer copies the key into the process
  environment, so nothing the command launches inherits it.
- A movie document's times accept a third anchor of the chapter's
  narration, `{"narrationEnd": true}` with an optional `plus`: the end of the
  last letter or digit of the chapter's take. `lines.end()` evaluates to it
  instead of the spoken end of an invented tail phrase, and resolves to the
  same frames. The schema refuses a `narrationEnd` that is not `true` or that
  carries another field, naming it and its path. `check` prints, after its
  summary line, each chapter's take, resolved length and tail, and the
  manual says that the narrator sets a film's length. (`narration-end-anchor`,
  ADR-001 amended)
- The fixture project's still is drawn by `scripts/draw-fixture-still.mjs`,
  864 by 576 pixels of flat shapes with no text, the same bytes on every run,
  and the tour's template puts its plate over the stage, as a film puts a
  drawing, instead of a stamp in a corner: the 48 by 32 still it replaces
  left the enlargement check and the picture proofs nothing of a film's
  shape to exercise. `scripts/pin-fixture-project.mjs` re-pins the fixture
  project in one command after any of its files changes: it makes the
  project's commit by the recipe, writes the revision, re-evaluates the
  registered documents and prints what changed, leaving the resolved pins
  to a person. The PNG encoder the review pack used moves beside the
  decoder in `src/pixels.mjs`. (`fixture-hygiene`)
- A pose waits for what can change the picture, and for nothing else: the
  stage repaints the whole page only for preview's proof poses, when a view
  was mounted, placed again or resized, or when anything the page shows
  outside the views' canvases changed since its last repaint; a frame in
  which only the model moved requests no animation frame. On the fixture
  tour (567 frames at 1280×720, the viewer double) 207 of 778 poses skip
  the repaint (55 ms each); capture runs at 5.3 to 5.4 frames a second
  instead of 4.8 to 4.9 (about 105 s instead of 116 to 118 s), and the
  command line's render of the tour takes 116.5 s instead of 127.6 s. A
  browser test pins the rule. Every film's stage bundle changes, so every
  film recaptures once. (`pose-repaints`, ADR-004 amended)

- The stage waits for a view's canvas to fill its box before measuring it:
  on a fresh mount, after a change of set, and when a view placed again after
  shots without it comes back (the real viewer sizes its canvas on its own
  animation frame, and a host detached while its view was off screen had its
  canvas shrunk to nothing; the first film on a project template was refused
  for both). The viewer double gains a `lateCanvas` option that behaves the
  same, and a browser test pins the three cases; the refusal now prints the
  canvas and box sizes.

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
