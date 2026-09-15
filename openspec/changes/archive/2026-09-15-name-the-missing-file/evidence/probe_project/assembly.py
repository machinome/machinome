"""A declarative assembly whose child's file is absent."""

from solid_node.node import AssemblyNode

from parts import MissingStl


class Rig(AssemblyNode):
    """The child is DECLARED here; nothing is constructed by this body."""

    part = MissingStl()
