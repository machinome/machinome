## Context

A cycle of the 0.9 campaign, cut from the line `v0.9-joins` at 5af14f71 (the
head after `commands-contributed-by-packages` and the decisions note of 12
October 2026) on the bench `machinome/WTs/v0.9-joins-join-movie`. It runs
beside `join-skills`, both contributors of the command seam; `join-viewer`,
which founds the npm workspace and takes ADR-188, and `join-skills`, which
takes ADR-190, land on the line before this change's planning commit, which
the orchestrator makes after fast-forwarding the bench to the line's head.
This change takes ADR-191. The method of `workflow/ongoing/joins-0.9.md`
holds: the product is imported by rewriting its history directly to its final
paths and merged with `--allow-unrelated-histories` by the orchestrator after
the planning commit; one licence at the join; a product that is not an
extension package keeps its record in its directory; the original repository
stays as it is.

The pilot's decisions of 12 October 2026 (`workflow/ongoing/release-0.9.md`,
decisions 1 to 5 and 9), settled and not reopened here:

- **Address and member.** The videomaker joins as one member, the
  distribution `machinome-movie` at `packages/machinome-movie/`, the portion
  `machinome.movie`, its Node side inside the portion at
  `machinome/movie/js/`. No module of the former name `machinome_movie` and no
  alias; the projects that import it or script `videomaker` move.
- **Version.** The set's, 0.8.1 on this line (the product was unversioned),
  pinned `~=` both ways, installed by a new core extra `machinome[movie]`.
- **One licence** at the join.
- **One command**, `machinome movie`, the first contributor of the group
  `machinome.commands` (ADR-189), with the verbs `list`, `evaluate`,
  `watch`, `check`, `speech`, `preview`, `render`, `build`, `live`, `review`
  and `setup`. No `--viewer` option: the verbs take the installed viewer's
  bundle through the `machinome.viewer` entry point, as `machinome develop`
  does. A source is an episode document (YAML), a movie document (JSON), or a
  project directory and a movie name, evaluated first.
- **Node** is the user's, 22 or newer, found on the PATH or named by
  `MACHINOME_NODE`. `machinome movie setup` installs the Node dependencies into
  the package's own JavaScript directory in the environment that owns it,
  never into a cache; `setup --remove` deletes them; Playwright's Chromium and
  FFmpeg stay documented steps.
- **Branches.** The join takes the videomaker's `main` and its two finished
  branches `live-audio-mixer` and `record-review`, fetched from the rewritten
  clone as `movie-live-audio-mixer` and `movie-record-review`, two commits
  each on the rewritten main, resumed later by merging the line onto them; the
  stale `remove-progress-rule` is discarded.
- **Distribution** is pip only; nothing of the set is published on npm.
- **The manual** stays inside the framework's package; the product's
  documents fold into it.

The videomaker (read-only at `/home/asa/devel/machinome/videomaker`) films a
machinome model: a project declares a movie in Python (`machinome_movie`,
evaluated to the movie document `machinome-movie/0.2`) or writes a YAML
episode, and the Node command `bin/videomaker.mjs` checks it, generates its
narration through ElevenLabs, previews it, renders it through a headless
Chromium mounting the browser viewer's bundle (`--viewer BUNDLE.js`), serves
it live and makes a review pack of the result. Its `main` is 1617f81 (12
October 2026), 242 commits from 19 September 2026, 679 tracked files:
`python/` (the distribution `machinome-movie` 0.0.0, `dependencies =
["machinome", "jsonschema"]`, "The distribution licence is not selected"; the
package `machinome_movie`, twelve modules and the schema as a symbolic link to
`../../schema/machinome-movie-0.2.json`; seven test modules and a fixture
project; an 18-line README), `bin/videomaker.mjs`, `src/` (30 modules),
`stage/` (the React stage), `player/`, `transport/`, `schema/`, `scripts/`
(five, the vitest runner `test.mjs` among them), `test/` and `fixtures/` (the
vitest suite of four projects, `pure`, `stage`, `slow` and `viewer`, and its
content-keyed memo), `docs/` (six pages and 21 ADRs under `docs/adrs/`),
`openspec/` (281 files), `workflow/` (89), `experiments/` (16), `AGENTS.md`,
`CHANGELOG.md` (one `Unreleased` section), `README.md` (523 lines, the tool's
manual), `package.json` (`machinome-videomaker` 0.0.0, private, `engines.node
>=22`, `bin`, dependencies esbuild 0.28.2, highlight.js 11.12.0, playwright
1.62.0, react and react-dom 19.3.0, yaml 2.8.1; dev @types/react,
@types/react-dom, jsdom 30.1.1, typescript 7.0.2, vitest 5.0.3; every version
exact), `package-lock.json`, `vitest.config.mjs`, `.env.example` and
`.gitignore`. Its working tree carries uncommitted edits under
`workflow/ongoing/free-voice/` and an untracked `curta-video.md`, which the
join does not take. The branches: `live-audio-mixer` (bcda766, 866c25a, 9
October 2026: a live audio mixer, `docs/listening.md`, an ADR-023) and
`record-review` (a7c1bd6, a0a1219, 8 October 2026: a native recording of the
live film, `scripts/check-record-review.mjs`, another ADR-023), each two
commits on 1617f81; `remove-progress-rule` (4b90abe, 30 September 2026), one
proposal 186 commits behind, not taken. No tag.

Paths below are the repository's when they start with `packages/` or name a
root file, the framework directory's otherwise; `D` is
`packages/machinome-movie`, `P` the package directory `D/machinome/movie`,
`J` its JavaScript directory `P/js`. Facts were read on the bench at 5af14f71,
on the viewer's bench (its change archived as `2026-10-12-join-viewer` in its
working tree) and the skills' (its planning commit 624aab77) read-only, and in
the product at 1617f81, unless marked *inferred*. Probes ran in the scratch
directory
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C6-propose/`
(`<scratch>` below), never in the bench, the product or a project, with the
bench's venv synced from the lock (CPython 3.12.3), uv 0.11.8,
git-filter-repo `ed61b4050b71`, Node 24.11.1 and npm 11.6.2, `build`, and the
OpenSpec CLI 1.6.0. `<scratch>/merge-rehearsal` is a clone of the bench's
branch at 5af14f71 with the rehearsed import merged and, in a scratch commit
b64e8640, the probe's edits of the JavaScript side; `<scratch>/proto/` is a
prototype of the package (its manifest and `cli.py`), evidence for the shape,
not the implementation.

### What the join touches

- **The product's tracked files and history**: 1013 paths across the three
  branches taken (`<scratch>/history-paths.txt`), under the root files above
  and `bin/`, `docs/`, `experiments/`, `fixtures/`, `openspec/`, `player/`,
  `python/`, `schema/`, `scripts/`, `src/`, `stage/`, `test/`, `transport/`
  and `workflow/`; earlier names live under the same prefixes
  (`schema/machinome-movie-0.1.json`, `src/film.js`). No path is outside them.
- **The licence.** The product carried none: `python/pyproject.toml` says the
  licence is not selected, `package.json` declares no `license`, and the README
  says "A distribution license for Videomaker itself remains unselected" and
  names the licence of the Leonardo project's sources. The join declares a
  licence for the first time, as the plan of 11 October 2026 says. The
  product records no third-party code: its runtime dependencies are npm
  packages installed beside it, and the stage bundle it writes into a
  project's `_build/` carries React and React DOM (`stage/` imports them;
  highlight.js runs in Node, `src/code.mjs`, and only its markup reaches the
  page).
- **Its cross-references.** The Python tests read `fixtures/`, `schema/`,
  `docs/`, `README.md` and `CHANGELOG.md` at the repository's root
  (`python/tests/conftest.py`, `test_repository.py`, `test_take.py`); the Node
  tests and scripts read the Python fixture project at
  `python/tests/fixtures/project` and the package at `python/machinome_movie`;
  77 fixture documents name their project root as
  `../../python/tests/fixtures/project/videos/<movie>`; the Python package's
  schema is a link to `schema/`.
- **Its node_modules assumption.** `src/stage-build.mjs` reads React, the
  React types, TypeScript's `tsc` and esbuild from `<tool>/node_modules`, and
  names every bundled file of that directory `videomaker/node_modules/<file>`
  so a bundle's bytes do not depend on the checkout (the product's ADR-013);
  `test/pipeline/movie-pipeline.test.mjs`, `test/stage-types.test.mjs` and
  `test/player-build.test.mjs` read `<tool>/node_modules` too. TypeScript and
  the React types serve `check` (the stage's type check), not the tests
  alone, yet are listed as development dependencies.
- **Its reader-facing words for the viewer**: two refusals of
  `src/episode.mjs` end "Select a ... machinome-viewer bundle with
  --viewer."; `src/render.mjs`'s retry hint says `node bin/videomaker.mjs
  review <manifest>`; the speech key's refusal says "set ELEVENLABS_API_KEY in
  the environment or in a Videomaker checkout's .env".
- **The core.** `pyproject.toml` (no `movie` extra); the root's sources and
  dev group; the layout gate (`PRODUCTS`, and on the viewer's line
  `NODE_MEMBERS` and `TheNodeWorkspaceTest`, which requires one
  `package-lock.json` in the tracked tree); the release records;
  `test_kernel_extras.py`'s and `test_machinome_identity.py`'s extras tables;
  the split-word gate, which reads every module under `packages/machinome-*/machinome/`;
  `machinome/vet/universe.toml`; the seam's fakes in
  `tests/contributed_commands.py`; `scripts/check-dist`; the CI workflow; the
  manual's `reference/cli.rst` ("The videomaker (``machinome movie``) ... are
  to add theirs"), `start/install.rst` and `index.rst`.
- **Consumers** (probe 16): five project repositories under
  `/home/asa/devel/machinome/projects/`, 66 files.

### Probes

1. **The import, rehearsed** on a fresh clone (`<scratch>/movie-rw`, the three
   branches made local) with the command of Decision 2
   (`<scratch>/filter-repo-command.sh`, output `<scratch>/filter-repo.out`):
   251 commits parsed and rewritten (every ref of the clone), none pruned:
   `main` at 83322ce with 242 commits, as before;
   `live-audio-mixer` at a36e32f (6961fd4, a36e32f) and `record-review` at
   ca99a77 (c552113, ca99a77), each two commits on 83322ce. `main`'s tree holds
   677 files (`<scratch>/rehearsal-ls-files.txt`): 672 under
   `packages/machinome-movie/` (212 under `J`, 33 under `D/tests/`, 281 under
   `D/openspec/`, 113 under `D/workflow/`, 16 under `D/experiments/`) and 5 in
   the framework's manual. `git log --format= --name-only main
   live-audio-mixer record-review` lists no path outside `packages/`. Without
   `--follow`, `git log` on `J/src/render.mjs` lists 31 commits back to
   a716989 (19 September 2026, "Build YAML-to-video workflow with cached
   ElevenLabs narration"), on `P/evaluate.py` 6 back to 6400f8a (30 September
   2026), on `packages/machinome/docs/howto/film-a-movie.rst` (the README) 47
   back to dc14262 (19 September 2026, the scaffold). The one symbolic link,
   `P/machinome-movie-0.2.json`, keeps its target `../../schema/...`, which
   no longer resolves (Decision 4).
2. **The merge, rehearsed** in `<scratch>/merge-rehearsal`: `git fetch
   <scratch>/movie-rw main live-audio-mixer:movie-live-audio-mixer
   record-review:movie-record-review` and `git merge
   --allow-unrelated-histories FETCH_HEAD` of `main`: no conflict, 677 files
   created, 198266 insertions (`<scratch>/merge.out`), `git status` clean;
   `git log --follow` on `J/src/render.mjs` reaches a716989b; the two branches
   read two commits each on 83322ce4. One subject appears twice in the global
   log ("update documentation"), a framework commit and a product commit.
3. **The gates at the join**, twelve suite modules on the merged tree with
   the bench's venv (`<scratch>/gates-at-join.txt`: 22 failed, 176 passed,
   1891 subtests). Red for the join: `test_every_member_is_a_workspace_source`,
   `test_the_readme_links_every_package_and_states_the_licence`,
   `test_every_sibling_is_in_the_table` and
   `test_the_guide_installs_every_member_without_uv` (each naming
   `machinome-movie`); `test_every_member_is_numbered_with_the_core` (0.0.0),
   `test_every_pin_between_members_is_compatible` (the bare `machinome`) and
   `test_the_version_is_bumped_from_the_root`;
   `test_no_module_names_the_split_but_by_its_two_words` (seven occurrences of
   the identifier `exact_seconds` in `P/document.py`, `P/take.py` and
   `P/names.py`); and two subtests of `test_docs_structure.py` on
   `howto/film-a-movie.rst` (the README names the licence of the Leonardo
   project's sources). The rest are the rehearsal's own (the bench's editable
   lines name the bench's directories, so `test_each_portion_resolves_from_its_package`
   and `test_each_product_resolves_from_its_directory` read the bench), not
   counted, as in the earlier joins. `test_core_names_no_scad.py`,
   `test_node_root_exports_nothing.py`, `test_core_kernel_free.py`,
   `test_machinome_identity.py`, `test_kernel_extras.py`,
   `test_vet_universe.py`, `test_mechanics_boundary.py` and
   `test_docs_exports.py` pass on the joined tree.
4. **The Python tests, before and after the move.** At the original layout (a
   fresh clone, `PYTHONPATH=python`, a scratch venv `<scratch>/venv-try`
   layered on the bench's with `jsonschema` added): 298 passed
   (`<scratch>/py-tests-original.txt`). At the new place (`<scratch>/py-probe`,
   `machinome_movie` renamed `machinome.movie` in the package and the tests,
   `conftest.py`'s repository the package's `js/`, the link retargeted,
   `PYTHONPATH=D`): 22 failed, 276 passed; with the 77 fixture documents'
   roots moved (Decision 13): 11 failed; with the fixture project re-pinned
   (probe 5) and `test_take.py`'s one path moved: 9 failed, 289 passed
   (`<scratch>/py-tests-new-place-3.txt`), each a pinning test of
   `test_repository.py` reading `docs/`, `README.md` or `CHANGELOG.md` at the
   product's former root.
5. **The fixture project's re-pin.** Renaming the import in the fixture
   project's five movie modules changes its reproducible commit, which every
   export's manifest records (`test_the_fixture_revision_is_a_reproducible_commit_of_the_project`).
   `scripts/pin-fixture-project.mjs`, its three paths moved, run at the new
   place with the scratch venv and the bench's `machinome`
   (`<scratch>/repin.txt`): both exports remade from 55ad41b, their models
   byte for byte as before and their manifests differing in `mtime` and the
   recorded revision; the documents `minimal`, `tour` and `count` changed in
   two lines each (the root and the revision); it prints the line to run
   `scripts/pin-resolved.mjs minimal tour count`, which the applier runs and
   reviews.
6. **The npm workspace, npm's default layout.** The viewer bench's root
   `package.json` and lock (176 packages, `<scratch>/root-lock.viewer-only.json`)
   with the widget's `package.json` and the movie's `J` as a second member
   (`<scratch>/npm-ws`): `npm install` "added 137 packages", the lock from
   2698 to 4025 lines. npm hoists to the root what does not conflict and nests
   under `J/node_modules` the movie's esbuild 0.28.2, TypeScript 7.0.2, vitest
   5.0.3 and jsdom 30.1.1, whose majors differ from the widget's (0.24.2,
   5.9.3, 3.2.7, 29.1.1); React, the React types, Playwright, yaml and
   highlight.js land at the root. Seven of the viewer's 176 resolutions
   change. The Node suite from that layout (`<scratch>/node-suite-ws.txt`,
   a scratch directory that is no Git work tree, the fixture documents'
   roots not yet moved, `stage-build.mjs` made to resolve its packages
   through Node's own lookup by `<scratch>/probe_js_patch.py`): 94 failed,
   411 passed of 505. Among them, the two tests that bundle the stage from a
   second checkout whose `node_modules` links the tool's (`Cannot find module
   'react/package.json'`: React is at the root) and the pipeline tests that
   import `<tool>/node_modules/playwright/index.mjs` fail on the layout
   itself; the rest on the missing Git work tree and the fixtures' roots.
   Under that layout the tool's assumption that its packages sit in its own
   `node_modules` holds under no change smaller than rewriting those tests and
   the bundle's names.
7. **The npm workspace, each member's dependencies in its own
   `node_modules`.** The same root with a root `.npmrc` holding
   `install-strategy=shallow` (`<scratch>/npm-ws-nested`): from the viewer's
   seeded lock, `npm install` "added 144 packages"; all 176 of the viewer's
   resolutions stay at their paths and versions; the movie's direct
   dependencies, the four conflicting ones and React, the React types,
   Playwright, yaml and highlight.js alike, are in `J/node_modules` (34
   entries, `.bin/tsc` and `.bin/esbuild` among them); the lock is 4152 lines.
   `npm ci` at the root reproduces it ("added 144 packages"); `npm ci` run in
   `J` installs that member alone, in the same layout ("added 86 packages").
   From no lock at all the same `.npmrc` gives each member a whole tree of its
   own (the widget's `node_modules` 78 entries, the root's 1,
   `<scratch>/npm-ws-shallow-fresh`): the layout follows the lock, which keeps
   the viewer's.
8. **The Node suite at its new place**, from the root of
   `<scratch>/merge-rehearsal` under the layout of probe 7 (the root
   `package.json`, lock and `.npmrc`, the widget's `package.json`), with the
   path edits of Decision 13 committed in the scratch clone, Playwright 1.63.0,
   `VIDEOMAKER_VIEWER_BUNDLE` naming the viewer bench's built bundle (0.8.1,
   API 29) and `stage-build.mjs` unchanged (`<scratch>/node-suite-shallow.txt`):
   52 files, 505 tests, 493 passed and 12 failed, none skipped, in 958 s;
   the four projects ran, `pure` 25 files, `stage` 6, `slow` 17 and
   `viewer` 4 on the real viewer. The twelve failures are all in
   `test/repository.test.mjs`, each a pin of the product's records at its
   former root (`docs/*.md`, `README.md`, `AGENTS.md`). The pipeline
   tests' Git provenance reads the scratch clone's tree, clean at its
   commit. The `pure` and `stage` projects alone (`npm test --workspace
   <J> -- --project pure --project stage`, `<scratch>/node-suite-pure-stage.txt`):
   31 files, 329 tests, 317 passed and the same 12 failed, in 7 s.
9. **Playwright.** The movie pins 1.62.0, whose Chromium is build 1234; the
   viewer's lock installs the Python Playwright 1.63.0, build 1243. With the
   member's pin at 1.63.0, `node_modules/playwright-core/browsers.json` names
   `chromium` and `chromium-headless-shell` 1243, the build
   `~/.cache/ms-playwright` holds for the viewer; probe 8 ran on it.
10. **The member's own lock.** `J/package.json` (the name `@machinome/movie`,
    version 0.8.1, Playwright 1.63.0, no `bin`) and the product's lock copied
    to a scratch directory outside any workspace, `npm install
    --package-lock-only`: "up to date", 42 lines of the lock changed (the name,
    the version, Playwright and its core, `fsevents` gone); with TypeScript and
    the two React type packages moved to `dependencies` (Decision 3), 33 more
    lines (their `dev` flags). npm ignores a member's lock inside the workspace
    (the viewer's probe 5) and reads it where there is none.
11. **The installed case.** The prototype built (`<scratch>/proto`,
    `python -m build`): the wheel 77 entries, the twelve modules and
    `cli.py`, the schema as a regular file, `J/package.json`, `J/package-lock.json`,
    `J/bin/`, `J/src/` (30), `J/stage/` (10), `J/player/` (7), `J/transport/`
    (4), `J/schema/`, the licence files and the entry point `movie =
    machinome.movie.cli:Movie`; no test, fixture, script or `node_modules`;
    the sdist 926 entries; `twine check --strict` passes both. setuptools warns
    twenty times at the build, "Package 'machinome.movie.js...' is absent from
    the `packages` configuration", once for each directory of `J`, and the
    data is carried all the same. Installed with the core's wheel built from
    the bench and the published `machinome-viewer` 0.8.0
    (`<scratch>/installed-venv`, no root, no root lock): `machinome -h` lists
    `movie` after `vet`; `machinome movie check x.yaml` before `setup` exits 1,
    "Error: the Node dependencies of machinome movie are not installed; run:
    machinome movie setup"; `setup` with `MACHINOME_NODE=/usr/bin/false`, with
    a Node reporting v20.11.0, and with no Node on the PATH exits 1 naming each;
    `machinome movie setup` runs `npm ci --omit=dev` in
    `site-packages/machinome/movie/js/`: 14 packages, 81 MB, 1.5 s from npm's
    cache, and prints the Chromium line; then `machinome movie review` and
    `check` of a missing file reach Node, which exits 1 naming the path;
    `machinome movie check` of the fixture project's `tour` document (its
    project committed by the recipe) runs the document's load in Node up to
    "Chapter opening has spoken anchors and no cached narration take; run the
    speech command first"; with the viewer uninstalled, `check` exits 1 "Error:
    machinome movie check needs the browser viewer: The browser viewer is not
    installed. ...", and `speech` still reaches Node; `setup --remove` deletes
    `J/node_modules`. `npm ci --omit=dev` beside a copy of `J/package.json`
    alone refuses, `EUSAGE`, "can only install with an existing
    package-lock.json" (`<scratch>/npm-ci-nolock/out.txt`). `pip uninstall
    machinome-movie` leaves `J/` behind with
    its 81 MB of `node_modules`. `machinome movie check . tour` (the project
    form) refused with the traceback of the fixture model's
    `ExtraUnavailable` for `cadquery`, absent from that venv (Decision 5).
12. **The seam's tests with the package installed.** The prototype's wheel in
    `<scratch>/venv-try` (`entry_points(group='machinome.commands')` reads one
    entry, `movie = machinome.movie.cli:Movie` of `machinome-movie`), and
    `test_cli_contributed.py`, `test_cli_lazy_imports.py` and `test_cli.py`
    run from the rehearsal's framework directory
    (`<scratch>/seam-with-movie.txt`): 7 failed, 49 passed, 1 skipped.
    `test_a_contributed_command_runs_with_its_own_verbs` (its three subtests
    exit 1, "Error: machinome movie is contributed by more than one package:
    fake-movie (machinome_fake_movie:Movie), machinome-movie
    (machinome.movie.cli:Movie)"), `test_help_lists_contributed_commands_after_the_framework`
    (`movie` unavailable), `test_a_name_two_packages_contribute_runs_neither`
    (three packages named, not two), `test_a_module_that_cannot_be_imported`
    (the choices end `gone,movie`) and
    `test_the_contract_walk_reads_a_fake_distribution` (the real package beside
    the fakes). `test_every_contributed_entry_resolves_and_honours_the_contract`
    walks the real `movie` and passes.
13. **The lock.** The viewer bench's manifests and lock copied to
    `<scratch>/uv-lock-probe` ("Resolved 192 packages" offline, the lock
    unchanged), with the member, the core's extra `movie =
    ["machinome-movie~=0.8.1"]`, the root's source and the dev group gaining
    `machinome[movie]`: `uv lock` "Resolved 197 packages", adding
    `machinome-movie` 0.8.1, `jsonschema` 4.26.0, `jsonschema-specifications`
    2025.9.1, `referencing` 0.37.0 and `rpds-py` 2026.9.1; the diff is 211
    lines (`<scratch>/uv-lock.diff`). Offline it fails, `jsonschema` not being
    in uv's cache. On the line with the skills' member the count is one more
    (*inferred*).
14. **The command's cost**, medians of eleven alternating runs in
    `<scratch>/installed-venv` (the movie installed) and `<scratch>/base-venv`
    (the same wheels without it), `<scratch>/probe_wall.py`
    (`<scratch>/wall-alternating.txt`): `machinome -h` 685 ms against 622 ms;
    `vet -h` 34 against 36 ms; an unknown name 70 against 70 ms; `machinome
    movie -h` 126 ms. `python -X importtime -c "import machinome.movie.cli"`:
    111 ms cumulative, of which the package root's re-exports 105 ms
    (`machinome.movie.document` 65 ms, `jsonschema` 41 ms of it). With the
    package root made lazy (the names read from their modules on first use,
    PEP 562, `<scratch>/wall-lazy.txt`): `machinome -h` 626 ms against 607 ms,
    `machinome movie -h` 72 ms, `from machinome.movie import Movie, evaluate`
    answering as before. A dispatch of `machinome movie list` imports no
    `machinome.manager.*` module.
15. **The vet.** A scratch copy of the fixture project, vetted on the bench's
    venv with the prototype on the path: a model importing `from
    machinome.movie import Movie` is pure, one importing `machinome_movie` is
    `outside-universe machinome_movie`, and an import of `machinome_movie` in
    `videos/tour/movie.py` changes nothing: vet reads the models, not the movie
    declarations. The address moves the movie from outside the universe into
    the contract unless the denylist names it, as `join-viewer`'s probe 21
    found for the viewer.
16. **The projects** (`grep -rIl -e machinome_movie -e videomaker`,
    `node_modules`, `_build`, `.git`, `.venv` and `WTs` skipped,
    `<scratch>/projects-grep.txt`): 66 files in five repositories, Leonardo
    (in `videos/`), kossel, Curta-Type-I-3x, Metamaquina2 and
    lumiere-cinematographe. 21 Python modules import `machinome_movie` (13 in
    Leonardo, 4 in kossel, 2 each in Metamaquina2 and the Curta): each film's
    `movie.py` and its `narration.py`, `editorial.py` or `takes.py`. 13 stage
    modules import `videomaker/stage` or `videomaker/movie`, the stage's own
    module specifiers, which the stage build resolves. 11 scripts reach the
    original checkout by path (`/home/asa/devel/machinome/videomaker/src/...`,
    `createRequire(.../videomaker/package.json)`, or a tool path given as an
    argument): auditions, a pause and a loop verification, an audio spike, and
    lumiere's `prepare.mjs` and `render-selected.mjs`. 21 Markdown files name
    the commands: each film's README showing `python -m machinome_movie
    evaluate` and `node bin/videomaker.mjs <verb> ... --viewer <bundle>` as the
    way to make it, and records of a day (`VERIFICATION.md`, `HANDOFF.md`,
    `VOICE-DESIGN.md`, `NARRATION.md`, `review-notes.md`).
17. **The deltas, archived in scratch.** A copy of the bench's `openspec/`
    with this change's planning artifacts and a one-line tasks file
    (`<scratch>/os-probe`, `<scratch>/os-archive.txt`): `openspec archive
    join-movie -y` creates `movie-distribution` (+ 5) and applies + 1 to
    `cli`, `cli-startup-cost`, `framework-contributor-guidance`,
    `user-documentation` and `vet`, and + 1, ~ 1 to `framework-identity`
    (totals + 11, ~ 1); `openspec validate --specs --strict` passes 47 of
    47. Every scenario survives: `framework-identity` 29 to 35 (against the
    bench's base, the modified requirement carrying the viewer's and the
    skills' scenario beside the movie's), `cli` 113 to 116,
    `cli-startup-cost` 41 to 43, `user-documentation` 86 to 88,
    `framework-contributor-guidance` 9 to 10, `vet` 66 to 68, and
    `movie-distribution` 11. The created spec's Purpose is the CLI's
    placeholder, for the applier to write at the archive.

## Goals / Non-Goals

**Goals:**

- The videomaker joins at `packages/machinome-movie/` with its history, every
  file at its final path, its two finished branches fetched beside the line,
  the merge rehearsed and clean.
- One installable product, `pip install "machinome[movie]"` then `machinome
  movie setup`, whose eleven verbs run from the one command, film with the
  installed viewer, and refuse with the line to run.
- Its Python tests and its Node suite green at their new place, run by a
  contributor from one checkout and one `npm ci`, and the parts that need no
  browser by CI; its record kept in its directory and brought current.
- Its documents in the manual by reader intent.
- The projects on `machinome.movie` and `machinome movie`; the Curta's
  `addition` checked and previewed from the bench.

**Non-Goals:**

- Any change of behaviour of the tool: the movie document, the episode
  formats, the stage, the render, the live session, the review pack.
- The merge of `movie-live-audio-mixer` and `movie-record-review`, which the
  product resumes later.
- A rename of the stage's module specifiers `videomaker/stage` and
  `videomaker/movie`, of `bin/videomaker.mjs`, or of the bundle names of the
  product's ADR-013 (Open Questions 12).
- A hint for `machinome movie` when the package is absent (ADR-189's decision;
  the skills' Open Questions 9).
- Publication on npm, an upload, a push; the workspace's follow-ups.

## Decisions

### 1. The join merges `main`, 1617f81, and fetches the two branches

`main` is the product's state; `live-audio-mixer` and `record-review` are
finished work the pilot keeps, each two commits on `main`'s head, and
`remove-progress-rule` is a proposal 186 commits behind, discarded. The
filter rewrites every ref of the clone with one deterministic command
(probe 1), so the two branches are fetched from the rewritten clone with their
commits on the rewritten `main`, which the line then contains. They are not
merged by this change: the product resumes each later by merging the line onto
it. Every path either branch adds (`docs/listening.md`,
`scripts/check-record-review.mjs`, two ADR-023 records, specs, tests) lands at
the place the mapping gives its prefix.

### 2. The mapping and the import

| at 1617f81 (and on the branches, and in history) | lands at | reason |
|---|---|---|
| `python/machinome_movie/` | `P/` | the portion at its address; its schema link edited in place (Decision 4) |
| `python/tests/` (seven modules, `conftest.py`, the fixture project) | `D/tests/` | the product's Python tests, its record |
| `python/pyproject.toml` | `D/pyproject.toml` | the package's manifest, rewritten in place (Decision 3) |
| `python/README.md` | `D/README.md` | the Python half's README, rewritten in place to the shape of the products' (Decision 3) |
| `bin/`, `src/`, `stage/`, `player/`, `transport/`, `schema/` | `J/bin/`, `J/src/`, `J/stage/`, `J/player/`, `J/transport/`, `J/schema/` | what the verbs run, inside the portion (the pilot's decision) |
| `package.json`, `package-lock.json` | `J/package.json`, `J/package-lock.json` | the npm member's manifest, and its own lock for the installed case (Decision 6) |
| `vitest.config.mjs`, `scripts/`, `test/`, `fixtures/` | `J/vitest.config.mjs`, `J/scripts/`, `J/test/`, `J/fixtures/` | the Node suite beside the sources it imports by `../src/`, its runner and its fixtures; excluded from the wheel (Decision 3, Open Questions 2) |
| `README.md` | `packages/machinome/docs/howto/film-a-movie.rst` | the tool's manual today: setup, the verbs, the outputs, timing; converted in place (Decision 12) |
| `docs/declaring-a-movie.md` | `packages/machinome/docs/howto/declare-a-movie.rst` | one job: declare a movie in Python |
| `docs/stage.md` | `packages/machinome/docs/howto/draw-a-movie-stage.rst` | one job: write the stage module a movie's sets are drawn by |
| `docs/listening.md` (branch `live-audio-mixer`) | `packages/machinome/docs/howto/listen-to-a-movie.rst` | the branch's how-to, at its place when the branch is resumed |
| `docs/movie-document.md` | `packages/machinome/docs/reference/movie/document.rst` | lookup: the JSON document |
| `docs/FORMAT.md` | `packages/machinome/docs/reference/movie/episode.rst` | lookup: the YAML episode formats (Open Questions 16) |
| `docs/first-rehearsal.md` | `D/workflow/first-rehearsal.md` | a record of 19 September 2026 (its evidence, its reproduction), not a guide |
| `docs/architecture-overview.md` | `D/workflow/architecture-overview.md` | the product's architecture as of the join, which the branches edit; its substance goes to the framework's `docs/architecture.md` (Decision 14) |
| `docs/adrs/` | `D/workflow/adrs/` | the product's own decision log, under its own numbers, as the viewer keeps its (Open Questions 6) |
| `openspec/`, `workflow/`, `experiments/` | `D/openspec/`, `D/workflow/`, `D/experiments/` | its record |
| `CHANGELOG.md`, `.gitignore` | `D/CHANGELOG.md`, `D/.gitignore` | its changelog, kept whole with its entry; its leavings, edited in place |
| `AGENTS.md` | dropped | the framework owns no agent prompts; its testing policy is the product's ADR-003, which stays (Open Questions 9) |
| `.env.example` | dropped | one variable, which the how-to states (Decision 5) |

Both `README.md` files land, each at the place of the role it takes: the
root one is the tool's manual and becomes a how-to, its history kept at the
page; the Python half's becomes the package's README. A move and an edit never
share a commit: the join moves, the implementation commit edits. The
rewritten commits keep their messages, authors and dates.

The command, run by the orchestrator in a fresh clone (`git clone
file:///home/asa/devel/machinome/videomaker <dir>`, then `git branch
live-audio-mixer origin/live-audio-mixer` and `git branch record-review
origin/record-review`), as rehearsed in probe 1
(`<scratch>/filter-repo-command.sh`):

```
D=packages/machinome-movie
P=$D/machinome/movie
J=$P/js
M=packages/machinome/docs
git filter-repo \
  --path AGENTS.md --path .env.example \
  --invert-paths \
  --path-rename README.md:$M/howto/film-a-movie.rst \
  --path-rename python/README.md:$D/README.md \
  --path-rename python/pyproject.toml:$D/pyproject.toml \
  --path-rename python/machinome_movie/:$P/ \
  --path-rename python/tests/:$D/tests/ \
  --path-rename CHANGELOG.md:$D/CHANGELOG.md \
  --path-rename .gitignore:$D/.gitignore \
  --path-rename package.json:$J/package.json \
  --path-rename package-lock.json:$J/package-lock.json \
  --path-rename vitest.config.mjs:$J/vitest.config.mjs \
  --path-rename bin/:$J/bin/ \
  --path-rename src/:$J/src/ \
  --path-rename stage/:$J/stage/ \
  --path-rename player/:$J/player/ \
  --path-rename transport/:$J/transport/ \
  --path-rename schema/:$J/schema/ \
  --path-rename scripts/:$J/scripts/ \
  --path-rename test/:$J/test/ \
  --path-rename fixtures/:$J/fixtures/ \
  --path-rename docs/declaring-a-movie.md:$M/howto/declare-a-movie.rst \
  --path-rename docs/stage.md:$M/howto/draw-a-movie-stage.rst \
  --path-rename docs/listening.md:$M/howto/listen-to-a-movie.rst \
  --path-rename docs/movie-document.md:$M/reference/movie/document.rst \
  --path-rename docs/FORMAT.md:$M/reference/movie/episode.rst \
  --path-rename docs/first-rehearsal.md:$D/workflow/first-rehearsal.md \
  --path-rename docs/architecture-overview.md:$D/workflow/architecture-overview.md \
  --path-rename docs/adrs/:$D/workflow/adrs/ \
  --path-rename openspec/:$D/openspec/ \
  --path-rename workflow/:$D/workflow/ \
  --path-rename experiments/:$D/experiments/
```

Each rename names an explicit prefix of an original path, no two overlapping:
`README.md` matches only the root file, `python/README.md` its own; no
`workflow/` path is named `first-rehearsal.md`, `architecture-overview.md` or
`adrs/`. No catch-all: part of the product goes to the framework's manual.
The product has no tag, so no `--tag-rename`.

The orchestrator then checks that `git ls-tree -r --name-only main` lists
the 677 paths of `<scratch>/rehearsal-ls-files.txt`, that `main` is 83322ce,
`live-audio-mixer` a36e32f and `record-review` ca99a77 (*inferred*
deterministic: the same input and options), and that no commit of the three
touches a path outside `packages/`; fetches `main` and
`live-audio-mixer:movie-live-audio-mixer` and
`record-review:movie-record-review` into the bench; and merges `main` with
`git merge --allow-unrelated-histories`, one merge commit, after the planning
commit.

### 3. The package's directory

`D` after the cycle holds `pyproject.toml`, `README.md`, `CHANGELOG.md`,
`MANIFEST.in`, `.gitignore`, the links `LICENSE -> ../../LICENSE` and
`LICENSES -> ../../LICENSES`, the package directory `machinome/movie/` (its
own `__init__.py`, none at `machinome/`; `js/` inside it), `tests/`,
`openspec/`, `workflow/` and `experiments/`.

`pyproject.toml`, replacing the product's (built, installed and smoked in
probes 11 and 13):

```toml
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "machinome-movie"
version = "0.8.1"
description = "Narrated films of machinome models: movies declared in Python, evaluated to the movie document, then checked, voiced, previewed, rendered and served"
readme = { file = "README.md", content-type = "text/markdown" }
requires-python = ">=3.11"
license = "GPL-2.0-or-later OR CERN-OHL-S-2.0+"
license-files = ["LICENSE", "LICENSES/*.txt"]
authors = [
    { name = "Luis Fagundes", email = "lhfagundes@gmail.com" },
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Multimedia :: Video",
]
keywords = ["machinome", "video", "film"]
dependencies = [
    # The framework a movie's take is recorded through, and the browser
    # viewer every frame is drawn by, released with it: the set carries one
    # version, and the pins between its packages are ~= both ways.
    "machinome~=0.8.1",
    "machinome-viewer~=0.8.1",
    "jsonschema",
]

[project.urls]
Homepage = "https://github.com/machinome/machinome"

# `machinome movie`, a command this package adds to machinome (ADR-189).
[project.entry-points."machinome.commands"]
movie = "machinome.movie.cli:Movie"

[tool.setuptools.packages.find]
# The package directory machinome/movie/, which has its own __init__.py,
# with none at machinome/. Its js/ directory is package data, not a package.
include = ["machinome.movie"]
namespaces = true

[tool.setuptools]
include-package-data = true
zip-safe = false

[tool.setuptools.package-data]
# The movie document's schema, a link to js/schema/ in the tree, a file in
# the wheel.
"machinome.movie" = ["machinome-movie-0.2.json"]

[tool.setuptools.exclude-package-data]
# The wheel carries what the verbs run; the Node suite, its fixtures, its
# scripts and its configuration travel in the sdist alone.
"machinome.movie" = [
    "js/test/*",
    "js/fixtures/*",
    "js/scripts/*",
    "js/vitest.config.mjs",
    "js/*.test.*",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

`MANIFEST.in`, new:

```
include CHANGELOG.md
recursive-include machinome/movie/js *
prune machinome/movie/js/node_modules
prune machinome/movie/js/.test-memo
recursive-include tests *
recursive-include openspec *.md *.yaml
recursive-include workflow *
recursive-include experiments *
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
```

The excluded data is keyed by the package's name, as the viewer learnt (its
probe 11). The setuptools warnings of probe 11 name each directory of `js/`
and change nothing the archives carry; `check-dist`'s smoke holds the wheel's
file list (Decision 11).

`README.md`, replacing the Python half's, in the products' shape:

```markdown
# machinome-movie

The films of [Machinome](https://github.com/machinome/machinome): the
package `machinome.movie` and the command `machinome movie`. A project
declares a movie of its machine in Python, or writes an episode in YAML;
the command evaluates it to the movie document, checks it, generates its
narration, previews it, renders it through the browser viewer, serves it
live and makes the review pack of the result. Its Node side runs on the
user's Node 22 or newer.

## Install

    pip install "machinome[movie]"
    machinome movie setup

## Manual

<https://machinome.readthedocs.io>

## Licence

GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, at the recipient's choice; the
texts are in `LICENSE` and `LICENSES/`.
```

`.gitignore`, edited in place to this package's own leavings (the root's
covers `__pycache__/`, `*.py[cod]`, `/packages/*/build/`,
`/packages/*/*.egg-info/`, `/.venv/`, `/.env`, `/node_modules/`):

```
# This package's leavings the root's .gitignore does not name: the Node
# dependencies npm installs into js/, its own test runs and their memo
# outside a Git work tree, a local build, the films a test or a probe
# writes under a project's _build/, and a speech key the Node side reads
# from js/.env.
node_modules/
.pytest_cache/
.test-memo/
dist/
_build/
*.log
.env
.env.*
```

**`J/package.json`**, edited in place: the name `@machinome/movie` (the
widget is `@machinome/viewer`), the version `0.8.1`, `"license":
"GPL-2.0-or-later OR CERN-OHL-S-2.0+"`; `bin` and the `video` script go, the
command being `machinome movie`; Playwright `1.63.0` (Decision 6);
TypeScript, `@types/react` and `@types/react-dom` move to `dependencies`,
which `check` runs (the stage's type check), so `setup`'s `npm ci --omit=dev`
installs them; vitest and jsdom stay development dependencies. Every version
stays exact. `J/package-lock.json` is regenerated by `npm install
--package-lock-only` in a scratch copy of `J` outside the workspace, then
copied back (probe 10).

**Headers.** The product's files carry no SPDX line and gain none; the
manifests carry the expression.

### 4. The source at its address

- **The import.** `machinome_movie` becomes `machinome.movie` in the three
  modules that spell it: `__main__.py`'s docstring and parser,
  `stage.py`'s test of a shipped set's module (`cls.__module__ ==
  'machinome.movie' or ...startswith('machinome.movie.')`), and `watch.py`'s
  docstring and evaluation command (`[sys.executable, '-m',
  'machinome.movie', 'evaluate', ...]`). Docstrings and comments naming
  `python/machinome_movie/<module>.py` in `J/src/` name
  `machinome/movie/<module>.py`.
- **The package root is lazy** (Open Questions 11): `__init__.py` keeps its
  docstring and `__all__` and maps each of its 45 names to its module, read on
  first use through a module `__getattr__` (PEP 562), as
  `machinome.node.freecad`'s root does; `from machinome.movie import Movie`
  answers as before. `machinome -h` and `machinome movie -h` then import no
  JSON-schema library (probe 14).
- **`__main__.py`** runs the command's own parser: `python -m machinome.movie
  <verb> ...` is `machinome movie <verb> ...`, one parser, so `watch`'s
  evaluation in a process of its own runs `python -m machinome.movie evaluate`
  as it ran `python -m machinome_movie evaluate`.
- **The schema link** `P/machinome-movie-0.2.json` is retargeted to
  `js/schema/machinome-movie-0.2.json`, one file both runtimes read
  (`J/test/repository.test.mjs` holds the two equal through `realpath`); the
  wheel carries it as a regular file (probe 11).
- **The Node side's reader-facing words**: the two refusals of
  `src/episode.mjs` end "Install a machinome-viewer that declares it: pip
  install -U \"machinome[viewer]\"." instead of naming `--viewer`;
  `src/render.mjs`'s retry hint says `machinome movie review <manifest>`; the
  speech key's refusal says "set ELEVENLABS_API_KEY in the environment, or in
  the .env of the directory machinome movie runs from" (the framework's
  `load_dotenv()` puts that file's variables into the environment before any
  command runs, the `cli` capability's "Dotenv loading with environment
  precedence", and the Node child inherits them). `keyFiles()` is unchanged:
  it still looks in its own directory's `.env`, now `J/.env`. The tests that
  match those words follow.
- **`--viewer`** stays the Node command's internal option; `bin/videomaker.mjs`
  is otherwise unchanged.

### 5. The command `machinome movie`

`P/cli.py`, the class `Movie`, meeting ADR-189's contract: a docstring ("Film
a machine: evaluate a project's movies, then check, voice, preview, render,
build, serve and review them."), `needs_node = False`, `add_arguments`,
`handle`. Its module imports the standard library alone at module scope
(probe 14 measured the prototype). The verbs are subparsers, each with the
options the product's two command lines have, `--viewer` excepted:

| verb | arguments | runs |
|---|---|---|
| `list` | `PROJECT` | Python: the project's movies table |
| `evaluate` | `PROJECT MOVIE [--out FILE]` | Python: the movie document, its path printed |
| `watch` | `PROJECT MOVIE [--out FILE] [--interval SECONDS]` | Python: evaluate, then again on every change of the project, until interrupted |
| `check`, `speech`, `preview`, `render`, `build` | `SOURCE [MOVIE] [--width N] [--fps N] [--silent]` | Node |
| `live` | `SOURCE [MOVIE] [--width N] [--port N] [--poll MS] [--open]` | Node, until interrupted |
| `review` | `MANIFEST` | Node: the review pack of a rendered film's manifest (Open Questions 7) |
| `setup` | `[--remove]` | installs, or removes, the Node dependencies |

- **The source.** `SOURCE` is an episode (`.yaml`), a movie document
  (`.json`), or a project directory followed by `MOVIE`. A directory is
  evaluated first by `evaluate`'s code in the command's own process (the
  document written to `<movie directory>/_build/movie.json`, its path
  printed), and the Node command is given that document. A directory without
  `MOVIE`, or `MOVIE` after a file, is refused naming the form. A movie whose
  model needs an absent extra is answered as the seam answers a command's:
  `Error: machinome movie <verb> needs the <extra> extra: <refusal>`, exit 1
  (probe 11 found a traceback). The same holds for `evaluate` and `watch`.
- **Node.** `MACHINOME_NODE` when set, else `node` on the PATH (Open
  Questions 15); its `--version` must be 22 or newer. Refusals, exit 1, each
  one line: none found ("machinome movie needs Node 22 or newer: none is on
  the PATH; install Node 22, or name it with MACHINOME_NODE"), one that cannot
  run (naming it and `MACHINOME_NODE` when that named it), one older (naming
  its path and version).
- **The dependencies.** A Node verb first asks whether `J/node_modules`
  holds the tool's packages (`esbuild`'s `package.json`); if not, it refuses:
  "the Node dependencies of machinome movie are not installed; run: machinome
  movie setup", or, when `J` is a member of an npm workspace (an ancestor
  `package.json` whose `workspaces` names it, the repository's checkout),
  "run: npm ci in <root>".
- **The viewer.** `check`, `preview`, `render`, `build` and `live` pass
  `--viewer <path>`, the `path` of `machinome.viewers.bundle.describe()`, the
  report `machinome develop` reads through the `machinome.viewer` entry point.
  When it raises `ViewerUnavailable`, the verb refuses, "Error: machinome movie
  <verb> needs the browser viewer: <remedy>", exit 1 (probe 11). `speech` and
  `review` draw nothing and pass none.
- **The run.** `[node, J/bin/videomaker.mjs, verb, source, options...]`,
  the working directory the user's, the environment inherited, the standard
  streams passed through; the command waits for the process, an interrupt
  passed to the child as the terminal passes it, and exits with its status.
- **`setup`** refuses, before anything, when `J` is a member of an npm
  workspace ("this machinome-movie is the source in the npm workspace at
  <root>; its dependencies are installed by npm ci there": an editable
  install, where `npm ci` in `J` installs at the root, the viewer's probe 5)
  and when any `node_modules` from `J` up to the filesystem root is a symbolic
  link, naming it (the viewer's guard). Otherwise it finds Node as above and
  `npm` beside it or on the PATH (refusing, naming both, when there is none),
  prints where it installs and with what, and runs `npm ci --omit=dev
  --no-audit --no-fund` in `J`, which reads `J/package-lock.json`; it then
  prints the second step, `<node> <J>/node_modules/playwright/cli.js install
  chromium`, and that FFmpeg is the system's. It exits with npm's status.
  `setup --remove` deletes `J/node_modules` when it exists and is not a link
  (saying so either way), with the same two refusals first. Nothing is
  written outside `J`.

### 6. The npm workspace

- **The root `package.json`**'s `workspaces` gains
  `packages/machinome-movie/machinome/movie/js` after the widget's; nothing
  else of it changes.
- **The root `.npmrc`**, new (Open Questions 3), one setting and its comment:

  ```
  # Each member's direct dependencies install in its own node_modules
  # (change join-movie): the movie's tool reads its packages there, and its
  # esbuild, TypeScript, vitest and jsdom differ in major from the widget's.
  install-strategy=shallow
  ```

- **The root lock** is regenerated by `npm install --no-audit --no-fund` at
  the root from the viewer's lock (probe 7: every one of the viewer's 176
  resolutions kept, the movie's in `J/node_modules`), and `npm ci` reproduces
  it. The root `.gitignore`'s `/node_modules/` and the package's
  `node_modules/` cover both directories.
- **The member's own lock**, `J/package-lock.json`, stays tracked (Open
  Questions 4): it is what `setup` installs from where no workspace exists.
  npm ignores it inside the workspace. A test (Decision 8) holds both locks to
  `J/package.json`: the member lock's root entry and the root lock's entry
  for `J` list exactly the manifest's dependencies and development
  dependencies with their versions, and each lock resolves every direct
  dependency to the manifest's exact version. The release pass regenerates it
  as Decision 3 says.
- **Playwright** is 1.63.0, the version of the Python Playwright the viewer's
  `web-snapshot` extra locks (Open Questions 5): one Chromium, build 1243,
  serves the viewer's capture and the movie's render.

### 7. The pins, the uv workspace and the bench venv

- The core's `pyproject.toml` gains, after the `mechanics` extra:

  ```toml
  # The films, `machinome.movie` and the command `machinome movie`, the
  # repository's distribution machinome-movie, numbered with the set; its
  # Node side is installed by `machinome movie setup`.
  movie = [
      "machinome-movie~=0.8.1",
  ]
  ```

  `all` stays the kernels' and `dev` does not name it, as for the skills.
- The root's sources gain `machinome-movie = { workspace = true }` after
  `machinome-mechanics`; the dev group gains `"machinome[movie]"`, its comment
  naming the movie package, whose tests run from its directory and whose
  command the suite's conformance walk reads.
- `uv lock`: the member and four packages more than the line's lock (probe
  13: 192 to 197 on the viewer's line); `uv sync --python 3.12`: one
  `__editable__` `.pth` file more, naming `D`. Then from `/tmp`: `machinome
  movie -h` lists the eleven verbs; `python -c "import machinome.movie"` names
  `P/__init__.py`; `import machinome_movie` raises `ModuleNotFoundError`.
- The bench's `npm ci` runs at the root, never through a link to another
  checkout's `node_modules`, which `npm ci` would write through (the guard of
  Decision 5 refuses one in `setup`).

### 8. The core

- **The layout gate**, `tests/test_repository_layout.py`. `PRODUCTS` gains:

  ```python
      'machinome-movie': ('machinome.movie', 'movie',
                          ('.gitignore', 'CHANGELOG.md', 'LICENSE',
                           'LICENSES', 'MANIFEST.in', 'README.md',
                           'experiments', 'machinome', 'openspec',
                           'pyproject.toml', 'tests', 'workflow')),
  ```

  `NODE_MEMBERS` becomes a mapping of each member's directory to its package
  name (`@machinome/viewer`, `@machinome/movie`), the root `package.json`'s
  `workspaces` its keys in order. `TheNodeWorkspaceTest`: the tracked locks are
  the root's and the members' of `OWN_LOCKS = ('packages/machinome-movie/machinome/movie/js',)`;
  the root lock names each member by its name; a new
  `test_the_movie_s_own_lock_agrees_with_its_manifest_and_the_root_s`
  (Decision 6); a new `test_the_root_installs_each_member_s_dependencies_beside_it`
  (`.npmrc` holds `install-strategy=shallow`). `TheRootIsTheRepositorysTest`
  lists `.npmrc`. `TheContinuousIntegrationTest` gains the movie's steps
  (Decision 10). The default group's test expects the movie's extra. The
  module's docstring names the movie and the change. Red at the join (probe
  3) and until the package exists: the workspace source, the README, the
  table, the guide, then the product's entries, manifest, README, resolution,
  the members, the locks, the CI steps.
- **The release records**, `tests/test_release_records.py`: the member is
  numbered with the core and its pins `~=` (already its rules); a new
  `test_the_movie_s_node_version_files_agree`: `J/package.json`'s version,
  `J/package-lock.json`'s two root entries and the root lock's entry for `J`
  equal the set's version, and `.bumpversion.cfg` names `J/package.json`.
- **`.bumpversion.cfg`** gains, after the viewer's tables:
  `[bumpversion:file(version):packages/machinome-movie/pyproject.toml]`,
  `[bumpversion:file(pins):packages/machinome-movie/pyproject.toml]` (`~=`)
  and `[bumpversion:file:packages/machinome-movie/machinome/movie/js/package.json]`
  (`"version": "{current_version}"`). No table for a lock: the release pass
  runs `npm install --package-lock-only` at the root and in a scratch copy of
  `J` (the viewer's probe 15). The applier proves the bump on a copy.
- **`tests/test_kernel_extras.py`**: `EXTRAS` gains `'movie':
  {f'machinome-movie~={VERSION}'}`, its comment naming the change.
  **`tests/test_machinome_identity.py`**: the extras' loop gains `('movie',
  'machinome-movie')`. Red: `KeyError: 'movie'`.
- **The split-word gate**, `tests/test_core_names_no_split_words.py`:
  `ORDINARY` gains `'machinome/movie/names.py'`, `'machinome/movie/document.py'`
  and `'machinome/movie/take.py'`, each `{'ex' 'act_seconds'}`: the seconds a
  take's written durations sum to exactly (the product's ADR-016), the
  ordinary adjective, not the engines' split. The function keeps its name.
- **The vet universe**, `machinome/vet/universe.toml`: `[contract] deny`
  gains `"machinome.movie"` after `"machinome.viewer.web"`, with a comment
  naming the change (Open Questions 13). A model that reaches it is
  `framework-internal`; a project's movie declarations are not read by vet
  (probe 15). `tests/test_vet_universe.py`: `test_the_contract`'s tuple, and a
  new `test_the_movie_is_internal_and_its_former_name_outside` (two scratch
  projects, as the viewer's test). Red: the first import passes.
- **`docs/conf.py`**: no new fact; the movie is numbered with `|release|`.

### 9. The seam's tests

The suite's environment installs the package (the dev group), so the seam's
fakes named `movie` collide with it (probe 12). In
`tests/contributed_commands.py`, `fake-movie` becomes `fake-film`, its entry
`film = machinome_fake_film:Film`, its docstring "Make films of machines (a
fake contributed command).", its verbs and output unchanged (`film <verb>
<source>`); `fake-movie-two` becomes `fake-film-two`, `film =
machinome_fake_film_two:Film`. No fake takes the name of a package of the set.
In `tests/test_cli_contributed.py` the invocations and expectations follow
(`film build film.yaml`, `film list build`, the collision of two packages on
`film`); the choices the help and the gone module's test expect are those
`join-skills` computes from the suite's own contributors, which now include
`movie`. In `tests/test_cli_lazy_imports.py`,
`test_the_contract_walk_reads_a_fake_distribution` compares the fakes'
distributions alone, as `join-skills` makes it. Red: probe 12's failures once
the sync installs the package, `skills` and `fake-lessons` already landed.

`test_every_contributed_entry_resolves_and_honours_the_contract` then walks
the entry `movie` of `machinome-movie` beside `skills`: the name is not a
framework command's, no other distribution declares it, the class imports and
constructs, carries a docstring, `add_arguments` and `handle`, and declares
`needs_node` a boolean. It proves the shipped class meets the contract from
the source tree, not the verbs (the package's tests) nor the wheel's entry
point (`check-dist`). Its red is shown once by deleting `needs_node` from
`Movie`, one run, reverted.

### 10. CI

`.github/workflows/python-app.yml`, `test` job:

- The root step that builds and tests the widget names it
  (`--workspace packages/machinome-viewer/machinome/viewer/web/widget`)
  instead of `--workspaces`, so the movie's suite does not run there before
  Chromium; `npm ci` at the root installs both members.
- After the viewer package's step, two steps:

  ```yaml
      # The movie package keeps its tests in its own directory (change
      # `join-movie`): the Python tests, and the Node suite's projects that
      # open no browser, run no FFmpeg and write no film.
      - name: Run the movie package's tests
        working-directory: packages/machinome-movie
        run: python -m pytest

      - name: Run the movie package's Node tests
        working-directory: .
        run: npm test --workspace packages/machinome-movie/machinome/movie/js -- --project pure --project stage
  ```

  The two projects are 31 files and 329 tests, 7 s on this machine (probe
  8). The `slow` and `viewer` projects, which launch Chromium, run FFmpeg and
  pin pixels, run in the cycle's evidence and on a contributor's machine
  (Open Questions 10).

`dist` already sets up Node (the viewer's). Lint reads `../machinome-*/machinome`,
the movie's twelve modules and `cli.py` among them; it is `continue-on-error`.

### 11. `scripts/check-dist`: one row, installed from its wheel

The row, after the viewer's, installed by path as the products' are (no
`through`): no index serves `machinome-movie`. The script's start refuses, as
for the viewer, when the movie is a member and `npm` or `node` is not on the
PATH. The smoke (Open Questions 8):

```python
    'machinome-movie': {
        # Installed from its wheel by path; the smoke reads the extra's
        # requirement from the core's metadata, installs the Node side as a
        # user does, and removes it.
        'extras': [],
        'code': '''
import importlib.metadata as metadata
import subprocess
from pathlib import Path
import machinome.movie as movie
distribution = metadata.distribution('machinome-movie')
version = metadata.version('machinome')
assert distribution.version == version, (distribution.version, version)
files = [str(path) for path in distribution.files]
shipped = sorted(path for path in files if path.startswith('machinome/'))
assert 'machinome/movie/cli.py' in shipped, shipped
assert 'machinome/movie/machinome-movie-0.2.json' in shipped, shipped
assert 'machinome/movie/js/bin/videomaker.mjs' in shipped, shipped
assert 'machinome/movie/js/package-lock.json' in shipped, shipped
assert not [path for path in shipped
            if '/js/test/' in path or '/js/fixtures/' in path
            or '/js/scripts/' in path or '.test.' in path
            or 'node_modules' in path], shipped
js = Path(movie.__file__).resolve().parent / 'js'
assert js.is_relative_to(Path(VENV).resolve()), js
assert f'machinome~={version}' in distribution.requires, distribution.requires
assert f'machinome-viewer~={version}' in distribution.requires, distribution.requires
core = metadata.requires('machinome')
assert any(line.startswith(f'machinome-movie~={version}')
           and 'movie' in line.partition(';')[2] for line in core), core
(entry,) = [entry for entry in metadata.entry_points(group='machinome.commands')
            if entry.name == 'movie']
assert entry.value == 'machinome.movie.cli:Movie', entry.value
command = str(Path(VENV) / 'bin' / 'machinome')
def run(*args):
    return subprocess.run([command, 'movie', *args], capture_output=True,
                          text=True)
before = run('review', 'missing.json')
assert before.returncode == 1 and 'machinome movie setup' in before.stderr, before
setup = run('setup')
assert setup.returncode == 0, setup.stdout + setup.stderr
assert (js / 'node_modules' / 'esbuild' / 'package.json').is_file(), js
after = run('review', 'missing.json')
assert after.returncode == 1 and 'missing.json' in after.stderr, after
removed = run('setup', '--remove')
assert removed.returncode == 0 and not (js / 'node_modules').exists(), removed
'''
        + LICENCES.substitute(name='machinome-movie')
        + '''
print('machinome-movie', distribution.version, 'module', movie.__file__,
      'Node side installed and removed')
''',
        'commands': [['machinome', 'movie', '-h']],
    },
```

The `review` of a missing manifest after `setup` proves Node loads the
command's whole module graph from the installed dependencies (every import of
`bin/videomaker.mjs` is static) and answers; before `setup`, the refusal's
line. A film is not rendered: no project, export or viewer page is at hand
in the throwaway environment. Red first: before the row, the script fails
"machinome-movie has no smoke in scripts/check-dist".

### 12. The manual

By reader intent, under the workspace's `skills/write-the-manual/SKILL.md`:

| page | section | from |
|---|---|---|
| `howto/film-a-movie.rst`, "Film a movie of your machine" | How-to guides, after the viewer's | the README: setup, the workflow, timing and revisions |
| `howto/declare-a-movie.rst`, "Declare a movie" | after the above | `declaring-a-movie.md` |
| `howto/draw-a-movie-stage.rst`, "Draw a movie's stage" | after the above | `stage.md` |
| `reference/movie/index.rst`, "Movies" | Reference, after `reference/viewer/index` | new: the package, its version, its three pages |
| `reference/movie/command.rst`, "The movie command" | the section's first | the README's verbs, what each checks, proves and prints, and its outputs |
| `reference/movie/document.rst`, "The movie document" | the section | `movie-document.md` |
| `reference/movie/episode.rst`, "The episode format" | the section | `FORMAT.md` |

- **Converted in place**: the four pages the join lands are Markdown at the
  join and reStructuredText after it, their substance kept, their links
  `:doc:` links; `reference/movie/command.rst` and the section's index are
  written new from the README's sections. The how-to opens by installing
  (`pip install "machinome[movie]"`, `machinome movie setup`, the Chromium
  line it prints, FFmpeg from the system, `ELEVENLABS_API_KEY` in the
  environment or the `.env` of the directory the command runs from, kept out
  of the repository) and runs one film both ways, `machinome movie check
  <project> <movie>` and an episode's `machinome movie check
  videos/<episode>/episode.yaml`; every `node bin/videomaker.mjs` and `python
  -m machinome_movie` becomes `machinome movie`, every `--viewer` goes, and
  "Requires ... a Machinome Viewer API 21 bundle" becomes the installed
  viewer and the API its films need.
- **What leaves the pages**: the README's statements of the tool's licence
  and of the Leonardo sources' licence, of "no remote is configured", of the
  repository's own tests and OpenSpec records (the contributor guide's and
  the product's), and its links to `docs/first-rehearsal.md` (a record, linked
  from nowhere a reader is sent). The pages name no project or checkout path
  (the product's own test of that rule moves with it, Decision 13).
- **`reference/cli.rst`**: in "Commands from other packages", the closing
  sentence becomes "The movie package adds ``machinome movie`` and the skills
  package ``machinome skills``, below; the studio (``machinome studio``) is to
  add its own."; then a section `machinome movie` (anchor `.. _movie-command:`)
  with the synopsis of the eleven verbs and their options, the three forms of a
  source, the Node and viewer it uses, the exit statuses, and a link to
  :doc:`/reference/movie/command`.
- **`start/install.rst`**: the extras paragraph gains ``movie`` (the
  distribution ``machinome-movie``, the films of a machine), with the second
  step ``machinome movie setup`` and Node 22, FFmpeg and Chromium as the
  documented steps; "Packages and licences" names ``machinome-movie`` among
  the packages of the set, under the same licence.
- **`index.rst`**: the three how-tos and `reference/movie/index` in their
  toctrees.
- **The build**: `sphinx -b html -n -W --keep-going` with
  `docs/requirements.txt` alone, exit 0; the new pages looked at.
- **The pages' pins**: `test_docs_structure.py` gains the toctree entries, the
  install page's distribution and its two lines, the CLI section's verbs, and
  no page saying the videomaker is "to add" its command; the product's
  `tests/test_repository.py` and `J/test/repository.test.mjs` read the facts
  they held at the pages' new paths (Decision 13).

### 13. The tests at their new place

- **Python** (`D/tests/`, `python -m pytest` from `D`, collected by no core
  run): `machinome_movie` becomes `machinome.movie` in the tests and in the
  fixture project's five movie modules; `conftest.py`'s `REPOSITORY` becomes
  `PYTHON / 'machinome' / 'movie' / 'js'` (`FIXTURES` and `SCHEMA` follow);
  `test_take.py`'s one path to `fixtures/documents` moves; the fixture project
  is re-pinned (`J/scripts/pin-fixture-project.mjs`, then
  `J/scripts/pin-resolved.mjs minimal tour count`, the pins reviewed, probe 5);
  `test_repository.py`'s nine pinning tests read the manual's pages
  (`packages/machinome/docs/howto/declare-a-movie.rst` and the others), the
  package's `README.md` and `CHANGELOG.md` at their new paths and keep their
  facts. Expected: 298 passed (probe 4).
- **Node** (`J/test/`, `npm test --workspace packages/machinome-movie/machinome/movie/js`
  from the root, or `npm test` in `J`): the fourteen path lines of nine files of probe 8
  (`<scratch>/probe_js_patch.py`, its `stage-build.mjs` part excepted) name
  the Python fixture project as `../../../tests/fixtures/project` from `J` and
  the Python package as `J/..`; `test/support/reach.mjs`'s `FIXTURE_PROJECT`
  follows; the 77 fixture documents' roots become
  `../../../../../tests/fixtures/project/videos/<movie>`;
  `test/repository.test.mjs`'s twelve pinning tests read the manual's pages
  (the command's options in `reference/movie/command.rst`, where the README
  held them) and the package's changelog; their assertions on `AGENTS.md`
  (its status line and its list of the test layers) go with that file, an
  agent prompt the framework does not keep (Open Questions 9), and those on
  the layers stay held by `vitest.config.mjs`'s own tests; the four comments
  that cite `AGENTS.md` (`vitest.config.mjs`, `test/support/memo.mjs`,
  `test/support/reach.mjs`, `test/memo.test.mjs`) cite the product's
  ADR-003; the words of Decision 4. The test memo stays inside the
  repository's common Git directory (`videomaker-test-memo/`), outside every
  work tree. Expected: probe 8's result with the pinning tests green.
- **The core's suite** collects neither (the viewer's and the mechanics'
  rule).

### 14. The records

- **`HISTORY.rst`**, at the end of `Unreleased`:

  ```
  * **The videomaker joins the repository, as MACHINOME MOVIE.** The
    videomaker, kept in a repository of its own since 19 September 2026, is
    the package ``machinome-movie`` at ``packages/machinome-movie/``, its
    history kept and its two finished branches beside the line: its Python
    package is ``machinome.movie`` (formerly ``machinome_movie``, which
    nothing provides any more), its Node side lives inside it, and ``pip
    install "machinome[movie]"`` then ``machinome movie setup`` install it.
    Its command, ``machinome movie``, the first a package adds to
    ``machinome``, lists, evaluates and watches a project's movies, and
    checks, voices, previews, renders, builds, serves and reviews a film from
    an episode, a movie document or a project and a movie name, with the
    installed viewer and the user's Node 22. It is numbered with the set,
    licensed as every package of the repository, the second member of the npm
    workspace, and keeps its changelog, specs, decision log and tests in its
    directory; its documents are part of this manual. Change ``join-movie``
    (ADR-191).
  ```

- **`docs/project/changelog.rst`**, at the end of `Unreleased`:

  ```
  * **Film a movie of your machine.** ``pip install "machinome[movie]"`` and
    ``machinome movie setup`` install the films; ``machinome movie check``,
    ``speech``, ``preview``, ``render`` and ``build`` make one from a YAML
    episode, a movie document or a project and a movie name, drawn by the
    installed viewer (:doc:`/howto/film-a-movie`, :ref:`movie-command`). A
    movie is declared with ``machinome.movie`` (formerly ``machinome_movie``).
  ```

- **The product's `CHANGELOG.md`**: its first line's sentence ("Videomaker is
  private and unversioned; ...") becomes "Machinome Movie is numbered with
  Machinome; entries accumulate under `Unreleased` until the set is
  released."; its `Unreleased` section gains, first:

  ```
  - Videomaker is part of the Machinome repository,
    <https://github.com/machinome/machinome>, at `packages/machinome-movie/`,
    with its history, as the distribution `machinome-movie`, numbered with
    Machinome. Its Python package is `machinome.movie` (formerly
    `machinome_movie`), a portion of the `machinome` package; its Node side is
    inside it, at `machinome/movie/js/`. `machinome movie` runs every verb of
    both former command lines, `python -m machinome_movie list|evaluate|watch`
    and `node bin/videomaker.mjs check|speech|preview|render|build|live|review`,
    takes a project and a movie name where those took a document, films with
    the installed viewer instead of `--viewer`, and installs its Node
    dependencies with `machinome movie setup`. It is licensed as every package
    of the repository, GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, at the
    recipient's choice. Playwright is 1.63.0, the viewer's. Its manual is part
    of Machinome's, <https://machinome.readthedocs.io>.
  ```

- **`CREDITS.md`** (the framework's): a section "### Installed by `machinome
  movie setup`, and drawn into every film" (Open Questions 18): the films'
  Node side runs on packages `machinome movie setup` installs from npm under
  their own licences, esbuild 0.28.2 (MIT), highlight.js 11.12.0
  (BSD-3-Clause), Playwright 1.63.0 (Apache-2.0), React and React DOM 19.3.0
  (MIT), TypeScript 7.0.2 (Apache-2.0), yaml 2.8.1 (ISC), the React types
  (MIT); the stage page a render writes bundles React and React DOM.
  Narration is generated by the ElevenLabs service with the user's key; FFmpeg
  is the system's. The file's last-updated line 2026-10-12.
- **`docs/architecture.md`**: in "CLI", after the contributed commands'
  paragraph, "The first is `machinome movie`, from the repository's
  distribution `machinome-movie` (ADR-191)."; a section "Movies (the
  distribution `machinome-movie` · spec `movie-distribution`)", the substance
  of the product's architecture overview: the Python declarations evaluated
  once to the movie document; the Node pipeline (load and resolve, speech,
  the stage bundle, the frames through the viewer in Chromium, the encode, the
  review pack, the live session and the player); the command that joins them,
  its Node and its viewer; its own decision log and record in its directory.
  The Map gains "Movies, the distribution `machinome-movie`" |
  "`packages/machinome-movie/` (`machinome/movie/`: the declarations, the
  evaluation, `cli.py`, `js/`; its own `tests/`, `openspec/`, `workflow/`)" |
  `movie-distribution` | "189, 191"; the extras sentence gains "`[movie]`
  for the films".
- **The root `README.md`**: a row after the viewer's:
  ``| [`machinome-movie`](packages/machinome-movie/) | The films, `machinome.movie` and the command `machinome movie`: a narrated film of a machine declared in Python or written as an episode, checked, voiced, previewed, rendered and served through the browser viewer; installed by `machinome[movie]`. |``
- **`CONTRIBUTING.rst`**: the pip block gains `-e packages/machinome-movie \`;
  "Running tests" gains "The movie package keeps its tests in its own
  directory: run ``python -m pytest`` from ``packages/machinome-movie``, and
  its Node suite with ``npm test --workspace
  packages/machinome-movie/machinome/movie/js`` from the root, after ``npm
  ci`` there; the browser and pipeline tests need Chromium and FFmpeg." The
  Node paragraph of `join-viewer` names both members and the root `.npmrc`.
- **`context7.json`**: `excludeFolders` gains `D/openspec`, `D/tests`,
  `D/workflow`, `D/experiments`, `J/test` and `J/fixtures`; `rules` gains one:
  "A film of a machine is made with pip install \"machinome[movie]\", then
  machinome movie setup (Node 22 or newer, the user's; FFmpeg and Playwright's
  Chromium are separate steps). Declare a movie in Python with
  machinome.movie (Movie, Chapter, Shot, Narration, Take and the stage's Set,
  Slot and Element) and list it in the project's pyproject.toml; machinome
  movie check|speech|preview|render|build|live takes an episode.yaml, a
  movie.json or a project directory and a movie name; the browser viewer
  installed beside it draws every frame."
- **`AI-USE.md`**: the paragraph on what is agent-written gains "and the
  films under `packages/machinome-movie/`, founded in a repository of their
  own after the line and joined here with their history".
- **ADR-191** (recommended, Open Questions 1),
  `docs/adrs/BUILD/ADR-191-the-videomaker-is-a-product-of-the-set-its-node-side-installed-by-its-command.md`,
  "The videomaker is a product of the set, its Node side inside its portion
  and installed by its command", Status Proposed, Change `join-movie`. Amends
  ADR-182 (the root's npm workspace installs each member's direct
  dependencies beside it) and ADR-188 (the workspace's second member, its own
  lock); Related to ADR-187 (the products), ADR-189 (its first contributor)
  and ADR-190. Context: the pilot's decisions; probes 6 to 11 and 14.
  Options: (1) one member at `machinome.movie`, its Node side as package
  data, installed by `machinome movie setup` from a lock of its own into the
  installed package's directory, the repository's checkout installed by the
  root's `npm ci` with each member's direct dependencies beside it (chosen);
  (2) the Node side a separate npm package (refused by the pilot: pip only);
  (3) the dependencies installed into a cache outside the package (refused by
  the pilot); (4) npm's default layout and the tool reading its packages
  through Node's lookup (refused by probe 6: three tests and the bundle's names
  rewritten for an install detail); (5) the dependencies vendored into the
  wheel (refused: 81 MB of other people's platform binaries per platform). The
  decision outcome states Decisions 3 to 7 and 11. Consequences: good, one
  install line and one command, the films numbered and licensed with the set,
  one Chromium; bad, Node and npm become the user's prerequisites for the film
  verbs, an uninstall leaves `J/node_modules` unless `setup --remove` ran
  (probe 11), the workspace's layout now depends on `.npmrc`, CI runs the
  browser and pipeline tests of the Node suite nowhere yet; neutral, the core
  imports nothing of the package. Index line under BUILD after ADR-190's.
  ADR-182 and ADR-188 gain the dated consequence "Neutral (2026-10-12,
  `join-movie`): ..." and "amended by 191".
- **The plan's progress** (`workflow/ongoing/release-0.9.md`): the cycle's
  entry at its close.

### 15. The product's record, brought current in place

With no change of behaviour:

- `D/openspec/config.yaml`: its context says the tool is the repository's
  distribution `machinome-movie` at `packages/machinome-movie/`, its Python
  package `machinome.movie` with its Node side at `machinome/movie/js/`, its
  command `machinome movie`, under the repository's licence, its specs and
  changes here, the framework's specs the framework's.
- `D/openspec/specs/*`: `Code:` lines and paths (`python/machinome_movie/` to
  `machinome/movie/`, `bin/videomaker.mjs` to `machinome/movie/js/bin/videomaker.mjs`)
  and the command lines of their scenarios that name `node bin/videomaker.mjs`
  or `python -m machinome_movie` as a user's command become `machinome movie`;
  titles kept. `env -C D openspec validate --specs --strict` passes.
- `D/workflow/README.md`: the maintainer notes in force (where the specs,
  the decision log and the notes are, how the tests run); its other notes are
  records of their day.
- `D/workflow/adrs/README.md`: a dated note, "(12 October 2026, change
  `join-movie`) The videomaker joined the machinome repository at
  `packages/machinome-movie/`; this log stays its own, beside the framework's
  `packages/machinome/docs/adrs/`. A number cited in the package's code,
  specs and records names this log's ADR; the framework's are cited as
  'framework ADR-nnn'." The records are untouched.
- `D/workflow/architecture-overview.md`: a dated note at its top saying the
  framework's `docs/architecture.md`, section "Movies", is the current
  statement from 12 October 2026, and this file the product's record.

### 16. The branches, the projects and the originating check

- **The branches** are the orchestrator's git step at the join (Decision
  2). Resuming one later is a merge of the line onto it; its Markdown how-to
  (`howto/listen-to-a-movie.rst`) and its paths follow the mapping.
- **The projects' move**, the orchestrator's, after the implementation, each
  repository under its own process, by a script like the mechanics cycle's
  (`<scratch>/../C2-move/move.py`):
  - in the 21 Python modules of probe 16, `from machinome_movie import`
    becomes `from machinome.movie import` and `machinome_movie.` in a
    docstring or comment `machinome.movie.`;
  - in each film's README that shows how it is made (Leonardo's
    `machinome-release-1` to `-5`, `-4-pt-br`, `study-1-pt-br`,
    `machinome-revolutions-v2` and `videos/README.md`; kossel's two; the
    Curta's; Metamaquina2's; lumiere's `short-ptbr-flow-v3`), `python -m
    machinome_movie evaluate <project> <movie>` followed by `node
    bin/videomaker.mjs <verb> <document> --viewer <bundle>` becomes `machinome
    movie <verb> <project> <movie>`, a lone `node bin/videomaker.mjs <verb>
    <source> --viewer <bundle>` becomes `machinome movie <verb> <source>`, and
    a sentence on the checkout, the Python path or the bundle goes;
  - left as they are: the 13 stage modules (`videomaker/stage` is the stage's
    specifier, unchanged); the 11 scripts that reach the original checkout by
    path, which stays where it is (listed for the workspace's consistency
    cycle); the records of a day (`VERIFICATION.md`, `HANDOFF.md`,
    `VOICE-DESIGN.md`, `NARRATION.md`, `review-notes.md`);
  - the commit message "Import the films from machinome.movie and run them
    with machinome movie", its body naming the change and the date.
- **The originating check**, on the bench after the Curta's move: `machinome
  movie check` and `machinome movie preview` from the bench's venv on
  `Calculators/Curta-Type-I-3x` and its movie `addition`, the bench's viewer
  0.8.1 (API 29) found through the entry point, the narration takes the
  project has cached; the storyboard `preview` writes is looked at as the
  pixels. A take that is missing makes `check` say so, which is a finding to
  record, not to work around.

### 17. Workspace follow-ups, outside this repository

Listed for the orchestrator; none is done by this cycle: the operating
contract's paragraph on the videomaker and its layout block; the
`videomaker` skill, rewritten for `machinome movie`; `docs/collaborator-setup.md`
and `scripts/setup`, which clone the product; the 11 project scripts of
probe 16; the speech key the pilot keeps in the original checkout's `.env`,
which `machinome movie speech` reads from the environment or the `.env` of the
directory it runs from (Decision 4); the original repository on GitHub, the
pilot's.

### 18. The spec deltas

The line's `framework-identity` requirement "Extras select independent
Machinome products" is modified by `join-viewer` (archived on its bench) and
by `join-skills` (planned); this change's MODIFIED copy is composed from the
viewer's archived text with the skills' sentence and scenario, then the
movie's. Every other change is an ADDED requirement, so no other requirement
is copied from a baseline that two other cycles move. The applier confirms,
at the bench's head before the archive, that the MODIFIED requirement equals
the baseline there plus the movie's sentence and scenario, and re-derives it
if the baseline moved (tasks 1.3 and 15.2).

- `movie-distribution`: new, five requirements (what ships; Node; setup;
  sources and verbs; the viewer).
- `cli`: ADDED "Movie command".
- `cli-startup-cost`: ADDED "The movie command loads none of the movie's
  evaluation to be listed".
- `framework-identity`: MODIFIED "Extras select independent Machinome
  products" (the `movie` extra; one scenario added, titles kept); ADDED "The
  films are a product of the set and a member of the npm workspace".
- `user-documentation`: ADDED "Filming a machine is documented in the
  manual".
- `framework-contributor-guidance`: ADDED "The contributor guide says how the
  movie package's tests run".
- `vet`: ADDED "A model that reaches the movie package is refused".

## Risks / Trade-offs

- [Node and npm become prerequisites] → Only of the film verbs; `list`,
  `evaluate` and `watch` are Python; every refusal names the line to run.
- [`pip uninstall` leaves `J/node_modules`, 81 MB] → pip removes what its
  record lists; the how-to says to run `machinome movie setup --remove`
  first, and `setup` writes nothing outside `J`.
- [`setup` needs the npm registry] → It is the documented second step, as
  `playwright install` is; `check-dist` proves it from npm's cache or the
  network.
- [The root's layout depends on `.npmrc`] → `TheNodeWorkspaceTest` holds the
  line; `npm ci` reproduces the lock's layout; the viewer's resolutions are
  unchanged (probe 7).
- [Two locks for the movie's packages] → One for the checkout, one for an
  installed copy; a test holds both to the manifest's exact versions; their
  transitive resolutions may differ by patch releases, each a lock npm
  resolved.
- [The Node suite's browser and pipeline tests run nowhere in CI] → They run
  in the cycle's evidence and on a contributor's machine; Open Questions 10
  asks the pilot.
- [setuptools warns twenty times at each build] → The data is carried; the
  smoke holds the wheel's files; the pilot's decision names `js/`.
- [The fixture project's re-pin re-exports its two models with the bench's
  framework] → Probe 5 found their models byte for byte as before; the pins are
  reviewed before the commit.
- [Eleven project scripts keep the original checkout's path] → It stays at its
  path; they are the workspace's to move.
- [Composed deltas] → Decision 18; the applier re-derives at the head.
- [The tool keeps its former name inside] → `bin/videomaker.mjs`, the stage's
  `videomaker/stage`, the memo `videomaker-test-memo/`, the bundle names
  `videomaker/...`: internal names a user never types; Open Questions 12.
- [The joined records keep their words] → Archived changes, notes and ADRs are
  historical, as in the earlier joins; every file this change writes states
  the set's licence and the new names.

## Migration Plan

In the order of tasks.md: the baseline; the join, by the orchestrator, and its
reds; the red tests; the package and its source; the npm workspace; the core,
the uv workspace and the sync; the seam's tests; the tests at their new
place; the manual; the version records, `check-dist` and CI; the records;
validation; the projects' move and the originating check, by the
orchestrator; the archive. Rollback is a revert of the implementation commit
and of the merge commit, `uv lock`, `uv sync`, `npm ci` at the root, and a
revert of each project's move commit; the two fetched branches are deleted.

## Open Questions

1. **The ADR.** ADR-191, or amendments of ADR-182, ADR-188 and ADR-189 only.
   Recommendation: ADR-191: the join makes choices no record holds, a
   product whose second runtime is the user's, installed by its own command
   into the installed package, from a lock of its own, and a workspace that
   installs each member's dependencies beside it. If declined, the HISTORY
   bullet ends "(ADR-182 and ADR-188 amended)".
2. **The Node tests' and fixtures' place.** Inside `js/` beside the sources
   they import by `../src/` (Decision 2), excluded from the wheel; or beside
   `tests/` at `D/test/` and `D/fixtures/`. Recommendation: inside `js/`:
   every test imports the sources by a relative path, which stays as it was,
   and the runner, the memo and the configuration take `js/` as their root;
   at `D/` every import of 52 test files would move.
3. **The npm layout.** A root `.npmrc` with `install-strategy=shallow`
   (Decision 6), or npm's default layout with the tool reading its packages
   through Node's lookup. Recommendation: `.npmrc`. It adds one file to the arrangement
   `join-viewer` founded, which the orchestrator's outline of this change kept
   unchanged but for the second member: the viewer's 176 resolutions stay, the tool's assumption holds unchanged in the checkout
   and in an installed copy alike, and the default layout splits the movie's
   packages over two directories, which probe 6 showed breaks the stage build
   and three tests short of rewriting them and the bundle's names. If declined,
   `stage-build.mjs` resolves its packages as `<scratch>/probe_js_patch.py`
   does, the bundle names every `node_modules` on the lookup path, and the
   three tests build a second checkout's packages from the lookup.
4. **The member's tracked lock.** Kept at `J/package-lock.json`, held to the
   manifest with the root's by a test; or none, `setup` resolving from the
   registry. Recommendation: kept; without a lock `npm ci` refuses, and `npm
   install` would resolve at the user's day; with it an installed copy gets
   the direct dependencies the repository tests, at the manifest's exact
   versions, and the transitive ones its own lock fixed (which may differ from
   the root lock's by patch releases).
5. **Playwright.** The viewer's 1.63.0 for both; or the movie's 1.62.0 kept.
   Recommendation: 1.63.0: one Chromium build (1243) for the capture and the
   render; probe 8 ran the suite on it.
6. **The ADRs' place.** `D/workflow/adrs/`, a log of its own as the viewer's
   is; or `D/docs/adrs/` as the product had it. Recommendation:
   `workflow/adrs/`: `D` keeps no `docs/` (the manual is the framework's),
   and the viewer set the precedent.
7. **The `review` verb's source.** A rendered film's manifest, as the Node
   command takes it; or a project and a movie name, finding its manifest.
   Recommendation: as the Node command has it; the manifest is the render's
   output, which the render prints.
8. **The smoke's depth.** `setup`, a Node verb and `setup --remove` from the
   wheel (Decision 11, network or npm's cache); or the files and `-h` alone.
   Recommendation: the depth of Decision 11: the installed case, `npm ci`
   from the member's lock outside the workspace, is the one place it runs
   before a user does.
9. **`AGENTS.md`, `.env.example` and `python/README.md`.** Dropped, dropped,
   and kept as the package's README. Recommendation: as Decision 2. `AGENTS.md`
   is an agent prompt, which the framework does not own; its testing policy
   is ADR-003 of the product's log, which stays; `.env.example` holds one
   line the how-to states.
10. **The Node suite in CI.** The `pure` and `stage` projects (Decision 10);
    or the whole suite with FFmpeg and Chromium on CI's image. Recommendation:
    the two; the `slow` and `viewer` projects pin pixels, fonts and
    toolchain versions measured on this machine, have never run on a CI image,
    and run here in the cycle's evidence. Running them in CI is a later step
    with its own probe, the pilot's to order.
11. **A lazy package root.** `machinome.movie`'s root reads each name from its
    module on first use; or it stays eager. Recommendation: lazy: with it
    `machinome -h` costs 19 ms more than without the package, and `machinome
    movie -h` 72 ms; eager, 63 ms and 126 ms (probe 14); the names and their
    behaviour are unchanged, and `cli-startup-cost` gains the requirement that
    holds it.
12. **The internal names.** `bin/videomaker.mjs`, the stage's specifiers
    `videomaker/stage` and `videomaker/movie` (13 project modules import
    them), the bundle's names and the memo's directory kept; or renamed for the
    movie. Recommendation: kept in this change: none is a name a user types;
    renaming the specifiers changes the stage's contract, 13 project modules
    and the bundles' bytes (the product's ADR-013), a change of its own if the
    pilot wants it.
13. **The vet's denial.** `machinome.movie` denied to a model; or admitted as
    a module beneath `machinome`. Recommendation: denied, as `join-viewer`
    denied the viewer: before the join a model importing the movie was
    refused, and its command spawns Node and npm; vet does not read the movie
    declarations (probe 15), so no project's films are refused by it.
14. **`watch` and `live`.** Separate verbs, as the tools had them; or `live`
    with a project and a movie name also watching. Recommendation: separate:
    `watch` re-evaluates the document, which `live` reloads when it changes;
    the how-to runs them side by side.
15. **`MACHINOME_NODE` over the PATH.** The variable when set, the PATH
    otherwise; or the PATH first. Recommendation: the variable first: its use
    is to choose a Node 22 where an older one is on the PATH, which the
    reverse order could not do.
16. **The reference pages for the two formats.** `document.rst` and
    `episode.rst` in one section; or one page "The movie document" from both,
    as the orchestrator's outline reads. Recommendation: two pages: the JSON document and
    the YAML episode are two formats with two readers, a project's declarations
    and an episode's author, and one page would hold 1880 lines.
17. **The README's place.** The root README as the how-to's source, its
    history kept there, and the Python half's README as the package's; or the
    reverse, or `first-rehearsal.md` as the how-to's source as the orchestrator's
    outline's candidate reads. Recommendation: as Decision 2: `first-rehearsal.md` is a
    dated record of the first film's evidence, while the root README is what a
    user follows today.
18. **`CREDITS.md`.** A section naming what `setup` installs and what a film's
    page bundles; or unchanged, the wheel carrying no third-party code.
    Recommendation: the section: the packages are installed by the set's own
    command into the set's own package directory, and every film's page
    carries React and React DOM.
