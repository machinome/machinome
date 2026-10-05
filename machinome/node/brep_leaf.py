# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

from machinome.brep_artifacts import deflections, write_brep, write_stl
from machinome.brep_cache import cached_shape
from machinome.engine import require_brep_engine
from machinome.node.leaf import LeafNode


class BrepLeafNode(LeafNode):
    """The base of a leaf whose geometry is a B-rep solid, a boundary
    representation.

    A declared extension point of the `leaf-contract` capability (ADR-163),
    at this one path, holding the B-rep leaf contract that `brep-geometry`
    specifies and ADR-047, ADR-160 and ADR-180 explain: because every B-rep
    leaf converts its render result to the B-rep engine's one currency at
    the adapter boundary, everything after that conversion is
    one implementation rather than one per backend. A subclass renders;
    when its render result is not something the engine admits as it is,
    it overrides the conversion hook `shape_from_rendered`, a rewrap of
    the kernel object the result holds and never a translation. The core
    writes the `.brep` and `.stl`, serves `shape()` from a current `.brep`
    without rendering, and never serves a shape from a replaced one, so no
    subclass ever evicts a cache. A subclass may declare its tessellation
    precision, and may extend `materialize` by calling it; it never
    overrides `shape`.

    Declared members: `shape_from_rendered`, `linear_deflection`,
    `angular_deflection`, `brep`, `shape`, `brep_file`.

    `brep_file` is set by the constructor; the others are class members.

    It declares no `namespace`, inheriting LeafNode's None, so it imposes
    none on a subclass: a leaf rendering the engine's currency declares
    none either, since admission is the conversion hook's.

    Kept out of leaf.py on purpose. That module imports nothing heavier than
    base. This one imports the core's B-rep modules -- the memos over shape
    handles and artifact publication -- but no engine and no kernel: the
    B-rep engine is resolved through its seam in `machinome.engine` only
    when a shape is converted, read or written, so a node whose artifacts
    are current never resolves it to be built.
    """

    #: The maximum distance, in millimetres, between this node's STL
    #: artifact and the surface it approximates -- the B-rep engine's own
    #: `theLinDeflection`. Declared as a class attribute like
    #: `SheetLeafNode.thickness`: an edit lands in this node's own class
    #: body, which the source-set path already tracks (ADR-071), so it
    #: rebuilds this node's artifacts and nothing else. It is read and
    #: validated at export time, not here -- see
    #: `brep_artifacts.deflections` --
    #: and never enters uniq_id (ADR-026/063): two tessellations of one
    #: solid are one node's artifact at two times, not two nodes.
    linear_deflection = 0.1

    #: The maximum angle, in radians, between the normals of two adjacent
    #: facets of this node's STL artifact -- the B-rep engine's own
    #: `theAngDeflection`. Same declaration shape and same defaults as
    #: `linear_deflection` above.
    angular_deflection = 0.1

    @property
    def brep(self):
        return True

    def shape(self):
        """This leaf's B-rep solid, in its own frame, in the B-rep engine's
        currency.

        Read from the `.brep` when it is current, without rendering, and
        never from a `.brep` that has since been replaced; rendered and
        converted otherwise. Not overridden by a subclass.
        """
        if self._up_to_date(self.brep_file):
            return cached_shape(self.brep_file)
        # `model` is the presentation after assemble(), often an
        # ArtifactImport. A stale BREP needs fresh native geometry.
        rendered = self.render()
        self.validate(rendered)
        return self._converted(rendered)

    def shape_from_rendered(self, rendered):
        """The engine's currency for one validated render result.

        The declared conversion hook. A rewrap of the kernel object the
        result holds, never a translation: no tessellation, tolerance or
        healing. The default admits what the B-rep engine admits as it is
        -- its currency, or an object carrying it as `.wrapped` -- so a
        leaf rendering the kernel's own shape needs no override; an adapter
        whose backend returns something else (a CadQuery `Workplane`, a
        build123d builder) overrides this, keeping that promise. A result
        it cannot convert raises `TypeError`, which the core re-raises
        naming this node.
        """
        return require_brep_engine(
            f'B-rep leaf {self.name}',
            'its render result becomes B-rep geometry').as_shape(rendered)

    def _converted(self, rendered):
        """`shape_from_rendered`, with a refusal that names this node.

        The engine's own refusal names only the type it was handed, which
        for a leaf declaring no `namespace` is the first and only word on
        what went wrong; the core adds which node rendered it.
        """
        try:
            return self.shape_from_rendered(rendered)
        except TypeError as error:
            kind = type(rendered)
            raise TypeError(
                f'{self.name} ({type(self).__qualname__}) rendered a '
                f'{kind.__module__}.{kind.__qualname__}, which its '
                f'conversion hook shape_from_rendered cannot turn into '
                f'B-rep geometry: {error}') from error

    def materialize(self, rendered):
        """Export native BREP and STL artifacts.

        The export is skipped when the artifact on disk was already produced
        from these sources -- the same guard generate_stl() has always had,
        which this path used to run upstream of. A node that opts out of
        optimization still reaches here, so the guard belongs on the adapter
        and not only on the assemble() shortcut.

        The render result is converted only once an artifact is known to
        be stale, inside the branch that writes it. A leaf declaring
        `optimize = False` is prepared on every build, current or not, and
        converting first would resolve the B-rep engine for nothing.

        The BREP is written before the STL, and not merely for symmetry
        with FusionNode.generate_stl(): the engine's STL writer meshes the
        shape, which stores its triangulation ON the shape, and its BREP
        writer serialises whatever triangulation the shape is carrying
        alongside its topology. Export the STL first and two builds of the
        same solid at different declared precision write BYTE-DIFFERENT
        `.brep` files, even though the topology -- everything `shape()`
        and `.brep` promise -- never changed. Writing the BREP from the
        not-yet-meshed shape is what keeps it, and `shape()`, independent
        of whatever precision is declared.
        """
        brep_current = self._up_to_date(self.brep_file)
        stl_current = self._up_to_date(self.stl_file)
        if brep_current and stl_current:
            return
        shape = self._converted(rendered)
        digest = self.source_digest
        fingerprint = self.source_fingerprint
        if not brep_current:
            write_brep(shape, self.brep_file, self.mtime_ns, digest,
                       fingerprint)
        if not stl_current:
            linear_deflection, angular_deflection = deflections(self)
            write_stl(shape, self.stl_file, self.mtime_ns,
                      linear_deflection, angular_deflection, digest,
                      fingerprint)
