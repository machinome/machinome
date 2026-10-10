# ADR-149: Vet Checks a Project Against a Versioned Universe, Statically, and the Adapters Contain Their Sources

**Status:** Accepted
**Date:** 2026-09-26
**Extends:** [ADR-024](ADR-024-command-first-cli-grammar-and-duck-typed-command-registry.md) (a tenth command in the duck-typed registry), [ADR-059](ADR-059-import-at-the-point-of-use.md) (the command imports only what it uses, and no kernel), [ADR-119](ADR-119-named-project-models-and-per-model-build-directories.md) (vet reads the declared models, and with no reference vets them all), [ADR-054](../NODE/ADR-054-imported-meshes-admitted-selected-and-corrected-explicitly.md) (a source-bound leaf's admission gains containment)
**OpenSpec change:** `vet-the-project`
**Ratified:** 26 September 2026. The design note `workflow/ongoing/vet.md` was settled with the pilot that day, and the pilot decided the nine questions the first design draft raised, accepting the reviewer's recommendations (design.md, last section).

## Context

Three hosts run project code they did not write, with the operator's
authority, and none can check what that code reaches without running it:
machinome.org's intake runs `models`, `export` and `snapshot` over every
Foundry project; the studio floor's project gate stops at `build` and
`test`, which run whatever an agent wrote; and browser delivery will run
a project in a runtime with no operating system at all. The pilot's
framing is that a machinome project is a pure machine simulation: it
imports the framework, the kernels the framework depends on and pure
computation, reads inside its own tree, and runs no command, opens no
socket, imports nothing by a computed name and writes no file. A survey
of the catalogue's 1,131 simulation files found almost everything
already inside that line, and the exceptions real.

## Decision

**The universe is a versioned declaration shipped as package data.**
`machinome/vet/universe.toml` names the universe (`machinome`) and the
framework version it describes; a test pins it to `machinome.__version__`
and `setup.cfg`'s bumpversion rewrites it with the other three version
files. It declares three tiers and a tests tier. The contract
(`machinome`, `machinome_mechanics`, `molejo`) is allowed whole except
twelve framework modules that run processes, write to a caller-chosen
path or import by name. The kernels (`cadquery`, `build123d`, `OCP`,
`solid2`, `trimesh`, `numpy`, `scipy`, `manifold3d`, `shapely`) are
allowed except dotted IO entry points and a list of IO method names.
The standard-library tier is an explicit list, with `os` restricted as
data to `os.path` and the directory listings, and `pathlib` whole. The
tests tier (`unittest`, `pytest`, `logging`) counts only in a file
reached solely through a companion test. Every other name is outside. A
member matches by whole dotted components. The verdict is a property of
the project and the declaration, never of what a machine has installed;
shapely therefore becomes a framework dependency (`shapely==2.1.*`),
because a member the framework does not install would let a project pass
and fail at import.

**Reads inside the project are pure** (the pilot, 2026-09-26). `open` and
any `.open` method pass with no mode or a literal mode free of `w`, `a`,
`x` and `+`; the pathlib methods that write, create or remove are
`file-write` by name on any receiver; `os` beyond its allowed prefixes is
`outside-universe`. A computed read is not proved to stay inside the
project: the runtime bounds it.

**The closure is resolved statically, never by import.** From every
declared model, or the one reference given, each `import` and
`from … import` anywhere in a file (function bodies and guarded `try`
blocks included) is resolved from the filesystem alone, project root
first as the runtime puts it; every package `__init__.py` on the way is
vetted; a star import from a project package vets every module in it; a
module whose real path leaves the root is `escaped-module` and not read;
a root-level file named like a universe top is `shadowing`. Files are
read as bytes and parsed, honouring coding declarations; nothing of the
project is imported, compiled or run, and no environment variable is
read. `--tests` adds the loader's companions of every vetted module and
their closures until nothing new appears.

**Three assertions, each with its limit.** Closure is sound for every
import written as a statement. The route and write rules (dynamic
built-ins and modules, `sys.path` and `sys.modules`, eleven dunders as
name, attribute or string, three denied built-ins, each built-in rule
waived for a name the file binds itself, kernel IO and
framework internals through import bindings and attribute chains, and the
write rules) are sound against accident and not against an author who
sets out to evade them; the text report says so first. Declared sources
are judged statically when literal (absolute, or resolving above the
root through `..` or a symlink, is a finding) and any `jscad_source` is
refused, because JavaScript is outside this universe. Sixteen finding
kinds, exactly.

**The adapters contain every declared source at construction.**
`require_source_file`, which the STL, STEP, OpenSCAD and JSCAD adapters
and `Svg.resolve` already call, first refuses with `ValueError` a source
whose real path is not under the real path of the declaring module's
project root, whether or not it exists, before anything is read or run.
A module in no project is not judged. The root is memoized per declaring
module. No adapter is edited. `import-step` refuses at generation a
document outside the target project, so the scaffold never declares a
source the adapters would refuse.

**Manifest reading moves to `machinome.manifest`.** Discovery and the
validated model declaration leave `machinome.core.loader`, whose import
drags in the node base and numpy, for a top-level stdlib-only module; the
loader re-exports every moved name as the same object and builds
`read_project` from the declaration. Vet and the adapters' containment
use it, and dispatching `machinome vet` imports no node module, no
`machinome.core` module, no kernel and no other command.

## Consequences

- A host can ask one question, `machinome vet --json`, read one object,
  and branch on the exit status: 0 pure, 1 not pure, 2 cannot vet.
- Vet is not a sandbox. It pairs with a runtime that lacks the
  capability; that pairing is each consumer's own change, in its own
  repository.
- Every framework release rewrites the declaration's version, and every
  change to the universe is a reviewed edit to one data file.
- The residuals are recorded rather than closed: `Path.replace`,
  `Path.rename` and `ElementTree.write` are not denied; a `.open` method
  with another signature is judged on its first argument; a local
  rebinding or a computed attribute name evades the rules; shadowing
  covers universe names only; the contract is trusted whole outside its
  denylist.
- Behaviour changes only for a source outside its project, which no
  catalogue project declares.
