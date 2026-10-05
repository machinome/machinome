# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

# Names the file binds itself are the project's, not the built-ins':
# a child called `input` (Poleni-1709, Pascaline-module), a `compile`
# imported from `re`, and a parameter called `help`.

from re import compile

from machinome.node import AssemblyNode


class InputArbor:

    class turn:

        @staticmethod
        def drives(coordinate):
            return coordinate


def matches(pattern, text):
    return compile(pattern).match(text)


def f(help):
    return help


class Machine(AssemblyNode):
    input = InputArbor()
    input.turn.drives('output')
