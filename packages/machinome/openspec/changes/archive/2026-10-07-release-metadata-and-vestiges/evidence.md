# Evidence — `release-metadata-and-vestiges`

Cycle 16 of the fix-warts-3 campaign (`workflow/ongoing/fix-warts-3.md`).
Bench `machinome/WTs/fix-warts-3`, branch `fix-warts-3`, planning commit
`184b06926a4cceae274e911fc42c959d432061cd` (`git -C <bench> rev-parse HEAD`).
Every command below ran as `env -C <bench> PYTHONPATH=<bench>
/home/asa/devel/machinome/.venv/bin/<tool> ...` (Python 3.12.3, OpenSCAD
2021.01 at `/usr/bin/openscad`), one run at a time, with `ps -eo pid,args |
grep '[p]ytest\|[m]achinome test\|[m]achinome snapshot\|[m]achinome build'`
empty first. `<scratch>` is the campaign scratchpad's `cycle16/`; every
hand-made build directory was under it. No project was run, built or
edited.

## The answer applied to Open Question 1

Answered at review on 7 October 2026: the viewer extras' floor is deferred
to the pilot. Before any code, the planning artifacts were revised in place
for the other two entries: item 1 left `proposal.md` (its measurement kept
as one paragraph saying it is deferred), `tasks.md` (its red test, its
change and its changelog bullet), `design.md`'s decisions (Decision 1 now
says the extras are left as they are; the goals, the changelog decision,
the red-test table, the risks and the migration plan lost their viewer
parts), and `specs/viewer-distribution/spec.md` was deleted from the
change. `openspec validate release-metadata-and-vestiges`: "Change
'release-metadata-and-vestiges' is valid". `pyproject.toml`,
`docs/conf.py`, `tests/test_release_records.py` and the
`viewer-distribution` spec are untouched.

## 1. Baseline on the unmodified tree (184b069)

### 1.1 Interpreter and viewer

```
$ python -c 'import machinome; print(machinome.__file__)'
/home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py

$ python -c 'from machinome.viewers import bundle; d = bundle.describe(); print(d["version"], d["apiVersion"], d["documentVersions"])'
0.7.0 29 [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

$ python -m pip index versions machinome-viewer
machinome-viewer (0.8.0)
Available versions: 0.8.0, 0.7.1, 0.7.0
  INSTALLED: 0.7.0
```

The installed viewer's `0.7.0` is the editable install's stale metadata
over 0.8.0 source, which reports API 29 (design.md, Context).

### 1.2 The extras as declared

```
$ python -c 'import tomllib; d = tomllib.load(open("pyproject.toml", "rb"))["project"]["optional-dependencies"]; print(d["viewer"], d["web-snapshot"])'
['machinome-viewer'] ['machinome-viewer[snapshot]']
```

Unchanged by this cycle (deferred).

### 1.3 The `mesh_stl_file` readers

```
$ grep -rn -I "mesh_stl_file\|mesh_scad_file" <bench> --exclude-dir=_build --exclude-dir=.git
machinome/parameters.py:141:    'build_dir', 'stl_file', 'brep_file', 'mesh_stl_file', 'lock_file',
machinome/node/base.py:695:        self.mesh_stl_file = f'{basepath}.mesh.stl'
workflow/warts.md:730:...
workflow/archive/warts-hygiene-2026-10-04/warts-before-hygiene.md:2557:...
workflow/ongoing/fix-warts-3.md:60:...
openspec/changes/archive/2026-10-04-openscad-out/{moved-names.toml,design.md,tasks.md,evidence.md}:...
openspec/changes/archive/2026-09-15-import-the-artifact-by-path/evidence.md:232:...
openspec/changes/release-metadata-and-vestiges/{proposal,design,tasks}.md:...
docs/adrs/BUILD/ADR-116-an-artifact-import-is-anchored-on-the-build-directory.md:185:  `mesh_scad_file`/`mesh_stl_file` are vestigial. ...
```

The only code lines are the assignment and the reserved name; every other
hit is a record. Over the catalogue:

```
$ grep -rIl --exclude-dir=_build --exclude-dir=WTs --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.venv --exclude-dir=venv --include='*.py' --include='*.md' --include='*.toml' --include='*.scad' --include='*.rst' --include='*.txt' --include='*.cfg' "mesh_stl_file\|mesh_scad_file" /home/asa/devel/machinome/projects/
(no output, exit 1)

$ grep -rIl <same exclusions> --include='*.py' "\.mesh\.stl" /home/asa/devel/machinome/projects/
(no output, exit 1)

$ find /home/asa/devel/machinome/projects/ \( -name _build -o -name WTs -o -name .git -o -name node_modules -o -name .venv -o -name venv \) -prune -o -name '*.py' -type f -print | wc -l
14618
```

### 1.4 The self-import, measured

`<scratch>/measure.sh a` (kept in the scratchpad): in `<scratch>/a-snap`,
`machinome build tests/scad_where_read_project/machine.py:FineCylinder`
twice, then `machinome snapshot
tests/scad_where_read_project/machine.py:FineCylinder -o <scratch>/a-fine.png
--renderer openscad --imgsize 64x48` (real OpenSCAD); then, in
`<scratch>/a-fresh`, `machinome build` of each reference followed by
`<scratch>/own_text_after_build.py <reference>` (loads the reference with
`machinome.core.loader.load_node`, calls `assemble()`, prints
`_up_to_date(stl_file)`, `scad_file` and `scad_code`). 33 s in all.

```
--- after build 1: machine-FineCylinder-2111f2f9079a.scad inode/mtime: 270050 1791295831 bytes: 35
$fn = 24;

cylinder(h = 8, r = 3);
--- after build 2: machine-FineCylinder-2111f2f9079a.scad inode/mtime: 270050 1791295831 bytes: 35
$fn = 24;

cylinder(h = 8, r = 3);
snapshot exit 0
--- after snapshot: machine-FineCylinder-2111f2f9079a.scad inode/mtime: 270058 1791295831 bytes: 84
$fn = 24;

import(file = "machine-FineCylinder-2111f2f9079a.stl", origin = [0, 0]);
```

The builds leave the file alone; the snapshot replaces it (new inode
270058) with an import of the STL OpenSCAD renders from it. The fresh
instances:

```
tests/scad_presentation_project/parts.py:Plate
up to date: True
--- scad_code of a fresh instance after assemble():
module plate(width = 10) {
	difference() {
		cube([width, width, 2], center = true);
		cylinder(h = 4, r = width / 5, center = true);
	}
}


import(file = "plate-__Plate_,_scad_presentation_project_parts.py__-9ea63c013015.stl", origin = [0, 0]);
--- built file (149 bytes) ends:
plate();

tests/scad_where_read_project/machine.py:FineCylinder
up to date: True
--- scad_code of a fresh instance after assemble():
$fn = 24;

import(file = "machine-FineCylinder-2111f2f9079a.stl", origin = [0, 0]);
--- built file (35 bytes):
$fn = 24;

cylinder(h = 8, r = 3);
```

`<scratch>/a-fine.png` (446 bytes, SHA-256 `552ba50a…f44ab83`) was written
and looked at: a yellow cylinder.

### 1.5 The goldens

```
$ python tests/scad_presentation_golden.py --check
golden comparison: 34 values, 0 differences, 9 presentation files absent as expected
$ python tests/expression_type_golden.py --check
golden comparison: 17 values, 0 differences
```

### 1.6 The focused tests

```
$ pytest -q -p no:cacheprovider tests/test_scad_presentation.py
22 passed, 2 warnings, 23 subtests passed in 101.58s (0:01:41)
$ pytest -q -p no:cacheprovider tests/test_release_records.py tests/test_declarative_nodes.py
101 passed, 4 warnings, 101 subtests passed in 3.80s
```

## 2. Red tests (unmodified code)

### 2.1 `tests/test_declarative_nodes.py`

`test_a_node_carries_no_mesh_stl_file` and
`test_every_reserved_name_is_an_attribute_a_node_carries` (a subtest per
name of `parameters._RESERVED`), beside
`test_a_declaration_cannot_shadow_a_base_attribute`; the module gains
`from machinome import parameters`.

```
$ pytest -q -p no:cacheprovider tests/test_declarative_nodes.py -k "mesh_stl_file or every_reserved_name"
F.
    def test_a_node_carries_no_mesh_stl_file(self):
        # It named a `.mesh.stl` file nothing wrote or read.
>       self.assertFalse(hasattr(Piston(), 'mesh_stl_file'))
E       AssertionError: True is not false
FAILED tests/test_declarative_nodes.py::ParameterDeclarationTest::test_a_node_carries_no_mesh_stl_file
1 failed, 1 passed, 92 deselected, 16 subtests passed in 0.32s
```

The coherence pin passed for all 16 reserved names: no other name is
listed without being carried.

### 2.2 and 2.3 `tests/test_scad_presentation.py`

`WrittenOnlyWhereReadTest.test_a_current_leafs_scad_code_is_its_geometry`
(subtests `tests/scad_where_read_project/machine.py:FineCylinder` and
`tests/scad_presentation_project/parts.py:Plate`: build with `machinome
build`, load a fresh instance with `load_node`, `assemble()`, assert the
STL current, no `import(file = "<own STL>"` in `scad_code`, and `scad_code`
equal to the built file) and
`SnapshotOnDemandTest.test_a_current_scad_authored_root_keeps_its_scad_as_built`
(build `FineCylinder` as the root, check its `.scad` against the golden's
`FineCylinder` digest, record `observed()`, snapshot through the
OpenSCAD renderer with OpenSCAD mocked, assert the text OpenSCAD was given
equals the built bytes, `observed()` unchanged and the file's bytes
unchanged).

```
$ pytest -q -p no:cacheprovider tests/test_scad_presentation.py -k "current_leafs_scad_code or current_scad_authored_root"
E               AssertionError: 'import(file = "machine-FineCylinder-2111f2f9079a.stl"' unexpectedly found in '$fn = 24;\n\nimport(file = "machine-FineCylinder-2111f2f9079a.stl", origin = [0, 0]);\n'
tests/test_scad_presentation.py:430: AssertionError
E               AssertionError: 'import(file = "plate-__Plate_,_scad_presentation_project_parts.py__-9ea63c013015.stl"' unexpectedly found in 'module plate(width = 10) {\n\tdifference() {\n\t\tcube([width, width, 2], center = true);\n\t\tcylinder(h = 4, r = width / 5, center = true);\n\t}\n}\n\n\nimport(file = "plate-__Plate_,_scad_presentation_project_parts.py__-9ea63c013015.stl", origin = [0, 0]);'
tests/test_scad_presentation.py:430: AssertionError
>       self.assertEqual(text.encode(), built)
E       AssertionError: b'$fn = 24;\n\nimport(file = "machine-FineCylinder-2111f[29 chars]);\n' != b'$fn = 24;\n\ncylinder(h = 8, r = 3);\n'
tests/test_scad_presentation.py:598: AssertionError
SUBFAILED[tests/scad_where_read_project/machine.py:FineCylinder] tests/test_scad_presentation.py::WrittenOnlyWhereReadTest::test_a_current_leafs_scad_code_is_its_geometry
SUBFAILED[tests/scad_presentation_project/parts.py:Plate] tests/test_scad_presentation.py::WrittenOnlyWhereReadTest::test_a_current_leafs_scad_code_is_its_geometry
FAILED tests/test_scad_presentation.py::SnapshotOnDemandTest::test_a_current_scad_authored_root_keeps_its_scad_as_built
3 failed, 1 passed, 22 deselected in 21.51s
```

## 3. The change

- `machinome/node/base.py`: the comment and the `self.mesh_stl_file`
  assignment left `AbstractBaseNode.__init__`; `assemble()`'s up-to-date
  branch sets `self.model = self._current_artifact_presentation()` when the
  model is unset, its comment now saying what that is; the new private
  `_current_artifact_presentation()` beside `_require_model()` returns
  `self.artifact_import(self.local_stl)`, as the branch did. Its docstring
  and the comment name no SCAD.
- `machinome/parameters.py`: `'mesh_stl_file'` left `_RESERVED`.
- `machinome/node/openscad/leaf.py`: `ScadLeafNode` overrides
  `_current_artifact_presentation()` to return None, with design.md's
  docstring.

```
$ pytest -q -p no:cacheprovider tests/test_declarative_nodes.py -k "mesh_stl_file or every_reserved_name"
2 passed, 92 deselected, 15 subtests passed in 0.25s
$ pytest -q -p no:cacheprovider tests/test_scad_presentation.py -k "current_leafs_scad_code or current_scad_authored_root"
2 passed, 22 deselected, 2 subtests passed in 21.82s
```

No divergence from design.md.

## 4. Green and validation

### 4.1 The measurement repeated (`<scratch>/measure.sh b`, 34 s)

| Step | Before (`a-snap`) | After (`b-snap`) |
|---|---|---|
| after build 1 | inode 270050, 35 bytes, geometry | inode 270084, 35 bytes, geometry |
| after build 2 | inode 270050, same | inode 270084, same |
| after the OpenSCAD snapshot | inode 270058, 84 bytes, `import(file = "machine-FineCylinder-2111f2f9079a.stl", origin = [0, 0]);` | inode 270084, 35 bytes, `$fn = 24;` / blank / `cylinder(h = 8, r = 3);` |
| stamp (`%Y`) throughout | 1791295831 | 1791295831 |

```
--- after snapshot: machine-FineCylinder-2111f2f9079a.scad inode/mtime: 270084 1791295831 bytes: 35
$fn = 24;

cylinder(h = 8, r = 3);
```

The snapshot still logs `... .scad generated with 1791295831.4799519!`
(`writer.generate_scad` logs every call) but `currency.publish_text` left
the unchanged text in place. `<scratch>/b-fine.png` is byte-identical to
`a-fine.png` (`cmp`; SHA-256 `552ba50a01b7e1580d5c7f6308ae336ccb25e0e84a0c20acf360ba3f7f44ab83`
both): at 64x48 OpenSCAD draws the 24-sided cylinder and its STL alike. A
second snapshot at `--imgsize 320x240` (`<scratch>/b-fine-320.png`, looked
at: a yellow 24-faceted cylinder) left the file at inode 270084, stamp
1791295831, 35 bytes.

Fresh instances (`b-fresh`):

```
tests/scad_presentation_project/parts.py:Plate
up to date: True
--- scad_code of a fresh instance after assemble():
module plate(width = 10) {
	difference() {
		cube([width, width, 2], center = true);
		cylinder(h = 4, r = width / 5, center = true);
	}
}


plate();
--- built file (149 bytes): the same text

tests/scad_where_read_project/machine.py:FineCylinder
up to date: True
--- scad_code of a fresh instance after assemble():
$fn = 24;

cylinder(h = 8, r = 3);
--- built file (35 bytes): the same text
```

### 4.2 The goldens

```
$ python tests/scad_presentation_golden.py --check
golden comparison: 34 values, 0 differences, 9 presentation files absent as expected
$ python tests/expression_type_golden.py --check
golden comparison: 17 values, 0 differences
```

### 4.3 The focused tests

```
$ pytest -q -p no:cacheprovider tests/test_scad_presentation.py
24 passed, 2 warnings, 25 subtests passed in 120.61s (0:02:00)
$ pytest -q -p no:cacheprovider tests/test_release_records.py tests/test_declarative_nodes.py
103 passed, 4 warnings, 116 subtests passed in 3.60s
```

Two tests and two subtests more in the first (the new ones); two tests and
15 subtests more in the second (the two new tests, the pin's 15 names).

### 4.4 The other readers

```
$ pytest -q -p no:cacheprovider tests/test_markings.py tests/test_frames.py tests/test_source_set.py tests/test_snapshot.py tests/test_expression_type.py
286 passed, 4 warnings, 162 subtests passed in 15.88s
```

## 5. Docs and changelog

- `docs/reference/api.rst`, `AbstractBaseNode.model`: the sentence on the
  OpenSCAD-family leaf gains "one whose `.stl` was already current keeps
  `None` once assembled, until its presentation is asked for, and is then
  given its render result."
- `docs/project/changelog.rst`, `Unreleased`: one bullet, "A SCAD-authored
  part's own `.scad` stays its geometry" (release-metadata-and-vestiges).
  None for `mesh_stl_file`.
- `grep -rn "mesh_stl\|machinome-viewer>=" docs`: only ADR-116's note,
  a record.

```
$ pytest -q -p no:cacheprovider tests/test_release_records.py tests/test_docs_structure.py tests/test_docs_exports.py
42 passed, 833 subtests passed in 0.68s
$ python -m sphinx -b html -W -q docs <scratch>/docs-build
(no output, exit 0, 5.5 s; nitpicky from docs/conf.py)
```

## 6. Records

- `workflow/warts.md`: the "import-the-artifact-by-path (2026-09-15, found
  while fixing)" section (heading, introduction, both entries) left; the
  viewer entry stays with a **Remaining (2026-10-07):** note pointing at
  the campaign note's "Deferred to the pilot".
- `workflow/archive/fix-warts-3-2026-10-06/resolved.md`: section
  `release-metadata-and-vestiges`, the introduction quoted, both entries
  verbatim, a "What shipped" paragraph for each, and a line on the viewer
  entry staying.
- `workflow/ongoing/fix-warts-3.md`: a Progress line after cycle 15's.

### Lint, against HEAD

Touched Python files: `machinome/node/base.py`,
`machinome/node/openscad/leaf.py`, `machinome/parameters.py`,
`tests/test_declarative_nodes.py`, `tests/test_scad_presentation.py`. The
HEAD copies (`git show HEAD:<file>`) were linted in `<scratch>/head/`.

- `flake8 --max-line-length=89` (pyenv shim, 7.3.0): 9 findings at HEAD,
  the same 9 after (compared with line and column stripped: no
  difference), all in lines this change does not touch (`base.py` E127,
  E128, E303; `test_declarative_nodes.py` E127 twice, E128 twice, F841,
  F401).
- `black --check` (26.5.1): all five "would reformat" at HEAD and after;
  none follows black. Changed lines in black's diff, HEAD and after:
  `base.py` 296 and 294, `leaf.py` 49 and 49, `parameters.py` 258 and 257,
  `test_declarative_nodes.py` 517 and 519, `test_scad_presentation.py` 442
  and 468. The new tests are written in their files' own style (single
  quotes), which is the whole of the growth. Nothing was reformatted.

### Sync, archive and validation

```
$ openspec validate release-metadata-and-vestiges
Change 'release-metadata-and-vestiges' is valid
$ openspec archive release-metadata-and-vestiges --yes
Proposal warnings in proposal.md (non-blocking):
  ⚠ Why section should not exceed 1000 characters
Task status: 22/25 tasks
Warning: 3 incomplete task(s) found. Continuing due to --yes flag.
Specs to update:
  openscad-node: update
  web-snapshot: update
Applying changes to openspec/specs/openscad-node/spec.md:
  ~ 1 modified
Applying changes to openspec/specs/web-snapshot/spec.md:
  ~ 1 modified
Totals: + 0, ~ 2, - 0, → 0
Specs updated successfully.
Change 'release-metadata-and-vestiges' archived as '2026-10-07-release-metadata-and-vestiges'.
```

The three incomplete tasks were 6.3 to 6.5, this archive and what follows
it; they were ticked in the archived copy afterwards. Before archiving, each
delta's requirement was diffed against its baseline: only additions (the
new paragraph or clause and the new scenario), every existing scenario
carried. After it, `git diff --stat -- openspec/specs`: `openscad-node`
15 insertions, `web-snapshot` 13 insertions and 1 deletion (the sentence
the clause extends), nothing else changed.

```
$ openspec validate --specs
Totals: 45 passed, 0 failed (45 items)
```

### The focused tests, once more, and the full suite

```
$ pytest -q -p no:cacheprovider tests/test_scad_presentation.py tests/test_release_records.py tests/test_declarative_nodes.py tests/test_markings.py tests/test_frames.py tests/test_source_set.py tests/test_snapshot.py tests/test_expression_type.py tests/test_docs_structure.py tests/test_docs_exports.py
446 passed, 6 warnings, 1078 subtests passed in 134.95s (0:02:14)

$ pytest -q -p no:cacheprovider        # bench root, alone
4746 passed, 4 skipped, 55 warnings, 6694 subtests passed in 672.86s (0:11:12)
```

Exit 0, 675 s wall clock. Everything is left uncommitted.
