# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
"""The OpenSpec capability and the floor tools it resolves to."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch

from floor.backends.base import session_tool_names
from floor.mcp_server import OPENSPEC_TOOLS, PROFILE_TOOL_MAP, ProjectTools, resolved_tool_names
from floor.openspec import resolve_openspec_command, resolve_openspec_root
from floor.profiles import ProfileError, load_profile


ROOT = Path(__file__).resolve().parents[1]

PROPOSAL = """## Why

The lid and the body meet at a rim whose fit is recorded nowhere.

## What Changes

- Record the interface between the lid and the body.

## Capabilities

### New Capabilities
- `lid-body-interface`: how the lid seats on the body.

## Impact

The lid and body parts.
"""

SPEC_DELTA = """## ADDED Requirements

### Requirement: The lid seats flush on the body

The lid SHALL seat on the body rim with a gap no greater than 0.3 mm.

#### Scenario: Closed lid

- **WHEN** the lid is closed on the body
- **THEN** the gap at the rim measures no more than 0.3 mm
"""


class OpenSpecCapabilityTest(unittest.TestCase):
    def test_the_capability_resolves_to_the_floor_openspec_tools(self) -> None:
        self.assertEqual(resolved_tool_names(("OpenSpec",)), OPENSPEC_TOOLS)
        self.assertEqual(OPENSPEC_TOOLS, ("openspec_setup", "openspec_run"))

    def test_no_other_capability_reaches_an_openspec_tool(self) -> None:
        for capability, resolved in PROFILE_TOOL_MAP.items():
            if capability == "OpenSpec":
                continue
            with self.subTest(capability=capability):
                self.assertEqual(set(resolved) & set(OPENSPEC_TOOLS), set())

    def test_a_profile_may_declare_the_capability_and_unknown_names_still_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            shop = Path(temporary)
            shutil.copytree(ROOT / "profiles", shop / "profiles", symlinks=True)
            shutil.copytree(ROOT / "shop-skills", shop / "shop-skills", symlinks=True)
            manifest = shop / "profiles" / "builder" / "profile.toml"
            value = manifest.read_text()

            manifest.write_text(value.replace('"Grep", "OpenSpec"]', '"Grep"]'))
            declared = load_profile("builder", shop_root=shop).user_agent.backends["claude"].tools
            self.assertNotIn("OpenSpec", declared)

            manifest.write_text(value)
            declared = load_profile("builder", shop_root=shop).user_agent.backends["claude"].tools
            self.assertIn("OpenSpec", declared)

            manifest.write_text(value.replace('"OpenSpec"]', '"OpenSpecs"]'))
            with self.assertRaisesRegex(ProfileError, "claude.*tools.*unsupported"):
                load_profile("builder", shop_root=shop)

    def test_builder_declares_the_capability(self) -> None:
        builder = load_profile("builder", shop_root=ROOT)
        session = session_tool_names(
            builder.user_agent.skills, builder.user_agent.backends["claude"].tools
        )
        for tool in OPENSPEC_TOOLS:
            self.assertIn(tool, session)

    def test_no_fordesmac_session_reaches_an_openspec_tool(self) -> None:
        fordesmac = load_profile("fordesmac", shop_root=ROOT)
        for agent in fordesmac.agents:
            with self.subTest(agent=agent.id):
                declared = agent.backends["claude"].tools
                self.assertNotIn("OpenSpec", declared)
                session = session_tool_names(agent.skills, declared)
                self.assertEqual(set(session) & set(OPENSPEC_TOOLS), set())

        # A role declaring every other capability still reaches none of them.
        every_other = tuple(name for name in PROFILE_TOOL_MAP if name != "OpenSpec")
        self.assertEqual(set(resolved_tool_names(every_other)) & set(OPENSPEC_TOOLS), set())


class OpenSpecProjectRecordTest(unittest.TestCase):
    """Exercised against the real OpenSpec CLI: no stand-in is maintained."""

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        workspace = Path(temporary.name)
        # An ancestor holding a record of its own, as the shop checkout does.
        self.ancestor = workspace / "workspace"
        (self.ancestor / "openspec" / "changes").mkdir(parents=True)
        (self.ancestor / "openspec" / "specs").mkdir(parents=True)
        (self.ancestor / "openspec" / "config.yaml").write_text("schema: spec-driven\n")
        self.project = self.ancestor / "projects" / "thing"
        self.project.mkdir(parents=True)
        for command in (
            ["git", "init", "-q", "-b", "main"],
            ["git", "config", "user.name", "Record Test"],
            ["git", "config", "user.email", "record@example.invalid"],
        ):
            subprocess.run(command, cwd=self.project, check=True)
        (self.project / "part.py").write_text("# a part\n")
        subprocess.run(["git", "add", "part.py"], cwd=self.project, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "initial"], cwd=self.project, check=True)
        self.tools = ProjectTools(self.project)

    # -- helpers -----------------------------------------------------

    def _commits(self) -> int:
        listed = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=self.project,
            capture_output=True,
            text=True,
            check=True,
        )
        return int(listed.stdout.strip())

    def _ancestor_state(self) -> list[tuple[str, str]]:
        return sorted(
            (str(path.relative_to(self.ancestor)), path.read_text())
            for path in (self.ancestor / "openspec").rglob("*")
            if path.is_file()
        )

    def _open_a_change(self, name: str = "lid-body-fit", *, done: bool = False) -> Path:
        self.tools.openspec_run(["new", "change", name])
        change = self.project / "openspec" / "changes" / name
        (change / "proposal.md").write_text(PROPOSAL)
        (change / "specs" / "lid-body-interface").mkdir(parents=True)
        (change / "specs" / "lid-body-interface" / "spec.md").write_text(SPEC_DELTA)
        mark = "x" if done else " "
        (change / "tasks.md").write_text(
            f"## 1. Fit\n\n- [x] 1.1 Model the rim\n- [{mark}] 1.2 Machine the seat\n"
        )
        return change

    # -- group 3: project record preparation -------------------------

    def test_setup_initializes_seeds_house_rules_and_commits(self) -> None:
        before = self._ancestor_state()
        result = self.tools.openspec_setup()

        self.assertTrue(result["ok"])
        self.assertTrue(result["created"])
        config = self.project / "openspec" / "config.yaml"
        self.assertTrue(config.exists())
        text = config.read_text()
        self.assertIn("context:", text)
        self.assertIn("rules:", text)
        self.assertEqual(self._commits(), 2)
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.project,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(status.stdout.strip(), "")
        self.assertEqual(self._ancestor_state(), before)

    def test_a_second_setup_changes_nothing(self) -> None:
        self.tools.openspec_setup()
        config = self.project / "openspec" / "config.yaml"
        # The project owns the file once it exists; improving the seed later
        # must not reach in and rewrite it.
        config.write_text(config.read_text() + "\n# the maker's own note\n")
        subprocess.run(["git", "commit", "-qam", "maker edit"], cwd=self.project, check=True)
        owned = config.read_bytes()
        commits = self._commits()

        result = self.tools.openspec_setup()

        self.assertTrue(result["ok"])
        self.assertFalse(result["created"])
        self.assertEqual(config.read_bytes(), owned)
        self.assertEqual(self._commits(), commits)

    # -- group 4: root containment -----------------------------------

    def test_run_in_an_unprepared_project_names_the_ancestor_root(self) -> None:
        before = self._ancestor_state()
        with self.assertRaises(ValueError) as raised:
            self.tools.openspec_run(["list", "--json"])
        self.assertIn(str(self.ancestor), str(raised.exception))
        self.assertEqual(self._ancestor_state(), before)
        self.assertFalse((self.project / "openspec").exists())

    def test_our_root_resolution_agrees_with_the_cli(self) -> None:
        command = resolve_openspec_command()

        def reported_root() -> str:
            listed = subprocess.run(
                [*command, "list", "--json"],
                cwd=self.project,
                capture_output=True,
                text=True,
                check=True,
            )
            return json.loads(listed.stdout)["root"]["path"]

        self.assertEqual(resolve_openspec_root(self.project), self.ancestor)
        self.assertEqual(reported_root(), str(self.ancestor))

        self.tools.openspec_setup()

        self.assertEqual(resolve_openspec_root(self.project), self.project)
        self.assertEqual(reported_root(), str(self.project))

    def test_run_proceeds_when_the_resolved_root_is_the_project(self) -> None:
        self.tools.openspec_setup()
        result = self.tools.openspec_run(["list", "--json"])
        self.assertTrue(result["ok"])
        self.assertEqual(json.loads(result["stdout"])["root"]["path"], str(self.project))

    # -- group 5: passthrough ----------------------------------------

    def test_run_creates_a_change_and_reports_the_cli_result(self) -> None:
        self.tools.openspec_setup()
        result = self.tools.openspec_run(["new", "change", "lid-body-fit"])

        self.assertTrue(result["ok"])
        self.assertEqual(result["exit_code"], 0)
        self.assertIn("lid-body-fit", result["stdout"])
        self.assertTrue((self.project / "openspec" / "changes" / "lid-body-fit").is_dir())

    def test_rejected_argument_vectors_start_no_process(self) -> None:
        self.tools.openspec_setup()
        rejected = (
            ["store", "list"],
            ["config", "--set", "profile=core"],
            ["feedback", "the tool is fine"],
            ["completion", "install"],
            ["list", "--store", "elsewhere"],
            ["init", str(self.ancestor)],
            ["show", "../../secrets.md"],
            [],
        )
        for vector in rejected:
            with self.subTest(vector=vector):
                with patch("floor.mcp_server.subprocess.run") as run:
                    with self.assertRaises(ValueError):
                        self.tools.openspec_run(vector)
                    run.assert_not_called()

    # -- group 6: the archive gate -----------------------------------

    def test_archiving_over_open_tasks_is_refused_and_names_them(self) -> None:
        self.tools.openspec_setup()
        change = self._open_a_change()

        with self.assertRaises(ValueError) as raised:
            self.tools.openspec_run(["archive", "lid-body-fit", "--yes"])

        message = str(raised.exception)
        self.assertIn("1.2 Machine the seat", message)
        self.assertNotIn("1.1 Model the rim", message)
        self.assertTrue(change.is_dir())
        self.assertFalse(any((self.project / "openspec" / "changes" / "archive").iterdir()))
        self.assertFalse((self.project / "openspec" / "specs" / "lid-body-interface").exists())

    def test_no_argument_overrides_the_archive_gate(self) -> None:
        self.tools.openspec_setup()
        self._open_a_change()
        for vector in (
            ["archive", "lid-body-fit", "--yes", "--force"],
            ["archive", "lid-body-fit", "--no-validate"],
            ["archive", "--yes", "lid-body-fit"],
        ):
            with self.subTest(vector=vector), self.assertRaises(ValueError):
                self.tools.openspec_run(vector)

    def test_a_complete_change_syncs_its_specs_and_archives(self) -> None:
        self.tools.openspec_setup()
        self._open_a_change(done=True)

        result = self.tools.openspec_run(["archive", "lid-body-fit", "--yes"])

        self.assertTrue(result["ok"])
        self.assertFalse((self.project / "openspec" / "changes" / "lid-body-fit").exists())
        archived = list((self.project / "openspec" / "changes" / "archive").iterdir())
        self.assertEqual(len(archived), 1)
        self.assertIn("lid-body-fit", archived[0].name)
        self.assertIn(
            "The lid seats flush on the body",
            (self.project / "openspec" / "specs" / "lid-body-interface" / "spec.md").read_text(),
        )

    # -- group 9: the seeded house rules reach the agent -------------

    def test_the_seeded_rules_reach_the_agent_through_the_cli(self) -> None:
        self.tools.openspec_setup()
        self._open_a_change()
        expected = {
            "proposal": "Name the interfaces the change establishes or alters",
            "specs": "silently lost when the change is archived",
            "design": "the measurement that decided it",
            "tasks": "before the geometry that satisfies it",
        }
        for artifact, rule in expected.items():
            with self.subTest(artifact=artifact):
                result = self.tools.openspec_run(
                    ["instructions", artifact, "--change", "lid-body-fit"]
                )
                self.assertTrue(result["ok"])
                # The vocabulary reaches every artifact through the context.
                self.assertIn("interface between parts", result["stdout"])
                # The artifact's own rules reach only that artifact.
                self.assertIn(rule, result["stdout"])
        tasks = self.tools.openspec_run(["instructions", "tasks", "--change", "lid-body-fit"])
        self.assertIn("`Purpose: TBD` records nothing", tasks["stdout"])


class SpecOnlyCommitTest(unittest.TestCase):
    """A planning commit renders nothing: there is no geometry in it."""

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.project = Path(temporary.name) / "thing"
        self.project.mkdir()
        for command in (
            ["git", "init", "-q", "-b", "main"],
            ["git", "config", "user.name", "Commit Test"],
            ["git", "config", "user.email", "commit@example.invalid"],
        ):
            subprocess.run(command, cwd=self.project, check=True)
        (self.project / "part.py").write_text("# a part\n")
        self.screenshot = self.project / "screenshot.png"
        self.screenshot.write_bytes(b"\x89PNG\r\n\x1a\nSTALE")
        subprocess.run(["git", "add", "part.py", "screenshot.png"], cwd=self.project, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "initial"], cwd=self.project, check=True)
        (self.project / "openspec" / "changes" / "lid-body-fit").mkdir(parents=True)
        (self.project / "openspec" / "config.yaml").write_text("schema: spec-driven\n")
        (self.project / "openspec" / "changes" / "lid-body-fit" / "proposal.md").write_text(PROPOSAL)
        self.tools = ProjectTools(self.project)

    def _staged_at_head(self) -> set[str]:
        listed = subprocess.run(
            ["git", "show", "--name-only", "--format=", "HEAD"],
            cwd=self.project,
            capture_output=True,
            text=True,
            check=True,
        )
        return {line for line in listed.stdout.split() if line}

    def test_a_spec_only_commit_renders_nothing(self) -> None:
        self.tools.git_add(["openspec"])
        with patch("floor.mcp_server.refresh_project_screenshot") as render:
            result = self.tools.git_commit("docs(openspec): propose the lid/body fit")

        self.assertTrue(result["ok"])
        render.assert_not_called()
        self.assertFalse(result["rendered"])
        self.assertIn("no model content", result["note"])
        self.assertEqual(self.screenshot.read_bytes(), b"\x89PNG\r\n\x1a\nSTALE")
        self.assertNotIn("screenshot.png", self._staged_at_head())

    def test_a_commit_carrying_model_source_still_refreshes(self) -> None:
        (self.project / "part.py").write_text("# a part, revised\n")
        self.tools.git_add(["openspec", "part.py"])

        def rendered(*_arguments: object, **_keywords: object) -> SimpleNamespace:
            self.screenshot.write_bytes(b"\x89PNG\r\n\x1a\nFRESH")
            return SimpleNamespace(warning=None)

        with patch("floor.mcp_server.refresh_project_screenshot", side_effect=rendered) as render:
            result = self.tools.git_commit("feat: revise the rim and record it")

        self.assertTrue(result["ok"])
        render.assert_called_once()
        self.assertTrue(result["rendered"])
        self.assertIn("screenshot.png", self._staged_at_head())


if __name__ == "__main__":
    unittest.main()
