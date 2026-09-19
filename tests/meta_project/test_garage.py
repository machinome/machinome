# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

from machinome.test import TestCase


class GarageTest(TestCase):

    def test_children_get_attribute_derived_names(self):
        self.assertEqual(self.garage.left.name, 'left')
        self.assertEqual(self.garage.right.name, 'right')
        self.assertEqual(self.garage.posts[0].name, 'posts-0')
        self.assertEqual(self.garage.posts[1].name, 'posts-1')
