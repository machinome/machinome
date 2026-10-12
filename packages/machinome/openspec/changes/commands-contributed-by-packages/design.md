## Context

A small framework cycle of the 0.9 joins campaign (`workflow/ongoing/joins-0.9.md`
at the repository root), on the bench `machinome/WTs/v0.9-joins-command-seam`,
branch `v0.9-joins-command-seam`, cut from the line `v0.9-joins` at 484a528f
(the line's head after `join-mechanics`). It is not one of the plan's joins: no
import and no merge. It runs beside the viewer's join on another bench, which
takes ADR-188; this change takes ADR-189.

The pilot's decision of 12 October 2026: "I'd like to have one single machinome
cli with packages contributing subcommands." Unifying the commands that exist
today (`machinome-viewer`, `machinome-studio`) is deferred. This change founds
the seam: the framework's one command, `machinome`, learns its subcommands from
the installed packages as well as from its own table. The first contributor is
to be the videomaker, joining as the distribution `machinome-movie`, born as
`machinome movie <verb>` (list, evaluate, watch, check, speech, preview,
render, build, live, review, setup); the second the skills package,
`machinome skills install|update|list`; the third the studio, `machinome
studio`. None exists in this change; each later join registers its command
through the seam. The skills package was not placed by the plan of 11 October
2026; the decision of 12 October 2026 names it as a contributor, and nothing
here depends on where it lives.

What the CLI is today (`packages/machinome/machinome/cli.py`, 207 lines):

- `COMMANDS` maps ten names to `(module, class_name, needs)`, in the order
  `machinome -h` lists them. `resolve_command(name)` imports the module and
  instantiates the class; `require_needed_module(name)` loads the node type a
  command needs through `machinome.node.supported` and answers an absent one
  with `Error: machinome <name> needs the <extra> extra: <refusal>`, exit 1
  (ADR-168, ADR-179); `add_command_parser` registers a command's subparser
  with its docstring as help and, when `needs_node`, the shared `reference`
  positional and `--set`.
- `manage()` runs the pre-0.4 guard (`argv[1]` not in `COMMANDS` and `argv[2]`
  in it: exit 2 and the hint), then selects `next(arg for arg in argv[1:] if
  arg in COMMANDS)`: the first argument, at any position, that spells a
  command. A selected command alone is resolved; `-h` or no argument resolves
  all ten (`HELP_FLAGS`, the one path that loads every command); anything else
  resolves none, and argparse reports the invalid choice against the names.
- The cli spec's requirement "A command that needs an extra is answered by the
  extra" ends: "No entry-point group or plugin registry SHALL be consulted to
  find a command." That sentence came from the lean-core plan's D2 and D3 (2
  October 2026) and ADR-168, which settled that a command whose implementation
  moves with a node package is found through the core's table, not through
  an entry-point group. ADR-179 weighed "discover renderers and commands from
  installed portions through entry points" as its option 3 and left it as "the
  pilot's later decision". The decision of 12 October 2026 is that later
  decision for commands: the three commands are of products the core does not
  ship and must not name.
- The framework already has one seam for a package it never imports: the
  viewer's entry point `bundle` in the group `machinome.viewer`
  (`machinome/viewers/bundle.py`), declared by the viewer's manifest as
  `[project.entry-points."machinome.viewer"] bundle =
  "machinome_viewer.bundle:describe"`. An absent node package is refused by
  its extra at its import (ADR-184), through the table of supported node
  types; nothing of that applies here, because a contributed command exists
  only when its package is installed.
- `tests/test_cli_lazy_imports.py` proves what a dispatch imports in a fresh
  interpreter (`tests/import_probe.py`), compares the help byte for byte with
  an eager reference parser, and walks the table so a moved class fails in the
  suite. The `cli-startup-cost` spec asserts module sets, not times; the
  timings of `fast-cli-startup` (about ten seconds of startup across
  `develop`, `build` and `snapshot`) were its proposal's motivation.

The three products' command surfaces, read for the seam's shape (read-only):
`videomaker/bin/videomaker.mjs` parses `check|speech|preview|render|build|
live|review` with Node's `parseArgs`; `videomaker/python/machinome_movie/
__main__.py` builds an argparse parser with subcommands `list`, `evaluate`,
`watch`; the studio's `floor/orchestrator.py` `main()` builds an argparse
parser (`--port`, `--projects-dir`, two hidden options) and runs the floor;
the skills package (`machinome-skills/README.md`) is today an instruction
package copied by hand, with no command. Each fits a class whose
`add_arguments(parser)` adds its options or its verbs as subparsers and whose
`handle(args)` runs them: probe 5 runs such a class with three verbs.

Facts below were read or run on the bench at 484a528f, its venv synced from
the lock (CPython 3.12.3, 179 `.dist-info` in `site-packages`), unless marked
*inferred*. Probes ran in the scratch directory
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C4-propose/`
(`<scratch>`), never in the bench; the prototype of probe 5 is a scratch copy
of `cli.py`, never the bench's file. The OS page cache was warm in every
timing: dropping it needs root, so "cold" below means the first call in a
fresh interpreter.

### Probes

1. **Today's answers to the three commands** (`<scratch>/probe_today.out`):
   `machinome movie build film.yaml` exits 2 with "The CLI grammar changed in
   0.4: commands come first. Try: machinome {command} {path} [options]": the
   guard reads `argv[1]` = `movie` as unknown and `argv[2]` = `build` as a
   framework command. `machinome movie render film.yaml`, `machinome movie
   list .`, `machinome skills install` and `machinome studio --port 9010` exit
   2 with argparse's "invalid choice" naming the ten. A movie named `build`
   (`machinome movie evaluate . build`) would today select `build`, by
   reading (not run: there is no `movie` to run it with).
2. **The cost of reading a group** (`<scratch>/probe_scan_cost.py`, ten fresh
   interpreters, `<scratch>/probe_scan_cost.out`): `import machinome.cli`
   11.6 to 19.5 ms and it does not import `importlib.metadata`; importing
   `importlib.metadata` 22.1 to 32.9 ms; the first
   `entry_points(group='machinome.commands')` in the process 24.3 to 39.9 ms
   (0 entries); the second in the same process 20.7 to 26.8 ms.
3. **Whole invocations, today** (`<scratch>/probe_wall.py`, median of ten,
   `<scratch>/probe_wall.out`): `python -c pass` 50 ms; `python -c "import
   machinome.cli"` 59 ms; `python -c` importing `importlib.metadata` and
   reading the group 106 ms, so the read costs about 56 ms to a process that
   has not imported `importlib.metadata`; `machinome -h` 825 ms; `machinome
   viewer` 121 ms (no viewer installed in the bench venv); `machinome build
   -h` 224 ms; `machinome vet -h` 53 ms; `machinome frobnicate` 54 ms.
4. **What `importlib.metadata` reports** (`<scratch>/make_dist.py`, which
   writes a `.dist-info` with `METADATA` and `entry_points.txt` and a module
   beside it): with `<scratch>/dists/one` (the distribution `fake-movie`,
   `movie = fake_movie_cli:Movie`) twice on `PYTHONPATH` and
   `<scratch>/dists/clash` (`fake-clash`: `build = fake_clash_cli:Build`,
   `movie = fake_clash_cli:Movie`), the group returns three entries: `movie`
   of `fake-movie` once, `build` and `movie` of `fake-clash`; each entry
   carries `.name`, `.value`, `.module`, `.attr` and `.dist.name`. A
   distribution found twice on the path is reported once (the standard
   library deduplicates by normalised distribution name, first on the path
   first); two distributions declaring one name are both reported. In the
   bench venv every member of the workspace is found twice, its `.dist-info`
   in `site-packages` and a stale `*.egg-info` in its package directory
   (ignored by `.gitignore`), 192 distributions raw for 179 unique; no group
   of the venv is named `machinome.*` (the twenty groups present include
   `twine.registered_commands`, `flake8.extension`, `pytest11`).
5. **A prototype of the seam** (`<scratch>/proto/patch_proto.py` applied to a
   scratch copy of `cli.py`, run through `python -c "from proto_cli import
   manage; manage()"`, `<scratch>/probe_proto.out`): with `fake-movie`
   installed, `-h` lists `movie` after `vet` with its docstring and the
   choices read `{build,...,vet,movie}`; `movie build film.yaml` prints
   `movie build film.yaml`, exit 0; `movie -h` shows the movie's three verbs;
   `frobnicate` names `movie` among the choices; `film.yaml movie` gives the
   migration hint, exit 2; `vet -h` is today's. With `fake-clash` too: `-h`
   writes one warning that `fake-clash`'s `build` is not used and lists
   `movie` as "(unavailable: contributed by fake-movie (fake_movie_cli:Movie)
   and fake-clash (fake_clash_cli:Movie))"; `movie list x` exits 1 naming
   both; `build -h` is the framework's, with no warning (the group is not
   read). With `<scratch>/dists/broken` (`gone` naming a missing module,
   `bare` a class with nothing): `-h` raised `ModuleNotFoundError` in the
   prototype, which listed only failures it caught (the reason for Decision
   7's help rule); `bare` exits 1 naming the missing docstring. With no
   contributor, `-h` is today's output. A command shipped as a portion of
   the `machinome` namespace (`<scratch>/dists/portion`, the module
   `machinome/fake_portion_command.py` with no `__init__.py` above it, the
   entry `portioned = machinome.fake_portion_command:Portioned`) is listed
   and runs: the core's `_namespace_portions` admits it, which is how
   `machinome.movie` is to ship (*inferred* from ADR-183's shape).
6. **The prototype's cost** (`<scratch>/probe_proto_wall.py`, median of ten
   with `fake-movie` installed, `<scratch>/probe_proto_wall.out`): today /
   prototype: `-h` 848 / 838 ms; `vet -h` 62 / 62 ms; `frobnicate` 55 / 112
   ms; `movie build film.yaml` 50 (the hint) / 122 ms. The help pays nothing
   measurable because its path already imports `importlib.metadata`, through
   the `build` command's modules; a framework command pays nothing because the
   group is not read.
7. **Which dispatches import `importlib.metadata` today** (in-process from a
   fresh interpreter): `vet -h`, `new -h` and `models -h` do not; `build -h`
   and `viewer` do (`VerdictStoreImportWeight.BUILD_BASELINE` already records
   it for `build`; `viewer` reads its own group).
8. **The base of the CLI modules**: `env -C <bench>/packages/machinome
   <bench>/.venv/bin/python -m pytest -q -p no:cacheprovider -rs
   tests/test_cli_lazy_imports.py tests/test_cli.py`: 37 passed, 1 skipped
   ("machinome-viewer not installed"), 31 subtests. With
   `test_vet_isolation.py`, `test_named_models.py` and
   `test_supported_node_types.py`: 90 passed, 1 skipped, 117 subtests.

## Goals / Non-Goals

**Goals:**

- One command, `machinome`, to which an installed package adds a subcommand by
  declaring it, with no edit to the framework.
- A contributed command written as the framework's commands are written, so
  a reader of either knows the other, and one resolver for both.
- The framework's own commands answered exactly as today, at today's cost.
- Every failure of a contributed command named by its distribution and its
  location; none decided by install order; none able to hide the framework's
  help.
- The seam proved by tests that install a fake distribution, so each later
  join only registers.

**Non-Goals:**

- Any command of the videomaker, the skills package or the studio.
- Retiring `machinome-viewer` or `machinome-studio`, the scripts that exist
  today.
- A version or a contract number for the seam, a base class, a decorator or
  a registry object.
- Help or completion beyond argparse's.
- The order of a contributed command among the framework's, or aliases.

## Decisions

### 1. The group `machinome.commands`, each entry a class's location

An installed distribution declares a command in its manifest:

```toml
[project.entry-points."machinome.commands"]
movie = "machinome.movie.cli:Movie"
```

The entry's name is the command's name; its value is `module:Class`, the
location the table holds as a pair (`('machinome.manager.vet', 'Vet', None)`).
One instantiation serves both: `resolve_command(name)` takes the table's
`(module, class_name)` and a contributed entry its `(entry.module,
entry.attr)`, and both import the module and call the class with no argument.

Why a group: the pilot decided that packages contribute; the core does not
ship, import or name the three products, and the skills package may never be
a member of the repository. The group is the standard library's way for a
distribution to tell another what it provides without being imported, and the
framework already reads one (`machinome.viewer`). Why this name: it says what
each entry is, a command of `machinome`, and echoes `COMMANDS`; the viewer's
group is likewise named for what it provides.

Alternatives: (a) a row per product in the core's table, as `import-step`'s
node type is named (lean-core D3): the core would name products it does not
ship, against the decision's "packages contributing", and a package outside
the repository could not add one; (b) the entry naming a factory function
rather than the class: a second shape beside the table's, for nothing the
class does not do; (c) `machinome.cli` or `machinome.subcommands` as the
group's name (Open Questions 1); (d) each product keeping its own script: the
state the decision ends, deferred only for the two that exist.

### 2. The contract: what the framework's ten already meet

A contributed command's class SHALL:

1. be constructed with no argument, and construct cheaply: the help path
   constructs every command;
2. carry a non-empty docstring, its help in `machinome -h`;
3. define `add_arguments(parser)`, which registers its options, positionals
   or verbs on the subparser it is given (a command with verbs adds
   subparsers, as probe 5's `Movie` does);
4. define `handle(args)`, which runs it with the parsed namespace; it sets
   its exit status by raising `SystemExit` (`sys.exit`), as `vet` does, and
   exits 0 when it returns;
5. declare `needs_node` as `True` or `False`. When `True`, the CLI gives it
   what it gives the node-scoped commands: the `reference` positional, `--set`
   and the refusal of a directory as a reference. Every one of the ten
   declares it; for a contributed class the CLI does not assume `True` as
   `add_command_parser` does for the table, because a contributor that forgot
   it would silently grow a `reference` positional.

Its module should import little at module scope, since `machinome -h` imports
it; that is stated in ADR-189 and not checked. A class that fails 2, 3, 4 or 5
is refused by Decision 7, naming the first unmet term in that order: "no
docstring", "no add_arguments()", "no handle()", "needs_node is not declared
as True or False". 1 is not checked: a constructor that needs an argument
raises `TypeError`, which propagates as any other failure to load does.

### 3. When the group is read

The command is the first argument that does not begin with `-` (Decision 4).
When it is a framework command, the group is not read: the dispatch imports
what it imports today and costs what it costs (probe 6: `vet -h` 62 ms before
and after). Every other path reads the group once, through a function that
imports `importlib.metadata` inside its body, so `import machinome.cli` stays
free of it (probe 2):

| Path | Reads the group | Measured cost of the read (probe 6) |
| --- | --- | --- |
| a framework command, its `-h` included | no | none |
| `machinome -h`, `--help`, no argument | yes | none measurable: the help already imports `importlib.metadata` (848 / 838 ms) |
| a contributed command | yes | about 56 ms over the CLI's import: 122 ms for the fake movie |
| an unknown name, the migration guard's path | yes | 55 / 112 ms |

Against `cli-startup-cost`: its requirements assert module sets, and the read
imports no command module, no `machinome` module and no project code; a
framework command's dispatch keeps its module set exactly (a new scenario pins
that `importlib.metadata` is absent from `vet -h`'s, probe 7). The only path
that becomes slower is the error of an unknown name, by about 57 ms, which no
automation runs (Open Questions 5).

Alternative: read the group on every invocation, so a contributed name could
shadow a framework one. Every framework command would pay about 56 ms, `vet
-h` doubling from 53 ms, for a shadowing the collision rule forbids anyway.

### 4. The command is selected by its position, from the union

Today's `selected = next(arg for arg in argv[1:] if arg in COMMANDS)` takes
the first argument that spells a framework command, at any position. A
contributed command's own arguments may spell one: the videomaker's `build`
verb (`machinome movie build film.yaml`), or a movie named `test`. So:

- the command is `first`, the first argument that does not begin with `-`
  (top-level options take no value, so no earlier argument is an option's
  value; `--` begins with `-` and is skipped, as argparse skips it);
- the guard reads the framework's names and the contributed ones on both
  sides: `len(argv) > 2 and argv[1] not in names and argv[2] in names` gives
  the hint, so `machinome film.yaml movie` is answered as `machinome
  mynode.py develop` is;
- `first` in `COMMANDS` resolves that command as today (`require_needed_module`
  first); `first` among the contributed resolves it (Decision 7); no argument
  or `argv[1]` in `HELP_FLAGS` resolves every command of both; anything else
  resolves none, and argparse reports the invalid choice against every name.

No framework invocation changes its answer. The cases where `first` and
today's `selected` differ are those where an argument before the first
framework name is not an option: today that argument is argparse's invalid
choice (`machinome x y build` exits 2 naming `x`), or the guard (`machinome x
build`), and it still is; only the read of the group is added, on that error
path.

### 5. The listing: the framework's commands, then the contributed by name

`machinome -h` lists the ten in `COMMANDS` order, then the contributed
commands in the order of their names, so the help reads the same whatever
order the distributions were installed in. Each is registered with
`add_command_parser`, its docstring the help. An unknown name's error lists
the same names in the same order (argparse's choices).

### 6. Collisions

- **A contributed name equal to a framework command's**: the framework's
  command, always. Decision 3 makes this the only possible rule, since a
  framework name never reads the group. The contributed entry is dropped when
  the group is read, with one line on standard error per dropped entry:

  ```
  Warning: <distribution> contributes the command <name> (<value>), which is machinome's own; it is not used
  ```

  The help still exits 0 and its standard output is the framework's help as
  if the entry did not exist.
- **One name contributed by two or more distributions**: none of them runs.
  Install order is the order of `sys.path`, which says nothing about intent.
  Invoking the name imports none of their modules, writes one line and exits 1:

  ```
  Error: machinome <name> is contributed by more than one package: <dist> (<value>), <dist> (<value>)
  ```

  The help lists the name once, its help "(unavailable: contributed by more
  than one package: ...)".
- **One distribution found twice on the path** (the bench's `.dist-info` and
  stale `.egg-info`, probe 4) counts once: the standard library already
  deduplicates by distribution name, and the reader adds nothing.

### 7. A contributed command that cannot run

The core cannot refuse an absent contributor: an entry exists only when its
distribution is installed. What can fail is the installed one:

- **Its module refuses for an absent extra** (`machinome.extras.
  ExtraUnavailable`, which every refusal of the framework's extras raises):
  answered as `require_needed_module` answers `import-step`, one line and exit
  1, before its arguments are parsed:

  ```
  Error: machinome <name> needs the <extra> extra: <refusal>
  ```

- **Its class does not meet the contract** (Decision 2): one line and exit 1,
  before its arguments are parsed:

  ```
  Error: machinome <name>: <distribution> (<value>) does not meet the command contract: <term>
  ```

- **Any other failure to import or construct it** propagates, with its
  traceback, as `resolve_command` lets a framework command's propagate: "a
  broken installation should say which module it could not load".

On the help path each of these, the collision of Decision 6 included, lists
the name with the help "(unavailable: <reason>)", the reason being the
refusal's text for an absent extra (`needs the <extra> extra: <refusal>`),
`<distribution> (<value>) does not meet the command contract: <term>`, or
`<distribution> (<value>) cannot be loaded: <ExceptionType>: <message>` for
any exception raised while importing or constructing it; and the help exits 0.
One broken package must not take `machinome -h` from every user of every
other command (probe 5's traceback). Whether to list or to omit such a name
is Open Questions 6.

### 8. The tests, red first

A helper module `tests/contributed_commands.py` writes a fake installed
distribution into a temporary directory: `<name>-0.0.0.dist-info/METADATA`
(`Metadata-Version`, `Name`, `Version`), `entry_points.txt` with the section
`[machinome.commands]`, and the module source beside it (probe 4's
`make_dist.py`, made a function). It offers the directories as a `PYTHONPATH`
for `import_probe.probe(..., env=...)` (with `REPO_DIR` first, as the probe
sets it), and, in-process, a context manager that prepends them to `sys.path`,
calls `importlib.invalidate_caches()`, and removes the fake modules from
`sys.modules` on exit. The fake distributions, each module a top-level name
starting `machinome_fake_`, but the portion:

| Fake | Entries | Its class |
| --- | --- | --- |
| `fake-movie` | `movie` | docstring; `needs_node = False`; verbs `list`, `build`, `render`, each with a positional `source`; prints `movie <verb> <source>` |
| `fake-skills` | `skills` | docstring; `needs_node = False`; verbs `install`, `list`; prints them |
| `fake-node` | `measure` | docstring; `needs_node = True`; prints `args.path` and `args.set` |
| `fake-shadow` | `build` | a conforming class that prints `shadow build ran` |
| `fake-movie-two` | `movie` | a conforming class |
| `fake-needy` | `needy` | its module raises `ExtraUnavailable('step', 'the needy fake command', 'cadquery')` at import |
| `fake-bare` | `bare` | a class with no docstring, no methods, no `needs_node` |
| `fake-gone` | `gone` | the value names a module that does not exist |
| `fake-portion` | `portioned` | the module `machinome/fake_portion_command.py`, no `__init__.py` above it (probe only) |

New module `tests/test_cli_contributed.py`, each test with its expected red on
the base:

1. `-h` with `fake-movie` and `fake-skills` (probe): exit 0; `movie` and
   `skills` each followed by its docstring (whitespace removed, as
   `test_top_level_help_lists_every_command_with_its_docstring` reads); the
   choices `{build,...,vet,movie,skills}`. Red: neither is listed.
2. `movie build film.yaml`, `movie list build`, `movie render film.yaml`
   (probe, `fake-movie`): stdout `movie <verb> <source>`, exit 0, the fake
   module imported and no module of `COMMAND_MODULES`. Red: the first exits
   2 with the migration hint; the second and third exit 2 "invalid choice:
   'movie'" (the second after resolving `build`).
3. `skills install` (probe, `fake-skills`): stdout `skills install`. Red:
   invalid choice.
4. `portioned hello` (probe, `fake-portion`): stdout `portioned hello`. Red:
   invalid choice.
5. `measure model.py --set bore=3` and `measure <a directory>` (in-process,
   `fake-node`): the handler receives `path` `model.py` and `set`
   `['bore=3']`; the directory is refused with exit 2 naming the spellings,
   as `test_node_commands_reject_a_directory_naming_the_spellings` reads.
   Red: invalid choice, exit 2 without the spellings.
6. `vet -h` with `fake-movie` installed (probe): exit 0, and
   `importlib.metadata` and the fake module absent from the imported modules.
   Green on the base, a guard (probe 7); its red is shown once by a temporary
   edit that reads the group on every path, reverted (`git diff` of `cli.py`
   back to the change's). `CommandImportIsolationTest.
   test_importing_the_cli_loads_no_command_module` in
   `test_cli_lazy_imports.py` gains the assertion that `importlib.metadata`
   is not imported; green on the base, a guard of the reader's deferred
   import, shown red once by the same kind of temporary edit (the import at
   module scope).
7. `frobnicate` (probe, `fake-movie`): exit 2, stderr names `movie` and the
   ten, no command module imported. Red: `movie` not named.
8. `film.yaml movie` (probe, `fake-movie`): exit 2, stderr the migration hint
   exactly. Red: argparse's invalid choice for `film.yaml`.
9. `fake-shadow` installed: `-h` exits 0, stdout equal to the help with no
   contributor, stderr the one warning line naming `fake-shadow`,
   `machinome_fake_shadow:Build` and `build`; `build -h` stdout the
   framework's `build` help, stderr empty, the fake module not imported.
   Red: no warning (stderr empty).
10. `fake-movie` and `fake-movie-two`: `movie list x` exits 1, stdout empty,
    stderr the one line naming both distributions and values, neither fake
    module imported; `-h` exits 0 and lists `movie` as unavailable naming
    both. Red: `movie list x` exits 2, invalid choice; `-h` lists no
    `movie`.
11. `fake-needy`: `needy` exits 1 with `Error: machinome needy needs the step
    extra: ` and the refusal; `-h` exits 0 listing `needy` as unavailable
    with `needs the step extra`. Red: invalid choice.
12. `fake-bare`: `bare` exits 1 naming `fake-bare`, its value and "no
    docstring"; `-h` lists it as unavailable. Red: invalid choice.
13. `fake-gone`: `-h` exits 0 listing `gone` as unavailable naming
    `ModuleNotFoundError`; `gone` exits 1 with a traceback naming the missing
    module. Red: `-h` does not list it; `gone` is an invalid choice.

`tests/test_cli_lazy_imports.py`:

14. `RegistryConformanceTest.test_the_group_is_named_machinome_commands`:
    `machinome.cli.COMMAND_GROUP == 'machinome.commands'`. Red:
    `AttributeError`.
15. `RegistryConformanceTest.test_every_contributed_entry_resolves_and_honours_the_contract`:
    walks `entry_points(group='machinome.commands')`, the group spelled in the
    test, of the suite's environment, through a module-level function
    `contract_failures(entry)` written independently of `cli.py` (the name not
    a framework command's; the distribution not `machinome`; one distribution
    per name; the class imports and
    constructs; docstring, `add_arguments`, `handle`, `needs_node` boolean).
    With no contributor installed today it walks nothing, and says so in its
    docstring: it is the walk that holds the videomaker and the studio once
    the workspace installs them. Green on the base (vacuous).
16. `RegistryConformanceTest.test_the_contract_walk_reads_a_fake_distribution`:
    `contract_failures` over the entries of `fake-movie` is empty and over
    `fake-bare`, `fake-gone` and `fake-shadow` names each failure. Red: an
    `ImportError`, the helper module not yet written; green once it is,
    before the seam, since this test proves the walk, not the seam.
17. `HelpFidelityTest` and `CommandNeedsTest.test_help_lists_import_step_without_its_extra`
    keep their oracle the framework's: the in-process help tests run with
    `importlib.metadata.entry_points` patched to return no entry for the
    group, so the byte comparison holds when a contributor is installed.
    Green before and after; its need is shown once by running
    `test_top_level_help_is_byte_identical` with `fake-movie` on `sys.path`
    and the patch removed (red after the seam: `movie` listed), reverted.

The probes and the in-process tests together prove each scenario of the delta
specs; the counts are recorded in `evidence.md`.

### 9. The records

- **ADR-189**, `docs/adrs/BUILD/ADR-189-a-package-contributes-a-command-through-the-group-machinome-commands.md`,
  in BUILD, whose section is "loading, watching, CLI" and holds ADR-024,
  ADR-059, ADR-168 and ADR-179 (Open Questions 4). Title: "A Package
  Contributes a Command Through the Group `machinome.commands`". Status
  Accepted at the archive; Date 2026-10-12; Change
  `commands-contributed-by-packages`; Amends ADR-024 (the registry has a
  second source, read off the table's path; the command is selected by
  position) and ADR-168 (its "no entry-point group" holds for the table's
  commands, not for a package's); Related to ADR-179 (its option 3, left to
  the pilot), ADR-059 (import at the point of use), ADR-184 (an absent
  package refused by its extra: not needed here, an entry exists only when
  installed). Context: the decision, probe 1. Considered options: the group
  (chosen); rows in the core's table; a factory entry; reading the group on
  every invocation; each product its own script. Decision outcome: Decisions
  1 to 7 in a paragraph each, with the four message lines verbatim.
  Consequences: a framework command's dispatch unchanged; an unknown name
  about 57 ms slower; `machinome -h` lists what is installed, so its output
  depends on the environment, and the help-fidelity tests pin the group
  empty; a contributor's module is imported by every `machinome -h`; no
  version is checked on a contributed command (ADR-162's pattern applies when
  one is needed); the three products register at their joins. References:
  `machinome/cli.py`, `tests/test_cli_contributed.py`,
  `tests/contributed_commands.py`, `tests/test_cli_lazy_imports.py`, the two
  specs.
- **ADR-024** and **ADR-168**: a dated "Amendment (2026-10-12)" section each,
  of one paragraph, and their status lines; the index lines of both in
  `docs/adrs/README.md` gain "amended by 189"; ADR-189's index line under
  BUILD after ADR-187's (after ADR-188's once the viewer's join is merged):

  ```
  - [ADR-189](BUILD/ADR-189-a-package-contributes-a-command-through-the-group-machinome-commands.md) — A package contributes a command through the group `machinome.commands`: `name = "package.module:Class"`, a class meeting the framework commands' contract (docstring, `add_arguments`, `handle`, `needs_node` declared); read only off the table's path, the command selected by position from the union; listed after the framework's by name; a framework name never taken, a name of two packages run by neither, an absent extra answered by it, an unmet contract refused, other failures propagated, each listed as unavailable by the help — **Accepted**, amends 024/168, cites 059/179/184
  ```

- **`docs/reference/cli.rst`**: a section before "Several models in one
  project":

  ```
  .. _contributed-commands:

  Commands from other packages
  ============================

  A package installed beside the framework may add a command of its own to
  ``machinome``. ``machinome -h`` lists it after the framework's commands,
  with its own help, and ``machinome <name> -h`` gives its options. A name
  of the framework's own commands always runs the framework's command. When
  two installed packages add the same name, neither runs, and ``machinome
  <name>`` names both; a command whose package lacks an extra, or cannot be
  loaded, is listed as unavailable with the reason. The videomaker
  (``machinome movie``), the skills package (``machinome skills``) and the
  studio (``machinome studio``) are to add theirs; no package adds one yet.
  ```

- **`docs/architecture.md`**: in "CLI", after the sentence ending "every
  command is listed with or without its extra.":

  ```
  An installed package may add a command through the entry-point group
  `machinome.commands`, `name = "package.module:Class"`, a class meeting the
  table's contract with `needs_node` declared (ADR-189). The command is the
  first argument that is not an option; the group is read only when that
  argument is not a framework command, so a framework command's dispatch
  reads no entry point, and the guard, the help and an unknown name's error
  read the union. A framework name is never taken; a name two packages
  declare runs neither; an absent extra is answered by it, an unmet contract
  refused, other failures propagate, and the help lists each as unavailable.
  ```

  "Top-level `-h` is the exception: it renders every command's docstring, so
  it loads them all." gains ", the contributed ones included". The Map's CLI
  row gains `168, 179, 189` in its ADR column (168 and 179 are missing from it
  today).
- **`HISTORY.rst`**, under `Unreleased`, after the last bullet at the bench's
  base (`join-mechanics`'s):

  ```
  * **Packages may add COMMANDS to ``machinome``.** An installed package
    declares a command in the entry-point group ``machinome.commands`` as
    ``name = "package.module:Class"``, its class a command like the
    framework's own: its docstring the help, ``add_arguments`` its options,
    ``handle`` its run, ``needs_node`` declared. ``machinome -h`` lists it
    after the framework's commands and ``machinome <name>`` runs it. A
    framework command's name is never taken, a name two packages declare
    runs neither, and a command that lacks an extra or cannot be loaded is
    listed as unavailable with the reason. Dispatching a framework command
    reads no entry point. No package declares one yet. Change
    ``commands-contributed-by-packages`` (ADR-189, ADR-024 and ADR-168
    amended).
  ```

- **`docs/project/changelog.rst`**, under `Unreleased`, after the mechanics
  bullet:

  ```
  * **Other packages can add commands to ``machinome``.** A package
    installed beside the framework may add a command of its own, listed by
    ``machinome -h`` after the framework's and run as ``machinome <name>``
    (:ref:`contributed-commands`). The framework's commands are unchanged
    and never replaced.
  ```

- **`machinome/cli.py`'s comments**: the `COMMANDS` comment gains one
  sentence naming the group and ADR-189; `manage()`'s selection comment is
  rewritten for the position rule.
- **`CONTRIBUTING.rst`** (the root's, linked from the package) says nothing of
  how a command is declared: unchanged. `framework-identity`'s "The command
  surface uses the framework identity" still holds (the framework's command
  set is unchanged): unchanged.

### 10. The spec deltas

- `cli`: ADDED "An installed package may contribute a command"; MODIFIED
  "Command-first grammar with migration guard" (the position rule and the
  union; scenario "Legacy grammar" kept, two added) and "A command that needs
  an extra is answered by the extra" (its last sentence; its three scenarios
  kept).
- `cli-startup-cost`: MODIFIED "A command loads only its own implementation"
  (no `importlib.metadata` at the CLI's import, no group read by a framework
  command, no framework module imported by a contributed one; its three
  scenarios kept, two added) and "Top-level help still describes every
  command" (the contributed commands; its two scenarios kept, the first's
  THEN extended).

## Risks / Trade-offs

- [`machinome -h` now depends on what is installed] → the help-fidelity tests
  pin the group empty (Decision 8, test 17), and test 1 proves the listing.
- [A contributor's slow module slows every `machinome -h`] → the contract
  says so; the help already costs about 0.8 s and is run by people, not
  automation. Not checked.
- [A contributed name beginning with `-` or holding spaces can never be
  selected] → entry names are written by package authors of the set; such a
  name is listed and unreachable, harmlessly. Not policed.
- [The core-name warning repeats on every help] → it names a misconfigured
  package, which is the point; it never changes stdout or the exit status.
- [The help path catches every exception a contributor raises at import] →
  only to list it; the dispatch of that name still propagates it.
- [The namespace-portion shape is proved by a fake only] → the videomaker's
  join proves it with `machinome.movie`.
- [Parallel records] → the viewer's join on another bench adds ADR-188 and
  bullets to the same `HISTORY.rst`, changelog and ADR index; the
  orchestrator's merge keeps both sides, as for `digest-only-what-the-node-names`.

## Migration Plan

Nothing migrates: no command, address, message or exit status of the
framework changes, and no contributor exists. Rollback is the revert of the
implementation commit. Each later join adds its entry to its own manifest
(`[project.entry-points."machinome.commands"]`) and its class to its package,
and the conformance walk (test 15) then holds it in the suite once the
workspace installs it.

## Open Questions

1. **The group's name.** `machinome.commands` names what each entry is and
   echoes `COMMANDS`; `machinome.cli` would name the module, and
   `machinome.subcommands` the argparse term. Recommendation:
   `machinome.commands`.
2. **Where the read sits.** Off the table's path, keyed on the first argument
   that is not an option (Decision 3); the alternative, on every invocation,
   costs every framework command about 56 ms and buys nothing the collision
   rule allows. Recommendation: off the table's path.
3. **The collision rule.** The framework's command always, with a warning;
   two packages, neither, with an error naming both. The alternative for two
   packages, the first on `sys.path`, makes the answer depend on install
   order. Recommendation: as Decision 6.
4. **The ADR's section.** BUILD holds the CLI's decisions (024, 059, 168,
   179); NODE holds the node packages'. Recommendation: BUILD.
5. **What the cost probe showed.** An unknown name's error goes from about
   55 to 112 ms and a contributed command pays about 56 ms over the CLI's
   import; the help and every framework command are unchanged within noise.
   Recommendation: accept; a cache of the group would be a second record of
   what is installed, to go stale.
6. **A contributor that cannot run, on the help path.** Listed as
   "(unavailable: <reason>)" so the user learns it exists and why it fails,
   or omitted with a warning on standard error. Recommendation: listed.
7. **The sentence of the cli spec and lean-core's D2.** The spec's "No
   entry-point group or plugin registry SHALL be consulted to find a command"
   and D2's "No entry-point group is introduced" were written for a command
   whose implementation moves with a node package the core names. This
   change keeps that for the table's commands and opens a group for a
   package's own. Recommendation: the pilot's decision of 12 October 2026
   governs, as ADR-179 left it to him; the orchestrator confirms with the
   pilot that the sentence's replacement is what he meant.
8. **The manual names three commands that do not exist yet.** The cli
   reference's section names `machinome movie`, `skills` and `studio` as "to
   add theirs" with "no package adds one yet". The alternative is to name
   none until the first join. Recommendation: name them, as the brief of this
   change asks, and let each join's change replace "are to add" for its own.
