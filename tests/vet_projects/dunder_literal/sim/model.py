# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

from machinome.node import AssemblyNode


def reach(obj):
    getattr(obj, '__subclasses__')
    getattr(obj, '__globals__')
    getattr(obj, '__builtins__')
    getattr(obj, '__loader__')
    getattr(obj, '__spec__')
    getattr(obj, '__code__')
    getattr(obj, '__closure__')
    getattr(obj, '__mro__')
    getattr(obj, '__bases__')
    getattr(obj, '__base__')
    getattr(obj, '__path__')
    return getattr(obj, f'__globals__')


class Machine(AssemblyNode):
    pass
