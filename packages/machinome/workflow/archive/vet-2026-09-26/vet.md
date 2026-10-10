# Vet: a project stays inside the machinome universe

**Status:** archived 2026-09-26. The design this note settled was cut into
the OpenSpec change `vet-the-project`, implemented and archived the same day
at `openspec/changes/archive/2026-09-26-vet-the-project/` (ADR-149). The
baseline specs `vet`, `cli`, `cli-startup-cost`, `stl-import`,
`step-import`, `node-model` and `markings` are the authority; where this
note and they disagree, they are right and this note is history.

**What this does not claim:** that a project which passes vet is safe to
run. Vet proves the project *declares* nothing outside the universe and
contains no syntactic route around that declaration. It is a static
analyser, not a sandbox; the runtime that lacks the capability is the
sandbox. The two halves together are the guarantee. In particular, vet
does not prove that a computed read stays inside the project: a path
built at run time is bounded by the runtime, and for a declared adapter
source by the adapters' own containment check, never by vet.

## The need

Three hosts run project code they did not write, and none has a gate on
what that code may reach:

- **machinome.org intake** runs `machinome models --json`, `machinome
  export` and `machinome snapshot` for every Foundry project on the pilot's
  machine, with the operator's authority.
- **The studio floor** contains agent tools behind the floor MCP server's
  project gate (studio ADR 0026), but `machinome build` and `machinome
  test` run whatever the agent wrote, with the operator's authority. An
  agent that adds `subprocess` to a model has left the gate.
- **Browser delivery**, when it exists, runs a project in a runtime where
  the operating system is genuinely absent. A project must be known to fit
  before it is sent there.

The pilot's framing: a machinome project is a pure machine simulation. It
imports the framework, the kernels the framework depends on, and pure
computation; it runs no command, opens no socket, imports nothing by a
computed name, and writes no file.

**The reads decision (the pilot, 2026-09-26).** Reads inside the project
are pure. Writes, processes, network and dynamic import are not. A pure
project reads only inside its own tree and writes nothing. Containment of
reads is the runtime's, and containment of declared sources is the
adapters'. This replaces the earlier wording "reads no file except the
sources it declares to the framework's adapters", which 31 files
importing `os` or `pathlib` and 122 computed source declarations showed to
be wrong about what projects are. Vet asserts the rest deterministically, without
importing the project or any kernel.

## What projects do today

Survey of 2026-09-26: every `*.py` under a project's `simulation/`
directory in `projects/`, excluding paths containing `/.git/`, `/_build`,
`/WTs/`, `/tests/`, `/tools/`, `/scripts/` or `/.venv/`, and files named
`test_*.py` or `conftest.py`: **1,131 files**. (An earlier count of 1,892
included the copies under `.git/licensing-worktrees/`.) Counts are of
files, not of model closures; a file flagged here is a finding only when a
model or, under `--tests`, a companion reaches it.

| What the code does | Files | Where | Under vet |
| --- | --- | --- | --- |
| Runs a process through `subprocess` | 4 | Metamaquina2, snappy-reprap and hangprinter echo OpenSCAD parameter values; the 3DPrintedClocks quality audit (`check_models.py`) | finding |
| Fetches over the network (`urllib`) | 1 | openvmp `don1/catalogue.py` | finding |
| Writes a file (write-mode `open`, `Path.mkdir`/`write_text`, `os.makedirs`/`os.replace`) | 7 | the three printers above, the clocks audit, openvmp `catalogue.py`, Internal-Cycloidal-Actuator `actuator/source.py`, Curta `source.py` | finding |
| Lists a directory through `os` (`os.listdir`, `os.walk`) | 6 | `scad.py` in kossel, Prusa3-vanilla, Metamaquina2, snappy-reprap and hangprinter; openvmp `blueprints.py` | allowed: a directory listing is a read, so `os.listdir`, `os.scandir` and `os.walk` join the `os` restriction |
| Mutates `sys.path` | 2 | fender-bender `simulation/__init__.py`; an archived evidence script under openflexure-microscope's `simulation/openspec/` that no model reaches | finding where reached |
| Other stdlib outside the pure tier | 8 | `sys` (5), `tempfile` (4), `zipfile` (1), and `argparse`, `signal`, `time`, `tomllib`, `types` in the clocks audit; `ast` (4 files, including Voron-2 `viewer_pose.py`, which needs nothing else) is admitted as pure | finding |
| Third-party outside the kernels | 1 | openvmp `blueprints.py` (`yaml`, `jinja2`) | finding |
| Uses shapely | 2 | Poleni-1709 (two checkouts) | allowed: kernel member and, with this change, a framework dependency |
| Reads a project file by hand (`open` or `.open` with no write mode) | 9 | Prusa3 scad, openvmp `.assy`, Voron-2 and orcahand archive digests, the printers' parameter files, and the writers above | allowed under the reads decision |
| Imports `os` or `pathlib` | 31 | 25 projects | allowed under the reads decision, while `os` use stays in `os.path` and no pathlib mutating method is called |
| Adapter sources computed rather than literal | 14 (122 assignments) | 11 projects: Thor, YouCanBuildDog, Pascaline-module, Curta, open_robot_actuator_hardware, OpenCycloid, Voron-2, open_manipulator, openarm, AlbertPro, mechanical-multiplier | allowed under the reads decision; bounded at construction by the adapters |

The 625 literal source declarations all resolve under their project root,
and none of the 11 projects with computed sources holds a symbolic link
leaving its root, so the adapters' new containment refuses nothing in the
catalogue today. Everything else is the contract, the kernels and pure
stdlib. The universe below is descriptive, not aspirational: most files
pass, and the failures are real findings.

## The universe

One declaration file inside the framework package, carrying the framework
version it describes. Three tiers, plus one for tests.

| Tier | Members | Rule |
| --- | --- | --- |
| The contract | `machinome`, `machinome_mechanics`, `molejo` | Allowed whole, except the framework's own modules that spawn processes, write outside the build, or import by name (below). |
| The kernels | `cadquery`, `build123d`, `OCP`, `solid2`, `trimesh`, `numpy`, `scipy`, `manifold3d`, `shapely` | Allowed, minus a curated denylist of IO entry points: importers and exporters, STEP/IGES/STL readers and writers, numpy load/save/fromfile/tofile/loadtxt/savetxt/genfromtxt/memmap, `scipy.io`, solid2's render-to-file. |
| Pure stdlib | `math`, `cmath`, `fractions`, `decimal`, `statistics`, `itertools`, `functools`, `operator`, `collections`, `dataclasses`, `enum`, `typing`, `abc`, `numbers`, `re`, `string`, `json`, `hashlib`, `struct`, `copy`, `contextlib`, `random`, `bisect`, `heapq`, `xml.etree`, `__future__`, `ast`, `os` (restricted to `os.path`, `os.listdir`, `os.scandir`, `os.walk`), `pathlib` | Everything else is outside: `sys`, `io`, `subprocess`, `socket`, `urllib`, `http`, `threading`, `multiprocessing`, `signal`, `ctypes`, `importlib`, `runpy`, `pickle`, `marshal`, `tempfile`, `shutil`, `glob`, and every name not listed. |
| Tests | `unittest`, `pytest`, `logging` | Allowed only in a file reached solely through a companion test under `--tests`. A file in a model closure is judged by the model rules. |

`os` is a *restricted* member: `import os`, `from os import path`, `from
os.path import join`, any chain beneath `os.path`, and the directory
listings `os.listdir`, `os.scandir` and `os.walk` pass; any other use
(`os.environ`, `os.system`, `os.makedirs`, `from os import
system`) is `outside-universe` naming `os.<attr>`. The declaration keeps
restrictions as a table (member → allowed prefixes), so a second
restricted member is data. `pathlib` is whole, but its mutating methods
(`write_text`, `write_bytes`, `mkdir`, `unlink`, `rmdir`, `touch`,
`chmod`, `lchmod`, `symlink_to`, `hardlink_to`) are `file-write`.

**The framework's own internals.** These contract modules are denied, as
`framework-internal`, because a project has no business with them and
each runs a process, writes to a caller-chosen path, or imports by name:
`machinome.cli`, `machinome.manager`, `machinome.core.builder`,
`machinome.core.processes`, `machinome.core.loader`,
`machinome.core.export`, `machinome.core.pieces`,
`machinome.source_generation`, `machinome.viewers`, `machinome.sphinx`,
`machinome.currency`, `machinome._artifact`. `machinome.openscad` is not
on the list: it only locates the binary. `machinome.node`,
`machinome.simulation`, `machinome.motion`, `machinome.math`,
`machinome.parameters`, `machinome.test` and `machinome.exact` stay
allowed.

Shapely is in by the pilot's decision of 2026-09-26: it is pure geometry
and Poleni-1709 needs it. A universe member must be installed by the
framework, or the universe lies to hosts, so shapely becomes a framework
dependency in the same change. The universe is not derived from what is
installed; it is a versioned declaration, so the verdict is a property of
the project and the framework version, not of the machine.

## Three assertions

1. **Closure.** Start from every reference in `[tool.machinome] model` and
   `[tool.machinome.models]`. Resolve `import` and `from` statements
   statically to files under the project root and vet them transitively,
   including every package `__init__.py` on the import path, because
   Python executes those. A name that does not resolve under the root must
   be a universe member. A project file that shadows a universe name is a
   finding. Sound for every static import.
2. **No dynamic route and no write.** In vetted files: no `exec`, `eval`,
   `compile` or `__import__`; no `importlib` or `runpy`; no mutation of
   `sys.path` or `sys.modules`; no denied dunders (`__subclasses__`,
   `__globals__`, `__builtins__`, `__loader__`, `__spec__`, `__code__`,
   `__closure__`, `__mro__`, `__bases__`, `__base__`, `__path__`), whether
   written as a bare name, an attribute or a string literal (`__path__`
   joined on 2026-09-26: it lets a package redirect its own submodule
   imports); no `breakpoint`, `help`
   or `input`; no kernel IO entry point; no framework internal. `open`
   and any `.open` method are allowed with no mode or a literal mode free
   of `w`, `a`, `x` and `+`; anything else is `file-write`, as are the
   pathlib mutating methods. Sound against every accident; not sound
   against a determined author, and the report's preamble says so.
3. **Sources stay home.** Every declared adapter source (`stl_source`,
   `step_source`, `scad_source`, `jscad_source`) stays under the project
   root. Statically, a literal must be relative and resolve under the
   root, symbolic links included; a computed source raises no static
   finding. At run time, `require_source_file`, which the STL, STEP,
   OpenSCAD and JSCAD adapters call at construction, refuses a source
   whose real path is not under the real path of the project root, found
   through the kernel-free manifest module from the declaring module's
   file. Static for literals, runtime for every declared source at
   construction. A `jscad_source` is a finding in this universe: node
   runs that JavaScript with full capability and vet does not read it.
   OpenSCAD files pass unread: OpenSCAD reads files and nothing else, and
   the runtime bounds the filesystem.

## Scope

The default scope is the model closure, which is exactly what `export` and
`snapshot` execute. `--tests` extends it to the companion tests the
framework's own discovery would run (`test_<module>.py` beside each vetted
module, and their closures), for the floor, where `machinome test`
executes them; files reached only that way are judged with the tests tier
added. Nothing else in the tree is read: fetch scripts, upstream firmware
and tools stay out, because the runtime never executes them.

## The report

One verdict per model and one per project; each finding as path, line,
kind, and the offending name; the universe version. Text for people,
`--json` for hosts, exit status nonzero when any model is not pure. Vet is a
function of the tree's bytes and the universe declaration alone: it reads
no site-packages, imports no project module and no kernel. One test asserts
that after a vet `OCP` and `cadquery` are absent from `sys.modules`.

## Residuals

Recorded, not closed:

- A computed read (`open(os.path.join(HERE, name))`, `solid2.import_scad`
  on a computed path, `xml.etree.ElementTree.parse(path)`, OpenSCAD's own
  `use` and `include`) is not proved to stay in the project. The runtime
  bounds it.
- `Path.replace` and `Path.rename` are not denied: denying `replace` by
  name would flag every `str.replace` on a receiver vet cannot type.
  `ElementTree.write` is not denied either.
- Shadowing is checked for universe names only. A root-level module named
  like a stdlib module a kernel imports internally (`tempfile.py`) could
  be picked up by that kernel and run unvetted. That takes intent, so it
  is hostile-only.
- The contract is trusted whole outside the denied internals:
  `machinome.node` itself runs OpenSCAD and node on declared sources, and
  `machinome.exact` keeps a private artifact writer.
- A `.open(name, mode)` method with a signature other than pathlib's is
  judged on its first argument only.
- `machinome_mechanics` is installed by the framework's `mechanics` extra,
  not as a dependency.
- A local rebinding (`p = os; p.listdir()`), `getattr` with a computed
  name, and an alias through a data structure evade the static rules.

## Implementation notes

- `machinome.core.loader` imports the node base, which loads numpy and its
  family. Manifest discovery and project-root resolution (the TOML read in
  `_find_manifest`, `project_root`, `read_project`) move into a light
  module both the loader and vet import; the loader re-exports them. The
  adapters' containment check uses the same module.
- The framework's own source-closure walker (`node/sources.py`) resolves
  through `sys.modules`, so it needs the model imported and cannot serve
  vet. The browser prototype's `scripts/walk-imports.py` resolves dotted and
  relative imports to paths statically and is the right ancestor.
- The command is `machinome vet [reference] [--tests] [--json]`, registered
  in the lazy command registry (`cli-startup-cost` spec).
- The universe declaration names the framework version, so `setup.cfg`'s
  bumpversion sections gain it.

## Consumers, in order

1. machinome.org intake, before `machinome models` (a site change).
2. The studio floor, before build and test (a studio change).
3. Browser delivery, which will want a second, narrower universe without
   OpenSCAD. One universe now; naming the declaration makes the second an
   addition.

## Findings the first vet would raise

- Three printers run OpenSCAD themselves to echo parameter values: a gap
  the SCAD import could close. For `warts.md`.
- Projects keep fetch and preparation tooling inside `simulation/`
  (openvmp, Internal-Cycloidal-Actuator, Curta) that writes files; it
  belongs in a project `tools/` directory. Project fixes.
- fender-bender imports upstream through `sys.path`: a vendored-dependency
  question, not a vet one.
