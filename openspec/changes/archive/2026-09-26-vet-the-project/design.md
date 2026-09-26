## Context

The design note `workflow/ongoing/vet.md` (settled with the pilot on
2026-09-26) is the brief. This design turns it into modules, data and
rules, and leaves its decisions alone. The first draft of this design
raised nine questions from a re-survey of the catalogue; the pilot
decided them on 2026-09-26, accepting the reviewer's recommendation, and
the last section records each decision. No question remains open.

Current state:

- `machinome.core.loader` discovers the manifest (`_find_manifest`,
  `project_root`, `read_project`). It imports `machinome.node.base` at
  module scope, and that brings numpy and its family with it.
  `read_project` also imports `machinome.core.builder` for the build
  root, which brings watchdog, the serializer, the pieces and the viewer
  bundle. `machinome/core/__init__.py` imports the loader, so every
  module under `machinome.core` pays that price.
- `machinome.node.sources.source_closure` walks project imports
  statically, but it computes each file's package from `sys.modules`
  (`_package_of`). It therefore only works after the model has been
  imported, which is exactly what vet must never do.
- The browser-engine prototype's `scripts/walk-imports.py` (another
  repository, read only) resolves dotted and relative imports to paths
  from the filesystem alone. Its `resolve` function handles a package's
  own `__init__.py` correctly. It is the right ancestor for vet's
  resolver, but its scope rule is wrong for vet: it deliberately skips
  imports inside function bodies and `try/except ImportError` blocks,
  and vet has to count both.
- The source adapters resolve `stl_source`, `step_source`, `scad_source`
  and `jscad_source` by joining the declared value to the directory of
  the declaring module and taking the real path
  (`node/adapters/{stl,step,openscad,jscad}.py`), then call
  `require_source_file` (`node/sources.py`), which refuses a missing
  file (`MissingSourceFile`) or a path that is not a regular file
  (`ValueError`). Nothing refuses a source outside the project: an
  absolute `step_source` is documented as resolving to itself. The
  marking artwork (`node/markings.py`, `Svg.resolve`) is admitted through
  the same function.
- Companion tests are named by `loader.load_tests`: `test_<name>.py`
  beside `<name>.py`, and `test.py` beside `__init__.py`.
  `manager/test.py:resolve_path` applies the same rule in reverse.

## Goals / Non-Goals

**Goals:**
- `machinome vet [reference] [--tests] [--json]` returns a deterministic
  verdict computed from the project tree's bytes and the universe
  declaration alone.
- The three assertions of the note, each with an honest statement of
  what it does and does not prove.
- A host (machinome.org intake first) can read the result as one JSON
  object, and the exit status carries the verdict.
- Vet costs nothing at import time: no kernel, no node package, no
  loader.
- Every declared adapter source is contained in its project at
  construction, whatever expression computed it.

**Non-Goals:**
- Sandboxing. Vet is a static check. The runtime that lacks a
  capability is the sandbox.
- Parsing OpenSCAD or JavaScript.
- Proving that a computed read stays inside the project. The runtime
  bounds it; for a declared source, the adapters do.
- Universe profiles, such as the narrower browser universe. There is one
  universe now, and it has a name so that a second one can be added
  later.
- Wiring vet into machinome.org, the studio floor or browser delivery.
  Each is a change in its own repository.
- A manifest key that declares a project pure, and any fix to the
  projects the first vet flags.

## Decisions

### D1. The manifest module is `machinome/manifest.py`, top level

It cannot live under `machinome/core/`, because importing any
`machinome.core.*` module first runs `machinome/core/__init__.py`, which
imports the loader. So it sits beside `machinome/parameters.py`, the
existing precedent for a top-level module that costs nothing to import.

It receives, unchanged in behaviour:

- `ProjectManifestError`
- `MODEL_NAME`
- `_find_manifest(origin)`, including the `[tool.solid-node]` refusal
- `project_root(origin)`
- a new `read_declaration(origin)`. It returns a frozen `Declaration`
  with `root`, `manifest`, `models` (a tuple of `(name, reference)`
  pairs in declaration order, `name` None for a single `model`),
  `default` (a name, or None) and `named`. Every validation that
  `read_project` performs today moves with it: the model-name pattern,
  the `package.module:Class` form, the root-directory collision check,
  a default that must name a declared model, and an empty or missing
  table.

`machinome.core.loader` imports these names from `machinome.manifest`,
so `loader.ProjectManifestError is manifest.ProjectManifestError`, and
it keeps them in its namespace for every existing importer
(`manager/*`, `node/sources.py`, `node/base.py`, `core/pieces.py`,
tests). `read_project` stays in the loader. It becomes the declaration
plus build directories: `project_build_root(root)` and each named
model's `<build root>/<name>`. `Model`, `Project`, `select_model` and
the rest stay where they are. Outside the loader, only
`node/sources.py` changes: `require_source_file` imports
`machinome.manifest` directly for the containment check of D10.

*Alternative considered:* moving `read_project` itself and passing the
build root in. That would drag the builder's `_anchored` state into the
light module, or make its signature odd. The declaration is what vet
needs, and a build directory means nothing to vet.

### D2. Module layout

- `machinome/vet/__init__.py`: `vet(origin=None, reference=None,
  tests=False)`, which returns a `Report`, plus the text and JSON
  rendering.
- `machinome/vet/universe.toml`: the declaration (D3), located
  beside `__file__` and read with `tomllib`. It ships as package
  data (`include-package-data = true` plus a `MANIFEST.in` line), and
  `setup.cfg` registers it with bumpversion (D3).
- `machinome/vet/resolve.py`: the static resolver (D4).
- `machinome/vet/assertions.py`: the per-file AST visitor that raises
  the findings of assertions 2 and 3, and records imports for
  assertion 1.
- `machinome/manager/vet.py`: the command class `Vet`, with
  `needs_node = False`. It declares its own `reference` positional,
  `--tests` and `--json`, and it is registered in `COMMANDS` after
  `import-step`.

The modules use `ast`, `os`, `json`, `tomllib`, `dataclasses` and
`machinome.manifest`, and nothing else.

### D3. The universe declaration

```toml
[universe]
name = "machinome"
version = "0.7.0"          # equals machinome.__version__; a test pins it,
                            # and setup.cfg's bumpversion rewrites it

[contract]                  # allowed whole, minus `deny`
members = ["machinome", "machinome_mechanics", "molejo"]

# The framework's own modules that spawn processes, write to a
# caller-chosen path, or import by name (D6). Kind `framework-internal`,
# matched exactly as the kernel denylist is.
deny = [
  "machinome.cli", "machinome.manager",
  "machinome.core.builder", "machinome.core.processes",
  "machinome.core.loader", "machinome.core.export",
  "machinome.core.pieces",
  "machinome.source_generation", "machinome.viewers", "machinome.sphinx",
  "machinome.currency", "machinome._artifact",
]

[kernels]                   # allowed, minus the denylists below
members = ["cadquery", "build123d", "OCP", "solid2", "trimesh",
           "numpy", "scipy", "manifold3d", "shapely"]

# Dotted names. A name reached by import or by an attribute chain on an
# import-bound name is denied when it equals, or lies beneath, one of these.
deny = [
  # cadquery importers and exporters
  "cadquery.importers", "cadquery.exporters",
  "cadquery.occ_impl.importers", "cadquery.occ_impl.exporters",
  # build123d importers, exporters and mesher
  "build123d.importers", "build123d.exporters", "build123d.exporters3d",
  "build123d.mesher", "build123d.Mesher",
  "build123d.import_brep", "build123d.import_step", "build123d.import_stl",
  "build123d.import_svg", "build123d.import_svg_as_buildline_code",
  "build123d.import_svg_document",
  "build123d.export_brep", "build123d.export_gltf", "build123d.export_step",
  "build123d.export_stl", "build123d.ExportDXF", "build123d.ExportSVG",
  "build123d.Export2D",
  # OCP STEP/IGES/STL readers and writers, and the file-level exchange
  "OCP.STEPControl", "OCP.STEPCAFControl", "OCP.IGESControl",
  "OCP.IGESCAFControl", "OCP.StlAPI", "OCP.RWStl", "OCP.RWGltf",
  "OCP.VrmlAPI", "OCP.XSControl", "OCP.IFSelect", "OCP.DE", "OCP.OSD",
  "OCP.BinTools", "OCP.BRepTools.BRepTools.Write_s",
  "OCP.BRepTools.BRepTools.Read_s",
  # trimesh loaders and exchange
  "trimesh.load", "trimesh.load_mesh", "trimesh.load_path",
  "trimesh.load_remote", "trimesh.exchange", "trimesh.resources",
  "trimesh.interfaces",
  # numpy file IO
  "numpy.load", "numpy.save", "numpy.savez", "numpy.savez_compressed",
  "numpy.fromfile", "numpy.loadtxt", "numpy.savetxt", "numpy.genfromtxt",
  "numpy.memmap", "numpy.fromregex", "numpy.lib.npyio", "numpy.lib.format",
  "numpy.ctypeslib", "numpy.f2py",
  # scipy file IO
  "scipy.io", "scipy.datasets",
  # solid2 render-to-file
  "solid2.scad_render_to_file", "solid2.render_to_stl_file",
]

# Attribute names that do file IO on a kernel object. Matched only on a
# receiver no import bound (a call result, a local, `self.x`).
deny_methods = [
  "export", "exportBin", "exportBrep", "exportStep", "exportStl",
  "exportSvg", "importBin", "importBrep", "importStep", "importDXF",
  "save", "load", "dump", "tofile", "save_image",
  "save_as_scad", "save_as_stl",
]

[stdlib]
members = ["math", "cmath", "fractions", "decimal", "statistics",
           "itertools", "functools", "operator", "collections",
           "dataclasses", "enum", "typing", "abc", "numbers", "re",
           "string", "json", "hashlib", "struct", "copy", "contextlib",
           "random", "bisect", "heapq", "xml.etree", "__future__",
           "ast", "os", "pathlib"]

# A restricted member admits the member itself and only the dotted names
# at or beneath one of its allowed prefixes. Anything else under it is
# `outside-universe`, named by the member and its next component.
[stdlib.restricted]
os = ["os.path", "os.listdir", "os.scandir", "os.walk"]

[tests]                     # added only for files reached solely
members = ["unittest", "pytest", "logging"]   # through a companion under --tests

[routes]
dynamic_builtins = ["exec", "eval", "compile", "__import__"]
dynamic_modules = ["importlib", "runpy"]
import_system = ["sys.path", "sys.modules"]
dunders = ["__subclasses__", "__globals__", "__builtins__", "__loader__",
           "__spec__", "__code__", "__closure__", "__mro__", "__bases__",
           "__base__", "__path__"]
denied_builtins = ["breakpoint", "help", "input"]

[writes]                    # kind `file-write`
open = "open"               # the built-in, and any `.open` method
write_modes = ["w", "a", "x", "+"]
# Mutating pathlib methods, matched by name on any receiver.
methods = ["write_text", "write_bytes", "mkdir", "unlink", "rmdir",
           "touch", "chmod", "lchmod", "symlink_to", "hardlink_to"]

[sources]
attributes = ["stl_source", "step_source", "scad_source"]
refused = ["jscad_source"]
```

The three member lists, the dynamic routes and the four source
attributes are the note's. The stdlib additions (`os` restricted,
`pathlib`), the contract denylist, the tests tier, `__path__` and the
`[writes]` table are the pilot's decisions of 2026-09-26 (last section).
The note describes the kernel denylist by category ("importers and
exporters, STEP/IGES/STL readers and writers, numpy load/save/…,
`scipy.io`, solid2's render-to-file"). The dotted entries above spell
those categories out against the installed kernels (cadquery 2.7,
build123d 0.10, OCP 7.8, trimesh 4.4, numpy 2.2, solidpython2 2.1,
shapely 2.1), as surveyed on 2026-09-26.

A universe member matches by prefix on dotted components. `xml.etree`
admits `xml.etree.ElementTree`, but not `xml` or `xml.sax`. A restricted
member is judged on the full dotted name: `os`, `os.path`,
`os.path.join`, `os.listdir` and `os.walk` pass (a directory listing is a
read), `os.makedirs` and `os.environ.get` are reported as
`os.makedirs` and `os.environ`. `from os import *` is reported as `os.*`,
because what it binds cannot be judged.

The declaration names the framework version, so it joins the three files
`setup.cfg` already rewrites on a release:

```ini
[bumpversion:file:machinome/vet/universe.toml]
search = version = "{current_version}"
replace = version = "{new_version}"
```

The search string is unique in the file (`[universe] version` is its only
`version` key). The equality test against `machinome.__version__` stays,
so a release made without bumpversion still cannot ship a stale
declaration.

### D4. The static resolver

Paths are real paths. The import root is the project root: the loader
inserts it at `sys.path[0]` (`_seed_project_path`), so vet resolves the
project first, the same way the runtime does.

- **Entry.** For each model, the reference is split as the loader
  splits it (`_reference_parts`, reimplemented without the loader). A
  qualifier `a.b.c` is resolved as an import of `a.b.c`. A path is
  taken as a file relative to the working directory. The class part is
  ignored. An entry that is not a `.py` file under the root raises
  `unresolved-reference`.
- **Dotted name `a.b.c`.** Try `a` under the root: `a.py`, `a/__init__.py`,
  or a namespace directory `a/`. If `a` is found, every prefix package's
  `__init__.py` (when present) and the final module are vetted.
  `import a.b.c` reaching a missing component raises `unresolved-import`.
  If `a` is not under the root, the name is checked against the universe
  (D5).
- **Relative import** (`level > 0`). Resolved against the importing
  module's package, using `walk-imports.py`'s rule: inside `pkg/__init__.py`
  the package is `pkg` itself. A relative import that climbs above the
  root raises `unresolved-import`.
- **`from p import n`.** If `p.n` resolves to a module under the root it
  is vetted. Otherwise `n` is a name inside `p` and adds nothing. For a
  universe `p`, `p.n` is the dotted name checked against the denylists
  and restrictions.
- **`from p import *`** from a project package vets every `*.py` directly
  inside `p`'s directory. This over-approximates `__all__`, and is sound
  whatever `__all__` says or computes.
- **Scope.** Every import node anywhere in the file counts: module
  level, class bodies, function bodies, conditionals and guarded `try`
  blocks.
- **Escape.** A resolved file whose real path is not under the root's
  real path raises `escaped-module` and is not vetted.
- **Shadowing.** Every `X.py` and every directory `X/` directly at the
  root, where `X` is the first component of a universe member (the tests
  tier included), raises `shadowing` at that file, whether or not it is
  imported.
- **Parsing.** Files are read as bytes and parsed with `ast.parse(bytes)`,
  which honours PEP 263 coding declarations and BOMs, as `walk-imports.py`
  does. A `SyntaxError`, `ValueError` or `UnicodeDecodeError` raises
  `unparseable` with the parser's line, or null. Such a file contributes
  no imports.
- **Worklist.** A worklist runs over real paths with a visited set, so a
  cycle terminates. Every file is parsed once per run, even when several
  models share it, and judged at most once per mode (model rules, or
  model rules plus the tests tier; D7).

*Why not `node/sources.py`:* it resolves relative imports through
`sys.modules`, so the model has to be imported first. It also silently
drops unparseable files, which vet has to report.

### D5. The three assertions and what each proves

The finding kinds are exactly sixteen: `outside-universe`, `kernel-io`,
`framework-internal`, `file-write`, `dynamic-route`, `import-system`,
`denied-dunder`, `denied-builtin`, `shadowing`, `unparseable`,
`unresolved-import`, `escaped-module`, `unresolved-reference`,
`source-absolute`, `source-escapes`, `jscad-source`.

**1. Closure** (kinds `outside-universe`, `unresolved-import`,
`escaped-module`, `unresolved-reference`, `shadowing`, `unparseable`).
Every import statement in a vetted file resolves either to a vetted
project file or to a universe member, and a restricted member's use stays
within its allowed prefixes. *Soundness:* sound for every import written
as a statement, because Python executes no project file that is not
reached by an import statement from a model, by a package `__init__` on
such a path, or by a route that assertion 2 forbids. Shadowing closes the
case where a universe name resolves to project code. The contract tier is
trusted whole outside its denylist (D6).

**2. No dynamic route and no write** (kinds `dynamic-route`,
`import-system`, `denied-dunder`, `denied-builtin`, `kernel-io`,
`framework-internal`, `file-write`). The visitor flags:

- a `Name` node whose id is in `dynamic_builtins` or `denied_builtins`
  and that the file does not bind itself (the bound-name rule below):
  a call, an alias (`f = eval`) or an argument;
- an import of a `dynamic_modules` name, reported as `dynamic-route`
  instead of `outside-universe`;
- any attribute chain that resolves, through import bindings, to
  `sys.path` or `sys.modules`, including `from sys import path`;
- any `Name` whose id is a denied dunder (`__builtins__`, and
  `__path__` inside a package `__init__`), any `Attribute` whose `attr`
  is one, and any string `Constant` equal to one, including inside
  f-strings;
- kernel IO and framework internals, as in D3;
- writes, as below.

Import bindings are tracked per file. A name bound by `import x`,
`import x as y` or `from p import n` maps to its dotted target. An
`Attribute` chain whose root `Name` is import-bound is expanded to a
dotted name and checked against the kernel `deny`, the contract `deny`,
the restrictions and `import_system`. A `kernel-io` or
`framework-internal` finding names the denylist entry matched
(`cadquery.importers`, `machinome.core.loader`); a restriction finding
names the member and its next component (`os.makedirs`). An `Attribute` whose root is not
import-bound is checked against `deny_methods` alone. A local rebinding
(`np = something`) is not tracked.

*Bound names.* A name the file binds anywhere is the project's name, not
the built-in's, and raises no `dynamic-route`, `denied-builtin` or `open`
finding. One `ast.walk` pass per file, beside the import bindings,
collects every name stored to (any assignment target, including a
class-body, augmented or annotated assignment and a tuple target, and a
`for`, `with`, comprehension or walrus target), every `def` and `class`
name, every parameter, every `except ... as` name, every `match` capture
and every imported name. Poleni-1709 and Pascaline-module declare a child
`input = InputArbor()` in a class body and write `input.turn.drives(...)`;
the first draft's "in any context" rule reported `denied-builtin` there,
wrongly. Scope is not tracked, so the residual is a file that binds
`eval` somewhere and also calls the built-in elsewhere: it is not caught.
Only an author setting out to evade vet writes that. The dunder rule is
unchanged: a denied dunder is a finding however it is bound.

*Writes.* A call to the built-in `open` is judged on its mode: the second
positional argument or the `mode=` keyword. A call to any `.open`
attribute is judged on its first positional argument or `mode=`, which
is where `pathlib.Path.open` takes its mode. No mode passes. A string
literal mode containing none of `w`, `a`, `x`, `+` passes. A non-literal
mode, or a literal containing any of them, is `file-write` naming `open`.
A reference to the built-in `open` other than as the callee of a call
(`opener = open`) is `file-write`, because its mode cannot be judged. A
file that binds `open` itself is judged by the bound-name rule: its
`open` is not the built-in. An
`Attribute` whose `attr` is one of `[writes] methods` is `file-write`
naming the method, on any receiver and whether or not it is called; these
are reported as `file-write`, never as `kernel-io`. `open` is no longer a
denied built-in.

*Soundness:* sound against accident, meaning every ordinary spelling of
these routes. It is not sound against a determined author:
`getattr(np, 'lo' + 'ad')`, a dunder assembled at run time, or an alias
through a data structure all evade it. The text report's preamble says
so.

**3. Sources stay home** (kinds `source-absolute`, `source-escapes`,
`jscad-source`, and the adapters' runtime refusal). An `Assign` or
`AnnAssign` whose target is a `Name` or an `Attribute` spelled with a
source attribute is judged when its value is a string literal. An
absolute literal is `source-absolute`. A relative literal is resolved as
`realpath(join(dirname(declaring file), value))`, which is the adapters'
own arithmetic, so a symbolic link that leaves the root is caught as
`source-escapes`. The file need not exist: a missing source is the
adapter's own refusal. A computed value raises no static finding. Any
non-`None` `jscad_source`, literal or computed, is `jscad-source`.
*Soundness:* static for literals; at run time, for every declared source
at construction (D10). OpenSCAD files pass unread. OpenSCAD's own `use`
and `include`, and `solid2.import_scad`, read by computed path; the
runtime bounds them.

### D6. What "allowed whole" trusts

The contract tier is trusted whole except its denylist. Vet does not look
inside `machinome`, `machinome_mechanics` or `molejo`. The denylist was
verified on 2026-09-26 by reading each module's imports and calls:

| Module | Why it is denied |
| --- | --- |
| `machinome.cli` | `import_module` on the command table: import by name. |
| `machinome.manager` | The commands: `develop` and `snapshot` run processes (`Popen`, `run`), `test` imports by path through the loader, `new` writes a project tree, `build` spawns build processes. |
| `machinome.core.builder` | Writes, relinks and removes files in the build directory, starts watchdog threads, loads nodes by reference. |
| `machinome.core.processes` | `multiprocessing.get_context('spawn')`: process creation. |
| `machinome.core.loader` | `import_module` and `import_module_from_path`: import by name and by path. |
| `machinome.core.export` | Writes the export tree into a caller-chosen output directory (`makedirs`, `copy2`, atomic replace). |
| `machinome.core.pieces` | `PieceInventory.copy_artifact(path, target)` and the fact-record writer write to caller-given paths. |
| `machinome.source_generation` | Installs a `MetaPathFinder` and `exec`s module code. |
| `machinome.viewers` | `browser.py` runs a process (`subprocess.run`) and stages files; the OpenSCAD viewer runs `openscad`/`xvfb-run`; `bundle.py` resolves entry points. |
| `machinome.sphinx` | The Sphinx extension copies bundles and exports into the documentation output (`copytree`, `copy2`). |
| `machinome.currency` | `record`, `publish`, `drop` and `restamp` write, replace and remove sidecars and artifacts at any path given. |
| `machinome._artifact` | `copy_to(target)` writes to any target. |

`machinome.openscad`, which the review's starting list named, is **not**
denied: it only locates the binary (`shutil.which`) and raises
`OpenScadUnavailable`. It spawns nothing, writes nothing and imports
nothing by name. `machinome.node`, `machinome.simulation`,
`machinome.motion`, `machinome.math`, `machinome.parameters` and
`machinome.test` stay allowed, as do `machinome.exact` (its public
functions are pure geometry, OpenAstroMount's `seats.py` and four Curta
tests use `intersect_shapes`, and its only writer, `_atomic_export`, is
private and called by the build), `machinome.mesh_engine`,
`machinome.expression_graph`, `machinome.scad_expression`, and the rest
of `machinome.core` (`expressions`, `expression_parser`, `serializer`,
`camera`, `logging`). The Metamaquina2 and snappy-reprap companion tests
import `machinome.core.serializer`. Importing any `machinome.core`
module runs the package `__init__`, which imports the loader; that is
harmless to the verdict, because vet judges what the project names, and
`machinome.core.loader` reached through any import-bound chain is still
`framework-internal`.

Residual: `machinome.node` itself runs processes, OpenSCAD for
`Solid2Node` and `OpenScadNode` and node for `JScadNode`, on the node's
own generated or declared source. That is the contract doing its job,
which is why a `jscad_source` is refused and why OpenSCAD's reach is left
to the runtime.

### D7. Scope and the tests tier

The default scope is every model's closure. `--tests` adds, for every
vetted module, its companion by the loader's rule (`test_<n>.py` beside
`<n>.py`, and `test.py` beside `__init__.py`) when that file exists. The
companion's closure is then vetted, and the process repeats until no new
file appears. This is wider than what `machinome test <model>` runs,
which is the root module's companion only, because the floor also runs
`machinome test <sub-node reference>`, and that runs a sub-module's
companion. Nothing else is ever opened. Directory listing happens only
at the root (for shadowing) and inside star-imported packages.

For each model, a file in the model closure is judged by the model rules.
A file reached only through a companion is judged with the tests tier
added: `unittest`, `pytest` and `logging` are members there, and nowhere
else. A
model module that imports `unittest` is `outside-universe`, whatever the
scope. The re-survey of 2026-09-26 counted companion imports of
`unittest` (168 files), `pathlib` (40), `pytest` (31), `logging` (12) and
`importlib` (9): with the tests tier and the reads decision the first
four pass, and `importlib` remains a finding under `--tests`.

### D8. Report

`Report` holds `universe` (name, version), `root`, `scope`, and a
`ModelReport` per model: `name`, `reference`, `pure`, `files` (sorted
paths relative to the root) and `findings`. Each `Finding` is
`(path, line, kind, name)`. Findings are sorted by `(path, line, kind,
name)` and deduplicated, and a shared file's findings are copied into
every model whose closure holds it.

Text output looks like this:

    machinome vet: universe machinome 0.7.0
    Vet statically checks what this project declares; it is not a sandbox, and it
    does not hold against an author who sets out to evade it.

    clock_a  pure
    clock_b  not pure
      simulation/b.py:3  outside-universe  socket
    project  not pure

JSON follows the specification's shape exactly, with keys in the order
given there and `json.dumps(sort_keys=False)`.

Exit status: 0 when pure, 1 when not pure, and 2 when vet cannot run
(manifest errors, or a directory reference). Using 2 for "cannot run"
lets a host tell a refusal from a failure to vet. `machinome models`
uses 1 for a malformed manifest, but it has no verdict to keep apart.

### D9. Determinism

The report depends only on the bytes of the files it opens, the
directory listings of D7, the real paths of those files, and
`universe.toml`. It never imports or compiles project code, never reads
`sys.path`, site-packages or `importlib.metadata`, and reads no clock
and no environment variable. `SOLID_BUILD_DIR` and `.env` do not matter
to it. The working directory is used only to find the manifest and to
resolve a path reference. The same tree gives a byte-identical JSON
report, and a test pins that.

### D10. The adapters contain every declared source at construction

`require_source_file(klass, attribute, declared, path)` gains one check,
made before the existence checks it already makes, so a source outside
the project is refused whether or not it exists:

- The declaring module is `sys.modules[klass.__module__]`, as the
  function already reads for its message. Its project root is
  `machinome.manifest.project_root(realpath(module.__file__))`.
- When `realpath(path)` is not under `realpath(root)` (by
  `os.path.commonpath`, as `loader._within` does), the function raises
  `ValueError` naming the class, the attribute, the declared value, the
  resolved path and the project root, like its other admission
  refusals. The message says the source lies outside the project.
- When the module has no `__file__`, or the manifest module finds no
  project above it (`ProjectManifestError`), the source is not judged:
  there is no project to contain it in. A model is always loaded from
  under a manifest, so every project source is judged. A library such as
  `machinome_mechanics` shipping a source beside its own module is not.
- The root is memoized per declaring module's real path, so the
  manifest is read once per module per process rather than once per
  leaf. The memo is cost, not semantics.

The four adapters call the function unchanged, so each is contained
without edits. `Svg.resolve` (markings) calls it too, so a marking's
artwork is contained the same way; the `markings` delta records it. The
step-import requirement's "an absolute path SHALL resolve to itself"
stays: an absolute path under the root is admitted, one outside is
refused.

Catalogue evidence: the 625 literal source declarations all resolve
under their roots, and the 11 projects with computed sources hold no
symbolic link leaving their roots, so no catalogue project is refused.
The framework's own fixtures declare their sources under `tests/`, whose
`pyproject.toml` makes it a project root; task 6.6 confirms the suites
that construct source-bound leaves stay green.

### D11. Import-step refuses a document outside the target project

D11 is the generation-time half of D10, added at the review closure of
2026-09-26. Since the adapters refuse a declared source outside its
project, `machinome import-step /elsewhere/doc.step --into sim/` would
scaffold a model that cannot construct. The command therefore resolves
the `--into` directory's project root through
`machinome.manifest.project_root` and, when there is one, refuses a
document whose real path is not under the root's real path (by
`os.path.commonpath`). It refuses after its existing refusals and before
it creates the directory or writes any file. The message names the
document, the root and the remedy, which is to copy the document under
the root, and the command exits 1. When `--into` lies in no project
(`ProjectManifestError`), nothing is judged, as in D10.

*Alternative considered:* warn and generate anyway. It was rejected
because the scaffold's first construction would then fail with the
adapters' message, which names a leaf class the pilot never wrote,
instead of the command's own message, which names the document and says
what to do.

## Risks / Trade-offs

- **The method denylist can flag a project method by name.** A project
  class with its own `save` or `load` method, called as `self.save()`,
  would be flagged. → The receiver rule keeps module functions such as
  `json.load` and `blueprints.load` clear. In the 2026-09-26 catalogue,
  every `.load(` and `.dump(` call in a simulation file is on an
  import-bound name (`trimesh.load`, `blueprints.load`, `ast.dump`), and
  no simulation file calls `.save(` or `.export(`. The pathlib write
  methods are matched on any receiver, so a project function named
  `touch` or `mkdir` would be flagged; none exists in the catalogue.
- **The `os` restriction is a list of spellings.** A read reached
  through an `os` name not on it (`os.stat`, `os.access`) is a finding
  while the pathlib spelling passes. → The catalogue uses `os.path`,
  `os.listdir` and `os.walk` only, and the restriction is data, so a
  spelling with evidence is one line.
- **Vet is not a sandbox.** → The preamble states it, the manual says
  it, and the pairing with a capability-free runtime is the
  consumers' job.
- **The universe version pinned to the framework version** makes every
  framework release bump the declaration. → bumpversion rewrites it, and
  a test fails when the two differ.
- **The containment check changes adapter behaviour.** A project that
  kept a source outside its root would stop constructing. → No catalogue
  project does (D10), and the refusal names the path and the root.
- **Moving manifest code** could change an error message or an
  exception's identity. → The loader's existing tests
  (`tests/test_named_models.py`, `tests/test_loader_references.py`,
  `tests/test_lazy_test_framework.py`) must stay green unchanged, and
  an identity test pins the re-export.

## Migration Plan

The command is additive. The adapters' containment refusal changes
behaviour only for a source outside its project, which no catalogue
project declares. shapely becomes a declared dependency; it is already
installed in the workspace venv at 2.1.2. Consumers adopt vet in their
own repositories. Rolling back means removing the command, the package,
the containment check and the dependency, since the manifest extraction
is behaviour-preserving.

## Decisions on the questions of review (2026-09-26)

The first draft of this design ended with nine open questions from the
re-survey. The pilot decided them on 2026-09-26, accepting the
reviewer's recommendation. None remains open.

1. **Reads (computed source paths, `os` and `pathlib`).** Reads inside
   the project are pure; writes, processes, network and dynamic import
   are not. A pure project reads only inside its own tree and writes
   nothing; containment of reads is the runtime's, and of declared
   sources the adapters'. Hence `os` (restricted to `os.path` and directory listing) and
   `pathlib` join the stdlib tier, a computed source raises no static
   finding, the kind `source-not-literal` is dropped, and
   `require_source_file` refuses at construction a source outside the
   project root (D10). The 122 computed source assignments in 11
   projects and the 31 files importing `os` or `pathlib` pass unless
   they write or use `os` beyond `os.path`.
2. **The contract tier.** Allowed whole except the verified denylist of
   D6, reported as `framework-internal`.
3. **`deny_methods` and `denied_builtins`.** Both stay. `open` leaves
   `denied_builtins`, which keeps `breakpoint`, `help` and `input`; the
   `file-write` rule (D5) judges `open` and `.open` by mode and denies
   the pathlib mutating methods by name.
4. **`solid2.import_scad`** stays allowed. It reads a `.scad` file
   inside the project, which the reads decision admits; its path is
   computed, so the runtime bounds it.
5. **`xml.etree`** stays in the pure tier. `ElementTree.parse(path)` is
   a read and is admitted by the reads decision. Residual:
   `ElementTree.write(path)` writes a file and no rule names it.
6. **`--tests`.** A tests tier (`unittest`, `pytest`) applies only to
   files reached solely through a companion (D7).
7. **shapely.** A universe member must be installed by the framework, or
   the universe lies to hosts: `shapely==2.1.*` joins `[project]
   dependencies`, pinned to the installed minor (2.1.2). The contract
   member `machinome_mechanics` is installed through the framework's own
   `mechanics` extra, not as a dependency; a host vetting a project that
   imports it installs that extra. This change leaves it so.
8. **Shadowing** stays limited to universe names. Residual, hostile-only:
   a root-level module named like a stdlib module that a kernel imports
   internally (`tempfile.py`) could be picked up by that kernel and run
   unvetted. Reaching it takes intent, not accident.
9. **`__path__`** joins the denied dunders: it lets a package redirect
   its own submodule imports outside the root.

Residuals recorded with these decisions: `Path.replace` and
`Path.rename` are not denied, because denying `replace` by name would
flag every `str.replace` on a receiver vet cannot type; a `.open(name,
mode)` method with another signature is judged on its first argument
only; and no computed read (`open` on a joined path, `import_scad`,
OpenSCAD's `use` and `include`) is proved to stay in the project.
