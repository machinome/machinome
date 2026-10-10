## Context

### The bench

`/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch `fix-warts-3`,
at `5a71304`. Commands run as
`env -C <bench> PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/<tool>`;
`import machinome` resolves to `<bench>/machinome/__init__.py`. trimesh is
4.4.9 (`pyproject.toml` pins `trimesh==4.4.*`); the workspace venv also
holds `networkx` 3.6.1, installed by hand and required by nothing in it
(`pip show networkx`: "Required-by:" empty).

### 1. Where the framework counts bodies on a mesh

- `assertNoDisconnectedSolids` (`machinome/test.py:2296`): for each topmost
  rigid solid that does not route to the B-rep engine,
  `len(cached_base_mesh(solid.stl_file).split(only_watertight=False))`.
  This is the path of every `StlNode`, of every solid on a `--mesh` run,
  and of every solid with no B-rep geometry on a `--brep` run.
- `_body_count` (`machinome/test.py:453`), read by `assertJoined`'s mesh
  branch (`machinome/test.py:2605`) on the union the mesh engine returns:
  `len(mesh.split(only_watertight=False))`.
- `machinome/node/stl.py:_bodies` (line 83), which selects a body of a
  multi-body STL: `mesh.split(only_watertight=False, repair=False)`, with a
  docstring saying the default repair "fills the holes of every component
  it splits out -- silently machining geometry the project did not author".

No other framework call reaches a trimesh function that uses `networkx`
(investigation 3's grep of `machinome/` for `fill_holes`, `fix_normals`,
`fix_winding`, `vertex_adjacency_graph`, `trimesh.graph`, `trimesh.path`,
sections and slices).

### 2. What trimesh 4.4.9 does with `repair`

Read in the venv's `site-packages/trimesh`:

- `Trimesh.split` calls `graph.split(mesh, only_watertight, ...)`, which
  finds the components with `connected_components` (engine `scipy` first,
  a core dependency, so `networkx` is not used there) and returns
  `mesh.submesh(components, only_watertight=only_watertight, **kwargs)`.
- `util.submesh(mesh, faces_sequence, repair=True, only_watertight=False,
  ...)` builds `result`, one `Trimesh` per non-empty component, and then:

      if only_watertight or repair:
          watertight = [i.fill_holes() and len(i.faces) >= 4 for i in result]
      if only_watertight:
          return [i for i, w in zip(result, watertight) if w]
      return result

  With `only_watertight=False` it returns `result` whatever `repair` is.
  `fill_holes` adds faces to a component in place; it cannot add, remove
  or merge components. **The number of components returned does not depend
  on `repair`**; `repair=True` can only add an exception.
- `repair.fill_holes` returns early for a component of fewer than three
  faces or a watertight one; otherwise, with three or more boundary edges,
  it calls `nx.from_edgelist` and `nx.cycle_basis`. `nx` is
  `try: import networkx as nx except: nx = ExceptionWrapper(E)`, which
  raises the import error on first use. So every component that is not
  watertight and has three or more boundary edges needs `networkx`, whatever
  the size of its holes.
- trimesh's metadata: `Requires-Dist: networkx; extra == "easy"`. machinome
  declares no trimesh extra; `requirements.txt` and `requirements_dev.txt`,
  which CI installs, name no `networkx`.

### 3. Measurements

**Six fixtures, `networkx` refused** (`<scratch>/networkx_hidden.py`,
investigation 3's script, re-run at `5a71304`: a `sys.meta_path` finder at
position 0 refusing `networkx`, then `assertNoDisconnectedSolids` on a
`tests.stand_in.NodeDouble` over each exported STL, both raw splits and
`_body_count`):

| Fixture | watertight | assertion, as today | `_body_count`, as today | `repair=False` |
|---|---|---|---|---|
| connected box | yes | passes | 1 | 1 |
| disconnected pair | yes | fails, names 2 bodies | 2 | 2 |
| open box, 1 triangle missing | no | `ModuleNotFoundError` | `ModuleNotFoundError` | 1 |
| open box, 2 triangles missing | no | `ModuleNotFoundError` | `ModuleNotFoundError` | 1 |
| open tube, both ends open | no | `ModuleNotFoundError` | `ModuleNotFoundError` | 1 |
| disconnected open pair | no | `ModuleNotFoundError` | `ModuleNotFoundError` | 2 |

Every `ModuleNotFoundError` is raised at `trimesh/repair.py:261 fill_holes`.
With `networkx` present the same script gives the expected count at both
`repair` values for all six, and the assertion passes the four connected
fixtures and fails the two disconnected ones naming 2 bodies.

**The suite's own finder.** `<scratch>/red_test_sketch.py` runs a snippet
through `tests.mesh_engine_absent.run_python(SNIPPET, absent=('networkx',))`
on an open box: exit 0, `CONNECTIVITY ModuleNotFoundError No module named
'networkx'` and `BODY COUNT ModuleNotFoundError No module named 'networkx'`.
trimesh asks for `networkx` at import from nine modules
(`trimesh.base`, `trimesh.graph`, `trimesh.repair`, `trimesh.poses`,
`trimesh.path.path`, `trimesh.path.polygons`, `trimesh.path.traversal`,
`trimesh.exchange.threemf`, `trimesh.exchange.threedxml`) and copes with
its absence there, so "never asked for" cannot be the test's claim; the
verdicts can.

**Counts over the catalogue, read only** (`<scratch>/repair_count_survey.py`:
every `.stl` under the four projects that combine
`require_watertight = False` with `assertNoDisconnectedSolids`, excluding
`WTs`, `.git`, `.venv` and `node_modules`, loaded as `cached_base_mesh`
loads, `trimesh.load(BytesIO, file_type='stl')`, then counted at both
`repair` values, `networkx` present):

    465 meshes, 157 not watertight, 0 counts differ, 0 errors, 84.5 s

| Project | STL files | not watertight |
|---|---|---|
| `Robotic-Arms/SO-ARM100` | 164 | 24 |
| `Robots/roboto_origin` | 198 | 126 |
| `Robots/hexapod_spiderbot_model` | 83 | 3 |
| `Calculators/mechanical-multiplier` | 20 | 4 |

The open meshes range from one face to 752,714 faces and from 1 to 3,833
components.

**SO-ARM100** (`/home/asa/devel/machinome/projects/Robotic-Arms/SO-ARM100`,
branch `frames-and-mates`, `4438106`), its README's three
`machinome test --mesh` commands, run by `<scratch>/so_arm100_mesh.py`
through `tests.mesh_engine_absent.run_machinome` with
`cwd=<project>`, `SOLID_BUILD_DIR=<scratch>/so-arm100-build` and
`PYTHONDONTWRITEBYTECODE=1`; a marker file touched before the first run and
`find <project> -newer <marker> -not -path '*/.git/*'` after the last
listed nothing:

| Suite | `networkx` present | `networkx` refused |
|---|---|---|
| `simulation/parts.py` | 4 passed, 0 failed, 1.5 s | 3 passed, 1 failed (`ImportedPartTest.test_each_selected_body_is_connected`), 1.2 s |
| `simulation/hardware.py` | 5 passed, 0 failed, 3.3 s | 5 passed, 0 failed, 2.8 s |
| `simulation/so_arm100.py` | 12 passed, 0 failed, 39.4 s | 11 passed, 1 failed (`SOArm100Test.test_solid_integrity`), 38.9 s |

Both failures are `ModuleNotFoundError: No module named 'networkx'` from
`fill_holes`, reached from `assertNoDisconnectedSolids` at
`machinome/test.py:2310`. The open meshes they reach are the
`LowerArmBody0..7` STLs split from `Lower_Arm.stl` (8 bodies, admitted with
`require_watertight = False`): bodies of 1, 6, 2,340 and 4,586 faces, none
watertight.

## Goals / Non-Goals

**Goals:**

- Both connectivity assertions count the bodies of a mesh that is not
  watertight in an environment holding only machinome's declared
  dependencies.
- Every count, and so every verdict, the assertions reach today is reached
  unchanged.
- One spelling of "count the bodies of a mesh" in `machinome/test.py`.

**Non-Goals:**

- Any change to which geometry is admitted (`require_watertight`) or to the
  B-rep path (`solid_count`).
- Declaring `networkx`, or any new dependency.
- The 3MF reader `StlNode` would reach through `trimesh.load` for a
  `.3mf` `stl_source` (investigation 3, "Adjacent, not verified").

## Decisions

### 1. Stop asking for the repair, rather than declare its dependency

Chosen: split with `repair=False`. The count is the only thing read, it is
independent of `repair` by construction (Context, 2), and the framework's
rule for imported geometry is that nothing is ever repaired (ADR-054,
`docs/architecture.md`, the `StlNode` paragraph); `node/stl.py:_bodies`
already follows it.

Alternatives:

- **Declare `networkx`.** It would have to be a core dependency:
  `test_connectivity_asserts_without_the_mesh_engine` pins that
  `assertNoDisconnectedSolids` needs no mesh engine, so a `mesh`-extra
  declaration would leave the B-rep install's STL path broken. A core
  dependency for work whose result is discarded, and the per-component
  repair would keep running on every open mesh.
- **Catch the `ModuleNotFoundError` and retry with `repair=False`.** Two
  code paths for one count, and a fallback the framework's dependency
  contracts refuse elsewhere ("never substitute"). No reason to keep the
  first path.

### 2. One counting function

`assertNoDisconnectedSolids` calls `_body_count` on the cached base mesh
instead of spelling its own `split`. `_body_count` keeps its name and
place; it is private, and its only readers are these two assertions.

The code, `machinome/test.py`:

    def _body_count(mesh):
        """Number of connected components in `mesh`, counted as the mesh
        holds them.

        `only_watertight=False` is deliberate: the question is whether the
        geometry hangs together, and a fragment that is itself watertight
        is exactly the case worth catching -- filtering to watertight
        components would silently drop the evidence.

        `repair=False` is deliberate too. Left at its default, trimesh
        fills the holes of every component it splits out, machining
        geometry the project never authored; filling a hole inside a
        component cannot change how many components there are, and the
        repair is the one step of the split that needs `networkx`, which
        machinome does not depend on.
        """
        return len(mesh.split(only_watertight=False, repair=False))

and in `assertNoDisconnectedSolids`'s mesh branch:

                bodies = _body_count(cached_base_mesh(solid.stl_file))
                source = 'STL'

`cached_base_mesh` returns the cached mesh itself; `split` does not modify
the mesh it splits (it reads its faces and caches its adjacency), with
either `repair` value, so sharing the cached mesh is as safe as today.

### 3. The proof

**Red:** `tests/test_connectivity.py`, a new class
`CountWithoutRepairTest`:

- `test_open_meshes_are_counted_where_networkx_is_absent`: a snippet run by
  `tests.mesh_engine_absent.run_python(SNIPPET, absent=('networkx',))`.
  The snippet builds a connected open box (a `trimesh.creation.box` with its
  first face removed, `process=False`) and a disconnected open pair (two
  such boxes, centres 5 mm apart along x, concatenated), exports each to an STL in a
  `tempfile.mkdtemp()` directory, wraps each in
  `tests.stand_in.NodeDouble(name=..., stl_file=path, rigid=True,
  children=(), _parent=None, operations=[])`, and prints one line per
  question: the outcome of `TestCase().assertNoDisconnectedSolids(node)`
  (`PASSED`, or the exception's type and message) and of `_body_count` on
  the reloaded mesh (the count, or the exception). The test asserts the
  subprocess exited 0, `ModuleNotFoundError` is nowhere in its output, the
  connected box passed, the pair failed with `AssertionError` naming
  `2 connected bodies`, and the counts are 1 and 2. On the unmodified bench
  it fails on `ModuleNotFoundError` (Context, 3). It asserts verdicts, not
  that `networkx` was never asked for: trimesh asks at import.
- `test_counts_are_the_bodies_the_mesh_holds`, in-process, over the six
  fixtures of Context, 3, each exported to STL and reloaded: a subtest per
  fixture asserting `_body_count` is the expected count (1, 2, 1, 1, 1, 2)
  and that `assertNoDisconnectedSolids` passes a one-body fixture and fails
  a two-body one naming `2 connected bodies`. Green before and after: the
  guard that the change moves no verdict where `networkx` is installed.
- `test_counts_match_the_repairing_split`, decorated
  `skipUnless(networkx is importable)`: for the same six fixtures,
  `_body_count(mesh) == len(mesh.split(only_watertight=False,
  repair=True))`. Green before and after in the workspace venv (which has
  `networkx`); it skips under CI's requirement files, which install none,
  and evidence must show it ran rather than skipped.

The fixtures are module-level helpers in the test file, built as
`<scratch>/networkx_hidden.py` builds them (`one_body`, `two_bodies`
already exist in the file; `open_box(missing)`, `open_tube()` and
`open_pair()` are added beside them).

**Project:** SO-ARM100's three `--mesh` suites with `networkx` present and
refused, before and after, by `<scratch>/so_arm100_mesh.py` as in Context,
3. After the change the refused runs must equal the present runs (4, 5 and
12 passed, 0 failed), and the present runs must equal their own baseline.
Nothing may be written into the project.

**Catalogue counts:** `<scratch>/repair_count_survey.py` once more after the
change is not needed: it calls trimesh directly, not the framework. The
in-process guard covers the framework's count.

### 4. Docs and changelog

No manual page is wrong after the change: `docs/reference/assertions.rst`
says "a split of the part's own STL", `docs/reference/api.rst` says "one
connected body", `docs/architecture.md` says of imported meshes "nothing is
ever auto-repaired" and of the assertion that "it reads each topmost rigid
node's local STL". None names `networkx` or the repair.

Changelog, `docs/project/changelog.rst`, under `Unreleased`, after the
existing bullets:

    * **An open part is counted where networkx is not installed.**
      ``assertNoDisconnectedSolids`` on a part whose STL is not watertight,
      such as an ``StlNode`` declaring ``require_watertight = False``, and
      ``assertJoined`` on meshes, failed with ``ModuleNotFoundError: No
      module named 'networkx'`` where that package, which machinome does not
      depend on, was not installed: counting a mesh's bodies asked trimesh
      to fill each body's holes first, and only that repair needs it. Bodies
      are now counted as the mesh holds them, with no repair, and every
      count is the one it was (count-bodies-without-repair).

## Risks / Trade-offs

- **A verdict could move.** Not by construction (Context, 2), not on the
  six fixtures and not on the 465 catalogue meshes (Context, 3). The
  in-process guard and the repairing comparison pin it.
- **A trimesh upgrade could change `submesh`.** `pyproject.toml` pins
  `trimesh==4.4.*`; the repairing comparison would catch a later trimesh
  whose count depended on the repair.
- **The red test spawns a Python subprocess** (about a second, trimesh's
  import), like every other test built on `tests.mesh_engine_absent`.

## Open Questions

1. **Can removing the repair change a verdict on any mesh?** No. trimesh
   4.4.9's `util.submesh` returns the same list of components with or
   without `repair` when `only_watertight=False`; the repair fills holes in
   place and only adds an exception. Measured: 0 of 6 fixtures and 0 of 465
   catalogue STL files (157 not watertight, up to 3,833 components) count
   differently between `repair=True` and `repair=False`. Recommendation:
   proceed; nothing to bring to the pilot. Answered by this proposal's
   measurement; confirmed by the orchestrator at review (7 October 2026).
2. **Should the repairing comparison run in CI?** It cannot without
   installing `networkx`, which is the dependency this change removes the
   need for. Recommendation: let it skip there and run in the workspace
   venv; the red test and the count guard run everywhere. Answered by the
   orchestrator at review (7 October 2026): let it skip in CI.
