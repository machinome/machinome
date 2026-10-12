# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Per-project runtime sessions owned by one long-lived shop service."""

from __future__ import annotations

import asyncio
import logging
import secrets
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any

from watchdog.observers import Observer

from .app import Broker
from .backends import create_backend
from .backends.base import AgentBackend
from .backends.codex_service import CodexService, ServiceReference, role_registry
from .orchestrator import LocalBrokerControl, ShopOrchestrator, _route_backend_events
from .preparation import (
    FolderListing,
    HubEntry,
    PreparedProject,
    PreparationError,
    ProjectRuntimeError,
    ViewerBundle,
    build_project,
    commit_new_project,
    default_machinome_command,
    has_complete_publication,
    list_folder,
    prepare_project,
    is_repository_root,
    read_project_runtime,
    resolve_entry,
    resolve_folder,
    resolve_viewer_bundle,
    validate_new_project,
)
from .profiles import (
    BackendRuntime,
    ProfileError,
    ProfileSkill,
    RuntimeProfile,
    load_profile,
    resolve_profile_runtime,
)
from .runtime_config import (
    RuntimeConfigConflict,
    config_revision,
    prepare_runtime_edit,
    publish_runtime_edit,
)
from .backends.base import AgentActivity
from .screenshots import refresh_project_screenshot
from .source_files import SourceDocument, SourceWorkspace
from .watcher import ArtifactWatcher, ModelWatcher, SourceFileWatcher

LOGGER = logging.getLogger(__name__)


BackendFactory = Callable[..., AgentBackend]


def _profile_skills(profile: RuntimeProfile) -> tuple[ProfileSkill, ...]:
    """Every skill the profile allowlists, in a stable order, without repeats.

    A backend whose tool server is shared by all its roles registers these
    before any role opens; each role is still announced only its own.
    """
    resolved: dict[str, ProfileSkill] = {}
    for agent in profile.agents:
        for skill in agent.skills:
            resolved.setdefault(skill.name, skill)
    return tuple(resolved[name] for name in sorted(resolved))


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
    build_task: asyncio.Task[None] | None = None
    observer: Observer | None = None
    source_watcher: ModelWatcher | None = None
    source_file_watcher: SourceFileWatcher | None = None
    artifact_watcher: ArtifactWatcher | None = None
    on_screenshot_changed: Callable[[str], None] | None = None
    source_workspace: SourceWorkspace = field(init=False)
    source_save_lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    runtime_lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    codex_reference: ServiceReference | None = None

    def __post_init__(self) -> None:
        self.source_workspace = SourceWorkspace(self.project_root)

    @property
    def project_root(self) -> Path:
        return self.prepared.project_root

    @property
    def artifact_root(self) -> Path:
        return self.prepared.artifact_root

    @property
    def model_building(self) -> bool:
        """Whether a build is still running behind the presented publication.

        The broker holds it so that the one place a browser learns the session's
        live state also answers whether its model has settled.
        """
        return self.broker.model_building

    @property
    def build_environment(self) -> Mapping[str, str] | None:
        return self.prepared.build_environment

    async def save_source(self, path: str, content: str, expected_revision: str) -> SourceDocument:
        async with self.source_save_lock:
            document = await asyncio.to_thread(
                self.source_workspace.save,
                path,
                content,
                expected_revision,
            )
            notices = self.broker.queue_user_file_changed(document.path, document.revision)
        if self.orchestrator is not None and notices:
            await asyncio.gather(
                *(
                    self.orchestrator.deliver_pending_notices(role)
                    for role in dict.fromkeys(notice.recipient for notice in notices)
                )
            )
        return document

    async def runtime_catalog(self, role: str) -> dict[str, object]:
        if self.orchestrator is None:
            raise RuntimeError("agent runtime is unavailable for this session")
        catalogue = await self.orchestrator.runtime_catalog(role)
        return {
            "role": role,
            "runtime": _runtime_value(self.orchestrator.current_runtime(role)),
            "supported": catalogue.supported,
            "reason": catalogue.reason or None,
            "unavailable": catalogue.unavailable,
            "choices": [asdict(choice) for choice in catalogue.choices],
            "config_revision": await asyncio.to_thread(config_revision, self.project_root / "pyproject.toml"),
            "runtime_idle": self.broker.runtime_idle(role),
            "runtime_pristine": self.broker.runtime_pristine(role),
        }

    async def update_runtime(
        self,
        role: str,
        backend: str,
        provider: str | None,
        model: str,
        effort: str,
        *,
        persist: bool,
        expected_revision: str | None,
    ) -> dict[str, object]:
        if self.orchestrator is None:
            raise RuntimeError("agent runtime is unavailable for this session")
        async with self.runtime_lock:
            requested = _selected_runtime(self.profile, role, backend, provider, model, effort)
            edit = None
            if persist:
                if expected_revision is None:
                    raise RuntimeConfigConflict("pyproject.toml revision is required for a persisted runtime update")
                edit = await asyncio.to_thread(
                    prepare_runtime_edit,
                    self.project_root / "pyproject.toml",
                    role,
                    requested,
                    expected_revision,
                )
            revision = (
                edit.revision
                if edit is not None
                else await asyncio.to_thread(config_revision, self.project_root / "pyproject.toml")
            )
            applied = await self.orchestrator.update_runtime(
                role,
                requested,
                commit=(lambda: publish_runtime_edit(edit)) if edit is not None else None,
            )
            self.broker.record_activity(AgentActivity(
                id=f"runtime-{self.broker.latest_event_sequence + 1}",
                role=role,
                category="message",
                state="completed",
                name="runtime changed",
                summary=f"{applied.backend} · {applied.model} · {applied.effort}",
                detail="written to pyproject.toml" if persist else "temporary session override",
            ), marks_runtime_used=False)
            return {
                "agent": self.broker.agents[role].browser_value(),
                "runtime": _runtime_value(applied),
                "config_revision": revision,
                "persisted": persist,
            }

    async def start_watchers(self, *, settle_delay: float = 0.5) -> None:
        loop = asyncio.get_running_loop()
        observer = Observer()
        self.source_file_watcher = SourceFileWatcher(
            self.project_root,
            loop,
            self.broker.publish,
        )
        observer.schedule(self.source_file_watcher, str(self.project_root), recursive=True)
        self.source_watcher = ModelWatcher(
            self.project_root,
            self.prepared.machinome_command,
            self.broker.publish,
            loop=loop,
            extra_environment=self.prepared.build_environment,
            settle_delay=settle_delay,
            on_build_success=self._request_screenshot_refresh,
        )
        observer.schedule(self.source_watcher, str(self.project_root), recursive=True)
        if self.artifact_root.is_dir():
            self.artifact_watcher = ArtifactWatcher(
                self.artifact_root,
                loop,
                self.broker.publish,
                on_viewer_published=self._request_screenshot_refresh,
            )
            observer.schedule(self.artifact_watcher, str(self.artifact_root), recursive=True)
        observer.start()
        self.observer = observer
        if self.prepared.build_error:
            self.broker.publish("model_build_unavailable", {"reason": self.prepared.build_error, "trigger": "open"})

    def _request_screenshot_refresh(self) -> None:
        task = asyncio.create_task(self._refresh_screenshot())
        self.event_tasks.append(task)

    async def _refresh_screenshot(self) -> None:
        result = await asyncio.to_thread(
            refresh_project_screenshot,
            self.project_root,
            self.prepared.machinome_command,
            model=self.prepared.project_model,
            extra_environment=self.prepared.build_environment,
        )
        if result.warning:
            LOGGER.warning(
                "no model preview for %s: %s", self.prepared.name, result.warning,
            )
        if result.updated and result.revision is not None and self.on_screenshot_changed is not None:
            self.on_screenshot_changed(result.revision)

    async def close(self) -> None:
        """Boundedly release every process, routing task and filesystem watch."""
        self.broker.shutdown()
        tasks = tuple(
            task
            for task in (self.delivery_task, self.build_task, *self.event_tasks)
            if task is not None
        )
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
        if self.codex_reference is not None:
            try:
                await self.codex_reference.close()
            except Exception:
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
        machinome_command: str | Sequence[str] | None = None,
        broker_url: str = "http://127.0.0.1:9000",
        backend_commands: Mapping[str, str] | None = None,
        backend_factory: BackendFactory = create_backend,
        start_agents: bool = True,
        settle_delay: float = 0.5,
        codex_service: CodexService | None = None,
    ) -> None:
        self.working_folder = working_folder.resolve()
        self.shop_root = shop_root.resolve()
        self.machinome_command = machinome_command or default_machinome_command()
        self.broker_url = broker_url
        self.backend_commands = dict(backend_commands or {})
        self.backend_factory = backend_factory
        self.start_agents = start_agents
        self.settle_delay = settle_delay
        self._by_entry: dict[str, Session] = {}
        self._by_id: dict[str, Session] = {}
        self._opening: dict[str, asyncio.Task[Session | None]] = {}
        self._provisional_profiles: dict[str, str] = {}
        self._failures: dict[str, str] = {}
        self._hub_subscribers: set[asyncio.Queue[dict[str, object]]] = set()
        self._lock = asyncio.Lock()
        self._viewer: ViewerBundle | None = None
        self._viewer_lock = asyncio.Lock()
        self.codex_service = codex_service or CodexService()

    def by_entry(self, path: str) -> Session | None:
        return self._by_entry.get(path)

    def by_id(self, session_id: str) -> Session | None:
        return self._by_id.get(session_id)

    def require_id(self, session_id: str) -> Session:
        session = self.by_id(session_id)
        if session is None:
            raise KeyError(session_id)
        return session

    async def entries(self, folder: str = "") -> list[dict[str, object]]:
        """Everything the hub shows for one folder, with live state folded in."""
        listings = await asyncio.to_thread(list_folder, self.working_folder, folder)
        values: list[dict[str, object]] = []
        listed_paths: set[str] = set()
        for listing in listings:
            if isinstance(listing, FolderListing):
                values.append(listing.browser_value())
                continue
            path = listing.path
            listed_paths.add(path)
            session = self._by_entry.get(path)
            provisional_profile = self._provisional_profiles.get(path)
            state = "open" if session is not None else "creating" if provisional_profile is not None else "opening" if path in self._opening else "failed" if path in self._failures else "closed"
            value = listing.browser_value(state=state, session_id=session.id if session else None)
            if provisional_profile is not None:
                value.update({"openable": True, "reason": None, "profile": provisional_profile})
            value["failure"] = self._failures.get(path)
            value["model_building"] = session is not None and session.model_building
            values.append(value)
        for path, profile in self._provisional_profiles.items():
            if path in listed_paths or _folder_of(path) != folder:
                continue
            values.append({
                "kind": "project",
                "path": path,
                "name": path.rsplit("/", 1)[-1],
                "openable": True,
                "reason": None,
                "profile": profile,
                "branch": None,
                "last_commit": None,
                "state": "creating",
                "session_id": None,
                "failure": None,
                "screenshot_revision": None,
                "model_building": False,
            })
        values.sort(key=lambda value: (value["kind"] != "folder", str(value["path"])))
        return values

    async def hub_snapshot(self, folder: str = "") -> dict[str, object]:
        return {
            "working_folder": str(self.working_folder),
            "folder": folder,
            "models": await asyncio.to_thread(self.lists_models, folder),
            "entries": await self.entries(folder),
        }

    def lists_models(self, folder: str) -> bool:
        """Whether this folder is a project, so its entries are its models.

        A project holds no directory the maker may create a project in, so the
        hub needs to know which kind of folder it is showing rather than
        guessing from the cards.
        """
        if not folder:
            return False
        try:
            return is_repository_root(resolve_folder(folder, self.working_folder))
        except PreparationError:
            return False

    async def subscribe_hub(self, folder: str = "") -> tuple[asyncio.Queue[dict[str, object]], dict[str, object]]:
        subscriber: asyncio.Queue[dict[str, object]] = asyncio.Queue()
        self._hub_subscribers.add(subscriber)
        return subscriber, await self.hub_snapshot(folder)

    def unsubscribe_hub(self, subscriber: asyncio.Queue[dict[str, object]]) -> None:
        self._hub_subscribers.discard(subscriber)

    def publish_hub(self, kind: str, path: str, **details: object) -> None:
        """Tell every hub browser about one entry, naming the folder it is in.

        A browser is listing one folder, so it needs the folder to decide
        whether the change is its business at all.
        """
        event = {"kind": kind, "project": path, "folder": _folder_of(path), **details}
        for subscriber in tuple(self._hub_subscribers):
            subscriber.put_nowait(event)

    async def request_open(
        self,
        path: str,
        *,
        entry: HubEntry | None = None,
        create_profile: str | None = None,
    ) -> dict[str, object]:
        if entry is None:
            entry = await asyncio.to_thread(resolve_entry, path, self.working_folder)
        path = entry.path
        async with self._lock:
            session = self._by_entry.get(path)
            if session is not None:
                return {"state": "open", "session_id": session.id}
            if path in self._opening:
                return {"state": "opening"}
            self._failures.pop(path, None)
            task = asyncio.create_task(self._open(entry, create_profile=create_profile))
            self._opening[path] = task
            if create_profile is not None:
                self._provisional_profiles[path] = create_profile
                self.publish_hub("creating", path, profile=create_profile)
            else:
                self.publish_hub("opening", path)
            return {"state": "opening"}

    async def create(self, folder: str, name: str, profile: str | None) -> dict[str, object]:
        if profile is None:
            raise ProfileError("profile is required")
        load_profile(profile, shop_root=self.shop_root)
        entry = validate_new_project(folder, name, self.working_folder)
        return await self.request_open(entry.path, entry=entry, create_profile=profile)

    async def wait_until_settled(self, path: str) -> Session | None:
        task = self._opening.get(path)
        if task is not None:
            return await task
        return self._by_entry.get(path)

    async def _open(self, entry: HubEntry, *, create_profile: str | None) -> Session | None:
        session: Session | None = None
        codex_reference: ServiceReference | None = None
        name = entry.path
        try:
            selection = await asyncio.to_thread(read_project_runtime, entry.project_root)
            profile = await asyncio.to_thread(
                lambda: resolve_profile_runtime(
                    load_profile(create_profile, shop_root=self.shop_root, selection=selection), selection
                )
            )
            session_id = secrets.token_urlsafe(24)
            codex_agents = [agent for agent in profile.agents if agent.runtime is not None and agent.runtime.backend == "codex"]
            if self.start_agents and codex_agents:
                codex_reference = await self.codex_service.acquire(session_id, [role_registry(agent) for agent in codex_agents])
            prepared = await asyncio.to_thread(
                prepare_project,
                entry,
                machinome_command=self.machinome_command,
                profile=create_profile,
                viewer=await self._viewer_bundle(),
            )
            # A project that already holds a complete, valid publication has
            # something to show now; one being created or never built has not,
            # so there is nothing to gain by opening ahead of its build.
            present_early = not prepared.created and await asyncio.to_thread(
                has_complete_publication, prepared
            )
            if not present_early:
                outcome = await asyncio.to_thread(build_project, prepared, allow_failure=True)
                prepared = replace(prepared, build_error=outcome.error)
                await asyncio.to_thread(commit_new_project, prepared)
            broker = Broker(profile=profile, session_id=session_id)
            broker.model_building = present_early
            session = Session(
                session_id,
                name,
                prepared,
                profile,
                broker,
                on_screenshot_changed=lambda revision: self.publish_hub(
                    "screenshot", name, screenshot_revision=revision
                ),
                codex_reference=codex_reference,
            )
            if self.start_agents:
                await self._start_orchestrator(session)
            await session.start_watchers(settle_delay=self.settle_delay)
            async with self._lock:
                self._by_entry[name] = session
                self._by_id[session.id] = session
            self.publish_hub("open", name, session_id=session.id, model_building=session.model_building)
            if present_early:
                # The watchers are already running, so the publication this
                # build produces cannot be missed, and the session owns the
                # task so the build cannot outlive it.
                session.build_task = asyncio.create_task(self._build_behind(session))
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
            if session is None and codex_reference is not None:
                await codex_reference.close()
            async with self._lock:
                self._opening.pop(name, None)
                self._provisional_profiles.pop(name, None)

    async def _viewer_bundle(self) -> ViewerBundle:
        """Hold the framework's viewer bundle for the life of the running shop.

        The bundle belongs to the shop's own installation, so a second open
        would pay a subprocess for an answer already held. A failure is not
        remembered: a shop whose framework installation is repaired must be
        able to open the next project.
        """
        async with self._viewer_lock:
            if self._viewer is None:
                self._viewer = await asyncio.to_thread(resolve_viewer_bundle, self.machinome_command)
            return self._viewer

    async def _build_behind(self, session: Session) -> None:
        """Bring a presented publication up to date behind its open session.

        The publication itself reaches the browser through the watchers. What
        this has to say is that the build is over -- and, when it failed, why;
        a failure leaves the previous publication in place rather than
        replacing it with nothing.
        """
        try:
            outcome = await asyncio.to_thread(
                build_project, session.prepared, allow_failure=True, watched=True
            )
            if outcome.error:
                session.broker.publish("model_build_unavailable", {"reason": outcome.error, "trigger": "open"})
        finally:
            # Whatever the build did -- published new work, published nothing
            # because the document was already current, or failed -- the model
            # is no longer being brought up to date. A build that publishes
            # nothing moves no artifact, so this is the only thing that can say
            # so, and the session must never be left claiming otherwise.
            session.broker.publish("model_build_settled", {"trigger": "open"})
        if self._by_id.get(session.id) is session:
            self.publish_hub("open", session.name, session_id=session.id, model_building=False)

    async def _start_orchestrator(self, session: Session) -> None:
        backend_instances: dict[str, AgentBackend] = {}
        for agent in session.profile.agents:
            if agent.runtime is None:
                raise RuntimeError(f"agent {agent.id!r} has no resolved runtime")
            backend_name = agent.runtime.backend
            if backend_name not in backend_instances:
                backend_instances[backend_name] = self.backend_factory(
                    backend_name,
                    shop_root=self.shop_root,
                    project=session.project_root,
                    model=session.prepared.project_model,
                    broker_url=self.broker_url,
                    command_overrides=self.backend_commands,
                    machinome_command=self.machinome_command,
                    session_id=session.id,
                    skills=_profile_skills(session.profile),
                    codex_service=self.codex_service,
                    codex_reference=session.codex_reference,
                )
        by_agent = {
            agent.id: backend_instances[agent.runtime.backend]
            for agent in session.profile.agents
            if agent.runtime is not None
        }
        resolver_lock = asyncio.Lock()
        async def resolve_backend(backend_name: str) -> AgentBackend:
            async with resolver_lock:
                existing = backend_instances.get(backend_name)
                if existing is not None:
                    return existing
                if backend_name == "codex" and session.codex_reference is None:
                    session.codex_reference = await self.codex_service.acquire(session.id,
                        [role_registry(agent) for agent in session.profile.agents])
                backend = self.backend_factory(
                    backend_name,
                    shop_root=self.shop_root,
                    project=session.project_root,
                    model=session.prepared.project_model,
                    broker_url=self.broker_url,
                    command_overrides=self.backend_commands,
                    machinome_command=self.machinome_command,
                    session_id=session.id,
                    skills=_profile_skills(session.profile),
                    codex_service=self.codex_service,
                    codex_reference=session.codex_reference,
                )
                try:
                    await backend.start()
                except BaseException:
                    try:
                        await backend.close()
                    except BaseException:
                        pass
                    raise
                backend_instances[backend_name] = backend
                session.event_tasks.append(asyncio.create_task(_route_backend_events(orchestrator, backend)))
                return backend

        orchestrator = ShopOrchestrator(
            by_agent,
            LocalBrokerControl(session.broker),
            profile=session.profile,
            shop_root=self.shop_root,
            active_project=session.project_root,
            active_model=session.prepared.project_model,
            backend_resolver=resolve_backend,
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
            self._by_entry.pop(session.name, None)
        await session.close()
        self.publish_hub("closed", session.name)

    async def close_all(self) -> None:
        opening = tuple(self._opening.values())
        for task in opening:
            task.cancel()
        if opening:
            await asyncio.gather(*opening, return_exceptions=True)
        sessions = tuple(self._by_entry.values())
        self._by_entry.clear()
        self._by_id.clear()
        self._provisional_profiles.clear()
        for session in sessions:
            await session.close()
            self.publish_hub("closed", session.name)
        await self.codex_service.close()


def _runtime_value(runtime) -> dict[str, object]:
    return {
        "backend": runtime.backend,
        "provider": runtime.provider,
        "model": runtime.model,
        "effort": runtime.effort,
    }


def _selected_runtime(
    profile: RuntimeProfile,
    role: str,
    backend: str,
    provider: str | None,
    model: str,
    effort: str,
) -> BackendRuntime:
    agent = profile.agent(role)
    if backend == "claude":
        if provider is not None:
            raise ValueError(f"{backend} does not accept a provider")
        return replace(agent.backends[backend], model=model, effort=effort, provider=None)
    if backend == "opencode":
        if not provider:
            raise ValueError("OpenCode requires a provider from its live catalogue")
        return BackendRuntime(
            model,
            effort,
            agent.backends["claude"].tools,
            backend="opencode",
            provider=provider,
        )
    raise ValueError(f"unknown backend: {backend}")


def _folder_of(path: str) -> str:
    """The folder one entry path belongs to; empty for the working folder."""
    head, _, _ = path.rpartition("/")
    return head
