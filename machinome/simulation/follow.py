# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Explicit two-envelope retained contact for a running coordinate."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Follow:
    """A retained scalar pushed by two independently authored envelopes.

    ``lower`` and ``upper`` receive the relation's two ordered source
    symbols. They build supported numeric expressions; the third source is
    the retained coordinate and is deliberately not passed to either.
    """

    lower: object
    upper: object
    _machinome_follow = True

    def __post_init__(self):
        if not callable(self.lower) or not callable(self.upper):
            raise TypeError('Follow(lower=, upper=) requires two callable '
                            'numeric envelope expressions.')
