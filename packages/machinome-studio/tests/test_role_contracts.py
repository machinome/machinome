# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import unittest
from pathlib import Path

from floor.profiles import load_profile


ROOT = Path(__file__).resolve().parents[1]


class RoleContractTest(unittest.TestCase):
    def test_runtime_prompts_are_profile_owned_and_runtime_skills_are_allowlisted(self) -> None:
        for profile_id in ("builder", "fordesmac"):
            profile = load_profile(profile_id, shop_root=ROOT)
            for agent in profile.agents:
                text = agent.prompt_path.read_text()
                self.assertNotIn("repository `skills/`", text)
                for skill in agent.skills:
                    self.assertTrue((skill.path / "SKILL.md").is_file())
        self.assertFalse((ROOT / "agents" / "foreman.md").exists())
        self.assertFalse((ROOT / ".codex" / "agents" / "foreman.toml").exists())

    def test_fordesmac_foreman_owns_the_pipeline_and_librarian_edge(self) -> None:
        foreman = (ROOT / "profiles" / "fordesmac" / "foreman.md").read_text()
        self.assertIn("Only you dispatch the designer, machinist, and librarian", foreman)
        self.assertIn("`floor_assign` tool", foreman)
        self.assertIn("reports only to you", foreman)
        self.assertNotIn("python -m floor.agent", foreman)
        self.assertIn("one next draft", foreman)
        self.assertNotIn("running-the-shop", foreman)

    def test_builder_is_direct_and_preserves_disassembled_leaf_first_red(self) -> None:
        builder = (ROOT / "profiles" / "builder" / "builder.md").read_text()
        self.assertIn("deliberately\ndisassembled position", builder)
        self.assertIn("already-existing leaf", builder)
        self.assertNotIn("machinome develop --callback", builder)
        self.assertNotIn("assignment ID", builder.split("never self-assign", 1)[0])

    def test_machinist_uses_finite_builds_not_a_live_model_process(self) -> None:
        machinist = (ROOT / "profiles" / "fordesmac" / "machinist.md").read_text()
        self.assertNotIn("machinome develop", machinist)
        self.assertIn("machinome build", machinist)
        self.assertIn('floor_report(sender="machinist", recipient="foreman"', machinist)


if __name__ == "__main__":
    unittest.main()
