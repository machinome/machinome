"""Leaves whose declared source file does not exist."""

import os

from solid_node.node import StlNode, StepNode
from solid_node.node.adapters.jscad import JScadNode
from solid_node.node.adapters.openscad import OpenScadNode


class MissingStl(StlNode):
    stl_source = 'absent.stl'


class MissingStep(StepNode):
    step_source = 'absent.step'


class MissingJscad(JScadNode):
    jscad_source = 'absent.js'


class MissingScad(OpenScadNode):
    scad_source = 'absent.scad'


class DirectoryStl(StlNode):
    """A declared source that exists but is a directory, not a file."""

    stl_source = 'a_directory'


class DirectoryStep(StepNode):
    """The same, for a STEP document."""

    step_source = 'a_directory'


class BareScad(OpenScadNode):
    """No `scad_source` at all: out of this change's scope, probed only
    to record what happens today."""


class VanishingJscad(JScadNode):
    """`tests/test_builder_reload_resilience.py`'s VANISHING_JSCAD_PIPE
    shape: the file is present when the node is constructed and removed
    by the constructor itself, right after `super().__init__()`.

    A construction-time check placed where this change places it -- inside
    `JScadNode.__init__`, before its own `super().__init__()` -- sees the
    file and passes; `mtime_ns` then fails as it does today.
    """

    jscad_source = 'vanishing.js'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        os.remove(self.jscad_source)
