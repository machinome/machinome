# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

from machinome.exact_engine import require_exact_engine
from machinome.node.exact_leaf import ExactLeafNode


def build123d_shape(rendered):
    """The kernel shape of a build123d render result, or None if
    ``rendered`` did not come from build123d.

    build123d is a front end over OCCT: every object of it wraps a single
    TopoDS_Shape, exposed as ``.wrapped``, which is the exact engine's
    currency itself (ADR-160). Taking that shape is therefore the whole
    conversion, and every consumer after it -- placement, fuse, common,
    BREP persistence, volume -- needs no backend special case, so a fusion
    may freely mix build123d with any other exact backend.

    build123d is recognised by module name rather than imported.
    ``machinome.node`` resolves its adapters on first use, and importing
    build123d costs about 1.6 seconds, which a project modelling in another
    backend should not pay.

    A builder is not itself geometry: ``with BuildPart() as part:`` is
    build123d's headline idiom, and returning the builder rather than its
    ``.part`` is the first mistake a user makes, so the finished part is
    taken. Returning None rather than raising leaves the diagnosis to
    Build123dNode.validate(), which can name the node.
    """
    if not type(rendered).__module__.startswith('build123d'):
        return None
    if not hasattr(rendered, 'wrapped'):
        rendered = getattr(rendered, 'part', None)
    return getattr(rendered, 'wrapped', None)


class Build123dNode(ExactLeafNode):
    """
    Represents a 3D object created using the build123d tool.

    build123d is a boundary-representation backend over the same OCCT that
    CadQueryNode uses, so the exact-adapter contract -- exact, shape(),
    as_scad() -- is ExactLeafNode's. What is build123d's own is the namespace
    and the solid-shaped-result rule below.

    Note that this module never imports build123d. See build123d_shape().
    """

    namespace = 'build123d'

    def shape_from_rendered(self, rendered):
        return build123d_shape(rendered)

    def validate(self, rendered):
        """Reject anything but a solid, on top of the inherited list and
        namespace checks.

        The namespace cannot carry this adapter alone. build123d's solids,
        sketches and curves are all under the `build123d` namespace -- Part
        and Compound in build123d.topology.composite, Solid in
        build123d.topology.three_d, but also Rectangle in
        build123d.objects_sketch and Line in build123d.objects_curve -- so
        `namespace` admits a sketch as readily as a part. Left to itself, a
        returned sketch would fail later and far less legibly, inside the STL
        export.

        The check stays here rather than on ExactLeafNode because it is not
        the exact contract's: a CadQuery render is legitimately a Workplane,
        which is not a solid until shape_from_rendered unwraps it. The
        solids are counted by the exact engine.
        """
        super().validate(rendered)

        shape = build123d_shape(rendered)
        if shape is None or not require_exact_engine(
                f'exact leaf {self.name}',
                'its render result is checked for a solid'
                ).solid_count(shape):
            raise Exception(
                f"{self.name} is a Build123dNode and should render a "
                f"build123d solid -- a Part, Solid or Compound, or a builder "
                f"whose .part is one -- not {type(rendered).__name__}"
            )
