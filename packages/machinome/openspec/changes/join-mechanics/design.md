## Context

The second cycle of the joins campaign of Machinome 0.9
(`workflow/ongoing/joins-0.9.md` at the repository root, cycle 2, set by the
pilot on 11 October 2026), cut from the line `v0.9-joins` at aa621c90, the
head of `join-freecad`, on the bench
`machinome/WTs/v0.9-joins-join-mechanics`, fast-forwarded on 12 October 2026
to d5d194ad, the line's head after the integration of
`digest-only-what-the-node-names` (ADR-186) and the plan note's entry for
it. The decisions of `monorepo-0.9.md`
still hold, and the joins plan's method: a product is imported by rewriting
its history directly to its final paths and merged with
`--allow-unrelated-histories` by the orchestrator after the planning commit;
one licence at the join; a product that is not an extension package keeps
its record in its directory ("Where a record lives"); the original repository
stays as it is.

The pilot's decisions for this cycle (12 October 2026), settled and not
reopened here:

- **The import is `machinome.mechanics`**, a portion of the `machinome`
  namespace as `machinome.node.freecad` is, in the distribution
  `machinome-mechanics` at `packages/machinome-mechanics/`. Nothing keeps the
  name `machinome_mechanics`: no shim, no alias, no compatibility import. The
  project repositories that import it migrate.
- **Mechanics keeps its own version.** The plan's "One version" rule does not
  apply to it: its manifest stays at 0.1.0, the version on PyPI; its
  `CHANGELOG.md` stays its own, recording the join under "Unreleased"; it
  enters no bumpversion table that would renumber it with the set. What the
  0.9 release does with its number is the pilot's, later.
- **Its manual folds into the one manual**, the framework's, under
  `skills/write-the-manual/SKILL.md`; the separate Read the Docs project is
  retired by the pilot later, and the framework's pages that link it link
  inside the manual instead.
- **Its record stays in its directory**: its specs and archived changes, its
  working record, its tests and its changelog live under
  `packages/machinome-mechanics/`. The manual is the one exception.

machinome-mechanics is the published mechanics helpers: 0.1.0 on PyPI (26
September 2026), import `machinome_mechanics`, twenty-four formulas in nine
family modules over `machinome.math`, a Sphinx manual on its own Read the Docs
project, three specs and fifteen archived changes. Its `main` is at 5fdf732
(44 commits); its branch `v0.8-symbolic-assertions` (and `v0.8`, the same
commit) is at 6588f0c, two commits on `main` never integrated: the ratified
and archived change `symbolic-assertions`, whose tests recognise a symbolic
result by `machinome.expression_graph.symbolic` instead of SolidPython's
`OpenSCADConstant`, a scenario in its `mechanisms` spec, a changelog entry
under "Unreleased", and the release-record test reading past that section.
Every other branch of the product is an ancestor of 6588f0c. Its one tag,
`v0.1.0`, annotated, is on a703d7f, the parent of `main`.

Paths below are the repository's when they start with `packages/` or name a
root file, the framework directory's otherwise. Facts were read on the bench
at aa621c90 and in the product at 5fdf732 and 6588f0c unless marked
*inferred*; probes 4 to 6 and 9 to 11 ran on a scratch clone of aa621c90, and
on d5d194ad none of the 157 joined paths exists in the bench and probe 7 and
probe 9's doctest run give the same counts. Probes ran in the scratch directory
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C2-propose/`
(named `<scratch>` below), never in the bench, the product or a project, with
the bench's synced venv (`<bench>/.venv`, from the lock, carrying
machinome-mechanics 0.1.0 from PyPI through the dev group), uv 0.11.8,
git-filter-repo `ed61b4050b71`, Sphinx 9.1.0 and the OpenSpec CLI.

### What the join touches

- **The product's 169 tracked files** at 6588f0c: `README.md`,
  `CHANGELOG.md`, `pyproject.toml` (version 0.1.0, `machinome>=0.7.0`, `dev`
  and `docs` extras, pytest's `--import-mode=importlib`), `MANIFEST.in`,
  `NOTICE` (the author's name and copyright only), `LICENSE`,
  `context7.json`, `.readthedocs.yaml`, `.github/workflows/ci.yml`,
  `.gitignore`, `scripts/check-dist`; `machinome_mechanics/` (`__init__.py`
  re-exporting the 24 names, nine family modules); `tests/` (16 test modules
  and `tests/pyproject.toml`, a `[tool.machinome]` table making the tests a
  project); `docs/` (`index.rst`, `getting-started.rst`, `conventions.rst`,
  `using-with-machinome.rst`, `reference/` with nine family pages and an
  index, `examples/` with `slider_crank.py`, `gear_phase.py` and a
  `pyproject.toml`, `_static/` with `mechanics.css` and two drawings,
  `conf.py`, `requirements.txt`, `Makefile`); `openspec/` (`config.yaml`, the
  specs `distribution`, `mechanisms` and `user-documentation`, sixteen archived
  changes); `workflow/` (`README.md` and seven notes).
- **History.** Earlier paths exist only in history: `solid_node_mechanics/`
  (renamed to `machinome_mechanics/` on 19 September 2026),
  `docs/extraction.md`, `docs/release-0.1.md` and `docs/validation.md` (moved
  to `workflow/`), and each change under `openspec/changes/<name>/` before its
  archive. 259 paths in all.
- **The licence the product carried** is stated in `LICENSE`, the manifest,
  the README, the module docstring of `__init__.py`, nineteen SPDX lines (the
  ten modules and nine test modules), `openspec/config.yaml`, its
  `distribution` spec, its manual's index page, one bullet of its changelog's
  0.1.0 section, and its archived changes and working notes. `NOTICE` records
  no third-party provenance: the helpers were extracted from the framework's
  own unreleased `machinome.mechanisms` by the same author
  (`workflow/extraction.md`).
- **The core.** `pyproject.toml`'s `mechanics` extra (`"machinome-mechanics"`,
  bare); the root's sources and dev group (`machinome[mechanics]`, which today
  installs 0.1.0 from PyPI); `tests/test_mechanics_boundary.py` (the extra's
  exact list, and a meta-path guard refusing the top-level names
  `machinome_mechanics` and `machinome_mechanisms` from the core);
  `machinome/vet/universe.toml` (`members = ["machinome", "machinome_mechanics",
  "molejo"]`); `docs/conf.py` (`mechanics_version = '0.1.0'`); the manual's
  `start/install.rst`, `reference/api.rst`, `reference/manuals.rst`,
  `concepts/relations.rst`, `howto/timeline.rst` and `project/upgrading.rst`,
  which link `machinome-mechanics.readthedocs.io`; the framework's
  `README.rst`, which links it too; `docs/architecture.md` ("Mechanics
  helpers", the Map's "Mechanics boundary"); ADR-132, "Mechanics helpers
  release independently".

### Probes

1. **The product on the line's core, as it is.** Clones of `main` and of the
   branch under `<scratch>/mech-main` and `<scratch>/mech-branch`, each run
   with `env -C <clone> PYTHONPATH=<clone> <bench>/.venv/bin/python -m pytest
   tests -q -p no:cacheprovider --continue-on-collection-errors`. `main`: 34
   failed, 179 passed, 2 errors, 8 subtests passed. The branch: 38 failed, 179
   passed, 2 errors, 4 subtests passed. Both: the two errors are
   `test_declarative.py` and `test_motion.py` refused at collection by `from
   machinome.node import AssemblyNode` (ADR-181); 34 failures are `TypeError:
   must be real number, not OpenSCADConstant` in `machinome.math`, because
   the tests take their symbolic time from `solid2.get_animation_time()`,
   whose value the core reads as symbolic only after a node package has
   registered its adopter (`openscad-out`, ADR-177), and no test imports one;
   the branch's four more are its predicate answering `None` for the same
   unadopted value.
2. **The smallest port, in scratch only.** `from solid2 import
   get_animation_time` to `from machinome.expression_graph import
   get_animation_time` (twelve lines) and `from machinome.node import
   AssemblyNode` to `from machinome.node.assembly import AssemblyNode` (two
   lines), nothing else. The branch: 201 passed, 24 subtests passed. `main`:
   13 failed, 200 passed, 12 subtests passed, the failures its
   `isinstance(..., OpenSCADConstant)` assertions on a `GraphValue`, which the
   branch's change replaces.
3. **The ported branch on published Machinome 0.8.0.** A throwaway venv
   (`<scratch>/core080-venv`, `machinome==0.8.0` and pytest from PyPI), the
   ported tests at the package's new place (probe 7) with
   `PYTHONPATH=<package directory>`: 195 passed, 24 subtests passed, the two
   pinning modules deselected (6 tests); `machinome.mechanics` resolves from
   the package directory through 0.8.0's `machinome._namespace_portions`.
4. **The import, rehearsed** on a fresh clone (`<scratch>/mechanics-rw`) with
   the command of Decision 2: 46 commits parsed, every branch rewritten,
   `v0.8-symbolic-assertions` at 4d3e075; 45 commits on it, the commit
   "Describe the package for Context7", which touched `context7.json` alone,
   pruned as empty. Its tree holds 157 files (`<scratch>/rehearsal-ls-files.txt`):
   140 under `packages/machinome-mechanics/`, 17 under `packages/machinome/docs/`;
   no commit of any branch touches a path outside `packages/`, and none of
   the 157 exists in the bench. `git log --follow` on
   `packages/machinome-mechanics/machinome/mechanics/belts.py` reaches f8c2cef,
   20 September 2026, the commit that wrote it; `git log` on `gears.py`,
   without `--follow`, reaches b3f5a12, 11 September 2026, the founding commit,
   through the rename of `solid_node_mechanics/`. The tag is
   `mechanics-v0.1.0`, annotated, on 058f0940, the rewritten a703d7f.
5. **The merge, rehearsed** in a scratch clone of the bench's branch
   (`<scratch>/merge-rehearsal`): `git fetch <scratch>/mechanics-rw
   v0.8-symbolic-assertions` and `git merge --allow-unrelated-histories
   FETCH_HEAD`: no conflict, 157 files created, 10075 insertions; `git log
   --follow` on `belts.py` reaches f8c2cefd from the merged tree and `git
   blame` attributes `gears.py`'s copyright line to b3f5a127.
6. **The gates at the join**, the rehearsed merge's tree, fifteen suite
   modules run with the bench's venv from
   `<scratch>/merge-rehearsal/packages/machinome` (49 failed, 188 passed, 1714
   subtests). Red for the join: `test_every_member_is_a_workspace_source`,
   `test_the_readme_links_every_package_and_states_the_licence`,
   `test_every_sibling_is_in_the_table` and
   `test_the_guide_installs_every_member_without_uv` (`test_repository_layout.py`,
   each naming `machinome-mechanics`); `test_every_member_is_numbered_with_the_core`
   (0.1.0), `test_every_pin_between_members_is_compatible` (the core's bare
   `machinome-mechanics` and the product's `machinome>=0.7.0`) and
   `test_the_version_is_bumped_from_the_root` (`test_release_records.py`);
   `test_no_module_outside_the_allowed_zones_holds_the_word`
   (`test_core_names_no_scad.py`: three occurrences, two in `__init__.py`'s
   docstring, one in `linkages.py`'s); and
   `test_no_file_of_the_three_zones_spells_a_former_root_name`
   (`test_node_root_exports_nothing.py`: `tests/test_declarative.py`,
   `tests/test_motion.py`, and the manual's `gear_phase.py` and
   `slider_crank.py`). Every other red of that run is the rehearsal's own
   (the bench venv's editable lines name the bench's directories, so
   `test_each_portion_resolves_from_its_package`, the absent-package doors of
   `test_supported_node_types.py` and the snapshot's refusal read the bench,
   not the clone) and is not counted, as in `join-freecad`'s probe 6.
   `test_mechanics_boundary.py`, `test_machinome_identity.py`,
   `test_vet_universe.py`, `test_kernel_extras.py`, `test_core_kernel_free.py`,
   `test_core_names_no_split_words.py`, `test_docs_structure.py` and
   `test_docs_exports.py` pass on the joined tree.
7. **The tests at their new place.** On the rehearsed merge, the product's
   imports renamed to `machinome.mechanics` and probe 2's fourteen lines
   applied: from `packages/machinome-mechanics` with
   `PYTHONPATH=<that directory>`, `python -m pytest -q -p no:cacheprovider`:
   198 passed, 3 failed, 24 subtests passed; `pytest` alone, and `python -m
   pytest machinome-mechanics/tests` from `packages/`, the same. The three
   failures are the two pinning modules reading the product's former layout
   (`test_documentation.py`'s reference directory, `test_machinome_identity.py`'s
   manifest and `machinome_mechanics/`). The suite's helper import `from
   tests.test_mechanisms import _eval_openscad_expr` resolves under pytest's
   importlib mode although the framework's `tests` package is on `sys.path`
   through its editable line. `python -m pytest --collect-only` from
   `packages/machinome` collects no item of `machinome-mechanics`.
8. **The product's manual, as it is**, built from the branch's clone:
   `sphinx -b html -n -W --keep-going` with Sphinx 9.1.0 and
   `sphinx_rtd_theme` 3.1.0 from a scratch venv (`<scratch>/docs-venv`, the
   framework's `docs/requirements.txt`): exit 0. `sphinx -b doctest -W
   --keep-going` on the bench venv: 151 examples, 10 failures, all in
   `using-with-machinome.rst`, its two example modules importing
   `AssemblyNode` from the node root.
9. **The manual folded in**, the rehearsed merge built with the scratch docs
   venv, `sphinx -b html -n -W --keep-going docs`: exit 1, 22 warnings (three
   pages in no toctree, fourteen links and includes naming the product's
   former layout, two drawings and three downloads not found) and 31 errors,
   each `Unknown directive type "doctest"`. With the edits of Decision 10
   applied in scratch (the extension, the two toctree lines, the section's
   toctree, the relative links, the drawings' and examples' paths, the module
   name): exit 0, no warning. Its doctests, `sphinx -b doctest -W --keep-going`
   on the bench venv with the examples' directory on the path: 141 examples,
   0 failures (151 less the 10 of the two dropped pages). The standard
   library's `doctest.testfile` over the eleven section pages and the how-to
   with Sphinx's default flags (`ELLIPSIS`, `IGNORE_EXCEPTION_DETAIL`,
   `DONT_ACCEPT_TRUE_FOR_1`): 141 attempted, 0 failed; without
   `IGNORE_EXCEPTION_DETAIL`, 1 failed (`cams.rst`, Python 3.12 says
   "division by zero" where the page shows "float division by zero").
10. **The lock.** In the rehearsed merge with the manifest of Decision 3, the
    root's source and the core's extra of Decision 6: `uv lock --offline`:
    "Resolved 188 packages", the same count as the bench's lock; the lock's
    diff is 19 lines: `machinome-mechanics` from the registry with its two
    archives becomes `source = { editable = "packages/machinome-mechanics" }`
    requiring `machinome` from the workspace, and the root's member list gains
    it. uv 0.11.8 does not check a requirement's specifier against a workspace
    member's version: with the core's extra at `machinome-mechanics>0.1.0`
    and, separately, the product at `machinome~=0.9.0`, `uv lock` (offline and
    online) still reported "Resolved 188 packages". What holds the pins is pip
    in `scripts/check-dist` and the release-records test.
11. **pip's choice between two 0.1.0 wheels.** The product's wheel built from
    the rehearsed tree (`<scratch>/wheels/machinome_mechanics-0.1.0-py3-none-any.whl`,
    17 entries: the ten modules under `machinome/mechanics/`, no
    `machinome/__init__.py`, the three licence files; its sdist 213 entries
    with the product's own `MANIFEST.in`). In a venv of the bench's Python
    (pip 24.0, which `scripts/check-dist`'s `python -m venv` provides),
    `pip install --dry-run --no-deps --find-links <scratch>/wheels
    'machinome-mechanics>=0.1.0'` chooses
    `files.pythonhosted.org/.../machinome_mechanics-0.1.0-py3-none-any.whl`,
    the published wheel, whose import is `machinome_mechanics`, not the local
    one (Decision 9).
12. **The projects.** `grep -rl machinome_mechanics` over
    `/home/asa/devel/machinome/projects` (excluding `.git`, `.venv`,
    `node_modules`, `.tools`, `_build*`, `WTs`): 98 files in 27 repositories,
    52 Python and 46 Markdown; the list is
    `<scratch>/projects-grep.txt`. Requirement lines name the distribution,
    not the module: fifteen manifests and requirement files say
    `machinome-mechanics` (bare, `>=0.1` or `>=0.1.0`). The shapes are in
    Decision 16.
13. **Lint.** `flake8 --max-line-length=89` from the framework's directory:
    5 lines on the product's modules, 47 on its tests; `black --check` would
    reformat 5 of its 10 modules. CI's lint reads `../machinome-*/machinome`
    and is `continue-on-error`.
14. **The deltas, archived in scratch.** A copy of the bench's `openspec/`
    with this change's planning artifacts and a one-line tasks file
    (`<scratch>/os-probe`): `openspec archive join-mechanics -y` applies "~ 6
    modified, → 1 renamed" to `framework-identity`, `mechanics-distribution`,
    `user-documentation` and `vet`, and `openspec validate --specs --strict`
    passes 46 of 46. The renamed `user-documentation` requirement is written
    at the end of that spec, after the FreeCAD how-to's.

## Goals / Non-Goals

**Goals:**

- machinome-mechanics joins at `packages/machinome-mechanics/` with its whole
  history, every file at its final path, the merge rehearsed and clean.
- The helpers imported as `machinome.mechanics`, a portion the core admits
  and never imports, installed by `machinome[mechanics]`, at their own
  version, under the set's licence, built and smoked by `scripts/check-dist`.
- Its tests green at their new place on today's core, run by CI and by a
  contributor from its directory; its record kept there and brought current.
- Its manual inside the framework's, by reader intent, every example run.
- The 27 importing repositories on `machinome.mechanics`, the universe sweep
  as it was.

**Non-Goals:**

- Any change to a helper, a signature, a formula, a convention or a domain.
- A new version for the package, its upload, or a compatibility module of the
  former name.
- The upgrading page's 0.9 section (Open Questions 6), the Read the Docs
  project's retirement and any push.
- The joins of the viewer, the videomaker and the studio.

## Decisions

### 1. The join merges `v0.8-symbolic-assertions`, 6588f0c

The branch holds `main` whole and the product's own catch-up to 0.8: the
ratified, archived change `symbolic-assertions`, its spec scenario and its
changelog entry. Probe 2 shows the difference: the same fourteen import lines
leave the branch green (201 passed) and `main` red on the assertions that
change replaces (13 failed). Merging `main` would bring those assertions to be
rewritten by this cycle, outside the product's own record of the decision.
`v0.8` names the same commit; every other branch is an ancestor of it, so the
merge brings the product's whole history. Its two commits are dated 3 October
2026 and keep their dates.

### 2. The mapping and the import

Every tracked file of the product at 6588f0c, and every earlier path, old to
new, or dropped:

| at 6588f0c (and in history) | lands at | reason |
|---|---|---|
| `README.md` | `packages/machinome-mechanics/README.md` | the package's README; rewritten in place by the applier (Decision 3) |
| `CHANGELOG.md` | `packages/machinome-mechanics/CHANGELOG.md` | the product's own changelog, kept whole; gains its Unreleased entry (Decision 12) |
| `pyproject.toml` | `packages/machinome-mechanics/pyproject.toml` | the package's manifest; rewritten in place (Decision 3) |
| `MANIFEST.in` | `packages/machinome-mechanics/MANIFEST.in` | the sdist of a product that keeps its record carries its tests, specs, working record and changelog, as the framework's does; edited in place (Decision 3) |
| `.gitignore` | `packages/machinome-mechanics/.gitignore` | the package's leavings (`.pytest_cache/` from its own runs is not in the root's); edited in place (Decision 3) |
| `machinome_mechanics/` (10 modules), and `solid_node_mechanics/` in history | `packages/machinome-mechanics/machinome/mechanics/` | the portion at its address; both spellings to one path, so a module's history reads there to the founding commit without `--follow` |
| `tests/` (16 modules and `pyproject.toml`) | `packages/machinome-mechanics/tests/` | its record stays in its directory; `tests/pyproject.toml` keeps the tests a project of their own, colliding with nothing there |
| `openspec/` (`config.yaml`, 3 specs, 16 archived changes; each change's earlier path in history) | `packages/machinome-mechanics/openspec/` | its specs and archives stay its record; whole, so every earlier path follows |
| `workflow/` (8 files), and `docs/extraction.md`, `docs/release-0.1.md`, `docs/validation.md` in history | `packages/machinome-mechanics/workflow/` | its working record; the three earlier paths to their later ones, so their history reads at one path |
| `docs/reference/index.rst` | `packages/machinome/docs/reference/mechanics/index.rst` | the section's index, the role it had; rewritten in place (Decision 10) |
| `docs/reference/` (nine family pages) | `packages/machinome/docs/reference/mechanics/` | lookup, the reference section's |
| `docs/conventions.rst` | `packages/machinome/docs/reference/mechanics/conventions.rst` | the key to the family pages' frames, zeros and signs, read beside them |
| `docs/using-with-machinome.rst` | `packages/machinome/docs/howto/mechanism-formulas.rst` | one job, a formula inside a machine's relation law: a how-to |
| `docs/examples/` (`slider_crank.py`, `gear_phase.py`, `pyproject.toml`) | `packages/machinome/docs/howto/mechanism-formulas/` | the how-to's example project, beside its page, as the tutorial's modules sit under `docs/tutorial/counter/`; included and offered for download, never exported (Decision 10) |
| `docs/_static/slider-crank.svg`, `circle-intersection.svg` | `packages/machinome/docs/_static/` | where the manual keeps statics |
| `docs/index.rst` | dropped | its introduction and family table are written into the section's index by the applier, its first example into the how-to; its version note and licence sentence go |
| `docs/getting-started.rst` | dropped | install is the installation page's row, the source build the contributor guide's, the first pose the how-to's, the migration the changelog's (Decision 10); no page of the manual has its role |
| `docs/_static/mechanics.css` | dropped | the manual carries no stylesheet; its rules (table cells wrapping, function entries breaking anywhere) would restyle every table and entry of the whole manual, not the mechanics pages |
| `docs/conf.py`, `docs/Makefile`, `docs/requirements.txt` | dropped | the framework's manual has its own |
| `LICENSE`, `NOTICE` | dropped | one licence at the join; the package links the root's; `NOTICE` records no third-party provenance |
| `context7.json` | dropped | one index per repository; its rules fold into the root's (Decision 12) |
| `.readthedocs.yaml` | dropped | the manual is the framework's; its project is retired by the pilot |
| `.github/workflows/ci.yml` | dropped | the repository's CI runs the tests (Decision 8) |
| `scripts/check-dist` | dropped | the root's builds and smokes every member (Decision 9) |

The import lands files only where the applier would otherwise move them:
README, manifest, `MANIFEST.in` and `.gitignore` in the package's directory,
which the applier edits in place; `docs/reference/index.rst` and
`docs/using-with-machinome.rst` at the pages they become. A move and an edit
never share a commit. A dropped file is absent from every rewritten commit;
the original repository keeps it with the original hashes. The rewritten
commits keep their messages, authors and dates.

The command, run by the orchestrator in a fresh clone (`git clone
file:///home/asa/devel/machinome/machinome-mechanics <dir>`), as rehearsed in
probe 4 (its text is `<scratch>/filter-repo-command.sh`):

```
git filter-repo \
  --path LICENSE --path NOTICE --path context7.json --path .readthedocs.yaml \
  --path .github/ --path scripts/check-dist \
  --path docs/conf.py --path docs/Makefile --path docs/requirements.txt \
  --path docs/index.rst --path docs/getting-started.rst \
  --path docs/_static/mechanics.css \
  --invert-paths \
  --path-rename README.md:packages/machinome-mechanics/README.md \
  --path-rename CHANGELOG.md:packages/machinome-mechanics/CHANGELOG.md \
  --path-rename pyproject.toml:packages/machinome-mechanics/pyproject.toml \
  --path-rename MANIFEST.in:packages/machinome-mechanics/MANIFEST.in \
  --path-rename .gitignore:packages/machinome-mechanics/.gitignore \
  --path-rename solid_node_mechanics/:packages/machinome-mechanics/machinome/mechanics/ \
  --path-rename machinome_mechanics/:packages/machinome-mechanics/machinome/mechanics/ \
  --path-rename tests/:packages/machinome-mechanics/tests/ \
  --path-rename openspec/:packages/machinome-mechanics/openspec/ \
  --path-rename workflow/:packages/machinome-mechanics/workflow/ \
  --path-rename docs/extraction.md:packages/machinome-mechanics/workflow/extraction.md \
  --path-rename docs/release-0.1.md:packages/machinome-mechanics/workflow/release-0.1.md \
  --path-rename docs/validation.md:packages/machinome-mechanics/workflow/validation.md \
  --path-rename docs/reference/index.rst:packages/machinome/docs/reference/mechanics/index.rst \
  --path-rename docs/reference/:packages/machinome/docs/reference/mechanics/ \
  --path-rename docs/conventions.rst:packages/machinome/docs/reference/mechanics/conventions.rst \
  --path-rename docs/using-with-machinome.rst:packages/machinome/docs/howto/mechanism-formulas.rst \
  --path-rename docs/examples/:packages/machinome/docs/howto/mechanism-formulas/ \
  --path-rename docs/_static/:packages/machinome/docs/_static/ \
  --tag-rename ':mechanics-'
```

The drops are matched against the original paths; each rename is an explicit
prefix of the original path, disjoint from the others but for
`docs/reference/index.rst`, which precedes `docs/reference/` and lands at the
same place the prefix would put it. No catch-all `--to-subdirectory-filter`:
part of the product goes to the framework's manual. The commit that touched
only `context7.json` is pruned as empty (probe 4).

**The tag** becomes `mechanics-v0.1.0`, the plan's `--tag-rename` with the
product's name: the framework's tags are its own versions, `v0.1` among
them, so a bare `v0.1.0` in this repository would read as a framework release
of that number. The annotation keeps its text ("machinome-mechanics 0.1.0,
Released with Machinome 0.7.0 on 23 September 2026"); it now points at the
rewritten release commit, whose tree lacks the twelve dropped files.

The orchestrator then checks that `git ls-tree -r --name-only
v0.8-symbolic-assertions` lists the 157 paths of
`<scratch>/rehearsal-ls-files.txt` and that the branch's head is 4d3e075
(*inferred* deterministic: same input, same options); fetches
`v0.8-symbolic-assertions` and the tag
(`refs/tags/mechanics-v0.1.0:refs/tags/mechanics-v0.1.0`) into the bench; and
merges the branch with `git merge --allow-unrelated-histories` into the
cycle's branch, one merge commit, after the planning commit.

### 3. The package's directory

`packages/machinome-mechanics/` after the cycle holds `pyproject.toml`,
`README.md`, `CHANGELOG.md`, `MANIFEST.in`, `.gitignore`, the links
`LICENSE -> ../../LICENSE` and `LICENSES -> ../../LICENSES`, the package
directory `machinome/mechanics/` (its own `__init__.py` and nine modules, no
`__init__.py` at `machinome/`), `tests/`, `openspec/` and `workflow/`.

`pyproject.toml`, replacing the product's (built and locked in probes 10 and
11):

```toml
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "machinome-mechanics"
# Its own version, not the set's (change `join-mechanics`): the root's
# .bumpversion.cfg does not renumber it, and tests/test_release_records.py
# holds it to its CHANGELOG.md and to the manual's mechanics_version.
version = "0.1.0"
description = "The mechanics helpers of Machinome: gear, screw, crank, cam, indexing, delta, linkage, rolling and belt formulas for numeric poses and symbolic motion"
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
    "Topic :: Scientific/Engineering",
]
keywords = ["machinome"]
dependencies = [
    # The core whose machinome.math the formulas compose over and whose path
    # extension admits this portion: Machinome 0.8 or newer, the first whose
    # symbolic value is its own (probe 3: the tests pass on 0.8.0).
    "machinome>=0.8.0",
]

[project.urls]
Homepage = "https://github.com/machinome/machinome"

[tool.setuptools.packages.find]
# The package directory machinome/mechanics/, which has its own __init__.py,
# with none at machinome/, so the core's package path admits it.
include = ["machinome.mechanics"]
namespaces = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--import-mode=importlib"
```

The `dev` and `docs` extras go: the workspace's dev group installs the tools,
and the manual is the framework's. The pytest table stays: it makes the
package's directory the tests' root and selects the import mode probe 7 ran
under.

`README.md`, replacing the product's, in the shape of the ten:

```markdown
# machinome-mechanics

The mechanics helpers of [Machinome](https://github.com/machinome/machinome):
the package `machinome.mechanics`, kinematic formulas for gears, lead screws,
slider-cranks, cams, indexed advance, linear deltas, planar linkages, rolling
motion and belts, each one definition that computes a number for a posed
machine and a deferred expression for a driver or the timeline.

## Install

    pip install "machinome[mechanics]"

## Manual

<https://machinome.readthedocs.io>

## Licence

GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, at the recipient's choice; the
texts are in `LICENSE` and `LICENSES/`.
```

`MANIFEST.in`, edited in place to what is still there:

```
include CHANGELOG.md
recursive-include tests *.py *.toml
recursive-include openspec *.md *.yaml
recursive-include workflow *.md
```

`.gitignore`, edited in place to the package's own leavings (the root's
covers `__pycache__/`, `*.py[cod]`, `build/`, `*.egg-info/`, `WTs/` and
`.venv/`):

```
# This package's leavings the root's .gitignore does not name: its own
# test runs and a local build.
.pytest_cache/
dist/
```

**Headers.** Each of the nineteen `SPDX-License-Identifier` lines (the ten
modules and nine test modules) becomes `# SPDX-License-Identifier:
GPL-2.0-or-later OR CERN-OHL-S-2.0+`; the copyright lines stay as they are,
and a file with no header gains none, so `git blame` keeps every other line.

### 4. The source at its address

- **Internal imports.** `__init__.py`'s nine lines `from machinome_mechanics.<family>
  import ...` and `belts.py`'s `from machinome_mechanics.rolling import
  rolling_angle` become `from machinome.mechanics.<family> import ...`; the
  name has the same length, so no continuation line moves.
- **`__init__.py`'s docstring**, whose first paragraph names the import, the
  licence and an independent package, and whose second names a deferred
  OpenSCAD expression (probe 6). Its first two paragraphs become:

  ```
  """The mechanics helpers: kinematic formulas for machinome projects.

  Import them from `machinome.mechanics`, or from its family modules
  (`machinome.mechanics.gears` and the others). The framework's `mechanics`
  extra installs them; the framework itself never imports them.
  ```

  and, in the paragraph "**Two faces, from `machinome.math`.**", the sentence
  "So it computes a number when the node is posed at a keyframe, and builds
  the equivalent deferred OpenSCAD expression when its driving argument is
  animation time or a driver symbol -- the same function either way, just
  deferred. Nothing here emits an OpenSCAD builtin `machinome.math` does not
  already emit, so the cross-runtime parity corpus covers this package
  without extension." becomes "So it computes a number when the node is posed
  at a keyframe, and builds the equivalent deferred expression when its
  driving argument is animation time or a driver symbol -- the same function
  either way, just deferred. Nothing here emits a function `machinome.math`
  does not already emit, so the cross-runtime parity corpus covers this
  package without extension." The rest of the docstring is unchanged.
- **`linkages.py`'s docstring**: "evaluates to NaN symbolically, exactly as
  OpenSCAD and the viewer do." becomes "evaluates to NaN symbolically, as
  every runtime that evaluates the expression does."

The word the core-names gate refuses then stands in no module of the package,
which is not of the OpenSCAD family; the gate's allowed zones are unchanged.

### 5. The pins, the workspace and the bench venv

- The package requires `machinome>=0.8.0`: the floor of what it needs (the
  core's `machinome.math` over its own symbolic value, and the root path
  extension that admits the portion when it is installed apart), proved by
  probe 3 on published 0.8.0; open above, so the set's renumbering at 0.9
  needs no edit of a package whose version the set does not move.
- The core's extra becomes `mechanics = ["machinome-mechanics>=0.1.0"]`: the
  package's own version as the floor, which the member in the tree satisfies.
  The floor cannot exclude the published 0.1.0, whose import is
  `machinome_mechanics`, while the member is numbered 0.1.0; the release that
  publishes the joined package moves both its version and this floor past it
  (Open Questions 3).
- Neither pin is `~=` and neither is in `.bumpversion.cfg`: the pins of the
  one-version set are `~=<version>` both ways and move with it, and this
  package is outside the set by the pilot's decision. uv does not check
  either specifier against the member's version (probe 10); pip does, in
  `scripts/check-dist`, and `tests/test_release_records.py` holds them
  (Decision 7).
- The root's `pyproject.toml` gains `machinome-mechanics = { workspace = true }`
  between `machinome-engine-mesh` and `machinome-node-build123d`; the dev
  group `["machinome[dev]", "machinome[mechanics]"]` and its comment stay, the
  extra now resolving to the member. Its comment's "the mechanics package the
  catalogue's projects import" stays true.
- The applier then runs `uv lock` (expected: "Resolved 188 packages", the
  diff of probe 10) and `uv sync --python 3.12` (expected: thirteen
  `__editable__` `.pth` files, the new one holding
  `<bench>/packages/machinome-mechanics`; uv uninstalls the PyPI 0.1.0, whose
  `site-packages/machinome_mechanics/` goes with it). Then, from `/tmp`, the
  bench venv's Python prints `machinome.mechanics.__file__` under the bench's
  package directory and `import machinome_mechanics` raises
  `ModuleNotFoundError`.

### 6. The core

- **The extra**, as Decision 5 states, with its comment: "`machinome.mechanics`,
  the mechanics helpers, the repository's distribution machinome-mechanics at
  its own version; the framework never imports them."
- **`tests/test_mechanics_boundary.py`.** `test_only_the_mechanics_extra_installs_helpers`
  expects `["machinome-mechanics>=0.1.0"]`. The guard of
  `test_math_and_motion_work_with_helpers_refused` refuses a name equal to
  `machinome.mechanics` or beginning `machinome.mechanics.`, as well as the
  two former top-level names. A new test,
  `test_the_guard_refuses_the_helpers_address`, runs the same guard and
  `import machinome.mechanics` in a subprocess and expects exit 1 with
  "framework imported helpers: machinome.mechanics" in its output: the
  positive control that the guard watches the dotted name. Red before the
  guard's edit: the import succeeds under a guard that reads only the first
  component (`machinome`). The docstring names the change.
- **`tests/test_machinome_identity.py`** needs no edit: it reads each extra's
  requirement name, and `Requirement("machinome-mechanics>=0.1.0").name` is
  `machinome-mechanics` (the `framework-identity` scenario "The extras keep the
  Machinome name under a version floor").
- **The layout gate**, `tests/test_repository_layout.py`. A product that keeps
  its record in its directory is neither an extension package nor the
  framework, so the gate gains a third table rather than stretching
  `EXTENSIONS`, whose test pins an extension package's four entries:

  ```python
  #: The products of the repository that keep their record in their own
  #: directory, by directory: the address of the package directory they
  #: ship, the core's extra that installs it, and the entries the directory
  #: holds beside the package (`join-mechanics`).
  PRODUCTS = {
      'machinome-mechanics': ('machinome.mechanics', 'mechanics',
                              ('.gitignore', 'CHANGELOG.md', 'LICENSE',
                               'LICENSES', 'MANIFEST.in', 'README.md',
                               'machinome', 'openspec', 'pyproject.toml',
                               'tests', 'workflow')),
  }
  ```

  A new class, `TheProductsTest`: each product's directory holds exactly those
  top-level entries (tracked and untracked, ignored leavings excepted), the
  two links resolve to the root's, `machinome/` holds no `__init__.py` and the
  package directory holds its own; its manifest names it, states the core's
  licence expression and files, and includes the package with `namespaces =
  true`; its README names `pip install "machinome[<extra>]"` and the licence;
  its package resolves from its directory on the workspace venv; its tests
  are a directory with a `pyproject.toml` and an `openspec/specs/`. Red at the
  join: the manifest (the former licence, `include`), the README, the links,
  the entries (`LICENSE` a file, no `LICENSES`), the resolution (the PyPI
  0.1.0 does not provide the address). `test_every_sibling_is_in_the_table`
  accepts a directory of `EXTENSIONS` or `PRODUCTS`.
  `TheIndexTest.test_context7_is_the_repository_s` accepts an excluded folder
  under a product's directory. `TheContinuousIntegrationTest` gains
  `test_the_test_job_runs_each_product_s_tests` (Decision 8). The module's
  docstring gains the sentence naming the products and the change.
- **The release records**, `tests/test_release_records.py`: a module
  constant `OWN_VERSION = ('machinome-mechanics',)`, the members the set does
  not number, with its comment citing the pilot's decision of 12 October 2026
  and ADR-187. `test_every_member_is_numbered_with_the_core` and
  `test_the_version_is_bumped_from_the_root` skip them;
  `test_every_pin_between_members_is_compatible` holds `~=<version>` between
  two members of the set and, for a requirement on or from a member of its own
  version, a floor `>=` that the required member's version in the tree
  satisfies. A new test, `test_a_member_of_its_own_version_is_outside_the_bump`:
  no table of `.bumpversion.cfg` names its manifest, its version equals the
  version of the first release section of its `CHANGELOG.md` (the first
  `## ` heading that is not `Unreleased`, which begins with the version) and
  the manual's `mechanics_version`. The docstring's "Every package of the
  repository carries the framework's version" gains "but the mechanics
  helpers, which carry their own (change `join-mechanics`)".
- **`.bumpversion.cfg`**: no table for `packages/machinome-mechanics/pyproject.toml`.
  Its pins table searches `~={current_version}"`, which the package's
  `machinome>=0.8.0` does not match. The applier proves both on a copy (task
  8.2).
- **The vet universe**, `machinome/vet/universe.toml`: `members =
  ["machinome", "molejo"]`. `machinome.mechanics` lies beneath `machinome`, a
  member allowed whole, so a project importing it is pure without a line of
  its own; `machinome_mechanics` is then a name the set does not install, and
  a project importing it is `outside-universe`, as the declaration's own
  comment on `shapely` requires (a member the framework does not install
  would let a project pass vet and fail at import). The universe's `version`
  is unchanged. `tests/test_vet_universe.py`'s `test_the_contract` expects
  `('machinome', 'molejo')`, and a new test,
  `test_the_mechanics_helpers_are_inside_and_their_former_name_outside`,
  vets a scratch project importing `from machinome.mechanics import
  meshed_angle` (pure) and one importing `from machinome_mechanics import
  meshed_angle` (`outside-universe machinome_mechanics`).

### 7. What holds the version and the pins

The pilot's decision puts one member outside the set's version; the tests say
where. `test_release_records.py` (Decision 6) holds: the member's version is
its changelog's released version and the manual's `mechanics_version`; no
bumpversion table names it; its requirement on the core and the core's extra
on it are floors the tree satisfies. The `framework-identity` delta states the
exception in the one-version requirement, and ADR-187 records why.

### 8. CI

The `test` job of `.github/workflows/python-app.yml` gains, after "Run tests":

```yaml
      # The mechanics helpers keep their tests in their own directory
      # (change `join-mechanics`); the workspace synced above installs them.
      - name: Run the mechanics package's tests
        working-directory: packages/machinome-mechanics
        run: python -m pytest
```

A step, not a job: it reuses the job's synced workspace, and the gate that
pins every job's default directory to `packages/machinome` stays as it is. The
new layout test reads the `test` job's steps and requires, for each product,
a step whose `working-directory` is `packages/<product>` and whose `run`
invokes pytest. Lint already reads `../machinome-*/machinome`. The core's
suite does not collect the package's tests (probe 7); its `coverage run
--source machinome` measures the core's run alone.

A contributor runs them with `env -C packages/machinome-mechanics python -m
pytest`, or `cd packages/machinome-mechanics && pytest`, on the synced venv;
`CONTRIBUTING.rst` says so (Decision 12).

### 9. `scripts/check-dist`: one row, installed from its wheel

The product's own `check-dist` is dropped; the root's builds every member
(probe 11: 17 wheel entries) and needs a row, or it fails "machinome-mechanics
has no smoke in scripts/check-dist". The row has no `through`: probe 11
shows pip 24.0, the venv's, choosing the published 0.1.0 over the built one
for `machinome-mechanics>=0.1.0`, so installing through the extra would smoke
the wrong package. Without `through`, `main` installs the wheel by its path,
which pip takes as given; the smoke then proves the extra's requirement from
the core's metadata. The row, after the FreeCAD package's, the version read
once at the top of the script beside `ROOT`:

```python
#: The mechanics helpers' own version (change `join-mechanics`): they are
#: not numbered with the set.
MECHANICS_VERSION = tomllib.loads(
    (ROOT / 'packages/machinome-mechanics/pyproject.toml').read_text()
)['project']['version']
```

```python
    'machinome-mechanics': {
        # Installed from its wheel by path, not through `machinome[mechanics]`:
        # the index serves another wheel of the same version, whose import is
        # the former one, and pip may take it.
        'extras': [],
        'code': f'''
import importlib.metadata as metadata
from pathlib import Path
import machinome.mechanics as mechanics
from machinome.expression_graph import get_animation_time, symbolic
distribution = metadata.distribution('machinome-mechanics')
assert distribution.version == {MECHANICS_VERSION!r}, distribution.version
files = [str(path) for path in distribution.files]
shipped = sorted(path for path in files
                 if path.startswith('machinome/') and path.endswith('.py'))
assert shipped == [f'machinome/mechanics/{{module}}.py' for module in (
    '__init__', 'belts', 'cams', 'cranks', 'deltas', 'gears', 'indexing',
    'linkages', 'rolling', 'screws')], shipped
owned = Path(distribution.locate_file(shipped[0])).resolve()
assert owned == Path(mechanics.__file__).resolve(), (owned, mechanics.__file__)
assert owned.is_relative_to(Path(VENV).resolve()), owned
assert 'machinome>=0.8.0' in distribution.requires, distribution.requires
core = metadata.requires('machinome')
assert any(line.startswith('machinome-mechanics>={MECHANICS_VERSION}')
           and 'mechanics' in line.partition(';')[2] for line in core), core
assert len(mechanics.__all__) == 24, mechanics.__all__
assert mechanics.screw_travel(360, 2) == 2
assert mechanics.piston_height(0, 15, 60) == 75
assert mechanics.meshed_angle(0, 12, 24, driver_gap=15) == 172.5
height = mechanics.piston_height(get_animation_time(), 15, 60)
assert symbolic(height) is not None, height
'''
        + LICENCES.substitute(name='machinome-mechanics')
        + '''
print('machinome-mechanics', distribution.version, 'module',
      mechanics.__file__, 'numeric and symbolic')
''',
        'commands': [],
    },
```

The count 24 is the package's `__all__`, which the manual's reference test
holds to one entry each; the smoke checks the installed package carries the
same. Red first: before the row, the script fails naming the package. The
license check is the extension packages' template, unchanged.

### 10. The manual

By reader intent, under `skills/write-the-manual/SKILL.md`:

| page | section | from |
|---|---|---|
| `reference/mechanics/index.rst`, "Mechanics helpers" | Reference, after `reference/sphinx` | the product's reference index, with its landing page's introduction and family table |
| `reference/mechanics/conventions.rst`, "Units, frames and valid poses" | the section's first entry | `conventions.rst` |
| `reference/mechanics/{gears,screws,cranks,cams,indexing,deltas,linkages,rolling,belts}.rst` | the section, in that order | the nine family pages |
| `howto/mechanism-formulas.rst`, "Use a mechanism formula in a machine" | How-to guides, after `howto/freecad-assemblies` | `using-with-machinome.rst`, with the first pose of `getting-started.rst` and of the landing page |

- **One section for the reference**, its index listing the conventions page
  and the nine families: the family pages answer one lookup each and share
  one module and one set of conventions, and a reader looking for a helper
  opens the Reference section and finds "Mechanics helpers" beside the API.
  Nine sibling pages directly under `reference/` would bury `cli`, `api` and
  `assertions` among formula families.
- **The section's index**, rewritten in place: the title "Mechanics helpers";
  the landing page's two paragraphs on what the helpers are and who supplies
  what, its links made `:doc:` links; one sentence "The helpers are the
  package ``machinome-mechanics`` |mechanics_version|, installed by
  ``machinome[mechanics]`` and imported from ``machinome.mechanics`` or its
  family modules; the framework never imports them. All angles are degrees;
  lengths use one consistent unit per calculation. Read
  :doc:`conventions` before adapting a law to another machine."; the
  landing page's family table ("Find the formula you need"), its links
  relative; the reference index's `.. py:module:: machinome.mechanics` and its
  helper table; the toctree `conventions` then the nine families. No version
  note, no licence sentence, no doctest (the how-to carries the first
  example).
- **The how-to**, converted in place from `using-with-machinome.rst`: an
  opening that installs (`pip install "machinome[mechanics]"`) and imports
  (`from machinome.mechanics import screw_travel, piston_height,
  meshed_angle`), with the landing page's three-line example and
  `getting-started.rst`'s quarter-turn screw as doctests; then its own
  sections unchanged in substance ("Connect an input to a joint", "Symbolic
  inputs", "Static calculations from declared parameters"), the three
  includes and downloads naming `mechanism-formulas/...`, the framework links
  `:doc:` links (`/concepts/relations`, `/concepts/values`,
  `/reference/mechanics/index`, `/reference/mechanics/cranks`). The examples
  import `AssemblyNode` from `machinome.node.assembly` and the helpers from
  `machinome.mechanics`.
- **The family and conventions pages**: `machinome_mechanics` becomes
  `machinome.mechanics` in each `py:currentmodule`, "Import from" sentence and
  doctest; `:doc:` links become section-relative (`conventions`, `<gears>`,
  `/howto/mechanism-formulas`); the two figures name `/_static/<drawing>.svg`;
  the conventions page's link to the assertions reference becomes
  `:doc:`/reference/assertions``. No other line changes.
- **`docs/conf.py`**: `extensions` gains `'sphinx.ext.doctest'`, part of
  Sphinx, which renders the `.. doctest::` blocks in the HTML build and lets a
  maintainer run `-b doctest`; `docs/requirements.txt` is unchanged and the
  build still imports nothing. `mechanics_version` stays the one statement of
  the helpers' version, its comment "the mechanics helpers' own version,
  `packages/machinome-mechanics/pyproject.toml`, which
  tests/test_release_records.py holds to it": a package with its own number
  is a fact the core's `|release|` does not imply, read on the installation
  page and the section's index.
- **`start/install.rst`**: the paragraph "Two more extras exist" says
  ``mechanics`` installs the :doc:`mechanics helpers
  </reference/mechanics/index>`, ``machinome.mechanics``, gear, screw, crank,
  cam, delta, linkage, rolling and belt formulas (the distribution
  ``machinome-mechanics``, version |mechanics_version|); "Packages and
  licences" names ``machinome-mechanics`` after the node packages, under the
  same licence. The count "twenty-four" goes (rule 6: a count is derived or
  not stated).
- **`reference/api.rst`**, "Mechanics helpers": the gear, screw, crank, cam,
  indexing, delta, linkage, rolling and belt formulas are the package
  ``machinome-mechanics`` |mechanics_version|, installed by
  ``machinome[mechanics]`` and imported from ``machinome.mechanics``;
  :doc:`/reference/mechanics/index` documents every signature, parameter,
  return value, convention and domain, and :doc:`/howto/mechanism-formulas`
  a worked piston law with the limit on dimensional class-body formulas;
  ``machinome.mechanisms`` is no longer a framework API; see
  :doc:`/concepts/relations`. The count goes.
- **`concepts/relations.rst`** and **`howto/timeline.rst`**: each link to the
  separate manual becomes `:doc:`/reference/mechanics/index``, the words around
  it "the mechanics helpers" rather than the product's name.
- **`reference/manuals.rst`**: the opening says the viewer releases with
  Machinome and has a manual of its own, as do the libraries below; the
  Machinome Mechanics entry goes, replaced by one line under the opening, "The
  mechanics helpers are documented in this manual, under
  :doc:`/reference/mechanics/index`."
- **`project/upgrading.rst`**: its 0.7 paragraph keeps its words, which were
  true of 0.7; its link to the separate manual becomes `:doc:`the mechanics
  helpers </reference/mechanics/index>``, so no page links a project the pilot
  retires. No section for the rename is written in this cycle (Open Questions
  6); `project/status.rst`, `project/changelog.rst`'s released sections and
  `releases/` keep their history as written.
- **The proof of the examples**: the package's `tests/test_documentation.py`
  runs every `>>>` example of the section's eleven pages and the how-to with
  the standard library's `doctest`, the how-to's example directory on the
  path, under Sphinx's default flags (probe 9: 141 examples, 0 failures); the
  manual's own build, which installs `docs/requirements.txt` alone, runs none.

### 11. The tests at their new place

- **Imports.** In the package's tests, `machinome_mechanics` becomes
  `machinome.mechanics` (`from ... import`, `import machinome.mechanics as
  mechanics`); probe 2's fourteen lines move the symbolic time to
  `machinome.expression_graph.get_animation_time` and `AssemblyNode` to
  `machinome.node.assembly`. `test_mechanisms.py`'s docstring
  "machinome_mechanics: the textbook mechanism laws..." names
  `machinome.mechanics`. No other line of the fifteen formula and integration
  modules changes.
- **`tests/test_documentation.py`**, rewritten for the new place:
  `REPOSITORY = Path(__file__).resolve().parents[3]`, the section
  `packages/machinome/docs/reference/mechanics`, the how-to
  `packages/machinome/docs/howto/mechanism-formulas.rst` and its examples
  directory; the reader-facing pages are those twelve pages, the package's
  `README.md` and its modules. Its tests:
  `test_every_export_has_one_reference_with_the_actual_signature` (the
  section's pages); `test_the_changelog_states_the_release` (the first release
  section's heading begins with `0.1.0`, is dated 23 September 2026 and the
  section names Machinome 0.7.0, one
  `Unreleased` section may stand above it, the manifest's version is that
  release's; the README states no version); `test_no_reader_page_states_a_publication_caveat`
  (the five phrases, over the reader pages);
  `test_the_pages_link_inside_the_manual` (no section page, how-to or module
  names `readthedocs.io`; the README's one manual link is
  `https://machinome.readthedocs.io`); `test_the_reference_names_no_consumer_projects`
  (the list kept); `test_every_example_in_the_manual_runs` (Decision 10's
  doctest run: at least one example on each page but the index, none failed).
  Red at the join: the reference directory is absent at the old path; the
  pages import `machinome_mechanics`, which after the sync no module provides;
  the how-to's examples import from the node root; the pages link the
  framework's manual on Read the Docs.
- **`tests/test_machinome_identity.py`**, rewritten: the manifest's name,
  `dependencies == ['machinome>=0.8.0']`, `license` the set's expression and
  `license-files` the set's, Homepage `https://github.com/machinome/machinome`,
  `include == ['machinome.mechanics']` with `namespaces = true`;
  `machinome/mechanics/__init__.py` a file and `machinome/__init__.py` absent;
  no `machinome_mechanics/` or `solid_node_mechanics/` directory; every module
  imports from `machinome` and none from `machinome_mechanics` or
  `solid_node`; `machinome.mechanics.__file__` resolves under the package's
  directory. Red at the join on each of those but the last two.

### 12. The records

- **`HISTORY.rst`**, at the end of `Unreleased`, after the digest bullet:

  ```
  * **The mechanics helpers join the repository.** machinome-mechanics,
    published as 0.1.0 from a repository of its own, is the package
    ``machinome-mechanics`` at ``packages/machinome-mechanics/``, its history
    kept: its helpers are imported from ``machinome.mechanics`` (formerly
    ``machinome_mechanics``, which nothing provides any more) and installed
    by ``pip install "machinome[mechanics]"``, with names, signatures and
    formulas unchanged. It keeps its own version, its changelog, its specs
    and its tests in its directory, and its manual is part of this one.
    Change ``join-mechanics`` (ADR-187).
  ```

- **`docs/project/changelog.rst`**, at the end of `Unreleased`, after the
  digest bullet:

  ```
  * **The mechanics helpers are part of this manual.** Import them from
    ``machinome.mechanics`` (formerly ``machinome_mechanics``); names,
    signatures and formulas are unchanged, and ``pip install
    "machinome[mechanics]"`` installs them
    (:doc:`/reference/mechanics/index`, :doc:`/howto/mechanism-formulas`).
  ```

- **The product's `CHANGELOG.md`**, its `## Unreleased` section (the branch's
  bullet kept first) gains:

  ```
  - Machinome Mechanics is part of the Machinome repository,
    <https://github.com/machinome/machinome>, at
    `packages/machinome-mechanics/`, with its history. The helpers are
    imported from `machinome.mechanics` (formerly `machinome_mechanics`), a
    portion of the `machinome` package; names, signatures and formulas are
    unchanged, and no module of the former name is provided. The package is
    licensed as every package of the repository, GPL-2.0-or-later or
    CERN-OHL-S-2.0-or-later, at the recipient's choice, and requires
    Machinome 0.8 or newer. Its manual is part of Machinome's,
    <https://machinome.readthedocs.io>: "Mechanics helpers" under Reference
    and "Use a mechanism formula in a machine" among the how-to guides.
  - The tests take their symbolic time from
    `machinome.expression_graph.get_animation_time()` and import
    `AssemblyNode` from `machinome.node.assembly`. The specifications name the
    new import and the manual's address, with no change of behaviour.
  ```

  The 0.1.0 section's identity bullet names the licence the product carried;
  Open Questions 5.
- **`CREDITS.md`**: unchanged. The product's `NOTICE` names its author and
  copyright alone; the helpers were extracted from the framework's own
  formulas, and no third party's work is called, adapted or retained.
- **`docs/architecture.md`**: the section "Mechanics helpers (independent
  package · spec `mechanics-distribution`)" becomes "Mechanics helpers (the
  distribution `machinome-mechanics` · spec `mechanics-distribution`)", its
  first paragraph saying the formulas live in the repository's
  `packages/machinome-mechanics/`, imported as `machinome.mechanics`, at their
  own version, with their tests, specs and working record in that directory
  (ADR-132, ADR-187), and its last sentence's `machinome_mechanics` becoming
  `machinome.mechanics`; the extras sentence gains "`[mechanics]` for the
  mechanics helpers (the distribution `machinome-mechanics`, at its own
  version)"; the Map's "Mechanics boundary" row becomes "Mechanics helpers,
  the distribution `machinome-mechanics`" | "the repository's
  `packages/machinome-mechanics/` (`machinome/mechanics/`: `__init__.py` and
  the nine family modules; its own `tests/`, `openspec/` and `workflow/`)" |
  `mechanics-distribution` | "022, 076, 132, 187".
- **The root `README.md`**: a row after the FreeCAD package's:
  ``| [`machinome-mechanics`](packages/machinome-mechanics/) | The mechanics helpers, `machinome.mechanics`: gear, screw, crank, cam, delta, linkage, rolling and belt formulas for numeric poses and symbolic motion; installed by `machinome[mechanics]`. |``
- **`packages/machinome/README.rst`**: the sentence "``mechanics`` installs
  `Machinome Mechanics <https://machinome-mechanics.readthedocs.io>`_, an
  independent package of gear, screw, cam, belt and linkage formulas." becomes
  "``mechanics`` installs ``machinome.mechanics``, the gear, screw, cam, belt
  and linkage formulas." Nothing else (its `ReadmeTest`).
- **`CONTRIBUTING.rst`**: the pip block gains `-e
  packages/machinome-mechanics \` before the framework's line; "Running tests"
  gains one sentence after the suite's command: "The mechanics helpers keep
  their tests in their own directory: run ``python -m pytest`` from
  ``packages/machinome-mechanics``."
- **`context7.json`**: `excludeFolders` gains
  `packages/machinome-mechanics/openspec`, `packages/machinome-mechanics/tests`
  and `packages/machinome-mechanics/workflow`; `rules` gains one, folding the
  product's: "The mechanics helpers are machinome.mechanics, installed by pip
  install \"machinome[mechanics]\" (the distribution machinome-mechanics, at
  its own version): gear, screw, crank, cam, indexing, delta, linkage, rolling
  and belt formulas. Angles are degrees. Each helper accepts numbers and the
  framework's symbolic values, so one formula serves a numeric pose and a
  relation law, for example crank.turn.drives(piston.rise, law=piston_law)
  where the law calls piston_height. The package supplies formulas only; the
  project supplies dimensions, reference frames, signs, branch selection and
  assembly facts; the framework never imports the helpers."
- **`AI-USE.md`**: machinome-mechanics leaves both mentions of the sibling
  repositories, and the paragraph on what is agent-written gains "and the
  mechanics helpers under `packages/machinome-mechanics/`, founded in a
  repository of their own after the line and joined here with their history"
  after the framework's records.
- **ADR-187** (recommended, Open Questions 2),
  `docs/adrs/BUILD/ADR-187-the-mechanics-helpers-are-a-portion-of-the-repository-at-their-own-version.md`,
  Status Proposed, Change `join-mechanics`, Supersedes ADR-132's import path
  and repository, Amends ADR-182 (a product keeps its record in its
  directory) and ADR-183 (a member of the repository not numbered with the
  set, outside `.bumpversion.cfg`, smoked from its wheel), Related to ADR-076,
  ADR-149 and ADR-170. Context: the pilot's three decisions; probes 1 to 3, 10
  and 11. Options: (1) a portion of the `machinome` namespace at its own
  version, its record in its directory (chosen); (2) the set's version, 0.8.1
  now and renumbered with the set (refused by the pilot); (3) the import
  `machinome_mechanics` kept (refused by the pilot); (4) an extension package
  whose record folds into the framework's (refused by the plan: a product
  keeps its record); (5) installed through the extra in `check-dist` (refused
  by probe 11). Decision: Decisions 3 to 9. Consequences: good, one address
  `machinome.mechanics`, one install line, one manual whose examples run; bad,
  the extra admits the published 0.1.0 of the former import until a release
  moves both past it, uv does not check the two floors, and 27 project
  repositories rename an import; neutral, the core never imports it, as
  before. Index line under BUILD after ADR-183 (ADR-186 stands under NODE);
  ADR-132's status and index line note "import path and repository
  superseded by 187"; ADR-182 and ADR-183 gain the dated
  consequence "Neutral (2026-10-12, `join-mechanics`): a product of a
  repository of its own may join with its record in its directory and its
  own version (ADR-187)", and their status and index lines "amended by 187".
- **The plan's progress** (`workflow/ongoing/joins-0.9.md`, "Progress"): the
  cycle's entry at its close.

### 13. The product's record, brought current in place

The product's specs, archived changes and notes are its record (the pilot's
decision). The applier edits, in place and with no change of behaviour:

- `openspec/specs/mechanisms/spec.md`: `Code: machinome_mechanics/` becomes
  `Code: machinome/mechanics/`; `machinome_mechanics` becomes
  `machinome.mechanics` in the five requirements that name the import.
- `openspec/specs/distribution/spec.md`: its Purpose says the helpers are a
  package of the Machinome repository; "Helpers depend on the framework"
  says the distribution exposes `machinome.mechanics` under the repository's
  licence, declares `machinome>=0.8.0` and uses `machinome.math`; the
  scenario "Install a built distribution" names Machinome 0.8 and
  `machinome.mechanics`; "The release pair is legible" stays a record of the
  0.1.0 release.
- `openspec/specs/user-documentation/spec.md`: "User documentation is readable
  and independently hosted" says the manual is the mechanics section and
  how-to of the Machinome manual, built with it, and that `workflow/` keeps
  the internal records; its scenario's words follow; the requirement's title
  stays, since its spec has no change to record a rename.
- `openspec/config.yaml`: its context says the helpers are the repository's
  package `machinome.mechanics` under the repository's licence, depending on
  machinome and using `machinome.math`, and that machinome never imports it.
- `workflow/README.md` and `workflow/documentation.md`: the maintainer notes
  in force; `documentation.md` says the pages are in the framework's manual
  (`packages/machinome/docs/reference/mechanics/` and the how-to), built with
  it, and that `tests/test_documentation.py` runs their examples; the Read the
  Docs section goes. The other six notes are records of their day and stay as
  written.

The alternative, a second OpenSpec change in the product's records, would
record a rename and an address as a behaviour change; the product's changelog
entry says what changed. The archived changes stay as written.

### 14. The spec deltas

- `mechanics-distribution`: MODIFIED "Framework independence from mechanics
  helpers" (the repository's distribution, the address, the extra's floor;
  the guard on the dotted name; scenario titles kept, two new).
- `framework-identity`: MODIFIED "Extras select independent Machinome
  products" (the mechanics extra selects the repository's distribution; the
  scenario "A user installs the mechanics extra" restated) and "The framework
  is the package directory `packages/machinome` of a monorepo" (products that
  keep their record; the one-version rule's exception; the sibling table;
  three new scenarios).
- `vet`: MODIFIED "The universe is a versioned declaration shipped with the
  framework" (the contract tier; one new scenario).
- `user-documentation`: RENAMED "Mechanics users can reach the independent
  helper manual" to "The mechanics helpers are documented in the manual", and
  MODIFIED under the new title (scenario titles kept, two new).
- `framework-contributor-guidance`: MODIFIED "The contributor guide states
  the monorepo's development setup" (the pip command names the mechanics
  directory; the guide says where its tests run; one new scenario).

Each MODIFIED requirement is copied whole from its baseline and edited;
every existing scenario keeps its title.

### 15. Workspace follow-ups, outside this repository

Listed for the orchestrator; none is done by this cycle:

- the studio's `machinome-studio/shop-skills/machinome-api/SKILL.md` and the
  workspace's `scripts/migrate-projects-to-machinome`, which name
  `machinome_mechanics`;
- `scripts/load-projects.d/join-mechanics.toml`, `[[moved]] name =
  "machinome_mechanics"`, `to = "machinome.mechanics"`, so a sweep between
  the implementation and the projects' move reads their rows as expected;
- the operating contract's status paragraph on `machinome-mechanics` (an
  independent repository) and `docs/collaborator-setup.md` and
  `scripts/setup`, which clone and install the product's repository; at the
  campaign's close, as the plan says.

### 16. The projects' move (the orchestrator's, after the implementation)

- **The rule.** In each repository, on a branch of the orchestrator's choosing
  under its own process: in every Python module the project's models, tests
  and tools import, `from machinome_mechanics import` and `from
  machinome_mechanics.<family> import` become `from machinome.mechanics import`
  and `from machinome.mechanics.<family> import`; `machinome_mechanics.<name>`
  in a docstring or comment becomes `machinome.mechanics.<name>`, and the path
  `machinome_mechanics/<family>.py` becomes `machinome/mechanics/<family>.py`;
  the README sentences that show the import as current do the same
  (`3D-Printers/kossel/README.md`, `3DPrintedClocks/simulation/README.md`).
- **What it leaves.** The verification records under each `docs/` (46
  Markdown files and Thor's `docs/verify_belt_path_metrics.py` and
  `docs/verify_belt_tangent_points.py`, which reproduce a recorded comparison
  and print the helper's file); tools pinned to a framework revision
  (`Lab-Equipment/science-jubilee/simulation/tools/run_frame_audit.py`, pinned
  at aabddc39); requirement lines, which name the distribution
  `machinome-mechanics` and stay valid as names (which published version
  carries the address is the release's); archived evidence directories,
  worktrees, other branches.
- **The repositories**: Metamaquina2, Prusa3-vanilla, fender-bender,
  hangprinter, kossel, snappy-reprap, 3DPrintedClocks, OpenCycloid,
  OpenTorque-Actuator, open_robot_actuator_hardware, Pascaline-module,
  CycloidalDrive, openflexure-microscope, science-jubilee, Leonardo,
  Vault_with_combination_lock, Thor, Inmoov-sim, AlbertPro, ZeroBug,
  hexapod_spiderbot_model, Leonardo-hydraulic-sawmill (under
  `Vibecoded-demos/Deepseek/`), v8-engine, dragon-r1, strandbeest, and
  `sandbox/dutch-windmill-2` and `sandbox/gearbox`.
- **The commit message**: "Import the mechanics helpers from
  machinome.mechanics", body "machinome-mechanics joined the machinome
  repository (change join-mechanics, 12 October 2026): its helpers are
  imported from machinome.mechanics, with names, signatures and formulas
  unchanged. Verification records under docs/ keep the import they ran."
- **Green**: the universe sweep of Decision 17 identical to its base row for
  row; Thor (`simulation/test_thor.py`), 3DPrintedClocks (its
  `simulation/test_*.py`) and dragon-r1 (`simulation/test_*.py`) loading and
  their companion tests passing on the bench venv; `git -C <project> status
  --short` showing only the move.

### 17. The universe sweep

The command of `join-freecad` with this bench:

```
MACHINOME_FREECAD_ROOT=<freecad> /home/asa/devel/machinome/.venv/bin/python \
  /home/asa/devel/machinome/scripts/load-projects \
  --bench /home/asa/devel/machinome/machinome/WTs/v0.9-joins-join-mechanics/packages/machinome \
  --python /home/asa/devel/machinome/machinome/WTs/v0.9-joins-join-mechanics/.venv/bin/python \
  --moved /home/asa/devel/machinome/scripts/load-projects.d/*.toml \
  --timeout 300 --json <scratch>/load-projects.json
```

Read against `join-freecad`'s: 63 repositories, 130 rows, 122 ok, 0
expected, 2 unexpected (fender-bender without `fb_library`, wall_clock_41's
own error), 0 timeout, 6 no-model. Run after the implementation and before
the projects' move, every row of the 27 repositories that imports the former
module fails on `No module named 'machinome_mechanics'` (expected with the
workspace's moved-names file of Decision 15, unexpected without it): that is
the move's red. After the move, the base's counts row for row; any other
difference is a finding.

## Risks / Trade-offs

- [The extra admits the published 0.1.0, whose import is the former one] →
  The floor cannot exclude it while the member is numbered 0.1.0;
  `check-dist` installs the built wheel by path (probe 11), and the release
  that publishes the joined package moves its version and the floor past
  0.1.0 (Open Questions 3).
- [uv does not check the two floors] → `check-dist`'s pip install and
  `test_release_records.py` hold them (probe 10).
- [The bench venv loses `machinome_mechanics` at the sync] → Every project
  that imports it fails on the bench until its move; the sweep records that
  red and the move turns it green (Decision 17).
- [A version the set does not move] → The release-records test holds it to
  its changelog and the manual's fact, and ADR-187 says why; the release pass
  must number it by hand.
- [The manual's examples run only in the package's tests] → The HTML build
  stays import-free, as Read the Docs needs; the doctest run is in CI's test
  job, and `-b doctest` stays available to a maintainer.
- [The rewritten history drops twelve files and one commit] → The original
  repository keeps them with the original hashes; the pruned commit touched
  `context7.json` alone, whose rules fold into the root's.
- [The joined archives and notes keep their words, the licence the product
  carried among them] → Archived records are historical, as in `join-freecad`;
  the specs, the config, the manifest, the README, the headers and every
  record this change writes state the set's.
- [The package's lint adds about 52 flake8 lines] → CI's lint is
  `continue-on-error`; reformatting would put an edit of every line between
  the join and `git blame`. Not done.

## Migration Plan

In the order of tasks.md: the baseline; the join, by the orchestrator, and
the reds it causes; the red gates; the package and its source; the core, the
workspace and the sync; the tests at their new place; the manual; `check-dist`
and CI; the records; validation; the projects' move and the sweep, by the
orchestrator; the archive. Rollback is a revert of the implementation commit
and of the merge commit, `uv lock` and `uv sync`, and a revert of each
project's move commit.

## Open Questions

1. **Which commit the join merges.** `v0.8-symbolic-assertions` (6588f0c) or
   `main` (5fdf732). Recommendation: the branch (Decision 1); its change is
   ratified in the product's record, and on `main` this cycle would rewrite the
   same assertions without that record.
2. **The ADR.** A new ADR-187, or amendments only (ADR-182 and ADR-183 a dated
   consequence each, ADR-132 a superseding note). Recommendation: ADR-187,
   since the join makes two choices no record holds: the first member the
   set's version does not number, which `test_release_records.py` and the
   bumpversion tables would otherwise make a surprise, and the first member
   that is a portion of the root package and keeps its own record, neither
   extension package nor framework. If declined, the HISTORY bullet's
   "(ADR-187)" becomes "(ADR-132 superseded in part, ADR-183 amended)".
3. **The pins.** `machinome>=0.8.0` from the package and
   `machinome-mechanics>=0.1.0` from the core, or `~=` shapes (`machinome~=0.8`
   and `machinome-mechanics~=0.1.0`). Recommendation: the floors; they resolve
   today (probe 10), survive the set's renumbering with no table, and the `~=`
   shapes are the set's convention for members the set numbers. At the
   release that publishes the joined package, its version must move past
   0.1.0 and the core's floor with it, or `pip install "machinome[mechanics]"`
   may install the published wheel of the former import; that is the pilot's,
   with the number.
4. **The examples' home and the doctests.** The examples beside the how-to,
   included and offered for download, their doctests run by the package's
   tests with the standard library; or the examples on machinome.org with the
   framework's, and no doctest. Recommendation: beside the how-to; they are
   two modules and a manifest the page includes, built by nothing, which is
   not what moved the framework's examples to the site (three exports at
   build time past Read the Docs' limit, `tests/test_docs_exports.py`); and a
   doctest run in the docs job would put the runtime into a build that
   installs `docs/requirements.txt` alone.
5. **The changelog's 0.1.0 section.** Its identity bullet names the licence
   the product carried, true of the published 0.1.0. Keep the bullet as
   written, as a record of the release, or drop the licence word from it in
   place, as the framework's changelog was made to read on 5 October 2026.
   Recommendation: drop the word in place ("Package `machinome-mechanics`,
   import `machinome_mechanics`, depending on `machinome>=0.7.0` ..."),
   following the pilot's ruling for the framework's own changelog; the
   original repository and PyPI keep the release's metadata.
6. **The upgrading page.** A section for the rename now, or at the 0.9
   release. Recommendation: at the release, which writes the page's section
   for every breaking change of 0.9; this cycle's changelog bullet states the
   old and new import, and the pages a reader is sent to name the new one.
7. **The tag.** `mechanics-v0.1.0`, or `v0.1.0` kept. Recommendation: the
   prefix (Decision 2), the plan's method; the framework's `v0.1` stands
   beside it.
8. **The stylesheet.** Dropped, or kept with its rules scoped to the mechanics
   pages. Recommendation: dropped (Decision 2); the probe 9 build renders the
   tables and entries with the theme's own styles, and scoping it would add
   the manual's only stylesheet for two cosmetic rules.
