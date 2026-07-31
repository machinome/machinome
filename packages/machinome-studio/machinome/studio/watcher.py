"""Deterministic project-source watcher for functional-model rebuilds.

The floor used to learn that a model had changed from a POST sent by a
`solid develop --callback` process the machinist was told to start and
keep alive. A guarantee the maker depends on rested on agent behaviour:
a designer's edit, or the pilot's own, refreshed nothing at all. This
watcher is shop machinery that runs for the whole life of the floor,
whoever made the change.

It never imports, executes, or serves project Python (ADR 0004). It runs
the same `solid build root` the shop already runs before the floor opens,
and reads only the published snapshot to decide what to say.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any


LOGGER = logging.getLogger(__name__)

# A build writes into the build tree. If the watcher saw those writes it
# would trigger itself forever, so the exclusion is a correctness
# requirement rather than an optimisation. `_build` is a symlink to a
# versioned sibling with transient staging directories beside it, so it
# has to cover the whole family and not the literal name.
EXCLUDED_DIRECTORIES = {".git", "__pycache__", ".venv", "_build"}
EXCLUDED_PREFIXES = ("_build.", ".solid-node-build-")

MAX_DIAGNOSTIC_CHARS = 4096

Fingerprint = dict[str, tuple[int, int]]
Publisher = Callable[..., Any]


class ModelWatcher:
    """Poll the project's Python sources and serialise solid-node rebuilds."""

    def __init__(
        self,
        project_root: Path,
        artifact_root: Path,
        solid_command: Sequence[str],
        publish: Publisher,
        *,
        extra_environment: Mapping[str, str] | None = None,
        poll_interval: float = 0.5,
    ) -> None:
        self.project_root = project_root.resolve()
        self.artifact_root = artifact_root
        self.solid_command = tuple(solid_command)
        self.publish = publish
        self.extra_environment = dict(extra_environment or {})
        self.poll_interval = poll_interval
        # Seeded from the snapshot preparation already validated, so the
        # first rebuild is compared against what the browser is showing.
        self._snapshot_hash = _content_hash(artifact_root / "viewer.json")

    async def run(self) -> None:
        baseline = _source_fingerprint(self.project_root)
        candidate: Fingerprint | None = None
        build: asyncio.Task[None] | None = None
        pending: tuple[Fingerprint, str] | None = None
        try:
            while True:
                await asyncio.sleep(self.poll_interval)
                current = _source_fingerprint(self.project_root)

                if current == baseline:
                    candidate = None
                elif candidate == current:
                    # Stable across two consecutive polls: an editor
                    # writing in place can be observed mid-write, and
                    # building that produces a failure banner that a
                    # rebuild moments later silently fixes. One quiet
                    # poll also coalesces a multi-file save into one
                    # build.
                    trigger = _changed_source(baseline, current)
                    baseline = current
                    if build is None:
                        build = asyncio.create_task(self._rebuild(trigger))
                    else:
                        # One build at a time. A change arriving during a
                        # build is remembered, not queued or raced.
                        pending = (current, trigger)
                    candidate = None
                else:
                    candidate = current

                if build is not None and build.done():
                    await build
                    build = None
                    if pending is not None:
                        _, trigger = pending
                        pending = None
                        build = asyncio.create_task(self._rebuild(trigger))
        finally:
            if build is not None:
                build.cancel()
                await asyncio.gather(build, return_exceptions=True)

    async def _rebuild(self, trigger: str) -> None:
        started = time.monotonic()
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
            stdout, stderr = await process.communicate()
        except OSError as error:
            # A missing or unusable solid command is a reportable
            # failure, not a reason for the watcher to die silently.
            self._publish_failure(str(error), trigger, started)
            return

        if process.returncode != 0:
            diagnostic = (stderr or stdout).decode(errors="replace").strip()
            if not diagnostic:
                diagnostic = f"solid build exited {process.returncode}"
            self._publish_failure(diagnostic, trigger, started)
            return

        duration = time.monotonic() - started
        LOGGER.info("model rebuild succeeded trigger=%s duration=%.3fs", trigger, duration)
        # Success clears a reported failure. It says nothing about whether
        # the artifacts changed -- that is model_changed's job alone.
        self.publish(
            "model_build_succeeded",
            {"trigger": trigger, "duration_seconds": round(duration, 3)},
        )

        snapshot_hash = _content_hash(self.artifact_root / "viewer.json")
        if snapshot_hash != self._snapshot_hash:
            self._snapshot_hash = snapshot_hash
            self.publish("model_changed", {"trigger": trigger})

    def _publish_failure(self, diagnostic: str, trigger: str, started: float) -> None:
        diagnostic = diagnostic[-MAX_DIAGNOSTIC_CHARS:]
        duration = time.monotonic() - started
        LOGGER.warning(
            "model rebuild failed trigger=%s duration=%.3fs error=%s",
            trigger,
            duration,
            diagnostic,
        )
        self.publish(
            "model_build_failed",
            {"error": diagnostic, "trigger": trigger, "duration_seconds": round(duration, 3)},
        )


def _source_fingerprint(project_root: Path) -> Fingerprint:
    fingerprint: Fingerprint = {}
    for directory, names, files in os.walk(project_root, followlinks=False):
        names[:] = [name for name in names if not _excluded_directory(name)]
        base = Path(directory)
        for name in files:
            if not name.endswith(".py"):
                continue
            path = base / name
            try:
                stat = path.stat()
            except OSError:
                # Vanished between listing and stat: the next poll sees
                # the settled state.
                continue
            fingerprint[str(path.relative_to(project_root))] = (stat.st_mtime_ns, stat.st_size)
    return fingerprint


def _excluded_directory(name: str) -> bool:
    return name in EXCLUDED_DIRECTORIES or name.startswith(EXCLUDED_PREFIXES)


def _changed_source(previous: Fingerprint, current: Fingerprint) -> str:
    """One named file for the log and the event, so a wasted rebuild can
    be attributed rather than guessed at."""
    changed = sorted(
        path for path in previous.keys() | current.keys()
        if previous.get(path) != current.get(path)
    )
    return changed[0] if changed else "unknown"


def _content_hash(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None
