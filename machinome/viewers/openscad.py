# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""OpenSCAD-backed PNG rendering."""

import logging
import os
import re
import shutil
import sys

from machinome import currency
from machinome.scad_engine import require_scad_engine


logger = logging.getLogger('viewers.openscad')

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


class OpenScadRenderer:
    """Renders a node's SCAD to an image with OpenSCAD.

    The SCAD it draws is obtained on demand, from no build: `present`
    writes the root's `.scad` in the build directory, through the OpenSCAD
    engine, for the pose the snapshot renders, and `render` removes it once
    OpenSCAD has read it, whether the render succeeded or failed -- the file
    exists only for this renderer. A root whose geometry is authored in SCAD
    keeps its `.scad`, which is its own build artifact. The engine and the
    binary are both reached through the seam `machinome.scad_engine`.
    """

    def require_engine(self):
        """The OpenSCAD engine, which writes the SCAD this renderer draws,
        or its refusal naming this renderer and `--renderer web`. Asked
        before the node is loaded."""
        return require_scad_engine(
            'the OpenSCAD snapshot renderer',
            'it renders the SCAD the OpenSCAD engine writes',
            'use --renderer web')

    def present(self, node):
        """Write the root's `.scad` at its own artifact path for the pose it
        is assembled in, its imports resolving from that file's directory.
        Called inside the project build lock, right after `assemble()`.
        Not a build artifact: `render` removes it after OpenSCAD has read
        it, and a build removes one a killed render left."""
        node.generate_scad()

    def withdraw(self, node):
        """Remove the root's on-demand `.scad` and its currency record,
        unless the root's geometry is authored in SCAD, whose `.scad` is
        its own build artifact."""
        if getattr(node, 'scad_authored', True):
            return
        for path in (node.scad_file, currency.sidecar(node.scad_file)):
            try:
                os.remove(path)
            except FileNotFoundError:
                pass

    def render(self, node, args, output, runner):
        try:
            openscad = self.require_engine().require_binary(
                'the OpenSCAD snapshot renderer',
                'rendering the requested image launches OpenSCAD',
                'use --renderer web')
            base_command = self.build_command(node, args, output)
            base_command[0] = openscad
            command = self.wrap_command(base_command)
            logger.info('Rendering %s to %s', node.scad_file, output)
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
            raise OpenScadImportError(missing, node.scad_file)

    def build_command(self, node, args, output):
        command = ['openscad', '-o', output]
        if args.camera:
            command.extend(['--camera', args.camera])
        if args.autocenter:
            command.append('--autocenter')
        if args.viewall:
            command.append('--viewall')
        command.extend(['--imgsize', args.imgsize.lower().replace('x', ',')])

        projection = args.projection or 'perspective'
        command.extend(['--projection', 'o' if projection == 'ortho' else 'p'])
        command.extend(['--colorscheme', args.colorscheme or 'Cornfield'])
        if args.preview:
            command.append('--preview')
        if args.view:
            command.extend(['--view', args.view])
        command.append(node.scad_file)
        return command

    def wrap_command(self, command):
        if os.environ.get('DISPLAY'):
            return command
        xvfb_run = self.find_xvfb_run()
        if not xvfb_run:
            sys.stderr.write(
                "Error: no DISPLAY and 'xvfb-run' not found on PATH. "
                "Install xvfb (e.g. `apt-get install -y xvfb`) or run this "
                "command under `xvfb-run -a`.\n"
            )
            raise SystemExit(1)
        return [xvfb_run, '-a'] + command

    def find_xvfb_run(self):
        return shutil.which('xvfb-run')
