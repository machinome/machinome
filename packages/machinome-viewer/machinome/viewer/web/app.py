# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Bundle a model's own app with the viewer's toolchain (OpenSpec
`show-a-models-own-app`, design Decision 11).

The framework asks, through its seam, for the operation `bundle`; this
module answers it. It runs the widget's `app-build.mjs` with Node, which
bundles the app's own TypeScript, JavaScript and CSS with the viewer's own
esbuild, its own React and React DOM and the helper
`@machinome/viewer/app` into one script and at most one stylesheet, named
by their content.

In this release an app is bundled only from a source checkout of the
repository whose JavaScript dependencies are installed. An installed viewer
(a wheel) carries no app toolchain, and says so; a checkout whose
dependencies are absent names them and the command that installs them; and
nothing here ever installs anything, as `currency` promises for the
viewer's own bundle. Like `currency`, this module imports only the
standard library.
"""

import json
import shutil
import subprocess
from pathlib import Path

from machinome.viewer.web.currency import WIDGET_DIR

#: The script that bundles, and the helper's sources, beside the widget's
#: own sources: neither is carried by a wheel.
BUILD_SCRIPT = 'app-build.mjs'
HELPER_DIR = 'app'

#: The JavaScript packages the bundling needs, found from the widget up to
#: the filesystem's root as Node finds them.
DEPENDENCIES = ('esbuild', 'react', 'react-dom')


def _viewer_version(widget):
    try:
        return json.loads((Path(widget) / 'package.json').read_text())[
            'version']
    except (OSError, ValueError, KeyError):
        from machinome.viewer.web import __version__
        return __version__


def _missing_dependencies(widget):
    """The packages of `DEPENDENCIES` no `node_modules` from `widget` up
    holds: the walk `currency._build_program_installed` makes, extended."""
    widget = Path(widget)
    directories = (widget, *widget.resolve().parents)
    return [package for package in DEPENDENCIES
            if not any((directory / 'node_modules' / package).is_dir()
                       for directory in directories)]


def _install_root(widget):
    """Where `npm ci` installs the widget's dependencies: the npm workspace
    naming it, or the widget's own directory outside one."""
    try:
        from machinome.viewer.web.packaging import workspace_root
    except ImportError:  # setuptools absent: no workspace to name
        return Path(widget)
    return workspace_root(widget) or Path(widget)


def refusal(widget=WIDGET_DIR):
    """Why an app cannot be bundled from this installation, or None."""
    widget = Path(widget)
    if not (widget / BUILD_SCRIPT).is_file() or not (widget / HELPER_DIR).is_dir():
        return (f'this machinome-viewer {_viewer_version(widget)} was installed '
                "without the toolchain that bundles a model's app; in this "
                'release an app is bundled only from a source checkout of the '
                'machinome repository with its JavaScript dependencies '
                'installed')
    missing = _missing_dependencies(widget)
    if missing:
        return ("the viewer's JavaScript dependencies are not installed "
                f'({", ".join(missing)}); install them with npm ci in '
                f'{_install_root(widget)}')
    if shutil.which('node') is None:
        return "bundling a model's app needs Node.js, and none is on the PATH"
    return None


def bundle_app(entry, root, output_dir, widget=WIDGET_DIR):
    """Bundle the app whose entry file is `entry`, every file it reads
    inside the project's `root`, into `output_dir`.

    Returns ``{'script': 'app-<h>.js', 'stylesheet': 'app-<h>.css' or None,
    'inputs': [<absolute paths of the project files read>]}``, the names
    relative to `output_dir`; raises `machinome.viewer.ViewerError` with the
    sentence, having written nothing, when it cannot.
    """
    from machinome.viewer import ViewerError

    widget = Path(widget)
    reason = refusal(widget)
    if reason is not None:
        raise ViewerError(reason)
    request = json.dumps({'entry': str(entry), 'root': str(root),
                          'output': str(output_dir)})
    try:
        finished = subprocess.run(
            [shutil.which('node'), str(widget / BUILD_SCRIPT)],
            input=request, capture_output=True, text=True, cwd=str(widget))
    except OSError as error:
        raise ViewerError(f"bundling a model's app could not run Node.js "
                          f'({error})') from error
    try:
        answer = json.loads(finished.stdout)
    except ValueError:
        tail = '\n'.join(((finished.stderr or '') + (finished.stdout or ''))
                         .splitlines()[-20:])
        raise ViewerError(f"bundling a model's app failed with status "
                          f'{finished.returncode}:\n{tail}') from None
    if 'refusal' in answer:
        raise ViewerError(answer['refusal'])
    return {'script': answer['script'], 'stylesheet': answer['stylesheet'],
            'inputs': list(answer['inputs'])}
