"""Filesystem-event model watching for the shop floor.

The floor never imports project code.  It asks ``solid build`` to publish
artifacts, then forwards the filesystem's publication events to the browser.
The framework defines publication as an atomic rename into ``_build``; that is
the only output event this module interprets.
"""

from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from watchdog.events import FileMovedEvent, FileSystemEvent, FileSystemEventHandler

from .source_files import SourceUnavailable, SourceWorkspace


LOGGER = logging.getLogger(__name__)
Publisher = Callable[..., Any]


class SourceFileWatcher(FileSystemEventHandler):
    """Publish Git-visible source invalidations without attributing an author."""

    def __init__(
        self,
        project_root: Path,
        loop: asyncio.AbstractEventLoop,
        publish: Publisher,
    ) -> None:
        super().__init__()
        self.project_root = project_root.resolve()
        self.loop = loop
        self.publish = publish
        self.workspace = SourceWorkspace(self.project_root)
        try:
            self.visible = self.workspace.visible_paths()
        except SourceUnavailable:
            self.visible = set()

    def on_created(self, event: FileSystemEvent) -> None:
        self._change("created", event)

    def on_modified(self, event: FileSystemEvent) -> None:
        self._change("modified", event)

    def on_moved(self, event: FileSystemEvent) -> None:
        self._change("moved", event)

    def on_deleted(self, event: FileSystemEvent) -> None:
        self._change("deleted", event)

    def _change(self, operation: str, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        source = self._relative(event.src_path)
        destination_value = getattr(event, "dest_path", "")
        destination = self._relative(destination_value) if destination_value else None
        if source is None and destination is None:
            return

        before = self.visible
        try:
            after = self.workspace.visible_paths()
        except SourceUnavailable:
            return
        self.visible = after

        payload: dict[str, str]
        if operation == "moved":
            if source not in before and destination not in after:
                return
            path = destination or source
            if path is None:
                return
            payload = {"operation": operation, "path": path}
            if source is not None:
                payload["previous_path"] = source
        elif operation == "deleted":
            if source is None or source not in before:
                return
            payload = {"operation": operation, "path": source}
        else:
            path = destination or source
            if path is None or path not in after:
                return
            payload = {"operation": operation, "path": path}
        self.loop.call_soon_threadsafe(self.publish, "source_file_changed", payload)

    def _relative(self, value: str) -> str | None:
        try:
            relative = Path(value).absolute().relative_to(self.project_root).as_posix()
        except (OSError, ValueError):
            return None
        if not relative or relative == ".":
            return None
        parts = Path(relative).parts
        first = parts[0]
        if (
            first == ".git"
            or first == "_build"
            or first.startswith("_build.")
            or first.startswith(".solid-node-build-")
            or any(part.startswith(".solid-node-studio-save-") for part in parts)
        ):
            return None
        return relative


class ArtifactWatcher(FileSystemEventHandler):
    """Forward each completed atomic publication into the build directory."""

    def __init__(
        self,
        artifact_root: Path,
        loop: asyncio.AbstractEventLoop,
        publish: Publisher,
        *,
        on_viewer_published: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()
        self.artifact_root = artifact_root.resolve()
        self.loop = loop
        self.publish = publish
        self.on_viewer_published = on_viewer_published

    def on_moved(self, event: FileMovedEvent) -> None:
        if event.is_directory:
            return
        destination = Path(event.dest_path)
        try:
            artifact = destination.resolve().relative_to(self.artifact_root).as_posix()
        except (OSError, ValueError):
            return
        # Watchdog invokes handlers from its observer thread.  Broker state is
        # asyncio-owned, so the handler only hands the completed publication to
        # the application's loop.
        self.loop.call_soon_threadsafe(
            self.publish,
            "model_artifact_changed",
            {"artifact": artifact},
        )
        if artifact == "viewer.json" and self.on_viewer_published is not None:
            self.loop.call_soon_threadsafe(self.on_viewer_published)


class ModelWatcher(FileSystemEventHandler):
    """Trigger one settled ``solid build`` for a burst of Python source events."""

    def __init__(
        self,
        project_root: Path,
        solid_command: Sequence[str],
        publish: Publisher,
        *,
        loop: asyncio.AbstractEventLoop,
        extra_environment: Mapping[str, str] | None = None,
        settle_delay: float = 0.5,
        on_build_success: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()
        self.project_root = project_root.resolve()
        self.build_root = self.project_root / "_build"
        self.solid_command = tuple(solid_command)
        self.publish = publish
        self.loop = loop
        self.extra_environment = dict(extra_environment or {})
        self.settle_delay = settle_delay
        self.on_build_success = on_build_success
        self._settle_handle: asyncio.TimerHandle | None = None
        self._build: asyncio.Task[None] | None = None
        self._pending_trigger: str | None = None

    # Only the four events that mean "this source is different now" may
    # trigger a build.  A real ``solid build`` opens every source it loads, so
    # dispatching on ``on_any_event`` would let inotify's ``opened`` and
    # ``closed_no_write`` events from one build trigger the next, forever.
    def on_created(self, event: FileSystemEvent) -> None:
        self._source_event(event)

    def on_modified(self, event: FileSystemEvent) -> None:
        self._source_event(event)

    def on_moved(self, event: FileSystemEvent) -> None:
        self._source_event(event)

    def on_deleted(self, event: FileSystemEvent) -> None:
        self._source_event(event)

    def _source_event(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        paths = [Path(event.src_path)]
        destination = getattr(event, "dest_path", "")
        if destination:
            paths.append(Path(destination))
        for path in paths:
            if path.suffix != ".py" or self._is_build_path(path):
                continue
            try:
                trigger = path.resolve().relative_to(self.project_root).as_posix()
            except (OSError, ValueError):
                continue
            self.loop.call_soon_threadsafe(self._source_changed, trigger)
            return

    def close(self) -> None:
        if self._settle_handle is not None:
            self._settle_handle.cancel()
            self._settle_handle = None
        if self._build is not None:
            self._build.cancel()

    def _is_build_path(self, path: Path) -> bool:
        try:
            path.resolve().relative_to(self.build_root.resolve())
            return True
        except (OSError, ValueError):
            return False

    def _source_changed(self, trigger: str) -> None:
        if self._build is not None and not self._build.done():
            self._pending_trigger = trigger
            return
        if self._settle_handle is not None:
            self._settle_handle.cancel()
        self._settle_handle = self.loop.call_later(self.settle_delay, self._start_build, trigger)

    def _start_build(self, trigger: str) -> None:
        self._settle_handle = None
        if self._build is not None and not self._build.done():
            self._pending_trigger = trigger
            return
        self._build = asyncio.create_task(self._rebuild(trigger))
        self._build.add_done_callback(self._build_finished)

    def _build_finished(self, task: asyncio.Task[None]) -> None:
        try:
            task.result()
        except asyncio.CancelledError:
            return
        except Exception:  # pragma: no cover - preserve the watcher after an unexpected subprocess failure
            LOGGER.exception("model rebuild task failed")
        finally:
            self._build = None
        if self._pending_trigger is not None:
            trigger, self._pending_trigger = self._pending_trigger, None
            self._source_changed(trigger)

    async def _rebuild(self, trigger: str) -> None:
        command = (*self.solid_command, "build")
        environment = {**os.environ, **self.extra_environment}
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=self.project_root,
                env=environment,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await process.communicate()
            if process.returncode == 0 and self.on_build_success is not None:
                self.on_build_success()
        except OSError as error:
            LOGGER.warning("could not run model rebuild trigger=%s error=%s", trigger, error)
            self.publish("model_build_unavailable", {"reason": str(error), "trigger": trigger})
