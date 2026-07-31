from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RoleContractTest(unittest.TestCase):
    def test_live_codex_roles_use_designer_and_have_no_porter(self) -> None:
        self.assertFalse((ROOT / "agents" / "drawing-office.md").exists())
        self.assertFalse((ROOT / ".codex" / "agents" / "drawing-office.toml").exists())
        self.assertFalse((ROOT / "agents" / "porter.md").exists())
        self.assertFalse((ROOT / ".codex" / "agents" / "porter.toml").exists())
        self.assertTrue((ROOT / "agents" / "designer.md").is_file())
        self.assertIn('name = "designer"', (ROOT / ".codex" / "agents" / "designer.toml").read_text())

    def test_foreman_alone_dispatches_and_holds_the_designer_one_slice_ahead(self) -> None:
        foreman = (ROOT / "agents" / "foreman.md").read_text()
        process = (ROOT / "skills" / "running-the-shop" / "SKILL.md").read_text()
        self.assertIn("Only you dispatch the designer and machinist", foreman)
        self.assertIn("prepare one next drawing as `DRAFT`", process)
        self.assertIn("designer reconciliation pass", process)
        self.assertIn("never poll or invoke a receive command", foreman)

    def test_foreman_prompt_distinguishes_floor_management_from_process_orchestration(self) -> None:
        foreman = (ROOT / "agents" / "foreman.md").read_text()
        process = (ROOT / "skills" / "running-the-shop" / "SKILL.md").read_text()
        self.assertIn("You do not own or monitor the agent processes", foreman)
        self.assertIn("python -m floor.agent assign --role designer", foreman)
        self.assertIn("Your ordinary agent messages are published", foreman)
        self.assertIn("Reports and maker messages wake your persistent thread", process)
        self.assertNotIn("Inspect specialist messages and the two checkpoint paths after 60 seconds", process)

    def test_machinist_is_not_told_to_run_a_live_model_process(self) -> None:
        # The shop watches the project and rebuilds it, so the maker's
        # view no longer depends on an agent keeping a process alive.
        machinist = (ROOT / "agents" / "machinist.md").read_text()
        self.assertNotIn("solid develop", machinist)
        self.assertIn("The shop keeps the maker's artifact view current on its own", machinist)

    def test_specialists_obey_the_assignment_lifecycle_before_loading_role_material(self) -> None:
        for role in ("designer", "machinist"):
            adapter = (ROOT / ".codex" / "agents" / f"{role}.toml").read_text()
            self.assertIn("ASSIGNMENT LIFECYCLE GATE", adapter)
            self.assertIn("before\nreading any file", adapter)
        machinist = (ROOT / "agents" / "machinist.md").read_text()
        self.assertIn("first report the\nblocker through the broker", machinist)

    def test_current_guidance_does_not_claim_claude_or_legacy_role_support(self) -> None:
        current = "\n".join(
            path.read_text()
            for path in (
                ROOT / "README.md",
                ROOT / "docs" / "foreman-listener.md",
                ROOT / "agents" / "foreman.md",
                ROOT / "skills" / "running-the-shop" / "SKILL.md",
            )
        )
        self.assertNotIn("drawing-office", current)
        self.assertNotIn("drawing office", current.lower())
        self.assertIn("Claude orchestration is not yet exercised", current)


if __name__ == "__main__":
    unittest.main()
