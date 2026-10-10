# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

from machinome.node.assembly import AssemblyNode
from pathlib import Path


def save(p, text, mode, archive):
    open(p, 'w')
    open(p, mode='a')
    open(p, mode='a+')
    open(p, mode)
    opener = open
    Path(p).write_text(text)
    Path(p).parent.mkdir(parents=True)
    return opener


def read(p, text, archive):
    with open(p) as stream:
        stream.read()
    open(p, 'rb')
    archive.open('rb')
    return text.replace('a', 'b')


class Machine(AssemblyNode):
    pass
