# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""A layer of a machine: a set of parts a page may show on its own.

A project defines each layer once, in a module of its own, and imports that
object wherever a node class declares it is on the layer::

    from machinome.layers import Layer

    ELECTRICAL = Layer('electrical', label='Electrical path')

A node class then says ``layers = ELECTRICAL`` (or a tuple of layers), so no
use site spells a string. The key is what a published document carries; the
label is what a person reads.

This module imports nothing, as ``machinome/parameters.py`` imports nothing:
it is on the import path of every project module that declares a layer and
of ``machinome/node/declarative.py``, which recognises a layer by
``isinstance``.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True, eq=False)
class Layer:
    """One layer, ``Layer(key, *, label)``.

    Both are required and both are non-empty strings. A layer never
    changes once made, and it is equal only to itself (equality and hash
    are identity, as a color choice's are): two objects that share a key
    are the conflict a published document refuses, never one layer.
    """

    key: str
    label: str = field(kw_only=True)

    def __post_init__(self):
        for name in ('key', 'label'):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise TypeError(
                    f'Layer {name} must be a non-empty string, not '
                    f'{value!r}')

    def __repr__(self):
        return f'Layer({self.key!r}, label={self.label!r})'
