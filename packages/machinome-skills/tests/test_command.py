# Machinome Skills - The machinome skills for assistants that read Agent Skills
# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""`machinome skills`: the registry, `install`, `update` and `list`.

The capability `skills-distribution` (change `join-skills`). Every test
works in scratch directories made by `tempfile`, `HOME` among them where a
personal directory is written; nothing is written under the repository or a
real home. The installer's functions run in this process with their output
captured; `machinome` runs in a subprocess where the dispatch through the
entry-point group `machinome.commands` is under test.
"""

import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from argparse import Namespace
from contextlib import redirect_stderr, redirect_stdout
from importlib import metadata
from pathlib import Path
from unittest.mock import patch

import yaml

from machinome.skills import installer

#: OpenSpec 1.6.0's tools that have a skills directory, by id, and the
#: dot-directory it names (`AI_TOOLS` of its `dist/core/config.js`),
#: written out here rather than read from the registry under test.
OPENSPEC = {
    'amazon-q': '.amazonq', 'antigravity': '.agent', 'auggie': '.augment',
    'bob': '.bob', 'claude': '.claude', 'cline': '.cline', 'codex': '.codex',
    'forgecode': '.forge', 'codebuddy': '.codebuddy',
    'continue': '.continue', 'costrict': '.cospec', 'crush': '.crush',
    'cursor': '.cursor', 'factory': '.factory', 'gemini': '.gemini',
    'github-copilot': '.github', 'iflow': '.iflow', 'junie': '.junie',
    'kilocode': '.kilocode', 'kimi': '.kimi', 'kiro': '.kiro',
    'lingma': '.lingma', 'vibe': '.vibe', 'oh-my-pi': '.omp',
    'opencode': '.opencode', 'pi': '.pi', 'qoder': '.qoder', 'qwen': '.qwen',
    'roocode': '.roo', 'trae': '.trae', 'windsurf': '.windsurf',
}

#: OpenSpec's detection paths for GitHub Copilot, its one tool not detected
#: by its dot-directory alone.
COPILOT = ('.github/copilot-instructions.md', '.github/instructions',
           '.github/workflows/copilot-setup-steps.yml', '.github/prompts',
           '.github/agents', '.github/skills', '.github/.mcp.json')

#: The rows whose directories follow the client's documentation rather
#: than OpenSpec's dot-directory: project and personal.
DIFFERING = {
    'codex': ('.agents/skills/', '~/.agents/skills/'),
    'pi': ('.agents/skills/', '~/.agents/skills/'),
    'kilocode': ('.kilo/skills/', '~/.kilo/skills/'),
    'windsurf': ('.devin/skills/', '~/.config/devin/skills/'),
}

#: The files of each skill the package ships.
SKILL_FILES = {
    'machinome': ('SKILL.md', 'references/mechanical-contracts.md'),
    'machinome-simulate': ('SKILL.md', 'references/source-adaptation.md'),
}

SHIPPED = (Path(__file__).resolve().parents[1] / 'machinome' / 'skills'
           / 'agent-skills')

MACHINOME = Path(sys.executable).parent / 'machinome'

VERSION = metadata.version('machinome-skills')


def copies(base):
    """The files a copy of both skills holds under `base`."""
    return sorted(f'{base}/{skill}/{name}'
                  for skill, names in SKILL_FILES.items() for name in names)


def files(root):
    return sorted(path.relative_to(root).as_posix()
                  for path in Path(root).rglob('*') if path.is_file())


def frontmatter(path):
    text = Path(path).read_text(encoding='utf-8')
    found = re.match(r'\A---\n(.*?)\n---\n', text, re.S)
    return yaml.safe_load(found.group(1))


def set_marker(path, version):
    text = Path(path).read_text(encoding='utf-8')
    changed = re.sub(r'(  version: )"[^"]*"', rf'\1"{version}"', text,
                     count=1)
    assert changed != text, path
    Path(path).write_text(changed, encoding='utf-8')


class Terminal(io.StringIO):
    """A standard input that says it is a terminal."""

    def isatty(self):
        return True


class Scratch(unittest.TestCase):
    """A scratch project, a scratch home, and the verbs run in process."""

    def setUp(self):
        self.project = Path(tempfile.mkdtemp(prefix='skills-project-'))
        self.home = Path(tempfile.mkdtemp(prefix='skills-home-'))
        self.addCleanup(shutil.rmtree, self.project)
        self.addCleanup(shutil.rmtree, self.home)
        environ = patch.dict(os.environ, {'HOME': str(self.home)})
        environ.start()
        self.addCleanup(environ.stop)
        os.environ.pop('CI', None)

    def run_verb(self, verb, stdin=None, **options):
        defaults = {'path': str(self.project), 'personal': False,
                    'force': False}
        if verb == 'install':
            defaults['tools'] = None
        if verb == 'list':
            defaults.pop('force')
        defaults.update(options)
        out, err = io.StringIO(), io.StringIO()
        function = {'install': installer.install, 'update': installer.update,
                    'list': installer.listing}[verb]
        with patch.object(sys, 'stdin', stdin or io.StringIO()), \
                redirect_stdout(out), redirect_stderr(err):
            status = function(Namespace(**defaults))
        return status, out.getvalue(), err.getvalue()

    def install(self, tools, **options):
        status, out, err = self.run_verb('install', tools=tools, **options)
        self.assertEqual(status, 0, out + err)
        return out


class TheRegistryTest(unittest.TestCase):
    """The registry names each tool by OpenSpec's id."""

    def setUp(self):
        self.tools = installer.registry()
        self.by_id = {tool['id']: tool for tool in self.tools}

    def test_the_ids_are_agents_then_openspec_s_in_its_order(self):
        self.assertEqual([tool['id'] for tool in self.tools],
                         ['agents', *OPENSPEC])

    def test_every_openspec_dot_directory_detects_its_tool(self):
        for name, directory in OPENSPEC.items():
            with self.subTest(tool=name):
                detect = self.by_id[name]['detect']
                if name == 'github-copilot':
                    self.assertEqual(tuple(detect), COPILOT)
                else:
                    self.assertIn(directory, detect)

    def test_each_row_states_its_directories_and_its_source(self):
        for tool in self.tools:
            with self.subTest(tool=tool['id']):
                self.assertTrue(tool['name'])
                self.assertTrue(tool['source'])
                self.assertTrue(tool['project'].endswith('skills/'))
                self.assertFalse(tool['project'].startswith(('/', '~')))
                if 'personal' in tool:
                    self.assertTrue(tool['personal'].startswith('~/'))
                    self.assertTrue(tool['personal'].endswith('skills/'))

    def test_the_rows_that_follow_their_client_s_documentation(self):
        for name, (project, personal) in DIFFERING.items():
            with self.subTest(tool=name):
                self.assertEqual(self.by_id[name]['project'], project)
                self.assertEqual(self.by_id[name]['personal'], personal)

    def test_the_other_rows_follow_openspec_s_directory(self):
        for name, directory in OPENSPEC.items():
            if name in DIFFERING:
                continue
            with self.subTest(tool=name):
                self.assertEqual(self.by_id[name]['project'],
                                 f'{directory}/skills/')

    def test_agents_claude_opencode_and_trae(self):
        self.assertEqual(
            {key: self.by_id['agents'][key]
             for key in ('detect', 'project', 'personal')},
            {'detect': ['.agents'], 'project': '.agents/skills/',
             'personal': '~/.agents/skills/'})
        self.assertEqual(self.by_id['claude']['project'], '.claude/skills/')
        self.assertEqual(self.by_id['claude']['personal'], '~/.claude/skills/')
        self.assertEqual(self.by_id['opencode']['personal'],
                         '~/.config/opencode/skills/')
        self.assertNotIn('personal', self.by_id['trae'])


class TheToolsOptionTest(unittest.TestCase):
    """`--tools` as OpenSpec reads it."""

    def test_all_none_and_ids(self):
        ids = [tool['id'] for tool in installer.registry()]
        self.assertEqual(installer.parse_tools('all'), ids)
        self.assertEqual(installer.parse_tools('NONE'), [])
        self.assertEqual(installer.parse_tools('Claude, claude ,AGENTS'),
                         ['claude', 'agents'])

    def test_what_is_refused_names_the_valid_values(self):
        for value, said in (('x', "unknown tool 'x'"),
                            ('claude,x,y', "unknown tools 'x', 'y'"),
                            ('all,claude', 'all and none stand alone'),
                            ('none,claude', 'all and none stand alone'),
                            ('', 'no tool named'), (' , ', 'no tool named')):
            with self.subTest(value=value):
                with self.assertRaises(installer.UsageError) as raised:
                    installer.parse_tools(value)
                message = str(raised.exception)
                self.assertIn(said, message)
                self.assertIn('use all, none or ids from: agents, amazon-q, ',
                              message)


class InstallTest(Scratch):
    """`machinome skills install`."""

    def test_install_for_two_tools(self):
        (self.project / 'README.md').write_text('a project\n')
        out = self.install('agents,claude')
        expected = sorted(copies('.agents/skills') + copies('.claude/skills')
                          + ['README.md'])
        self.assertEqual(files(self.project), expected)
        self.assertEqual((self.project / 'README.md').read_text(),
                         'a project\n')
        self.assertIn(f'{self.project / ".agents/skills"}/ (agents)', out)
        self.assertIn(f'{self.project / ".claude/skills"}/ (claude)', out)
        for relative in expected:
            if relative == 'README.md':
                continue
            with self.subTest(file=relative):
                self.assertIn(f'  wrote {self.project / relative}\n', out)
        self.assertEqual(out.count('  wrote '), 8)

    def test_a_copy_is_the_shipped_skill_with_the_marker(self):
        self.install('claude')
        for skill, names in SKILL_FILES.items():
            for name in names:
                with self.subTest(skill=skill, file=name):
                    copy = (self.project / '.claude/skills' / skill / name)
                    shipped = (SHIPPED / skill / name).read_text()
                    text = copy.read_text()
                    if name != 'SKILL.md':
                        self.assertEqual(text, shipped)
                        continue
                    marker = ('metadata:\n  installed-by: machinome-skills\n'
                              f'  version: "{VERSION}"\n')
                    self.assertIn(marker, text)
                    self.assertEqual(text.replace(marker, ''), shipped)
                    data = frontmatter(copy)
                    self.assertEqual(data['metadata'],
                                     {'installed-by': 'machinome-skills',
                                      'version': VERSION})
                    self.assertEqual(data['name'], skill)
                    self.assertTrue(all(isinstance(value, str) for value
                                        in data['metadata'].values()))

    def test_a_shared_directory_is_written_once(self):
        out = self.install('agents,codex,pi')
        self.assertEqual(files(self.project), copies('.agents/skills'))
        self.assertIn(f'{self.project / ".agents/skills"}/ (agents, codex, pi)',
                      out)
        self.assertEqual(out.count('  wrote '), 4)

    def test_all_writes_each_directory_of_the_registry(self):
        out = self.install('all')
        directories = {tool['project'] for tool in installer.registry()}
        self.assertEqual(files(self.project), sorted(
            path for directory in directories
            for path in copies(directory.rstrip('/'))))
        self.assertEqual(out.count('  wrote '), 4 * len(directories))

    def test_none_writes_nothing(self):
        status, out, _err = self.run_verb('install', tools='none')
        self.assertEqual(status, 0)
        self.assertIn('Nothing installed: --tools none', out)
        self.assertEqual(files(self.project), [])

    def test_a_skill_the_command_did_not_write_is_refused(self):
        own = self.project / '.cursor/skills/machinome'
        own.mkdir(parents=True)
        (own / 'SKILL.md').write_text('---\nname: machinome\n---\nmine\n')
        (own / 'notes.md').write_text('my notes\n')
        before = files(self.project)
        status, out, err = self.run_verb('install', tools='cursor')
        self.assertEqual(status, 1)
        self.assertEqual(files(self.project), before)
        self.assertEqual((own / 'SKILL.md').read_text(),
                         '---\nname: machinome\n---\nmine\n')
        self.assertNotIn('wrote', out)
        self.assertIn(f'Error: {own} holds a skill machinome skills did not '
                      'write; nothing was written', err)
        self.assertIn('To replace it, run: machinome skills install --tools '
                      f'cursor --force {self.project}', err)

        out = self.install('cursor', force=True)
        self.assertIn('installed-by: machinome-skills',
                      (own / 'SKILL.md').read_text())
        self.assertEqual((own / 'notes.md').read_text(), 'my notes\n')
        self.assertEqual(files(self.project), sorted(
            copies('.cursor/skills') + ['.cursor/skills/machinome/notes.md']))

    def test_a_copy_the_command_wrote_is_rewritten(self):
        self.install('claude')
        skill = self.project / '.claude/skills/machinome'
        set_marker(skill / 'SKILL.md', '0.8.0')
        (skill / 'notes.md').write_text('mine\n')
        out = self.install('claude')
        self.assertIn(f'{skill}: 0.8.0 -> {VERSION}', out)
        self.assertIn(f'version: "{VERSION}"', (skill / 'SKILL.md').read_text())
        self.assertEqual((skill / 'notes.md').read_text(), 'mine\n')

    def test_a_path_that_is_not_a_directory(self):
        status, _out, err = self.run_verb(
            'install', tools='claude', path=str(self.project / 'absent'))
        self.assertEqual(status, 1)
        self.assertIn(f'Error: {self.project / "absent"} is not a directory',
                      err)


class InstallWithoutToolsTest(Scratch):
    """Without `--tools`: a prompt at a terminal, `agents` without one."""

    def answer(self, *answers):
        replies = iter(answers)

        def ask(prompt):
            print(prompt)
            try:
                return next(replies)
            except StopIteration:
                raise EOFError from None
        return patch('builtins.input', ask)

    def test_no_terminal_installs_for_agents(self):
        status, out, _err = self.run_verb('install')
        self.assertEqual(status, 0)
        self.assertIn('No --tools given and no terminal to ask: installing '
                      'for agents (.agents/skills/); name others with '
                      '--tools', out)
        self.assertEqual(files(self.project), copies('.agents/skills'))

    def test_ci_set_installs_for_agents(self):
        os.environ['CI'] = 'true'
        with self.answer():
            status, out, _err = self.run_verb('install', stdin=Terminal())
        self.assertEqual(status, 0)
        self.assertIn('no terminal to ask', out)
        self.assertEqual(files(self.project), copies('.agents/skills'))

    def marked_rows(self, out):
        return [line.split()[2] for line in out.splitlines()
                if re.match(r'\s*\*\s+\d+ ', line)]

    def test_enter_takes_the_detected_tools(self):
        (self.project / '.claude').mkdir()
        (self.project / '.cursor').mkdir()
        with self.answer(''):
            status, out, _err = self.run_verb('install', stdin=Terminal())
        self.assertEqual(status, 0)
        self.assertEqual(self.marked_rows(out), ['claude', 'cursor'])
        self.assertEqual(files(self.project), sorted(
            copies('.claude/skills') + copies('.cursor/skills')))

    def test_nothing_detected_marks_agents(self):
        with self.answer(''):
            status, out, _err = self.run_verb('install', stdin=Terminal())
        self.assertEqual(status, 0)
        self.assertEqual(self.marked_rows(out), ['agents'])
        self.assertEqual(files(self.project), copies('.agents/skills'))

    def test_the_marked_copies_come_before_the_detected_tools(self):
        self.install('cursor')
        (self.project / '.claude').mkdir()
        with self.answer(''):
            _status, out, _err = self.run_verb('install', stdin=Terminal())
        self.assertEqual(self.marked_rows(out), ['cursor'])

    def test_a_number_and_ids(self):
        number = [tool['id'] for tool in installer.registry()].index(
            'claude') + 1
        with self.answer(f'{number}, cursor'):
            status, _out, _err = self.run_verb('install', stdin=Terminal())
        self.assertEqual(status, 0)
        self.assertEqual(files(self.project), sorted(
            copies('.claude/skills') + copies('.cursor/skills')))

    def test_an_invalid_answer_is_named_and_asked_again(self):
        with self.answer('nope', '999', 'claude'):
            status, out, _err = self.run_verb('install', stdin=Terminal())
        self.assertEqual(status, 0)
        self.assertIn("unknown tool 'nope'", out)
        self.assertIn('no tool numbered 999', out)
        self.assertEqual(out.count('Tools (Enter for the marked ones'), 3)
        self.assertEqual(files(self.project), copies('.claude/skills'))

    def test_end_of_input_installs_nothing(self):
        with self.answer():
            status, _out, err = self.run_verb('install', stdin=Terminal())
        self.assertEqual(status, 1)
        self.assertIn('nothing was written', err)
        self.assertEqual(files(self.project), [])


class PersonalTest(Scratch):
    """`--personal`: each tool's directory under the user's home."""

    def test_a_personal_install(self):
        out = self.install('opencode,codex', personal=True)
        self.assertEqual(files(self.home), sorted(
            copies('.config/opencode/skills') + copies('.agents/skills')))
        self.assertEqual(files(self.project), [])
        self.assertIn(f'{self.home / ".config/opencode/skills"}/ (opencode)',
                      out)

    def test_a_tool_with_no_personal_directory_is_refused(self):
        status, out, err = self.run_verb('install', tools='trae',
                                         personal=True)
        self.assertEqual(status, 1)
        self.assertIn('Error: trae documents no personal skills directory; '
                      'install it into a project: machinome skills install '
                      '--tools trae <project>', err)
        self.assertEqual(files(self.home), [])

    def test_update_and_list_read_the_home(self):
        self.install('claude', personal=True)
        set_marker(self.home / '.claude/skills/machinome/SKILL.md', '0.8.0')
        status, out, _err = self.run_verb('update', personal=True)
        self.assertEqual(status, 0)
        self.assertIn(f'{self.home / ".claude/skills/machinome"}: 0.8.0 -> '
                      f'{VERSION}', out)
        status, out, _err = self.run_verb('list', personal=True)
        self.assertEqual(status, 0)
        self.assertIn('Installed in your home:', out)
        self.assertIn(f'{self.home / ".claude/skills/machinome"} (claude): '
                      f'{VERSION}, current', out)


class UpdateTest(Scratch):
    """`machinome skills update`."""

    def setUp(self):
        super().setUp()
        self.install('agents,claude')
        self.older = self.project / '.claude/skills/machinome'
        self.newer = self.project / '.agents/skills/machinome'
        self.foreign = self.project / '.cursor/skills/machinome-simulate'
        set_marker(self.older / 'SKILL.md', '0.8.0')
        set_marker(self.newer / 'SKILL.md', '99.0.0')
        self.foreign.mkdir(parents=True)
        (self.foreign / 'SKILL.md').write_text('mine\n')
        (self.newer / 'notes.md').write_text('kept\n')

    def test_an_older_copy_is_rewritten_alone(self):
        before = files(self.project)
        status, out, _err = self.run_verb('update')
        self.assertEqual(status, 0)
        self.assertIn(f'{self.older}: 0.8.0 -> {VERSION}', out)
        self.assertIn(f'version: "{VERSION}"',
                      (self.older / 'SKILL.md').read_text())
        self.assertEqual(out.count('  wrote '), 2)
        self.assertIn(f'{self.newer}: 99.0.0, newer than {VERSION}, left as '
                      'it is', out)
        self.assertIn('version: "99.0.0"', (self.newer / 'SKILL.md').read_text())
        self.assertIn(f'{self.foreign}: not written by machinome skills, left '
                      'as it is', out)
        self.assertEqual((self.foreign / 'SKILL.md').read_text(), 'mine\n')
        for current in ('.agents/skills/machinome-simulate',
                        '.claude/skills/machinome-simulate'):
            self.assertIn(f'{self.project / current}: {VERSION}, current', out)
        self.assertEqual(files(self.project), before)

    def test_force_rewrites_every_marked_copy_and_no_other(self):
        before = files(self.project)
        status, out, _err = self.run_verb('update', force=True)
        self.assertEqual(status, 0)
        self.assertIn(f'version: "{VERSION}"',
                      (self.newer / 'SKILL.md').read_text())
        self.assertIn(f'{self.newer}: 99.0.0 -> {VERSION}', out)
        self.assertEqual(out.count('  wrote '), 8)
        self.assertEqual((self.foreign / 'SKILL.md').read_text(), 'mine\n')
        self.assertEqual((self.newer / 'notes.md').read_text(), 'kept\n')
        self.assertEqual(files(self.project), before)

    def test_no_copy_says_how_to_install(self):
        empty = Path(tempfile.mkdtemp(prefix='skills-empty-'))
        self.addCleanup(shutil.rmtree, empty)
        status, out, _err = self.run_verb('update', path=str(empty))
        self.assertEqual(status, 0)
        self.assertIn(f'No copy of the machinome skills under {empty}; '
                      'install them with: machinome skills install', out)


class ListTest(Scratch):
    """`machinome skills list`."""

    def test_the_registry_and_no_copy(self):
        status, out, _err = self.run_verb('list')
        self.assertEqual(status, 0)
        for tool in installer.registry():
            with self.subTest(tool=tool['id']):
                self.assertRegex(
                    out, rf'(?m)^{re.escape(tool["id"])} +'
                    rf'{re.escape(tool["project"])} +'
                    rf'{re.escape(tool.get("personal", "-"))} +'
                    rf'{re.escape(tool["name"])}$')
        self.assertIn(f'Installed under {self.project}:\n  none\n', out)

    def test_the_copies_by_tool(self):
        self.install('agents')
        set_marker(self.project / '.agents/skills/machinome/SKILL.md', '0.1.0')
        status, out, _err = self.run_verb('list')
        self.assertEqual(status, 0)
        base = self.project / '.agents/skills'
        self.assertIn(f'{base / "machinome"} (agents, codex, pi): 0.1.0, older '
                      f'than {VERSION}', out)
        self.assertIn(f'{base / "machinome-simulate"} (agents, codex, pi): '
                      f'{VERSION}, current', out)


class TheCommandTest(unittest.TestCase):
    """`machinome skills` through the installed entry point."""

    def machinome(self, *arguments, cwd=None):
        return subprocess.run([str(MACHINOME), *arguments], cwd=cwd,
                              capture_output=True, text=True,
                              env={**os.environ, 'CI': 'true'})

    def test_the_help_lists_skills_with_its_docstring(self):
        run = self.machinome('-h')
        self.assertEqual(run.returncode, 0, run.stderr)
        from machinome.skills.cli import Skills
        summary = ' '.join(Skills.__doc__.split())
        self.assertIn(summary, ' '.join(run.stdout.split()))
        run = self.machinome('skills', '-h')
        self.assertEqual(run.returncode, 0, run.stderr)
        for verb in ('install', 'update', 'list'):
            with self.subTest(verb=verb):
                self.assertIn(verb, run.stdout)

    def test_install_through_the_entry_point(self):
        with tempfile.TemporaryDirectory() as project:
            run = self.machinome('skills', 'install', '--tools', 'claude',
                                 project)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertEqual(files(project), copies('.claude/skills'))

    def test_a_usage_error_exits_2(self):
        with tempfile.TemporaryDirectory() as project:
            run = self.machinome('skills', 'install', '--tools', 'x', project)
            self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
            self.assertIn("machinome skills install: error: unknown tool 'x'; "
                          'use all, none or ids from: agents, amazon-q, ',
                          run.stderr)
            self.assertEqual(files(project), [])

    def test_list_runs_alone(self):
        # The dispatch imports the command's module and its installer, and
        # no module of the framework's own commands.
        code = (
            'import sys\n'
            'from machinome.cli import manage\n'
            'try:\n'
            '    manage()\n'
            'except SystemExit as stop:\n'
            '    status = stop.code\n'
            'print("modules", sorted(name for name in sys.modules\n'
            '      if name.startswith(("machinome.manager.",\n'
            '                          "machinome.skills."))))\n'
            'print("status", status)\n')
        with tempfile.TemporaryDirectory() as project:
            run = subprocess.run(
                [sys.executable, '-c', code, 'skills', 'list', project],
                capture_output=True, text=True,
                env={**os.environ, 'CI': 'true'})
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("modules ['machinome.skills.cli', "
                      "'machinome.skills.installer']\nstatus 0\n", run.stdout)
