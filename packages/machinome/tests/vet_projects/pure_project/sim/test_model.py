# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

import unittest

from machinome.test import TestCase

from .model import Machine


class MachineTest(TestCase):
    node = Machine


if __name__ == '__main__':
    unittest.main()
