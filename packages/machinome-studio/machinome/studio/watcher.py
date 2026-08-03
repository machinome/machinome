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


LOGGER = logging.getLogger(__name__)
Publisher = Callable[..., Any]


class ArtifactWatcher(FileSystemEventHandler):
    """Forward each completed atomic publication into the build directory."""

    def __init__(self, artifact_root: Path, loop: asyncio.AbstractEventLoop, publish: Publisher) -> None:
        super().__init__()
        self.artifact_root = artifact_root.resolve()
        self.loop = loop
        self.publish = publish

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
    ) -> None:
        super().__init__()
        self.project_root = project_root.resolve()
        self.build_root = self.project_root / "_build"
        self.solid_command = tuple(solid_command)
        self.publish = publish
        self.loop = loop
        self.extra_environment = dict(extra_environment or {})
        self.settle_delay = settle_delay
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
        command = (*self.solid_command, "build", "root")
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
        except OSError as error:
            LOGGER.warning("could not run model rebuild trigger=%s error=%s", trigger, error)
            self.publish("model_build_unavailable", {"reason": str(error), "trigger": trigger})
