## Context

The seventh cycle of the road in `workflow/ongoing/release-0.9.md` at the
repository root, its decision 9 (pilot, 12 October 2026): "The manual stays
inside the framework's package, `packages/machinome/docs/`, distributed with
its source archive; the other products' pages fold into it. One small cycle
gives every page the extra it needs, rendered at the top of the page by the
manual's own extension, pinned by a test, the installation page's list
derived from the same declarations." Cut from the line `v0.9-joins` at
462f7119, on the bench `machinome/WTs/v0.9-joins-manual-extras`, whose head
holds the joins of the viewer, the skills and the movie with their manual
pages.

Paths below are the framework directory's (`packages/machinome/`) unless
they start with `packages/` or name a root file. Facts were read on the bench
at 462f7119 unless marked *assumed*. Probes ran in the scratch directory
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C10-propose/`
(`<scratch>` below), never in the bench, with the bench's uv venv (CPython
3.12.3, Sphinx and Playwright from the `dev` extra, no `sphinx_rtd_theme`)
and a docs venv made from `docs/requirements.txt` alone (`<scratch>/docs-venv`:
Sphinx 9.1.0, sphinx_rtd_theme 3.1.0, docutils 0.22.4, `packaging` 26.3, and
`machinome-viewer` 0.8.0 from PyPI, since 0.8.1 is not uploaded).

### What the manual is today

- `docs/conf.py` lists `sphinx.ext.autodoc`, `sphinx.ext.napoleon`,
  `sphinx.ext.doctest` and `machinome.sphinx` (the framework's own
  `.. machinome::` directive, a package module a project's manual uses too);
  it defines the release facts as `rst_prolog` substitutions, is nitpicky,
  and copies the embedding example at `build-finished`. The manual has no
  extension of its own and no `docs/_ext/`.
- 79 `.rst` files: the two release notes under `releases/` (history, reached
  from the changelog's toctree, excluded from the licence test) and 77 pages:
  `index`, `why`, `examples`, `start/` 2, `tutorial/` 10, `howto/` 20,
  `concepts/` 9, `reference/` 29 (`api`, `assertions`, `cli`, `manuals`,
  `sphinx`, and the sections `mechanics/` 11, `viewer/` 9, `movie/` 4),
  `project/` 4.
- `start/install.rst`: "Requirements" (Linux, Python, OpenSCAD for the
  OpenSCAD family, an "Optional" list of the `jscad` command and FreeCAD);
  "CAD kernels are extras", a `list-table` of twelve rows (the nine node
  types, `brep`, `mesh`, `all`) and the refusal prose; "Packages and
  licences", one sentence naming fifteen distributions; "Install", whose
  first line is `python -m pip install "machinome[viewer,cadquery]"`, "which
  the tutorial models with"; "Check the installation"; a paragraph "Four more
  extras exist" (`mechanics`, `skills`, `movie` with its two-line block,
  `web-snapshot`); "Upgrading". The `studio` extra is named on no page but
  `project/status.rst` and `project/upgrading.rst`.
- The core's manifest declares 20 extras: `dev` and `docs` (a contributor's)
  and 18 a reader installs: `viewer`, `web-snapshot`, `mechanics`, `movie`,
  `brep`, `mesh`, `cadquery`, `build123d`, `step`, `molejo`, `openscad`,
  `solid2`, `jscad`, `stl`, `freecad`, `skills`, `all`, `studio`. Each but
  `all` lists one requirement, a distribution of the set; `all` lists
  `machinome[cadquery,build123d,step,molejo,brep,mesh,openscad,solid2,jscad,stl,freecad]`.
  The manifest's comments are not a contract.
- The tests that read the installation page: `KernelExtrasTest` in
  `tests/test_docs_structure.py` (`test_the_installation_page_names_every_kernel_extra`,
  ten `machinome[x]` strings; `test_the_installation_page_names_the_extension_distributions`,
  fifteen distribution names and the movie's two install lines, read from
  the page's source). `tests/test_kernel_extras.py` holds the manifest's
  extras (`EXTRAS`, written out) and reads no page.
- `tests/test_sphinx_ext.py` builds small Sphinx projects with
  `sphinx.testing.util.SphinxTestApp` in temporary directories: the pattern
  this cycle's unit tests take.
- `MANIFEST.in` carries `docs` as `*.rst conf.py Makefile make.bat *.jpg
  *.png *.gif`: neither `_static/*.js`, `_static/*.css` nor the committed
  exports' `manifest.json` and models. The manual is not buildable from the
  source archive today (*inferred* from the file; not built from an sdist
  here).

### Probes

1. **The count** (`<scratch>/declarations.py`, the table of declarations
   below as a dictionary, checked to cover the 77 pages exactly). A page
   "names an extra" when its source matches `machinome\[[a-z0-9,-]+\]`,
   ``` ``x`` extra ``` or `the x extra`. 24 of the 77 pages do (concepts 1,
   how-to 8, project 3, reference 9, start 2, tutorial 1). Of the 50 pages
   whose declaration names an extra, 8 name one before their first section
   heading (`howto/browser-viewer`, `howto/declare-a-movie`,
   `howto/mechanism-formulas`, `reference/mechanics/index`,
   `reference/movie/command`, `reference/movie/index`, `reference/sphinx`,
   `reference/viewer/index`), 8 further down, 34 nowhere. Pages per extra:
   `viewer` 23, `cadquery` 12, `mechanics` 12, `build123d` 9, `movie` 7,
   `web-snapshot` 2, `skills`, `mesh`, `molejo`, `freecad`, `step`, `stl`
   and `openscad` 1 each.
2. **The tutorial's chapter 4 without build123d** (`<scratch>/probe_c04.py`:
   the tutorial project copied to `<scratch>/tutorial`, `machinome build
   <model>` through `tests/brep_engine_absent.run_machinome` with `build123d`
   and `machinome.node.build123d` refused, a fresh build directory each):
   `c03` exit 0; `c04` exit 1, "The model counter.c04_relations:Counter
   could not be assembled: No module named 'machinome.node.build123d'". The
   counter's digits are `Svg('digits.svg')` artwork, which
   `machinome.node.markings` reduces through `machinome.node.build123d`
   (its docstring: "only building a stale marking does" need the extra; a
   reader's first build is one).
3. **The tutorial with only its declared node packages**
   (`<scratch>/probe_tutorial.py`, `probe_test.py`, `probe_snap.py`; the
   refused modules `machinome.node.step`, `.molejo`, `.openscad`, `.solid2`,
   `.jscad`, `.stl`, `.freecad` and `machinome.engine.mesh`):
   `build --all` exit 0 in 60.7 s; `c01`, `c02`, `c03` and `first` with
   `machinome.node.build123d` refused too, exit 0, 6.0 to 6.3 s each; `test
   --all`, "Ran 11 tests in 0.96 seconds: 11 passed, 0 failed", its processes
   importing `OCP`, `cadquery` and `machinome.engine.brep` and nothing else
   of the B-rep stack; chapter 10's `machinome snapshot -o counter.png
   --viewall --autocenter`, exit 1, "Error: machinome snapshot --renderer
   openscad needs the openscad extra: the openscad node type (OpenScadNode)
   needs machinome.node.openscad, which is not installed; install it with
   'pip install "machinome[openscad]"'; or use --renderer web". A first run
   that also refused the third-party `manifold3d` failed every chapter inside
   `trimesh`'s `util.has_module`, which calls `importlib.util.find_spec` and
   expects `None`, not a raise: the finder stands in for an absent package of
   the set, not for an absent third-party module.
4. **The extension on three pages** (`<scratch>/proto/`: a manifest of five
   reader extras, `index`, `start/install` with the list, a movie how-to with
   an overline title, a springs how-to whose label precedes its title, a
   concept page; built from the docs venv with `-b html -n -W --keep-going
   -E`): exit 0. Five refusals, each a copy with one edit, each exit 1: an
   undeclared page ("WARNING: the page declares no extra ..."); an unknown
   extra ("ERROR: needs: viewr is not an extra of the manual's table", with
   the line); a declaration after a paragraph and a second declaration
   ("ERROR: needs: the declaration is the first thing after the page's
   title"); a manifest extra the table lacks ("WARNING: the manual's table
   of extras [...] is not the manifest's [...]"). Screenshots at 1200 and
   390 px wide: the line sits under the title in a bordered box and wraps at
   390. The list as a four-column table scrolled sideways at 390 (the
   theme's cells do not wrap; the base installation page's own table does the
   same); as a definition list it reads at 390 with no extra style.
5. **A docinfo field instead** (`<scratch>/docinfo/`): `:needs: movie`
   before the title, after a label or not, is in `env.metadata[docname]`;
   the same field after the title is not metadata and renders as a visible
   field list.
6. **The whole manual declared** (`<scratch>/full/`: the bench's `docs/`
   copied beside symbolic links to the framework's package and its
   siblings, the declarations of the table inserted under every title by
   `<scratch>/declare.py`, the prototype extension and table under
   `docs/_ext/`, `conf.py` given the path, the extension and
   `manual_extras_exempt = ['releases/*']`, the installation page's
   `list-table` replaced by `.. extras::` under an `extras` label). The
   base, built the same way into `<scratch>/base-html`: exit 0, 9.0 s, 89
   HTML files. The first declared build: exit 1, three pages refused,
   `examples`, `project/changelog` and `project/contributing`, whose label
   equals their title's identifier, so docutils puts an INFO
   `system_message` ("Duplicate implicit target name") into the section
   before the directive runs; the placement check then ignores
   `system_message` nodes, and the build gives exit 0, 8.3 s, 89 HTML files,
   50 of them carrying the line. The `all` entry written as one literal of
   its eleven extras made the installation page 678 px wide at a 390 px
   viewport; written as eleven literals, 390. The base installation page is
   390 wide at 390 (its table scrolls inside its own box).
7. **The viewer's pages reviewed in a browser** (`<scratch>/check-docs-browser.py`,
   a copy of `packages/machinome-viewer/scripts/check-docs-browser.py` whose
   artifacts go to `<scratch>/docs-review`, run on probe 6's build): exit 0;
   12 pages at 2 viewports, 271 local links, the mobile menu, the search and
   the interactive example passed, 2 reference examples, 0 browser errors.
8. **A unit harness** (`<scratch>/probe_unit.py`, the bench venv,
   `SphinxTestApp` and the default theme, the prototype extension reading
   the core's real manifest): a three-page project builds in 0.38 s with no
   warning once the table holds no cross-reference (a `:doc:` to
   `/howto/markings` in the table warned "unknown document" in the scratch
   project); the resolved doctree's text holds "Needs pip install
   "machinome[movie]", and outside pip, ..." and every reader extra with its
   distribution, `machinome[studio]` and `machinome movie setup` included,
   while the HTML splits each literal into one span per word, so assertions
   read the doctree; an undeclared page warns.
9. **The code a teaching page shows** (`<scratch>/derived.py`): reading the
   code blocks of every `tutorial/`, `howto/` and `start/first-machine` page
   (`code-block`, `doctest`, `::` literal blocks) and every module a page
   literal-includes, closed over its relative imports, the rules of Decision
   5 derive for each page a set of extras; every page's declaration in the
   table holds its set but `howto/backends`, whose code shows all nine node
   types (the chooser page).

### Assumptions about the cycles before this one

Three cycles land on the line before this planning commit (the orchestrator
fast-forwards the bench); this design was written on 462f7119 without them.

- `release-tooling` (ADR-192, *assumed* from its planning commit afef5c96):
  `make docs` installs `docs/requirements.txt` alone into `.docs-venv/` and
  builds with `-W -E`. The extension needs nothing more, so the target is
  unchanged and is this cycle's manual build.
- `join-studio` (ADR-193, *assumed* from its uncommitted planning files):
  eight pages, `howto/open-a-studio-project`, `howto/studio-workspace`,
  `howto/studio-agents` and `reference/studio/` (`index`, `command`,
  `project-configuration`, `profiles`, `troubleshooting`), the `studio`
  extra pinned, and a paragraph and test assertions for the studio on the
  installation page. Here the eight pages declare `studio`, the section is a
  product's reference section, the `studio` row's outside-pip phrases are
  the opening how-to's prerequisites, and that paragraph and those
  assertions fold into the list and its rendered test.
- `viewer-seam` (ADR-194, *assumed*): the flag `--renderer` becomes
  `--viewer`, and a second viewer extra may appear. The derived rule for the
  web photograph reads either flag. An extra it adds fails the build until
  the table has its row, by design, and its pages declare it. `join-movie`'s
  test refuses `--viewer` on every page; that conflict is the seam's to
  settle, and the table's text names no flag.
- `viewer-command`, the road's sixth cycle, if it lands first: its pages
  declare `viewer`.

The ADR number is 195 if those three take 192 to 194; the orchestrator
assigns the next free number at implementation.

## Goals / Non-Goals

**Goals:**

- A reader who lands on any page sees, before its first paragraph, the one
  `pip install` line and the outside-pip steps the page needs, or nothing
  when the bare framework suffices.
- One declaration per page, recorded where the build can read it, so the
  installation page lists every extra from the manifest with the pages that
  need it, and nothing about an extra is kept by hand twice.
- The build refuses an undeclared page, an unknown extra and a table that
  drifts from the manifest; the suite refuses the same before any build and
  holds the declarations to rules derived from the pages' own code.
- The two false claims of the finding: the installation page's tutorial line
  names what the tutorial needs; chapter 10's needs are stated at its top.

**Non-Goals:**

- Rewriting a page's prose about its extra. The line is added; a page's own
  install section stays (it says more: the `machinome movie setup` output,
  FreeCAD's checksum).
- Chapter 10's photograph text, the requirements paragraph and chapter 1's
  sentence that contradict it (Open Questions 6).
- `MANIFEST.in` and the source archive's manual (Open Questions 7).
- The workspace's `write-the-manual` skill (the `workspace-consistency`
  cycle) and the viewer's own `scripts/check-docs-browser.py`.
- A version, a push, an upload, a Read the Docs setting.

## Decisions

### 1. The declaration is a directive, first under the title

```rst
Film a movie of your machine
============================

.. needs:: movie
```

One argument: extras of the table separated by commas, or `none` alone.
It is the first element of the page's first section, a `system_message`
docutils puts there aside (probe 6); a label above the title and an overline
are allowed (probe 4). It renders nothing for `none`.

A directive rather than a docinfo field (probe 5): it is validated where it
is written, with its line number; a field misplaced after the title
silently renders as a field list instead of failing; and the directive is
where its line appears. Rejected: a field read by a transform that inserts
the line after the title.

Every page but those the setting `manual_extras_exempt` names declares
(`['releases/*']` in `conf.py`: the release notes are history). `index`,
`why`, `examples` and the project pages declare `none` too, so the rule has
no list of pages to keep.

### 2. The extension

`docs/_ext/manual_extras.py`, the manual's own, imported by `conf.py` from
`docs/_ext` (`sys.path.insert(0, os.path.abspath('_ext'))`, `'manual_extras'`
appended to `extensions`). It imports Sphinx, docutils, `packaging` (a
requirement of Sphinx, `packaging>=23.0`) and the standard library, so
`docs/requirements.txt` and `.readthedocs.yaml` are unchanged. A module docstring
states what it does; the licence header is the repository's.

- Two settings: `manual_extras_manifest`, the core's manifest relative to
  the configuration directory (default `'../pyproject.toml'`, which the unit
  tests set to an absolute path), and `manual_extras_exempt`, `fnmatch`
  patterns of document names that need no declaration.
- `.. needs::` (a `SphinxDirective`): refuses, as a directive error naming
  the page and line, a name the table lacks (`none` among others included),
  a name given twice, and a declaration that is not the first element under
  the title or is the page's second. It records the extras, in the table's
  order, on the environment (`env.manual_extras[docname]`, purged on
  `env-purge-doc`, merged on `env-merge-info`, parallel-safe). For extras
  it renders a `container` of class `machinome-needs` holding one paragraph
  parsed as reST:

  ``:ref:`Needs <extras>` ``pip install "machinome[<extras, comma-joined, table order>]"```
  then, when any of those extras (an extra written `machinome[...]` in the
  manifest standing for its members) needs something outside pip,
  `, and outside pip: ` and those phrases, each once, joined by `; `, then a
  full stop. "Needs" links to the installation page's list (label `extras`).
- `.. extras::`: one definition list (class `machinome-extras`) with an item
  per row of the table, in its order. The term is ``` ``machinome[<name>]`` ```;
  the definition's first paragraph reads `Installs <what>, for <for>.` and,
  when the row needs something outside pip, `Outside pip: <phrases joined by
  "; ">.`, where `<what>` comes from the manifest: each requirement's
  distribution name, with its extras when it has some
  (``` ``machinome-viewer`` with its ``snapshot`` extra ```), or, for a
  requirement on `machinome` itself, `the extras` and each extra as its own
  literal (probe 6: one literal of eleven names widens the page). A second
  paragraph, `Needed by <pages>.`, is filled at `doctree-resolved`: the
  pages declaring the extra in the order of their document names, the
  tutorial once as "the tutorial", linked to its first declaring chapter,
  and a reference section once by its index when the index declares it;
  none when no page declares it.
- At `env-check-consistency`: a warning naming each found document that
  declares nothing and is not exempt, and a warning naming both sets when the
  table's extras are not the manifest's minus `dev` and `docs`. Under `-W`
  (CI, Read the Docs' `fail_on_warning`, `make docs`) each fails the build.
- `docs/_static/manual-extras.css`, added by `app.add_css_file`: the box's
  left border and background (`border-left: 4px solid #2980b9; background:
  #f3f6f6; padding: 6px 12px; margin-bottom: 24px`, its paragraph without
  margin), the theme's link colour.

Rejected: adding the directive to `machinome.sphinx`, the framework's
public extension a project's manual uses, which has nothing to do with the
framework's extras; a table instead of a definition list (probe 4).

### 3. The table of extras

`docs/_ext/manual_extras.toml`, read with `tomllib`. One table per extra a
reader installs, in the order the installation page lists them; `for`, an
inline reST phrase completing "for ...", with no cross-reference (probe 8);
`outside`, inline reST phrases, each completing "needs, outside pip, ...".
Verbatim:

```toml
# The extras a reader installs, in the order the installation page lists
# them: what each is for, and what it needs that no pip extra installs.
# The distribution each installs is read from the framework's manifest, and
# the build refuses a table whose extras are not the manifest's.

[viewer]
for = "the browser viewer: ``machinome develop`` opens it, and every export carries its page"
outside = []

[cadquery]
for = "``CadQueryNode``"
outside = []

[build123d]
for = "``Build123dNode``, ``Build123dSheetNode`` and the SVG artwork of markings"
outside = []

[step]
for = "``StepNode``, ``StepAssembly`` and ``machinome import-step``"
outside = []

[molejo]
for = "``MolejoNode``, with `molejo <https://molejo.readthedocs.io>`_"
outside = []

[openscad]
for = "``OpenScadNode`` and the OpenSCAD renderer of ``machinome snapshot``"
outside = ["the OpenSCAD executable"]

[solid2]
for = "``Solid2Node``, with the ``openscad`` extra's package"
outside = ["the OpenSCAD executable"]

[jscad]
for = "``JScadNode``, compared on its mesh by the mesh engine"
outside = ["the ``jscad`` command from npm"]

[stl]
for = "``StlNode``, compared on its mesh by the mesh engine"
outside = []

[freecad]
for = "``FreeCADAssemblyNode`` and ``FreeCADJoint``"
outside = ["FreeCAD 1.1.4, extracted, its root named by ``MACHINOME_FREECAD_ROOT``"]

[brep]
for = "the B-rep engine, which every node type over it installs too"
outside = []

[mesh]
for = "the mesh engine, for every comparison on meshes"
outside = []

[all]
for = "every node type and both engines"
outside = []

[web-snapshot]
for = "the viewer with its headless browser driver, for transparent photographs"
outside = ["Chromium for Playwright, ``playwright install chromium``"]

[mechanics]
for = "the mechanics helpers, ``machinome.mechanics``"
outside = []

[skills]
for = "the machinome skills and the command ``machinome skills``"
outside = []

[movie]
for = "the films of a machine, ``machinome.movie`` and the command ``machinome movie``, with the viewer they draw with"
outside = ["Node 22 or newer, then ``machinome movie setup``", "the Chromium that ``machinome movie setup`` names", "FFmpeg with ffprobe"]

[studio]
for = "Machinome Studio and the command ``machinome studio``"
outside = ["Git", "the OpenSCAD executable", "the OpenSpec CLI", "a logged-in agent backend", "Chromium for Playwright, ``playwright install chromium``"]
```

`all`'s `outside` stays empty: the extension shows its members' phrases.
The `studio` row is *assumed* from `join-studio`'s opening how-to and
follows it as landed. Each phrase repeats a fact one page already states
(the installation page's requirements, the FreeCAD and movie how-tos):
the line is the summary, the page keeps the detail.

Rejected: a dictionary in `conf.py`, which would put twenty-odd lines of
prose among the release facts and make the tests import or parse
`conf.py`; the manifest's comments, which are not a contract; the table in
the extension module, which makes a test import Sphinx to read data.

### 4. The installation page

`start/install.rst` after the change (the rest unchanged):

- "Requirements": the "Optional:" list and its two items go (they are the
  `jscad` and `freecad` rows' outside-pip phrases); in the OpenSCAD item,
  `and a ``CadQueryNode`` where only ``machinome[cadquery]`` is` becomes
  `and a ``CadQueryNode`` where CadQuery is and SolidPython is not`.
- "CAD kernels are extras" becomes, above the unchanged refusal prose:

  ```rst
  .. _extras:

  The extras
  ----------

  Every package of the set beyond the framework is installed by an extra,
  and every page of this manual says at its top which extras it needs. A
  node type lives in one module, ``machinome.node.<name>``, installed by the
  extra of the same name: the extra is the last component of the module's
  address.

  .. extras::
  ```

  replacing the section's first paragraph and its `list-table`.
- "Packages and licences": the first sentence becomes `The framework is the
  package ``machinome``, and every package its extras install, listed
  above, is licensed |framework_licence|, at the recipient's choice.`; the
  rest of the section is unchanged.
- "Install": `install the framework with the viewer and CadQuery, which the
  tutorial models with:` becomes `install the framework with the viewer,
  CadQuery and build123d, which the tutorial models with (build123d draws
  the digits on its drums):`, and the line becomes `$ python -m pip install
  "machinome[viewer,cadquery,build123d]"`.
- The paragraph "Four more extras exist ..." with its code block, through
  "None is needed to start.", goes: its four extras are rows of the list,
  the movie's two steps its outside-pip phrases. `join-studio`'s studio
  paragraph, wherever it lands on the page, goes the same way.

`start/first-machine.rst`: `as on the installation page's route, only
``machinome[cadquery]`` is installed,` becomes `as on the installation
page's route, SolidPython is not installed,`.

### 5. The pins, red first

`tests/test_docs_structure.py`, a new class `PageExtrasTest` (module
docstring and class docstring name this change):

- `TABLE`: the table read with `tomllib`; `declaration(text)`: the title
  found as `ReadmeTest.headings` finds one (with an optional overline), the
  first non-blank line after it, and its extras or `()` for `none`.
- `test_every_page_declares_first_under_its_title`: every `.rst` but under
  `releases/` and `_build` has exactly one line `.. needs:: ...` at column 0,
  and it is the first non-blank line after the title. Red at the base: 77
  pages, each named.
- `test_a_declaration_names_extras_of_the_table`: `none` alone, or names of
  the table, none twice.
- `test_the_table_is_the_manifest_s`: the table's keys equal the manifest's
  `optional-dependencies` minus `dev` and `docs`, and every row has `for`
  and `outside`. Red: no table.
- `test_a_product_s_reference_section_declares_its_product`: every page
  under `reference/viewer/`, `reference/movie/`, `reference/mechanics/` and
  `reference/studio/` (each present) declares `viewer`, `movie`,
  `mechanics`, `studio` and nothing else.
- `test_the_core_s_rules_and_records_declare_none`: `index`, `why`,
  `examples`, `start/install`, every page under `concepts/` and `project/`,
  and `reference/api`, `reference/assertions`, `reference/cli` and
  `reference/manuals` declare `none`.
- `test_a_teaching_page_declares_what_its_code_needs`: for every page under
  `tutorial/` and `howto/` and `start/first-machine`, the extras derived from
  its code are among its declaration's. The code is every `code-block`,
  `code`, `doctest` and `::` literal block and every file a
  `literalinclude` names, closed over that file's `from .<module> import`
  lines in its directory. The rules: `machinome.node.<key>` for a key of
  `machinome.node.supported.NODE_TYPES` gives `<key>`; `machinome.mechanics`
  gives `mechanics`; `machinome.movie` and a line beginning `machinome
  movie` give `movie`; a line beginning `machinome skills` gives `skills`; a
  line beginning `machinome studio` gives `studio`; `Svg(` gives
  `build123d`; `--renderer web` or `--viewer web` gives `web-snapshot`. One
  exemption, with its reason in the test: `howto/backends`, the page that
  chooses among the node types and names each one's extra in its table.
- `test_the_installation_page_derives_its_list`: the page holds the label
  `.. _extras:`, the heading "The extras" under it and one `.. extras::`, and
  no `list-table`.
- `test_the_tutorial_s_install_line_names_its_chapters_extras`: the extras
  of the first `pip install "machinome[...]"` line of the page's "Install"
  section equal the union of the declarations of the tutorial chapters that
  literal-include a module of `tutorial/counter/` (chapters 1 to 9). Red:
  the line names `viewer,cadquery`.

`KernelExtrasTest`'s two installation-page tests are removed, with
`EXTRAS`, and the class docstring says the rendered list holds them since
this change: their assertions move to the rendered list below, where they
hold for every extra of the manifest instead of the ten and fifteen written
out.

`tests/test_manual_extras.py`, new, on `tests/test_sphinx_ext.py`'s
pattern (`SphinxTestApp`, a temporary project whose `conf.py` puts
`docs/_ext` on the path, lists `manual_extras`, sets
`manual_extras_manifest` to the core's manifest, is nitpicky; skipped
without Sphinx); assertions read the resolved doctrees' text (probe 8):

- a declared project (an index, an installation page with the label and
  the list, a page declaring `movie`, one declaring `cadquery, viewer`, one
  `none`) builds with no warning;
- the list names `machinome[<x>]` for every reader extra of the manifest,
  and, for each, every requirement's distribution, or each member extra of
  `all`; the movie entry names `machinome movie setup`, `Node 22`, `FFmpeg`
  and `Chromium`; the freecad entry `MACHINOME_FREECAD_ROOT`; the jscad
  entry the `jscad` command; the movie entry is "Needed by" the movie page;
- the movie page's line is `Needs pip install "machinome[movie]", and
  outside pip: ` followed by the movie row's three phrases; the
  `cadquery, viewer` page's names `machinome[viewer,cadquery]`; the `none`
  page has no "Needs";
- refusals, one project each: an undeclared page warns naming it; an
  unknown extra, `none, viewer`, a repeated extra, a declaration after a
  paragraph and a second declaration each give an error naming the page and
  line; a manifest copy with an extra the table lacks, and one without an
  extra the table has, each warn naming both sets;
- the extension module imports only Sphinx, docutils, `packaging` and the
  standard library (its `import` statements read with `ast`).

Red: `ModuleNotFoundError` for `manual_extras` (the extension does not
exist), at each build.

`tests/test_repository_layout.py`, `test_the_guide_says_a_page_declares_its_extras`:
`CONTRIBUTING.rst` contains ``` ``.. needs::`` ```. Red: it does not.

The tutorial's declarations are proved once by probe 3's builds, rerun at
implementation into the evidence, not in the suite (Open Questions 8).

### 6. The rule where a page is written

- `docs/project/contributing.rst`, after the sentence ending "the suite
  builds and tests every chapter.": `Every page begins, under its title,
  with ``.. needs::`` and the extras a reader installs to follow it, or
  ``none``; the build refuses a page without one.`
- `CONTRIBUTING.rst`, "Pull requests", step 3 becomes: `Update the
  documentation the change touches: the manual under
  ``packages/machinome/docs/``, whose every page begins, under its title,
  with ``.. needs::`` and the extras it needs or ``none``, and the
  changelog's ``Unreleased`` section for anything a project can use, in the
  same change.`

### 7. The records and the ADR

- `HISTORY.rst`, `Unreleased`, after the last bullet:

  ```rst
  * **Every page of the manual says what it needs.** A page begins with
    ``.. needs::`` and the extras a reader installs to follow it, or
    ``none``; the manual's own Sphinx extension, ``docs/_ext/manual_extras.py``,
    shows them at the top of the page with what they need outside pip, and
    the installation page lists every extra of the manifest with the pages
    that need it. The build refuses an undeclared page and a table of
    extras that is not the manifest's. The tutorial's install line names
    ``build123d``, which its digits need. Change ``manual-extras``
    (ADR-195).
  ```
- `docs/project/changelog.rst`, `Unreleased`, after the last bullet:

  ```rst
  * **Every page says what to install.** The top of each page names the
    ``pip install`` line it needs and what those extras need outside pip,
    and :doc:`/start/install` lists every extra with the pages that need
    it. The tutorial installs ``machinome[viewer,cadquery,build123d]``:
    the digits on its drums need build123d.
  ```
- `docs/architecture.md`, the Map, a row after "Sphinx embedding":
  `| The manual | `docs/` (`conf.py`, `_ext/manual_extras.py` and its table
  `_ext/manual_extras.toml`) | `user-documentation` | 195 |`.
- ADR-195, `docs/adrs/BUILD/ADR-195-every-manual-page-declares-the-extras-it-needs.md`,
  Accepted, dated at implementation, change `manual-extras`, related to
  ADR-182 and ADR-188 (the manual is the set's) and to ADR-020 (the
  framework's own Sphinx directive, which it does not touch). Context: the
  finding's counts and the two false claims. Options: a directive, a
  docinfo field, prose per page. Decision: Decisions 1 to 5 in brief.
  Consequences: a new page declares or the build fails; a new extra fails
  the build until the table has its row; a reader sees the line before the
  page; the tutorial's needs are derived from its code. Its index line in
  `docs/adrs/README.md` under BUILD. No ADR holds the manual's shape today
  (the index names none), so nothing is amended.

### 8. The spec deltas

- `user-documentation`: ADDED "Every page states the extras it needs" and
  "The installation page lists the extras from the manifest".
- `framework-contributor-guidance`: ADDED "The contributor guide says a
  manual page declares its extras".
- `kernel-extras`: unchanged. Its sentence "The installation page of the
  manual SHALL name, for each extra that installs a distribution of the set,
  the distribution it installs" and its scenario "The installation page
  names the extension distributions" hold of the rendered list, which
  `test_manual_extras.py` reads. The other requirements that say the
  installation page names an extra (`user-documentation`: the node types,
  FreeCAD, the skills, the films; `join-studio`'s studio) hold the same way.

### 9. Validation

- The red runs of Decision 5, each module once, one pytest process at a
  time.
- After the change: `test_docs_structure.py`, `test_manual_extras.py`,
  `test_repository_layout.py`, `test_kernel_extras.py`,
  `test_release_records.py`, `test_docs_exports.py`, `test_sphinx_ext.py`
  and `test_tutorial_counter.py` on the bench venv; the whole suite is the
  orchestrator's at the cycle's head.
- `make docs` at the root (`release-tooling`'s target; before it lands, the
  same command by hand: a venv from `docs/requirements.txt` alone and
  `python -m sphinx -b html -n -W --keep-going -E docs <out>` from
  `packages/machinome`): exit 0, its HTML count, and the count of pages
  carrying `machinome-needs` (58 with `join-studio`'s eight).
- The rendering in Chromium: the installation page's list and four pages
  (chapter 4, chapter 10, the movie how-to, the FreeCAD how-to)
  photographed at 1200 and 390 px into the scratch directory and looked
  at; `document.documentElement.scrollWidth` at 390 equal to 390 on the
  installation page; `packages/machinome-viewer/scripts/check-docs-browser.py`
  on the build (its artifacts under the viewer's ignored `_build/`), its
  counts recorded.
- Probe 3's tutorial runs, rerun on the changed tree.
- No universe sweep: no module of a package changes.

## The declarations

Every page at 462f7119 and the eight `join-studio` adds (*assumed*), with
what it declares. The judgment behind the rows the rules of Decision 5 do
not fix: a page declares what its commands and code need as written; the
viewer where the page's steps are done or seen in it (`machinome develop`
to watch, an export's page, the viewer's own pages); a concept, reference or
project page of the core declares `none` (its examples illustrate a rule,
and a copied example's import refusal names its extra).

| Page | Declares |
|---|---|
| `index`, `why`, `examples` | none |
| `start/install` | none |
| `start/first-machine` | viewer, cadquery |
| `tutorial/01-part`, `02-input`, `03-dimensions` | viewer, cadquery |
| `tutorial/04-relations` to `09-clocked` (six) | viewer, cadquery, build123d |
| `tutorial/10-share` | viewer, cadquery, build123d, openscad, web-snapshot |
| `howto/backends` | none (the chooser; its table names each kind's extra) |
| `howto/imported-parts` | step, stl |
| `howto/sheet-parts` | build123d |
| `howto/flexible-parts` | molejo |
| `howto/fusion` | none |
| `howto/markings` | cadquery, build123d |
| `howto/repeat-and-vary` | none |
| `howto/timeline` | none |
| `howto/several-models` | none |
| `howto/fast-tests` | mesh |
| `howto/simulate-existing` | none |
| `howto/freecad-assemblies` | freecad |
| `howto/mechanism-formulas` | mechanics |
| `howto/browser-viewer` | viewer |
| `howto/share-an-export` | web-snapshot |
| `howto/embed-the-viewer` | viewer |
| `howto/film-a-movie`, `declare-a-movie`, `draw-a-movie-stage` | movie |
| `howto/assistant-skills` | skills |
| `howto/open-a-studio-project`, `studio-workspace`, `studio-agents` | studio |
| `concepts/` (nine) | none |
| `reference/cli`, `api`, `assertions`, `manuals` | none |
| `reference/sphinx` | viewer |
| `reference/mechanics/` (eleven) | mechanics |
| `reference/viewer/` (nine) | viewer |
| `reference/movie/` (four) | movie |
| `reference/studio/` (five) | studio |
| `project/` (four) | none |

At the base: 77 pages, 50 declaring an extra, 27 `none`; with
`join-studio`, 85 pages, 58 and 27.

## Risks / Trade-offs

- [A declaration goes stale when a page changes] → The derived rule holds a
  teaching page to its code; the build refuses an undeclared page; a
  judgment extra (the viewer on a page that stops using it) is held by
  review only. The design accepts that over a written-out copy of the
  table in a test.
- [A new extra of the manifest fails every build until the table has its
  row] → Intended: the list is complete or the manual does not build. The
  failure names both sets.
- [The line repeats what a page's install section says] → The line is one
  sentence; the section keeps the detail. The 34 pages that name no extra
  gain the only statement they have.
- [Chapter 10's line is long and asks for OpenSCAD in a tutorial that says
  it needs none] → It is what the chapter's commands need as written; the
  contradiction is reported (Open Questions 6) rather than settled here.
- [The extension runs on Read the Docs] → It needs nothing the requirements
  file does not bring (probe 6, from the docs venv); its static file is in
  `_static/`, which `conf.py` already serves.
- [`SphinxTestApp` builds add to the suite] → About 0.4 s each (probe 8),
  roughly a dozen builds.

## Migration Plan

None for a reader: pages gain a line, the installation page a list in place
of a table. For an author: a new page declares, or the build says so. The
viewer's `check-docs-browser.py` and the movie's and studio's page tests
read pages that change by one line under their title; nothing they assert
is touched (probe 7 for the viewer's). Rollback: revert the commit.

## Open Questions

1. **The declaration's form.** A directive under the title, or a docinfo
   field above it (probe 5). Recommendation: the directive (Decision 1): it
   fails where it is wrong and renders where it is written.
2. **A page without a declaration.** A build error, a test failure, or
   both. Recommendation: both: the extension's warning fails every `-W`
   build (CI, Read the Docs, `make docs`), and the structure test fails
   `make test` before any build.
3. **The descriptions' source.** A TOML table beside the extension held to
   the manifest's set of extras (Decision 3), a dictionary in `conf.py`, or
   the manifest's comments. Recommendation: the TOML table; the manifest
   supplies the distributions, the table the reader's words.
4. **The second-step tools.** Phrases per extra in the table, shown on every
   page needing that extra and in the list, or a `:tools:` option written on
   each page. Recommendation: the table, so a tool is stated once.
5. **The ADR.** A new ADR-195 or an amendment. Recommendation: a new one,
   under BUILD; no ADR holds the manual's shape to amend.
6. **The tutorial's declarations, and chapter 10.** Recommendation: every
   chapter declares what its machine needs plus the viewer, so chapters 4
   to 10 name `build123d` and the installation page's tutorial line follows;
   chapter 10 declares its photograph's `openscad` and `web-snapshot` as
   written. Two sentences then disagree with chapter 10's two default
   `machinome snapshot` lines: chapter 1's "The tutorial stays with CadQuery
   so that nothing here needs OpenSCAD" and the installation page's "The
   tutorial's machine is one of those, so you can follow it without
   OpenSCAD". Making chapter 10 photograph through the web viewer alone
   would settle both and drop `openscad` from its
   line; that is a change to the tutorial's teaching, recorded in
   `workflow/warts.md` for the pilot rather than made here.
7. **The manual in the source archive.** Decision 9 of the release note says
   the manual is distributed with the framework's source archive;
   `MANIFEST.in` already leaves out its static files and committed exports,
   and would leave out `docs/_ext/`. Recommendation: not in this cycle; a
   line for `docs/_ext` and `docs/_static` and the exports belongs with the
   release cycle's check of the archives, as the pilot decides.
8. **Proving the tutorial's declarations in the suite.** A test building
   the tutorial with every undeclared node package refused (probe 3, about
   80 s a run), or the derived rule alone, which reads the chapters' code and
   its `Svg` artwork. Recommendation: the derived rule in the suite and the
   builds once in the evidence.
9. **What `none` renders.** Nothing, or "Needs only `pip install
   machinome`". Recommendation: nothing; a reader sees a line only when
   there is something to install.
10. **The viewer on the how-to pages that mention it in passing**
    (`timeline`, `repeat-and-vary`, `several-models`, `markings`).
    Recommendation: no viewer: their jobs are declarations a build and a
    test check; the tutorial and the viewer's own pages, whose steps are in
    the viewer, declare it.
