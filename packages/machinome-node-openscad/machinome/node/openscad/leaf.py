# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""`ScadLeafNode`, the OpenSCAD family's leaf base.

A family leaf's geometry is authored in SCAD: its materialization writes its
own `.scad` from what it rendered, which it keeps (`kept_artifacts()`), and
OpenSCAD renders its STL from that file, asynchronously, under the build's
STL render protocol (`StlRenderStart`). `OpenScadNode` and `Solid2Node` are
its node types.
"""

import logging
import os
import tempfile
from subprocess import Popen

from machinome.node.base import StlRenderStart
from machinome.node.leaf import LeafNode
from machinome.node.openscad import binary, writer


logger = logging.getLogger('node.base')


class ScadLeafNode(LeafNode):
    """A leaf whose geometry is authored in SCAD and rendered by OpenSCAD.

    Members beyond `LeafNode`'s: `fn` (the `$fn` its `.scad` begins with,
    when set), `scad_file`, `scad_code`, `generate_scad()`,
    `stl_builder_command` and `stl_builder_command_for(output)`.
    """

    #: The `$fn` the leaf's `.scad` begins with; None writes none.
    fn = None

    @property
    def scad_file(self):
        """This leaf's own `.scad`, beside its STL."""
        return writer.scad_file(self)

    def present(self, rendered):
        """What the leaf rendered, which the core holds as authored
        geometry."""
        return rendered

    def _current_artifact_presentation(self):
        """None: a family leaf's presentation is the geometry it authored,
        which its own `.scad` holds and OpenSCAD renders its STL from, so it
        is rendered on demand (`_require_model()`), never the import of
        that STL."""
        return None

    def materialize(self, rendered):
        """Write this leaf's own `.scad` from what it rendered: OpenSCAD
        renders its STL from it."""
        self.model = rendered
        self.generate_scad()

    def kept_artifacts(self):
        """The leaf's `.scad`, which the build keeps while the leaf is in the
        published tree: OpenSCAD renders its STL from it."""
        return (self.scad_file,)

    @property
    def scad_code(self):
        """This leaf's own SCAD text, which the OpenSCAD writer writes from
        its presentation."""
        return writer.scad_code(self)

    def generate_scad(self):
        """Publish this leaf's `.scad` (`writer.generate_scad`)."""
        writer.generate_scad(self)

    def generate_stl(self):
        """Render this leaf's STL from its `.scad` with OpenSCAD, in a
        subprocess, and raise `StlRenderStart` for the builder to wait on;
        nothing when the STL is current, the node is not rigid or another
        process holds its render lock."""
        if self._up_to_date(self.stl_file):
            return logger.info('STL up to date')
        if not self.rigid:
            return logger.info('Non rigid node, no STL to generate')
        if self._stl_generation_locked:
            return logger.info('Cannot generate, locked')

        node_name = getattr(self, 'name', type(self).__name__)
        needed_by = f'node {node_name} ({type(self).__qualname__})'
        reason = 'its STL is rendered from SCAD by OpenSCAD'
        openscad = binary.require_openscad(needed_by, reason)

        fh = open(self.lock_file, 'w')

        os.makedirs(os.path.dirname(self.stl_file) or '.', exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(
            prefix=f'.{os.path.basename(self.stl_file)}.', suffix='.tmp',
            dir=os.path.dirname(self.stl_file) or '.')
        os.close(descriptor)
        command = self.stl_builder_command_for(temporary)
        command[0] = openscad
        proc = Popen(command)

        fh.write(f'{proc.pid}')
        fh.close()
        logger.info(f'Job started with pid {proc.pid}')
        raise StlRenderStart(proc, self.stl_file, temporary, self.mtime_ns,
                             self.lock_file, self.source_digest,
                             self.source_fingerprint)

    @property
    def stl_builder_command(self):
        return self.stl_builder_command_for(self.stl_file)

    def stl_builder_command_for(self, output):
        return [
            'openscad', self.scad_file,
            '-o', output,
            '--export-format', 'binstl',
        ]
