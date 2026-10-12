"""`machinome movie`, the command this package contributes through the
entry-point group `machinome.commands` (ADR-189, change `join-movie`).

`list`, `evaluate` and `watch` run in Python. `check`, `speech`, `preview`,
`render`, `build`, `live` and `review` run the Node side, `js/bin/videomaker.mjs`,
with the Node named by `MACHINOME_NODE` or found on the PATH, 22 or newer;
the film verbs give it the bundle of the viewer installed beside the
framework. `setup` installs the Node side's dependencies into `js/node_modules`
of this package, from its own lock, and `setup --remove` deletes them.

The module imports the standard library alone at its import, so `machinome
-h` pays for it only the class; a verb imports what it runs when it runs.
"""

import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

#: The Node side, package data of this package.
JS = Path(__file__).resolve().parent / 'js'

#: The oldest Node the Node side runs on.
NODE_MAJOR = 22

#: The verbs the Node side runs, and those of them that draw on the viewer.
NODE_VERBS = ('check', 'speech', 'preview', 'render', 'build', 'live', 'review')
VIEWER_VERBS = ('check', 'preview', 'render', 'build', 'live')

#: What a source is, in the words of every verb that takes one.
SOURCE = ('an episode (.yaml), a movie document (.json), or a project '
          'directory followed by the movie name')

DEFAULT_OUT = 'where to write it (default <movie dir>/_build/movie.json)'


class Refusal(Exception):
    """A refusal of the command: one line on standard error, exit 1."""


class Movie:
    """Film a machine: evaluate a project's movies, then check, voice,
    preview, render, build, serve and review them."""

    needs_node = False

    def add_arguments(self, parser):
        verbs = parser.add_subparsers(dest='verb', required=True,
                                      metavar='VERB')
        listing = verbs.add_parser('list', help="print a project's movies table")
        listing.add_argument('project', metavar='PROJECT')
        evaluating = verbs.add_parser('evaluate', help='write a movie document')
        evaluating.add_argument('project', metavar='PROJECT')
        evaluating.add_argument('movie', metavar='MOVIE')
        evaluating.add_argument('--out', metavar='FILE', help=DEFAULT_OUT)
        watching = verbs.add_parser(
            'watch', help='evaluate a movie, then again whenever a file of its '
                          'project changes, until interrupted')
        watching.add_argument('project', metavar='PROJECT')
        watching.add_argument('movie', metavar='MOVIE')
        watching.add_argument('--out', metavar='FILE', help=DEFAULT_OUT)
        watching.add_argument('--interval', metavar='SECONDS', default='0.5',
                              help='seconds between two looks at the files '
                                   '(default 0.5)')
        for name, help in (
                ('check', 'check a film: its sources, narration, takes and '
                          'stage'),
                ('speech', 'generate the narration a film still lacks'),
                ('preview', 'draw a film\'s storyboard and its highlight '
                            'checks'),
                ('render', 'render a film to video'),
                ('build', 'generate the narration a film lacks, then render it '
                          'with its audio'),
                ('live', 'serve a film at a local address and reload it when '
                         'its inputs change, until interrupted')):
            verb = verbs.add_parser(name, help=help)
            verb.add_argument('source', metavar='SOURCE', help=SOURCE)
            verb.add_argument('movie', metavar='MOVIE', nargs='?',
                              help='the movie, after a project directory')
            verb.add_argument('--width', metavar='N',
                              help='the frame width in pixels')
            if name == 'live':
                verb.add_argument('--port', metavar='N',
                                  help='the port to serve at (default: any '
                                       'free one)')
                verb.add_argument('--poll', metavar='MS',
                                  help='milliseconds between two looks at the '
                                       'inputs')
                verb.add_argument('--open', action='store_true',
                                  help='open the address in a browser')
            else:
                verb.add_argument('--fps', metavar='N',
                                  help='frames per second')
                verb.add_argument('--silent', action='store_true',
                                  help='without narration')
        review = verbs.add_parser(
            'review', help="make the review pack of a rendered film's manifest")
        review.add_argument('manifest', metavar='MANIFEST')
        setup = verbs.add_parser(
            'setup', help="install the Node side's dependencies into this "
                          'package')
        setup.add_argument('--remove', action='store_true',
                           help='delete them instead')

    def handle(self, args):
        try:
            if args.verb in NODE_VERBS:
                code = self.node(args)
            else:
                code = getattr(self, args.verb)(args)
        except Refusal as refusal:
            sys.stderr.write(f'Error: {refusal}\n')
            code = 1
        except MovieRefusal as refusal:
            sys.stderr.write(f'machinome-movie: {refusal}\n')
            code = 1
        sys.exit(code)

    # Python's verbs.

    def list(self, args):
        from machinome.movie.names import MovieError
        from machinome.movie.project import movies
        try:
            table = movies(args.project)
        except MovieError as refusal:
            raise MovieRefusal(refusal) from None
        for name, reference in table.items():
            print(f'{name}\t{reference}')
        return 0

    def evaluate(self, args):
        print(evaluated(args.verb, args.project, args.movie, args.out))
        return 0

    def watch(self, args):
        from machinome.movie.watch import watch
        interval = seconds(args.interval)
        # Each evaluation prints the path or the refusal; an interrupt ends it.
        try:
            watch(args.project, args.movie, out=args.out, interval=interval)
        except KeyboardInterrupt:
            pass
        return 0

    def setup(self, args):
        refuse_outside_an_installed_package()
        target = JS / 'node_modules'
        if args.remove:
            if target.exists():
                shutil.rmtree(target)
                print(f'Removed {target}')
            else:
                print(f'Nothing to remove: {target} does not exist')
            return 0
        node = find_node()
        npm = (shutil.which('npm', path=str(Path(node).parent))
               or shutil.which('npm'))
        if not npm:
            raise Refusal(f'machinome movie setup needs npm: none is beside '
                          f'{node} or on the PATH')
        print(f'Installing the Node dependencies of machinome movie into '
              f'{target} with {npm} ci --omit=dev', flush=True)
        done = subprocess.run([npm, 'ci', '--omit=dev', '--no-audit',
                               '--no-fund'], cwd=JS)
        if done.returncode:
            return done.returncode
        print('Then install Chromium for Playwright, a second step: '
              f"{node} {target / 'playwright' / 'cli.js'} install chromium")
        print("FFmpeg is the system's: install it with your system's package "
              'manager.')
        return 0

    # The Node side's verbs.

    def node(self, args):
        if not (JS / 'node_modules' / 'esbuild' / 'package.json').is_file():
            root = workspace_root()
            raise Refusal('the Node dependencies of machinome movie are not '
                          'installed; run: '
                          + (f'npm ci in {root}' if root
                             else 'machinome movie setup'))
        node = find_node()
        viewer = installed_viewer(args.verb) if args.verb in VIEWER_VERBS \
            else None
        command = [node, str(JS / 'bin' / 'videomaker.mjs'), args.verb]
        if args.verb == 'review':
            command.append(args.manifest)
        else:
            command.append(self.source(args))
            for option in ('width', 'fps', 'port', 'poll'):
                value = getattr(args, option, None)
                if value is not None:
                    command += [f'--{option}', value]
            for flag in ('silent', 'open'):
                if getattr(args, flag, False):
                    command.append(f'--{flag}')
        if viewer is not None:
            command += ['--viewer', viewer]
        sys.stdout.flush()
        child = subprocess.Popen(command)
        while True:
            try:
                return child.wait()
            except KeyboardInterrupt:
                # The terminal interrupts the Node process too; it ends the
                # session and its status is the command's.
                continue

    def source(self, args):
        """The file the Node side is given: the source, or the document a
        project's movie evaluates to, its path printed."""
        if os.path.isdir(args.source):
            if not args.movie:
                raise Refusal(f'{args.source} is a project directory; name the '
                              f'movie after it: machinome movie {args.verb} '
                              f'{args.source} MOVIE')
            out = evaluated(args.verb, args.source, args.movie)
            print(out)
            return out
        if args.movie:
            raise Refusal(f'{args.movie} follows {args.source}, which is not a '
                          'project directory; a movie name follows a project '
                          'directory, and an episode or a movie document stands '
                          'alone')
        return args.source


class MovieRefusal(Exception):
    """A refusal of the movie's own evaluation, written as the package always
    wrote it: `machinome-movie: <refusal>`, exit 1."""


def evaluated(verb, project, movie, out=None):
    """Evaluate `movie` of `project` to its document, in this process; the
    document's absolute path. A movie whose project needs an absent extra is
    answered by the extra, as the framework answers a command."""
    from machinome.extras import ExtraUnavailable
    from machinome.movie.evaluate import evaluate, write
    from machinome.movie.names import MovieError, module_directory
    from machinome.movie.project import load_movie
    try:
        declared = load_movie(project, movie)
        out = out or os.path.join(module_directory(declared), '_build',
                                  'movie.json')
        write(evaluate(declared, name=movie, out=out), out)
    except MovieError as refusal:
        raise MovieRefusal(refusal) from None
    except ExtraUnavailable as absent:
        raise Refusal(f'machinome movie {verb} needs the {absent.extra} extra: '
                      f'{absent}') from None
    return os.path.abspath(out)


def seconds(text):
    try:
        value = float(text)
    except ValueError:
        value = math.nan
    if not (math.isfinite(value) and value > 0):
        raise MovieRefusal(f'--interval {text} is not a positive number of '
                           'seconds')
    return value


def find_node():
    """The Node named by `MACHINOME_NODE`, else `node` on the PATH, when it
    runs and is 22 or newer."""
    named = os.environ.get('MACHINOME_NODE')
    node = named or shutil.which('node')
    if not node:
        raise Refusal(f'machinome movie needs Node {NODE_MAJOR} or newer: none '
                      f'is on the PATH; install Node {NODE_MAJOR}, or name it '
                      'with MACHINOME_NODE')
    where = f'{node} (named by MACHINOME_NODE)' if named else node
    try:
        version = subprocess.run([node, '--version'], capture_output=True,
                                 text=True, check=True).stdout.strip()
        major = int(version.lstrip('v').split('.')[0])
    except (OSError, ValueError, subprocess.CalledProcessError) as failure:
        reason = ' '.join(str(failure).split()) or type(failure).__name__
        raise Refusal(f'machinome movie cannot run Node at {where}: {reason}; '
                      f'install Node {NODE_MAJOR}, or name it with '
                      'MACHINOME_NODE') from None
    if major < NODE_MAJOR:
        raise Refusal(f'machinome movie needs Node {NODE_MAJOR} or newer; '
                      f'{where} is {version}; install Node {NODE_MAJOR}, or '
                      'name it with MACHINOME_NODE')
    return node


def installed_viewer(verb):
    """The bundle of the web viewer installed beside the framework, asked
    through the seam of viewers as `machinome develop` asks it; only the web
    viewer draws a film, so no project's viewer is read."""
    from machinome import viewer as viewers
    try:
        web = viewers.require('web', 'embed', f'machinome movie {verb}')
        web.describe()
        return str(web.files()['machinome-viewer.js'])
    except (ImportError, LookupError, RuntimeError, OSError) as absent:
        raise Refusal(f'machinome movie {verb} needs the browser viewer: '
                      f'{absent}') from None


def workspace_root():
    """The npm workspace whose root `package.json` names the JavaScript
    directory among its `workspaces`, or None: a source checkout."""
    here = JS.resolve()
    for parent in here.parents:
        manifest = parent / 'package.json'
        if not manifest.is_file():
            continue
        try:
            members = json.loads(manifest.read_text()).get('workspaces') or []
        except (OSError, ValueError, AttributeError):
            continue
        if isinstance(members, dict):
            members = members.get('packages') or []
        for member in members:
            if any(found.resolve() == here
                   for found in parent.glob(str(member))):
                return parent
    return None


def refuse_outside_an_installed_package():
    """`setup` writes only into an installed copy's own `node_modules`."""
    root = workspace_root()
    if root is not None:
        raise Refusal(f'this machinome-movie is the source in the npm '
                      f'workspace at {root}; its dependencies are installed by '
                      'npm ci there')
    for directory in (JS, *JS.parents):
        candidate = directory / 'node_modules'
        if candidate.is_symlink():
            raise Refusal(f'{candidate} is a symbolic link; machinome movie '
                          'setup installs nowhere npm would write through it')
