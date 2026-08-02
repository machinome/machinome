"""Regression coverage for S1's source-build and publication-event pipeline."""

from __future__ import annotations

import asyncio
import json
import os
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

from floor.app import Broker, create_app


ROOT = Path(__file__).resolve().parents[1]
FAKE_SOLID = ROOT / "tests" / "fixtures" / "fake_solid.py"
SOLID_COMMAND = (sys.executable, str(FAKE_SOLID))
SETTLE = 0.04


def build_state(project: Path, **state: object) -> None:
    (project / ".fake-solid-state.json").write_text(json.dumps(state))


def atomic_publish(root: Path, name: str, content: str) -> None:
    target = root / name
    temporary = root / f".{name}.temporary"
    temporary.write_text(content)
    os.replace(temporary, target)


class WatcherTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name) / "project"
        self.model = self.project / "root" / "__init__.py"
        self.model.parent.mkdir(parents=True)
        self.model.write_text("# model\n")
        self.artifacts = self.project / "_build"
        await self.build_once()

    async def build_once(self) -> None:
        process = await asyncio.create_subprocess_exec(*SOLID_COMMAND, "build", "root", cwd=self.project)
        self.assertEqual(await process.wait(), 0)

    async def wait_for(self, events: list[tuple[str, dict[str, object]]], kind: str, *, timeout: float = 3) -> dict[str, object]:
        deadline = asyncio.get_running_loop().time() + timeout
        while asyncio.get_running_loop().time() < deadline:
            for actual_kind, payload in events:
                if actual_kind == kind:
                    return payload
            await asyncio.sleep(0.01)
        self.fail(f"timed out waiting for {kind}; saw {[item[0] for item in events]}")

    def app(self, *, solid_command: tuple[str, ...] | None = SOLID_COMMAND) -> tuple[object, list[tuple[str, dict[str, object]]]]:
        broker = Broker()
        events: list[tuple[str, dict[str, object]]] = []
        original = broker.publish

        def record(kind: str, payload: object, **kwargs: object):
            if isinstance(payload, dict):
                events.append((kind, payload))
            return original(kind, payload, **kwargs)

        broker.publish = record  # type: ignore[method-assign]
        return create_app(
            self.project,
            artifact_root=self.artifacts,
            broker=broker,
            solid_command=solid_command,
            settle_delay=SETTLE,
        ), events


class ArtifactWatcherTest(WatcherTestCase):
    async def test_atomic_rename_reports_exactly_one_named_artifact(self) -> None:
        app, events = self.app(solid_command=None)
        async with app.router.lifespan_context(app):  # type: ignore[attr-defined]
            atomic_publish(self.artifacts, "leaf.stl", "new leaf")
            payload = await self.wait_for(events, "model_artifact_changed")
        self.assertEqual(payload, {"artifact": "leaf.stl"})
        self.assertEqual([kind for kind, _ in events], ["model_artifact_changed"])

    async def test_external_build_output_is_forwarded_without_a_source_build(self) -> None:
        app, events = self.app(solid_command=None)
        async with app.router.lifespan_context(app):  # type: ignore[attr-defined]
            atomic_publish(self.artifacts, "other.stl", "external build")
            await self.wait_for(events, "model_artifact_changed")
        self.assertEqual(events[0][1], {"artifact": "other.stl"})

    async def test_republishing_one_of_three_artifacts_reports_only_that_artifact(self) -> None:
        for name in ("one.stl", "two.stl", "three.stl"):
            (self.artifacts / name).write_text(name)
        app, events = self.app(solid_command=None)
        async with app.router.lifespan_context(app):  # type: ignore[attr-defined]
            atomic_publish(self.artifacts, "two.stl", "new two")
            await self.wait_for(events, "model_artifact_changed")
            await asyncio.sleep(SETTLE * 2)
        self.assertEqual(events, [("model_artifact_changed", {"artifact": "two.stl"})])

    async def test_deletion_and_direct_write_are_silent_until_rename(self) -> None:
        app, events = self.app(solid_command=None)
        async with app.router.lifespan_context(app):  # type: ignore[attr-defined]
            (self.artifacts / "part.stl").unlink()
            (self.artifacts / "draft.stl").write_text("not published")
            await asyncio.sleep(SETTLE * 3)
            self.assertEqual(events, [])
            atomic_publish(self.artifacts, "draft.stl", "published")
            payload = await self.wait_for(events, "model_artifact_changed")
        self.assertEqual(payload, {"artifact": "draft.stl"})

    async def test_errors_file_uses_the_same_event_path(self) -> None:
        app, events = self.app(solid_command=None)
        async with app.router.lifespan_context(app):  # type: ignore[attr-defined]
            atomic_publish(self.artifacts, "errors.json", "broken model")
            payload = await self.wait_for(events, "model_artifact_changed")
        self.assertEqual(payload, {"artifact": "errors.json"})

    async def test_startup_does_not_announce_existing_artifacts(self) -> None:
        app, events = self.app(solid_command=None)
        async with app.router.lifespan_context(app):  # type: ignore[attr-defined]
            await asyncio.sleep(SETTLE * 3)
        self.assertEqual(events, [])


class SourceWatcherTest(WatcherTestCase):
    async def test_source_burst_coalesces_to_one_build_and_ignores_build_tree(self) -> None:
        build_state(self.project, viewer={"version": 1, "root": {"name": "part", "model": "part.stl"}, "revision": 2})
        app, events = self.app()
        async with app.router.lifespan_context(app):  # type: ignore[attr-defined]
            self.model.write_text("# first\n")
            self.model.write_text("# second\n")
            await self.wait_for(events, "model_artifact_changed")
            await asyncio.sleep(SETTLE * 3)
            published = [payload["artifact"] for kind, payload in events if kind == "model_artifact_changed"]
            self.assertEqual(published.count("viewer.json"), 1)
            events.clear()
            atomic_publish(self.artifacts, "generated.py", "# output")
            await asyncio.sleep(SETTLE * 3)
        self.assertEqual([kind for kind, _ in events], ["model_artifact_changed"])

    async def test_unavailable_build_command_has_its_own_event(self) -> None:
        app, events = self.app(solid_command=("/not/a/solid",))
        async with app.router.lifespan_context(app):  # type: ignore[attr-defined]
            self.model.write_text("# trigger\n")
            payload = await self.wait_for(events, "model_build_unavailable")
        self.assertIn("/not/a/solid", str(payload["reason"]))

    async def test_failed_build_forwards_its_error_record_without_a_verdict_event(self) -> None:
        build_state(self.project, fail="broken model")
        app, events = self.app()
        async with app.router.lifespan_context(app):  # type: ignore[attr-defined]
            self.model.write_text("# broken\n")
            payload = await self.wait_for(events, "model_artifact_changed")
        self.assertEqual(payload, {"artifact": "errors.json"})
        self.assertEqual([kind for kind, _ in events], ["model_artifact_changed"])

    async def test_project_directories_named_build_prefix_are_watched(self) -> None:
        prefixed = self.project / "_build.source" / "part.py"
        prefixed.parent.mkdir()
        build_state(self.project, viewer={"version": 1, "root": {"name": "part", "model": "part.stl"}, "revision": 3})
        app, events = self.app()
        async with app.router.lifespan_context(app):  # type: ignore[attr-defined]
            prefixed.write_text("# project code\n")
            payload = await self.wait_for(events, "model_artifact_changed")
        self.assertIn(payload["artifact"], {"part.stl", "viewer.json"})

    async def test_app_without_solid_command_observes_output_but_has_no_source_handler(self) -> None:
        app, events = self.app(solid_command=None)
        async with app.router.lifespan_context(app):  # type: ignore[attr-defined]
            self.assertIsNone(app.state.model_watcher)  # type: ignore[attr-defined]
            atomic_publish(self.artifacts, "outside.stl", "changed")
            await self.wait_for(events, "model_artifact_changed")
        self.assertIsNotNone(app.state.artifact_watcher)  # type: ignore[attr-defined]

    async def test_observer_stops_on_lifespan_shutdown(self) -> None:
        app, _ = self.app()
        async with app.router.lifespan_context(app):  # type: ignore[attr-defined]
            observer = app.state.observer  # type: ignore[attr-defined]
            self.assertTrue(observer.is_alive())
        self.assertFalse(observer.is_alive())


class ArtifactRouteTest(WatcherTestCase):
    async def test_route_serves_a_stable_artifact_during_another_republication(self) -> None:
        app = create_app(self.project, artifact_root=self.artifacts, broker=Broker())
        with TestClient(app) as client:
            self.assertEqual(client.get("/artifacts/part.stl").status_code, 200)
            atomic_publish(self.artifacts, "other.stl", "new sibling")
            self.assertEqual(client.get("/artifacts/part.stl").status_code, 200)
            self.assertEqual(client.get("/artifacts/../root/__init__.py").status_code, 404)
