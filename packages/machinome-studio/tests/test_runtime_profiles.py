from __future__ import annotations

import shutil
import tempfile
import tomllib
import unittest
from pathlib import Path

from floor.profiles import ProfileError, load_profile


ROOT = Path(__file__).resolve().parents[1]


class RuntimeProfileTest(unittest.TestCase):
    def test_builtin_profiles_have_the_ratified_topologies_and_backend_matrix(self) -> None:
        builder = load_profile(None, shop_root=ROOT, backend="codex")
        self.assertEqual(builder.id, "builder")
        self.assertEqual(builder.user_label, "Maker")
        self.assertEqual(builder.user_agent.id, "builder")
        self.assertEqual(builder.work_mode, "direct")
        self.assertEqual([(agent.id, agent.label) for agent in builder.agents], [("builder", "Builder")])
        self.assertEqual(builder.user_agent.runtime.model, "gpt-5.3-codex-spark")
        self.assertEqual(builder.user_agent.runtime.effort, "high")
        self.assertEqual(builder.user_agent.runtime.tools, "inherit")

        fordesmac = load_profile("fordesmac", shop_root=ROOT, backend="claude")
        self.assertEqual(fordesmac.work_mode, "delegated")
        self.assertEqual(fordesmac.user_agent.id, "foreman")
        self.assertEqual(
            [(agent.id, agent.label) for agent in fordesmac.agents],
            [("foreman", "Foreman"), ("designer", "Designer"), ("machinist", "Machinist"), ("librarian", "Librarian")],
        )
        self.assertEqual(fordesmac.agent("designer").runtime.model, "opus")
        self.assertEqual(fordesmac.agent("designer").runtime.effort, "medium")
        self.assertEqual(fordesmac.agent("designer").runtime.permission, "autonomous")
        self.assertEqual(fordesmac.agent("designer").reports_to, "foreman")
        self.assertEqual(fordesmac.agent("foreman").assigns, ("designer", "machinist", "librarian"))

    def test_skills_are_profile_allowlisted(self) -> None:
        profile = load_profile("builder", shop_root=ROOT, backend="codex")
        agent = profile.user_agent
        self.assertEqual({path.name for path in agent.skill_paths}, {"solid-node", "solid-node-api"})
        for path in agent.skill_paths:
            self.assertTrue((path / "SKILL.md").is_file())
            self.assertTrue(path.is_symlink())
            self.assertEqual(path.resolve().parent, ROOT / "shop-skills")

    def test_builtin_profiles_declare_only_profile_explicit_backends(self) -> None:
        for profile_id in ("builder", "fordesmac"):
            with (ROOT / "profiles" / profile_id / "profile.toml").open("rb") as source:
                manifest = tomllib.load(source)
            for agent in manifest["agents"]:
                self.assertEqual(set(agent["backends"]), {"codex", "claude"})

    def test_retired_hermes_backend_is_rejected(self) -> None:
        with self.assertRaisesRegex(ProfileError, "unsupported backend 'hermes'"):
            load_profile("builder", shop_root=ROOT, backend="hermes")

    def test_invalid_selection_and_unknown_schema_key_fail_with_actionable_errors(self) -> None:
        with self.assertRaisesRegex(ProfileError, "profile.*lowercase kebab-case"):
            load_profile("../builder", shop_root=ROOT, backend="codex")
        with tempfile.TemporaryDirectory() as temporary:
            shop = Path(temporary)
            shutil.copytree(ROOT / "profiles", shop / "profiles", symlinks=True)
            shutil.copytree(ROOT / "shop-skills", shop / "shop-skills", symlinks=True)
            profile = shop / "profiles" / "builder" / "profile.toml"
            profile.write_text(profile.read_text() + "\nmisspelled = true\n")
            with self.assertRaisesRegex(ProfileError, "builder.*unknown key.*misspelled"):
                load_profile("builder", shop_root=shop, backend="codex")

    def test_skill_links_and_prompt_paths_cannot_escape_the_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            shop = Path(temporary)
            shutil.copytree(ROOT / "profiles", shop / "profiles", symlinks=True)
            shutil.copytree(ROOT / "shop-skills", shop / "shop-skills", symlinks=True)
            (shop / "skills").mkdir()
            skills = shop / "profiles" / "builder" / "skills"
            (skills / "solid-node").unlink()
            (skills / "solid-node").symlink_to(shop / "skills")
            with self.assertRaisesRegex(ProfileError, "builder.*skills.*solid-node.*shop-skills"):
                load_profile("builder", shop_root=shop, backend="codex")

    def test_selected_backends_reject_controls_their_adapters_cannot_enforce(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            shop = Path(temporary)
            shutil.copytree(ROOT / "profiles", shop / "profiles", symlinks=True)
            shutil.copytree(ROOT / "shop-skills", shop / "shop-skills", symlinks=True)
            manifest = shop / "profiles" / "builder" / "profile.toml"
            value = manifest.read_text()
            manifest.write_text(value.replace('model = "sonnet"', 'model = "not-a-claude-model"'))
            with self.assertRaisesRegex(ProfileError, "claude.*model.*unsupported"):
                load_profile("builder", shop_root=shop, backend="claude")

            manifest.write_text(value.replace('tools = ["Bash", "Read", "Write", "Edit", "Glob", "Grep"]', 'tools = ["ImaginaryTool"]'))
            with self.assertRaisesRegex(ProfileError, "claude.*tools.*unsupported"):
                load_profile("builder", shop_root=shop, backend="claude")

            manifest.write_text(value.replace('[agents.backends.claude]\nmodel = "sonnet"\neffort = "medium"', '[agents.backends.claude]\nmodel = "sonnet"\neffort = "ultra"'))
            with self.assertRaisesRegex(ProfileError, "claude.*effort.*unsupported"):
                load_profile("builder", shop_root=shop, backend="claude")

            manifest.write_text(value.replace('permission = "autonomous"', 'permission = "unattended"'))
            with self.assertRaisesRegex(ProfileError, "claude.*permission.*unsupported"):
                load_profile("builder", shop_root=shop, backend="claude")

            manifest.write_text(value.replace('permission = "autonomous"\n', ''))
            with self.assertRaisesRegex(ProfileError, "claude.*must declare model, effort, tools, and permission"):
                load_profile("builder", shop_root=shop, backend="claude")

            manifest.write_text(value.replace('tools = "inherit"\n\n[agents.backends.claude]', 'tools = "inherit"\npermission = "autonomous"\n\n[agents.backends.claude]'))
            with self.assertRaisesRegex(ProfileError, "codex.*unknown key.*permission"):
                load_profile("builder", shop_root=shop, backend="codex")


if __name__ == "__main__":
    unittest.main()
