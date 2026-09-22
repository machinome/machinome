# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0
"""Keep historical fixtures as controls, allowing only the declared v11 gate."""
from copy import deepcopy


def without_semantic_upgrade(test, actual, expected):
    result = deepcopy(actual)
    if 'program' in expected:
        test.assertEqual(actual['version'], 11)
        test.assertIn(expected['version'], (5, 6, 7, 9, 10))
        test.assertNotEqual(actual['program']['identity'], expected['program']['identity'])
        result['version'] = expected['version']
        result['program']['identity'] = expected['program']['identity']
    return result
