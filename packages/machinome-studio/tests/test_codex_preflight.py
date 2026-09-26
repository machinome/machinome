# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Qualification failure cannot prepare or render a selected project."""
import asyncio
from dataclasses import replace
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

from floor.profiles import load_profile, resolve_profile_runtime
from floor.sessions import SessionRegistry

ROOT = Path(__file__).resolve().parents[1]


class CodexPreflightTests(unittest.IsolatedAsyncioTestCase):
    async def test_qualification_failure_precedes_every_project_effect(self):
        with tempfile.TemporaryDirectory() as temporary:
            service = SimpleNamespace(acquire=AsyncMock(side_effect=RuntimeError("qualification failed")), close=AsyncMock())
            registry = SessionRegistry(Path(temporary), shop_root=ROOT, codex_service=service)
            profile = resolve_profile_runtime(load_profile("builder", shop_root=ROOT))
            agent = profile.agents[0]
            profile = replace(profile, agents=(replace(agent, runtime=replace(agent.runtime, backend="codex", model="gpt-6-sol")),))
            entry = SimpleNamespace(path="synthetic", project_root=Path(temporary))
            with patch("floor.sessions.read_project_runtime"), patch("floor.sessions.load_profile"), \
                 patch("floor.sessions.resolve_profile_runtime", return_value=profile), \
                 patch("floor.sessions.prepare_project") as preparation, \
                 patch.object(registry, "_viewer_bundle", AsyncMock()) as viewer:
                self.assertIsNone(await registry._open(entry, create_profile=None))
                preparation.assert_not_called()
                viewer.assert_not_awaited()
                self.assertIn("qualification failed", registry._failures["synthetic"])
            await registry.close_all()

    async def test_pre_session_failure_releases_pending_reference(self):
        with tempfile.TemporaryDirectory() as temporary:
            reference = SimpleNamespace(close=AsyncMock())
            service = SimpleNamespace(acquire=AsyncMock(return_value=reference), close=AsyncMock())
            registry = SessionRegistry(Path(temporary), shop_root=ROOT, codex_service=service)
            profile = resolve_profile_runtime(load_profile("builder", shop_root=ROOT))
            agent = profile.agents[0]
            profile = replace(profile, agents=(replace(agent, runtime=replace(agent.runtime, backend="codex", model="gpt-6-sol")),))
            entry = SimpleNamespace(path="synthetic", project_root=Path(temporary))
            with patch("floor.sessions.read_project_runtime"), patch("floor.sessions.load_profile"), \
                 patch("floor.sessions.resolve_profile_runtime", return_value=profile), \
                 patch("floor.sessions.prepare_project", side_effect=RuntimeError("preparation failed")), \
                 patch.object(registry, "_viewer_bundle", AsyncMock()):
                self.assertIsNone(await registry._open(entry, create_profile=None))
                reference.close.assert_awaited_once()
            await registry.close_all()

    async def test_claude_only_composition_needs_no_home_or_codex(self):
        with tempfile.TemporaryDirectory() as temporary, patch.dict("os.environ", {}, clear=True):
            registry = SessionRegistry(Path(temporary), shop_root=ROOT)
            await registry.close_all()
