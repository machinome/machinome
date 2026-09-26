# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
import unittest

from floor.backends.codex_tools import validate_arguments, dynamic_result


class CodexToolsTests(unittest.TestCase):
    def test_floor_schema_rejects_wrong_type_missing_extra_and_boolean_integer(self):
        schema = {"type": "object", "required": ["count"], "additionalProperties": False,
                  "properties": {"count": {"type": "integer"}, "choice": {"type": "string", "enum": ["exact"]}}}
        validate_arguments({"count": 3}, schema)
        for arguments in ({}, {"count": True}, {"count": "3"}, {"count": 3, "other": 1}, {"count": 3, "choice": "wrong"}):
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                validate_arguments(arguments, schema)

    def test_image_and_text_results_preserve_native_content(self):
        response = dynamic_result({"content": [{"type": "image", "mimeType": "image/png", "data": "YWJj"}, {"type": "text", "text": "caption"}]})
        self.assertEqual(response, {"success": True, "contentItems": [{"type": "inputImage", "imageUrl": "data:image/png;base64,YWJj"}, {"type": "inputText", "text": "caption"}]})
