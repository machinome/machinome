## Why

On 12 October 2026 the pilot decided: "I'd like to have one single machinome
cli with packages contributing subcommands." Three products of the set need a
subcommand of `machinome` and have no way to add one: the videomaker, which
joins the repository as the distribution `machinome-movie` and is to be born
as `machinome movie <verb>` (list, evaluate, watch, check, speech, preview,
render, build, live, review, setup); the skills package, as `machinome skills
install|update|list`; and the studio, as `machinome studio`. The framework's
command knows only its own table, `machinome.cli.COMMANDS`, and the cli spec
says no entry-point group is consulted to find a command. On the bench at
484a528f, `machinome movie build film.yaml` exits 2 with the 0.4 migration
hint, because the guard reads the videomaker's verb `build` as a framework
command, and `machinome movie render film.yaml`, `machinome skills install`
and `machinome studio --port 9010` exit 2 with "invalid choice" (design.md,
probe 1). This change founds the seam those three joins register through, and
proves it with a test fixture; no contributor exists in this change.

## What Changes

- **An entry-point group `machinome.commands`.** An installed distribution
  declares a command as `name = "package.module:Class"`, the location the
  table already holds as a pair, resolved by the same code. The class meets
  the contract the framework's ten commands meet: constructed with no
  argument, its docstring its help, `add_arguments(parser)`, `handle(args)`,
  and `needs_node` declared as a boolean (design.md, Decisions 1 and 2).
- **The group is read only off the table's path.** The command is the first
  argument that does not begin with `-`; when it is a framework command, the
  group is not read and the dispatch costs what it costs today. The help, an
  unknown name, the migration guard's path and a contributed command read it.
  Measured on the bench: the read adds about 56 ms to a process that has not
  imported `importlib.metadata`, nothing measurable to `machinome -h`, and
  nothing to `machinome vet -h` (Decision 3).
- **The grammar reads the union.** The migration guard and the command
  selection use the framework's names and the contributed ones, and the
  command is selected by position, so a contributed command's verb that
  spells a framework command (`machinome movie build`) is that command's
  argument, not a framework command. `machinome -h` lists contributed commands
  after the framework's, by name; an unknown name's error names them too
  (Decisions 4 and 5).
- **Collisions and failures are named, never resolved by install order.** A
  contributed name equal to a framework command's is not used, with one
  warning line; a name two distributions contribute runs neither and names
  both; a contributed command whose module refuses for an absent extra is
  answered by the extra, as `import-step` is; a class that does not meet the
  contract is refused naming the unmet term; any other import failure
  propagates. The help lists each of these as unavailable, with the reason,
  and still exits 0 (Decisions 6 and 7).
- **Tests, red first**, through temporary distributions written by a test
  helper (a `.dist-info` with an `entry_points.txt` and a module, on
  `sys.path` or `PYTHONPATH`): the listing, the dispatch, the verb that
  spells a framework command, the guard, the unknown name, both collisions,
  the absent extra, the unmet contract, the broken location, the import
  isolation both ways; the conformance walk of `test_cli_lazy_imports.py`
  extended to contributed entries; the help-fidelity oracle pinned to the
  framework's commands so it holds when a contributor is installed
  (Decision 8).
- **Records**: ADR-189 (BUILD), amending ADR-024 and ADR-168; one section of
  `docs/reference/cli.rst`; the CLI section and the Map of
  `docs/architecture.md`; `HISTORY.rst` and the manual's changelog; the ADR
  index (Decision 9).

Not in this change: the existing scripts `machinome-viewer` and
`machinome-studio`, which stay; any command of the videomaker, the skills
package or the studio; any entry in the group from a distribution of the
repository; a version bump, an upload or a push.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `cli`: a new requirement for commands an installed package contributes
  through `machinome.commands`; the command-first grammar's guard and
  selection read the framework's and the contributed names, the command
  being the first argument that is not an option; the extra requirement's
  closing sentence, which forbade any entry-point group, says that no group
  is consulted for a framework command.
- `cli-startup-cost`: importing the CLI imports no `importlib.metadata`, a
  framework command's dispatch reads no entry-point group, a contributed
  command's dispatch imports no framework command module, and the unknown
  name's error and the help include the contributed commands.

## Impact

- **Code.** `packages/machinome/machinome/cli.py` only: the group's name, a
  reader of the group, a resolver of a contributed entry sharing the table's
  instantiation, and `manage()`'s selection, guard and listing. No other
  module, no manifest, no extra and no dependency changes.
- **Tests.** New `tests/test_cli_contributed.py` and the helper
  `tests/contributed_commands.py`; `tests/test_cli_lazy_imports.py` gains the
  contributed conformance walk and pins its help oracle to the framework's
  commands. The CLI modules' base on the bench: `test_cli_lazy_imports.py` and
  `test_cli.py`, 37 passed, 1 skipped (no viewer installed), 31 subtests.
- **Records.** Two delta specs; ADR-189 new, ADR-024 and ADR-168 amended; the
  manual's command reference and changelog; `HISTORY.rst`;
  `docs/architecture.md`. `CONTRIBUTING.rst` says nothing of how a command is
  declared and is unchanged.

Originating evidence: the pilot's decision of 12 October 2026; the three
invocations of probe 1 on the bench; the videomaker's `bin/videomaker.mjs` and
`python/machinome_movie/__main__.py`, the studio's `floor/orchestrator.py`
`main` and the skills package's README, read for the shape of the seam; and
the probes recorded in design.md.
