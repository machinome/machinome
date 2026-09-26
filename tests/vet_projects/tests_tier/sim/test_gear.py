# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

import logging
import unittest

import pytest

from machinome.test import TestCase

from .gear import Gear

LOG = logging.getLogger(__name__)


class GearTest(TestCase):
    node = Gear

    @pytest.mark.slow
    def test_it(self):
        unittest.TestCase.assertTrue(self, True)
