# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""Select a body's declared color from the state that poses it."""
from dataclasses import dataclass
import math
from numbers import Real
import re

from machinome.expression_graph import GraphValue, symbolic

_HEX = re.compile(r'#[0-9a-fA-F]{6}\Z')


@dataclass(frozen=True, eq=False)
class _ColorChoice:
    condition: object
    on: str
    off: str

    def rgb(self):
        """The same selection in the existing scalar presentation language."""
        enabled = GraphValue(self.condition) != 0
        return tuple(int(self.off[i:i + 2], 16) / 255
                     + enabled * ((int(self.on[i:i + 2], 16)
                                   - int(self.off[i:i + 2], 16)) / 255)
                     for i in (1, 3, 5))


def color_when(condition, *, on, off):
    """Choose between two fixed ``#RRGGBB`` strings for a node's ``color``.

    A finite numeric zero selects ``off``; every other finite bool or real
    selects ``on``. Both colors are required and validated even when one
    is not selected. A supported symbolic scalar retains its expression
    and palette for ordinary publication, without evaluating Python truth.

    Assign the result where the model's numeric or symbolic observation is
    available. Reset, restore and replay recompute the same body's color
    from that state; no separate appearance state is retained. This changes
    its visual color, not its geometry or emitted light. Conditional live
    publication requires document 14 and a reader supporting it (API 30).
    """
    for name, value in (('on', on), ('off', off)):
        if not isinstance(value, str) or _HEX.fullmatch(value) is None:
            raise ValueError(f'color_when {name} must be a six-digit #RRGGBB string')
    if isinstance(condition, Real):
        if condition != condition or condition == math.inf or condition == -math.inf:
            raise ValueError('color_when condition must be finite')
        return on if condition != 0 else off
    graph = symbolic(condition)
    if graph is None:
        raise TypeError('color_when condition must be a finite bool/real or symbolic scalar')
    return _ColorChoice(graph, on, off)
