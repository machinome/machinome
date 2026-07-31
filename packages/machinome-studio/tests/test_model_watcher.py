"""The floor keeps the maker's model view current on its own.

Until now `model_changed` had exactly one source: a POST from a `solid
develop --callback` process the machinist was told to start and keep
alive. A maker editing a file by hand, or a designer, or a machinist that
never started the process, got a silently stale view. These tests drive
the watcher that replaces it, and the failure reporting that replaces the
old silence.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from floor.app import Broker, create_app
from floor.watcher import ModelWatcher


ROOT = Path(__file__).resolve().parents[1]
FAKE_SOLID = ROOT / "tests" / "fixtures" / "fake_solid.py"
SOLID_COMMAND = (sys.executable, str(FAKE_SOLID))
POLL = 0.02


def build_state(project: Path, **state: object) -> None:
    """Steer the next fake build: fail, or publish given viewer content."""
    (project / ".fake-solid-state.json").write_text(json.dumps(state))


class WatcherTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name) / "project"
        (self.project / "root").mkdir(parents=True)
        self.model = self.project / "root" / "__init__.py"
        self.model.write_text("# model\n")
        self.artifacts = self.project / "_build"
        await self.build_once()
        self.published: list[tuple[str, dict]] = []

    async def build_once(self) -> None:
        process = await asyncio.create_subprocess_exec(
            *SOLID_COMMAND, "build", "root", cwd=self.project,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()

    def record(self, kind: str, payload: dict) -> None:
        self.published.append((kind, payload))

    def kinds(self) -> list[str]:
        return [kind for kind, _ in self.published]

    def payload(self, kind: str) -> dict:
        return next(payload for published, payload in self.published if published == kind)

    def watcher(self) -> ModelWatcher:
        return ModelWatcher(
            self.project,
            self.artifacts,
            SOLID_COMMAND,
            self.record,
            poll_interval=POLL,
        )

    async def run_until(self, watcher: ModelWatcher, kind: str, *, edit: str | None = None, timeout: float = 10.0) -> None:
        """Run the watcher until it publishes `kind`, then stop it.

        An `edit` is applied after the watcher has taken its baseline —
        editing before it starts is indistinguishable from the project's
        settled state, which is correct behaviour and not what these
        tests are about.
        """
        task = asyncio.create_task(watcher.run())
        deadline = asyncio.get_running_loop().time() + timeout
        try:
            if edit is not None:
                await asyncio.sleep(POLL * 2)
                self.touch_model(edit)
            while kind not in self.kinds():
                if task.done():
                    await task
                    self.fail(f"watcher stopped before publishing {kind}")
                if asyncio.get_running_loop().time() > deadline:
                    self.fail(f"timed out waiting for {kind}; saw {self.kinds()}")
                await asyncio.sleep(POLL / 2)
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    async def settle(self, watcher: ModelWatcher, *, seconds: float = 0.6) -> None:
        """Run the watcher for a fixed spell and stop it."""
        task = asyncio.create_task(watcher.run())
        try:
            await asyncio.sleep(seconds)
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    def touch_model(self, body: str) -> None:
        self.model.write_text(body)
        stamp = self.model.stat().st_mtime + 10
        os.utime(self.model, (stamp, stamp))


class ModelRefreshTest(WatcherTestCase):

    async def test_a_source_change_refreshes_the_view_with_no_agent_action(self) -> None:
        """Nobody posts a callback and no agent runs: the floor notices."""
        build_state(self.project, viewer={"version": 1, "root": {"name": "part", "model": "part.stl"}, "revision": 2})
        watcher = self.watcher()

        await self.run_until(watcher, "model_changed", edit="# edited by the maker, by hand\n")

        self.assertIn("model_changed", self.kinds())

    async def test_a_rebuild_that_changes_nothing_reports_no_model_change(self) -> None:
        """The published snapshot is the signal, not the fact of a build."""
        watcher = self.watcher()

        await self.run_until(watcher, "model_build_succeeded", edit="# a comment the model does not depend on\n")
        await asyncio.sleep(POLL * 4)

        self.assertNotIn("model_changed", self.kinds())

    async def test_an_unchanged_project_builds_nothing(self) -> None:
        """No edit, no build. The watcher must not trigger itself."""
        watcher = self.watcher()

        await self.settle(watcher)

        self.assertEqual(self.kinds(), [])

    async def test_writes_into_the_build_tree_do_not_trigger_a_build(self) -> None:
        """A build writes into the build tree; seeing that would loop forever."""
        watcher = self.watcher()
        for directory in ("_build", "_build.abc12345", ".solid-node-build-xyz", "__pycache__", ".git"):
            noise = self.project / directory
            noise.mkdir(exist_ok=True)
            (noise / "generated.py").write_text("# written by the build\n")

        await self.settle(watcher)

        self.assertEqual(self.kinds(), [])


class FailedRebuildTest(WatcherTestCase):

    async def test_a_failed_rebuild_is_reported_with_its_diagnostic(self) -> None:
        """Under the callback design a failed rebuild sent nothing at all."""
        build_state(self.project, fail="the model source is broken")
        watcher = self.watcher()

        await self.run_until(watcher, "model_build_failed", edit="# broken\n")

        self.assertIn("the model source is broken", self.payload("model_build_failed")["error"])

    async def test_the_previous_model_stays_inspectable_after_a_failure(self) -> None:
        before = (self.artifacts / "viewer.json").read_bytes()
        build_state(self.project, fail="broken")
        watcher = self.watcher()

        await self.run_until(watcher, "model_build_failed", edit="# broken\n")

        self.assertEqual((self.artifacts / "viewer.json").read_bytes(), before)
        self.assertNotIn("model_changed", self.kinds())

    async def test_a_later_success_clears_the_failure(self) -> None:
        build_state(self.project, fail="broken")
        watcher = self.watcher()
        await self.run_until(watcher, "model_build_failed", edit="# broken\n")

        self.published.clear()
        build_state(self.project, viewer={"version": 1, "root": {"name": "part", "model": "part.stl"}, "revision": 3})
        await self.run_until(watcher, "model_build_succeeded", edit="# fixed\n")

        self.assertIn("model_build_succeeded", self.kinds())

    async def test_a_missing_solid_command_reports_a_failure_rather_than_dying(self) -> None:
        watcher = ModelWatcher(
            self.project, self.artifacts, ("/nonexistent/solid",), self.record, poll_interval=POLL,
        )

        await self.run_until(watcher, "model_build_failed", edit="# edited\n")

        self.assertIn("model_build_failed", self.kinds())


class WatcherWiringTest(WatcherTestCase):
    """D1: the watcher belongs to the app lifespan, so broker-only mode
    behaves the same as a full orchestrated floor."""

    async def test_the_app_lifespan_runs_the_watcher(self) -> None:
        broker = Broker()
        published: list[str] = []
        original = broker.publish
        broker.publish = lambda kind, payload=None: (published.append(kind), original(kind, payload))[1]

        build_state(self.project, viewer={"version": 1, "root": {"name": "part", "model": "part.stl"}, "revision": 4})
        app = create_app(
            self.project,
            artifact_root=self.artifacts,
            broker=broker,
            solid_command=SOLID_COMMAND,
            poll_interval=POLL,
        )
        async with app.router.lifespan_context(app):
            await asyncio.sleep(POLL * 2)
            self.touch_model("# edited while the floor is open\n")
            for _ in range(400):
                if "model_changed" in published:
                    break
                await asyncio.sleep(POLL / 2)

        self.assertIn("model_changed", published)

    async def test_an_app_without_a_solid_command_runs_no_watcher(self) -> None:
        """Existing API tests must not gain build subprocesses."""
        app = create_app(self.project, artifact_root=self.artifacts, broker=Broker())
        async with app.router.lifespan_context(app):
            self.touch_model("# edited\n")
            await asyncio.sleep(POLL * 8)

        self.assertIsNone(getattr(app.state, "model_watcher", None))


if __name__ == "__main__":
    unittest.main()
