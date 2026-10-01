## Context

A film is pinned to its model by `model.sourceRevision`: the source panels
read their excerpts at that commit (`src/code.mjs`, `git show
<revision>:<path>`), and the commands refuse a film whose pin differs from
what the export says it was made from. Until now the export said it in a
sidecar, `<export>/source-revision.txt`:

- `python/machinome_movie/evaluate.py` (`_read_revision`) copied the file
  into the document's `model.sourceRevision`, or wrote `null` when it was
  absent;
- `src/movie.mjs` (`loadMovie`) and `src/episode.mjs` (`loadEpisode`) read
  it and refused a differing pin with "Pin model.sourceRevision to the
  export source-revision.txt before rendering", or failed with a bare
  `ENOENT` when it was absent.

The framework never wrote that file. Since its ADR-158 (framework `main`
096217f, installed in the workspace venv) `machinome export` records the
revision inside `manifest.json`: a top-level `source` object with exactly
two keys, `revision` (the full object name of `HEAD` in the work tree
holding the project root) and `dirty` (true exactly when `git status
--porcelain --untracked-files=normal` listed anything when the export
started; ignored files never count), present when the project root is in
a Git work tree with a commit and absent otherwise. It is additive: no
version bump, and a consumer that ignores it renders the same picture.

`src/provenance.mjs` (ADR-015) reads the project's and Videomaker's Git
trees, words them in the `Project tree:` and `Videomaker tree:` lines and
in `releaseIssues`, and the renderer records each head beside its dirt
(`projectHead`/`projectDirty`, `workflowHead`/`workflowDirty`) in the
render manifest's `provenance`, every captured shot generation's
`index.provenance` and the preview's `report.json`. The export's own
record is a third revision with its own dirt, made at another moment.

The fixture project (`python/tests/fixtures/project/`) lives inside
Videomaker's repository; its revision is not Videomaker's commit but the
commit of a fixed recipe (`fixtures/README.md`): its files, without
`export/`, `_build/` and `__pycache__/`, committed into a fresh repository
with a fixed identity, date and message. Every fixture document pins that
recipe revision (`10b189d…`), the Python suite asserts it, and the Node
suite commits a copy of the project by the recipe so that its source panels
read the pinned commit with `git show`.

## Goals / Non-Goals

Goals: the revision a film is pinned to is the one the framework recorded
in the export, in both runtimes, with no sidecar; an export that records
none is refused by name; the export's dirt is said and recorded as
provenance and kept from release, never refused and never a key; the
fixtures are real exports of the installed framework. Non-goals: those of
the proposal.

## Decisions

### D1. The revision is the manifest's `source.revision`, and nothing else

Both runtimes read the export's revision from `manifest.source.revision`.
`source-revision.txt` is read by nothing, and no code path falls back to
it: a step is not a protocol, and an export that has a sidecar but no
`source` is an export made before the framework recorded it, which is
exported again. Evaluation (Python) writes `source.revision` verbatim as
the document's `model.sourceRevision`. Loading (Node, `loadMovie` and
`loadEpisode`) holds the film's `model.sourceRevision` to it, as it held
it to the sidecar.

`src/provenance.mjs` gains the reading, since the export's record is the
third revision a film's records name: `exportSource(manifest,
manifestPath)` returns `{revision, dirty}` or refuses (D2), and
`pinnedRevision(declared, source, manifestPath)` refuses a differing pin
(D3). Both are pure; the loaders call them after reading the manifest they
already read, before any take, picture or browser.

### D2. An export without a source is refused by name, in both runtimes

A manifest with no `source` key is refused, naming the manifest (the path
the loader read; evaluation names it relative to the movie, as the
document's `model.manifest` does), the missing field and the remedy:

    The export <manifest> records no source, the revision it was made from (manifest field source.revision); export the model again with a machinome that records it, from the project's Git repository with a commit: a project outside Git cannot be filmed with a pinned revision

Evaluation's refusal is the same sentence after its subject (`Movie
<Class>: …`). Evaluation no longer writes `null` for a missing revision: a
film whose excerpts cannot be pinned is refused where the export is read,
not discovered at render. A `source` that is present but malformed is
refused naming the field: `source.revision` that is not a string of 40 or
64 lower-case hexadecimal digits (a full SHA-1 or SHA-256 object name, as
`git rev-parse` prints it), or `source.dirty` that is not `true` or
`false`:

    The export <manifest> records source.revision "abc", which is not a full commit hash; export the model again
    The export <manifest> records source.dirty "yes", which is not true or false; export the model again

### D3. A pin that differs names both values

    model.sourceRevision is <declared>, and the export <manifest> was made from source.revision <recorded>; pin the revision the export records (evaluate a movie again), or export the model again from <declared>

The words name the declared value as written (`null` included) and the
recorded one, both in full: the author compares them with `git log`, and
a twelve-digit prefix would make them look equal when they are not.

### D4. The export's dirt is provenance, said beside the trees

The film carries the export's record (`film.exportSource`, `{revision,
dirty}`), read once when the film is loaded. `readTrees` prints, after the
`Project tree:` and `Videomaker tree:` lines, one `Export:` line:

    Export: made from 10b189d1516c, clean
    Export: made from 10b189d1516c, dirty: Git listed changes in the project when the model was exported; a render now records an export that is not that revision and is not release-ready
    Export: made from 10b189d1516c, dirty: Git listed changes in the project when the model was exported; the preview's exportRevision is not the content exported
    Export: made from 10b189d1516c, dirty: Git listed changes in the project when the model was exported; the manifest's exportRevision is not the content exported, and the film is not release-ready

The revision is printed to twelve digits, like the heads. The export does
not say which paths were dirty (the framework records a boolean), so the
line says what Git listed, not which files.

The records gain `exportRevision` and `exportDirty` beside the heads, in
ADR-015's naming: the render manifest's `provenance`, each captured shot
generation's `index.provenance` (and so `cache.shots[].origin`), and the
preview's `report.json` `provenance`. A shot generation is verified for
reuse as before: the fields are not required.

An export made from a dirty tree adds one `releaseIssues` entry, after the
trees':

    export dirty when made: exportRevision 10b189d1516c is not the content exported; export the model again from a clean tree

so `releaseReady` is false for it. Nothing is refused: a rehearsal is made
from whatever export the author has, and the record says what it was.

### D5. The export's source enters no cache key

The renderer serves `/model/manifest.json` byte for byte, `source`
included (the viewer ignores the key, as the framework's ADR-158 states),
and records the served file's SHA-256 as before (`hashes`, `modelSha256`).
For the shot cache's common key alone, the manifest is hashed with its
`source` record removed: an export made again from another commit or with
other dirt, whose picture inputs are unchanged, keeps the common key and
reuses every verified shot. The revision leaves the key with the dirt,
since neither reaches a pixel: the source panels' excerpts are read at
`model.sourceRevision` and reach the frames through the requests, which
the shot keys hash. The proof renders a fixture from a clean export, then
from the same export marked dirty, and asserts the same common key and no
frame captured.

### D6. The fixture exports are made from the recipe commit

The brief expected the framework, run inside Videomaker's repository, to
record Videomaker's `HEAD` and dirt, and the fixtures to pin that value.
It cannot be pinned: Videomaker's `HEAD` moves with every commit and its
tree is dirty while a change is made, and the source panels of the
fixture movies read their excerpts with `git show
<sourceRevision>:models/seesaw.py` in a copy of the project committed by
the recipe, where Videomaker's commits do not exist (and where the
project's paths are not prefixed by `python/tests/fixtures/project/`).

So `scripts/pin-fixture-project.mjs` exports each model from the recipe
copy itself: it makes the recipe commit in a temporary directory, runs
`machinome export <model> -o <temporary output> --no-widget` (with the
seesaw's `--fps 30 --frames 600`) from that copy, with no bytecode written
and no global or system Git configuration, replaces the fixture's export
with the output, and refuses unless the manifest records the recipe
revision and `dirty: false`. The framework then records what is true: the
export was made from the recipe commit, clean. The fixture documents keep
the revision they pin, so no document changes for its revision; the
manifests change by their `source` and by whatever the installed framework
writes differently, and a resolved pin that moves because of it is
re-pinned with `scripts/pin-resolved.mjs` and shown in the evidence. The
script takes `--machinome <command>` (default `machinome`) beside
`--python`.

No test depends on the revision's value beyond its equality with the
recipe commit, which the Python suite computes and the Node suite's copy
reproduces: `test_repository.py` asserts that both manifests record the
recipe commit, clean; `fixture-movie.mjs` refuses a copy whose commit is
not the seesaw manifest's `source.revision`.

### D7. Synthetic exports write `source`

The Node helpers that write a synthetic export for a throwaway project
(`test/support/yaml-project.mjs`, `test/project-fixture.mjs`) write its
manifest with `source: {revision: <the project's commit>, dirty: false}`
instead of a sidecar, and `yamlProject` re-writes it on each commit. A
test marks the export dirty, or removes its source, by writing the
manifest itself.

## Alternatives rejected

- **Fall back to `source-revision.txt` when the manifest has no
  `source`.** It would keep a file the framework never wrote as a second
  authority, and the Curta's hand-typed one alive; the pilot ruled the
  record into the manifest.
- **Evaluate an export without `source` to an unpinned document
  (`sourceRevision: null`).** The Node side refuses such a document at
  load anyway (a null pin equals no revision); refusing where the export is
  read names the cause and the remedy before anything else is built.
- **Refuse an export made from a dirty tree.** Exporting work in progress
  is normal, and the framework exports it; the finding is that the record
  must say so, not that the film must not be made.
- **Keep `source` in the common key.** Every commit of the project, and
  every change of an untracked file, would recapture a whole film whose
  pixels cannot have changed (the Curta's 3 787 frames cost an hour).
- **Hold the export's revision to the project's head.** An export from an
  earlier commit is legitimate (the film pins it and reads its excerpts
  there); the tree lines already say what the project is now.
- **Pin Videomaker's own `HEAD` in the fixture exports** (the brief's
  expectation; D6).
- **Edit the fixture manifests to add `source` by hand.** A record the
  framework did not write is the hand-typed file again, in another place.
