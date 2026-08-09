from __future__ import annotations

import re
import shutil
import tempfile
import unittest
from pathlib import Path

from floor.preparation import ProjectRuntimeError, read_project_runtime
from floor.profiles import ProfileError, load_profile, resolve_profile_runtime


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
foreman = "codex:gpt-5.6-terra"
designer = "claude:opus:high"
machinist = "opencode:anthropic:claude-sonnet-4-5"
librarian = "opencode:openai:gpt-5.4:medium"
"""
        )

        self.assertEqual(
            (selection.agents["foreman"].backend, selection.agents["foreman"].provider,
             selection.agents["foreman"].model, selection.agents["foreman"].effort),
            ("codex", None, "gpt-5.6-terra", None),
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
            'foreman = "codex:gpt-5.6-terra"\n'
        )

        self.assertEqual(selection.profile, "fordesmac")
        self.assertEqual(set(selection.agents), {"foreman"})

    def test_malformed_selections_are_rejected_with_agent_and_value(self) -> None:
        invalid = (
            "imaginary:model",
            "codex",
            "codex:model:high:extra",
            "opencode:provider",
            "opencode::model",
            "claude:not-a-model",
        )
        for value in invalid:
            with self.subTest(value=value):
                with self.assertRaisesRegex(ProjectRuntimeError, r"foreman.*" + value.replace("-", r"\-")):
                    self._selection(f'[tool.solid-node-studio.agents]\nforeman = "{value}"\n')

    def test_reasoning_levels_are_backend_specific(self) -> None:
        for value in ("codex:gpt-5.6-terra:impossible", "claude:opus:ultra"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ProjectRuntimeError, "foreman.*reasoning"):
                    self._selection(f'[tool.solid-node-studio.agents]\nforeman = "{value}"\n')

        selection = self._selection(
            '[tool.solid-node-studio.agents]\n'
            'foreman = "codex:gpt-5.6-terra:ultra"\n'
            'designer = "claude:opus:high"\n'
            'machinist = "opencode:anthropic:claude-sonnet-4-5:max"\n'
        )
        self.assertEqual(selection.agents["foreman"].effort, "ultra")
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
            self._selection('[tool.solid-node-studio.agents]\nBadAgent = "codex:gpt-5.6-terra"\n')
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
            'designer = "codex:gpt-5.6-sol"\n'
        )
        profile = resolve_profile_runtime(load_profile("builder", shop_root=ROOT), selection)
        self.assertEqual(profile.user_agent.runtime.backend, "claude")
        self.assertEqual(profile.ignored_agent_ids, ("designer",))

    def test_unnamed_agents_default_to_profile_codex_runtime(self) -> None:
        selection = self._selection('[tool.solid-node-studio.agents]\ndesigner = "claude:opus"\n')
        profile = resolve_profile_runtime(load_profile("fordesmac", shop_root=ROOT), selection)
        self.assertEqual(profile.agent("foreman").runtime, profile.agent("foreman").backends["codex"])

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
