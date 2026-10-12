# Machinome Skills - The machinome skills for assistants that read Agent Skills
# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""The shipped skills follow the Agent Skills format.

Each check reads the skills the package ships, under
`machinome/skills/agent-skills/`, never an installed copy: exactly the
skills `machinome` and `machinome-simulate`, real files, a frontmatter of
`name`, `description` and `license` with the name valid and equal to its
directory, the licence the set's, an entry point under 500 lines, local
links that stay inside their skill, every reference linked from its
`SKILL.md`, nothing but `SKILL.md` and `references/*.md` in a skill, and
every shipped file named by the manifest's package data (change
`join-skills`, capability `skills-distribution`).
"""

import re
import tomllib
import unittest
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

import yaml

PACKAGE = Path(__file__).resolve().parents[1]
PORTION = PACKAGE / 'machinome' / 'skills'
SKILLS_DIRECTORY = PORTION / 'agent-skills'
#: The framework's manifest, whose licence expression is the set's.
FRAMEWORK = PACKAGE.parent / 'machinome' / 'pyproject.toml'

SKILLS = ('machinome', 'machinome-simulate')
FIELDS = {'name', 'description', 'license'}
NAME = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*')
LINK = re.compile(r'\[[^\]\n]+\]\(([^\s)]+)\)')
FRONTMATTER = re.compile(r'\A---\n(.*?)\n---\n', re.S)


def read_toml(path):
    with open(path, 'rb') as stream:
        return tomllib.load(stream)


def frontmatter(name):
    text = (SKILLS_DIRECTORY / name / 'SKILL.md').read_text(encoding='utf-8')
    found = FRONTMATTER.match(text)
    if found is None:
        raise AssertionError(f'{name}: SKILL.md has no YAML frontmatter')
    return yaml.safe_load(found.group(1)), text


def local_links(path):
    for target in LINK.findall(path.read_text(encoding='utf-8')):
        url = urlsplit(target)
        if url.scheme or url.netloc or not url.path:
            continue
        yield target, (path.parent / unquote(url.path)).resolve()


class TheSkillsTest(unittest.TestCase):
    """The two skills, each a directory of real files."""

    def test_the_package_ships_exactly_the_two_skills(self):
        self.assertEqual(sorted(path.name
                                for path in SKILLS_DIRECTORY.iterdir()),
                         sorted(SKILLS))

    def test_each_skill_is_real_files(self):
        for name in SKILLS:
            with self.subTest(skill=name):
                directory = SKILLS_DIRECTORY / name
                self.assertFalse(directory.is_symlink(),
                                 f'{name} is a symbolic link')
                for path in directory.rglob('*'):
                    self.assertFalse(path.is_symlink(),
                                     f'{name}: {path.name} is a symbolic '
                                     'link, not a file the package ships')

    def test_each_skill_holds_its_entry_point_and_references_only(self):
        for name in SKILLS:
            with self.subTest(skill=name):
                directory = SKILLS_DIRECTORY / name
                files = sorted(path.relative_to(directory).as_posix()
                               for path in directory.rglob('*')
                               if path.is_file())
                self.assertIn('SKILL.md', files)
                for relative in files:
                    self.assertTrue(
                        relative == 'SKILL.md'
                        or re.fullmatch(r'references/[^/]+\.md', relative),
                        f'{name} ships {relative}, neither SKILL.md nor a '
                        'reference: a skill carries no licence or notice '
                        'file of its own')


class TheFrontmatterTest(unittest.TestCase):
    """Each `SKILL.md` begins with the format's frontmatter."""

    def test_the_keys_are_name_description_and_licence(self):
        for name in SKILLS:
            with self.subTest(skill=name):
                data, _text = frontmatter(name)
                self.assertIsInstance(data, dict)
                self.assertEqual(set(data), FIELDS,
                                 f'{name}: the frontmatter keys are not '
                                 f'{sorted(FIELDS)}')

    def test_the_name_is_valid_and_its_directory_s(self):
        for name in SKILLS:
            with self.subTest(skill=name):
                data, _text = frontmatter(name)
                self.assertEqual(data['name'], name,
                                 f'{name}: the name differs from its '
                                 'directory')
                self.assertTrue(NAME.fullmatch(name) and len(name) <= 64,
                                f'{name}: not a valid skill name')

    def test_the_description_is_1_to_1024_characters(self):
        for name in SKILLS:
            with self.subTest(skill=name):
                data, _text = frontmatter(name)
                description = data['description']
                self.assertIsInstance(description, str)
                self.assertTrue(1 <= len(description.strip()) <= 1024,
                                f'{name}: the description has '
                                f'{len(description.strip())} characters')

    def test_the_licence_is_the_set_s(self):
        expression = read_toml(FRAMEWORK)['project']['license']
        for name in SKILLS:
            with self.subTest(skill=name):
                data, _text = frontmatter(name)
                self.assertEqual(data['license'], expression,
                                 f'{name}: the licence field is not the '
                                 'set\'s expression')

    def test_the_entry_point_is_under_500_lines(self):
        for name in SKILLS:
            with self.subTest(skill=name):
                _data, text = frontmatter(name)
                self.assertLess(len(text.splitlines()), 500,
                                f'{name}: move detailed guidance into '
                                'references')


class TheLinksTest(unittest.TestCase):
    """A skill's links stay inside it and reach every reference."""

    def test_every_local_link_resolves_inside_its_skill(self):
        for name in SKILLS:
            directory = (SKILLS_DIRECTORY / name).resolve()
            for path in sorted(directory.rglob('*.md')):
                for target, resolved in local_links(path):
                    with self.subTest(skill=name, file=path.name,
                                      target=target):
                        self.assertTrue(
                            resolved.is_relative_to(directory)
                            and resolved.is_file(),
                            f'{name}: {path.name} links {target}, which is '
                            'not a file of the skill')

    def test_every_reference_is_linked_from_the_entry_point(self):
        for name in SKILLS:
            directory = SKILLS_DIRECTORY / name
            _data, text = frontmatter(name)
            links = set(LINK.findall(text))
            for path in sorted((directory / 'references').glob('*')):
                with self.subTest(skill=name, reference=path.name):
                    self.assertIn(
                        path.relative_to(directory).as_posix(), links,
                        f'{name}: references/{path.name} is not linked '
                        'from SKILL.md')


class TheManifestTest(unittest.TestCase):
    """Every file the package ships beside its modules is package data."""

    def test_every_shipped_file_is_named_by_the_package_data(self):
        manifest = read_toml(PACKAGE / 'pyproject.toml')
        patterns = manifest['tool']['setuptools']['package-data'][
            'machinome.skills']
        shipped = sorted(
            path.relative_to(PORTION).as_posix()
            for path in PORTION.rglob('*')
            if path.is_file() and path.suffix not in ('.py', '.pyc')
            and '__pycache__' not in path.parts)
        self.assertIn('tools.toml', shipped)
        for relative in shipped:
            with self.subTest(file=relative):
                path = PurePosixPath(relative)
                self.assertTrue(
                    any(len(path.parts) == len(PurePosixPath(pattern).parts)
                        and path.match(pattern) for pattern in patterns),
                    f'{relative} is matched by no package-data pattern of '
                    'the manifest')
