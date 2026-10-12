# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

import argparse
import os
import sys
from importlib import import_module

#: Command name -> the module and class that implement it, and the one module
#: of the framework it needs beyond them (or None), in the order
#: `machinome -h` lists them.
#:
#: The table holds locations rather than instances because almost nothing
#: the CLI does needs a command object. The migration guard, the subparser
#: names, and argparse's invalid-choice report all work from names alone,
#: and every one of them used to cost seven module imports -- including
#: `cadquery`, reached through the node package. `manage()` now imports the
#: one command it is about to run.
#:
#: Naming the class in a string is what makes that possible, and it is also
#: the one risk: a rename or a move fails when that command is invoked
#: rather than when the CLI loads. tests/test_cli_lazy_imports.py walks the
#: whole table once so the failure lands in the suite instead.
#:
#: The third column names the node type a command cannot run without, whose
#: kernel is an extra: `import-step` reads with the `step` node type's module,
#: which the `step` extra installs. The node type is the table of supported
#: node types' (`machinome.node.supported`, its `commands`), which names its
#: module. Dispatching the command imports that module first, and where it
#: refuses because its kernel is absent the CLI answers the command with the
#: extra the refusal names -- stated once, by the module that needs it, never
#: copied here -- instead of a traceback or an unknown command. The help path
#: imports no such module, so every command is listed whether or not its
#: extra is installed (OpenSpec change `lean-install`; ADR-168, ADR-179).
#:
#: A package installed beside the framework adds a command of its own
#: through the entry-point group `COMMAND_GROUP`, read only when the command
#: is not one of this table's (OpenSpec change
#: `commands-contributed-by-packages`; ADR-189).
COMMANDS = {
    'build': ('machinome.manager.build', 'Build', None),
    'develop': ('machinome.manager.develop', 'Develop', None),
    'test': ('machinome.manager.test', 'Test', None),
    'snapshot': ('machinome.manager.snapshot', 'Snapshot', None),
    'new': ('machinome.manager.new', 'New', None),
    'export': ('machinome.manager.export', 'Export', None),
    'viewer': ('machinome.manager.viewer', 'Viewer', None),
    'models': ('machinome.manager.models', 'Models', None),
    'import-step': ('machinome.manager.import_step', 'ImportStep', 'step'),
    'vet': ('machinome.manager.vet', 'Vet', None),
}

#: The tokens that make the top-level parser print its own help. That is the
#: one output that depends on every command, so it is the one path allowed
#: to load them all.
HELP_FLAGS = ('-h', '--help')

#: The entry-point group through which an installed distribution contributes
#: a command: `name = "package.module:Class"`, the class meeting the
#: contract the table's classes meet, with `needs_node` declared.
COMMAND_GROUP = 'machinome.commands'


def load_dotenv():
    """Load KEY=value lines from ./.env into os.environ.

    Real environment variables take precedence. This is how worktrees
    created by scripts/dev-env get their own ports (MACHINOME_PORT,
    MACHINOME_FRONTEND_PORT).
    """
    legacy = sorted(key for key in os.environ if key.startswith('SOLID_NODE_'))
    if legacy:
        raise SystemExit(
            f"Machinome 0.7 renamed {legacy[0]} to "
            f"{legacy[0].replace('SOLID_NODE_', 'MACHINOME_', 1)}")
    if not os.path.isfile('.env'):
        return
    with open('.env') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            if key.strip().startswith('SOLID_NODE_'):
                replacement = key.strip().replace(
                    'SOLID_NODE_', 'MACHINOME_', 1)
                raise SystemExit(
                    f"Machinome 0.7 renamed {key.strip()} to {replacement}")
            os.environ.setdefault(key.strip(), value.strip())


def instantiate(module, class_name):
    """Import `module` and return an instance of its class `class_name`: the
    one construction of a command, the table's and a contributed one alike.
    """
    return getattr(import_module(module), class_name)()


def resolve_command(name):
    """Import a command's module and return an instance of its class.

    A failing import is left to propagate: a broken installation should say
    which module it could not load, not disappear into a missing command.
    """
    module, class_name, _ = COMMANDS[name]
    return instantiate(module, class_name)


def contributed_commands():
    """The commands installed packages contribute: name -> its entries of
    `COMMAND_GROUP`, in the order of the names.

    `importlib.metadata` is imported here, never at the CLI's import, and
    this is called only when the command is not one of `COMMANDS`, so a
    framework command reads no entry point. An entry taking a name of
    `COMMANDS` is dropped with one warning line; a name with more than one
    entry is kept with all of them, for `resolve_contributed` to refuse. The
    standard library already counts a distribution found twice on the path
    once.
    """
    from importlib.metadata import entry_points

    found = {}
    for entry in sorted(entry_points(group=COMMAND_GROUP),
                        key=lambda entry: (entry.name, entry.dist.name,
                                           entry.value)):
        if entry.name in COMMANDS:
            sys.stderr.write(
                f"Warning: {entry.dist.name} contributes the command "
                f"{entry.name} ({entry.value}), which is machinome's own; "
                f"it is not used\n")
            continue
        found.setdefault(entry.name, []).append(entry)
    return found


def located(entry):
    """A contributed entry as its messages name it: its distribution and
    its location."""
    return f'{entry.dist.name} ({entry.value})'


def unmet_term(command):
    """The first term of the command contract `command` does not meet, or
    None. The construction with no argument is not checked here: a
    constructor that needs one has already raised."""
    if not (command.__doc__ or '').strip():
        return 'no docstring'
    if not callable(getattr(command, 'add_arguments', None)):
        return 'no add_arguments()'
    if not callable(getattr(command, 'handle', None)):
        return 'no handle()'
    if not isinstance(getattr(command, 'needs_node', None), bool):
        return 'needs_node is not declared as True or False'
    return None


class CommandUnavailable(Exception):
    """A contributed command that cannot run: `str()` is the line its
    invocation writes, `reason` the help it is listed with."""

    def __init__(self, message, reason):
        super().__init__(message)
        self.reason = reason


def resolve_contributed(name, entries):
    """An instance of the class a package contributes as `name`.

    A name two packages contribute, a module refusing for an absent extra
    and a class not meeting the contract raise `CommandUnavailable`; any
    other failure to import or construct it propagates, as
    `resolve_command` lets a broken installation's.
    """
    if len(entries) > 1:
        both = ', '.join(located(entry) for entry in entries)
        raise CommandUnavailable(
            f'Error: machinome {name} is contributed by more than one '
            f'package: {both}',
            f'contributed by more than one package: {both}')
    entry, = entries
    from machinome.extras import ExtraUnavailable
    try:
        command = instantiate(entry.module, entry.attr)
    except ExtraUnavailable as absent:
        raise CommandUnavailable(
            f'Error: machinome {name} needs the {absent.extra} extra: '
            f'{absent}',
            f'needs the {absent.extra} extra: {absent}') from None
    unmet = unmet_term(command)
    if unmet is not None:
        reason = (f'{located(entry)} does not meet the command contract: '
                  f'{unmet}')
        raise CommandUnavailable(f'Error: machinome {name}: {reason}', reason)
    return command


class Unlisted:
    """A contributed command the help lists as unavailable, its help the
    reason."""

    def __init__(self, reason):
        self.__doc__ = f'(unavailable: {reason})'


def list_contributed(name, entries):
    """`resolve_contributed` for the help: a command that cannot run is
    listed with its reason, whatever it raised, so one broken package never
    takes `machinome -h` from the users of every other command."""
    try:
        return resolve_contributed(name, entries)
    except CommandUnavailable as unavailable:
        return Unlisted(unavailable.reason)
    except Exception as failure:
        return Unlisted(f'{located(entries[0])} cannot be loaded: '
                        f'{type(failure).__name__}: {failure}')


def require_needed_module(name):
    """Import the module of the node type command `name` needs, through the
    table of supported node types, or answer the command by the extra that
    installs it.

    A refusal for an absent kernel (`ExtraUnavailable`) is written as one
    line naming the command and the extra, and the CLI exits 1 before the
    command parses or runs. Any other import error propagates, as
    `resolve_command` requires of a broken installation.
    """
    needs = COMMANDS[name][2]
    if needs is None:
        return
    from machinome.extras import ExtraUnavailable
    from machinome.node import supported
    try:
        supported.load(needs)
    except ExtraUnavailable as absent:
        sys.stderr.write(f'Error: machinome {name} needs the {absent.extra} '
                         f'extra: {absent}\n')
        sys.exit(1)


def add_command_parser(subparsers, name, command):
    """Register `command` under `name` with its help, options and, when it
    operates on a node, the shared `reference` positional."""
    command_parser = subparsers.add_parser(
        name,
        help=command.__doc__,
    )
    if getattr(command, 'needs_node', True):
        command_parser.add_argument(
            'path', nargs='?',
            type=str,
            metavar='reference',
            help='Node reference: a declared model name, package.module:Class, path/to/file.py, or path/to/file.py:Class',
        )
        # Registered once, here, beside the reference it applies to: every
        # command that loads a node takes the root's parameters the same
        # way, and none re-declares the flag.
        command_parser.add_argument(
            '--set', action='append', default=[], metavar='NAME=VALUE',
            help='Set a declared parameter of the root node, parsed by its '
                 'kind (repeatable)',
        )
    command.add_arguments(command_parser)
    return command_parser


def manage():
    """
    Runs cli commands, available in managers.* namespace
    """
    load_dotenv()

    # The command is the first argument that is not an option: no top-level
    # option takes a value, so no earlier argument is an option's value, and
    # a `--` before the command is skipped as argparse skips it. A later
    # argument spelling a command -- a contributed command's verb `build` --
    # is that command's argument, never a command (ADR-189).
    first = next((arg for arg in sys.argv[1:] if not arg.startswith('-')),
                 None)
    # A framework command never reads the group of contributed commands, so
    # its dispatch imports what it did before packages could contribute one;
    # the help, a contributed command, an unknown name and the guard do.
    contributed = {} if first in COMMANDS else contributed_commands()
    names = [*COMMANDS, *contributed]

    # Old grammar was `machinome <path> <command>`. If it looks like someone is
    # still using that order, fail fast with a clear hint instead of
    # silently misinterpreting the path as a command name.
    if len(sys.argv) > 2 and sys.argv[1] not in names and sys.argv[2] in names:
        sys.stderr.write(
            "The CLI grammar changed in 0.4: commands come first. "
            "Try: machinome {command} {path} [options]\n"
        )
        sys.exit(2)

    parser = argparse.ArgumentParser(description='Machinome')

    subparsers = parser.add_subparsers(
        dest='command',

        title='Commands',
        description='Pick an action to do on Node',
        help='use -h {command} for more options',
    )

    if first in COMMANDS:
        require_needed_module(first)
        resolved = {first: resolve_command(first)}
    elif first in contributed:
        try:
            resolved = {first: resolve_contributed(first, contributed[first])}
        except CommandUnavailable as unavailable:
            sys.stderr.write(f'{unavailable}\n')
            sys.exit(1)
    elif len(sys.argv) == 1 or sys.argv[1] in HELP_FLAGS:
        # Each command's help is its docstring, and only the class carries
        # it. `machinome -h` therefore costs what it always cost; nothing
        # automated runs it, and duplicating seven docstrings into the table
        # to avoid that would only invite them to drift. The contributed
        # commands follow the table's, in the order of their names.
        resolved = {name: resolve_command(name) for name in COMMANDS}
        resolved.update({name: list_contributed(name, entries)
                         for name, entries in contributed.items()})
    else:
        # An unknown command. argparse reports it against the registered
        # names, which is the same error as before with nothing loaded.
        resolved = {}

    for name in names:
        command = resolved.get(name)
        if isinstance(command, Unlisted):
            subparsers.add_parser(name, help=command.__doc__)
        elif command is None:
            # A name for argparse to match and to list; the options behind
            # it belong to an invocation that is not happening.
            subparsers.add_parser(name)
        else:
            add_command_parser(subparsers, name, command)

    args = parser.parse_args()

    if args.command is None:
        return parser.print_help()

    command = resolved[args.command]

    if getattr(command, 'needs_node', True) and args.path and os.path.isdir(args.path):
        parser.error('A directory is not a node reference; use a declared model name, package.module:Class, path/to/file.py, or path/to/file.py:Class')

    command.handle(args)
