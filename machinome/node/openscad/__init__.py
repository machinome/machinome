# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The OpenSCAD node family: the node type `OpenScadNode`, and the modules
every leaf authored in SCAD is built from.

- `machinome.node.openscad.leaf`: `ScadLeafNode`, the family's leaf base,
  which writes and keeps its own `.scad` and renders its STL from it with
  OpenSCAD;
- `machinome.node.openscad.writer`: the SCAD text of a presentation the core
  described (`machinome.node.presentation`), and its publication;
- `machinome.node.openscad.binary`: the OpenSCAD executable's contract.

`Solid2Node`, a leaf of the family rendered with SolidPython, is its own node
type at `machinome.node.solid2`. SolidPython is the family's kernel, installed
by the `openscad` extra: without it, importing this package -- or any module
beneath it -- is refused with the line that installs it (OpenSpec change
`openscad-out`, capability `openscad-node`).
"""

from machinome.extras import require_extra

# A project names this package to use OpenScadNode, and the OpenSCAD viewer
# imports its writer, so without the `openscad` extra both are refused here,
# with the line that installs it, before SolidPython is imported.
require_extra('openscad',
              'machinome.node.openscad (OpenScadNode and the OpenSCAD writer)',
              'solid2')

from solid2.core.parse_scad import get_scad_file_as_dict
from solid2.core.utils import resolve_scad_filename

from machinome.node.openscad.leaf import ScadLeafNode
from machinome.node.openscad.writer import scad_text
from machinome.node.sources import ExternalSourceIdentity, require_source_file
from machinome.source_generation import coherent_read


class OpenScadNode(ExternalSourceIdentity, ScadLeafNode):
    """
    A pure OpenScad node. You just need to declare the property "scad_source" with
    the path of your OpenScad source code, relative to the directory of the
    python file containing this node or absolute.

    The scad file must contain a module with the same name of the file, or you
    may specify the property "module_name" with the module name.
    """

    namespace = 'solid2.core.object_factory'
    scad_source = None
    module_name = None

    def __init__(self, *args, name=None, **kwargs):
        """Receives args, an optional name keyword argument and a list of keyword
        arguments. The list of arguments and keyword arguments will be passed as
        parameter to the module.

        Args:
           *args: will be passed as arguments to the OpenScad module
           name: the name of this node, by default the name of the class
           **kwargs: will be passed as keyword arguments to the openscad module
        """
        self.openscad_source = require_source_file(
            self.__class__, 'scad_source', self.scad_source)
        # This happens during root construction, before the assembly census
        # exists.  Tie the retained text to the active loader generation so a
        # replacement between this read and assembly cannot bless old bytes.
        self.openscad_code = coherent_read(self.openscad_source).decode()
        self.args = args
        self.kwargs = kwargs
        if self.module_name is None:
            self.module_name = self.openscad_source.split('/')[-1].split('.')[0]

        super().__init__(*args, name=name, **kwargs)

    def get_source_file(self):
        """Gets the openscad source code path"""
        return self.openscad_source

    def render(self):
        """Imports the OpenScad source code and renders into a solid2 object"""
        filename = resolve_scad_filename(self.openscad_source)
        scad = get_scad_file_as_dict(filename)
        try:
            module = scad[self.module_name]
        except KeyError:
            raise Exception(f"No module {self.module_name} found in {self.openscad_source}")
        rendered = module(*self.args, **self.kwargs)
        return rendered

    @property
    def scad_code(self):
        """The contents of the code, plus a module call, whose text the
        OpenSCAD writer writes"""
        rendered = scad_text(self.presentation())
        module_call = rendered.strip().split('\n')[-1]
        return f'{self.openscad_code}\n\n{module_call}'
