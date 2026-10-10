#!/usr/bin/env python3
# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""Prototype of the `root-cleanup` acceptance gate's scan (design.md,
Decision 6).

Planning evidence, not a test: run it with any Python 3.11+ from anywhere,
`python3 gate-prototype.py <checkout> [--files]`, and it prints the red count
per zone (and, with `--files`, per file). Task 1.1 re-measures with it; task
2.1 turns the same rule into `tests/test_node_root_exports_nothing.py`, after
which this file is evidence only. The gate's runtime half (the root resolves
none of the names, and binds no public name but its submodules) is not here:
it needs the framework imported, and this prototype imports nothing of it.

The rule, over every text file of three zones, read as text (code, strings,
docstrings, comments and prose alike, since a fixture project in a string or
an example in a page is code a reader runs):

- R1, the import line: every `from machinome.node import <names>` statement
  -- one line, a parenthesised list across lines, or a backslash
  continuation -- whose names include one of the twenty-one former root
  names (FORMER), or that is the star import `*`, offends once per name.
  A name that is a submodule (`supported`, `phase`, `base`, ...) passes,
  and so does a name outside the twenty-one (`RotationalPort`, which
  `_MOVED` refuses, or `NoSuchThing`): the scan judges the twenty-one, the
  runtime half judges the rest. A statement composed at run time
  (`f'from machinome.node import {name}'`) is not a literal line and
  passes: that is how a test pinning the refusal spells it.
- R2, the dotted address: `machinome.node.<name>` for a name of FORMER, as
  in `.. autoclass:: machinome.node.Solid2Node` or
  `patch('machinome.node.StepNode')`, offends once.

The zones: `machinome/` (every file, the project templates included);
`tests/` (every file, the fixture projects included); `docs/` without
`docs/adrs/` (decision records keep the names they used), `docs/_build/`
and `docs/_exports/` (built output), plus `README.rst`.
"""

import re
import sys
from pathlib import Path

#: The twenty-one names `machinome/node/__init__.py` resolved at 815ceb9,
#: each with the module that defines it. Written out here, not read from
#: the package under test.
FORMER = {
    'AssemblyNode': 'machinome.node.assembly',
    'declared_children': 'machinome.node.declarative',
    'FusionNode': 'machinome.node.fusion',
    'CadQueryNode': 'machinome.node.cadquery',
    'Build123dNode': 'machinome.node.build123d',
    'Build123dSheetNode': 'machinome.node.build123d',
    'SheetLeafNode': 'machinome.node.sheet_leaf',
    'FlexibleNode': 'machinome.node.flexible',
    'MolejoNode': 'machinome.node.molejo',
    'Solid2Node': 'machinome.node.solid2',
    'OpenScadNode': 'machinome.node.openscad',
    'JScadNode': 'machinome.node.jscad',
    'StlNode': 'machinome.node.stl',
    'Marking': 'machinome.node.markings',
    'Wrapped': 'machinome.node.markings',
    'Flat': 'machinome.node.markings',
    'Svg': 'machinome.node.markings',
    'Frame': 'machinome.node.frames',
    'StepNode': 'machinome.node.step',
    'property_as_number': 'machinome.node.decorators',
    'StlRenderStart': 'machinome.node.base',
}

IMPORT = re.compile(
    r'from\s+machinome\.node\s+import\s+'
    r'(\([^)]*\)|(?:[^\n\\]|\\\n)*)')
DOTTED = re.compile(
    r'\bmachinome\.node\.(' + '|'.join(sorted(FORMER, key=len, reverse=True))
    + r')\b')
NAME = re.compile(r'[A-Za-z_]\w*|\*')

SKIPPED_PARTS = {'__pycache__', '.pytest_cache', '_build', '_exports'}


def imported_names(clause):
    """The names one `import` clause lists, aliases and comments dropped."""
    text = clause.strip()
    if text.startswith('('):
        text = text[1:].rsplit(')', 1)[0]
    text = re.sub(r'#[^\n]*', '', text).replace('\\\n', ' ')
    names = []
    for part in text.split(','):
        match = NAME.match(part.strip())
        if match:
            names.append(match.group(0))
    return names


def offences(text):
    """`[(line, spelling), ...]` for every offence in `text`."""
    found = []
    for match in IMPORT.finditer(text):
        line = text.count('\n', 0, match.start()) + 1
        for name in imported_names(match.group(1)):
            if name in FORMER or name == '*':
                found.append((line, f'from machinome.node import {name}'))
    for match in DOTTED.finditer(text):
        line = text.count('\n', 0, match.start()) + 1
        found.append((line, match.group(0)))
    return found


def files(root, zone):
    if zone == 'machinome':
        paths = (root / 'machinome').rglob('*')
    elif zone == 'tests':
        paths = (root / 'tests').rglob('*')
    else:
        paths = [p for p in (root / 'docs').rglob('*')
                 if 'adrs' not in p.relative_to(root / 'docs').parts[:1]]
        paths.append(root / 'README.rst')
    for path in sorted(paths):
        if not path.is_file() or SKIPPED_PARTS & set(path.parts):
            continue
        try:
            yield path, path.read_text()
        except (UnicodeDecodeError, OSError):
            continue


def scan(root):
    """`{zone: {relative path: [(line, spelling), ...]}}`."""
    result = {}
    for zone in ('machinome', 'tests', 'docs'):
        result[zone] = {}
        for path, text in files(root, zone):
            found = offences(text)
            if found:
                result[zone][path.relative_to(root).as_posix()] = found
    return result


if __name__ == '__main__':
    checkout = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
    result = scan(checkout)
    for zone, found in result.items():
        total = sum(len(v) for v in found.values())
        print(f'{zone}: {len(found)} files, {total} offences')
        if '--files' in sys.argv:
            for relative, hits in sorted(found.items()):
                print(f'  {len(hits):3d} {relative}')
