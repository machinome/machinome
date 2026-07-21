from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from floor.preparation import PreparationError, prepare_project, primary_shop_root, resolve_project


ROOT = Path(__file__).resolve().parents[1]


class ProjectResolutionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name) / "projects"
        self.home.mkdir()

    def test_accepts_lowercase_kebab_case(self) -> None:
        self.assertEqual(resolve_project("v8-engine", self.home), self.home / "v8-engine")

    def test_rejects_missing_and_unsafe_names(self) -> None:
        for name in (None, "", "V8-engine", "v8 engine", "v8_engine", "../v8", ".", "v8/engine", "/tmp/v8"):
            with self.subTest(name=name), self.assertRaises(PreparationError) as raised:
                resolve_project(name, self.home)
            self.assertEqual(raised.exception.stage, "project-name")

    def test_rejects_a_symlink_escape(self) -> None:
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        (self.home / "escaped").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(PreparationError) as raised:
            resolve_project("escaped", self.home)
        self.assertEqual(raised.exception.stage, "project-path")

    def test_rejects_an_in_home_symlink_alias(self) -> None:
        target = self.home / "target"
        target.mkdir()
        (self.home / "alias").symlink_to(target, target_is_directory=True)
        with self.assertRaises(PreparationError) as raised:
            resolve_project("alias", self.home)
        self.assertEqual(raised.exception.stage, "project-path")


class ProjectPreparationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name) / "projects"
        self.home.mkdir()
        self.fake_solid = Path(self.temporary.name) / "fake_solid.py"
        self.fake_solid.write_text(FAKE_SOLID)
        self.call_log = Path(self.temporary.name) / "solid-calls.jsonl"
        self.command = (sys.executable, str(self.fake_solid))
        self.git_environment = {
            "GIT_AUTHOR_NAME": "Shop Test",
            "GIT_AUTHOR_EMAIL": "shop@example.invalid",
            "GIT_COMMITTER_NAME": "Shop Test",
            "GIT_COMMITTER_EMAIL": "shop@example.invalid",
            "SOLID_CALL_LOG": str(self.call_log),
        }

    def prepare(self, name: str = "new-engine"):
        with patch.dict(os.environ, self.git_environment):
            return prepare_project(name, project_home=self.home, solid_command=self.command)

    def test_missing_project_is_scaffolded_committed_built_and_validated(self) -> None:
        prepared = self.prepare()
        project = self.home / "new-engine"
        self.assertEqual(prepared.project_root, project.resolve())
        self.assertEqual(prepared.model, Path("root"))
        self.assertEqual(prepared.artifact_root, (project / "_build").resolve())
        self.assertEqual(self.call_log.read_text().splitlines()[0], "new:new-engine")
        self.assertTrue((project / "root" / "__init__.py").is_file())
        self.assertEqual(
            subprocess.run(["git", "-C", str(project), "rev-list", "--count", "HEAD"], check=True, text=True, capture_output=True).stdout.strip(),
            "1",
        )
        self.assertEqual(
            set(subprocess.run(["git", "-C", str(project), "ls-files"], check=True, text=True, capture_output=True).stdout.splitlines()),
            {".gitignore", "root/__init__.py"},
        )

    def test_existing_exact_repository_is_reused_without_git_mutation(self) -> None:
        project = self.home / "existing"
        _make_repository(project)
        before = _git_state(project)
        prepared = self.prepare("existing")
        self.assertEqual(prepared.project_root, project.resolve())
        self.assertEqual(_git_state(project), before)
        self.assertEqual(self.call_log.read_text().splitlines(), ["build:root"])

    def test_rejects_existing_file_plain_directory_and_nested_repository(self) -> None:
        (self.home / "file").write_text("not a project")
        (self.home / "plain").mkdir()
        nested = self.home / "nested"
        nested.mkdir()
        _make_repository(nested / "repo")
        for name, stage in (("file", "project-path"), ("plain", "repository"), ("nested", "repository")):
            with self.subTest(name=name), self.assertRaises(PreparationError) as raised:
                self.prepare(name)
            self.assertEqual(raised.exception.stage, stage)

    def test_reports_scaffold_build_snapshot_and_artifact_failures_by_stage(self) -> None:
        cases = {
            "fail-new": "scaffold",
            "fail-build": "build",
            "bad-json": "snapshot",
            "missing-model": "artifact",
            "stale": "snapshot",
        }
        for name, stage in cases.items():
            with self.subTest(name=name), self.assertRaises(PreparationError) as raised:
                self.prepare(name)
            self.assertEqual(raised.exception.stage, stage)
            self.assertIn(str(self.home / name), str(raised.exception))
            if name != "fail-new":
                self.assertTrue((self.home / name).exists(), "failed project evidence must be preserved")

    def test_reports_git_initialization_and_initial_commit_failures_by_stage(self) -> None:
        real_run = subprocess.run
        for name, failing_words, stage in (
            ("git-init-failure", ("git", "init"), "git-init"),
            ("git-commit-failure", ("git", "-C"), "git-commit"),
        ):
            def controlled_run(command, *args, **kwargs):
                command_words = tuple(command)
                if stage == "git-init" and command_words[:2] == failing_words:
                    raise subprocess.CalledProcessError(11, command, stderr="git init failed")
                if stage == "git-commit" and "commit" in command_words:
                    raise subprocess.CalledProcessError(12, command, stderr="git commit failed")
                return real_run(command, *args, **kwargs)

            with self.subTest(stage=stage), patch("floor.preparation.subprocess.run", side_effect=controlled_run):
                with self.assertRaises(PreparationError) as raised:
                    self.prepare(name)
            self.assertEqual(raised.exception.stage, stage)
            self.assertTrue((self.home / name / "root" / "__init__.py").is_file())


class WorkspaceSolidAcceptanceTest(unittest.TestCase):
    def test_selected_workspace_cli_builds_once_and_rejects_an_invalid_model(self) -> None:
        shop = primary_shop_root(ROOT)
        solid = shop / ".venv" / "bin" / "solid"
        framework = shop / "solid-node"
        if not solid.is_file() or not framework.is_dir():
            self.skipTest("development workspace solid-node installation is unavailable")
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            subprocess.run([str(solid), "new", "acceptance"], cwd=home, check=True, capture_output=True, text=True)
            project = home / "acceptance"
            built = subprocess.run([str(solid), "build", "root"], cwd=project, capture_output=True, text=True)
            self.assertEqual(built.returncode, 0, built.stderr)
            snapshot = json.loads((project / "_build" / "viewer.json").read_text())
            models = list(_models(snapshot))
            self.assertTrue(models)
            self.assertTrue(all((project / "_build" / model).is_file() for model in models))
            invalid = subprocess.run([str(solid), "build", "absent"], cwd=project, capture_output=True, text=True)
            self.assertNotEqual(invalid.returncode, 0)
        revision = subprocess.run(["git", "-C", str(framework), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
        self.assertRegex(revision, r"[0-9a-f]{40}")


def _make_repository(project: Path) -> None:
    project.mkdir(parents=True)
    (project / "root").mkdir()
    (project / "root" / "__init__.py").write_text("# existing\n")
    (project / ".gitignore").write_text("_build/\n")
    subprocess.run(["git", "init", "-q", "-b", "main", str(project)], check=True)
    subprocess.run(["git", "-C", str(project), "add", ".gitignore", "root/__init__.py"], check=True)
    subprocess.run(
        ["git", "-C", str(project), "-c", "user.name=Shop Test", "-c", "user.email=shop@example.invalid", "commit", "-q", "-m", "initial"],
        check=True,
    )


def _git_state(project: Path) -> tuple[str, str, str]:
    return tuple(
        subprocess.run(command, check=True, text=True, capture_output=True).stdout
        for command in (
            ["git", "-C", str(project), "rev-parse", "HEAD"],
            ["git", "-C", str(project), "status", "--porcelain=v1"],
            ["git", "-C", str(project), "diff", "--cached"],
        )
    )


def _models(value: object):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "model" and isinstance(child, str):
                yield child
            else:
                yield from _models(child)
    elif isinstance(value, list):
        for child in value:
            yield from _models(child)


FAKE_SOLID = r'''from pathlib import Path
import json
import os
import sys

command, argument = sys.argv[1:3]
cwd = Path.cwd()
with Path(os.environ["SOLID_CALL_LOG"]).open("a") as calls:
    calls.write(f"{command}:{argument}\n")
if command == "new":
    if argument == "fail-new":
        print("scaffold exploded", file=sys.stderr)
        raise SystemExit(9)
    project = cwd / argument
    (project / "root").mkdir(parents=True)
    (project / "root" / "__init__.py").write_text("# scaffold\n")
    (project / ".gitignore").write_text("_build/\n")
    if argument == "stale":
        (project / "_build").mkdir()
        (project / "_build" / "part.stl").write_text("solid old")
        (project / "_build" / "viewer.json").write_text(json.dumps({"version": 1, "root": {"model": "part.stl"}}))
elif command == "build":
    if cwd.name == "fail-build":
        print("build exploded", file=sys.stderr)
        raise SystemExit(10)
    build = cwd / "_build"
    build.mkdir(exist_ok=True)
    if cwd.name == "bad-json":
        (build / "viewer.json").write_text("{")
    elif cwd.name == "missing-model":
        (build / "viewer.json").write_text(json.dumps({"root": {"model": "missing.stl"}}))
    elif cwd.name == "stale":
        pass
    else:
        (build / "part.stl").write_text("solid part")
        (build / "viewer.json").write_text(json.dumps({"version": 1, "root": {"model": "part.stl"}}))
'''
