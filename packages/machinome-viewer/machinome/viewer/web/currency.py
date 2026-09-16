# solid-node-viewer - the browser viewer for solid-node models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

"""Keep the built bundle current with the sources it is built from.

`dist/solid-widget.js` is this package's one published artifact, and it is
a build product of `widget/src/`, `package.json`, `build.mjs` and
`tsconfig.json`. In a wheel those are the same instant by construction --
packaging builds the bundle and the sources are not shipped. In a SOURCE
CHECKOUT they are two instants, and until ADR-059 nothing here compared
them: the lookup read `package.json` at the moment it was asked and handed
out the path of a file built from whatever that file said whenever someone
last ran a build.

That is not theoretical. A maker was told a correct version 7 document
"declares document version 7, which this viewer does not render", by a
bundle built the evening before the cycle that reads version 7 landed.

So the four exits that hand the bundle out -- the entry point, the
development server's routes, the capture and packaging -- make it current
first. Like `bundle`, this module imports only the standard library, so
asking costs no browser bundle and no web framework.
"""

import logging
import os
import subprocess
from pathlib import Path

try:  # pragma: no cover - present on every platform this package targets
    import fcntl
except ImportError:  # pragma: no cover - Windows has no flock
    fcntl = None

logger = logging.getLogger('viewer.currency')

PACKAGE_DIR = Path(__file__).parent
WIDGET_DIR = PACKAGE_DIR / 'widget'
#: The published artifact's name is a compatibility contract: `solid export`,
#: the development server's `/_viewer/bundle.js` and the capture page all
#: copy this one file.
BUNDLE_NAME = 'solid-widget.js'
LOCK_NAME = '.build.lock'

#: The files the bundle is built from. `node_modules` is deliberately NOT
#: among them: a dependency change is an INSTALL, which this path refuses to
#: perform (see `BUILD_COMMAND`), and walking it would cost orders of
#: magnitude more than the check it serves.
SOURCE_DIR = 'src'
DECLARED_INPUTS = ('package.json', 'build.mjs', 'tsconfig.json')

#: The rebuild BUILDS. It does not install, and no future edit may make it.
#:
#: In this workspace a worktree's `node_modules` is a symlink to the primary
#: checkout's, and running `npm ci` through that symlink EMPTIED the
#: primary's dependencies. An automatic repair that can destroy a sibling
#: checkout while answering a question is worse than the staleness it fixes,
#: so absent dependencies are REPORTED with the remedy, never installed.
BUILD_COMMAND = ('npm', 'run', 'build')
INSTALL_REMEDY = 'npm ci && npm run build'


class BundleStale(RuntimeError):
    """The built bundle is older than the sources, and was not repaired.

    A sibling of `BundleMissing`: a named artifact, a reason, a remedy, and
    no substitution. A stale bundle is a broken installation, and answering
    from it is how a correct document came to be blamed for a stale
    renderer.
    """


def bundle_file(widget=WIDGET_DIR):
    """The built bundle inside a widget directory."""
    return Path(widget) / 'dist' / BUNDLE_NAME


def is_source_checkout(widget=WIDGET_DIR):
    """Whether this installation carries the widget's sources.

    A wheel carries the bundle, the pages and `package.json` -- but no
    `src/` and no `build.mjs`. So their presence is the question, and in a
    wheel the whole check costs one `is_file()` (design D9).
    """
    widget = Path(widget)
    return (widget / 'build.mjs').is_file() and (widget / SOURCE_DIR).is_dir()


def build_inputs(widget=WIDGET_DIR):
    """Every file the bundle is built from, in no particular order."""
    widget = Path(widget)
    for path in sorted((widget / SOURCE_DIR).rglob('*')):
        if path.is_file():
            yield path
    for name in DECLARED_INPUTS:
        path = widget / name
        if path.is_file():
            yield path


def newest_input(widget=WIDGET_DIR):
    """The most recently modified build input and its time, or `(None, None)`."""
    newest, newest_ns = None, None
    for path in build_inputs(widget):
        moment = path.stat().st_mtime_ns
        if newest_ns is None or moment > newest_ns:
            newest, newest_ns = path, moment
    return newest, newest_ns


def newest_input_ns(widget=WIDGET_DIR):
    """The most recent build-input time in integer nanoseconds, or `None`."""
    return newest_input(widget)[1]


def is_stale(widget=WIDGET_DIR):
    """Whether the built bundle is older than the sources beside it.

    Integer nanoseconds, never floats -- the comparison solid-node settled
    for its own artifacts, because a float comparison on a coarse
    filesystem is exactly the near-miss that leaves a stale artifact nobody
    can reproduce. Equal times mean CURRENT: the tolerant direction.
    """
    widget = Path(widget)
    if not is_source_checkout(widget):
        return False
    built = bundle_file(widget)
    if not built.is_file():
        # An absent bundle is `BundleMissing`'s business, with its own
        # remedy. There is nothing to compare and nothing to repair.
        return False
    _, newest_ns = newest_input(widget)
    return newest_ns is not None and newest_ns > built.stat().st_mtime_ns


def ensure_current(widget=WIDGET_DIR):
    """Make the built bundle current, or raise `BundleStale` saying why not.

    Returns silently -- and costs one `is_file()` -- for an installed
    distribution, and a newest-mtime scan of the build inputs (a median
    2.88 ms over the 77 files of this widget) for a checkout that is
    already current.
    """
    widget = Path(widget)
    if not is_stale(widget):
        return
    built = bundle_file(widget)
    with _build_lock(widget):
        # Another process may have rebuilt it while we waited.
        if not is_stale(widget):
            return
        newest, newest_ns = newest_input(widget)
        _require_dependencies(widget, built, newest)
        logger.info('viewer bundle %s is older than %s; rebuilding with %s',
                    built, newest, ' '.join(BUILD_COMMAND))
        try:
            finished = subprocess.run(
                BUILD_COMMAND, cwd=str(widget),
                capture_output=True, text=True)
        except OSError as error:
            # FileNotFoundError included: no npm on PATH.
            raise _stale(built, newest, f'{BUILD_COMMAND[0]} could not be run '
                                        f'({error})') from error
        if finished.returncode != 0:
            raise _stale(built, newest,
                         f'{" ".join(BUILD_COMMAND)} failed with status '
                         f'{finished.returncode}:\n{_tail(finished)}')
        logger.info('viewer bundle rebuilt: %s', built)


def _require_dependencies(widget, built, newest):
    if not (widget / 'node_modules').is_dir():
        raise _stale(built, newest,
                     'the widget\'s dependencies are not installed, and a '
                     'rebuild never installs them')


def _stale(built, newest, reason):
    return BundleStale(
        f'Viewer bundle {built} is older than {newest} and was not rebuilt: '
        f'{reason}. The bundle a caller would receive is not the one this '
        f'installation declares. Remedy: cd {built.parent.parent} && '
        f'{INSTALL_REMEDY}.')


def _tail(finished, lines=20):
    output = (finished.stderr or '') + (finished.stdout or '')
    return '\n'.join(output.splitlines()[-lines:])


class _build_lock:
    """Serialize rebuilds so no caller can observe a torn bundle.

    Two `esbuild` runs writing one `outfile` can leave a partial file, and
    several processes can ask at once -- a shop opening two sessions, a
    development server and a capture, `check-dist` beside either. Where
    `fcntl` is unavailable the rebuild proceeds unlocked: the lock protects
    a concurrency case, and its absence must not make a single-process
    rebuild impossible.
    """

    def __init__(self, widget):
        self.path = bundle_file(widget).parent / LOCK_NAME
        self.handle = None

    def __enter__(self):
        if fcntl is None:  # pragma: no cover - Windows has no flock
            logger.debug('no fcntl on this platform; rebuilding unlocked')
            return self
        os.makedirs(self.path.parent, exist_ok=True)
        self.handle = open(self.path, 'w')
        fcntl.flock(self.handle, fcntl.LOCK_EX)
        return self

    def __exit__(self, *error):
        if self.handle is not None:
            fcntl.flock(self.handle, fcntl.LOCK_UN)
            self.handle.close()
            self.handle = None
        return False
