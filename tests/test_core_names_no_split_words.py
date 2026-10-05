# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The core names its two engines for the representation each consumes,
`brep` and `mesh` (OpenSpec change `brep-mesh`, design.md Decision 9): the
acceptance gate, permanent.

Every Python module of the distribution under `machinome/`, the project
templates included, is read by token -- identifiers and attribute names
(NAME), strings and docstrings (STRING; an f-string read whole, as one
string, on every Python), and comments (COMMENT) -- and by its own path.
Each module is parsed, so one that does not parse fails the gate rather
than being skipped. The rule, per word:

- W1, `faceted`: every case-insensitive occurrence offends. No zone.
- W2, `exact` in an identifier, an attribute name or a path: an offence
  when `exact` or `exactness` is one of its components (split at `_`, `/`,
  `.` and a lower-to-upper camel-case boundary), except the ordinary-sense
  identifiers of `ORDINARY`, by module.
- W3, `exact` in a string, docstring or comment, as a word: an offence when
  the token's whole text is the word (the path word), when it is written as
  a flag or a setting, when it is back-quoted as a member, when it is
  `exactness`, or when the next word, across spaces, back-quotes,
  asterisks, braces, `_`, `-` and `.`, is one of `SPLIT_NOUNS`; except the
  phrases of `ORDINARY_TEXT`, by module, in which the adjective is ordinary.
  `exact` before any other word (`exactly`, `exact IEEE-754 values`, `the
  exact set`, `exact-negative`, `exact-bytes`) is the ordinary adjective.
- W4, `occt` and `manifold`: every case-insensitive occurrence offends
  outside `ZONES`: the two provider modules, which may name their
  libraries, and the four node-type modules whose own kernels are built on
  OCCT.

The words are spelled in pieces below so this file's own reading of them is
plain; the gate does not scan `tests/`.
"""

import ast
import io
import re
import tokenize
from pathlib import Path
from unittest import TestCase

ROOT = Path(__file__).resolve().parents[1]

#: Where `occt` and `manifold` may stand.
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
    'machinome/simulation/profile.py': {'ex' 'act'},
    'machinome/node/frames.py': {'ex' 'act'},
    'machinome/motion/joints.py': {'ex' 'act'},
    'machinome/simulation/trajectory.py': {
        'ex' 'act_lines', 'ex' 'act_source_lines', 'ex' 'act_end',
        'authored_ex' 'act'},
}

#: Phrases, by module, in which `exact` before a noun of SPLIT_NOUNS is
#: still the ordinary adjective; matched on the text from the word on, its
#: whitespace collapsed.
ORDINARY_TEXT = {
    'machinome/node/sources.py': ('ex' 'act path to watch',),
    'machinome/simulation/driver.py': ('ex' 'act comparison rather',),
    'machinome/manager/test.py': ('ex' 'act operations list',),
    'machinome/node/base.py': ('Ex' 'act artifact equality',),
}

#: The nouns after which `exact` names the split.
SPLIT_NOUNS = frozenset((
    'engine', 'engines', 'kernel', 'kernels', 'geometry', 'leaf', 'leaves',
    'node', 'nodes', 'shape', 'shapes', 'solid', 'solids', 'common',
    'cache', 'artifact', 'artifacts', 'path', 'paths', 'verdict',
    'verdicts', 'fusion', 'adapter', 'adapters', 'layer', 'backend',
    'contract', 'branch', 'record', 'records', 'identity', 'stack', 'part',
    'parts', 'comparison', 'comparisons', 'placement', 'placements',
    'composition', 'operation', 'operations', 'module', 'modules',
    'surface', 'surfaces', 'children', 'route', 'project', 'projects',
    'model', 'models', 'run', 'test', 'side', 'currency', 'memo', 'memos',
    'state', 'result', 'binding', 'only', 'needed', 'reason', 'base',
    'bases'))

_FACETED = re.compile('fac' 'eted', re.IGNORECASE)
_TECH = re.compile('oc' 'ct|mani' 'fold', re.IGNORECASE)
_WORD = re.compile(r'(?<![A-Za-z])(ex' r'act)(ness)?(?![a-z])',
                   re.IGNORECASE)
_NEXT = re.compile(r'[\s`*_\-.{}]*([A-Za-z]+)')
_COMPONENT = re.compile(r'[A-Z]?[a-z]+|[A-Z]+(?![a-z])|[0-9]+')
_COMPONENTS = frozenset(('ex' 'act', 'ex' 'actness'))

_KINDS = {tokenize.NAME, tokenize.STRING, tokenize.COMMENT}


def name_offences(name, relative=''):
    """W2: how many components of one identifier or one path are the
    word."""
    if name in ORDINARY.get(relative, ()):
        return 0
    words = []
    for part in re.split(r'[_/.]+', name):
        words += [w.lower() for w in _COMPONENT.findall(part)]
    return sum(1 for word in words if word in _COMPONENTS)


def text_offences(text, relative=''):
    """W3: how many occurrences of the word in one string, docstring or
    comment name the split."""
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


def word_offences(text, relative=''):
    """W1 and W4: the occurrences of `faceted`, and of the two technology
    names outside the zones."""
    hits = len(_FACETED.findall(text))
    if relative not in ZONES:
        hits += len(_TECH.findall(text))
    return hits


def token_offences(kind, text, relative=''):
    """Every offence of one token."""
    hits = word_offences(text, relative)
    if kind == tokenize.NAME:
        return hits + name_offences(text, relative)
    return hits + text_offences(text, relative)


def path_offences(relative):
    """Every offence of a module's own path."""
    return word_offences(relative, relative) + name_offences(relative)


def tokens(source):
    """The module's tokens, an f-string read whole as one STRING token.

    Python 3.11 yields an f-string as one STRING token; 3.12 splits it into
    FSTRING_START, FSTRING_MIDDLE pieces and the tokens of its expressions.
    Reading it whole on both keeps the count the same on both.
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


def scan(root=ROOT):
    """`{relative path: (count, [(line, token), ...])}` for every module of
    `machinome/` that offends."""
    found = {}
    for path in sorted((root / 'machinome').rglob('*.py')):
        relative = path.relative_to(root).as_posix()
        source = path.read_text()
        # A module that does not parse fails the gate rather than being
        # skipped.
        ast.parse(source, filename=relative)
        count = path_offences(relative)
        offending = [(0, relative)] if count else []
        for token in tokens(source):
            if token.type in _KINDS:
                hits = token_offences(token.type, token.string, relative)
                if hits:
                    count += hits
                    offending.append((token.start[0], token.string))
        if count:
            found[relative] = (count, offending)
    return found


def report(found):
    lines = []
    for relative, (count, offending) in sorted(
            found.items(), key=lambda item: (-item[1][0], item[0])):
        first = ', '.join(f'{line}: {text[:40]!r}'
                          for line, text in offending[:3])
        lines.append(f'{count:4d} {relative} ({first})')
    total = sum(count for count, _ in found.values())
    lines.append(f'modules: {len(found)}  occurrences: {total}')
    return '\n'.join(lines)


E = 'ex' 'act'
F = 'fac' 'eted'


class TheRuleTest(TestCase):

    def test_w1_every_occurrence_of_the_mesh_quality_word_offends(self):
        for text in (F, F.upper(), f'--{F}', f'_{F}_verdict', f'a {F} run'):
            with self.subTest(text=text):
                self.assertEqual(word_offences(text, ''), 1)
        self.assertEqual(word_offences(F, 'machinome/engine/mesh.py'), 1)

    def test_w2_the_word_as_a_component_of_a_name_or_path_offends(self):
        for name in (f'{E.capitalize()}LeafNode', f'{E}_cache',
                     f'_routes_{E}', f'node.{E}', f'machinome/{E}_engine.py',
                     E, f'{E}ness'):
            with self.subTest(name=name):
                self.assertEqual(name_offences(name), 1)

    def test_w2_the_ordinary_identifiers_pass_only_in_their_module(self):
        for relative, names in ORDINARY.items():
            for name in names:
                with self.subTest(relative=relative, name=name):
                    self.assertEqual(name_offences(name, relative), 0)
                    self.assertEqual(
                        name_offences(name, 'machinome/test.py'), 1)

    def test_w2_a_longer_word_is_not_the_word(self):
        for name in (f'{E}ly', f'{E}itude', 'inexact', 'exacting'):
            with self.subTest(name=name):
                self.assertEqual(name_offences(name), 0)

    def test_w3_the_split_in_text_offends(self):
        for text in (f"'{E}'", f'"{E}"', f'--{E}', f'KERNEL={E}',
                     f'the `{E}` member', f'its {E}ness',
                     f'the {E} engine', f'{E}-geometry', f'an {E}_cache',
                     f'the {E} {{artifact}} artifact', f'# {E} leaf',
                     f'two **{E}** parts'):
            with self.subTest(text=text):
                self.assertEqual(text_offences(text), 1)

    def test_w3_the_ordinary_adjective_passes(self):
        for text in (f'{E}ly', f'{E} IEEE-754 values', f'{E} matrix bytes',
                     f'the {E}-negative shortcut', f'the {E}-bytes key',
                     f'the {E} set', f'the {E} 0, 1 or -1'):
            with self.subTest(text=text):
                self.assertEqual(text_offences(text), 0)

    def test_w3_the_four_ordinary_phrases_pass_only_in_their_module(self):
        for relative, phrases in ORDINARY_TEXT.items():
            for phrase in phrases:
                with self.subTest(relative=relative, phrase=phrase):
                    self.assertEqual(text_offences(f'the {phrase} here',
                                                   relative), 0)
                    self.assertEqual(text_offences(f'the {phrase} here',
                                                   'machinome/test.py'), 1)

    def test_w4_the_technologies_offend_outside_the_zones(self):
        for text in ('oc' 'ct', 'OC' 'CT', 'mani' 'fold3d',
                     'machinome/' 'oc' 'ct/engine.py'):
            with self.subTest(text=text):
                self.assertEqual(word_offences(text, 'machinome/test.py'), 1)
        for zone in ZONES:
            with self.subTest(zone=zone):
                self.assertEqual(word_offences('OC' 'CT', zone), 0)

    def test_a_path_is_read_like_a_name(self):
        self.assertEqual(path_offences(f'machinome/node/{E}_leaf.py'), 1)
        self.assertEqual(path_offences('machinome/' 'oc' 'ct/engine.py'), 1)
        self.assertEqual(path_offences('machinome/engine/brep.py'), 0)

    def test_an_f_string_is_one_text(self):
        source = f"x = f'it is the {E} {{artifact}} artifact'\n"
        texts = [token.string for token in tokens(source)
                 if token.type == tokenize.STRING]
        self.assertEqual(len(texts), 1)
        self.assertEqual(text_offences(texts[0]), 1)


class TheCoreNamesNoSplitWordsTest(TestCase):

    def test_no_module_names_the_split_but_by_its_two_words(self):
        found = scan()
        self.assertEqual(found, {}, '\n' + report(found))
