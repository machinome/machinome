# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
import asyncio
import tempfile
import json
from types import SimpleNamespace
from pathlib import Path
import unittest
from unittest.mock import AsyncMock, patch

from floor.backends.codex_qualification import CodexQualifier, _registry
from floor.backends.codex_policy import CodexPolicyError, controlled_catalogue, validate_schema


class CodexQualificationTests(unittest.IsolatedAsyncioTestCase):
    async def test_cache_invalidates_binary_schema_registry_and_effective_policy(self):
        with tempfile.TemporaryDirectory() as temporary:
            binary = Path(temporary) / "native"
            binary.write_bytes(b"first")
            qualifier = CodexQualifier()
            qualifier._configuration = AsyncMock(return_value={"policy":"first"})
            qualifier._probe = AsyncMock(return_value=31)
            with patch("floor.backends.codex_qualification.codex_binary", return_value=binary), \
                 patch("floor.backends.codex_qualification.controlled_catalogue", return_value={"models":[]}):
                self.assertFalse((await qualifier.qualify([]))["cached"])
                self.assertTrue((await qualifier.qualify([]))["cached"])
                binary.write_bytes(b"changed")
                self.assertFalse((await qualifier.qualify([]))["cached"])
                qualifier._configuration.return_value = {"policy":"changed"}
                self.assertFalse((await qualifier.qualify([]))["cached"])
                self.assertFalse((await qualifier.qualify([[{"name":"new-tool"}]]))["cached"])
                with patch("floor.backends.codex_qualification.SCHEMA_FINGERPRINTS", {"drift":"changed"}):
                    self.assertFalse((await qualifier.qualify([]))["cached"])
            self.assertEqual(qualifier._probe.await_count, 5)

    def test_extra_namespace_and_native_skill_instructions_fail_registry_proof(self):
        for request in ({"tools":[{"type":"function","name":"native"}]},
                        {"input":[{"type":"message","content":"<skills_instructions>untrusted"}]}):
            with self.assertRaises(CodexPolicyError):
                _registry(request)

    async def test_probe_failure_is_never_cached(self):
        with tempfile.TemporaryDirectory() as temporary:
            binary = Path(temporary) / "native"
            binary.write_bytes(b"first")
            qualifier = CodexQualifier()
            qualifier._configuration = AsyncMock(return_value={})
            qualifier._probe = AsyncMock(side_effect=CodexPolicyError("expanded registry"))
            with patch("floor.backends.codex_qualification.codex_binary", return_value=binary), \
                 patch("floor.backends.codex_qualification.controlled_catalogue", return_value={"models":[]}):
                for _ in range(2):
                    with self.assertRaises(CodexPolicyError):
                        await qualifier.qualify([])
            self.assertEqual(qualifier._probe.await_count, 2)

    def test_changed_bundled_model_metadata_refuses_runtime(self):
        result = SimpleNamespace(stdout=json.dumps({"models":[{"slug":"gpt-6-sol"},{"slug":"gpt-6-astra"}]}).encode())
        with patch("floor.backends.codex_policy.subprocess.run", return_value=result) as invocation:
            with self.assertRaisesRegex(CodexPolicyError, "metadata differs"):
                controlled_catalogue(Path("/synthetic/native"))
            self.assertNotEqual(invocation.call_args.kwargs["cwd"], Path.cwd())
            self.assertNotIn("OPENAI_API_KEY", invocation.call_args.kwargs["env"])

    def test_changed_schema_types_refuse_runtime(self):
        with tempfile.TemporaryDirectory() as temporary:
            private = Path(temporary)
            output = private / "schemas" / "v2"
            output.mkdir(parents=True)
            (output / "ThreadStartParams.json").write_text(json.dumps({"properties": {
                name: {"type":"string"} for name in ("environments","dynamicTools","sandbox","approvalPolicy","baseInstructions")}}))
            with patch("floor.backends.codex_policy.subprocess.run"):
                with self.assertRaisesRegex(CodexPolicyError, "schema"):
                    validate_schema(Path("/synthetic/native"), private, {})

    async def test_bounded_probe_timeout_never_creates_success_cache(self):
        with tempfile.TemporaryDirectory() as temporary:
            binary = Path(temporary) / "native"
            binary.write_bytes(b"first")
            qualifier = CodexQualifier()
            qualifier._configuration = AsyncMock(return_value={})
            async def never(*_):
                await asyncio.sleep(30)
            qualifier._probe = never
            with patch("floor.backends.codex_qualification.codex_binary", return_value=binary), \
                 patch("floor.backends.codex_qualification.controlled_catalogue", return_value={"models":[]}), \
                 patch("floor.backends.codex_qualification.PROBE_TIMEOUT", 0.01):
                with self.assertRaises(TimeoutError):
                    await qualifier.qualify([])
            self.assertEqual(qualifier._successes, set())
