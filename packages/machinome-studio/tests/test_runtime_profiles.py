# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import shutil
import tempfile
import tomllib
import unittest
from pathlib import Path

from floor.preparation import ProjectRuntimeError, ProjectRuntimeSelection
from floor.profiles import ProfileError, load_profile


ROOT = Path(__file__).resolve().parents[1]


class RuntimeProfileTest(unittest.TestCase):
    def test_builtin_profiles_have_the_ratified_topologies_and_backend_matrix(self) -> None:
        builder = load_profile("builder", shop_root=ROOT)
        self.assertEqual(builder.id, "builder")
        self.assertEqual(builder.user_label, "Maker")
        self.assertEqual(builder.user_agent.id, "builder")
        self.assertEqual(builder.work_mode, "direct")
        self.assertEqual([(agent.id, agent.label) for agent in builder.agents], [("builder", "Builder")])
        self.assertEqual(builder.user_agent.backends["claude"].model, "sonnet")
        self.assertEqual(builder.user_agent.backends["claude"].effort, "medium")

        fordesmac = load_profile("fordesmac", shop_root=ROOT)
        self.assertEqual(fordesmac.work_mode, "delegated")
        self.assertEqual(fordesmac.user_agent.id, "foreman")
        self.assertEqual(
            [(agent.id, agent.label) for agent in fordesmac.agents],
            [("foreman", "Foreman"), ("designer", "Designer"), ("machinist", "Machinist"), ("librarian", "Librarian")],
        )
        self.assertEqual(fordesmac.agent("designer").backends["claude"].model, "opus")
        self.assertEqual(fordesmac.agent("designer").backends["claude"].effort, "medium")
        self.assertEqual(fordesmac.agent("designer").reports_to, "foreman")
        self.assertEqual(fordesmac.agent("foreman").assigns, ("designer", "machinist", "librarian"))

    def test_requested_project_and_default_profile_precedence(self) -> None:
        source_path = ROOT / "projects" / "sample" / "pyproject.toml"
        declared = ProjectRuntimeSelection(source_path.parent, source_path, {}, "builder")

        self.assertEqual(load_profile("fordesmac", shop_root=ROOT, selection=declared).id, "fordesmac")
        self.assertEqual(load_profile(None, shop_root=ROOT, selection=declared).id, "builder")
        self.assertEqual(load_profile(None, shop_root=ROOT).id, "fordesmac")

    def test_project_profile_resolution_errors_name_the_source_and_explicit_requests_still_validate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source_path = Path(temporary) / "projects" / "sample" / "pyproject.toml"
            declared = ProjectRuntimeSelection(source_path.parent, source_path, {}, "missing-profile")

            with self.assertRaisesRegex(
                ProjectRuntimeError,
                r"pyproject\.toml.*missing-profile",
            ):
                load_profile(None, shop_root=ROOT, selection=declared)

            self.assertEqual(
                load_profile("builder", shop_root=ROOT, selection=declared).id,
                "builder",
            )

    def test_skills_are_profile_allowlisted(self) -> None:
        profile = load_profile("builder", shop_root=ROOT)
        agent = profile.user_agent
        self.assertEqual({skill.path.name for skill in agent.skills}, {"machinome", "machinome-api"})
        for skill in agent.skills:
            self.assertTrue((skill.path / "SKILL.md").is_file())
            self.assertTrue(skill.path.is_symlink())
            self.assertEqual(skill.path.resolve().parent, ROOT / "shop-skills")

    def test_allowlisted_skills_carry_the_announcement_their_skill_file_declares(self) -> None:
        agent = load_profile("builder", shop_root=ROOT).user_agent
        self.assertEqual(
            {skill.name for skill in agent.skills}, {"machinome", "machinome-api"}
        )
        for skill in agent.skills:
            self.assertEqual(skill.name, skill.path.name)
            self.assertTrue(skill.description.strip())
            self.assertNotIn("\n", skill.description)
            self.assertIn(skill.description, (skill.path / "SKILL.md").read_text())

    def test_a_skill_that_cannot_describe_itself_fails_validation(self) -> None:
        cases = {
            "frontmatter": "# machinome\n\nBody without frontmatter.\n",
            "name": "---\nname: something-else\ndescription: Real work.\n---\n\nBody.\n",
            "description": "---\nname: machinome\ndescription:   \n---\n\nBody.\n",
            "missing description": "---\nname: machinome\n---\n\nBody.\n",
            "unterminated": "---\nname: machinome\ndescription: Real work.\n\nBody.\n",
        }
        for label, content in cases.items():
            with self.subTest(broken=label), tempfile.TemporaryDirectory() as temporary:
                shop = Path(temporary)
                shutil.copytree(ROOT / "profiles", shop / "profiles", symlinks=True)
                shutil.copytree(ROOT / "shop-skills", shop / "shop-skills", symlinks=True)
                (shop / "shop-skills" / "machinome" / "SKILL.md").write_text(content)
                with self.assertRaisesRegex(ProfileError, "builder.*skills.*machinome"):
                    load_profile("builder", shop_root=shop)

    def test_builtin_profiles_declare_only_profile_explicit_backends(self) -> None:
        for profile_id in ("builder", "fordesmac"):
            with (ROOT / "profiles" / profile_id / "profile.toml").open("rb") as source:
                manifest = tomllib.load(source)
            for agent in manifest["agents"]:
                self.assertEqual(set(agent["backends"]), {"claude"})

    def test_retired_backends_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            shop = Path(temporary)
            shutil.copytree(ROOT / "profiles", shop / "profiles", symlinks=True)
            shutil.copytree(ROOT / "shop-skills", shop / "shop-skills", symlinks=True)
            manifest = shop / "profiles" / "builder" / "profile.toml"
            original = manifest.read_text()
            for retired in ("hermes", "codex"):
                with self.subTest(backend=retired):
                    manifest.write_text(
                        original
                        + f'\n[agents.backends.{retired}]\nmodel = "inherit"\neffort = "inherit"\ntools = "inherit"\n'
                    )
                    with self.assertRaisesRegex(ProfileError, f"unknown key.*{retired}"):
                        load_profile("builder", shop_root=shop)

    def test_invalid_selection_and_unknown_schema_key_fail_with_actionable_errors(self) -> None:
        with self.assertRaisesRegex(ProfileError, "profile.*lowercase kebab-case"):
            load_profile("../builder", shop_root=ROOT)
        with tempfile.TemporaryDirectory() as temporary:
            shop = Path(temporary)
            shutil.copytree(ROOT / "profiles", shop / "profiles", symlinks=True)
            shutil.copytree(ROOT / "shop-skills", shop / "shop-skills", symlinks=True)
            profile = shop / "profiles" / "builder" / "profile.toml"
            profile.write_text(profile.read_text() + "\nmisspelled = true\n")
            with self.assertRaisesRegex(ProfileError, "builder.*unknown key.*misspelled"):
                load_profile("builder", shop_root=shop)

    def test_skill_links_and_prompt_paths_cannot_escape_the_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            shop = Path(temporary)
            shutil.copytree(ROOT / "profiles", shop / "profiles", symlinks=True)
            shutil.copytree(ROOT / "shop-skills", shop / "shop-skills", symlinks=True)
            (shop / "skills").mkdir()
            skills = shop / "profiles" / "builder" / "skills"
            (skills / "machinome").unlink()
            (skills / "machinome").symlink_to(shop / "skills")
            with self.assertRaisesRegex(ProfileError, "builder.*skills.*machinome.*shop-skills"):
                load_profile("builder", shop_root=shop)

    def test_selected_backends_reject_controls_their_adapters_cannot_enforce(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            shop = Path(temporary)
            shutil.copytree(ROOT / "profiles", shop / "profiles", symlinks=True)
            shutil.copytree(ROOT / "shop-skills", shop / "shop-skills", symlinks=True)
            manifest = shop / "profiles" / "builder" / "profile.toml"
            value = manifest.read_text()
            manifest.write_text(value.replace('model = "sonnet"', 'model = "not-a-claude-model"'))
            with self.assertRaisesRegex(ProfileError, "claude.*model.*unsupported"):
                load_profile("builder", shop_root=shop)

            manifest.write_text(value.replace('tools = ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "OpenSpec"]', 'tools = ["ImaginaryTool"]'))
            with self.assertRaisesRegex(ProfileError, "claude.*tools.*unsupported"):
                load_profile("builder", shop_root=shop)

            manifest.write_text(value.replace('[agents.backends.claude]\nmodel = "sonnet"\neffort = "medium"', '[agents.backends.claude]\nmodel = "sonnet"\neffort = "ultra"'))
            with self.assertRaisesRegex(ProfileError, "claude.*effort.*unsupported"):
                load_profile("builder", shop_root=shop)

            manifest.write_text(value.replace('tools = ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "OpenSpec"]', 'tools = "inherit"'))
            with self.assertRaisesRegex(ProfileError, "claude.*tools.*must be a list"):
                load_profile("builder", shop_root=shop)

            # A permission policy is no longer a thing a profile can declare:
            # the tool list is the whole authority a role session holds.
            manifest.write_text(value.replace('effort = "medium"', 'effort = "medium"\npermission = "autonomous"'))
            with self.assertRaisesRegex(ProfileError, "claude.*unknown"):
                load_profile("builder", shop_root=shop)

            manifest.write_text(value.replace('effort = "medium"\n', ''))
            with self.assertRaisesRegex(ProfileError, "claude.*must declare model, effort, and tools"):
                load_profile("builder", shop_root=shop)



if __name__ == "__main__":
    unittest.main()
