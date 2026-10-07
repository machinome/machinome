## Context

### The bench

`/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch `fix-warts-3`,
at `ad08fe8` (cycles 1 to 15 complete). Commands run as
`env -C <bench> PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/<tool>`;
`import machinome` resolves to
`<bench>/machinome/__init__.py`. The workspace venv's editable viewer reports
`importlib.metadata.version('machinome-viewer') == '0.7.0'` while its source
(`/home/asa/devel/machinome/machinome-viewer`) is 0.8.0 and its report says
API 29, documents 1 to 13: stale metadata, not a stale viewer. OpenSCAD is
`/usr/bin/openscad`.

### 1. The viewer extras

`pyproject.toml`:

    viewer = [
        "machinome-viewer",
    ]
    web-snapshot = [
        "machinome-viewer[snapshot]",
    ]

PyPI (`pip index versions machinome-viewer`, and the JSON API): 0.7.0,
0.7.1, 0.8.0. There was never an earlier `machinome-viewer` on PyPI.

What the records say about which viewer goes with 0.8.0:

| Record | Statement |
|---|---|
| `docs/conf.py` | `viewer_version = '0.8.0'  # the matching machinome-viewer package`, `viewer_api = '29'`, `document_versions = '1 to 13'` |
| `tests/test_release_records.py` | `test_the_matching_viewer_is_numbered_with_the_framework`: `viewer_version` equals the framework's version |
| `docs/project/status.rst` | running documents this release exports "need the matching viewer \|viewer_version\|, API \|viewer_api\|" |
| `docs/start/install.rst`, `docs/concepts/publishing.rst`, `docs/project/upgrading.rst` | "This manual matches viewer \|viewer_version\|, API \|viewer_api\|"; "The matching viewer is ..." |
| `context7.json` (pinned by the same test) | "The matching viewer is 0.8.0, API 29" |
| `docs/releases/release-0.8.rst`, `docs/project/changelog.rst` (0.8.0), `docs/project/upgrading.rst` | "Exports keep document versions 1 to 13, so a 0.7 viewer reads them" |
| the viewer's `CHANGELOG.md`, 0.8.0 | "Released with Machinome 0.8.0 and numbered with it ... Install both with `pip install "machinome[viewer]"`. ... a 0.7 viewer reads a 0.8 export"; API 28 and 29 are host members (`partOnScreen`, `highlight`, per-view up and field of view, the on-demand clocked mount) |

What the framework uses of the viewer (`machinome/viewers/bundle.py`,
`machinome/viewers/browser.py`, `machinome/manager/develop.py`): the
`machinome.viewer` entry point's `bundle` report, `serve --build-dir` and
`capture <staging> -o --imgsize --time --view= --up= --fov`. The viewer's
argument parser (`machinome_viewer/cli.py`) declares the same arguments at
`v0.7.0` and `v0.8.0`. No framework code reads an API 28 or 29 member.

So the framework 0.8.0 *runs* against viewer 0.7.0, which reads every
document it writes; the records nonetheless name one viewer per release, the
matching one, numbered with the framework, and the status page says 0.8
documents *need* it. Those two statements disagree (Open Questions, 1).

### 2. `mesh_stl_file`

    machinome/node/base.py:693-695
            # A mesh with transformations applied, used for mesh generation
            # for spatial calculations, specially tests
            self.mesh_stl_file = f'{basepath}.mesh.stl'

    machinome/parameters.py:136-143
    # Instance attributes AbstractBaseNode.__init__ assigns. A declaration
    # is read as an attribute of its node, so a declaration by one of these
    # names would either be assigned over in __init__ or shadow what every
    # caller of that attribute expects.
    _RESERVED = frozenset({
        'name', 'uniq_id', 'operations', 'checkpoint', 'src', 'basedir',
        'build_dir', 'stl_file', 'brep_file', 'mesh_stl_file', 'lock_file',
        'local_stl', 'basepath', 'files', 'model', 'root',
    })

`_RESERVED` is read by `Declaration.__set_name__` (parameters, flags),
`machinome/node/declarative.py` (two class-body checks) and
`machinome/motion/mates.py` (a mate's name). Readers of `mesh_stl_file`
or `.mesh.stl`:

- `grep -rn "mesh_stl_file\|mesh_scad_file" <bench>` (excluding `_build`,
  `.git`): the two lines above, `workflow/` and archived OpenSpec records,
  and ADR-116's note that both names are vestigial. `mesh_scad_file` left
  with `openscad-out`.
- `grep -rIl "mesh_stl_file\|mesh_scad_file"` over
  `/home/asa/devel/machinome/projects/` (`*.py`, `*.md`, `*.toml`, `*.scad`,
  `*.rst`, `*.txt`, `*.cfg`; excluding `_build`, `WTs`, `.git`,
  `node_modules`, `.venv`, `venv`): no file (exit 1). The same exclusions
  hold 14,618 Python files. `grep ... "\.mesh\.stl"` over the catalogue's
  Python files: no file.
- `machinome/node/fusion.py`'s `_generate_mesh_stl` is a method name; it
  writes `self.stl_file`.

### 3. The leaf's `.scad`

`assemble()` (`machinome/node/base.py:849-889`):

    if self.optimize and self.rigid and self._up_to_date(self.stl_file):
        # Everything below would recompute an artifact that is
        # already on disk and already current. import_optimized()
        # imports it instead; self.model stays unset and is
        # rendered lazily if something actually asks for the
        # presentation.
        if self.model is None:
            self.model = self.artifact_import(self.local_stl)
        assembled = self.import_optimized()

The comment says the model stays unset; the code sets it to the import of
the node's own STL. Only `presentation()` reads a node's model
(`described(self._require_model())`), and only the OpenSCAD writer reads
`presentation()`: `writer.scad_code(node)`, `ScadLeafNode.scad_code` (which
is that), and `OpenScadNode.scad_code` (its source plus the last line of
`scad_text(self.presentation())`). A parent imports a current child through
`import_optimized()`, which calls `artifact_import` itself and never reads
the child's model. `_require_model()` renders and presents on demand when
the model is unset; it exists for exactly this case.

Measured (scratch build directories under the campaign scratchpad's
`cycle16/`):

1. `machinome build tests/scad_where_read_project/machine.py:Machine`,
   twice: `machine-FineCylinder-2111f2f9079a.scad` holds `$fn = 24;`, a
   blank line and `cylinder(h = 8, r = 3);` after each, same inode
   (270007) and stamp. The build path no longer rewrites it.
2. `machinome build ...:FineCylinder` twice, then `machinome snapshot
   ...:FineCylinder -o fine.png --renderer openscad --imgsize 64x48` (real
   OpenSCAD, exit 0): after both builds the file is the geometry (inode
   270022); after the snapshot it is `$fn = 24;`, a blank line and
   `import(file = "machine-FineCylinder-2111f2f9079a.stl", origin = [0, 0]);`
   (84 bytes, inode 269993, the stamp kept at the source's). The renderer's
   `present()` assembles the root, which takes the up-to-date branch, and
   `writer.generate_scad(root)` publishes the leaf's `scad_code` over its
   kept file; the bytes differ, so `currency.publish_text` replaces it.
3. With the STL then deleted, the next build re-renders and rewrites the
   geometry (the file is 35 bytes again): the build heals it only when the
   STL is stale or missing.
4. A fresh instance, loaded with `load_node` and assembled with its STL
   current (`own_text_after_build.py` in the scratchpad), gives as
   `scad_code`: for `FineCylinder`, `$fn = 24;` and the import of its own
   STL; for the `OpenScadNode` `tests/scad_presentation_project/parts.py:
   Plate`, its module source followed by
   `import(file = "plate-__Plate_,_scad_presentation_project_parts.py__-9ea63c013015.stl", origin = [0, 0]);`
   where its build wrote the module call.

The presentation golden (`tests/scad_presentation_golden.py --check`, 34
values, 0 differences, 9 presentation files absent as expected) does not see
this: it assembles one `Bench` instance, builds its STLs and assembles the
same instance again, so every leaf's model was set by the first pass and the
up-to-date branch's `if self.model is None` never fires.
`tests/test_scad_presentation.py`'s
`test_a_scad_authored_root_keeps_its_own_scad` checks that the file exists,
not what it holds. Both pass at `ad08fe8` (22 passed, 23 subtests, 101 s).

An `optimize = False` leaf never takes the up-to-date branch (its condition
starts with `self.optimize`), so the coloured `scad_code` that
`scad-presentation`'s Decision 8 kept for such a leaf is not touched here.

## Goals / Non-Goals

**Goals:** `pip install "machinome[viewer]"` and `[web-snapshot]` bring at
least the viewer the manual describes, from the one statement of it;
`AbstractBaseNode` carries no attribute nobody reads; a SCAD-authored leaf's
own SCAD text is its geometry whether or not its STL is current, so nothing
rewrites its kept `.scad` as an import of the STL it renders.

**Non-Goals:** a run-time viewer version check; a change to what the
OpenSCAD renderer draws for a root outside the family; a change to any
golden value; any project edit.

## Decisions

### 1. The extras' floor is `docs/conf.py`'s `viewer_version`, pinned by test

    viewer = [
        "machinome-viewer>=0.8.0",
    ]
    web-snapshot = [
        "machinome-viewer[snapshot]>=0.8.0",
    ]

with the comment above `viewer` gaining one line: the floor is the matching
viewer `docs/conf.py` states as `viewer_version`, and
`tests/test_release_records.py` holds the two together.

The release fact is stated once (`docs/conf.py`, the write-the-manual
skill's rule), and `pyproject.toml` restates it under a test, as it
already restates the framework's own version for `setup.cfg`,
`machinome/__init__.py` and `machinome/vet/universe.toml`. A release that
moves `viewer_version` and not the extras fails the test naming the extra.

New test in `VersionFilesTest`:

    def test_the_viewer_extras_require_the_matching_viewer(self):
        extras = tomllib.loads((ROOT / 'pyproject.toml').read_text())[
            'project']['optional-dependencies']
        floor = conf_value('viewer_version')
        for extra, requirement in (
                ('viewer', f'machinome-viewer>={floor}'),
                ('web-snapshot', f'machinome-viewer[snapshot]>={floor}')):
            with self.subTest(extra=extra):
                self.assertEqual(extras[extra], [requirement])

Exact equality also refuses an upper bound or a second requirement. Both
extras, not only `viewer`: they install the same distribution, and a floor
on one alone would let `pip install "machinome[web-snapshot]"` keep an
older viewer.

*Alternative:* `>=0.7.0`, the oldest viewer the framework runs against. It
excludes nothing PyPI has ever held, so it changes no installation, and it
is a second viewer fact the records state nowhere (the status page would
still say 0.8 documents need 0.8.0). *Alternative:* no floor, closing the
entry as intended. Then the manual and `context7.json` describe a viewer an
upgraded environment may not have. Both are the pilot's to choose instead
(Open Questions, 1).

### 2. `mesh_stl_file` goes from `__init__` and from `_RESERVED`

Delete the three lines at `base.py:693-695` (the comment and the
assignment) and the name from `_RESERVED`. Nothing else changes: `stl_file`,
`brep_file`, `lock_file` and the rest stay.

Removing the name from `_RESERVED` is a loosening: a parameter, flag,
marking, frame or mate named `mesh_stl_file` is accepted from now on. That
is the rule `_RESERVED` states for itself (the attributes `__init__`
assigns), not a new permission.

Red test in `tests/test_declarative_nodes.py`, beside
`test_a_declaration_cannot_shadow_a_base_attribute`:
`test_a_node_carries_no_mesh_stl_file` (an instance of the module's
`Piston` has no attribute `mesh_stl_file`; fails at `ad08fe8`). A
coherence pin beside it, green before and after:
`test_every_reserved_name_is_an_attribute_a_node_carries` (every name in
`parameters._RESERVED` is an attribute of a `Piston` instance), so the list
and `__init__` cannot drift apart again in the other direction. If any name
other than `mesh_stl_file` fails that pin at `ad08fe8`, the applier records
it and leaves that name alone (it would be a second finding).

### 3. A family leaf leaves its model unset when its STL is current

One private hook on `AbstractBaseNode`, beside `_require_model()`:

    def _current_artifact_presentation(self):
        """This node's presentation when its STL is already current, for a
        caller that asks for it after `assemble()` took the up-to-date
        branch: the import of that STL, which is what the node is. None
        leaves the model unset, to be rendered on demand by
        `_require_model()`."""
        return self.artifact_import(self.local_stl)

and the up-to-date branch reads it:

    if self.model is None:
        self.model = self._current_artifact_presentation()

`ScadLeafNode` (`machinome/node/openscad/leaf.py`) overrides it:

    def _current_artifact_presentation(self):
        """None: a family leaf's presentation is the geometry it authored,
        which its own `.scad` holds and OpenSCAD renders its STL from, so it
        is rendered on demand (`_require_model()`), never the import of
        that STL."""
        return None

The base's docstring names no SCAD (`openscad-node`: the core names no SCAD
outside the family). The assemble comment ("self.model stays unset and is
rendered lazily") is corrected to say what the code then does: the model is
the node's presentation of its current artifact, which for most nodes is
its import and for a node that answers None is rendered when asked.

What this changes, and only this: a family leaf with `optimize` true and a
current STL, assembled by an instance that has not rendered, leaves
`model` None; `presentation()` then renders it (`_prepare()`,
`_require_rendered()`, `present()`, which returns the render), so
`scad_code` is `scad_text` of the authored geometry with the leaf's `fn`,
byte for byte the text its materialization wrote; `OpenScadNode.scad_code`'s
last line is the module call again. `generate_scad()`, and the OpenSCAD
renderer's `present()` for such a root, publish those same bytes, stamp and
record, which `currency.publish_text` leaves in place (same inode). Its cost
is one render of the leaf, paid only when something asks for its SCAD (the
OpenSCAD renderer, a caller of `scad_code`); a build pays nothing, since the
build path never asks.

What it does not change: every other node's up-to-date presentation (an
`StlNode`, a B-rep leaf, a fusion, a flexible leaf), so what the OpenSCAD
renderer draws for those roots is unchanged; an `optimize = False` leaf,
which never takes the branch; the goldens, whose fixture sets every model
in its first pass (Context, 3). `tests/scad_presentation_golden.py --check`
and `tests/expression_type_golden.py --check` stay at zero differences.

*Alternative:* `ScadLeafNode.scad_code` writes `scad_text` of
`described(self._require_rendered())` regardless of the model. It fixes the
same files but also changes an `optimize = False` leaf's `scad_code` from
its coloured presentation (82 bytes in the golden's `InlineCylinder`) to its
uncoloured geometry, reversing what `scad-presentation`'s Decision 8 kept
("The leaf's `scad_code` and its parent's presentation keep the colour"),
and re-records a golden value. *Alternative:* remove the assignment for
every node. Then an OpenSCAD snapshot of a fusion root would draw the union
of its children's imports instead of its fused STL, and render it to do so;
no finding asks for that. *Alternative:* the renderer skips writing a root's
kept `.scad`. It leaves `scad_code` and `generate_scad()` on a current
family leaf giving the self-import, and leaves nothing to draw when the kept
file is missing.

### 4. Docs and changelog

- `docs/reference/api.rst`, the `model` attribute: "The node's presentation
  once assembled, or `None` before" becomes true for every case by naming
  the one exception: an OpenSCAD-family leaf whose STL was already current
  keeps `None` until its presentation is asked for, and is then given its
  render result. One sentence, replacing nothing else.
- `docs/project/changelog.rst`, `Unreleased`, two bullets naming the change:
  the extras require the matching viewer (`pip install -U
  "machinome[viewer]"` now upgrades a 0.7 viewer); an OpenSCAD snapshot no
  longer rewrites a current `Solid2Node`'s or `OpenScadNode`'s own `.scad`
  as an import of its STL, and such a leaf's `scad_code` is its geometry. No
  bullet for `mesh_stl_file`: the attribute was never in the manual and
  nothing in the catalogue reads it; the loosening is recorded here and in
  the resolved record.
- No other page states the extras' requirement or the leaf's `.scad`
  content (`grep` of `docs/` for `machinome-viewer>=`, `mesh_stl`, and the
  `scad_file`/`scad_code` entries, which stay true).

### 5. Red first, and the fixture validation

| Red test | File | Red at `ad08fe8` because |
|---|---|---|
| `test_the_viewer_extras_require_the_matching_viewer` | `tests/test_release_records.py` | `['machinome-viewer'] != ['machinome-viewer>=0.8.0']` |
| `test_a_node_carries_no_mesh_stl_file` | `tests/test_declarative_nodes.py` | the instance has it |
| `test_a_current_leafs_scad_code_is_its_geometry` (subtests `FineCylinder`, `Plate`) | `tests/test_scad_presentation.py` | the fresh instance's `scad_code` imports its own STL |
| `test_a_current_scad_authored_root_keeps_its_scad_as_built` | `tests/test_scad_presentation.py`, `SnapshotOnDemandTest` | the snapshot rewrites the file (new inode, import text) |

The third builds each reference into the test's build directory
(`self.build(...)`, the `_BuildDirectory` helper), loads a fresh instance
with `machinome.core.loader.load_node`, `assemble()`s it, and asserts its
`scad_code` equals the bytes of its `.scad` on disk and contains no
`import(file = "<its own STL name>"`. The fourth builds
`FineCylinder` as the root, records `observed(build_dir)` and the file's
bytes, runs `self.snapshot('openscad', root='FineCylinder')`, and asserts
the text OpenSCAD was given equals those bytes, which equal the golden's
`FineCylinder` digest (`golden_file_digest`), and that `observed()` is
unchanged.

Fixture validation, before and after: `tests/scad_presentation_golden.py
--check` (0 differences both times), `tests/test_scad_presentation.py` in
full, and the measurement of Context, 3, item 2 repeated with real OpenSCAD
(the file's bytes and inode unchanged by the snapshot, the PNG written).

## Risks / Trade-offs

- [The floor forces an upgrade the framework does not technically need] →
  that is the effect of naming the matching viewer, and the reason the
  choice is recorded for the pilot (Open Questions, 1). A user who must
  keep 0.7.x installs the framework without the extra.
- [A user's code read `node.mesh_stl_file`] → none in the catalogue; it
  named a file nothing writes, so a reader would have found nothing there.
- [Rendering a family leaf on demand costs more than importing its STL for
  an OpenSCAD snapshot of it as a root] → one SolidPython render, or one
  parse of an `OpenScadNode`'s library, paid only by that snapshot; OpenSCAD
  then draws the geometry instead of the STL, which is what that file is.
- [A family subclass relied on `model` being set after an up-to-date
  `assemble()`] → nothing in `machinome/` or the tests reads a node's model
  outside `presentation()` (Context, 3); `test_source_set.py`'s
  `node.model` read is a `CadQueryNode`'s, outside the family.

## Migration Plan

None. An environment upgrades the viewer on its next install of the extra.
A kept `.scad` that an earlier OpenSCAD snapshot rewrote as a self-import is
written again from the leaf's geometry the next time anything publishes it:
the next OpenSCAD snapshot of that root, or the next build that re-renders
the leaf.

## Open Questions

1. **Which viewer does 0.8.0 require?** (the pilot) The records disagree.
   `docs/conf.py`, its test, `context7.json`, the install, publishing and
   upgrading pages name one *matching* viewer, 0.8.0 with API 29, and
   `docs/project/status.rst` says the documents 0.8 exports "need the
   matching viewer |viewer_version|, API |viewer_api|". The 0.8 release
   note, the 0.8.0 changelog section, the upgrading page and the viewer's
   own changelog say the documents keep versions 1 to 13, "so a 0.7 viewer
   reads them"; the framework uses nothing viewer 0.7.0 lacks (Context, 1).
   Choices: (a) floor at the matching viewer, `>=0.8.0`, held to
   `viewer_version`, which moves with every release; (b) floor at the oldest
   viewer the framework runs against, `>=0.7.0`, a new fact with no home in
   `docs/conf.py`, which changes no installation today; (c) no floor, and the
   entry closed as intended. *Recommendation:* (a). Every record that names
   a viewer for this release names 0.8.0, the viewer and framework are
   released together and numbered together, and "install both with `pip
   install "machinome[viewer]"`" is true of an upgrade only with this floor;
   the "0.7 viewer reads them" sentences are about reading a published
   document, not about what the extra installs. Independently of the
   choice, the status page's "need the matching viewer" overstates what a
   document needs (API 27 reads schemas 11 to 13); whether to soften it is
   the same decision and is left to it. This proposal is written for (a);
   under (b) only the number and the test's source of it change, and under
   (c) the first item is dropped and the entry closed with Context, 1 as its
   measurement.

   Answered by the orchestrator at review (7 October 2026): deferred to
   the pilot. The records of a released version disagree about what the
   extra should install, and which of (a), (b) or (c) is right is a
   release decision; the campaign note records the disagreement and the
   three choices under "Deferred to the pilot". This change therefore
   takes items 2 and 3 only: the applier removes item 1 from the
   proposal, the tasks, the `viewer-distribution` delta and the
   changelog, leaves the extras as they are, and keeps the `warts.md`
   entry with a "**Remaining (2026-10-07)**" note pointing at that
   decision.
