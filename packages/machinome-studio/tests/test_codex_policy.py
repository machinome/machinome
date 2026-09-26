# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
import unittest
from floor.backends.codex_policy import CodexPolicyError, validate_effective_config


class CodexPolicyTests(unittest.TestCase):
    def test_inherited_system_layer_is_rejected_even_when_overridden(self):
        with self.assertRaisesRegex(CodexPolicyError, "configuration layer"):
            validate_effective_config({"config": {}, "layers": [{"name": {"type": "system"}, "config": {"mcp_servers": {"bad": {"command": "bad"}}}}], "origins": {}}, {"requirements": None}, {})

    def test_unknown_layer_is_rejected(self):
        with self.assertRaises(CodexPolicyError):
            validate_effective_config({"config": {}, "layers": [{"name": {"type": "unknown"}, "config": {}}], "origins": {}}, {"requirements": None}, {})

    def test_requirements_are_not_overridden(self):
        with self.assertRaisesRegex(CodexPolicyError, "managed"):
            validate_effective_config({"config": {}, "layers": [], "origins": {}}, {"requirements": {"hooks": {}}}, {})

    def test_wrong_effective_value_is_rejected(self):
        with self.assertRaisesRegex(CodexPolicyError, "sandbox_mode"):
            validate_effective_config({"config": {"sandbox_mode": "workspace-write"}, "layers": [{"name": {"type": "sessionFlags"}, "config": {"sandbox_mode": "read-only"}}], "origins": {}}, {"requirements": None}, {"sandbox_mode": "read-only"})
