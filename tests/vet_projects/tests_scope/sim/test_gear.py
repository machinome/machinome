# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

import subprocess  # noqa: F401

from machinome.test import TestCase

from .gear import Gear


class GearTest(TestCase):
    node = Gear
