# vet Specification

## Purpose

`machinome vet`: the static, deterministic check that a project stays
inside the machinome universe. It reads a project's files as bytes and the
universe declaration shipped with the framework, never imports project code
or a kernel, and gives one verdict per model and per project: pure, or the
findings that say why not. Vet checks what a project declares; it is not a
sandbox, and the runtime that lacks a capability is. Encodes ADR-149.

Code: `machinome/vet/`, `machinome/manifest.py`, `machinome/manager/vet.py`.

## Requirements

### Requirement: The universe is a versioned declaration shipped with the framework

The system SHALL carry one universe declaration as a data file inside the
installed framework package. The declaration SHALL name the universe
(`machinome`) and the framework version it describes, which SHALL equal the
installed framework's version, and the framework's release tooling
SHALL rewrite that version with the others on every release. It SHALL
declare three tiers and a tests tier:

- **The contract**, allowed whole except a denylist of the framework's
  own modules that spawn processes, write to a caller-chosen path, or
  import by name: `machinome`, `machinome_mechanics`, `molejo`.
- **The kernels**, allowed except for a denylist of IO entry points:
  `cadquery`, `build123d`, `OCP`, `solid2`, `trimesh`, `numpy`, `scipy`,
  `manifold3d`, `shapely`. The denylist covers importers and exporters,
  STEP/IGES/STL readers and writers, numpy's
  load/save/fromfile/tofile/loadtxt/savetxt/genfromtxt/memmap, `scipy.io`,
  and solid2's render-to-file. It SHALL be written as dotted names, plus a
  list of method names that do file IO on kernel objects.
- **Pure stdlib**: `math`, `cmath`, `fractions`, `decimal`, `statistics`,
  `itertools`, `functools`, `operator`, `collections`, `dataclasses`,
  `enum`, `typing`, `abc`, `numbers`, `re`, `string`, `json`, `hashlib`,
  `struct`, `copy`, `contextlib`, `random`, `bisect`, `heapq`,
  `xml.etree`, `__future__`, `ast`, `os` restricted to `os.path` and the
  directory listings `os.listdir`, `os.scandir` and `os.walk`, and `pathlib`.
- **Tests**: `unittest`, `pytest` and `logging`, members only for a file that vet
  reaches solely through a companion test under the tests scope.

A module name SHALL count as a member when it equals a member or lies
beneath one: `xml.etree.ElementTree` is beneath `xml.etree`, but `xml`
alone is not a member. The declaration SHALL be able to restrict a member
to allowed dotted prefixes, as data: for a restricted member, the member
itself and names at or beneath an allowed prefix are members, and every
other name beneath the member is outside the universe. Every name that is
neither a member nor a project module SHALL be outside the universe, and
that includes `sys`, `io`, `subprocess`, `socket`, `urllib`, `http`,
`threading`, `multiprocessing`, `signal`, `ctypes`, `importlib`, `runpy`,
`pickle`, `marshal`, `tempfile`, `shutil` and `glob`.

The verdict SHALL depend only on the declaration and the project's files,
never on which packages the machine happens to have installed.

#### Scenario: The declaration names its version

- **WHEN** the universe declaration is read from the installed package
- **THEN** it names the universe `machinome` and a version equal to
  `machinome.__version__`

#### Scenario: os.path is inside the universe

- **WHEN** a vetted module runs `import os`, `from os.path import join`
  and calls `os.path.join(HERE, 'x')`, `os.path.exists(path)` and
  `os.listdir(HERE)`
- **THEN** vet reports no finding for them

#### Scenario: The rest of os is outside the universe

- **WHEN** a vetted module calls `os.makedirs(HERE)`, reads `os.environ`,
  or runs `from os import system`
- **THEN** vet reports kind `outside-universe`, named `os.makedirs`,
  `os.environ` and `os.system` respectively

#### Scenario: pathlib reads pass

- **WHEN** a vetted module runs `from pathlib import Path` and computes
  `Path(__file__).parent / 'x'`
- **THEN** vet reports no finding for it

#### Scenario: An installed package outside the universe is still outside

- **WHEN** a project imports `requests` on a machine where `requests` is
  installed
- **THEN** vet reports that import as `outside-universe`

### Requirement: Vet resolves the model closure statically

The system SHALL start from every model reference in `[tool.machinome]
model` and `[tool.machinome.models]` and resolve each reference to a file
under the project root without importing it.

Every `import` and `from ... import` statement in a vetted file SHALL be
resolved statically, whatever scope it sits in. That includes imports
inside function bodies, class bodies, `if` blocks and
`try`/`except ImportError` blocks.

- An absolute dotted name SHALL be looked up under the project root as a
  module file (`a/b.py`), a regular package (`a/b/__init__.py`) or a
  namespace directory.
- A relative import SHALL be resolved against the importing module's
  package, and inside a package's own `__init__.py` that package is the
  package itself.
- `from p import n` SHALL vet `p/n` when that is a module, and otherwise
  treats `n` as a name defined in `p`.
- A star import from a project package SHALL vet every module directly in
  that package.

Every package `__init__.py` on the path to a vetted module SHALL itself be
vetted, because Python executes it. A name whose top level does not
resolve under the root SHALL be checked against the universe. Resolution
SHALL follow the runtime's order, which puts the project root first on the
import path.

#### Scenario: The pure fixture is pure

- **WHEN** vet runs over a fixture project whose model imports only
  `machinome`, `cadquery`, `math` and its own modules
- **THEN** every model's verdict is `pure`, the project's verdict is
  `pure`, and the vetted files are the model module, the project modules
  it reaches, and their package `__init__.py` files

#### Scenario: A package init on the path is vetted

- **WHEN** a model at `sim/parts/gear.py` is pure but `sim/__init__.py`
  imports `subprocess`
- **THEN** vet reports `outside-universe` for `subprocess` at
  `sim/__init__.py`, and the model is not pure

#### Scenario: A function-local import is vetted

- **WHEN** a vetted module imports `tempfile` inside a function body that
  the model never calls
- **THEN** vet reports `outside-universe` for `tempfile` at that line

#### Scenario: A guarded import is vetted

- **WHEN** a vetted module imports `socket` inside `try: ... except
  ImportError:`
- **THEN** vet reports `outside-universe` for `socket`

#### Scenario: A relative import is followed

- **WHEN** a vetted module runs `from .helpers import pitch`, and
  `helpers.py` beside it imports `pickle`
- **THEN** `helpers.py` is vetted and `pickle` is reported there

#### Scenario: A module that is not there

- **WHEN** a vetted module imports `sim.missing` and `sim` resolves under
  the root but `missing` is neither a module nor a package there
- **THEN** vet reports `unresolved-import` naming `sim.missing`

### Requirement: An import outside the universe is a finding

The system SHALL report `outside-universe` for every import whose name
neither resolves under the project root nor is a member of the universe.
This covers stdlib modules outside the pure tier and third-party packages
outside the kernel tier alike.

#### Scenario: A denied stdlib module

- **WHEN** a vetted module runs `import subprocess`
- **THEN** vet reports kind `outside-universe`, name `subprocess`, with
  that file and line

#### Scenario: A third-party library outside the kernels

- **WHEN** a vetted module runs `import yaml`
- **THEN** vet reports kind `outside-universe`, name `yaml`

#### Scenario: A pure stdlib module passes

- **WHEN** a vetted module runs `from fractions import Fraction` and
  `import xml.etree.ElementTree as ET`
- **THEN** vet reports no finding for either import

### Requirement: A denied kernel IO entry point is a finding

The system SHALL report `kernel-io` when a vetted file reaches a dotted
name on the kernel denylist, or anything beneath one. Such a name can be
reached through an import statement (`from numpy import load`,
`import cadquery.importers`) or through an attribute chain on a name that
an import bound (`np.load` after `import numpy as np`,
`cq.importers.importStep` after `import cadquery as cq`).

The system SHALL also report `kernel-io` when a vetted file names a
method on the method denylist (`export`, `exportStl`, `tofile` and the
rest) as an attribute of a receiver that no import statement bound, such
as a call result or a local variable. An attribute of a name an import
bound SHALL be judged only by the dotted denylist, so `json.load` and a
project module's own `load` function are not method findings. A pathlib
mutating method is a `file-write` finding, never `kernel-io`.

#### Scenario: A numpy load through an alias

- **WHEN** a vetted module runs `import numpy as np` and later calls
  `np.load('table.npy')`
- **THEN** vet reports kind `kernel-io`, name `numpy.load`, at the line
  of the call

#### Scenario: A cadquery importer

- **WHEN** a vetted module calls `cq.importers.importStep(path)` after
  `import cadquery as cq`
- **THEN** vet reports kind `kernel-io`, name `cadquery.importers`

#### Scenario: An IO method on a kernel object

- **WHEN** a vetted module calls `.export('out.stl')` on a `Workplane`
  result
- **THEN** vet reports kind `kernel-io`, name `export`

#### Scenario: A kernel's pure API passes

- **WHEN** a vetted module calls `np.linspace`, `cq.Workplane().box(...)`
  and `trimesh.creation.cylinder(...)`
- **THEN** vet reports no finding for them

### Requirement: A framework internal is a finding

The system SHALL report `framework-internal` when a vetted file reaches,
through an import statement or through an attribute chain on a name that
an import bound, a dotted name equal to or beneath one of the contract's
denied modules: `machinome.cli`, `machinome.manager`,
`machinome.core.builder`, `machinome.core.processes`,
`machinome.core.loader`, `machinome.core.export`,
`machinome.core.pieces`, `machinome.source_generation`,
`machinome.viewers`, `machinome.sphinx`, `machinome.currency`,
`machinome._artifact`, `machinome.exact_cache`, `machinome.exact_artifacts`,
and the exact engine's file operations `machinome.occt.engine.read_brep`,
`machinome.occt.engine.write_brep` and `machinome.occt.engine.write_stl`.
The finding SHALL name the denied name reached. Every other name beneath
the contract members, including `machinome.node`, `machinome.simulation`,
`machinome.motion`, `machinome.math`, `machinome.parameters`,
`machinome.test`, `machinome.exact_engine`, `machinome.occt.engine` and its
other operations, and `machinome.openscad`, SHALL pass.

`machinome.exact` no longer exists: the exact operations a project calls
directly are defined in `machinome.occt.engine` and are reached there. Vet
judges a name by its place in the universe, not by whether a module defines
it, so an import of the removed module is not a vet finding; it fails when the
project runs.

#### Scenario: The loader through an import

- **WHEN** a vetted module runs `from machinome.core.loader import
  load_node`
- **THEN** vet reports kind `framework-internal`, name
  `machinome.core.loader`

#### Scenario: The builder through an attribute chain

- **WHEN** a vetted module runs `import machinome.core.expressions` and
  later names `machinome.core.builder.Builder`
- **THEN** vet reports kind `framework-internal`, name
  `machinome.core.builder`, and no finding for
  `machinome.core.expressions`

#### Scenario: The public contract passes

- **WHEN** a vetted module imports from `machinome.node`,
  `machinome.simulation`, `machinome.motion` and `machinome.occt.engine`
- **THEN** vet reports no finding for those imports

#### Scenario: The engine's exact operations pass

- **WHEN** a vetted module runs `from machinome.occt.engine import
  intersect_shapes, placed_shape, solid_volume`
- **THEN** vet reports no finding for that import

#### Scenario: The engine's file operations are internals

- **WHEN** a vetted module runs `from machinome.occt.engine import
  write_brep`, or names `machinome.exact_cache.cached_shape`
- **THEN** vet reports kind `framework-internal`, naming
  `machinome.occt.engine.write_brep` or `machinome.exact_cache`

### Requirement: A file write is a finding

The system SHALL report `file-write` in every vetted file for:

- a call to the built-in `open` whose mode, the second positional
  argument or the `mode=` keyword, is not a string literal, or is a
  string literal containing any of `w`, `a`, `x` or `+`;
- a call to any `.open` attribute whose mode, the first positional
  argument or the `mode=` keyword, is judged the same way;
- a reference to the built-in `open` other than as the callee of a call;
- any attribute named `write_text`, `write_bytes`, `mkdir`, `unlink`,
  `rmdir`, `touch`, `chmod`, `lchmod`, `symlink_to` or `hardlink_to`, on
  any receiver.

The first three SHALL name `open`, and the last SHALL name the method. A
call to `open` or `.open` with no mode, or with a string literal mode
containing none of those characters, SHALL NOT be a finding.

The built-in `open` is judged only where the file does not bind the name
`open` itself, by the bound-name rule of "A dynamic route around the
declaration is a finding".

#### Scenario: A read passes

- **WHEN** a vetted module runs `with open(path) as f:`,
  `open(path, 'rb')` and `archive.open('rb')`
- **THEN** vet reports no finding for them

#### Scenario: A write mode

- **WHEN** a vetted module calls `open(path, 'w')`, or
  `open(path, mode='a+')`
- **THEN** vet reports kind `file-write`, name `open`, for each

#### Scenario: A mode vet cannot read

- **WHEN** a vetted module calls `open(path, mode)` where `mode` is a
  variable
- **THEN** vet reports kind `file-write`, name `open`

#### Scenario: A pathlib write

- **WHEN** a vetted module calls `Path(out).write_text(text)` and
  `target.parent.mkdir(parents=True)`
- **THEN** vet reports kind `file-write`, named `write_text` and `mkdir`

### Requirement: A dynamic route around the declaration is a finding

The system SHALL report, in every vetted file:

- `dynamic-route` for any reference to the built-in names `exec`, `eval`,
  `compile` or `__import__`, whether called or not, and for any import of
  `importlib` or `runpy`. A method that happens to be spelled the same,
  such as `re.compile`, is not a finding.
- `import-system` for any reference to `sys.path` or `sys.modules`,
  whether reached through `import sys` or through `from sys import path`.
- `denied-dunder` for any of `__subclasses__`, `__globals__`,
  `__builtins__`, `__loader__`, `__spec__`, `__code__`, `__closure__`,
  `__mro__`, `__bases__`, `__base__` and `__path__`, whether written as a
  bare name, as an attribute or as a string literal anywhere in the file.
- `denied-builtin` for any reference to the built-in names `breakpoint`,
  `help` or `input`. The built-in `open` is judged by the file-write
  rule instead.

An import of `importlib` or `runpy` SHALL be reported as `dynamic-route`
and not also as `outside-universe`. An import of `sys` SHALL still be
reported as `outside-universe`, in addition to each `import-system`
finding.

A name that the file itself binds anywhere is the project's name, not
the built-in's: bound by assignment (any name stored to, including a
class-body, augmented or annotated assignment and a tuple target), by a
`def` or `class` definition, by a function parameter, by a `for`,
`with`, `except` or comprehension target, or by an import. A reference
to such a name SHALL NOT raise `dynamic-route`, `denied-builtin` or a
`file-write` finding for the built-in `open`. The `denied-dunder` rule is
unaffected: a denied dunder is a finding however it is bound.

#### Scenario: eval is a dynamic route

- **WHEN** a vetted module that binds no name `eval` calls
  `eval(expression)`
- **THEN** vet reports kind `dynamic-route`, name `eval`

#### Scenario: re.compile is not a dynamic route

- **WHEN** a vetted module calls `re.compile(pattern)`
- **THEN** vet reports no finding for it

#### Scenario: A child named input

- **WHEN** a vetted module declares, in a class body,
  `input = InputArbor()` and then writes `input.turn.drives(...)`
- **THEN** vet reports no finding for either line

#### Scenario: A locally bound compile

- **WHEN** a vetted module runs `from re import compile` and calls
  `compile(p)`, and defines `def f(help): return help`
- **THEN** vet reports no finding for them

#### Scenario: importlib is a dynamic route

- **WHEN** a vetted module runs `import importlib`
- **THEN** vet reports kind `dynamic-route`, name `importlib`, and no
  `outside-universe` finding for that import

#### Scenario: sys.path mutation

- **WHEN** a vetted module runs `sys.path.insert(0, upstream)`
- **THEN** vet reports kind `import-system`, name `sys.path`, at that line,
  and kind `outside-universe`, name `sys`, at the import

#### Scenario: sys.modules mutation

- **WHEN** a vetted module assigns into `sys.modules['gears']`
- **THEN** vet reports kind `import-system`, name `sys.modules`

#### Scenario: A denied dunder as an attribute

- **WHEN** a vetted module reads `type(self).__mro__`
- **THEN** vet reports kind `denied-dunder`, name `__mro__`

#### Scenario: A denied dunder as a string literal

- **WHEN** a vetted module calls `getattr(obj, '__globals__')`
- **THEN** vet reports kind `denied-dunder`, name `__globals__`

#### Scenario: A package redirecting its own imports

- **WHEN** a vetted package's `__init__.py` runs
  `__path__.append(elsewhere)`
- **THEN** vet reports kind `denied-dunder`, name `__path__`

#### Scenario: input is a denied built-in

- **WHEN** a vetted module that binds no name `input` calls
  `input('size? ')`
- **THEN** vet reports kind `denied-builtin`, name `input`

### Requirement: A project file that shadows a universe name is a finding

The system SHALL report `shadowing` for every module file (`X.py`) or
package directory (`X/`) at the project root whose name `X` is the top
level of any universe member, whether or not anything imports it. An
import of that name SHALL resolve to the project file, as it does at run
time, and that file SHALL be vetted as project code.

#### Scenario: A project json module

- **WHEN** the project root holds `json.py`
- **THEN** vet reports kind `shadowing`, name `json`, at `json.py`, and
  the project is not pure

### Requirement: A file vet cannot read is a finding

The system SHALL report `unparseable` for a vetted file that cannot be
decoded or parsed as Python, naming the parser's reason. Such a file
SHALL contribute no imports to the closure. Vet SHALL decode a source
file the way the interpreter does, honouring a coding declaration and a
byte-order mark.

#### Scenario: A syntax error

- **WHEN** a module in the closure contains a syntax error
- **THEN** vet reports kind `unparseable` at that file and the line the
  parser names, and the model is not pure

### Requirement: The closure stays under the project root

The system SHALL report `escaped-module` when a module that an import
resolves to under the project root has a real path outside the root, for
example through a symbolic link. Such a file SHALL NOT be vetted.

The system SHALL report `unresolved-reference` when a model's reference
does not resolve to a Python file under the root. The model is then not
pure.

#### Scenario: A symlinked module leaving the root

- **WHEN** `sim/vendor.py` is a symbolic link to a file outside the
  project root and a vetted module imports `sim.vendor`
- **THEN** vet reports kind `escaped-module`, name `sim.vendor`

#### Scenario: A reference to a module that is not there

- **WHEN** the manifest declares `model = "sim.absent:Machine"` and there
  is no `sim/absent.py`
- **THEN** vet reports kind `unresolved-reference` for that model and
  the model is not pure

### Requirement: Declared sources stay under the project root

In every vetted file, the system SHALL judge each assignment to
`stl_source`, `step_source` or `scad_source` whose value is a string
literal, whether the target is a class-body name or an attribute. A
literal that is an absolute path SHALL be reported as `source-absolute`.
A relative literal SHALL be joined to the directory of the declaring file, the way the
adapters resolve it. When the real path of the result is not under the
real path of the project root, it SHALL be reported as `source-escapes`.
An assignment of `None` SHALL NOT be a finding. A value that is not a
string literal SHALL NOT be a static finding: a computed source is a read
inside the project, and the adapters contain it at construction (the
`node-model`, `stl-import` and `step-import` capabilities). Vet SHALL NOT
read the source file itself and SHALL NOT require it to exist.

#### Scenario: A relative literal under the root passes

- **WHEN** a vetted class declares `stl_source = '../meshes/gear.stl'` and
  that path lies under the project root
- **THEN** vet reports no finding for it

#### Scenario: A computed source passes

- **WHEN** a vetted class declares
  `step_source = os.path.join(HERE, 'x.step')`
- **THEN** vet reports no finding for it

#### Scenario: An absolute source

- **WHEN** a vetted class declares `stl_source = '/etc/model.stl'`
- **THEN** vet reports kind `source-absolute`, name `stl_source`

#### Scenario: An escaping source

- **WHEN** a vetted class declares `scad_source = '../../../outside.scad'`
  and that path resolves above the project root
- **THEN** vet reports kind `source-escapes`, name `scad_source`

#### Scenario: A source reached through a symlink

- **WHEN** a vetted class declares `stl_source = 'link/gear.stl'` and
  `link` is a symbolic link to a directory outside the root
- **THEN** vet reports kind `source-escapes`

### Requirement: A JavaScript source is outside this universe

The system SHALL report `jscad-source` for every assignment to
`jscad_source` in a vetted file whose value is not `None`, whatever that
value is. Vet SHALL NOT read the JavaScript file.

#### Scenario: A JScad leaf

- **WHEN** a vetted class declares `jscad_source = 'part.jscad'`
- **THEN** vet reports kind `jscad-source`, name `jscad_source`, and the
  model is not pure

### Requirement: The tests scope adds the companion tests

By default, the system SHALL vet the model closure and nothing else in the
tree. With `--tests`, it SHALL also vet the companion test module of every
vetted module, together with that companion's closure, and it SHALL repeat
this until no new file is added. Companions are named by the framework's
own discovery rule: `test_<name>.py` beside `<name>.py`, and `test.py`
beside a package's `__init__.py`. A file named like a test that is not a
companion of a vetted module SHALL NOT be read.

For each model, a file in that model's closure SHALL be judged by the
model rules, and a file reached only through a companion SHALL be judged
with the tests tier added, so `unittest`, `pytest` and `logging` pass
there and nowhere else.

#### Scenario: A companion is out of scope by default

- **WHEN** a pure model's companion `test_gear.py` imports `subprocess`
  and vet runs without `--tests`
- **THEN** the model is `pure` and `test_gear.py` is not among the vetted
  files

#### Scenario: A companion is in scope with --tests

- **WHEN** the same project is vetted with `--tests`
- **THEN** vet reports `outside-universe` for `subprocess` at
  `test_gear.py` and the model is not pure

#### Scenario: A companion may use the test frameworks

- **WHEN** a pure model's companion `test_gear.py` imports `unittest` and
  `pytest`, and vet runs with `--tests`
- **THEN** vet reports no finding for those imports and the model is
  `pure`

#### Scenario: A model may not import unittest

- **WHEN** a model module imports `unittest`
- **THEN** vet reports `outside-universe` for `unittest` under either
  scope

#### Scenario: A package companion

- **WHEN** a vetted package `sim/` has `sim/test.py`, and vet runs with
  `--tests`
- **THEN** `sim/test.py` is vetted

#### Scenario: A tool is never read

- **WHEN** the project holds `tools/fetch.py`, which imports `urllib`, and
  no vetted module imports it
- **THEN** vet reports no finding for it under either scope

### Requirement: The verdict is pure or not

The system SHALL give each model the verdict `pure` exactly when its
vetted files raise no finding. It SHALL give the project the verdict
`pure` exactly when every model it vetted is pure. A finding in a file
that several models share SHALL be reported under each of those models.
Findings SHALL be ordered by path and then by line.

With no reference, vet SHALL vet every model the manifest declares: the
single `model`, or every entry of `[tool.machinome.models]`. With a
reference, which may be a declared model name or any of the loader's other
spellings, it SHALL vet that one closure. A class named in the reference
SHALL NOT change the closure, which starts from the module file.

#### Scenario: One impure model among two

- **WHEN** a project declares `clock_a`, which is pure, and `clock_b`,
  which imports `socket`
- **THEN** `clock_a` is `pure`, `clock_b` is not, and the project is not

#### Scenario: A single reference

- **WHEN** vet runs with the reference `clock_a`
- **THEN** only `clock_a`'s closure is vetted and reported

### Requirement: The report is text for people and JSON for hosts

Every text report SHALL start with a preamble stating that vet is a
static check of what the project declares, not a sandbox, and that it
does not hold against an author who sets out to evade it. The preamble
SHALL name the universe and its version. The report SHALL then give one
line per model with its verdict, one line per finding with its path
(relative to the project root), line, kind and name, and finally the
project's verdict.

With `--json`, the system SHALL print exactly one JSON object and nothing
else on standard output. The object SHALL hold:

- `universe`: an object with `name` and `version`.
- `root`: the absolute project root.
- `scope`: `models` or `tests`.
- `pure`: the project's verdict, as a boolean.
- `models`: a list, in declaration order. Each entry holds `name` (null
  for a single-model project or a non-model reference), `reference`,
  `pure`, `files` (the vetted files, relative to the root and sorted) and
  `findings`. Each finding holds `path`, `line` (null when the finding
  has no line), `kind` and `name`.

A finding's kind SHALL be one of exactly these sixteen, in text and JSON
alike: `outside-universe`, `kernel-io`, `framework-internal`,
`file-write`, `dynamic-route`, `import-system`, `denied-dunder`,
`denied-builtin`, `shadowing`, `unparseable`, `unresolved-import`,
`escaped-module`, `unresolved-reference`, `source-absolute`,
`source-escapes`, `jscad-source`.

#### Scenario: A host reads the verdict

- **WHEN** a program runs `machinome vet --json` in the pure fixture
  project
- **THEN** it parses one object whose `pure` is true, whose `universe`
  names `machinome` and the framework version, and whose every model
  has `pure` true and an empty `findings` list

#### Scenario: A finding in JSON

- **WHEN** a program runs `machinome vet --json` in a project whose model
  imports `subprocess` at line 3 of `sim/gear.py`
- **THEN** that model's `findings` contains `{"path": "sim/gear.py",
  "line": 3, "kind": "outside-universe", "name": "subprocess"}`

### Requirement: The exit status carries the verdict

The system SHALL exit 0 when every vetted model is pure and 1 when any
model is not pure. When vet cannot run, because there is no manifest, the
manifest is malformed, or the reference is a directory, it SHALL write the
reason to standard error, print nothing on standard output, and exit 2.

#### Scenario: Pure exits zero

- **WHEN** vet runs in the pure fixture project
- **THEN** it exits 0

#### Scenario: Impure exits one

- **WHEN** vet runs in a project with any finding
- **THEN** it exits 1

#### Scenario: No manifest

- **WHEN** vet runs in a directory with no `[tool.machinome]` manifest
  above it
- **THEN** it writes the manifest error to standard error, prints nothing
  on standard output, and exits 2

### Requirement: Vet loads no kernel

The system SHALL vet a project without importing any kernel, any
`machinome.node` module or `machinome.core` module, or any command module
other than vet's own. Vet SHALL depend only on the standard library, the
universe declaration and the manifest module. It SHALL NOT read
site-packages or any installed package's files other than its own
declaration, and it SHALL NOT consult the clock or the environment beyond
locating the project.

#### Scenario: The kernels are absent after a vet

- **WHEN** `machinome vet` runs to completion in a fresh interpreter over
  the pure fixture project, whose model imports `cadquery`
- **THEN** `OCP`, `cadquery`, `numpy`, `trimesh` and every
  `machinome.node` module are absent from `sys.modules`

### Requirement: Vet imports no project module

The system SHALL NOT import, execute or compile any file of the project it
vets. The system SHALL read those files as bytes and parse them.

#### Scenario: A module with a side effect is not run

- **WHEN** vet runs over a fixture whose model module, if imported,
  would write a marker file at import time
- **THEN** no marker file exists afterwards, and no module of the fixture
  project is in `sys.modules`

#### Scenario: The same tree gives the same report

- **WHEN** vet runs twice over an unchanged tree
- **THEN** the two JSON reports are byte-identical
