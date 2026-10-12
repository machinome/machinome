# Machinome Skills - The machinome skills for assistants that read Agent Skills
# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Copy the shipped skills into the directories assistants read them from.

The verbs of `machinome skills` (change `join-skills`, capability
`skills-distribution`): `install`, `update` and `listing`, each taking the
parsed arguments and returning the exit status. They read the registry
`tools.toml` and the skills under `agent-skills/` as the package's data,
from the source directory on an editable install and from `site-packages`
on a wheel's.

A copy is the shipped skill directory whole, its `SKILL.md` carrying a
marker: a `metadata` mapping added at the end of its frontmatter,
`installed-by: machinome-skills` and the installed package's `version`. A
target whose `SKILL.md` carries no marker is not this command's and is never
written without `--force`; a file the package does not ship is never
touched; nothing is ever deleted. The marker is written and read as text,
as OpenSpec reads its own, with the standard library alone.
"""

import os
import re
import sys
import tomllib
from importlib import metadata, resources
from pathlib import Path

#: The distribution whose version marks a copy.
DISTRIBUTION = 'machinome-skills'

#: The package whose data is the registry and the skills.
PACKAGE = 'machinome.skills'

FRONTMATTER = re.compile(r'\A---\n(.*?\n)---\n', re.S)
METADATA = re.compile(r'^metadata:[ \t]*\n((?:[ \t]+\S.*\n)*)', re.M)
INSTALLED_BY = re.compile(
    rf'^[ \t]+installed-by:[ \t]*(["\']?){re.escape(DISTRIBUTION)}\1[ \t]*$',
    re.M)
VERSION = re.compile(r'^[ \t]+version:[ \t]*(["\']?)([^"\'\s]*)\1[ \t]*$',
                     re.M)

PROMPT = ('Tools (Enter for the marked ones; numbers or ids separated by '
          'commas; all; none): ')


class UsageError(ValueError):
    """A value of `--tools` the command does not accept: its message names
    the valid values."""


def registry():
    """The tools, in the registry's order: each a mapping of `id`, `name`,
    `detect`, `project`, `personal` (absent where the tool documents none)
    and `source`."""
    data = resources.files(PACKAGE).joinpath('tools.toml').read_bytes()
    return tomllib.loads(data.decode('utf-8'))['tool']


def version():
    """The installed package's version, which marks every copy."""
    return metadata.version(DISTRIBUTION)


def shipped():
    """Each shipped skill by name: its files by relative path, as bytes."""
    skills = {}
    root = resources.files(PACKAGE) / 'agent-skills'
    for skill in sorted(root.iterdir(), key=lambda entry: entry.name):
        if not skill.is_dir():
            continue
        found = {}
        pending = [(skill, '')]
        while pending:
            directory, prefix = pending.pop()
            for entry in directory.iterdir():
                if entry.is_dir():
                    if entry.name != '__pycache__':
                        pending.append((entry, f'{prefix}{entry.name}/'))
                elif entry.is_file():
                    found[f'{prefix}{entry.name}'] = entry.read_bytes()
        skills[skill.name] = dict(sorted(found.items()))
    return skills


def marked(text, number):
    """A shipped `SKILL.md` with the marker of version `number` added at the
    end of its frontmatter."""
    frontmatter = FRONTMATTER.match(text)
    if frontmatter is None:
        raise ValueError('a shipped SKILL.md has no frontmatter')
    body = (f'{frontmatter.group(1)}metadata:\n'
            f'  installed-by: {DISTRIBUTION}\n'
            f'  version: "{number}"\n')
    return f'---\n{body}---\n{text[frontmatter.end():]}'


def marker(target):
    """The version the marker of the copy at `target` names, `''` when it
    names none, or None when `target` is not this command's copy."""
    try:
        text = (Path(target) / 'SKILL.md').read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        return None
    frontmatter = FRONTMATTER.match(text)
    if frontmatter is None:
        return None
    mapping = METADATA.search(frontmatter.group(1))
    if mapping is None or not INSTALLED_BY.search(mapping.group(1)):
        return None
    found = VERSION.search(mapping.group(1))
    return found.group(2) if found else ''


def numbers(text):
    """A version as a tuple of integers, or None when it is not numeric."""
    try:
        return tuple(int(part) for part in text.split('.'))
    except ValueError:
        return None


def compared(old, new):
    """`current`, `older` or `newer`: a copy's version against the
    installed one; a version that is not numeric reads as newer, so it is
    never rewritten unasked."""
    if old == new:
        return 'current'
    if numbers(old) is not None and numbers(new) is not None \
            and numbers(old) < numbers(new):
        return 'older'
    return 'newer'


def valid_values(tools):
    return ('use all, none or ids from: '
            + ', '.join(tool['id'] for tool in tools))


def parse_tools(value, tools=None):
    """The ids `value` names, as `--tools` reads it: `all`, `none`, or ids
    separated by commas, case-folded and deduplicated in order."""
    tools = registry() if tools is None else tools
    known = [tool['id'] for tool in tools]
    words = [word.strip().lower() for word in value.split(',')]
    words = [word for word in words if word]
    if not words:
        raise UsageError(f'no tool named; {valid_values(tools)}')
    if words == ['all']:
        return known
    if words == ['none']:
        return []
    if 'all' in words or 'none' in words:
        raise UsageError(f'all and none stand alone; {valid_values(tools)}')
    unknown = [word for word in dict.fromkeys(words) if word not in known]
    if unknown:
        named = ', '.join(repr(word) for word in unknown)
        plural = 's' if len(unknown) > 1 else ''
        raise UsageError(f'unknown tool{plural} {named}; '
                         f'{valid_values(tools)}')
    return list(dict.fromkeys(words))


def directory_of(tool, path, personal):
    """The skills directory of `tool`: under `path`, or under the user's
    home."""
    if personal:
        return Path(tool['personal']).expanduser()
    return Path(path) / tool['project']


def directories(tools, ids, path, personal):
    """Each distinct skills directory of the tools `ids`, in their order,
    with the ids it serves."""
    by_id = {tool['id']: tool for tool in tools}
    found = {}
    for name in ids:
        found.setdefault(directory_of(by_id[name], path, personal),
                         []).append(name)
    return found


def detected(tools, path):
    """The tools whose detection paths exist under `path`."""
    return [tool['id'] for tool in tools
            if any((Path(path) / entry).exists() for entry in tool['detect'])]


def preselected(tools, path, personal, skills):
    """The tools a prompt marks: those whose directories hold a copy of
    this command's, else those detected under `path`, else `agents`."""
    holding = []
    for tool in tools:
        if personal and 'personal' not in tool:
            continue
        directory = directory_of(tool, path, personal)
        if any(marker(directory / skill) is not None for skill in skills):
            holding.append(tool['id'])
    if holding:
        return holding
    if Path(path).is_dir():
        found = detected(tools, path)
        if found:
            return found
    return ['agents']


def interactive():
    """Whether a prompt can be answered: standard input is a terminal and
    `CI` is not set, OpenSpec's rule."""
    try:
        terminal = sys.stdin.isatty()
    except (AttributeError, ValueError):
        terminal = False
    return terminal and 'CI' not in os.environ


def ask(tools, marked_ids, where):
    """The tools chosen at the prompt, or None when standard input ends."""
    print(f'Tools to install the machinome skills for, into {where} '
          '(* marked):')
    for number, tool in enumerate(tools, 1):
        mark = '*' if tool['id'] in marked_ids else ' '
        print(f" {mark} {number:2} {tool['id']:<15} {tool['project']:<19} "
              f"{tool['name']}")
    known = [tool['id'] for tool in tools]
    while True:
        try:
            answer = input(PROMPT).strip()
        except EOFError:
            print()
            return None
        if not answer:
            return list(marked_ids)
        words = []
        try:
            for word in answer.split(','):
                word = word.strip()
                if word.isdigit():
                    if not 1 <= int(word) <= len(known):
                        raise UsageError(
                            f'no tool numbered {word}; '
                            f'{valid_values(tools)}, or numbers from 1 to '
                            f'{len(known)}')
                    word = known[int(word) - 1]
                words.append(word)
            return parse_tools(','.join(words), tools)
        except UsageError as error:
            print(f'Not understood: {error}')


def write_copy(target, files, number):
    """Write the skill's `files` into `target`, the marker in its
    `SKILL.md`, printing each path; nothing else under `target` is
    touched."""
    for relative, data in files.items():
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if relative == 'SKILL.md':
            data = marked(data.decode('utf-8'), number).encode('utf-8')
        destination.write_bytes(data)
        print(f'  wrote {destination}')


def not_a_directory(path):
    print(f'Error: {path} is not a directory', file=sys.stderr)
    return 1


def install(args):
    """`machinome skills install [path] [--tools ...] [--personal]
    [--force]`."""
    path = Path(args.path)
    if not args.personal and not path.is_dir():
        return not_a_directory(path)
    tools = registry()
    skills = shipped()
    if args.tools is not None:
        ids = parse_tools(args.tools, tools)
        if not ids:
            print('Nothing installed: --tools none')
            return 0
    elif interactive():
        where = 'your home' if args.personal else str(path)
        ids = ask(tools, preselected(tools, path, args.personal, skills),
                  where)
        if ids is None:
            print('Error: no answer; nothing was written', file=sys.stderr)
            return 1
        if not ids:
            print('Nothing installed: none chosen')
            return 0
    else:
        print('No --tools given and no terminal to ask: installing for '
              'agents (.agents/skills/); name others with --tools')
        ids = ['agents']

    by_id = {tool['id']: tool for tool in tools}
    if args.personal:
        absent = [name for name in ids if 'personal' not in by_id[name]]
        for name in absent:
            print(f'Error: {name} documents no personal skills directory; '
                  'install it into a project: machinome skills install '
                  f'--tools {name} <project>', file=sys.stderr)
        if absent:
            return 1

    targets = directories(tools, ids, path, args.personal)
    blocked = []
    refused = {}
    for directory, served in targets.items():
        for skill in skills:
            target = directory / skill
            if target.exists() and not target.is_dir():
                blocked.append(target)
            elif target.exists() and marker(target) is None \
                    and not args.force:
                refused.setdefault(directory, []).append(target)
    for target in blocked:
        print(f'Error: {target} is not a directory; nothing was written',
              file=sys.stderr)
    for directory, refusals in refused.items():
        for target in refusals:
            print(f'Error: {target} holds a skill machinome skills did not '
                  'write; nothing was written', file=sys.stderr)
    if refused:
        served = list(dict.fromkeys(
            name for directory in refused for name in targets[directory]))
        where = '--personal' if args.personal else str(args.path)
        print('To replace it, run: machinome skills install --tools '
              f"{','.join(served)} --force {where}", file=sys.stderr)
    if blocked or refused:
        return 1

    number = version()
    for directory, served in targets.items():
        print(f"{directory}/ ({', '.join(served)})")
        for skill, files in skills.items():
            target = directory / skill
            old = marker(target) if target.exists() else None
            replaced = target.exists() and old is None
            write_copy(target, files, number)
            if old is not None:
                print(f'  {target}: {old or "unversioned"} -> {number}')
            elif replaced:
                print(f'  {target}: replaced a skill machinome skills did '
                      'not write (--force)')
    return 0


def every_directory(tools, path, personal):
    """Each distinct skills directory of the registry, under `path` or the
    home, with the ids it serves."""
    ids = [tool['id'] for tool in tools
           if not personal or 'personal' in tool]
    return directories(tools, ids, path, personal)


def update(args):
    """`machinome skills update [path] [--personal] [--force]`."""
    path = Path(args.path)
    if not args.personal and not path.is_dir():
        return not_a_directory(path)
    tools = registry()
    skills = shipped()
    number = version()
    found = False
    for directory in every_directory(tools, path, args.personal):
        for skill, files in skills.items():
            target = directory / skill
            if not target.exists():
                continue
            found = True
            old = marker(target)
            if old is None:
                print(f'{target}: not written by machinome skills, left as '
                      'it is')
                continue
            state = compared(old, number)
            if not args.force and state == 'current':
                print(f'{target}: {old}, current')
                continue
            if not args.force and state == 'newer':
                print(f'{target}: {old or "unversioned"}, newer than '
                      f'{number}, left as it is')
                continue
            write_copy(target, files, number)
            print(f'{target}: {old or "unversioned"} -> {number}')
    if not found:
        where = 'in your home' if args.personal else f'under {path}'
        print(f'No copy of the machinome skills {where}; install them with: '
              'machinome skills install')
    return 0


def listing(args):
    """`machinome skills list [path] [--personal]`."""
    path = Path(args.path)
    if not args.personal and not path.is_dir():
        return not_a_directory(path)
    tools = registry()
    for tool in tools:
        print(f"{tool['id']:<15} {tool['project']:<19} "
              f"{tool.get('personal', '-'):<26} {tool['name']}")
    print()
    print('Installed in your home:' if args.personal
          else f'Installed under {path}:')
    number = version()
    found = False
    for directory, served in every_directory(tools, path,
                                             args.personal).items():
        for skill in shipped():
            target = directory / skill
            if not target.exists():
                continue
            found = True
            old = marker(target)
            if old is None:
                state = 'not written by machinome skills'
            else:
                comparison = compared(old, number)
                state = (f'{old or "unversioned"}, '
                         + ('current' if comparison == 'current'
                            else f'{comparison} than {number}'))
            print(f"  {target} ({', '.join(served)}): {state}")
    if not found:
        print('  none')
    return 0
