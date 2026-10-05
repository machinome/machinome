#!/usr/bin/env python3
# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""Prototype of the `brep-mesh` acceptance gate (design.md, Decision 9).

Planning evidence, not a test: run it with any Python 3.11+ from anywhere,
`python3 gate-prototype.py <checkout>`, and it prints the red count per
module. Task 1.1 re-measures with it; task 2.1 turns the same rule into
`tests/test_core_names_no_split_words.py`, after which this file is
evidence only.

The rule, per word, over every `machinome/**/*.py` of the checkout (the
project templates included), read by token -- identifiers and attribute
names (NAME), strings and docstrings (STRING, and FSTRING_MIDDLE where the
running Python has it), comments (COMMENT) -- and by the module's own path:

- W1, `faceted`: every case-insensitive occurrence offends. No zone.
- W2, `exact` in an identifier, an attribute name or a path component: an
  offence when `exact` or `exactness` is one of its components (split at
  `_`, `/`, `.` and a lower-to-upper camel-case boundary), except the
  ordinary-sense identifiers of ORDINARY, by module.
- An f-string is read whole, as one string, on every Python (`tokens`).
- W3, `exact` in a string, docstring or comment, as a word (no letter
  before it; nothing but `ness` after it): an offence when the token's
  whole text is the word (the path word `'exact'`), when it is written as
  a flag or a setting (`--exact`, `=exact`), when it is back-quoted as a
  member (`` `exact` ``), when it is `exactness`, or when the next word,
  across spaces, back-quotes, asterisks, braces, `_`, `-` and `.`, is one of
  SPLIT_NOUNS (`exact engine`, `exact_cache`, `exact-geometry`, ...).
  `exact-negative` (ADR-090's sound shortcut, which never answers wrongly)
  is the ordinary adjective and is not in the list.
  `exact` before any other word -- `exact IEEE-754 values`, `the exact
  set`, `exact matrix bytes`, `exactly` -- is the ordinary adjective and
  passes, and so do the four phrases of ORDINARY_TEXT, in which a noun of
  the list follows the ordinary adjective.
- W4, `occt` and `manifold`: every case-insensitive occurrence offends
  outside ZONES: the two provider modules, which may name their libraries,
  and the four node-type modules whose own kernels are built on OCCT.
"""

import ast
import io
import re
import sys
import tokenize
from pathlib import Path

ZONES = frozenset((
    'machinome/engine/brep.py',
    'machinome/engine/mesh.py',
    'machinome/node/cadquery.py',
    'machinome/node/build123d.py',
    'machinome/node/step.py',
    'machinome/node/molejo.py',
))

#: Identifiers in which `exact` is the ordinary adjective, by module.
ORDINARY = {
    'machinome/simulation/profile.py': {'exact'},
    'machinome/node/frames.py': {'exact'},
    'machinome/motion/joints.py': {'exact'},
    'machinome/simulation/trajectory.py': {
        'exact_lines', 'exact_source_lines', 'exact_end', 'authored_exact'},
}

#: Phrases, by module, in which `exact` before a noun of SPLIT_NOUNS is
#: still the ordinary adjective; matched on the text from the word on, its
#: whitespace collapsed.
ORDINARY_TEXT = {
    'machinome/node/sources.py': ('exact path to watch',),
    'machinome/simulation/driver.py': ('exact comparison rather',),
    'machinome/manager/test.py': ("exact operations list",),
    'machinome/node/base.py': ('Exact artifact equality',),
}

SPLIT_NOUNS = (
    'engine', 'engines', 'kernel', 'kernels', 'geometry', 'leaf', 'leaves',
    'node', 'nodes', 'shape', 'shapes', 'solid', 'solids', 'common',
    'cache', 'artifact', 'artifacts', 'path', 'paths', 'verdict',
    'verdicts', 'fusion', 'adapter', 'adapters', 'layer', 'backend',
    'contract', 'branch', 'record', 'records', 'identity', 'stack', 'part',
    'parts', 'comparison', 'comparisons', 'placement',
    'placements', 'composition', 'operation', 'operations', 'module',
    'modules', 'surface', 'surfaces', 'children', 'route', 'project',
    'projects', 'model', 'models',
    'run', 'test', 'side', 'currency', 'memo', 'memos', 'state', 'result',
    'binding', 'only', 'needed', 'reason', 'base', 'bases')

_FACETED = re.compile('fac' 'eted', re.IGNORECASE)
_TECH = re.compile('oc' 'ct|mani' 'fold', re.IGNORECASE)
_WORD = re.compile(r'(?<![A-Za-z])(ex' r'act)(ness)?(?![a-z])',
                   re.IGNORECASE)
_NEXT = re.compile(r'[\s`*_\-.{}]*([A-Za-z]+)')
_COMPONENT = re.compile(r'[A-Z]?[a-z]+|[A-Z]+(?![a-z])|[0-9]+')

_KINDS = {tokenize.NAME, tokenize.STRING, tokenize.COMMENT}
if hasattr(tokenize, 'FSTRING_MIDDLE'):
    _KINDS.add(tokenize.FSTRING_MIDDLE)


def name_offences(name, relative):
    """W2 for one identifier or one path."""
    if name in ORDINARY.get(relative, ()):
        return 0
    words = []
    for part in re.split(r'[_/.]+', name):
        words += [w.lower() for w in _COMPONENT.findall(part)]
    return sum(1 for w in words if w in ('ex' 'act', 'ex' 'actness'))


def text_offences(text, relative=''):
    """W3 for one string, docstring or comment."""
    found = 0
    ordinary = ORDINARY_TEXT.get(relative, ())
    body = text.strip('\'"rRbBfFuU \n#')
    if body.lower() == 'ex' 'act':
        return 1
    for match in _WORD.finditer(text):
        start, end = match.span()
        if match.group(2):
            found += 1
            continue
        before = text[max(0, start - 2):start]
        if before == '--' or before.endswith('='):
            found += 1
            continue
        if before.endswith('`') and text[end:end + 1] == '`':
            found += 1
            continue
        following = _NEXT.match(text, end)
        if following and following.group(1).lower() in SPLIT_NOUNS:
            rest = ' '.join(text[start:start + 80].split())
            if not any(rest.startswith(phrase) for phrase in ordinary):
                found += 1
    return found


def count(token, relative):
    hits = len(_FACETED.findall(token.string))
    if relative not in ZONES:
        hits += len(_TECH.findall(token.string))
    if token.type == tokenize.NAME:
        hits += name_offences(token.string, relative)
    else:
        hits += text_offences(token.string, relative)
    return hits


def tokens(source):
    """The module's tokens, an f-string read whole as one STRING token.

    Python 3.11 yields an f-string as one STRING token; 3.12 splits it into
    FSTRING_START, FSTRING_MIDDLE pieces and the tokens of its expressions.
    Reading it whole on both keeps the count the same on both: the text of
    `f'it is the exact {artifact} artifact'` is one text either way.
    """
    lines = source.splitlines(keepends=True)
    start = getattr(tokenize, 'FSTRING_START', None)
    end = getattr(tokenize, 'FSTRING_END', None)
    depth = 0
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if start is not None and token.type == start:
            if depth == 0:
                begin = token.start
            depth += 1
            continue
        if depth:
            if token.type == end:
                depth -= 1
                if depth == 0:
                    (row0, col0), (row1, col1) = begin, token.end
                    if row0 == row1:
                        text = lines[row0 - 1][col0:col1]
                    else:
                        text = (lines[row0 - 1][col0:]
                                + ''.join(lines[row0:row1 - 1])
                                + lines[row1 - 1][:col1])
                    yield tokenize.TokenInfo(tokenize.STRING, text, begin,
                                             token.end, '')
            continue
        yield token


def scan(root):
    found = {}
    for path in sorted((root / 'machinome').rglob('*.py')):
        relative = path.relative_to(root).as_posix()
        source = path.read_text()
        ast.parse(source, filename=relative)
        total = len(_FACETED.findall(relative)) + name_offences(relative, '')
        if relative not in ZONES:
            total += len(_TECH.findall(relative))
        for token in tokens(source):
            if token.type in _KINDS:
                total += count(token, relative)
        if total:
            found[relative] = total
    return found


if __name__ == '__main__':
    found = scan(Path(sys.argv[1] if len(sys.argv) > 1 else '.'))
    for relative, total in sorted(found.items(),
                                  key=lambda item: (-item[1], item[0])):
        print(f'{total:5d} {relative}')
    print(f'modules: {len(found)}  occurrences: {sum(found.values())}')
