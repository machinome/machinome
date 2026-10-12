## Why

The pilot's decisions of 12 October 2026 (`workflow/ongoing/release-0.9.md`
at the repository root, decisions 1 to 5 and 9) settle how the videomaker
joins the repository: as one member, the distribution `machinome-movie` at
`packages/machinome-movie/`, the portion `machinome.movie` with its Node side
inside it at `machinome/movie/js/`, at the set's version 0.8.1 pinned `~=`
both ways and installed by a new extra `machinome[movie]`, under the set's one
licence, its command `machinome movie` the first contributor of the group
`machinome.commands` (ADR-189) with the verbs `list`, `evaluate`, `watch`,
`check`, `speech`, `preview`, `render`, `build`, `live`, `review` and `setup`,
no `--viewer` option, Node 22 or newer the user's, its dependencies installed
by `machinome movie setup` into the package's own JavaScript directory, its
main and its two finished branches `live-audio-mixer` and `record-review`
taken, its documents folded into the manual, and no module of the former name.

Today the videomaker is a private, unversioned repository with no licence of
its own, two command lines (`python -m machinome_movie` and `node
bin/videomaker.mjs`, which takes the viewer's bundle by path), and five
project repositories that import `machinome_movie` or script the tool by its
checkout. The probes in design.md find that the product does not work at its
new place as it is: its Python package and its Node side read each other's
files across the old `python/` boundary (at the new place 22 of its 298
Python tests fail before those paths move); its 77 fixture documents name
their project by a path that no longer resolves; its Node dependencies conflict in
four majors with the viewer's widget, so the npm workspace's default layout
splits them between two `node_modules`, where the stage build, which reads
its packages from its own directory, cannot find React (design.md probe 6); its split-word gate finds
the identifier `exact_seconds` seven times; and, with the package installed,
four tests of the command seam fail on the fakes named `movie`.

## What Changes

- **The join, by the orchestrator, after the planning commit**: a fresh clone
  of the videomaker rewritten by `git filter-repo` with the mapping of design.md
  Decision 2 (677 files land: 672 under `packages/machinome-movie/`, 5 in the
  framework's manual; `AGENTS.md` and `.env.example` dropped), its `main`
  (1617f81, rewritten 83322ce) merged with `--allow-unrelated-histories`, its
  branches `live-audio-mixer` and `record-review` fetched from the rewritten
  clone as `movie-live-audio-mixer` and `movie-record-review` (two commits each
  on the rewritten main, every path under `packages/`), `remove-progress-rule`
  not taken; rehearsed in the scratch directory, where the merge is clean.
- **`machinome-movie` at `packages/machinome-movie/`**, a product that keeps
  its record in its directory (tests, specs and 281 files of OpenSpec record,
  working record, decision log, experiments, changelog): its manifest at the
  set's version 0.8.1, requiring `machinome~=0.8.1`, `machinome-viewer~=0.8.1`
  and `jsonschema`, under the set's licence, declaring `movie =
  "machinome.movie.cli:Movie"` in `machinome.commands`; the package
  `machinome.movie` with its JavaScript directory `js/` as package data, the
  wheel carrying what the verbs run (77 entries) and nothing the tests alone
  read. **BREAKING** for projects: `machinome_movie` is not provided; names,
  declarations and the movie document are unchanged.
- **`machinome movie`**: one command class meeting the seam's contract, its
  eleven verbs as subparsers; the film verbs run the package's own
  `js/bin/videomaker.mjs` with the Node found through `MACHINOME_NODE` or the
  PATH, version 22 or newer, standard streams passed through and its exit
  status returned; a source is an episode (YAML), a movie document (JSON), or a
  project directory and a movie name, evaluated first; the viewer's bundle is
  the installed viewer's, found through the `machinome.viewer` entry point as
  `machinome develop` finds it; `setup` installs the Node dependencies with
  `npm ci --omit=dev` into `js/node_modules` of the installed package and
  `setup --remove` deletes them; every refusal names the line to run.
- **The npm workspace's second member**: the root `package.json` names the
  movie's `js/` beside the viewer's widget; the root lock grows by the movie's
  resolutions, every one of the viewer's kept; a root `.npmrc` installs each
  member's direct dependencies in its own `node_modules`
  (`install-strategy=shallow`), so the tool reads its packages where it always
  has; Playwright moves to the viewer's 1.63.0, one Chromium for both; the
  member keeps a lock of its own for the installed case.
- **One version and the pins**: the manifest, its pins, the member's
  `package.json` and its lock in `.bumpversion.cfg` and the release records;
  the core's extra `movie = ["machinome-movie~=0.8.1"]`; the root's source and
  dev group; `uv lock` resolves the member and four new packages
  (`jsonschema` and its three dependencies).
- **One licence at the join**: the product carried none; its manifests and
  every file the join writes state the set's expression, and the comment "The
  distribution licence is not selected" goes.
- **The tests at their new place**: the Python tests from the package's
  directory (298), the Node suite from the workspace's root (505 tests in four
  projects); their cross-paths, the 77 fixture documents' roots and the
  fixture project's re-pin follow the move; the records' pinning tests read the
  manual; the seam's fakes `fake-movie` and `fake-movie-two` become `fake-film`
  and `fake-film-two`, and the conformance walk reads the real `movie`.
- **The manual folds in** by reader intent: three how-to guides ("Film a
  movie of your machine", "Declare a movie", "Draw a movie's stage") and the
  reference section `reference/movie/` ("The movie document", "The episode
  format", and the command); the install page's row, the CLI reference's
  section, the `-W` build.
- **The core**: the extra; the layout gate's `PRODUCTS` row and its npm
  workspace tests; the release records; `test_kernel_extras.py` and
  `test_machinome_identity.py`; the split-word gate's ordinary-sense entries
  for `exact_seconds`; the vet universe denying `machinome.movie` to a model;
  `scripts/check-dist`'s row, smoked from the wheel through `setup` and a Node
  verb; CI's steps.
- **Records**: `HISTORY.rst`, the manual's changelog, the product's
  `CHANGELOG.md`, `CREDITS.md`, `docs/architecture.md`, the root `README.md`,
  `CONTRIBUTING.rst`, `context7.json` and `AI-USE.md`; ADR-191 (recommended,
  Open Questions 1); the product's own specs and notes brought current in
  place.
- **Validation in the projects**, by the orchestrator after the
  implementation: 21 Python modules in four repositories move to
  `machinome.movie`, and the video READMEs that show the commands to
  `machinome movie`; the originating check films the Curta's `addition` with
  `machinome movie check` and `preview` from the bench.

Not in this change: the merge of the two fetched branches (the product's,
later), a rename of the stage's module specifier `videomaker/stage`, a hint
for `machinome movie` without the package, the workspace's follow-ups, any
upload or push.

## Capabilities

### New Capabilities

- `movie-distribution`: what the distribution `machinome-movie` ships, how its
  Node side is found and installed, the three forms of a source, the viewer it
  films with, and its refusals.

### Modified Capabilities

- `cli`: the command `machinome movie`, contributed through the group (one
  requirement added).
- `cli-startup-cost`: the movie command's module and its package root import
  no JSON-schema library and none of the movie's modules but the command's, so
  `machinome -h` stays within noise of its cost without the package (one
  requirement added).
- `framework-identity`: the `movie` extra selects the repository's
  distribution (one requirement modified, its scenario titles kept, one
  scenario added); the movie is a product of the set numbered with it, the
  second member of the npm workspace, smoked from its wheel (one requirement
  added).
- `user-documentation`: filming a machine is documented in the manual (one
  requirement added).
- `framework-contributor-guidance`: the guide states how the movie's Python
  and Node tests run and how its dependencies are installed (one requirement
  added).
- `vet`: a model that reaches the movie package is refused as a framework
  internal (one requirement added).

`kernel-extras` is unchanged: its requirements name the kernel and node
extras, and none names `mechanics`, `viewer` or `skills`.

## Impact

- **Tree.** The join adds 677 files. The cycle adds the package's licence
  links, `cli.py`, the root `.npmrc`, ADR-191, the folded pages' edits and the
  edits of design.md Decisions 3 to 15; it deletes nothing the join did not
  bring.
- **Code.** In the package: the import `machinome.movie` (the module
  `machinome_movie` renamed in seven lines of three modules, and 22 lines of
  eleven files of the tests and their fixture project), a lazy
  package root, the command, `stage.py`'s module check, `watch.py`'s
  subprocess, the schema link, three reader-facing messages of the Node side.
  In the core: the manifest's extra, the vet universe's denylist.
- **Tests.** Joining: 7 Python test modules (298 tests) and 52 Node test files
  (505 tests). Changed in the core's suite: `test_repository_layout.py`,
  `test_release_records.py`, `test_docs_structure.py`,
  `test_kernel_extras.py`, `test_machinome_identity.py`,
  `test_core_names_no_split_words.py`, `test_vet_universe.py`,
  `contributed_commands.py`, `test_cli_contributed.py`,
  `test_cli_lazy_imports.py`.
- **Build and CI.** Sixteen members build from `packages/` once the viewer's
  and the skills' joins are on the line; `check-dist` gains a row that needs
  Node and npm; the test job gains the package's Python tests and its Node
  suite's pure and stage projects, FFmpeg for none of them.
- **Environment.** A developer's sync installs the package editable; the root
  `npm ci` installs its Node dependencies; Chromium 1243 serves both members.
- **Projects.** Five repositories reach the videomaker (66 files): 21 Python
  modules import `machinome_movie`, 13 stage modules import `videomaker/stage`
  (unchanged), 11 scripts reach the original checkout by path, 21 Markdown
  files name the commands.

Originating evidence: the pilot's decisions of 12 October 2026, the campaign
plans (`workflow/ongoing/release-0.9.md`, `joins-0.9.md`), the product's own
record, the probes of design.md, the five consuming project repositories, and
the originating check of design.md Decision 16.
