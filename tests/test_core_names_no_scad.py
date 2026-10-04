# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The core names no OpenSCAD technology (OpenSpec change `openscad-out`,
design.md Decision 1): the acceptance gate, permanent.

Every Python module of the distribution under `machinome/`, the project
templates included, is read by token -- identifiers and attribute names,
strings and docstrings (f-string text included), and comments -- and by its
own path. Every case-insensitive occurrence of the three letters the family
is named by is an offence, except JSCAD's own name: an occurrence immediately
preceded by a `j` that begins a word (at the start of the text, after a
character that is not a letter, or an upper-case `J` after a lower-case
letter). The occurrences may stand only in the four allowed zones: the
family's package `machinome/node/openscad/`, the module
`machinome/node/solid2.py`, the OpenSCAD viewer's module
`machinome/viewers/openscad.py` (until the viewer cycle moves it) and the
table of supported node types `machinome/node/supported.py`.
"""

import ast
import io
import re
import tokenize
from pathlib import Path
from unittest import TestCase

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'machinome'

#: The four places the word may stand.
ALLOWED_PACKAGE = 'machinome/node/openscad/'
ALLOWED_MODULES = frozenset((
    'machinome/node/solid2.py',
    'machinome/viewers/openscad.py',
    'machinome/node/supported.py',
))

#: The three letters, spelled so this file's own reading of them is plain.
_WORD = re.compile('s' 'cad', re.IGNORECASE)

_KINDS = {tokenize.NAME, tokenize.STRING, tokenize.COMMENT}
if hasattr(tokenize, 'FSTRING_MIDDLE'):
    _KINDS.add(tokenize.FSTRING_MIDDLE)


def offences(text):
    """The start offset of every occurrence of the word in `text` that is
    not JSCAD's own name."""
    found = []
    for match in _WORD.finditer(text):
        start = match.start()
        if start > 0 and text[start - 1] in 'jJ':
            j = start - 1
            before = text[j - 1] if j > 0 else ''
            if not before.isalpha() or (text[j] == 'J' and before.islower()):
                continue
        found.append(start)
    return found


def allowed(relative):
    return (relative.startswith(ALLOWED_PACKAGE)
            or relative in ALLOWED_MODULES)


def scan(root=ROOT):
    """`{relative path: (count, [(line, token), ...])}` for every module of
    `machinome/` outside the allowed zones that holds the word."""
    found = {}
    for path in sorted((root / 'machinome').rglob('*.py')):
        relative = path.relative_to(root).as_posix()
        if allowed(relative):
            continue
        source = path.read_text()
        # A module that does not parse fails the gate rather than being
        # skipped.
        ast.parse(source, filename=relative)
        count = len(offences(relative))
        tokens = [(0, relative)] if count else []
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type in _KINDS:
                hits = len(offences(token.string))
                if hits:
                    count += hits
                    tokens.append((token.start[0], token.string))
        if count:
            found[relative] = (count, tokens)
    return found


def report(found):
    lines = []
    for relative, (count, tokens) in sorted(
            found.items(), key=lambda item: (-item[1][0], item[0])):
        first = ', '.join(f'{line}: {text[:40]!r}' for line, text in tokens[:3])
        lines.append(f'{count:4d} {relative} ({first})')
    total = sum(count for count, _ in found.values())
    lines.append(f'modules: {len(found)}  occurrences: {total}')
    return '\n'.join(lines)


class TheRuleTest(TestCase):

    def test_jscad_names_pass(self):
        for text in ('jscad', 'JSCAD', 'jscad_source', 'JScadNode',
                     'OpenJScadNode', 'machinome/node/jscad.py', '_jscad'):
            with self.subTest(text=text):
                self.assertEqual(offences(text), [])

    def test_every_other_occurrence_offends(self):
        for text in ('open' 's' 'cad', 'Open' 'SCAD', 's' 'cad_file',
                     '.s' 'cad', 'S' 'CAD', 'xs' 'cad', 'openjs' 'cad',
                     'ca' 's' 'cade'):
            with self.subTest(text=text):
                self.assertEqual(len(offences(text)), 1)

    def test_a_path_is_read_like_a_token(self):
        self.assertEqual(len(offences('machinome/node/open' 's' 'cad.py')), 1)

    def test_the_allowed_zones(self):
        self.assertTrue(allowed('machinome/node/open' 's' 'cad/writer.py'))
        self.assertTrue(allowed('machinome/node/solid2.py'))
        self.assertTrue(allowed('machinome/viewers/open' 's' 'cad.py'))
        self.assertTrue(allowed('machinome/node/supported.py'))
        self.assertFalse(allowed('machinome/node/base.py'))
        self.assertFalse(allowed('machinome/open' 's' 'cad/engine.py'))


class TheCoreNamesNoScadTest(TestCase):

    def test_no_module_outside_the_allowed_zones_holds_the_word(self):
        found = scan()
        self.assertEqual(found, {}, '\n' + report(found))
