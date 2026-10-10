# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

from machinome.node.assembly import AssemblyNode
import re

VALUE = eval('1 + 1')
ALIAS = eval
exec('x = 1')
CODE = compile('1', '<s>', 'eval')
MATH = __import__('math')
PATTERN = re.compile('[0-9]')


class Machine(AssemblyNode):
    pass
