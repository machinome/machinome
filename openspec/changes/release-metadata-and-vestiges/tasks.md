Bench: `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch
`fix-warts-3`. Framework commands run as
`env -C <bench> PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/<tool> ...`.
`<scratch>` is the campaign scratchpad's `cycle16/` directory; every build
directory a task creates by hand lives under it (`SOLID_BUILD_DIR=<scratch>/<name>`),
never in the bench. One build or test run of ours at a time (`ps -eo
pid,args | grep '[p]ytest\|[m]achinome test\|[m]achinome snapshot\|[m]achinome
build'` first). The catalogue is read-only and is not built: this cycle only
greps it, with absolute paths under `/home/asa/devel/machinome/projects/`.
Record every command and its result in `evidence.md` as you go, in the shape
of `openspec/changes/archive/2026-10-04-scad-presentation/evidence.md`; the
scratchpad is not durable, so copy outputs verbatim.

Group 2 implements design.md, Decision 1 as recommended under Open Question 1.
If the orchestrator relays a different answer from the pilot, follow that
answer instead: under (b) the floor is `>=0.7.0` and the test reads it from
where the answer puts it; under (c) skip 2.1, 3.1 and 3.2, and move the warts
entry with Context, 1 as its measurement. Record which answer was applied.

## 1. Baseline on the unmodified tree

- [ ] 1.1 Create `evidence.md` with the bench commit (`git -C <bench>
  rev-parse HEAD`), the interpreter check (`python -c 'import machinome;
  print(machinome.__file__)'` prints a path under the bench), the viewer
  report (`python -c 'from machinome.viewers import bundle; d =
  bundle.describe(); print(d["version"], d["apiVersion"],
  d["documentVersions"])'`) and `pip index versions machinome-viewer`.
- [ ] 1.2 The extras as declared: `python -c 'import tomllib; d =
  tomllib.load(open("pyproject.toml", "rb"))["project"]
  ["optional-dependencies"]; print(d["viewer"], d["web-snapshot"])'` (Stage
  P: `['machinome-viewer'] ['machinome-viewer[snapshot]']`).
- [ ] 1.3 The `mesh_stl_file` readers: `grep -rn -I
  "mesh_stl_file\|mesh_scad_file" <bench> --exclude-dir=_build
  --exclude-dir=.git`, and over the catalogue `grep -rIl
  --exclude-dir=_build --exclude-dir=WTs --exclude-dir=.git
  --exclude-dir=node_modules --exclude-dir=.venv --exclude-dir=venv
  --include='*.py' --include='*.md' --include='*.toml' --include='*.scad'
  --include='*.rst' --include='*.txt' --include='*.cfg'
  "mesh_stl_file\|mesh_scad_file" /home/asa/devel/machinome/projects/`
  (Stage P: no file, exit 1, over 14,618 Python files).
- [ ] 1.4 The self-import, measured: in `<scratch>/a-snap`, `machinome build
  tests/scad_where_read_project/machine.py:FineCylinder` twice, then
  `machinome snapshot tests/scad_where_read_project/machine.py:FineCylinder
  -o <scratch>/a-fine.png --renderer openscad --imgsize 64x48`; after each
  step record the leaf's `.scad` text and `stat -c '%i %Y'` (Stage P: the
  geometry after both builds, the self-import with a new inode after the
  snapshot). Then, in `<scratch>/a-fresh`, build
  `tests/scad_presentation_project/parts.py:Plate` and `...:FineCylinder`
  and run `<scratch>/own_text_after_build.py <reference>` for each with the
  same `SOLID_BUILD_DIR` (Stage P: each `scad_code` ends in an import of the
  leaf's own STL). If the script is gone, it loads the reference with
  `machinome.core.loader.load_node`, calls `assemble()` and prints
  `scad_code`.
- [ ] 1.5 `python tests/scad_presentation_golden.py --check` (Stage P:
  `golden comparison: 34 values, 0 differences, 9 presentation files absent
  as expected`) and `python tests/expression_type_golden.py --check` (read
  its header for how; record its summary line).
- [ ] 1.6 `pytest -q -p no:cacheprovider tests/test_scad_presentation.py`
  (Stage P: `22 passed, 23 subtests passed`, about 100 s) and `pytest -q -p
  no:cacheprovider tests/test_release_records.py
  tests/test_declarative_nodes.py` (Stage P: `101 passed, 101 subtests
  passed`).

## 2. Red tests

- [ ] 2.1 `tests/test_release_records.py`, `VersionFilesTest`:
  `test_the_viewer_extras_require_the_matching_viewer` as design.md,
  Decision 1 writes it. Run it; record the failure (`['machinome-viewer'] !=
  ['machinome-viewer>=0.8.0']`, both subtests).
- [ ] 2.2 `tests/test_declarative_nodes.py`, beside
  `test_a_declaration_cannot_shadow_a_base_attribute`:
  `test_a_node_carries_no_mesh_stl_file` (red) and
  `test_every_reserved_name_is_an_attribute_a_node_carries` (green; Stage P
  found every name carried by a `Piston`). Record the red failure and the
  pin's pass.
- [ ] 2.3 `tests/test_scad_presentation.py`: a `_BuildDirectory` test
  `test_a_current_leafs_scad_code_is_its_geometry`, with subtests for
  `tests/scad_where_read_project/machine.py:FineCylinder` and
  `tests/scad_presentation_project/parts.py:Plate`, as design.md, Decision
  5 describes. Record both subtests' failures.
- [ ] 2.4 `tests/test_scad_presentation.py`, `SnapshotOnDemandTest`:
  `test_a_current_scad_authored_root_keeps_its_scad_as_built`, as design.md,
  Decision 5 describes (build `FineCylinder` as the root with
  `self.build(f'{FIXTURE}/machine.py:FineCylinder')`). Record the failure.

## 3. The change

- [ ] 3.1 `pyproject.toml`: the `viewer` and `web-snapshot` extras take the
  floor of design.md, Decision 1, and the comment above `viewer` its one line
  naming `docs/conf.py`'s `viewer_version` and the test.
- [ ] 3.2 Run 2.1: green.
- [ ] 3.3 `machinome/node/base.py`: delete the comment and the
  `self.mesh_stl_file` assignment in `__init__`; `machinome/parameters.py`:
  drop `'mesh_stl_file'` from `_RESERVED`. Run 2.2: both green.
- [ ] 3.4 `machinome/node/base.py`: add `_current_artifact_presentation()`
  beside `_require_model()`, have `assemble()`'s up-to-date branch read it,
  and correct that branch's comment, as design.md, Decision 3 writes them.
  The base's docstring and comment name no SCAD.
- [ ] 3.5 `machinome/node/openscad/leaf.py`: `ScadLeafNode` overrides
  `_current_artifact_presentation()` to return None, with the docstring of
  design.md, Decision 3.
- [ ] 3.6 Run 2.3 and 2.4: green. Record.

## 4. Green and validation

- [ ] 4.1 Repeat 1.4 on the changed tree in fresh scratch directories
  (`<scratch>/b-snap`, `<scratch>/b-fresh`): the leaf's `.scad` text, inode
  and stamp unchanged by the snapshot, the PNG written, and each fresh
  `scad_code` equal to the built file. Record before and after side by side.
- [ ] 4.2 Repeat 1.5: both goldens at zero differences.
- [ ] 4.3 Repeat 1.6: every test green, with the new ones counted.
- [ ] 4.4 `pytest -q -p no:cacheprovider tests/test_markings.py
  tests/test_frames.py tests/test_source_set.py tests/test_snapshot.py
  tests/test_expression_type.py` (the other readers of `_RESERVED`, the
  up-to-date branch and the core-names-no-SCAD scan). Record the counts.

## 5. Docs and changelog

- [ ] 5.1 `docs/reference/api.rst`, the `model` attribute of
  `AbstractBaseNode`: the one sentence of design.md, Decision 4.
- [ ] 5.2 `docs/project/changelog.rst`, under `Unreleased`: the two
  bullets of design.md, Decision 4, each ending
  `(release-metadata-and-vestiges)`.
- [ ] 5.3 `pytest -q -p no:cacheprovider tests/test_release_records.py
  tests/test_docs_structure.py tests/test_docs_exports.py`: green.

## 6. Records

- [ ] 6.1 `workflow/warts.md`: move the three entries verbatim to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md` under a heading
  naming `release-metadata-and-vestiges`, each with a "What shipped"
  paragraph (the viewer one naming the answer to Open Question 1 that was
  applied). The "import-the-artifact-by-path (2026-09-15, found while
  fixing)" section is then empty: remove its heading and its introductory
  paragraph with it, and say so in the resolved record.
- [ ] 6.2 `openspec/specs/`: sync the three delta specs
  (`viewer-distribution`, `openscad-node`, `web-snapshot`), each modified
  requirement replaced whole, every carried scenario kept.
- [ ] 6.3 Archive the change to
  `openspec/changes/archive/<date>-release-metadata-and-vestiges/`; run
  `openspec validate --specs` (or `openspec validate` for each touched spec)
  and record the result.
- [ ] 6.4 `black --check` and `flake8 --max-line-length=89` on every
  touched Python file; the focused tests of 4.3 and 4.4 once more; then the
  full suite once, alone (`pytest -q -p no:cacheprovider` at the bench
  root). Record the counts and the time. Leave everything uncommitted.
