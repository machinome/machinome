# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

from machinome.node import AssemblyNode
from . import names  # noqa: F401


class Probe:
    pass


def reach(obj):
    obj.__subclasses__
    obj.__globals__
    obj.__builtins__
    obj.__loader__
    obj.__spec__
    obj.__code__
    obj.__closure__
    obj.__mro__
    obj.__bases__
    obj.__base__
    obj.__path__
    return type(Probe()).__mro__


class Machine(AssemblyNode):
    pass
