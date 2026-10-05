#!/usr/bin/env python3
# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""Repoint the framework's own files from the node root to the modules
(design.md, Decision 8): the applier's method for task group 4.

    python3 repoint.py <checkout>            # dry run: the plan, nothing written
    python3 repoint.py <checkout> --apply    # write it
    python3 repoint.py <checkout> --diff     # dry run with a unified diff

The mapping is this change's `moved-names.toml`, the twenty-one rows of the
workspace's `scripts/rewrite-projects.d/root-cleanup.toml` root block, name
for name. The workspace tool itself is not the method: it walks the project
catalogue and skips a linked worktree (this bench is one), it applies every
cycle's table at once (which would rewrite the suite's deliberate spellings
of earlier cycles' former names, `machinome.exact_engine` in the refusal
tests among them), and it rewrites import statements only, where 81 of the
suite's offences are fixture sources inside strings.

The zones and the reading are the gate's (`gate-prototype.py`): every text
file under `machinome/`, `tests/`, `docs/` (without `docs/adrs/`, `_build/`,
`_exports/`) and `README.rst`, read as text, so a fixture project in a
string is repointed like code. Three rules:

- A `from machinome.node import ...` statement whose names include one of
  the twenty-one, all of which the mapping sends to ONE module: the address
  `machinome.node` in it becomes that module's, in place. Format, aliases,
  parentheses and trailing comments are kept.
- Such a statement whose names go to SEVERAL modules (a submodule name such
  as `phase` stays with `machinome.node`) and which begins its physical line
  (code, a triple-quoted fixture, a page's code block): it becomes one
  statement per module, in order of first appearance, at the same
  indentation, each carrying the statement's trailing comment, a line
  longer than 79 columns written as a parenthesised list. Elsewhere (inside
  a one-line string, an f-string, prose) it is listed for a hand edit.
- A dotted address `machinome.node.<name>` of the twenty-one becomes
  `machinome.node.<module>.<name>` (`.. autoclass::`, `patch(...)`).

The files the design revises by hand (HAND) are never touched, and the star
import is always listed, never rewritten. The plan's counts are printed per
zone; the listed sites are the hand edits task 4.3 makes.
"""

import difflib
import re
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent

#: Revised by hand (design.md, Decision 8): the root itself, the dissolved
#: package's docstring, the generator that composes its import lines from
#: the classes, the root's own test, and the two records a reader is sent to.
HAND = frozenset((
    'machinome/node/__init__.py',
    'machinome/node/adapters/__init__.py',
    'machinome/manager/import_step.py',
    'tests/test_node_lazy_exports.py',
    'docs/project/changelog.rst',
    'docs/project/upgrading.rst',
))

LINE_LENGTH = 79
SKIPPED_PARTS = {'__pycache__', '.pytest_cache', '_build', '_exports'}

#: One imported item: a name with an optional alias, or the star.
ITEM = r'(?:[A-Za-z_]\w*(?:[ \t]+as[ \t]+[A-Za-z_]\w*)?|\*)'

#: A statement: a parenthesised list, or items separated by commas (a
#: backslash continuation allowed), then an optional trailing comment. What
#: follows the last item -- a closing quote, a semicolon, prose -- is not
#: part of the statement.
IMPORT = re.compile(
    r'from(?P<gap>\s+)machinome\.node(?P<rest>\s+import\s+)'
    r'(?P<clause>\([^)]*\)|' + ITEM
    + r'(?:[ \t]*,[ \t]*(?:\\\n[ \t]*)?' + ITEM + r')*)'
    r'(?P<comment>[ \t]+#[^\n]*)?')


def mapping():
    with open(HERE / 'moved-names.toml', 'rb') as stream:
        rows = tomllib.load(stream)['moved']
    former = {}
    for row in rows:
        name = row['name'].rpartition('.')[2]
        module = row['to'].rpartition('.')[0]
        former[name] = module
    return former


FORMER = mapping()
#: The gate's loose reading of a statement, used to list what is left.
LOOSE = re.compile(r'from\s+machinome\.node\s+import\s+([^\n]*)')
DOTTED = re.compile(
    r'\bmachinome\.node\.(' + '|'.join(sorted(FORMER, key=len, reverse=True))
    + r')\b')


def parts_of(clause):
    """`(items, comment)`: each imported item's text (`Name` or `Name as
    alias`) and the clause's trailing comment, if any."""
    text = clause.strip()
    comment = ''
    if text.startswith('('):
        inner = text[1:].rsplit(')', 1)
        text, tail = inner[0], (inner[1] if len(inner) > 1 else '')
        found = re.search(r'#.*$', tail)
        comment = found.group(0) if found else ''
        notes = re.findall(r'#[^\n]*', text)
        if notes and not comment:
            comment = notes[-1]
        text = re.sub(r'#[^\n]*', '', text)
    else:
        found = re.search(r'\s#.*$', text)
        if found:
            comment = found.group(0).strip()
            text = text[:found.start()]
    text = text.replace('\\\n', ' ')
    items = [' '.join(part.split()) for part in text.split(',')]
    return [item for item in items if item], comment


def module_of(item):
    name = item.split(' as ')[0].strip()
    return FORMER.get(name, 'machinome.node'), name


def statement_lines(indent, module, items, comment):
    tail = f'  {comment}' if comment else ''
    line = f'{indent}from {module} import {", ".join(items)}{tail}'
    if len(line) <= LINE_LENGTH:
        return [line]
    body = [f'{indent}    {item},' for item in items]
    return [f'{indent}from {module} import ({tail}', *body, f'{indent})']


def rewrite(text, relative):
    """`(new text, counts, listed)` for one file."""
    counts = {'in place': 0, 'split': 0, 'dotted': 0}
    listed = []
    pieces = []
    last = 0
    for match in IMPORT.finditer(text):
        items, comment = parts_of(match.group('clause'))
        if match.group('comment'):
            comment = match.group('comment').strip()
        modules = [module_of(item) for item in items]
        if not any(name in FORMER or name == '*' for _, name in modules):
            continue
        line = text.count('\n', 0, match.start()) + 1
        if any(name == '*' for _, name in modules):
            listed.append((line, 'star import'))
            continue
        groups = {}
        for item, (module, _) in zip(items, modules):
            groups.setdefault(module, []).append(item)
        if len(groups) == 1:
            (module,) = groups
            replacement = (f'from{match.group("gap")}{module}'
                           f'{match.group("rest")}{match.group("clause")}'
                           f'{match.group("comment") or ""}')
            counts['in place'] += 1
        else:
            start = text.rfind('\n', 0, match.start()) + 1
            indent = text[start:match.start()]
            if indent.strip():
                listed.append((line, 'several modules, not at a line start'))
                continue
            lines = []
            for module, group in groups.items():
                lines.extend(statement_lines(indent, module, group, comment))
            replacement = '\n'.join(lines)[len(indent):]
            counts['split'] += 1
        pieces.append(text[last:match.start()])
        pieces.append(replacement)
        last = match.end()
    pieces.append(text[last:])
    new = ''.join(pieces)

    def dotted(found):
        counts['dotted'] += 1
        return f'{FORMER[found.group(1)]}.{found.group(1)}'

    new = DOTTED.sub(dotted, new)
    # Whatever the gate would still find (a statement composed in an
    # f-string, say) is listed for the hand edit.
    seen = {line for line, _ in listed}
    for found in LOOSE.finditer(new):
        names = re.findall(r'[A-Za-z_]\w*', found.group(1).split('#')[0])
        line = new.count('\n', 0, found.start()) + 1
        if line not in seen and any(name in FORMER for name in names):
            listed.append((line, 'left for a hand edit'))
            seen.add(line)
    return new, counts, listed


def files(root):
    zones = [('machinome', (root / 'machinome').rglob('*')),
             ('tests', (root / 'tests').rglob('*')),
             ('docs', [p for p in (root / 'docs').rglob('*')
                       if p.relative_to(root / 'docs').parts[:1] != ('adrs',)]
              + [root / 'README.rst'])]
    for zone, paths in zones:
        for path in sorted(paths):
            if not path.is_file() or SKIPPED_PARTS & set(path.parts):
                continue
            relative = path.relative_to(root).as_posix()
            try:
                yield zone, relative, path, path.read_text()
            except (UnicodeDecodeError, OSError):
                continue


def main(argv):
    root = Path(argv[1]).resolve()
    apply = '--apply' in argv
    show = '--diff' in argv
    totals = {}
    hand_files = []
    for zone, relative, path, text in files(root):
        if relative in HAND:
            if IMPORT.search(text) or DOTTED.search(text):
                hand_files.append(relative)
            continue
        new, counts, listed = rewrite(text, relative)
        zone_total = totals.setdefault(
            zone, {'files': 0, 'in place': 0, 'split': 0, 'dotted': 0,
                   'listed': 0})
        if new != text:
            zone_total['files'] += 1
            for key, value in counts.items():
                zone_total[key] += value
            if show:
                sys.stdout.writelines(difflib.unified_diff(
                    text.splitlines(True), new.splitlines(True),
                    f'a/{relative}', f'b/{relative}'))
            if apply:
                path.write_text(new)
        for line, why in listed:
            zone_total['listed'] += 1
            print(f'LISTED {relative}:{line}: {why}')
    for zone, total in totals.items():
        print(f'{zone}: {total}')
    for relative in hand_files:
        print(f'HAND {relative}')
    print('applied' if apply else 'dry run: nothing written')


if __name__ == '__main__':
    main(sys.argv)
