"""Layer 1: `machinome movie` (change `join-movie` of the machinome
repository), the command this package contributes through the entry-point
group `machinome.commands`: its eleven verbs, the Node it finds, the
dependencies `setup` installs and removes, the three forms of a source and the
viewer it films with.

Node is a fake here: a script named by `MACHINOME_NODE` that answers
`--version` as it is told, and otherwise records its arguments and working
directory and exits with the status it is told; an `npm` beside it records
its own and writes what `npm ci` would. The JavaScript directory is a scratch
copy, outside or inside a scratch npm workspace, given to the command module
by a bootstrap that runs it in a process of its own, so nothing here installs
or deletes anything of the package's.
"""

import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from conftest import PROJECT

PACKAGE = Path(__file__).resolve().parents[1]
JS = PACKAGE / 'machinome' / 'movie' / 'js'
MACHINOME = Path(sys.executable).parent / 'machinome'
VERBS = ('list', 'evaluate', 'watch', 'check', 'speech', 'preview', 'render',
         'build', 'live', 'review', 'setup')

FAKE_NODE = '''#!{python}
import json, os, sys
if sys.argv[1:] == ['--version']:
    print(os.environ.get('FAKE_NODE_VERSION', 'v22.11.0'))
    sys.exit(0)
with open(os.environ['FAKE_LOG'], 'a') as log:
    log.write(json.dumps({{'program': 'node', 'argv': sys.argv[1:],
                          'cwd': os.getcwd()}}) + '\\n')
sys.exit(int(os.environ.get('FAKE_NODE_STATUS', '0')))
'''

FAKE_NPM = '''#!{python}
import json, os, sys
with open(os.environ['FAKE_LOG'], 'a') as log:
    log.write(json.dumps({{'program': 'npm', 'argv': sys.argv[1:],
                          'cwd': os.getcwd()}}) + '\\n')
package = os.path.join(os.getcwd(), 'node_modules', 'esbuild')
os.makedirs(package)
with open(os.path.join(package, 'package.json'), 'w') as stream:
    stream.write('{{}}')
'''

#: Runs the command module with its JavaScript directory and, when given,
#: the viewer's report replaced, then exits as `machinome movie` would.
BOOTSTRAP = '''
import json, sys
from pathlib import Path
from machinome.movie import cli
from machinome.viewers import bundle
cli.JS = Path(sys.argv[1])
viewer = json.loads(sys.argv[2])
if viewer is not None:
    def describe():
        if 'absent' in viewer:
            raise bundle.ViewerUnavailable(viewer['absent'])
        return viewer
    bundle.describe = describe
from machinome.movie.__main__ import main
main(sys.argv[3:])
'''


def write_script(path, text):
    path.write_text(text.format(python=sys.executable))
    path.chmod(0o755)
    return path


@pytest.fixture
def fake(tmp_path):
    """A directory holding the fake `node` and `npm`, and their log."""
    tools = tmp_path / 'tools'
    tools.mkdir()
    write_script(tools / 'node', FAKE_NODE)
    write_script(tools / 'npm', FAKE_NPM)
    return tools


def log(tmp_path):
    path = tmp_path / 'log.jsonl'
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines()]


def javascript(directory, installed=True):
    """A copy of the package's JavaScript directory's manifests and command,
    with its dependencies marked installed or not."""
    directory.mkdir(parents=True)
    (directory / 'bin').mkdir()
    shutil.copy(JS / 'bin' / 'videomaker.mjs', directory / 'bin')
    for name in ('package.json', 'package-lock.json'):
        shutil.copy(JS / name, directory)
    if installed:
        (directory / 'node_modules' / 'esbuild').mkdir(parents=True)
        (directory / 'node_modules' / 'esbuild' / 'package.json').write_text('{}')
    return directory


def run(tmp_path, js, *arguments, node=None, viewer=None, cwd=None, env=None,
        path=None):
    environment = {'PATH': path if path is not None else '/usr/bin:/bin',
                   'FAKE_LOG': str(tmp_path / 'log.jsonl'),
                   'PYTHONDONTWRITEBYTECODE': '1', 'HOME': str(tmp_path)}
    if node is not None:
        environment['MACHINOME_NODE'] = str(node)
    environment.update(env or {})
    return subprocess.run(
        [sys.executable, '-c', BOOTSTRAP, str(js), json.dumps(viewer),
         *map(str, arguments)],
        capture_output=True, text=True, cwd=cwd or tmp_path, env=environment)


@pytest.fixture
def copy(tmp_path):
    target = tmp_path / 'project'
    shutil.copytree(PROJECT, target,
                    ignore=shutil.ignore_patterns('_build', '__pycache__'))
    return target


VIEWER = {'path': '/viewer/machinome-viewer.js', 'apiVersion': 29}


def test_the_help_lists_the_eleven_verbs():
    done = subprocess.run([str(MACHINOME), 'movie', '-h'], capture_output=True,
                          text=True)
    assert done.returncode == 0, done.stderr
    for verb in VERBS:
        assert verb in done.stdout, verb
    listed = subprocess.run([str(MACHINOME), '-h'], capture_output=True,
                            text=True)
    assert 'Film a machine' in ' '.join(listed.stdout.split())


def test_python_m_runs_the_same_parser():
    command = subprocess.run([str(MACHINOME), 'movie', '-h'],
                             capture_output=True, text=True)
    module = subprocess.run([sys.executable, '-m', 'machinome.movie', '-h'],
                            capture_output=True, text=True)
    assert module.returncode == 0, module.stderr
    assert module.stdout == command.stdout


def test_no_node_on_the_path_is_refused(tmp_path):
    js = javascript(tmp_path / 'js')
    empty = tmp_path / 'empty'
    empty.mkdir()
    done = run(tmp_path, js, 'speech', 'film.yaml', path=str(empty))
    assert done.returncode == 1
    assert done.stderr == ('Error: machinome movie needs Node 22 or newer: none '
                           'is on the PATH; install Node 22, or name it with '
                           'MACHINOME_NODE\n')


def test_a_node_that_cannot_run_is_named(tmp_path):
    js = javascript(tmp_path / 'js')
    absent = tmp_path / 'no-such-node'
    done = run(tmp_path, js, 'speech', 'film.yaml', node=absent)
    assert done.returncode == 1
    assert str(absent) in done.stderr and 'MACHINOME_NODE' in done.stderr
    assert done.stderr.count('\n') == 1


def test_an_older_node_is_named_with_its_version(tmp_path, fake):
    js = javascript(tmp_path / 'js')
    for verb in (('speech', 'film.yaml'), ('setup',)):
        done = run(tmp_path, js, *verb, node=fake / 'node',
                   env={'FAKE_NODE_VERSION': 'v20.11.0'})
        assert done.returncode == 1, verb
        assert str(fake / 'node') in done.stderr and 'v20.11.0' in done.stderr
        assert 'Node 22' in done.stderr and 'MACHINOME_NODE' in done.stderr
        assert done.stderr.count('\n') == 1
    assert log(tmp_path) == []


def test_missing_dependencies_name_setup(tmp_path, fake):
    js = javascript(tmp_path / 'js', installed=False)
    done = run(tmp_path, js, 'check', 'film.yaml', node=fake / 'node',
               viewer=VIEWER)
    assert done.returncode == 1
    assert done.stderr == ('Error: the Node dependencies of machinome movie are '
                           'not installed; run: machinome movie setup\n')
    assert log(tmp_path) == []


def workspace(tmp_path, installed=False):
    root = tmp_path / 'checkout'
    js = javascript(root / 'packages' / 'movie' / 'js', installed=installed)
    (root / 'package.json').write_text(json.dumps(
        {'private': True, 'workspaces': ['packages/movie/js']}))
    return root, js


def test_missing_dependencies_in_a_workspace_name_its_root(tmp_path, fake):
    root, js = workspace(tmp_path)
    done = run(tmp_path, js, 'check', 'film.yaml', node=fake / 'node',
               viewer=VIEWER)
    assert done.returncode == 1
    assert done.stderr == ('Error: the Node dependencies of machinome movie are '
                           f'not installed; run: npm ci in {root}\n')


def listing(directory):
    return sorted(str(path.relative_to(directory))
                  for path in directory.rglob('*'))


def test_setup_refuses_in_a_workspace_and_writes_nothing(tmp_path, fake):
    root, js = workspace(tmp_path)
    before = listing(root)
    for arguments in (('setup',), ('setup', '--remove')):
        done = run(tmp_path, js, *arguments, node=fake / 'node')
        assert done.returncode == 1, arguments
        assert done.stderr == (
            f'Error: this machinome-movie is the source in the npm workspace '
            f'at {root}; its dependencies are installed by npm ci there\n')
    assert listing(root) == before
    assert log(tmp_path) == []


def test_setup_refuses_a_linked_node_modules_above_and_writes_nothing(
        tmp_path, fake):
    elsewhere = tmp_path / 'elsewhere'
    elsewhere.mkdir()
    above = tmp_path / 'site'
    js = javascript(above / 'machinome' / 'movie' / 'js', installed=False)
    (above / 'node_modules').symlink_to(elsewhere)
    before = listing(above), listing(elsewhere)
    for arguments in (('setup',), ('setup', '--remove')):
        done = run(tmp_path, js, *arguments, node=fake / 'node')
        assert done.returncode == 1, arguments
        assert str(above / 'node_modules') in done.stderr
        assert 'symbolic link' in done.stderr
        assert done.stderr.count('\n') == 1
    assert (listing(above), listing(elsewhere)) == before
    assert log(tmp_path) == []


def test_setup_installs_into_the_package_and_remove_deletes(tmp_path, fake):
    js = javascript(tmp_path / 'site' / 'machinome' / 'movie' / 'js',
                    installed=False)
    done = run(tmp_path, js, 'setup', node=fake / 'node')
    assert done.returncode == 0, done.stderr
    (npm,) = log(tmp_path)
    assert npm == {'program': 'npm',
                   'argv': ['ci', '--omit=dev', '--no-audit', '--no-fund'],
                   'cwd': str(js)}
    assert (js / 'node_modules' / 'esbuild' / 'package.json').is_file()
    words = ' '.join(done.stdout.split())
    assert str(js / 'node_modules') in words
    assert (f"{fake / 'node'} {js / 'node_modules' / 'playwright' / 'cli.js'} "
            'install chromium') in words
    assert 'FFmpeg' in words
    removed = run(tmp_path, js, 'setup', '--remove', node=fake / 'node')
    assert removed.returncode == 0, removed.stderr
    assert not (js / 'node_modules').exists()
    assert str(js / 'node_modules') in removed.stdout
    again = run(tmp_path, js, 'setup', '--remove', node=fake / 'node')
    assert again.returncode == 0, again.stderr
    assert str(js / 'node_modules') in again.stdout


def test_a_film_verb_needs_the_viewer(tmp_path, fake):
    js = javascript(tmp_path / 'js')
    remedy = ('The browser viewer is not installed. Install it with: '
              'pip install "machinome[viewer]"')
    done = run(tmp_path, js, 'check', 'film.yaml', node=fake / 'node',
               viewer={'absent': remedy})
    assert done.returncode == 1
    assert done.stderr == ('Error: machinome movie check needs the browser '
                           f'viewer: {remedy}\n')
    assert log(tmp_path) == []
    spoken = run(tmp_path, js, 'speech', 'film.yaml', node=fake / 'node',
                 viewer={'absent': remedy})
    assert spoken.returncode == 0, spoken.stderr
    (node,) = log(tmp_path)
    assert '--viewer' not in node['argv']


def test_a_directory_needs_a_movie_and_a_file_takes_none(tmp_path, fake, copy):
    js = javascript(tmp_path / 'js')
    done = run(tmp_path, js, 'check', copy, node=fake / 'node', viewer=VIEWER)
    assert done.returncode == 1
    assert str(copy) in done.stderr and 'movie' in done.stderr
    assert done.stderr.count('\n') == 1
    film = tmp_path / 'film.yaml'
    film.write_text('format: 1\n')
    done = run(tmp_path, js, 'check', film, 'tour', node=fake / 'node',
               viewer=VIEWER)
    assert done.returncode == 1
    assert 'tour' in done.stderr and done.stderr.count('\n') == 1
    assert log(tmp_path) == []


def test_a_project_and_a_movie_are_evaluated_first(tmp_path, fake, copy):
    js = javascript(tmp_path / 'js')
    work = tmp_path / 'work'
    work.mkdir()
    done = run(tmp_path, js, 'check', copy, 'minimal', node=fake / 'node',
               viewer=VIEWER, cwd=work)
    assert done.returncode == 0, done.stderr
    document = copy / 'videos' / 'minimal' / '_build' / 'movie.json'
    assert done.stdout.strip() == str(document)
    assert json.loads(document.read_text())['format'] == 'machinome-movie/0.2'
    (node,) = log(tmp_path)
    assert node == {'program': 'node',
                    'argv': [str(js / 'bin' / 'videomaker.mjs'), 'check',
                             str(document), '--viewer', VIEWER['path']],
                    'cwd': str(work)}


def test_the_options_pass_as_given_and_the_viewer_is_the_report_s(
        tmp_path, fake):
    js = javascript(tmp_path / 'js')
    cases = (
        (('render', 'film.yaml', '--width', '640', '--fps', '24',
          '--silent'),
         ['render', 'film.yaml', '--width', '640', '--fps', '24', '--silent',
          '--viewer', VIEWER['path']]),
        (('live', 'movie.json', '--width', '800', '--port', '8123', '--poll',
          '250', '--open'),
         ['live', 'movie.json', '--width', '800', '--port', '8123', '--poll',
          '250', '--open', '--viewer', VIEWER['path']]),
        (('speech', 'film.yaml', '--silent'), ['speech', 'film.yaml',
                                               '--silent']),
        (('review', 'out/manifest.json'), ['review', 'out/manifest.json']),
    )
    for arguments, expected in cases:
        (tmp_path / 'log.jsonl').unlink(missing_ok=True)
        done = run(tmp_path, js, *arguments, node=fake / 'node', viewer=VIEWER)
        assert done.returncode == 0, (arguments, done.stderr)
        (node,) = log(tmp_path)
        assert node['argv'] == [str(js / 'bin' / 'videomaker.mjs'), *expected]


def test_the_node_process_s_status_is_the_command_s(tmp_path, fake):
    js = javascript(tmp_path / 'js')
    done = run(tmp_path, js, 'preview', 'film.yaml', node=fake / 'node',
               viewer=VIEWER, env={'FAKE_NODE_STATUS': '3'})
    assert done.returncode == 3


def test_node_is_found_on_the_path(tmp_path, fake):
    js = javascript(tmp_path / 'js')
    done = run(tmp_path, js, 'speech', 'film.yaml',
               path=f'{fake}:/usr/bin:/bin')
    assert done.returncode == 0, done.stderr
    (node,) = log(tmp_path)
    assert node['argv'][1:] == ['speech', 'film.yaml']


def test_a_movie_whose_project_lacks_an_extra_is_refused_in_one_line(
        tmp_path, fake):
    project = tmp_path / 'project'
    (project / 'videos' / 'film').mkdir(parents=True)
    (project / 'pyproject.toml').write_text(
        '[tool.machinome.movies]\nfilm = "videos.film.movie:Film"\n')
    for package in (project / 'videos', project / 'videos' / 'film'):
        (package / '__init__.py').write_text('')
    (project / 'videos' / 'film' / 'movie.py').write_text(textwrap.dedent('''
        from machinome.extras import ExtraUnavailable
        raise ExtraUnavailable('cadquery', 'videos.film.movie', 'cadquery')
    '''))
    js = javascript(tmp_path / 'js')
    for verb in ('preview', 'evaluate'):
        done = run(tmp_path, js, verb, project, 'film', node=fake / 'node',
                   viewer=VIEWER)
        assert done.returncode == 1, verb
        assert done.stderr.startswith(
            f'Error: machinome movie {verb} needs the cadquery extra: '), \
            done.stderr
        assert done.stderr.count('\n') == 1, done.stderr
        assert 'Traceback' not in done.stderr
    assert log(tmp_path) == []
