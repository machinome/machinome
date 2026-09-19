# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Play:
    """A running backlash/clearance law with ordered contact offsets."""

    low: float
    high: float
    _machinome_play = True

    def __post_init__(self):
        if (isinstance(self.low, bool) or isinstance(self.high, bool)
                or not isinstance(self.low, (int, float))
                or not isinstance(self.high, (int, float))
                or not math.isfinite(self.low)
                or not math.isfinite(self.high)
                or not self.low < self.high):
            raise ValueError(
                f'Play(low={self.low!r}, high={self.high!r}) requires finite '
                f'offsets ordered low < high.')
