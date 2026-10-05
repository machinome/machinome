# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

from machinome.node.assembly import AssemblyNode
import os
from os import path
from os.path import join
from os import system
from os import *  # noqa: F401,F403

HERE = os.path.dirname(__file__)
JOINED = os.path.join(HERE, 'x')
THERE = os.path.exists(HERE)
LISTED = os.listdir(HERE)
WALKED = os.walk(HERE)
ALSO = join(path.dirname(HERE), 'y')


def mutate():
    os.makedirs(HERE)
    os.environ.get('HOME')
    os.system('true')
    return system


class Machine(AssemblyNode):
    pass
