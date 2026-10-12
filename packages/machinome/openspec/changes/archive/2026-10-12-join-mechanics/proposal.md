## Why

The pilot's plan for the joins of Machinome 0.9 (`workflow/ongoing/joins-0.9.md`
at the repository root, set on 11 October 2026) names this change its second
cycle: machinome-mechanics, the mechanics helpers published as 0.1.0, joins the
repository whole, its history imported to its final paths. On 12 October 2026
the pilot settled the two decisions the plan held for him: the import is
`machinome.mechanics`, a portion of the `machinome` namespace like
`machinome.node.freecad`, with no module of the former name; and its manual
folds into the framework's one manual. He added a third: mechanics keeps its
own version, 0.1.0, outside the set's one-version rule. The probes in design.md
find the product cannot be used against the framework it joins: on the line's
head its suite collects with 2 errors and fails 34 tests from its `main` (38
from its unmerged 0.8 branch), because two tests import `AssemblyNode` from the
node root, refused since `root-cleanup`, and every symbolic check takes its time
from SolidPython, whose values the core reads as symbolic only once a node
package adopts them; its manual's doctests fail 10 of 151 on the same import.
Twenty-five project repositories and two sandboxes import `machinome_mechanics`.

## What Changes

- **The join, by the orchestrator, after the planning commit**: a fresh clone
  of machinome-mechanics rewritten by `git filter-repo` with the mapping of
  design.md Decision 2 (157 files land, 140 under `packages/machinome-mechanics/`
  and 17 in the framework's manual; 12 are dropped), its branch
  `v0.8-symbolic-assertions` (6588f0c, its `main` and the ratified change
  `symbolic-assertions`) merged with `--allow-unrelated-histories`, its tag
  `v0.1.0` renamed `mechanics-v0.1.0`; rehearsed in the scratch directory,
  where the merge is clean and the history of every helper reads at its new
  path back to the founding commit.
- **`machinome-mechanics` at `packages/machinome-mechanics/`**, a product that
  keeps its record in its directory (its tests, its OpenSpec specs and 16
  archived changes, its working record, its changelog): its manifest at its
  own version 0.1.0, requiring `machinome>=0.8.0`, under the set's licence;
  the links `LICENSE` and `LICENSES`; the package directory
  `machinome/mechanics/` with its nine family modules and `__init__.py`,
  imported as `machinome.mechanics`. **BREAKING** for projects:
  `machinome_mechanics` is not provided; names, signatures and formulas are
  unchanged.
- **The tests at their new place**, run from `packages/machinome-mechanics/`
  by a step of CI's test job; the core suite does not collect them. Fourteen
  import lines move to the core's own symbolic time and `AssemblyNode`'s module
  (probed: 201 passed on the line's core, 195 on published Machinome 0.8.0);
  the two tests that pin the manual and the identity are rewritten for the
  new place, and a new one runs the manual's 141 examples.
- **The manual folds in** by reader intent: the nine family pages and the
  conventions page as the section `reference/mechanics/`, the worked relation
  law as the how-to `howto/mechanism-formulas` with its example project
  beside it, the two drawings in `_static/`; the framework's pages that link
  the separate manual link inside it; `sphinx.ext.doctest` renders the
  examples, which the mechanics tests run.
- **The core names it as a product, not a portion of the set**: the
  `mechanics` extra floors at `machinome-mechanics>=0.1.0`; the boundary test's
  guard refuses `machinome.mechanics` from the core; the layout gate gains a
  table of products that keep their record; the release records hold mechanics
  to its own version, outside `.bumpversion.cfg`; the vet universe's contract
  drops `machinome_mechanics`, since `machinome.mechanics` lies beneath
  `machinome`; `scripts/check-dist` builds it and smokes it from its wheel.
- **One licence at the join**: the product's licence file and notice are
  dropped by the import; its manifest declares the set's expression and files;
  no record this change writes names the licence it carried. Its notice records
  no third-party provenance, so `CREDITS.md` is unchanged.
- **Records**: the `Unreleased` bullets of `HISTORY.rst`, the manual's
  changelog and the product's `CHANGELOG.md`; the root `README.md`,
  `CONTRIBUTING.rst`, `context7.json` (the product's rules folded in) and
  `AI-USE.md`; the framework's `README.rst` sentence; the architecture's Map
  and mechanics section; ADR-187 (recommended, Open Questions 2), ADR-132
  superseded in its import path and repository, ADR-182 and ADR-183 amended.
- **Validation in the projects**, by the orchestrator after the
  implementation: the 27 repositories moved onto `machinome.mechanics` by a
  mechanical rename in their own repositories (design.md Decision 16), the
  universe sweep identical to its base row for row.

Not in this change: a version for the joined mechanics package, its upload, the
upgrading page's section for the rename (Open Questions 6), the Read the Docs
project's retirement (the pilot's), any push, and the other three joins.

## Capabilities

### New Capabilities

None. The product's own specs (`distribution`, `mechanisms`,
`user-documentation`) arrive by the import under
`packages/machinome-mechanics/openspec/specs/`, its own record, and are
brought current in place by the applier (design.md Decision 13).

### Modified Capabilities

- `mechanics-distribution`: the helpers are the repository's distribution
  `machinome-mechanics`, imported as `machinome.mechanics`, which the core
  never imports (the guard watches the dotted name; new scenarios).
- `framework-identity`: the `mechanics` extra selects a distribution of the
  repository; the monorepo holds products that keep their record in their
  directory, and `machinome-mechanics` carries its own version outside the
  set's (new scenarios).
- `vet`: the contract tier is `machinome` and `molejo`; a project importing
  the former module is outside the universe (new scenario).
- `user-documentation`: the requirement on the separate mechanics manual is
  renamed and restated for the mechanics section and how-to inside the
  manual, whose examples run.
- `framework-contributor-guidance`: the install without uv names the
  mechanics directory, and the guide says where its tests run.

`kernel-extras` is unchanged: its requirements name the kernel and node
extras, and none names `mechanics`.

## Impact

- **Tree.** The join adds 157 files. The cycle adds the two licence links,
  ADR-187 and the edits of design.md Decisions 3 to 15; it deletes nothing the
  join did not bring.
- **Code.** No module of the core changes but the vet universe's data file.
  The core's manifest changes one extra; the product's ten modules change
  their SPDX lines, `__init__.py` its nine internal imports and two docstring
  passages, `belts.py` one import and `linkages.py` one docstring sentence.
- **Tests.** Joining: 17 modules, 201 tests run from their own directory.
  Changed in the core's suite: `test_mechanics_boundary.py`,
  `test_repository_layout.py`, `test_release_records.py`,
  `test_vet_universe.py`, `test_docs_structure.py`; design.md probe 6 lists the
  gates the join alone turns red.
- **Build and CI.** Thirteen members build from `packages/`; `check-dist`
  gains a row; the test job gains a step; the docs job is unchanged.
- **Projects.** 27 repositories import `machinome_mechanics` (25 under
  `projects/`, 2 under `projects/sandbox/`); after the implementation the
  bench venv has no such module until they move.

Originating evidence: the campaign plan (`workflow/ongoing/joins-0.9.md`, "The
method" and cycle 2), the pilot's decisions of 12 October 2026, the product's
own record (its specs, its 16 archived changes, its eight working notes), the
probes recorded in design.md, and the 27 importing repositories.
