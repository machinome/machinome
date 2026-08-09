"""Per-project runtime sessions owned by one long-lived shop service."""

from __future__ import annotations

import asyncio
import secrets
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from watchdog.observers import Observer

from .app import Broker
from .backends import create_backend
from .backends.base import AgentBackend
from .orchestrator import LocalBrokerControl, ShopOrchestrator, _route_backend_events
from .preparation import (
    PreparedProject,
    PreparationError,
    ProjectRuntimeError,
    default_solid_command,
    list_projects,
    prepare_project,
    read_project_runtime,
    resolve_project,
    validate_new_project,
)
from .profiles import ProfileError, RuntimeProfile, load_profile, resolve_profile_runtime
from .watcher import ArtifactWatcher, ModelWatcher


BackendFactory = Callable[..., AgentBackend]


@dataclass
class Session:
    """All state and resources that belong to one opened project."""

    id: str
    name: str
    prepared: PreparedProject
    profile: RuntimeProfile
    broker: Broker
    orchestrator: ShopOrchestrator | None = None
    delivery_task: asyncio.Task[None] | None = None
    event_tasks: list[asyncio.Task[None]] = field(default_factory=list)
    observer: Observer | None = None
    source_watcher: ModelWatcher | None = None
    artifact_watcher: ArtifactWatcher | None = None

    @property
    def project_root(self) -> Path:
        return self.prepared.project_root

    @property
    def artifact_root(self) -> Path:
        return self.prepared.artifact_root

    @property
    def build_environment(self) -> Mapping[str, str] | None:
        return self.prepared.build_environment

    async def start_watchers(self, *, settle_delay: float = 0.5) -> None:
        loop = asyncio.get_running_loop()
        observer = Observer()
        self.source_watcher = ModelWatcher(
            self.project_root,
            self.prepared.solid_command,
            self.broker.publish,
            loop=loop,
            extra_environment=self.prepared.build_environment,
            settle_delay=settle_delay,
        )
        observer.schedule(self.source_watcher, str(self.project_root), recursive=True)
        if self.artifact_root.is_dir():
            self.artifact_watcher = ArtifactWatcher(self.artifact_root, loop, self.broker.publish)
            observer.schedule(self.artifact_watcher, str(self.artifact_root), recursive=True)
        observer.start()
        self.observer = observer
        if self.prepared.build_error:
            self.broker.publish("model_build_unavailable", {"reason": self.prepared.build_error, "trigger": "open"})

    async def close(self) -> None:
        """Boundedly release every process, routing task and filesystem watch."""
        self.broker.shutdown()
        tasks = tuple(task for task in (self.delivery_task, *self.event_tasks) if task is not None)
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        if self.orchestrator is not None:
            try:
                await asyncio.wait_for(self.orchestrator.close(), timeout=35)
            except Exception:
                # The orchestrator bounds every role operation and asks every
                # process owner to escalate shutdown. One failure must not
                # prevent watcher cleanup or registry removal.
                pass
        if self.source_watcher is not None:
            self.source_watcher.close()
        if self.observer is not None:
            self.observer.stop()
            await asyncio.to_thread(self.observer.join, 5)


class SessionRegistry:
    """Open, find and close at most one ephemeral session per project."""

    def __init__(
        self,
        working_folder: Path,
        *,
        shop_root: Path,
        solid_command: str | Sequence[str] | None = None,
        broker_url: str = "http://127.0.0.1:9000",
        backend_commands: Mapping[str, str] | None = None,
        backend_factory: BackendFactory = create_backend,
        start_agents: bool = True,
        settle_delay: float = 0.5,
    ) -> None:
        self.working_folder = working_folder.resolve()
        self.shop_root = shop_root.resolve()
        self.solid_command = solid_command or default_solid_command(shop_root)
        self.broker_url = broker_url
        self.backend_commands = dict(backend_commands or {})
        self.backend_factory = backend_factory
        self.start_agents = start_agents
        self.settle_delay = settle_delay
        self._by_project: dict[str, Session] = {}
        self._by_id: dict[str, Session] = {}
        self._opening: dict[str, asyncio.Task[Session | None]] = {}
        self._provisional_profiles: dict[str, str] = {}
        self._failures: dict[str, str] = {}
        self._hub_subscribers: set[asyncio.Queue[dict[str, object]]] = set()
        self._lock = asyncio.Lock()

    def by_project(self, name: str) -> Session | None:
        return self._by_project.get(name)

    def by_id(self, session_id: str) -> Session | None:
        return self._by_id.get(session_id)

    def require_id(self, session_id: str) -> Session:
        session = self.by_id(session_id)
        if session is None:
            raise KeyError(session_id)
        return session

    async def projects(self) -> list[dict[str, object]]:
        listings = await asyncio.to_thread(list_projects, self.working_folder)
        values: list[dict[str, object]] = []
        listed_names: set[str] = set()
        for listing in listings:
            listed_names.add(listing.name)
            session = self._by_project.get(listing.name)
            provisional_profile = self._provisional_profiles.get(listing.name)
            state = "open" if session is not None else "creating" if provisional_profile is not None else "opening" if listing.name in self._opening else "failed" if listing.name in self._failures else "closed"
            value = listing.browser_value(state=state, session_id=session.id if session else None)
            if provisional_profile is not None:
                value.update({"openable": True, "reason": None, "profile": provisional_profile})
            value["failure"] = self._failures.get(listing.name)
            values.append(value)
        for name, profile in self._provisional_profiles.items():
            if name in listed_names:
                continue
            values.append({
                "name": name,
                "openable": True,
                "reason": None,
                "profile": profile,
                "branch": None,
                "last_commit": None,
                "state": "creating",
                "session_id": None,
                "failure": None,
            })
        values.sort(key=lambda value: str(value["name"]))
        return values

    async def hub_snapshot(self) -> dict[str, object]:
        return {"working_folder": str(self.working_folder), "projects": await self.projects()}

    async def subscribe_hub(self) -> tuple[asyncio.Queue[dict[str, object]], dict[str, object]]:
        subscriber: asyncio.Queue[dict[str, object]] = asyncio.Queue()
        self._hub_subscribers.add(subscriber)
        return subscriber, await self.hub_snapshot()

    def unsubscribe_hub(self, subscriber: asyncio.Queue[dict[str, object]]) -> None:
        self._hub_subscribers.discard(subscriber)

    def publish_hub(self, kind: str, name: str, **details: object) -> None:
        event = {"kind": kind, "project": name, **details}
        for subscriber in tuple(self._hub_subscribers):
            subscriber.put_nowait(event)

    async def request_open(self, name: str, *, create_profile: str | None = None) -> dict[str, object]:
        resolve_project(name, self.working_folder)
        async with self._lock:
            session = self._by_project.get(name)
            if session is not None:
                return {"state": "open", "session_id": session.id}
            if name in self._opening:
                return {"state": "opening"}
            self._failures.pop(name, None)
            task = asyncio.create_task(self._open(name, create_profile=create_profile))
            self._opening[name] = task
            if create_profile is not None:
                self._provisional_profiles[name] = create_profile
                self.publish_hub("creating", name, profile=create_profile)
            else:
                self.publish_hub("opening", name)
            return {"state": "opening"}

    async def create(self, name: str, profile: str | None) -> dict[str, object]:
        if profile is None:
            raise ProfileError("profile is required")
        load_profile(profile, shop_root=self.shop_root)
        validate_new_project(name, self.working_folder)
        return await self.request_open(name, create_profile=profile)

    async def wait_until_settled(self, name: str) -> Session | None:
        task = self._opening.get(name)
        if task is not None:
            return await task
        return self._by_project.get(name)

    async def _open(self, name: str, *, create_profile: str | None) -> Session | None:
        session: Session | None = None
        try:
            selection = await asyncio.to_thread(read_project_runtime, name, project_home=self.working_folder)
            profile = await asyncio.to_thread(
                lambda: resolve_profile_runtime(
                    load_profile(create_profile, shop_root=self.shop_root, selection=selection), selection
                )
            )
            prepared = await asyncio.to_thread(
                prepare_project,
                name,
                project_home=self.working_folder,
                solid_command=self.solid_command,
                shop_root=self.shop_root,
                profile=create_profile,
                allow_build_failure=True,
            )
            session_id = secrets.token_urlsafe(24)
            session = Session(session_id, name, prepared, profile, Broker(profile=profile, session_id=session_id))
            if self.start_agents:
                await self._start_orchestrator(session)
            await session.start_watchers(settle_delay=self.settle_delay)
            async with self._lock:
                self._by_project[name] = session
                self._by_id[session.id] = session
            self.publish_hub("open", name, session_id=session.id)
            return session
        except asyncio.CancelledError:
            if session is not None:
                await asyncio.shield(session.close())
            raise
        except Exception as error:
            if session is not None:
                await session.close()
            self._failures[name] = str(error)
            self.publish_hub("failed", name, reason=str(error))
            return None
        finally:
            async with self._lock:
                self._opening.pop(name, None)
                self._provisional_profiles.pop(name, None)

    async def _start_orchestrator(self, session: Session) -> None:
        backend_instances: dict[str, AgentBackend] = {}
        for agent in session.profile.agents:
            if agent.runtime is None:
                raise RuntimeError(f"agent {agent.id!r} has no resolved runtime")
            backend_name = agent.runtime.backend
            if backend_name not in backend_instances:
                backend_instances[backend_name] = self.backend_factory(
                    backend_name,
                    cwd=self.shop_root,
                    project=session.project_root,
                    broker_url=self.broker_url,
                    command_overrides=self.backend_commands,
                    solid_command=self.solid_command,
                    session_id=session.id,
                )
        by_agent = {
            agent.id: backend_instances[agent.runtime.backend]
            for agent in session.profile.agents
            if agent.runtime is not None
        }
        orchestrator = ShopOrchestrator(
            by_agent,
            LocalBrokerControl(session.broker),
            profile=session.profile,
            shop_checkout=self.shop_root,
            active_project=session.project_root,
        )
        session.orchestrator = orchestrator
        await orchestrator.open()

        async def route_deliveries() -> None:
            async for envelope in session.broker.deliveries():
                await orchestrator.deliver(envelope)

        session.delivery_task = asyncio.create_task(route_deliveries())
        session.event_tasks = [
            asyncio.create_task(_route_backend_events(orchestrator, backend))
            for backend in backend_instances.values()
        ]

    async def request_close(self, session_id: str) -> None:
        async with self._lock:
            session = self._by_id.get(session_id)
            if session is None:
                return
            self._by_id.pop(session.id, None)
            self._by_project.pop(session.name, None)
        await session.close()
        self.publish_hub("closed", session.name)

    async def close_all(self) -> None:
        opening = tuple(self._opening.values())
        for task in opening:
            task.cancel()
        if opening:
            await asyncio.gather(*opening, return_exceptions=True)
        sessions = tuple(self._by_project.values())
        self._by_project.clear()
        self._by_id.clear()
        self._provisional_profiles.clear()
        for session in sessions:
            await session.close()
            self.publish_hub("closed", session.name)
