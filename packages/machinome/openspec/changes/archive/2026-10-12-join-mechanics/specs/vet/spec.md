## MODIFIED Requirements

### Requirement: The universe is a versioned declaration shipped with the framework

The system SHALL carry one universe declaration as a data file inside the
installed framework package. The declaration SHALL name the universe
(`machinome`) and the framework version it describes, which SHALL equal the
installed framework's version, and the framework's release tooling
SHALL rewrite that version with the others on every release. It SHALL
declare three tiers and a tests tier:

- **The contract**, allowed whole except a denylist of the framework's
  own modules that spawn processes, write to a caller-chosen path, or
  import by name: `machinome` and `molejo`. The mechanics helpers,
  `machinome.mechanics`, lie beneath `machinome` and are in the contract
  without a member of their own; the former module name
  `machinome_mechanics`, which no package of the set installs, is not a
  member.
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

#### Scenario: The mechanics helpers are judged by their address

- **WHEN** one vetted project runs `from machinome.mechanics import
  meshed_angle` and another runs `from machinome_mechanics import
  meshed_angle`
- **THEN** vet reports no finding for the first, and reports the second as
  `outside-universe` named `machinome_mechanics`
