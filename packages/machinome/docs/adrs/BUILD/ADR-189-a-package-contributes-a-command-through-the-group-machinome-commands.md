# ADR-189: A Package Contributes a Command Through the Group `machinome.commands`

**Status:** Accepted; its third contributor, `machinome studio`, amended 2026-10-12 by [ADR-193](ADR-193-the-studio-is-a-product-of-the-set-reached-by-machinome-studio.md)
**Date:** 2026-10-12
**Change:** [`commands-contributed-by-packages`](../../../openspec/changes/archive/2026-10-12-commands-contributed-by-packages/)
**Amends:**
- [ADR-024: Command-First CLI Grammar and Duck-Typed Command Registry](ADR-024-command-first-cli-grammar-and-duck-typed-command-registry.md): the registry has a second source, read only off the table's path, and the command is selected by its position
- [ADR-168: The command table names the module a command needs](ADR-168-the-command-table-names-the-module-a-command-needs.md): its "no entry-point group" holds for the table's commands, not for a package's own
**Related to:**
- [ADR-179: The core reaches a node package's renderer and command through the table of supported node types](ADR-179-the-core-reaches-a-node-packages-renderer-and-command-through-the-table-of-supported-node-types.md): its option 3, discovering commands from installed packages through entry points, left to the pilot's later decision, which this is
- [ADR-059: Import at the point of use](ADR-059-import-at-the-point-of-use.md): the group is read, and `importlib.metadata` imported, only where a contributed command can be meant
- [NODE/ADR-184: An absent node package is refused by its extra at its import](../NODE/ADR-184-an-absent-node-package-is-refused-by-its-extra-at-its-import.md): not needed here, since an entry exists only when its package is installed

## Context and Problem Statement

On 12 October 2026 the pilot decided: "I'd like to have one single machinome
cli with packages contributing subcommands." Three products of the set need
a subcommand of `machinome`: the videomaker, joining as the distribution
`machinome-movie`, as `machinome movie <verb>`; the skills package as
`machinome skills install|update|list`; the studio as `machinome studio`.
The framework's command knew only its own table, `machinome.cli.COMMANDS`,
and the `cli` spec said no entry-point group was consulted to find a
command. On the line's head at 484a528f, `machinome movie build film.yaml`
exited 2 with the 0.4 migration hint, because the guard read the verb
`build` as a framework command, and `machinome movie render film.yaml`,
`machinome skills install` and `machinome studio --port 9010` exited 2 with
"invalid choice" (design.md of the change, probe 1). The core does not ship,
import or name those products, and the skills package may never be a
member of the repository.

## Considered Options

1. **The entry-point group `machinome.commands`, each entry a class's
   location, read only off the table's path** (chosen)
2. A row per product in the core's table, as `import-step`'s node type is
   named: the core would name products it does not ship, and a package
   outside the repository could not add one
3. The entry naming a factory function rather than the class: a second
   shape beside the table's, for nothing the class does not do
4. Reading the group on every invocation: every framework command would pay
   the read, `vet -h` doubling, for a shadowing the collision rule forbids
5. Each product keeping its own script: the state the decision ends

## Decision Outcome

**The group.** An installed distribution declares a command in its manifest
as `[project.entry-points."machinome.commands"] name =
"package.module:Class"`. The entry's name is the command's; its value is the
location the table holds as a pair, and one construction serves both
(`instantiate(module, class_name)`). The framework's own distribution
declares no entry.

**The contract.** A contributed class meets what the table's ten meet: it is
constructed with no argument, and cheaply, since the help constructs every
command; its docstring, not empty, is its help; `add_arguments(parser)`
registers its options, positionals or verbs; `handle(args)` runs it, its exit
status set by `SystemExit`; and it declares `needs_node` as `True` or
`False`, the CLI giving a `True` one the shared `reference` positional,
`--set` and the refusal of a directory. The CLI does not assume `needs_node`
for a contributed class, as it does for the table's, so a contributor that
forgot it does not silently grow a positional. Its module should import
little at its scope, since every `machinome -h` imports it; that is stated,
not checked.

**When the group is read.** The command is the first argument that does not
begin with `-`. When it is a framework command, the group is not read, and
the dispatch imports what it imported before. The help, a contributed
command, an unknown name and the migration guard's path read the group once,
through a function that imports `importlib.metadata` in its body, so
importing `machinome.cli` does not import it.

**The grammar reads the union.** The guard (`argv[1]` not a command and
`argv[2]` one) and argparse's choices read the framework's names and the
contributed ones, so `machinome film.yaml movie` is answered with the hint as
`machinome mynode.py develop` is. A later argument that spells a command, a
contributed command's verb `build` or a movie named `test`, is that command's
argument: no framework invocation changes its answer, since an argument
before the first framework name that is not an option was already argparse's
invalid choice or the guard's.

**The listing.** `machinome -h` lists the table's commands in its order, then
the contributed commands in the order of their names, whatever order their
distributions were installed in; an unknown name's error names the same
commands.

**Collisions.** A contributed name equal to a framework command's is not used:
the framework's command runs, and each read of the group writes, per such
entry,

```
Warning: <distribution> contributes the command <name> (<value>), which is machinome's own; it is not used
```

on standard error, the help's standard output and exit status unchanged. A
name two or more distributions contribute runs none of them; invoking it
imports none of their modules, writes

```
Error: machinome <name> is contributed by more than one package: <dist> (<value>), <dist> (<value>)
```

and exits 1, the distributions in the order of their names. A distribution
found twice on the path counts once, as the standard library already reports
it.

**A contributed command that cannot run.** Its module refusing for an absent
extra (`machinome.extras.ExtraUnavailable`) is answered as
`require_needed_module` answers `import-step`, before its arguments are
parsed:

```
Error: machinome <name> needs the <extra> extra: <refusal>
```

A class that does not meet the contract is refused before its arguments are
parsed, naming the first unmet term of "no docstring", "no add_arguments()",
"no handle()" and "needs_node is not declared as True or False":

```
Error: machinome <name>: <distribution> (<value>) does not meet the command contract: <term>
```

Any other failure to import or construct it propagates, naming what could
not be loaded. On the help path each of these, and the name of two
distributions, is listed with the help `(unavailable: <reason>)`, the reason
naming the refusal, the unmet term, or `<ExceptionType>: <message>` for
anything raised while importing or constructing it, and the help exits 0:
one broken package does not take `machinome -h` from the users of every
other command.

### Measurements

Measured on the bench on 12 October 2026, the page cache warm, the base's
`cli.py` and the change's run alternately in the same loop (the change's
`evidence.md`, task 5.2):

- `machinome -h` is about 70 ms slower: 807 against 874 ms over thirty
  alternating runs, 918 against 991 ms and, with one contributor installed,
  822 against 885 ms over twenty. The help path imports the same 1023
  modules and prints the same output; the group's first read, measured
  in-process after every command module is imported, costs 25 to 31 ms,
  and the rest is not explained by these measurements.
- A framework command is unchanged within noise: `machinome vet -h` 56
  against 58 ms, and 58 against 58 ms with a contributor installed;
  `machinome build -h` 231 against 244 ms, and 254 against 251 ms.
- An unknown name's error is about 67 ms slower: `machinome frobnicate` 47
  against 114 ms.
- A contributed command: `machinome movie build film.yaml` with the fake
  movie installed runs in 112 ms, where the base answered with the migration
  hint in 41 ms.

### Consequences

- Good: a package adds a command to `machinome` by declaring it, with no edit
  to the framework; the three products register at their joins.
- Good: a framework command's dispatch reads no entry point and imports what
  it imported before.
- Good: no answer depends on install order.
- Bad: an unknown name's error is about 67 ms slower, and `machinome -h`
  about 70 ms slower, of which the group's read accounts for 25 to 31 ms.
- Bad: `machinome -h` lists what is installed, so its output depends on the
  environment; the help-fidelity tests read the group empty to keep their
  oracle the framework's.
- Bad: every `machinome -h` imports every contributor's module.
- Neutral: no version is checked on a contributed command; ADR-162's pattern
  applies when one is needed.
- Neutral (2026-10-12, `join-studio`): `machinome studio` is the group's
  third contributor, after `machinome movie` and `machinome skills`; its
  module imports the standard library alone (ADR-193).

## References

- `machinome/cli.py` (`COMMAND_GROUP`, `instantiate`, `contributed_commands`,
  `resolve_contributed`, `list_contributed`, `manage`)
- `tests/test_cli_contributed.py`, `tests/contributed_commands.py`,
  `tests/test_cli_lazy_imports.py`
- `openspec/specs/cli/spec.md` ("An installed package may contribute a
  command", "Command-first grammar with migration guard", "A command that
  needs an extra is answered by the extra"), `openspec/specs/cli-startup-cost/spec.md`
