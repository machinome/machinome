# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
"""Regression coverage for S1's source-build and publication-event pipeline."""

from __future__ import annotations

import asyncio
import json
import os
import sys
import unittest
from contextlib import asynccontextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from fastapi.testclient import TestClient

from floor.app import Broker, create_app
from floor.watcher import ArtifactWatcher, ModelWatcher, SourceFileWatcher
from watchdog.observers import Observer


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
        process = await asyncio.create_subprocess_exec(*SOLID_COMMAND, "build", cwd=self.project)
        self.assertEqual(await process.wait(), 0)

    async def wait_for(self, events: list[tuple[str, dict[str, object]]], kind: str, *, timeout: float = 3) -> dict[str, object]:
        deadline = asyncio.get_running_loop().time() + timeout
        while asyncio.get_running_loop().time() < deadline:
            for actual_kind, payload in events:
                if actual_kind == kind:
                    return payload
            await asyncio.sleep(0.01)
        self.fail(f"timed out waiting for {kind}; saw {[item[0] for item in events]}")

    def app(
        self,
        *,
        solid_command: tuple[str, ...] | None = SOLID_COMMAND,
        source_events: bool = False,
    ) -> tuple[object, list[tuple[str, dict[str, object]]]]:
        broker = Broker()
        events: list[tuple[str, dict[str, object]]] = []
        original = broker.publish

        def record(kind: str, payload: object, **kwargs: object):
            if isinstance(payload, dict):
                events.append((kind, payload))
            return original(kind, payload, **kwargs)

        broker.publish = record  # type: ignore[method-assign]
        return _WatcherHarness(
            self.project,
            self.artifacts,
            broker,
            solid_command=solid_command,
            source_events=source_events,
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
    def builds(self) -> int:
        log = self.project / ".fake-solid-builds"
        return len(log.read_text().splitlines()) if log.is_file() else 0

    async def test_a_build_reading_the_sources_does_not_trigger_another_build(self) -> None:
        # The build opens every source it loads.  If those reads counted as
        # source changes, one edit would rebuild the project forever.
        sibling = self.project / "root" / "sibling.py"
        sibling.write_text("# untouched\n")
        build_state(self.project, viewer={"version": 1, "root": {"name": "part", "model": "part.stl"}, "revision": 4})
        app, events = self.app()
        async with app.router.lifespan_context(app):  # type: ignore[attr-defined]
            before = self.builds()
            self.model.write_text("# edited\n")
            await self.wait_for(events, "model_artifact_changed")
            await asyncio.sleep(SETTLE * 20)
            self.assertEqual(self.builds() - before, 1)

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


class SourceInvalidationWatcherTest(WatcherTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        (self.project / ".gitignore").write_text("_build/\nignored/\n")
        subprocess = await asyncio.create_subprocess_exec("git", "init", "-q", "-b", "main", str(self.project))
        self.assertEqual(await subprocess.wait(), 0)
        subprocess = await asyncio.create_subprocess_exec("git", "-C", str(self.project), "add", "root/__init__.py", ".gitignore")
        self.assertEqual(await subprocess.wait(), 0)

    async def test_create_modify_move_and_delete_publish_project_relative_invalidations(self) -> None:
        app, events = self.app(solid_command=None, source_events=True)
        async with app.router.lifespan_context(app):  # type: ignore[attr-defined]
            created = self.project / "agent.py"
            created.write_text("one = 1\n")
            await self._wait_source(events, "created", "agent.py")
            events.clear()

            created.write_text("two = 2\n")
            await self._wait_source(events, "modified", "agent.py")
            events.clear()

            moved = self.project / "renamed.py"
            os.replace(created, moved)
            payload = await self._wait_source(events, "moved", "renamed.py")
            self.assertEqual(payload["previous_path"], "agent.py")
            events.clear()

            moved.unlink()
            await self._wait_source(events, "deleted", "renamed.py")

    async def test_ignored_and_build_paths_never_publish_source_invalidations(self) -> None:
        app, events = self.app(solid_command=None, source_events=True)
        async with app.router.lifespan_context(app):  # type: ignore[attr-defined]
            ignored = self.project / "ignored"
            ignored.mkdir()
            (ignored / "hidden.py").write_text("hidden = True\n")
            atomic_publish(self.artifacts, "generated.py", "generated = True\n")
            await asyncio.sleep(SETTLE * 5)
        self.assertFalse(any(kind == "source_file_changed" for kind, _ in events), events)

    async def _wait_source(
        self,
        events: list[tuple[str, dict[str, object]]],
        operation: str,
        path: str,
    ) -> dict[str, object]:
        deadline = asyncio.get_running_loop().time() + 3
        while asyncio.get_running_loop().time() < deadline:
            for kind, payload in events:
                if kind == "source_file_changed" and payload.get("operation") == operation and payload.get("path") == path:
                    return payload
            await asyncio.sleep(0.01)
        self.fail(f"timed out waiting for source {operation} {path}; saw {events}")


class ArtifactRouteTest(WatcherTestCase):
    async def test_republished_artifacts_must_revalidate(self) -> None:
        app = _artifact_app(self.project, self.artifacts)
        with TestClient(app) as client:
            response = client.get("/projects/project/artifacts/part.stl")
        self.assertEqual(response.headers["cache-control"], "no-cache")

    async def test_route_serves_a_stable_artifact_during_another_republication(self) -> None:
        app = _artifact_app(self.project, self.artifacts)
        with TestClient(app) as client:
            self.assertEqual(client.get("/projects/project/artifacts/part.stl").status_code, 200)
            atomic_publish(self.artifacts, "other.stl", "new sibling")
            self.assertEqual(client.get("/projects/project/artifacts/part.stl").status_code, 200)
            self.assertEqual(client.get("/projects/project/artifacts/%2e%2e/root/__init__.py").status_code, 404)


class _WatcherHarness:
    def __init__(
        self,
        project: Path,
        artifacts: Path,
        broker: Broker,
        *,
        solid_command: tuple[str, ...] | None,
        source_events: bool,
    ) -> None:
        self.project = project
        self.artifacts = artifacts
        self.broker = broker
        self.solid_command = solid_command
        self.source_events = source_events
        self.state = SimpleNamespace(model_watcher=None, artifact_watcher=None, source_file_watcher=None, observer=None)
        self.router = SimpleNamespace(lifespan_context=self.lifespan_context)

    @asynccontextmanager
    async def lifespan_context(self, _app):
        loop = asyncio.get_running_loop()
        observer = Observer()
        artifact = ArtifactWatcher(self.artifacts, loop, self.broker.publish)
        observer.schedule(artifact, str(self.artifacts), recursive=True)
        source_file = None
        if self.source_events:
            source_file = SourceFileWatcher(self.project, loop, self.broker.publish)
            observer.schedule(source_file, str(self.project), recursive=True)
        source = None
        if self.solid_command is not None:
            source = ModelWatcher(
                self.project,
                self.solid_command,
                self.broker.publish,
                loop=loop,
                settle_delay=SETTLE,
            )
            observer.schedule(source, str(self.project), recursive=True)
        self.state.model_watcher = source
        self.state.artifact_watcher = artifact
        self.state.source_file_watcher = source_file
        self.state.observer = observer
        observer.start()
        try:
            yield
        finally:
            if source is not None:
                source.close()
            observer.stop()
            await asyncio.to_thread(observer.join)


def _artifact_app(project: Path, artifacts: Path):
    session = SimpleNamespace(
        id="session",
        name="project",
        artifact_root=artifacts,
        prepared=SimpleNamespace(viewer_bundle=None),
        broker=Broker(),
    )

    class Registry:
        shop_root = ROOT

        def by_project(self, name: str):
            return session if name == "project" else None

        def require_id(self, session_id: str):
            if session_id != "session":
                raise KeyError(session_id)
            return session

        async def close_all(self) -> None:
            return None

        async def projects(self):
            return []

    return create_app(project.parent, registry=Registry())
