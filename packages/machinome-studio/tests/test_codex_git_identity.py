# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
from dataclasses import replace
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from floor.backends.base import RoleContext
from floor.backends.codex_tools import FloorWorker
from floor.profiles import load_profile, resolve_profile_runtime

ROOT = Path(__file__).resolve().parents[1]


class CodexGitIdentityTests(unittest.IsolatedAsyncioTestCase):
    async def exercise(self, signed=False):
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            project = parent / "project"
            project.mkdir()
            operator = parent / "operator"
            operator.mkdir()
            (operator / ".gitconfig").write_text('[user]\nname = Synthetic Maker\nemail = maker@example.invalid\n' + ('[commit]\ngpgsign = true\n' if signed else ''))
            subprocess.run(["git", "init", "-q", str(project)], check=True)
            (project / "openspec").mkdir()
            (project / "openspec" / "planning.md").write_text("Synthetic planning record\n")
            subprocess.run(["git", "-C", str(project), "add", "openspec/planning.md"], check=True)
            agent = resolve_profile_runtime(load_profile("builder", shop_root=ROOT)).user_agent
            agent = replace(agent, skills=())
            context = RoleContext(str(ROOT), str(project), agent, "builder", "Maker", "Builder")
            worker = FloorWorker(context, machinome_command=("unused",), broker_url="http://unused", session_id="synthetic")
            with patch.dict(os.environ, {"HOME": str(operator), "PATH": os.environ["PATH"]}, clear=True):
                await worker.start()
            try:
                result = await worker.rpc("tools/call", {"name": "git_commit", "arguments": {"message": "Synthetic planning"}})
                if signed:
                    self.assertTrue(result["isError"])
                    self.assertIn("signed commits", result["content"][0]["text"])
                    self.assertNotEqual(subprocess.run(["git", "-C", str(project), "rev-parse", "HEAD"], capture_output=True).returncode, 0)
                else:
                    self.assertFalse(result["isError"], result)
                    value = subprocess.run(["git", "-C", str(project), "log", "-1", "--format=%an <%ae>"], check=True, capture_output=True, text=True).stdout.strip()
                    self.assertEqual(value, "Synthetic Maker <maker@example.invalid>")
                self.assertFalse((Path(worker.private.name) / ".gitconfig").exists())
            finally:
                await worker.close()

    async def test_plain_identity_only_in_operator_global_config_is_preserved(self):
        await self.exercise()

    async def test_required_global_signing_is_not_silently_downgraded(self):
        await self.exercise(signed=True)

    async def test_signed_openspec_setup_refuses_before_initialization(self):
        from floor.mcp_server import ProjectTools
        from unittest.mock import Mock
        with tempfile.TemporaryDirectory() as temporary:
            tools = ProjectTools(Path(temporary), git_signing_required=True)
            tools._run_openspec = Mock(return_value={"ok": False, "stderr": "initialization attempted"})
            tools._git = Mock()
            with self.assertRaisesRegex(RuntimeError, "signed commits"):
                tools.openspec_setup()
            tools._run_openspec.assert_not_called()
            tools._git.assert_not_called()
            self.assertFalse((Path(temporary) / "openspec").exists())
