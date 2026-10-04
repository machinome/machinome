from machinome.node.assembly import AssemblyNode
from machinome.node.flexible import FlexibleNode
from tests.test_model_consumption import NativeBox


class Wire(FlexibleNode):
    def render(self):
        raise AssertionError("production never asks flexible shape")


class Pair(AssemblyNode):
    first = NativeBox()
    second = NativeBox()
    unknown = Wire()
