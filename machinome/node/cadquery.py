# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

import sys
from machinome.exact_engine import require_exact_engine
from machinome.extras import require_extra
from machinome.node.declarative import NodeMeta
from machinome.node.exact_leaf import ExactLeafNode

# A project names this module to render with CadQuery, so without the
# `cadquery` extra it is refused here, at the import line, with the line
# that installs it. The check imports nothing: rendering imports CadQuery
# in the project's own module.
require_extra('cadquery', 'machinome.node.cadquery (CadQueryNode)',
              'cadquery')


def workplane_shape(rendered, engine):
    """The exact engine's currency for a CadQuery render result.

    A `Workplane` is a stack of values, not a shape: its values are taken,
    one becomes the currency as it is and several become one compound. A
    render that is already a shape -- a CadQuery `Shape`, or the kernel's
    own -- is admitted by the engine directly. Recognised by its `vals`
    method rather than imported, so this module does not load
    CadQuery.
    """
    shapes = list(rendered.vals()) if hasattr(rendered, 'vals') else [rendered]
    if not shapes:
        raise ValueError('CadQuery render produced no shape')
    if len(shapes) == 1:
        return engine.as_shape(shapes[0])
    return engine.compound([engine.as_shape(shape) for shape in shapes])


class CheckCQEditor(NodeMeta):
    """This metaclass will check if we are in the context of
    CQ-editor, if so, use no base classes, otherwise inherit
    ExactLeafNode.

    It drops whatever bases were declared rather than naming one, so it is
    unaffected by what the adapter inherits from.

    Derived from `NodeMeta`, as every node metaclass must be: a derived
    class's metaclass has to subclass the metaclass of each of its bases,
    and `NodeMeta` is what tells a node constructor it is running inside
    a class body.
    """
    def __new__(mcs, name, bases, namespace):
        if sys.modules.get('cq_editor.__main__', None):
            bases = tuple()

        return super().__new__(mcs, name, bases, namespace)


class CadQueryNode(ExactLeafNode, metaclass=CheckCQEditor):
    """
    Represents a 3D object created using the CadQuery tool.

    The exact-adapter contract -- exact, shape(), present() -- is
    ExactLeafNode's; CadQuery adds its namespace, the CQ-editor metaclass,
    and the conversion of a `Workplane` to the engine's currency.
    """
    namespace = 'cadquery.cq'

    def shape_from_rendered(self, rendered):
        return workplane_shape(rendered, require_exact_engine(
            f'exact leaf {self.name}',
            'its render result becomes exact geometry'))
