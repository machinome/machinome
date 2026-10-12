# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The OpenSCAD viewer: a provider of the seam of viewers, `machinome.viewer`.

It takes a still of a machine at one assembled instant, for `machinome
snapshot --viewer openscad`, the snapshot's default: `present` assembles the
posed root and writes its SCAD through the OpenSCAD node family's writer
inside the build lock, `capture` runs the `openscad` executable on it after,
and `withdraw` removes the file. It offers no session and embeds nothing. It
reaches the OpenSCAD node package directly, its writer for the SCAD it draws
and its binary contract for the executable, so importing it without
SolidPython or without the node package is the package's refusal, naming
`machinome[openscad]`, which the seam passes through (OpenSpec change
`viewer-seam`).
"""

import logging
import os
import re
import shutil
from subprocess import CalledProcessError, run

from machinome import currency
from machinome.node import supported
from machinome.viewer import ViewerError

# The node package first, through the table's `load`, so its absence is the
# node type's refusal by the `openscad` extra however the import system
# reports it, as the table's renderer column did before this viewer had an
# address of its own (`viewer-seam`).
supported.load('openscad')

from machinome.node.openscad import binary, writer  # noqa: E402

#: The viewer contract version this provider implements.
CONTRACT = 1

#: The name the seam knows this viewer by.
NAME = 'openscad'

#: A still, and nothing else: no session, no embedding.
OPERATIONS = frozenset({'present', 'capture'})

#: Every snapshot option beyond the common ones: OpenSCAD's own.
CAPTURE_OPTIONS = frozenset({'autocenter', 'viewall', 'projection',
                             'colorscheme', 'view', 'render', 'preview'})

logger = logging.getLogger('viewer.openscad')

# OpenSCAD prefixes its own diagnostic lines this way; everything else on
# either captured stream is progress output ("Compiling design...", cache
# sizes, rendering time) and stays on the debug stream. Measured against
# OpenSCAD 2021.01 (evidence/probe_openscad_missing.py).
_DIAGNOSTIC_LINE = re.compile(r'^(WARNING|ERROR|DEPRECATED):')

# "WARNING: Can't open import file '<path>', import() at line N" -- measured
# against OpenSCAD 2021.01 (evidence/probe_openscad_missing.py), on stdout,
# with a return code of 0. A future OpenSCAD build that rewords this warning
# silently returns this guard to today's behaviour (the part goes missing
# and the command still reports success); the spec rule that reads the
# generated `.scad` and checks the named path on disk
# (`build-pipeline`, "Generated SCAD imports resolve from the file that
# holds them") is the first guard and does not depend on this text at all.
_CANNOT_OPEN_IMPORT = re.compile(r"Can't open import file '([^']*)'")


class OpenScadImportError(RuntimeError):
    """OpenSCAD reported it could not open a file a design imports.

    Carries the file OpenSCAD named and the `.scad` that imports it, so
    `machinome snapshot` can fail loudly -- naming the missing part -- instead
    of writing an image with it silently absent.
    """

    def __init__(self, missing_file, scad_file):
        self.missing_file = missing_file
        self.scad_file = scad_file
        super().__init__(
            f"OpenSCAD could not open import file {missing_file!r}, "
            f"imported by {scad_file}")


class OpenScadViewer:
    """Draws a node's SCAD to an image with OpenSCAD.

    The SCAD it draws is obtained on demand, from no build: `present`
    assembles the root and has the OpenSCAD writer publish its `.scad` in
    the build directory for the pose the snapshot draws, as a transient
    artifact, and `draw` removes it once OpenSCAD has read it, whether the
    drawing succeeded or failed -- the file exists only for this viewer,
    and a build removes one a killed drawing left. A root that keeps its
    `.scad` (`kept_artifacts()`, a family leaf) keeps it.
    """

    def present(self, node):
        """Assemble the root and write its `.scad` at its own artifact path
        for the pose it is assembled in, its imports resolving from that
        file's directory. Called inside the project build lock. Not a build
        artifact unless the root keeps it: published transient."""
        node.assemble()
        writer.generate_scad(node)

    def withdraw(self, node):
        """Remove the root's on-demand `.scad` and its currency record,
        unless the root keeps it (`kept_artifacts()`)."""
        path = writer.scad_file(node)
        if path in node.kept_artifacts():
            return
        for each in (path, currency.sidecar(path)):
            try:
                os.remove(each)
            except FileNotFoundError:
                pass

    def capture(self, node, request, output, runner):
        """Draw the root's `.scad` to `output`, raising `ViewerError` with
        the sentence the snapshot command writes: an import OpenSCAD could
        not open removes the partial image; a process failure, a missing
        executable and the binary contract's refusal each say what
        failed."""
        try:
            self.draw(node, request, output, runner)
        except OpenScadImportError as error:
            # OpenSCAD itself already wrote whatever it could draw -- the
            # picture with the missing part -- straight to output; the spec
            # is that a failed snapshot leaves no image behind.
            if os.path.exists(output):
                os.remove(output)
            raise ViewerError(str(error)) from error
        except CalledProcessError as error:
            raise ViewerError(
                f'OpenSCAD rendering failed:\n{error.stderr}') from error
        except FileNotFoundError as error:
            raise ViewerError(
                'OpenSCAD not found in PATH. Please install OpenSCAD and '
                'ensure it is accessible.') from error
        except binary.OpenScadUnavailable as error:
            raise ViewerError(str(error)) from error

    def draw(self, node, request, output, runner):
        """Run OpenSCAD on the root's `.scad`, then withdraw it; raise what
        went wrong (`OpenScadImportError` for an import it could not
        open)."""
        try:
            openscad = binary.require_openscad(
                'the OpenSCAD viewer',
                'rendering the requested image launches OpenSCAD',
                'use --viewer web')
            base_command = self.build_command(node, request, output)
            base_command[0] = openscad
            command = self.wrap_command(base_command)
            logger.info('Rendering %s to %s', writer.scad_file(node), output)
            logger.debug('OpenSCAD command: %s', ' '.join(command))
            result = runner(command, check=True, capture_output=True,
                            text=True)
        finally:
            self.withdraw(node)
        self._report(result, node)

    def _report(self, result, node):
        """Surface what OpenSCAD said on either captured stream, and
        fail when a line reports it could not open a file this design
        imports.

        Every warning, error or deprecation line OpenSCAD prints reaches
        a level a normal run shows; everything else -- OpenSCAD's own
        progress output -- stays on the debug stream, exactly as before.
        """
        missing = None
        for stream in (result.stdout, result.stderr):
            if not stream:
                continue
            for line in stream.splitlines():
                if _DIAGNOSTIC_LINE.match(line):
                    logger.warning(line)
                else:
                    logger.debug(line)
                if missing is None:
                    match = _CANNOT_OPEN_IMPORT.search(line)
                    if match:
                        missing = match.group(1)
        if missing is not None:
            raise OpenScadImportError(missing, writer.scad_file(node))

    def build_command(self, node, request, output):
        command = ['openscad', '-o', output]
        if request.camera:
            command.extend(['--camera', request.camera])
        if request.autocenter:
            command.append('--autocenter')
        if request.viewall:
            command.append('--viewall')
        command.extend(['--imgsize', request.imgsize.lower().replace('x', ',')])

        projection = request.projection or 'perspective'
        command.extend(['--projection', 'o' if projection == 'ortho' else 'p'])
        command.extend(['--colorscheme', request.colorscheme or 'Cornfield'])
        if request.preview:
            # OpenSCAD's --preview takes a value; given bare, it takes the
            # next token (the .scad path) as that value.
            command.append('--preview=throwntogether')
        if request.view:
            command.extend(['--view', request.view])
        command.append(writer.scad_file(node))
        return command

    def wrap_command(self, command):
        if os.environ.get('DISPLAY'):
            return command
        xvfb_run = self.find_xvfb_run()
        if not xvfb_run:
            raise ViewerError(
                "no DISPLAY and 'xvfb-run' not found on PATH. "
                "Install xvfb (e.g. `apt-get install -y xvfb`) or run this "
                "command under `xvfb-run -a`.")
        return [xvfb_run, '-a'] + command

    def find_xvfb_run(self):
        return shutil.which('xvfb-run')


_VIEWER = OpenScadViewer()


def identity():
    """`('machinome-viewer-openscad', <version>)`, the installed
    distribution."""
    from importlib.metadata import PackageNotFoundError, version
    try:
        installed = version('machinome-viewer-openscad')
    except PackageNotFoundError:
        installed = None
    return ('machinome-viewer-openscad', installed)


def document_versions():
    """None: this viewer reads no node-tree document."""
    return None


def readable(version):
    """False: this viewer reads no node-tree document."""
    return False


def present(node, build_dir):
    """Assemble the posed root and write its `.scad`; called inside the
    project build lock. Returns the root, which `capture` draws and
    `withdraw` cleans after."""
    _VIEWER.present(node)
    return node


def withdraw(node):
    """Remove the root's on-demand `.scad`, unless the root keeps it."""
    _VIEWER.withdraw(node)


def capture(node, request, output):
    """Draw the presented root to the PNG `output` with OpenSCAD, or raise
    `ViewerError` writing none. The subprocess runner is this module's
    `run`, read when it is called."""
    _VIEWER.capture(node, request, output, run)
