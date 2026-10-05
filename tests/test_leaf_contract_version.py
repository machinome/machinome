# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The leaf contract is versioned, and a declaration is checked when its
class is created (OpenSpec change `leaf-contract`, capability
`leaf-contract`, ADR-165; version 3 by the change `brep-mesh`)."""

import ast
import os
from unittest import TestCase
from unittest.mock import patch

BASEDIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(BASEDIR)
LEAF = os.path.join(REPO_DIR, 'machinome', 'node', 'leaf.py')


def _bases():
    from machinome.node.brep_leaf import BrepLeafNode
    from machinome.node.flexible import FlexibleNode
    from machinome.node.leaf import LeafNode
    from machinome.node.sheet_leaf import SheetLeafNode
    return (LeafNode, BrepLeafNode, SheetLeafNode, FlexibleNode)


def declaring(base, value):
    class Declaring(base):
        leaf_contract = value
    return Declaring


class ContractVersionTest(TestCase):

    def test_the_core_speaks_contract_three(self):
        from machinome.node import leaf
        self.assertEqual(leaf.CONTRACT, 3)
        self.assertIs(type(leaf.CONTRACT), int)

    def test_the_version_is_an_integer_literal_in_the_source(self):
        with open(LEAF) as handle:
            tree = ast.parse(handle.read())
        values = [node.value for node in tree.body
                  if isinstance(node, ast.Assign)
                  and [target.id for target in node.targets
                       if isinstance(target, ast.Name)] == ['CONTRACT']]
        self.assertEqual(len(values), 1)
        self.assertIsInstance(values[0], ast.Constant)
        self.assertIs(type(values[0].value), int)

    def test_the_base_documents_an_undeclared_contract(self):
        from machinome.node.leaf import LeafNode
        self.assertIsNone(LeafNode.leaf_contract)

    def test_a_matching_declaration_is_admitted(self):
        for base in _bases():
            with self.subTest(base=base.__name__):
                self.assertEqual(declaring(base, 3).leaf_contract, 3)

    def test_a_mismatched_declaration_is_refused_naming_both_versions(self):
        for base in _bases():
            for value in (1, 2, '3', True):
                with self.subTest(base=base.__name__, value=value):
                    with self.assertRaises(TypeError) as refused:
                        declaring(base, value)
                    message = str(refused.exception)
                    self.assertIn('Declaring', message)
                    self.assertIn(repr(value), message)
                    self.assertIn('3', message.replace(repr(value), ''))
                    self.assertIn('machinome.node.leaf', message)

    def test_an_undeclared_subclass_is_not_checked(self):
        from machinome.node.cadquery import CadQueryNode
        from machinome.node.leaf import LeafNode
        declared = declaring(LeafNode, 3)
        with patch('machinome.node.leaf.CONTRACT', 4):
            class Inherits(declared):
                pass

            class ProjectLeaf(CadQueryNode):
                pass

            class Plain(LeafNode):
                pass

            class ExplicitlyUndeclared(LeafNode):
                leaf_contract = None
        self.assertEqual(Inherits.leaf_contract, 3)
        self.assertIsNone(ProjectLeaf.leaf_contract)
        self.assertIsNone(Plain.leaf_contract)
        self.assertIsNone(ExplicitlyUndeclared.leaf_contract)
