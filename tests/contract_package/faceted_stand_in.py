# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A faceted leaf written outside the core, producing its own STL.

`MeshPart` takes its geometry from a committed mesh file, as `StlNode`
does, through the declared members alone: one call of
`require_source_file`, given the declared value, resolves the file beside
the declaring module or refuses the leaf (no declaration, no file) before
the base constructor runs, `get_source_file()` returns it,
`ExternalSourceIdentity` puts the wrapper module in its identity, and
`materialize()` publishes the STL through `publish_artifact`. It declares
no `as_scad`: the core presents its artifact.

When `LEAF_CONTRACT_WRITE_LOG` names a file, every call of the writer
appends one line to it, so a test can count how often the artifact was
produced across processes.
"""

import os

import trimesh

from machinome.node.leaf import LeafNode
from machinome.node.sources import ExternalSourceIdentity, require_source_file


class MeshPart(ExternalSourceIdentity, LeafNode):
    """A part whose geometry is a committed mesh file."""

    leaf_contract = 3

    #: The committed mesh, relative to the wrapper module's directory.
    mesh_source = None

    def __init__(self, *args, **kwargs):
        self.mesh_source = require_source_file(type(self), 'mesh_source',
                                               self.mesh_source)
        super().__init__(*args, **kwargs)

    def get_source_file(self):
        return self.mesh_source

    def render(self):
        return self

    def materialize(self, rendered):
        def write(temporary):
            log = os.environ.get('LEAF_CONTRACT_WRITE_LOG')
            if log:
                with open(log, 'a') as handle:
                    handle.write(f'{os.getpid()}\n')
            mesh = trimesh.load(self.mesh_source, force='mesh')
            mesh.export(temporary, file_type='stl')

        self.publish_artifact(self.stl_file, write)
