from __future__ import annotations

import re
import shutil
import tempfile
import unittest
import os
import sys
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch

from floor.app import Broker
from floor.backends.base import RoleHandle, RuntimeCatalogue, RuntimeChoice
from floor.orchestrator import LocalBrokerControl, ShopOrchestrator
from floor.preparation import ProjectRuntimeError, prepare_project, read_project_runtime
from floor.profiles import BackendRuntime, ProfileError, load_profile, resolve_profile_runtime
from floor.sessions import Session
from tests.fixtures.fake_backend import FakeBackend
from floor.runtime_config import (
    RuntimeConfigConflict,
    config_revision,
    prepare_runtime_edit,
    publish_runtime_edit,
)


ROOT = Path(__file__).resolve().parents[1]


class ProjectRuntimeSelectionTest(unittest.TestCase):
    def _selection(self, source: str):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        home = Path(temporary.name) / "projects"
        project = home / "sample-project"
        project.mkdir(parents=True)
        (project / "pyproject.toml").write_text(source)
        return read_project_runtime("sample-project", project_home=home)

    def test_backend_fixes_selection_arity_and_segment_meaning(self) -> None:
        selection = self._selection(
            """
[tool.solid-node-studio.agents]
foreman = "claude:sonnet"
designer = "claude:opus:high"
machinist = "opencode:anthropic:claude-sonnet-4-5"
librarian = "opencode:openai:gpt-5.4:medium"
"""
        )

        self.assertEqual(
            (selection.agents["foreman"].backend, selection.agents["foreman"].provider,
             selection.agents["foreman"].model, selection.agents["foreman"].effort),
            ("claude", None, "sonnet", None),
        )
        self.assertEqual(selection.agents["designer"].effort, "high")
        self.assertEqual(selection.agents["machinist"].provider, "anthropic")
        self.assertIsNone(selection.agents["machinist"].effort)
        self.assertEqual(selection.agents["librarian"].effort, "medium")

    def test_profile_is_read_beside_agents(self) -> None:
        selection = self._selection(
            '[tool.solid-node-studio]\n'
            'profile = "fordesmac"\n'
            '[tool.solid-node-studio.agents]\n'
            'foreman = "claude:sonnet"\n'
        )

        self.assertEqual(selection.profile, "fordesmac")
        self.assertEqual(set(selection.agents), {"foreman"})

    def test_created_project_declares_the_makers_chosen_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary) / "projects"
            environment = {
                "GIT_AUTHOR_NAME": "Shop Test",
                "GIT_AUTHOR_EMAIL": "shop@example.invalid",
                "GIT_COMMITTER_NAME": "Shop Test",
                "GIT_COMMITTER_EMAIL": "shop@example.invalid",
            }
            with patch.dict(os.environ, environment):
                prepare_project(
                    "created-project",
                    project_home=home,
                    solid_command=(sys.executable, str(ROOT / "tests" / "fixtures" / "fake_solid.py")),
                    profile="builder",
                )
            self.assertEqual(read_project_runtime("created-project", project_home=home).profile, "builder")

    def test_malformed_selections_are_rejected_with_agent_and_value(self) -> None:
        invalid = (
            "imaginary:model",
            "codex:gpt-5.6-terra",
            "claude",
            "claude:opus:high:extra",
            "opencode:provider",
            "opencode::model",
            "claude:not-a-model",
        )
        for value in invalid:
            with self.subTest(value=value):
                with self.assertRaisesRegex(ProjectRuntimeError, r"foreman.*" + value.replace("-", r"\-")):
                    self._selection(f'[tool.solid-node-studio.agents]\nforeman = "{value}"\n')

    def test_reasoning_levels_are_backend_specific(self) -> None:
        for value in ("claude:opus:impossible", "claude:opus:ultra"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ProjectRuntimeError, "foreman.*reasoning"):
                    self._selection(f'[tool.solid-node-studio.agents]\nforeman = "{value}"\n')

        selection = self._selection(
            '[tool.solid-node-studio.agents]\n'
            'foreman = "claude:sonnet:low"\n'
            'designer = "claude:opus:high"\n'
            'machinist = "opencode:anthropic:claude-sonnet-4-5:max"\n'
        )
        self.assertEqual(selection.agents["foreman"].effort, "low")
        self.assertEqual(selection.agents["designer"].effort, "high")
        self.assertEqual(selection.agents["machinist"].effort, "max")

    def test_absent_configuration_and_project_are_side_effect_free(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary) / "projects"
            selection = read_project_runtime("new-project", project_home=home)
            self.assertEqual(selection.agents, {})
            self.assertIsNone(selection.profile)
            self.assertFalse(home.exists())

            project = home / "existing-project"
            project.mkdir(parents=True)
            selection = read_project_runtime("existing-project", project_home=home)
            self.assertEqual(selection.agents, {})
            self.assertIsNone(selection.profile)

            (project / "pyproject.toml").write_text('[tool.solid-node]\nmodel = "part:Part"\n')
            selection = read_project_runtime("existing-project", project_home=home)
            self.assertEqual(selection.agents, {})
            self.assertIsNone(selection.profile)

            (project / "pyproject.toml").write_text('[tool.solid-node-studio]\n')
            selection = read_project_runtime("existing-project", project_home=home)
            self.assertEqual(selection.agents, {})
            self.assertIsNone(selection.profile)

    def test_agent_ids_and_unknown_table_keys_are_rejected(self) -> None:
        with self.assertRaisesRegex(ProjectRuntimeError, "BadAgent.*lowercase kebab-case"):
            self._selection('[tool.solid-node-studio.agents]\nBadAgent = "claude:sonnet"\n')
        with self.assertRaisesRegex(ProjectRuntimeError, "unknown key.*effort"):
            self._selection('[tool.solid-node-studio]\neffort = "high"\n')

    def test_profile_must_be_a_lowercase_kebab_case_string(self) -> None:
        invalid = (42, "../builder", "builder/child", "Builder", "builder..next")
        for value in invalid:
            rendered = repr(value)
            source_value = f'"{value}"' if isinstance(value, str) else str(value)
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    ProjectRuntimeError,
                    r"pyproject\.toml.*profile.*" + re.escape(rendered),
                ):
                    self._selection(f"[tool.solid-node-studio]\nprofile = {source_value}\n")

    def test_resolution_ignores_and_reports_keys_outside_the_roster(self) -> None:
        selection = self._selection(
            '[tool.solid-node-studio.agents]\n'
            'builder = "claude:opus"\n'
            'designer = "claude:sonnet"\n'
        )
        profile = resolve_profile_runtime(load_profile("builder", shop_root=ROOT), selection)
        self.assertEqual(profile.user_agent.runtime.backend, "claude")
        self.assertEqual(profile.ignored_agent_ids, ("designer",))

    def test_unnamed_agents_default_to_profile_claude_runtime(self) -> None:
        selection = self._selection('[tool.solid-node-studio.agents]\ndesigner = "claude:opus"\n')
        profile = resolve_profile_runtime(load_profile("fordesmac", shop_root=ROOT), selection)
        self.assertEqual(profile.agent("foreman").runtime, profile.agent("foreman").backends["claude"])

    def test_project_values_override_only_model_and_reasoning(self) -> None:
        selection = self._selection(
            '[tool.solid-node-studio.agents]\n'
            'designer = "claude:sonnet:high"\n'
            'machinist = "claude:opus"\n'
        )
        profile = resolve_profile_runtime(load_profile("fordesmac", shop_root=ROOT), selection)
        designer = profile.agent("designer")
        default = designer.backends["claude"]
        self.assertEqual(designer.runtime.model, "sonnet")
        self.assertEqual(designer.runtime.effort, "high")
        self.assertEqual(designer.runtime.tools, default.tools)
        self.assertEqual(designer.runtime.permission, default.permission)
        self.assertEqual(profile.agent("machinist").runtime.effort, profile.agent("machinist").backends["claude"].effort)


class RuntimeConfigWriterTest(unittest.TestCase):
    def test_updates_one_agent_and_preserves_comments_and_framework_table(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "pyproject.toml"
            path.write_text(
                '# maker comment\n[tool.solid-node]\nmodel = "root:Assembly"\n\n'
                '[tool.solid-node-studio]\nprofile = "fordesmac"\n\n'
                '[tool.solid-node-studio.agents]\ndesigner = "claude:sonnet:medium" # keep\n'
            )
            revision = config_revision(path)
            runtime = BackendRuntime("opus", "high", "inherit")

            edit = prepare_runtime_edit(path, "designer", runtime, revision)
            published = publish_runtime_edit(edit)

            text = path.read_text()
            self.assertEqual(published, config_revision(path))
            self.assertIn("# maker comment", text)
            self.assertIn('model = "root:Assembly"', text)
            self.assertIn('# keep', text)
            self.assertIn('designer = "claude:opus:high"', text)

    def test_stale_revision_never_overwrites_project_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "pyproject.toml"
            path.write_text('[tool.solid-node-studio]\nprofile = "builder"\n')
            stale = config_revision(path)
            path.write_text('[tool.solid-node-studio]\nprofile = "fordesmac"\n')

            with self.assertRaises(RuntimeConfigConflict):
                prepare_runtime_edit(
                    path, "builder", BackendRuntime("gpt-5.6-sol", "high", "inherit"), stale
                )

            self.assertEqual(path.read_text(), '[tool.solid-node-studio]\nprofile = "fordesmac"\n')


class LiveRuntimeUpdateTest(unittest.IsolatedAsyncioTestCase):
    async def test_temporary_and_persisted_updates_share_the_atomic_role_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            path = project / "pyproject.toml"
            original = '[tool.solid-node-studio]\nprofile = "builder"\n'
            path.write_text(original)
            selection = read_project_runtime(project.name, project_home=project.parent)
            profile = resolve_profile_runtime(load_profile("builder", shop_root=ROOT), selection)
            broker = Broker(profile, session_id="runtime-test")
            backend = FakeBackend()
            orchestrator = ShopOrchestrator(
                backend,
                LocalBrokerControl(broker),
                profile=profile,
                shop_root=ROOT,
                active_project=project,
            )
            await orchestrator.open()
            self.addAsyncCleanup(orchestrator.close)
            session = Session(
                "runtime-test",
                project.name,
                SimpleNamespace(
                    project_root=project,
                    artifact_root=project / "_build",
                    build_environment=None,
                ),
                profile,
                broker,
                orchestrator=orchestrator,
            )

            temporary_result = await session.update_runtime(
                "builder", "claude", None, "opus", "high", persist=False, expected_revision=None
            )
            self.assertFalse(temporary_result["persisted"])
            self.assertEqual(path.read_text(), original)
            self.assertEqual(orchestrator.current_runtime("builder").effort, "high")

            revision = config_revision(path)
            persisted = await session.update_runtime(
                "builder", "claude", None, "opus", "medium", persist=True, expected_revision=revision
            )
            self.assertTrue(persisted["persisted"])
            self.assertIn('builder = "claude:opus:medium"', path.read_text())

            stale = revision
            current = orchestrator.current_runtime("builder")
            with self.assertRaises(RuntimeConfigConflict):
                await session.update_runtime(
                    "builder", "claude", None, "opus", "high", persist=True, expected_revision=stale
                )
            self.assertEqual(orchestrator.current_runtime("builder"), current)

    async def test_pristine_backend_selection_applies_live_and_persists_complete_value(self) -> None:
        class OpenCodeBackend(FakeBackend):
            async def runtime_catalog(self, handle: RoleHandle | None) -> RuntimeCatalogue:
                return RuntimeCatalogue(
                    True, (RuntimeChoice("gpt-5.4", ("high",), "opencode", "openai"),)
                )

        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            path = project / "pyproject.toml"
            path.write_text('[tool.solid-node-studio]\nprofile = "builder"\n')
            selection = read_project_runtime(project.name, project_home=project.parent)
            profile = resolve_profile_runtime(load_profile("builder", shop_root=ROOT), selection)
            broker = Broker(profile, session_id="runtime-switch")
            original, opencode = FakeBackend(), OpenCodeBackend()

            async def resolve_backend(name: str):
                self.assertEqual(name, "opencode")
                return opencode

            orchestrator = ShopOrchestrator(
                original,
                LocalBrokerControl(broker),
                profile=profile,
                shop_root=ROOT,
                active_project=project,
                backend_resolver=resolve_backend,
            )
            await orchestrator.open()
            self.addAsyncCleanup(orchestrator.close)
            session = Session(
                "runtime-switch", project.name,
                SimpleNamespace(project_root=project, artifact_root=project / "_build", build_environment=None),
                profile, broker, orchestrator=orchestrator,
            )

            result = await session.update_runtime(
                "builder", "opencode", "openai", "gpt-5.4", "high",
                persist=True, expected_revision=config_revision(path),
            )

            self.assertEqual(result["runtime"]["backend"], "opencode")
            self.assertIn('builder = "opencode:openai:gpt-5.4:high"', path.read_text())
            self.assertTrue(broker.runtime_pristine("builder"))
            self.assertEqual(opencode.opened_roles[-1][1].agent.runtime.backend, "opencode")
            self.assertIn(original.opened_roles[0][0], [handle.role for handle in original.closed_roles])


class ProfileRuntimeTableTest(unittest.TestCase):
    def _shop(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        shop = Path(temporary.name)
        shutil.copytree(ROOT / "profiles", shop / "profiles", symlinks=True)
        shutil.copytree(ROOT / "shop-skills", shop / "shop-skills", symlinks=True)
        return temporary, shop

    def test_loader_validates_every_backend_table(self) -> None:
        temporary, shop = self._shop()
        with temporary:
            manifest = shop / "profiles" / "builder" / "profile.toml"
            manifest.write_text(manifest.read_text().replace('model = "sonnet"', 'model = "not-a-claude-model"'))
            with self.assertRaisesRegex(ProfileError, "claude.*model.*unsupported"):
                load_profile("builder", shop_root=shop)

    def test_loader_rejects_opencode_profile_table(self) -> None:
        temporary, shop = self._shop()
        with temporary:
            manifest = shop / "profiles" / "builder" / "profile.toml"
            manifest.write_text(
                manifest.read_text()
                + '\n[agents.backends.opencode]\nmodel = "inherit"\neffort = "inherit"\ntools = "inherit"\n'
            )
            with self.assertRaisesRegex(ProfileError, "unknown key.*opencode"):
                load_profile("builder", shop_root=shop)


if __name__ == "__main__":
    unittest.main()
