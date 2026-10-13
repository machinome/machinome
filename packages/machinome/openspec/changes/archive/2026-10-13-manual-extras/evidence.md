# Evidence: `manual-extras`

The seventh cycle of the road in `workflow/ongoing/release-0.9.md` at the
repository root (its decision 9, the pilot, 12 October 2026). Worktree
`machinome/WTs/v0.9-joins-manual-extras`, branch
`v0.9-joins-manual-extras`, planning commit 70be3aab on the line's head
c5eeb038. Ratified by the orchestrator on 12 October 2026: Open Questions
1 to 6 and 8 to 10 as recommended, Open Question 7 overruled by task 5.9.
Applied on 12 October 2026, up to the checkpoint before the records
closing (group 7 is not done here).

Tools: uv 0.11.8, CPython 3.12.3 (the bench venv, synced from the lock,
`<join>/uv-sync-2.log` ending "exit 0"), Sphinx 9.1.0, docutils 0.22.4,
sphinx_rtd_theme 3.1.0 and packaging 26.3 in `.docs-venv/` (made by `make
docs` from `docs/requirements.txt` alone), Playwright's Chromium, OpenSCAD
2021.01, the OpenSpec CLI 1.6.0. `<bench>` is
`/home/asa/devel/machinome/machinome/WTs/v0.9-joins-manual-extras`,
`<scratch>`
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C10-apply/`.
The core's tests ran from `<bench>/packages/machinome` on the bench venv
(`python -m pytest -q tests/<module>.py -p no:cacheprovider`), one pytest
process at a time. Logs and pictures are in `<scratch>`, never in the bench.

## 1. Evidence baseline

### 1.1 The base, and the assumptions about the cycles before this one

```
$ git -C <bench> log --oneline -3
70be3aab Propose manual-extras: every manual page declares the extra it needs
c5eeb038 Implement viewer-command: the viewer's verbs are the framework's viewer command
4c68d02c Propose viewer-command: the viewer's verbs are the framework's viewer command
$ git -C <bench> status --short | wc -l
0
```

What held, of design.md's "Assumptions about the cycles before this one":

- `release-tooling` landed (ADR-192): the root `Makefile`'s `docs` target
  is `docs: bundle`, then `uv venv --python 3.12 .docs-venv` when absent,
  `uv pip install -r packages/machinome/docs/requirements.txt`, and `cd
  packages/machinome && .docs-venv/bin/python -m sphinx -b html -W -E docs
  docs/_build/html` (no `-n`; `conf.py` sets `nitpicky = True`). It is this
  cycle's manual build.
- `join-studio` landed (ADR-193) with the eight pages design.md names:
  `howto/open-a-studio-project`, `howto/studio-workspace`,
  `howto/studio-agents`, `reference/studio/index`, `command`,
  `project-configuration`, `profiles`, `troubleshooting`. The opening
  how-to's "What you need" names Git, OpenSCAD, the OpenSpec CLI and a
  logged-in agent backend, and its install the Chromium step: the `studio`
  row of design.md stands as written. Its installation-page paragraph and
  its assertions in `KernelExtrasTest` were there and fold in (2.4).
- `viewer-seam` landed (ADR-194): the flag is `--viewer`; `--renderer` is
  refused naming it (`reference/cli.rst`, `project/upgrading.rst`). It added
  the extra `viewer-openscad` (the distribution
  `machinome-viewer-openscad`), and `openscad` and `solid2` now install that
  distribution too. `machinome/viewer/__init__.py` declares `EXTRAS =
  {'openscad': 'viewer-openscad', 'web': 'viewer'}`: an absent OpenSCAD
  viewer is refused naming `viewer-openscad`.
- `viewer-command` landed (ADR-196, which took the number after 195): it
  added no page; `reference/viewer/cli.rst` and `reference/cli.rst` changed
  in place. ADR-195 is free and is this change's.

Adjustments made for them, each a departure from design.md's text:

1. **A row for `viewer-openscad`** in `docs/_ext/manual_extras.toml`,
   after `openscad` (the installation page's former table had it there):
   `for = "the OpenSCAD viewer of ``machinome snapshot`` alone, a still of
   a model of any parts"`, `outside = ["the OpenSCAD executable"]`. Without
   it the build and `test_the_table_is_the_manifest_s` fail, by design.
2. **The `openscad` row** reads "the OpenSCAD viewer of ``machinome
   snapshot``" where design.md wrote "renderer": since the seam it is a
   viewer, and the word renderer names the refused flag's concept.
3. **Chapter 10 declares `viewer-openscad`, not `openscad`.** Its default
   `machinome snapshot` lines take the OpenSCAD viewer, which the seam
   installs with `viewer-openscad` alone; with the chapters' other extras
   installed the line is refused naming `viewer-openscad` (6.5). The
   declaration is `viewer, cadquery, build123d, viewer-openscad,
   web-snapshot`; the page's line asks for the OpenSCAD executable as
   before. The orchestrator's resolution of Open Question 6 named
   `openscad`, written before the seam; task 1.1's re-check governs, and
   this is the extra the chapter needs as written.
4. **The derived rule reads `--viewer web`** (`--viewer[ =]web`) and not
   `--renderer web`, which is refused since the seam; no page's code shows
   it.
5. **The seam's installation-page test moves too.**
   `tests/test_viewer_documentation_links.py::test_the_installation_page_lists_the_openscad_viewer`
   read the page's source for `machinome[viewer-openscad]` and
   `machinome-viewer-openscad`; it is removed, a comment in its place
   saying the rendered list holds it, which
   `test_the_list_names_every_reader_extra_and_what_it_installs` does for
   every extra (2.4).
6. **The installation page's "Packages and licences"** had been rewritten
   by the seam and the studio into one sentence naming seventeen
   distributions; Decision 4's replacement sentence replaces that sentence,
   and the rest of the section (the seam's lines on the browser viewer and
   the `openscad` or `viewer-openscad` extra) is unchanged.

### 1.2 The manual's base build

```
$ env -C <bench> make docs          # <scratch>/base-make-docs.log
exit 0, 15.6 s (creating .docs-venv included), 97 HTML files
```

The only "warning" lines are uv's hardlink notice. Pages (`.rst` under
`docs/` but `releases/` and `_build/`): 85, the 77 of 462f7119 and the
studio's eight. The base HTML is kept at `<scratch>/base-html`.

### 1.3 The base runs

| Module | Base |
|---|---|
| `test_docs_structure.py` | 32 passed, 6460 subtests passed |
| `test_kernel_extras.py` | 19 passed, 80 subtests passed |
| `test_repository_layout.py` | 55 passed, 472 subtests passed |
| `test_sphinx_ext.py` | 14 passed |
| `test_viewer_documentation_links.py` | 16 passed |

## 2. Red first

### 2.1 `PageExtrasTest` (`<scratch>/red-2.1.log`)

`tests/test_docs_structure.py`, the class of Decision 5, its eight tests,
the module docstring naming `manual-extras`. Run alone: 8 failed.

- `test_every_page_declares_first_under_its_title`: "85 pages do not
  begin, under their title, with one `.. needs::` ...", each page listed.
- `test_a_declaration_names_extras_of_the_table`: `FileNotFoundError`, no
  `docs/_ext/manual_extras.toml`.
- `test_the_table_is_the_manifest_s`: `FileNotFoundError`, the same.
- `test_a_product_s_reference_section_declares_its_product`: the 29 pages
  of the four sections, each `None` (no declaration).
- `test_the_core_s_rules_and_records_declare_none`: the 21 pages, each
  `None`.
- `test_a_teaching_page_declares_what_its_code_needs`: 22 pages, each with
  the extras its code needs and the file that needs it (for example
  `tutorial/05-buttons.rst`: `build123d` and `cadquery` from
  `tutorial/counter/c04_relations.py`; `tutorial/10-share.rst`:
  `web-snapshot` from the page).
- `test_the_installation_page_derives_its_list`: install.rst has no
  section "The extras" under the label `extras`.
- `test_the_tutorial_s_install_line_names_its_chapters_extras`: `['cadquery',
  'viewer'] != []`, the union empty first (no chapter declares).

### 2.2 `tests/test_manual_extras.py` (`<scratch>/red-2.2.log`)

New, 15 tests at the red (a sixteenth added at 3.4 below). 13 tests and 6
subtests failed: each build `sphinx.errors.ExtensionError: Could not import
extension manual_extras (exception: No module named 'manual_extras')`
(18 times); the import test `FileNotFoundError`, no
`docs/_ext/manual_extras.py`. The table is read lazily, after the build, so
the red is the missing extension and not the missing table.

### 2.3 The guide (`<scratch>/red-2.3.log`)

`test_repository_layout.py::test_the_guide_says_a_page_declares_its_extras`:
1 failed, "CONTRIBUTING.rst does not say a manual page begins with
``.. needs::``".

### 2.4 The tests that read the installation page's source

`KernelExtrasTest` lost `EXTRAS`,
`test_the_installation_page_names_every_kernel_extra` and
`test_the_installation_page_names_the_extension_distributions` (which held
`join-studio`'s `machinome-studio`, `pip install "machinome[studio]"` and
`playwright install chromium`); its docstring says the rendered list holds
them since `manual-extras`. Their assertions are in `test_manual_extras.py`:
every reader extra, every distribution its requirements name with their
extras, each member of `all`; the movie's `machinome movie setup`, `Node
22`, `FFmpeg`, `Chromium`; the studio's `playwright install chromium`,
`OpenSpec`, `agent backend`; `web-snapshot`'s `machinome-viewer` with
`snapshot`.

```
$ git -C <bench> grep -n "install\.rst\|'start' / 'install\|start/install" -- 'packages/*/tests/*.py' 'packages/*/scripts/*' 'scripts/*'
```

found, besides `PageExtrasTest`: `test_viewer_documentation_links.py:25`,
a link from the page to `/howto/browser-viewer` (kept: the link stays in
"Packages and licences"), and `:126`, the seam's
`test_the_installation_page_lists_the_openscad_viewer` (moved, 1.1
adjustment 5). No product's test reads the page.

## 3. The extension and its table

- `docs/_ext/manual_extras.toml`: Decision 3 with 1.1's adjustments 1 and
  2; 19 rows, the manifest's 21 extras but `dev` and `docs`.
- `docs/_ext/manual_extras.py`: Decision 2. The manifest's path is made
  absolute at `config-inited` (reading `env.app` is deprecated in Sphinx 9);
  the line is parsed with `state.inline_text`. The outside-pip phrases of
  an extra that names other extras of the framework (`all`) are its
  members', in the table's order.
- `docs/_static/manual-extras.css`: Decision 2's box.
- `docs/conf.py`: `git diff` shows the `sys.path.insert(0,
  os.path.abspath('_ext'))` line with a one-line comment, `'manual_extras'`
  appended to `extensions`, `manual_extras_exempt = ['releases/*']` with a
  one-line comment, and nothing else (6 lines added, 1 changed).

3.4: `test_manual_extras.py` green, 15 passed, 41 subtests passed
(`<scratch>/green-3.4.log`). The first run found the smart quotes docutils
writes (`extra’s`); the test reads the doctree with them straightened.
Looking at the rendered list (6.3) found `all`'s outside-pip phrases in the
alphabetical order of its members; a sixteenth test,
`test_an_aggregate_extra_lists_its_members_steps_in_table_order`, was red
on that order (`<scratch>/red-order.log`, 1 failed: "Outside pip: FreeCAD
1.1.4, ...; the jscad command from npm; the OpenSCAD executable" where the
table's order is OpenSCAD, jscad, FreeCAD) and green after the fix: 16
passed, 41 subtests passed.

`flake8 --max-line-length=89` of the extension, `conf.py` and the five
changed test modules: 0 lines. `black --check` is not clean on these files,
as on 520 of the package's files at the base (`black --check machinome
tests`: "520 files would be reformatted"); not a gate of this change.

## 4. The declarations and the pages

4.1: `<scratch>/declare.py`, one script, the table of declarations of
design.md with 1.1's adjustment 3; for every page it asserts the title
found, one blank line under it and text after, no declaration before, the
extras in the table's order. `declared 85`. `git diff --numstat -- docs`:
every page `2 0` (the directive and one blank line; the blank line above
was there), `conf.py` aside.

Declarations as built: 27 `none`, 58 naming extras. Pages per extra:
`viewer` 23, `mechanics` 12, `cadquery` 12, `build123d` 9, `studio` 8,
`movie` 7, `web-snapshot` 2, `viewer-openscad`, `step`, `stl`, `molejo`,
`mesh`, `freecad`, `skills` 1 each; `openscad`, `solid2`, `jscad`, `brep`,
`all` none.

4.2: `start/install.rst` per Decision 4 (the requirements' clause, the
"Optional:" list gone, "CAD kernels are extras" become "The extras" under
the label `extras` with `.. extras::`, the "Packages and licences" sentence
(1.1 adjustment 6), the tutorial's line `machinome[viewer,cadquery,build123d]`,
the paragraphs on the five other extras gone through "None is needed to
start."); `start/first-machine.rst` the one clause. `git diff` of the two
shows those hunks and the declarations.

4.3: `docs/project/contributing.rst` and `CONTRIBUTING.rst`, Decision 6.

4.4 (`<scratch>/green-4.4-*.log`): `test_docs_structure.py` 38 passed, 6460
subtests passed; `test_repository_layout.py` 56 passed, 472 subtests
passed; `test_manual_extras.py` 15 passed, 41 subtests passed. The derived
rule's red shown once (`<scratch>/red-4.4-chapter5.log`): chapter 5's
declaration made `viewer, cadquery`, the test failed with
`{'tutorial/05-buttons.rst': {'build123d':
'tutorial/counter/c04_relations.py'}}`; the page restored from its copy
(`cmp` identical, its `git diff` the declaration alone).

## 5. The records

- 5.1: `HISTORY.rst` and `docs/project/changelog.rst`, Decision 7's
  bullets verbatim, after the last bullet of `Unreleased`.
- 5.2: `docs/architecture.md`, the Map row after "Sphinx embedding".
- 5.3: `docs/adrs/BUILD/ADR-195-every-manual-page-declares-the-extras-it-needs.md`,
  **Status: Proposed** (its promotion is the records closing), its Change
  link to `openspec/changes/manual-extras/` until the archive; the index
  line under BUILD before ADR-196's.
- 5.4: `workflow/warts.md`, one entry, "Findings from the framework cycle
  `manual-extras` (12 October 2026)": chapter 10 against chapter 1's and
  the installation page's sentences, with 6.5's refusal.
- 5.5: `test_release_records.py` 20 passed, 193 subtests passed;
  `test_docs_structure.py` 38 passed, 6460 subtests passed;
  `test_docs_exports.py` 22 passed, 15 subtests passed.

### 5.9 The manual in the source archive

The test, in `tests/test_release_records.py`,
`TheManualInTheSourceArchiveTest.test_the_sdist_carries_what_the_manual_s_build_reads`:
it builds the sdist (`python -m build --sdist --no-isolation --outdir
<tmp>`, from the package directory, 4.6 s), and asserts that it carries
every file under `docs/` that Git tracks or would track (`git ls-files
--cached --others --exclude-standard docs`) but the `.md` records Sphinx
does not read and `.gitignore`/`.gitkeep`, and nothing under `docs/_build/`.

Red (`<scratch>/red-5.9.log`): 1 failed, the sdist lacking 60 files:
`docs/_ext/` (2), `docs/_static/` (5), `docs/_exports/` (27),
`docs/howto/embed-the-viewer/` (2), `docs/howto/mechanism-formulas/` (3),
`docs/tutorial/counter/` (18), `docs/tutorial/pyproject.toml`,
`docs/requirements.txt`.

`MANIFEST.in`: the `docs` line gains `requirements.txt`, and five lines
follow it, with a comment: `docs/_ext *.py *.toml`, `docs/_static *.css
*.js *.svg`, `docs/_exports *.json *.stl`, `docs/howto *.html *.js *.py
*.toml`, `docs/tutorial *.py *.svg *.toml`, and `prune docs/_build`. Green
(`<scratch>/green-5.9.log`): 1 passed.

The build from the unpacked archive (`<scratch>/sdist/`):

```
$ env -C <bench>/packages/machinome .venv/bin/python -m build --sdist --no-isolation --outdir <scratch>/sdist/out
exit 0, machinome-0.8.1.tar.gz
$ env -C <scratch>/sdist/alone/machinome-0.8.1 <bench>/.docs-venv/bin/python -m sphinx -b html -W -E docs <scratch>/sdist/alone-html
exit 2, 9.1 s
```

Alone, the archive's manual does not build: 21 warnings, 15 autodoc
imports of node-package classes (`machinome.node.cadquery` and the
others, which are other distributions of the set) and 5 `.. machinome::`
exports that "the web viewer needs machinome.viewer.web, which is not
installed", then `copy_the_embedding_example` raising the same at
`build-finished`. `conf.py` reaches the set's other packages as directories
`../../machinome-*` beside the framework's, as in the repository.

With the repository's packages beside it (each `<bench>/packages/machinome-*`
linked into `<scratch>/sdist/beside/`, the viewer's bundle built by `make
docs`):

```
$ env -C <scratch>/sdist/beside/machinome-0.8.1 <bench>/.docs-venv/bin/python -m sphinx -b html -W -E docs <scratch>/sdist/beside-html
exit 0, 9.7 s, 0 warnings, 97 HTML files
```

So the core's archive now carries every file of `docs/` the build reads;
the build also reads the other packages of the set, which no single
archive carries. Settled by the orchestrator at the checkpoint (12 October
2026), `conf.py` unchanged: the archive carries every file the manual's
build reads, which the test holds, and building the pages needs the set's
packages installed beside them, from the index once 0.9.0 is uploaded or
from the repository.

## 6. Validation

### 6.1 The manual

```
$ env -C <bench> make docs          # <scratch>/make-docs-6.1.log
exit 0, 10.0 s (.docs-venv existing), 0 warnings, 97 HTML files
$ grep -rl 'class="machinome-needs' <bench>/packages/machinome/docs/_build/html --include=*.html | wc -l
58
```

58, as design.md expects with the studio's pages: the 58 pages whose
declaration names extras; the 27 `none` pages and the 12 other HTML files
(search, genindex, the release notes, ...) carry none.

### 6.2 The build's refusal (`<scratch>/make-docs-6.2-refusal.log`)

`howto/fusion.rst`'s declaration removed: `checking consistency...
.../docs/howto/fusion.rst: WARNING: the page declares no extra: begin it,
under its title, with `.. needs::` and the extras a reader installs to
follow it, or `none``, Sphinx exit 1, `make: *** [Makefile:148: docs] Error
1`, make exit 2. Restored from its copy (`cmp` identical; its `git diff`
the declaration alone, `2 0`); `make docs` again exit 0.

### 6.3 The rendering (`<scratch>/shots/`, `<scratch>/shot.py`, on `<scratch>/html`)

Pictures at 1200 and 390 px: `start-install-{1200,390}.png` (the section
"The extras"), `tutorial-04-relations-*`, `tutorial-10-share-*`,
`howto-film-a-movie-*`, `howto-freecad-assemblies-*`. Read: the line sits
under the title in the bordered box, "Needs" a link, and wraps within the
box at 390; the list is a definition list, each term a literal, its text
wrapping at 390. `document.documentElement.scrollWidth` of the installation
page: 1200 at 1200, 390 at 390.

The lines, verbatim (`.machinome-needs` inner text):

- `tutorial/04-relations`: Needs pip install "machinome[viewer,cadquery,build123d]".
- `tutorial/10-share`: Needs pip install "machinome[viewer,cadquery,build123d,viewer-openscad,web-snapshot]", and outside pip: the OpenSCAD executable; Chromium for Playwright, playwright install chromium.
- `howto/film-a-movie`: Needs pip install "machinome[movie]", and outside pip: Node 22 or newer, then machinome movie setup; the Chromium that machinome movie setup names; FFmpeg with ffprobe.
- `howto/freecad-assemblies`: Needs pip install "machinome[freecad]", and outside pip: FreeCAD 1.1.4, extracted, its root named by MACHINOME_FREECAD_ROOT.

The list's "Needed by", per entry: `viewer` the browser-viewer and
embedding how-tos, the Sphinx directive, the viewer section, the first
machine and the tutorial; `cadquery` markings, the first machine, the
tutorial; `build123d` markings, sheet, the tutorial; `step` and `stl` the
imported-parts how-to; `molejo`, `freecad`, `mesh`, `skills` their how-to;
`viewer-openscad` the tutorial; `web-snapshot` sharing and the tutorial;
`mechanics`, `movie`, `studio` their how-tos and their section;
`openscad`, `solid2`, `jscad`, `brep`, `all` none.

### 6.4 The viewer's browser review

```
$ <bench>/.venv/bin/python <bench>/packages/machinome-viewer/scripts/check-docs-browser.py <bench>/packages/machinome/docs/_build/html
exit 0, 10.6 s
```

12 pages, viewports 1440 and 390, 279 local links, mobile menu, search and
interactive example passed, 2 reference examples (pascaline: 1 admitted,
calculator: 360 admitted, restored), 0 browser errors. On the base build
(`<scratch>/base-html`): the same but 278 local links. (Design.md's 271 was
measured on 462f7119, before the seam's and the command's pages.) Its
artifacts go to the viewer's ignored `_build/docs-review`.

### 6.5 The tutorial's declarations (`<scratch>/probe_tutorial.py`, `.log`)

On a copy of `docs/tutorial/` in `<scratch>/tutorial`, through
`tests/brep_engine_absent.run_machinome`, refusing `machinome.node.step`,
`.molejo`, `.solid2`, `.jscad`, `.stl`, `.freecad`, `machinome.engine.mesh`
and, since the seam, `machinome.node.openscad` and
`machinome.viewer.openscad`:

| Run | Exit | Seconds |
|---|---|---|
| `build --all` | 0 | 53.2 |
| `build c01`, `machinome.node.build123d` refused too | 0 | 5.5 |
| `build c02`, the same | 0 | 6.0 |
| `build c03`, the same | 0 | 6.2 |
| `build first`, the same | 0 | 6.0 |
| `build c04`, the same | 1 | 6.0 |
| `test --all` | 0 | 12.1 |
| chapter 10's `snapshot -o counter.png --viewall --autocenter` | 1 | 0.3 |
| the same, `machinome.node.openscad` and `machinome.viewer.openscad` allowed | 0 | 4.7 |
| chapter 10's `snapshot --viewer web --drive crank=3580 -o carry.png` | 0 | 6.8 |

`c04`: "The model counter.c04_relations:Counter could not be assembled: No
module named 'machinome.node.build123d'". `test --all`: "Ran 11 tests in
8.72 seconds: 11 passed, 0 failed", its processes importing `OCP`,
`build123d`, `cadquery` and `machinome.engine.brep` of the B-rep stack.
Chapter 10's refused still: "Error: machinome snapshot --viewer openscad
needs the viewer-openscad extra: the openscad viewer needs
machinome.viewer.openscad, which is not installed; install it with 'pip
install "machinome[viewer-openscad]"'; or use --viewer web". The two
stills (`<scratch>/probe/counter.png`, `carry.png`, 1920 x 1080; the web
one RGBA, the counter with its digits at 0 9 9 mid-carry) were written.

### 6.6 The modules (`<scratch>/green-6.6-*.log`)

| Module | Base (1.3) | After |
|---|---|---|
| `test_docs_structure.py` | 32 passed, 6460 subtests | 38 passed, 6460 subtests |
| `test_manual_extras.py` | (new) | 16 passed, 41 subtests |
| `test_repository_layout.py` | 55 passed, 472 subtests | 56 passed, 472 subtests |
| `test_kernel_extras.py` | 19 passed, 80 subtests | 19 passed, 80 subtests |
| `test_release_records.py` | not run at the base | 20 passed, 193 subtests |
| `test_docs_exports.py` | not run at the base | 22 passed, 15 subtests |
| `test_sphinx_ext.py` | 14 passed | 14 passed |
| `test_tutorial_counter.py` | not run at the base | 3 passed (63.7 s) |
| `test_viewer_documentation_links.py` | 16 passed | 15 passed |

Every run exit 0, no skip. The products' tests that read the manual's
pages, from their directories: the studio's `tests/test_documentation.py`
23 passed, 232 subtests; the viewer's 12 passed; the mechanics helpers' 6
passed; the movie's `tests/test_repository.py` 17 passed.

### 6.7 Lint and status

`flake8 --max-line-length=89 docs/_ext/manual_extras.py docs/conf.py
tests/test_manual_extras.py tests/test_docs_structure.py
tests/test_repository_layout.py tests/test_viewer_documentation_links.py
tests/test_release_records.py`: 0 lines. `git -C <bench> status --short`:
96 modified (the 85 pages, `conf.py`, `architecture.md`,
`adrs/README.md`, `MANIFEST.in`, `warts.md`, four test modules, and at the
root `CONTRIBUTING.rst` and `HISTORY.rst`) and four untracked
(`docs/_ext/`, `docs/_static/manual-extras.css`, ADR-195,
`tests/test_manual_extras.py`), with `evidence.md` and `tasks.md` of this
change.

`openspec validate manual-extras --strict` (from
`<bench>/packages/machinome`): "Change 'manual-extras' is valid".

### The orchestrator's run at the checkpoint

The orchestrator reviewed the checkpoint on 12 October 2026 and kept every
departure of 1.1 as recorded. Its run on the bench, started at 00:01 on 13
October 2026 (`<join>/validate-run.log`, `<join>` being
`.../scratchpad/C10-join/`): `make test PKG=machinome` exit 0, 5046
passed, 9 skipped in 13 min 35 s (`viewer-command`'s 5023 and this
change's 23: `PageExtrasTest` 8, `test_manual_extras.py` 16, the guide's
and the archive's tests 1 each, less `KernelExtrasTest`'s two and the
seam's one installation-page tests); `make docs` exit 0; `make check` exit
0, 72 PASSED (36 archives on the tree and 36 on the clean copy).

## 7. The record of the change

On 13 October 2026, after the orchestrator's run had ended:

- 7.1: this file, complete.
- 7.2 and 7.3: `openspec archive manual-extras --yes` from
  `<bench>/packages/machinome`, which applied the deltas to
  `openspec/specs/user-documentation/spec.md` (two requirements added) and
  `openspec/specs/framework-contributor-guidance/spec.md` (one added) and
  moved the change to
  `openspec/changes/archive/2026-10-13-manual-extras/`, this file with it.
- ADR-195 **Accepted**, its date kept at 12 October 2026, the day the
  change was proposed and ratified; its Change link at the archive; a
  consequence stating the source archive's manual as settled above; its
  index line in `docs/adrs/README.md` Accepted.
- 7.4: the progress entry, entry 5 under "Progress" of
  `workflow/ongoing/release-0.9.md` at the repository root.
- The validation and the record-reading tests after the archive are in the
  orchestrator's report of the close.
