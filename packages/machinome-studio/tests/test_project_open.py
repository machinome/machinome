# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
"""What opening a project is allowed to cost, and what it may present early."""

from __future__ import annotations

import asyncio
import base64
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from floor.preparation import PreparationError
from floor.sessions import Session, SessionRegistry


ROOT = Path(__file__).resolve().parents[1]
FAKE_SOLID = ROOT / "tests" / "fixtures" / "fake_solid.py"
RENDERED_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAFklEQVR4nGP8/+8dAwMDEwMDAwMDAwAjPwLvkz8BYAAAAABJRU5ErkJggg=="
)


class ProjectOpenTest(unittest.IsolatedAsyncioTestCase):
    """Registry-level acceptance for the cost and sequencing of one open."""

    async def asyncSetUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name) / "projects"
        self.home.mkdir()
        self.call_log = Path(self.temporary.name) / "solid-calls.jsonl"
        self.enterContext(patch.dict(os.environ, {
            "GIT_AUTHOR_NAME": "Shop Test",
            "GIT_AUTHOR_EMAIL": "shop@example.invalid",
            "GIT_COMMITTER_NAME": "Shop Test",
            "GIT_COMMITTER_EMAIL": "shop@example.invalid",
            "SOLID_CALL_LOG": str(self.call_log),
        }))
        self.backends: list[object] = []

        def factory(*_args, **_kwargs):
            from tests.fixtures.fake_backend import FakeBackend
            backend = FakeBackend()
            self.backends.append(backend)
            return backend

        self.registry = SessionRegistry(
            self.home,
            shop_root=ROOT,
            solid_command=(sys.executable, str(FAKE_SOLID)),
            backend_factory=factory,
        )
        self.addAsyncCleanup(self.registry.close_all)

    # ── fixtures ────────────────────────────────────────────────────────

    def make_project(self, name: str, profile: str = "builder") -> Path:
        project = self.home / name
        (project / "root").mkdir(parents=True)
        (project / "root" / "__init__.py").write_text("# model\n")
        (project / ".gitignore").write_text(
            "_build/\n.fake-solid-builds\n.fake-solid-state.json\nscreenshot.png\n"
        )
        (project / "pyproject.toml").write_text(f'[tool.libresolid-studio]\nprofile = "{profile}"\n')
        subprocess.run(["git", "init", "-q", "-b", "main", str(project)], check=True)
        subprocess.run(["git", "-C", str(project), "add", "--all"], check=True)
        subprocess.run(
            ["git", "-C", str(project), "commit", "-q", "-m", "fixture"],
            check=True,
        )
        return project

    def build_once(self, project: Path) -> None:
        """Publish the project outside the shop, as a previous run would have."""
        subprocess.run(
            [sys.executable, str(FAKE_SOLID), "build"],
            cwd=project,
            check=True,
            capture_output=True,
        )

    def state(self, project: Path, **values: object) -> None:
        (project / ".fake-solid-state.json").write_text(json.dumps(values))

    async def open(self, name: str) -> Session:
        await self.registry.request_open(name)
        session = await self.registry.wait_until_settled(name)
        self.assertIsNotNone(session, self.registry._failures.get(name))
        assert session is not None
        return session

    def calls(self, command: str) -> int:
        if not self.call_log.is_file():
            return 0
        return sum(
            1 for line in self.call_log.read_text().splitlines()
            if line.startswith(f"{command}:")
        )

    def settled(self, session: Session) -> int:
        return sum(1 for event in session.broker.events if event.kind == "model_build_settled")

    async def wait_until(self, predicate, timeout: float = 5) -> None:
        deadline = asyncio.get_running_loop().time() + timeout
        while asyncio.get_running_loop().time() < deadline:
            if predicate():
                return
            await asyncio.sleep(0.02)
        self.fail("condition did not become true within the timeout")

    # ── one viewer bundle per running shop ──────────────────────────────

    async def test_opening_several_projects_asks_the_framework_for_its_viewer_once(self) -> None:
        self.make_project("alpha")
        self.make_project("bravo")

        alpha = await self.open("alpha")
        bravo = await self.open("bravo")

        self.assertEqual(self.calls("viewer"), 1)
        self.assertEqual(alpha.prepared.viewer_bundle, bravo.prepared.viewer_bundle)
        self.assertEqual(alpha.prepared.viewer_api_version, 10)

        await self.registry.request_close(alpha.id)
        reopened = await self.open("alpha")

        self.assertEqual(self.calls("viewer"), 1)
        self.assertEqual(reopened.prepared.viewer_bundle, alpha.prepared.viewer_bundle)

    # ── rendering only when the open changed the model ──────────────────

    async def test_an_open_that_publishes_nothing_renders_no_screenshot(self) -> None:
        project = self.make_project("engine")
        first = await self.open("engine")
        await self.registry.request_close(first.id)
        screenshot = project / "screenshot.png"
        self.assertTrue(screenshot.is_file())
        before = (screenshot.read_bytes(), screenshot.stat().st_mtime_ns)
        renders = self.calls("snapshot")

        session = await self.open("engine")
        await self._settled_build(session)

        self.assertEqual(self.calls("snapshot"), renders)
        self.assertEqual((screenshot.read_bytes(), screenshot.stat().st_mtime_ns), before)

    async def test_an_open_that_publishes_nothing_still_renders_a_missing_screenshot(self) -> None:
        project = self.make_project("engine")
        first = await self.open("engine")
        await self.registry.request_close(first.id)
        (project / "screenshot.png").unlink()
        renders = self.calls("snapshot")

        session = await self.open("engine")
        await self._settled_build(session)
        await self.wait_until(lambda: (project / "screenshot.png").is_file())

        self.assertEqual(self.calls("snapshot"), renders + 1)

    async def test_an_open_that_publishes_new_work_renders_exactly_one_screenshot(self) -> None:
        project = self.make_project("engine")
        self.build_once(project)
        (project / "screenshot.png").write_bytes(RENDERED_PNG)
        renders = self.calls("snapshot")
        self.state(project, viewer={"version": 1, "root": {"name": "part", "model": "part.stl", "revision": 2}})

        session = await self.open("engine")
        await self._settled_build(session)
        await self.wait_until(lambda: self.calls("snapshot") >= renders + 1)
        await asyncio.sleep(0.4)

        self.assertEqual(self.calls("snapshot"), renders + 1)

    # ── presenting an existing publication ──────────────────────────────

    async def test_a_complete_publication_opens_before_its_build_finishes(self) -> None:
        project = self.make_project("engine")
        self.build_once(project)
        (project / "screenshot.png").write_bytes(RENDERED_PNG)
        self.state(project, build_delay=1.5)

        started = asyncio.get_running_loop().time()
        session = await self.open("engine")
        opening = asyncio.get_running_loop().time() - started

        self.assertLess(opening, 1.5, "the open awaited a build it could have run behind the session")
        self.assertIsNotNone(session.build_task)
        assert session.build_task is not None
        self.assertFalse(session.build_task.done())
        self.assertTrue(session.model_building)
        self.assertEqual(list(session.broker.agents), ["builder"])
        projects = {item["path"]: item for item in await self.registry.entries()}
        self.assertTrue(projects["engine"]["model_building"])

        await self._settled_build(session)

        self.assertFalse(session.model_building)
        projects = {item["path"]: item for item in await self.registry.entries()}
        self.assertFalse(projects["engine"]["model_building"])

    async def test_an_unbuilt_project_waits_for_its_build_before_opening(self) -> None:
        project = self.make_project("engine")
        self.state(project, build_delay=0.2)

        session = await self.open("engine")

        self.assertIsNone(session.build_task)
        self.assertFalse(session.model_building)
        self.assertTrue((project / "_build" / "viewer.json").is_file())
        self.assertTrue((project / "screenshot.png").is_file())

    async def test_a_created_project_waits_for_its_build_before_opening(self) -> None:
        await self.registry.create("", "new_engine", "builder")
        session = await self.registry.wait_until_settled("new_engine")
        self.assertIsNotNone(session, self.registry._failures.get("new_engine"))
        assert session is not None

        project = self.home / "new_engine"
        self.assertIsNone(session.build_task)
        self.assertTrue((project / "_build" / "viewer.json").is_file())
        self.assertTrue((project / "screenshot.png").is_file())

    async def test_a_build_failing_behind_an_open_session_keeps_the_publication(self) -> None:
        project = self.make_project("engine")
        self.build_once(project)
        (project / "screenshot.png").write_bytes(RENDERED_PNG)
        published = (project / "_build" / "viewer.json").read_text()
        self.state(project, fail="broken model evidence")

        session = await self.open("engine")
        self.assertIsNotNone(session.build_task, "the failing build ran behind the open session")
        await self._settled_build(session)

        self.assertIn("broken model evidence", session.broker.model_build_error or "")
        self.assertTrue(
            any(event.kind == "model_build_unavailable" for event in session.broker.events)
        )
        self.assertEqual((project / "_build" / "viewer.json").read_text(), published)

    async def test_closing_a_session_ends_the_build_running_behind_it(self) -> None:
        project = self.make_project("engine")
        self.build_once(project)
        (project / "screenshot.png").write_bytes(RENDERED_PNG)
        self.state(project, build_delay=1.0)

        session = await self.open("engine")
        build = session.build_task
        assert build is not None
        await self.registry.request_close(session.id)

        self.assertTrue(build.done())

    # ── telling the session the build behind it is over ─────────────────

    async def test_a_build_that_publishes_nothing_still_says_the_model_settled(self) -> None:
        project = self.make_project("engine")
        first = await self.open("engine")
        await self.registry.request_close(first.id)
        published = (project / "_build" / "viewer.json").read_text()

        session = await self.open("engine")
        self.assertTrue(session.broker.run()["model_building"])
        await self._settled_build(session)

        self.assertEqual((project / "_build" / "viewer.json").read_text(), published)
        self.assertEqual(self.settled(session), 1)
        self.assertFalse(session.broker.run()["model_building"])
        # Nothing was republished, so no watcher spoke: without the settled
        # event this session would say "bringing the model up to date" forever.
        self.assertEqual(
            [event.kind for event in session.broker.events if event.kind.startswith("model_")],
            ["model_build_settled"],
        )

    async def test_a_build_that_publishes_new_work_says_the_model_settled(self) -> None:
        project = self.make_project("engine")
        self.build_once(project)
        (project / "screenshot.png").write_bytes(RENDERED_PNG)
        self.state(project, viewer={"version": 1, "root": {"name": "part", "model": "part.stl", "revision": 2}})

        session = await self.open("engine")
        await self._settled_build(session)

        self.assertEqual(self.settled(session), 1)
        self.assertFalse(session.broker.run()["model_building"])

    async def test_a_build_that_fails_says_the_model_settled_as_well_as_why(self) -> None:
        project = self.make_project("engine")
        self.build_once(project)
        (project / "screenshot.png").write_bytes(RENDERED_PNG)
        self.state(project, fail="broken model evidence")

        session = await self.open("engine")
        await self._settled_build(session)

        self.assertEqual(self.settled(session), 1)
        self.assertFalse(session.broker.run()["model_building"])
        self.assertIn("broken model evidence", session.broker.model_build_error or "")

    async def test_the_session_stream_carries_the_build_it_opened_ahead_of(self) -> None:
        """A browser reaching the session mid-build is told, and told it ended.

        The subscriber here stands for that browser: it registers while the
        build is held open, so nothing it needs can have been published before
        it was listening.
        """
        project = self.make_project("engine")
        self.build_once(project)
        (project / "screenshot.png").write_bytes(RENDERED_PNG)
        gate = Path(self.temporary.name) / "release-build"
        self.state(project, build_gate=str(gate))

        session = await self.open("engine")
        subscriber, snapshot = session.broker.subscribe_snapshot()
        self.assertTrue(snapshot["run"]["model_building"])
        assert session.build_task is not None
        self.assertFalse(session.build_task.done())

        gate.write_text("go\n")
        await self._settled_build(session)

        live = []
        while not subscriber.empty():
            live.append(subscriber.get_nowait()["kind"])
        self.assertIn("model_build_settled", live)

    async def test_a_publication_does_not_open_a_directory_that_is_not_a_repository(self) -> None:
        project = self.home / "loose"
        (project / "root").mkdir(parents=True)
        (project / "root" / "__init__.py").write_text("# model\n")
        self.build_once(project)

        with self.assertRaises(PreparationError) as raised:
            await self.registry.request_open("loose")

        self.assertIn("not a project repository", str(raised.exception))
        self.assertIsNone(self.registry.by_entry("loose"))
        self.assertEqual(self.backends, [])

    async def _settled_build(self, session: Session) -> None:
        if session.build_task is not None:
            await session.build_task


if __name__ == "__main__":
    unittest.main()
