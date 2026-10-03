# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

import os

from .base import AbstractBaseNode


#: The version of the leaf contract this machinome speaks -- the members
#: the four leaf bases declare, and what each promises (the
#: `leaf-contract` capability, ADR-163). A change to the meaning of a
#: declared member, or the removal of one, changes this number in the same
#: change. A leaf written outside the core may declare the number it was
#: written against as `leaf_contract`; see `LeafNode.__init_subclass__`.
CONTRACT = 1


class LeafNode(AbstractBaseNode):
    """The base of every leaf: a node that produces one solid's geometry.

    A declared extension point of the `leaf-contract` capability (ADR-163),
    at this one path: a node type written outside the core subclasses it,
    or one of the three bases that extend it (`ExactLeafNode`,
    `SheetLeafNode`, `FlexibleNode`), and uses only the members declared
    here and on those bases. Each technology renders its solid its own
    way; a faceted leaf either presents its render as SCAD (`as_scad`),
    which OpenSCAD turns into the STL, or produces its own STL in
    `materialize`, publishing it through `publish_artifact`. The core
    does everything else: currency, stamps, source records, the tree,
    assembly, fusion, export, the viewer document and the test framework.
    A subclass never overrides `assemble`, `mtime_ns`, `mtime`,
    `source_digest`, `source_fingerprint`, `uniq_id`, `children`, `time`
    or a member whose name begins with an underscore.

    Declared members: `render`, `validate`, `namespace`, `as_scad`,
    `materialize`, `publish_artifact`, `get_source_file`, `files`,
    `source_recipe`, `artifact_import`, `basepath`, `local_stl`,
    `scad_file`, `stl_file`, `model`, `generate_scad`, `leaf_contract`.

    `files`, `basepath`, `local_stl`, `scad_file`, `stl_file` and `model`
    are set by the constructor; the others are class members.
    """

    _type = 'LeafNode'

    #: An optional module prefix. When declared, validation refuses a
    #: render result whose type's module does not start with it, naming
    #: the node, before any artifact is written. None checks nothing.
    namespace = None

    #: The leaf contract version this class was written against, when it
    #: declares one in its own body; checked against `CONTRACT` when the
    #: class is created (see `__init_subclass__`). None, here and in a
    #: subclass's body, declares nothing and is not checked.
    leaf_contract = None

    def __init_subclass__(cls, **kwargs):
        """Refuse a class that declares a leaf contract this core does
        not speak.

        Only a declaration in the class's OWN body is checked, so a
        project leaf that declares nothing, and a subclass inheriting a
        declaration that was checked when its parent was created, are
        created as before. The declaration must be an integer equal to
        `CONTRACT` (`bool` is not one); anything else raises `TypeError`
        and the class does not exist (ADR-165).
        """
        super().__init_subclass__(**kwargs)
        declared = cls.__dict__.get('leaf_contract')
        if declared is None:
            return
        if type(declared) is not int or declared != CONTRACT:
            raise TypeError(
                f'{cls.__module__}.{cls.__qualname__} declares leaf '
                f'contract {declared!r}; this machinome speaks leaf '
                f'contract {CONTRACT} (machinome.node.leaf.CONTRACT)')

    @property
    def time(self):
        """Raise an exception, as leaf nodes cannot rely on time.

        A part whose SHAPE follows the machine -- a spring, a belt, a
        loom -- is a flexible leaf (`MolejoNode`), and it reads no time
        either: its geometry is a pure function of the values its parent
        binds to its declared ports.
        """
        raise Exception(f"Leaf node cannot rely on time, animation should be "
                        "done on internal nodes. A part whose shape follows "
                        "the machine is a flexible leaf (MolejoNode), whose "
                        "parameters arrive through its declared ports")

    @property
    def children(self):
        """Returns an empty tuple, as leaf nodes have no children"""
        return tuple()

    def _render_can_be_skipped(self):
        """A leaf knows its own source set at construction, so it can
        answer this before doing any work -- unlike an internal node.

        Both artifacts must be current, not just the STL: the scad is
        what regenerates the STL if it is ever lost, and skipping is
        only safe while the pair on disk is the pair this source would
        produce.
        """
        return (
            self.optimize
            and self.rigid
            and self._up_to_date(self.stl_file)
            and self._up_to_date(self.scad_file)
            and (not self.exact or self._up_to_date(self.brep_file))
        )

    def _prepare_can_be_skipped(self):
        """Native geometry does not depend on a presentation sidecar."""
        return (
            self.optimize
            and self.rigid
            and self._up_to_date(self.stl_file)
            and (not self.exact or self._up_to_date(self.brep_file))
        )

    def as_scad(self, rendered):
        """This leaf's render result as a solid2 object, for a leaf
        presented as SCAD: the core writes that SCAD and OpenSCAD produces
        the STL from it.

        A leaf that produces its own STL in `materialize` need not
        implement it: once that artifact is current, the core presents it
        by importing it.
        """
        raise NotImplementedError(f"LeafNode subclass {self.__class__} must "
                                  "be able to output scad")

    def publish_artifact(self, path, write):
        """Publish one artifact of this node's own, unless it is current.

        `path` must be one of this node's artifact paths -- a path
        beginning with its `basepath` -- or the call raises `ValueError`
        naming the node and the path, before `write` is called. When the
        artifact at `path` is already the one this node's sources would
        produce, nothing is done and False is returned. Otherwise
        `write(temporary)` is called with a temporary path in the
        artifact's directory; that file is stamped with the node's
        `mtime_ns` and put in place of `path` by rename, together with the
        record of the node's `source_digest` and `source_fingerprint`, and
        True is returned. If `write` raises, nothing is published: the
        previous artifact and its record stay as they were, and the
        temporary file is removed.

        The one way a leaf writes an artifact of its own, so the stamp,
        the record and the atomic replacement are the core's, the same
        for every artifact (the `leaf-contract` capability).
        """
        spelling = os.fspath(path)
        if not spelling.startswith(self.basepath):
            raise ValueError(
                f'{self.name} can only publish its own artifacts, whose '
                f'paths begin with {self.basepath}; {spelling} is not one')
        if self._up_to_date(spelling):
            return False
        # Imported here, as the exact base does: the publication sequence
        # is the exact artifacts', and this module stays as light as base.
        from machinome.exact_artifacts import _atomic_export
        _atomic_export(spelling, self.mtime_ns, write, self.source_digest,
                       self.source_fingerprint)
        return True

    def validate(self, rendered):
        """Check a render result before anything is made of it.

        Refuses None and a list, which no leaf may render, and, when the
        leaf declares a `namespace`, a result from any other module. A
        subclass may extend it, calling this first.
        """
        if rendered is None:
            # Only an internal node's render() may return nothing (its
            # children are then the declared ones); a leaf has geometry
            # to hand over or it has nothing.
            raise Exception(f"{self.__class__} is a LeafNode and its "
                            f"render() returned None instead of a "
                            f"{self.namespace} object")
        if type(rendered) in (list, tuple):
            raise Exception(f"{self.__class__} is a LeafNode and should return "
                            f"a {self.namespace} object, not a list")

        if self.namespace and not type(rendered).__module__.startswith(self.namespace):
            raise Exception(f"{self.__class__} is a LeafNode and should render "
                            f"as {self.namespace} child, not {type(rendered)}")
    def _uses_legacy_scad_materialization(self):
        """Honor a project leaf's explicit ``as_scad`` override.

        Built-in adapters that own both materialization and presentation are
        native.  An earlier class in the MRO owning only ``as_scad`` is the
        legacy extension seam and must still drive its artifact production.
        """
        mro = type(self).mro()
        scad_owner = next(
            index for index, cls in enumerate(mro)
            if 'as_scad' in cls.__dict__)
        materialize_owner = next(
            index for index, cls in enumerate(mro)
            if 'materialize' in cls.__dict__)
        return scad_owner < materialize_owner
