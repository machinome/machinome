## Why

Three entries of `workflow/warts.md` concern the package's metadata and two
leftovers of the build pipeline. Each was measured on the bench
`fix-warts-3` at `ad08fe8` before this proposal; all three still reproduce,
the third on a narrower path than the one it was recorded on (design.md,
Context).

From "Expression math and mechanisms (2026-09-06)":

> - **The `viewer` extra carries no version floor.** Item 12's fix left it
>   unpinned "because the viewer is unreleased"; machinome-viewer has been on
>   PyPI since 0.7.0, and `pyproject.toml` still declares
>   `viewer = ["machinome-viewer"]`. Added 2026-10-04 from item 12's own
>   remainder.

From "import-the-artifact-by-path (2026-09-15, found while fixing)":

> - **A rigid leaf's own `.scad` stops describing its geometry after the
>   first build: it becomes a self-import of the STL it exists to
>   regenerate.** Build 1 writes it as the leaf's own geometry (e.g.
>   `cube(size = [10, 10, 10]);`); once the STL is current, `assemble()`'s
>   up-to-date branch sets `self.model = self.artifact_import(self.local_stl)`
>   (`base.py:862-863`) and then calls `generate_scad()`, so the file that is
>   supposed to be able to rebuild the STL from scratch merely imports it.
>   It resolves (same directory), so it is not this change's bug.
>   `FusionNode`'s own `.scad` is written the same self-importing way, but
>   harmlessly: its STL is produced natively (OCCT or manifold3d), never by
>   OpenSCAD from that `.scad`.
> - **`self.mesh_scad_file` / `self.mesh_stl_file` are vestigial.** Nothing
>   in `machinome/` writes or reads them beyond the assignment at
>   `base.py:711-712`.

Measured at `ad08fe8`:

- **The viewer extras.** `pyproject.toml` declares
  `viewer = ["machinome-viewer"]` and
  `web-snapshot = ["machinome-viewer[snapshot]"]`. PyPI holds
  machinome-viewer 0.7.0, 0.7.1 and 0.8.0. `docs/conf.py` states the
  matching viewer once (`viewer_version = '0.8.0'`, API 29), and
  `tests/test_release_records.py` holds it equal to the framework's version;
  nothing holds the extras to it. With the extra unranged, `pip install -U
  "machinome[viewer]"` in a 0.7 environment upgrades the framework and keeps
  viewer 0.7.x, which is not the viewer the manual describes.
- **`mesh_stl_file`.** `mesh_scad_file` went with `openscad-out`
  (2026-10-04). `mesh_stl_file` is still assigned in
  `AbstractBaseNode.__init__` (`machinome/node/base.py:695`) and listed in
  `parameters._RESERVED` (`machinome/parameters.py:141`), the set of
  instance attributes a declaration may not shadow. Nothing reads it: no
  reader in `machinome/`, `tests/` or `docs/`, and none in the catalogue's
  14,618 Python files (`projects/`, excluding `_build`, `WTs`, `.git`, virtual
  environments); no `.mesh.stl` file is named anywhere.
- **The self-import.** Since `scad-presentation` (2026-10-04), `assemble()`
  writes no `.scad`, so `machinome build` run twice leaves a `Solid2Node`'s
  own `.scad` as its geometry (`$fn = 24;` then `cylinder(h = 8, r = 3);`),
  untouched (same inode and stamp). The up-to-date branch still sets the
  model to the import of the leaf's own STL, though, and that model is what
  the leaf's `scad_code` and `generate_scad()` write. `machinome snapshot
  --renderer openscad` of a `Solid2Node` root whose STL is current therefore
  rewrites the leaf's kept `.scad` as `$fn = 24;` then
  `import(file = "machine-FineCylinder-2111f2f9079a.stl", origin = [0, 0]);`
  (new inode), and a fresh `OpenScadNode` assembled with its STL current
  gives `scad_code` ending in an import of its own STL instead of its module
  call. The next build heals the file only when the STL is stale or missing.

## What Changes

- **The viewer extras require the matching viewer.** `viewer` becomes
  `machinome-viewer>=0.8.0` and `web-snapshot` becomes
  `machinome-viewer[snapshot]>=0.8.0`, with no upper bound. The number is
  `docs/conf.py`'s `viewer_version`, the one statement of the matching
  viewer; a release-records test reads both files and fails naming the
  extra that disagrees. This item carries an open question for the pilot:
  the records disagree on whether 0.8 documents *need* viewer 0.8.0
  (design.md, Open Questions, 1). The proposal follows the recommendation
  given there.
- **`mesh_stl_file` is removed.** The assignment in
  `AbstractBaseNode.__init__` and the name in `parameters._RESERVED` go.
  Removing a reserved name is a loosening: a parameter, marking, frame or
  mate may now be named `mesh_stl_file`, as it may be named anything else a
  node does not carry.
- **A family leaf's presentation stays its own geometry when its STL is
  current.** `assemble()`'s up-to-date branch asks the node for its
  presentation of a current artifact through one private hook; the base
  answers with the import of its STL, as today, and the OpenSCAD family's
  leaf base answers with nothing, so its model is rendered on demand from
  its own geometry when something asks for it (`_require_model()`, which
  exists for that). Its `scad_code`, its `generate_scad()` and the OpenSCAD
  snapshot of it as a root then hold the text its materialization wrote, and
  an unchanged file is not rewritten.
- Red tests for each: the extras against `docs/conf.py`
  (`tests/test_release_records.py`); a node carrying no `mesh_stl_file`, and
  every reserved name being an attribute a node carries
  (`tests/test_declarative_nodes.py`); a current `Solid2Node`'s and
  `OpenScadNode`'s `scad_code` equal to their built `.scad`, and an OpenSCAD
  snapshot of a current `Solid2Node` root leaving its `.scad` as built
  (`tests/test_scad_presentation.py`).
- The API reference's `model` entry says when it is unset; the changelog's
  `Unreleased` section takes two bullets; the three warts entries move to the
  campaign's resolved record.

**Deliberately out**, with the reason:

- An upper bound on the viewer. It would refuse a later viewer the framework
  can still drive; what a viewer can read is checked at run time, through
  the report the framework already reads.
- `docs/requirements.txt`'s unranged `machinome-viewer` (the Read the Docs
  build) and CI's Git install of the viewer. They install a viewer for the
  manual's build and the browser-snapshot job, not for a user; nobody asked
  for either to change.
- A run-time check of the installed viewer's version. The framework already
  reads the viewer's report (`apiVersion`, `documentVersions`) and warns or
  refuses on what the viewer cannot read (`viewer-distribution`); a version
  comparison would be a second, weaker check.
- The status page's sentence that 0.8 documents "need the matching viewer
  |viewer_version|, API |viewer_api|". It is half of the disagreement in
  Open Question 1, and changing it is the pilot's answer, not this change's.
- `lock_file`'s comment "(not implemented yet)" and the rest of
  `AbstractBaseNode.__init__`. Not in the finding; `lock_file` is read by
  the OpenSCAD leaf's render lock.
- The up-to-date branch for nodes outside the OpenSCAD family. Their
  presentation of a current artifact is the import of that artifact, which is
  what an OpenSCAD snapshot of such a root draws; no finding asks for it to
  change (design.md, Decision 3).
- The `FusionNode` half of the third entry: since `scad-presentation` no
  build writes a fusion's `.scad`, so there is nothing to change.
- A catalogue build. The finding is reproduced and proved on the fixture
  projects; the brief asks for none.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `viewer-distribution`:
  - MODIFIED "The viewer is an optional extra": both extras require at least
    the matching viewer version `docs/conf.py` states, with no upper bound;
    its two scenarios carried and one added.
- `openscad-node`:
  - MODIFIED "A family leaf writes and keeps its own SCAD and renders its STL
    with OpenSCAD": a family leaf's presentation is the geometry it
    authored whether or not its STL is current, never an import of that
    STL; its two scenarios carried and one added.
- `web-snapshot`:
  - MODIFIED "The OpenSCAD renderer writes the root's SCAD on demand": a
    family leaf snapshotted alone keeps its `.scad` as its build wrote it;
    its four scenarios carried and one added.

The removal of `mesh_stl_file` carries no delta: `declarative-nodes` and
`markings` refuse a declaration that would shadow an attribute a node
carries, by rule and not by list, and a node no longer carries this one.

## Impact

- Packaging: `pyproject.toml`'s `viewer` and `web-snapshot` extras. An
  environment holding viewer 0.7.x is upgraded to the matching viewer by
  the next `pip install -U "machinome[viewer]"`. The workspace venv's
  editable viewer reports stale metadata (0.7.0) over 0.8.0 source; `pip
  check` would flag it once the framework's own metadata is reinstalled,
  which this change does not do.
- Code: `machinome/node/base.py` (one assignment removed from `__init__`;
  the up-to-date branch reads a private hook, defined beside
  `_require_model`), `machinome/parameters.py` (one name out of
  `_RESERVED`), `machinome/node/openscad/leaf.py` (the hook's family
  answer).
- Tests: `tests/test_release_records.py`, `tests/test_declarative_nodes.py`,
  `tests/test_scad_presentation.py`. `tests/scad_presentation_golden.py
  --check` and `tests/expression_type_golden.py --check` stay at zero
  differences, by construction (design.md, Decision 3).
- Docs: `docs/reference/api.rst` (the `model` attribute),
  `docs/project/changelog.rst` (`Unreleased`, two bullets).
- Records: `workflow/warts.md` (three entries, and the emptied
  "import-the-artifact-by-path" section) to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md`.
- Projects: 18 catalogue projects use a `Solid2Node` or `OpenScadNode`;
  none reads `mesh_stl_file`. None is built or edited by this change.
- No ADR: the hook restores the behaviour `assemble()`'s own comment
  describes ("self.model stays unset and is rendered lazily") for the one
  family whose presentation is not its artifact, and `scad-presentation`'s
  Decision 8 already settled that a family leaf's `.scad` is the text
  OpenSCAD renders its STL from.

## Authorization

The pilot's mandate of 6 October 2026 for the fix-warts-3 campaign
(`workflow/ongoing/fix-warts-3.md`, "Mandate"): "work on the items you can
autonomously, orchestrating opus subagents and using empirical evidence
from projects to validate, other than your adversarial review. if
something needs my input, record and defer, you'll go unsupervised." This
change is the campaign table's cycle 16, `release-metadata-and-vestiges`,
validated on the fixture projects. Its first item depends on the answer to
design.md's Open Question 1, recorded for the pilot under that mandate.
