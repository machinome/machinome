## Why

Three hosts run project code they did not write, and none of them can
check what that code reaches:

- **machinome.org intake** runs `machinome models --json`, `machinome
  export` and `machinome snapshot` for every Foundry project on the
  pilot's machine, with the operator's authority.
- **The studio floor** keeps its agent tools behind the floor MCP
  server's project gate (studio ADR 0026). That gate has a gap:
  `machinome build` and `machinome test` run whatever the agent wrote,
  with the operator's authority. An agent that adds `subprocess` to a
  model has stepped outside the gate.
- **Browser delivery**, once it exists, runs a project in a runtime
  with no operating system at all. A project has to be known to fit
  before it is sent there.

The pilot's framing (settled 2026-09-26, `workflow/ongoing/vet.md`): a
machinome project is a pure machine simulation. It imports the
framework, the kernels the framework depends on, and pure computation.
It runs no command, opens no socket, imports nothing by a computed name
and writes no file. By the pilot's decision of 2026-09-26, reads inside
the project are pure: a pure project reads only inside its own tree and
writes nothing. Containment of reads is the runtime's, and containment
of declared sources is the adapters'. None of the three hosts can check
the rest today without running the project. Running it is the risk they
are trying to avoid.

The note surveyed every `*.py` under a project's `simulation/`
directory, leaving out paths containing `/.git/`, `/_build`, `/WTs/`,
`/tests/`, `/tools/`, `/scripts/` or `/.venv/`, and files named
`test_*.py` or `conftest.py`: 1,131 files on 2026-09-26. Almost
everything already stays inside the contract, the kernels and pure
stdlib. The exceptions are real findings, and the reads decision admits
the path arithmetic projects actually do:

| What the code does | Files | Where | Under vet |
| --- | --- | --- | --- |
| Runs a process through `subprocess` | 4 | Metamaquina2, snappy-reprap and hangprinter echo OpenSCAD parameter values; the 3DPrintedClocks quality audit | finding |
| Fetches over the network (`urllib`) | 1 | openvmp `don1/catalogue.py` | finding |
| Writes a file (write-mode `open`, `Path.mkdir`/`write_text`, `os.makedirs`/`os.replace`) | 7 | the three printers, the clocks audit, openvmp, Internal-Cycloidal-Actuator, Curta | finding |
| Lists a directory through `os` (`os.listdir`, `os.walk`) | 6 | `scad.py` in kossel, Prusa3-vanilla, Metamaquina2, snappy-reprap, hangprinter; openvmp `blueprints.py` | allowed under the reads decision: a directory listing is a read |
| Mutates `sys.path` | 2 | fender-bender; an archived openflexure-microscope evidence script no model reaches | finding where reached |
| Other stdlib outside the pure tier (`sys`, `tempfile`, `zipfile`, the audit's `argparse` and others) | 8 | the printers, the clocks audit, Internal-Cycloidal-Actuator, openvmp, fender-bender | finding; `ast`, which Voron-2's `viewer_pose.py` needs and nothing else, is admitted as pure |
| Third-party outside the kernels (`yaml`, `jinja2`) | 1 | openvmp `blueprints.py` | finding |
| Uses shapely | 2 | Poleni-1709 (two checkouts) | allowed; shapely becomes a framework dependency |
| Reads a project file by hand (`open`/`.open` with no write mode) | 9 | Prusa3, openvmp, Voron-2, orcahand, the printers' parameter files, and the writers above | allowed under the reads decision |
| Imports `os` or `pathlib` | 31 | 25 projects | allowed under the reads decision |
| Adapter sources computed rather than literal | 14 (122 assignments) | 11 projects, among them Thor, YouCanBuildDog, Pascaline-module and Curta | allowed under the reads decision; bounded at construction |

An earlier count of 1,892 files included the copies under
`.git/licensing-worktrees/`. The 625 literal source declarations in the
catalogue all resolve under their project root, and no project with
computed sources holds a symbolic link leaving its root, so the adapters'
new containment check refuses nothing in the catalogue today.

## What Changes

- **A new command, `machinome vet [reference] [--tests] [--json]`.**
  It checks, statically, that a project stays inside the machinome
  universe. It reads only the bytes of the project tree and the
  universe declaration. It never imports project code, never imports a
  kernel, and never reads site-packages. It reports one verdict per
  model and one for the project. The verdict word is `pure`. Each
  finding carries a path, a line, a kind and the offending name. Text
  output is for people and `--json` is for hosts. The exit status is
  nonzero when any model is not pure.
- **The universe is a versioned declaration shipped with the framework
  package.** It is data, and it names the framework version it
  describes. It has three tiers and a tests tier. The contract
  (`machinome`, `machinome_mechanics`, `molejo`) is allowed whole except
  a denylist of the framework's own modules that spawn processes, write
  outside the build, or import by name. The kernels (`cadquery`,
  `build123d`, `OCP`, `solid2`, `trimesh`, `numpy`, `scipy`,
  `manifold3d`, `shapely`) are allowed except for a curated denylist of
  IO entry points. The pure stdlib tier is an explicit list that now
  holds `ast`, `os`, restricted to `os.path` and directory listing, and
  `pathlib`, whose mutating methods are file writes; every name outside it is outside the
  universe. The tests tier (`unittest`, `pytest`, `logging`) applies only to files
  reached solely through a companion test. The universe is not derived
  from what happens to be installed, so a verdict is a property of the
  project and the framework version, not of the machine.
- **Three assertions:**
  1. **Closure.** From every model the manifest declares, imports are
     resolved statically to files under the project root and vetted
     transitively, including every package `__init__.py` on the path. A
     name that does not resolve under the root must be a universe
     member. A project file that shadows a universe name is a finding.
  2. **No dynamic route and no write.** A vetted file uses no `exec`,
     `eval`, `compile` or `__import__`, no `importlib` or `runpy`, does
     not touch `sys.path` or `sys.modules`, names no denied dunder
     (`__path__` among them) either as an attribute or as a string
     literal, reaches no kernel IO entry point and no framework
     internal, and opens no file for writing: `open` and `.open` pass
     only with no mode or a literal mode free of `w`, `a`, `x` and `+`.
  3. **Sources stay home.** Every declared adapter source (`stl_source`,
     `step_source`, `scad_source`, `jscad_source`) stays under the
     project root: statically for a literal, which must be relative and
     resolve under the root; at run time for every declared source,
     because `require_source_file` refuses at construction a source
     whose real path leaves the project root. A `jscad_source` is a
     finding in this universe.
- **The source adapters refuse a source outside the project.** The STL,
  STEP, OpenSCAD and JSCAD adapters, through `require_source_file`,
  refuse with `ValueError` a declared source whose real path is not
  under the real path of the declaring module's project root. The
  marking artwork (`Svg`), which is admitted through the same function,
  is refused the same way. A declaring module that lies in no project is
  not judged.
- **Scope.** By default vet checks the model closure, which is exactly
  what `export` and `snapshot` execute. `--tests` adds the companion
  tests that the framework's own naming rule pairs with each vetted
  module, plus their closures, which is what `machinome test` executes
  on the floor. Nothing else in the tree is read.
- **A kernel-free manifest module.** Manifest discovery and model
  declaration move out of `machinome.core.loader`, which imports the
  node base and numpy with it, into a new top-level module
  `machinome.manifest`. The loader, vet and the adapters' containment
  check use it. The loader re-exports every name it moves, so every
  existing caller keeps working.
- **shapely becomes a framework dependency**, pinned to the installed
  minor (`shapely==2.1.*`), because a universe member the framework does
  not install would let a project pass vet and fail at import.
- **A `workflow/warts.md` entry.** Three printers run OpenSCAD
  themselves to echo parameter values. That is a gap the SCAD import
  could close.

**Not in this change:**
- Vet is not a sandbox. It shows that a project *declares* nothing
  outside the universe and has no syntactic route around that
  declaration. It does not prove that a computed read stays inside the
  project; the runtime bounds that. The runtime that lacks the
  capability is the sandbox. The report says so in its preamble.
- Vet does not parse JavaScript or OpenSCAD. OpenSCAD files pass
  unread, because OpenSCAD reads files and nothing else and the runtime
  bounds the filesystem. A `jscad_source` is refused rather than read.
- No universe profiles yet. Browser delivery will want a second,
  narrower universe without OpenSCAD. Giving the declaration a name now
  makes that second universe an addition later, but this change builds
  only one.
- No host wiring. machinome.org intake and the studio floor adopt vet
  in their own repositories as separate changes.
- No `[tool.machinome] pure` manifest key, no fixes to the projects the
  first vet will flag, and no change to what `build`, `test`, `export`
  or `snapshot` do beyond the adapters' containment refusal.

## Capabilities

### New Capabilities
- `vet`: the universe declaration, the static closure resolver, the
  three assertions and every finding kind they raise, the default and
  `--tests` scopes, the report (text, JSON, exit status), and the
  guarantees that vet imports no kernel and no project module.

### Modified Capabilities
- `cli`: the command registry gains `vet`. The node-reference
  requirement names `vet` as a command with its own reference
  positional: the same four spellings, no `--set`, and no argument
  means every declared model rather than the default one.
- `cli-startup-cost`: running `machinome vet` imports vet's modules and
  the manifest module, and no other command's module, no node module
  and no kernel. Importing the manifest module loads nothing from the
  node package.
- `stl-import`: "STL source declaration and freshness" refuses an
  `stl_source` whose real path leaves the project root.
- `step-import`: "STEP source declaration and freshness" refuses a
  `step_source`, absolute or relative, whose real path leaves the
  project root.
- `node-model`: "A source-bound leaf names its missing file", which
  governs all four adapters and is the only requirement stating the
  OpenSCAD and JSCAD source declarations, gains the containment refusal.
- `markings`: "A marking's artwork is a declared drawing file" refuses
  artwork outside the project root, because the artwork is admitted
  through the same function.

## Impact

- New module `machinome/manifest.py`, which receives
  `ProjectManifestError`, `MODEL_NAME`, `_find_manifest`,
  `project_root` and the validated model declaration from
  `machinome/core/loader.py`. `loader.py` imports them from there and
  re-exports them under the same names.
- `machinome/node/sources.py`: `require_source_file` gains the
  containment refusal, finding the root through `machinome.manifest`.
- New package `machinome/vet/`: the universe declaration
  (`universe.toml`), the static resolver, the assertions and the
  report. New command module `machinome/manager/vet.py`, registered in
  `machinome/cli.py`'s `COMMANDS`.
- `pyproject.toml`: `shapely==2.1.*` joins `[project] dependencies`.
- `setup.cfg`: a `[bumpversion:file:machinome/vet/universe.toml]`
  section, so a release cannot leave the declaration's version behind.
- Tests: fixture projects under `tests/vet_projects/`, one pure project
  and one per finding kind, added to `tests/conftest.py`'s
  `collect_ignore`. The golden help oracle in
  `tests/test_cli_lazy_imports.py` gains `vet`. The containment refusal
  is tested red first in `tests/test_missing_source_file.py`, the
  adapters' existing admission tests.
- Documentation: the CLI section of `docs/architecture.md`, and a
  `machinome vet` section in the manual's `docs/reference/cli.rst`,
  written under `skills/write-the-manual`. The studio's
  `shop-skills/machinome-api/SKILL.md` belongs to another repository
  and is not touched here.
- `workflow/warts.md`: the OpenSCAD parameter-echo finding.
- No change to the published document, the build pipeline or the
  viewer. The only existing behaviour that changes is the adapters'
  refusal of a source outside the project, which no catalogue project
  declares today.
