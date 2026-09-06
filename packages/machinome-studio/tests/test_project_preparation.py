# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json
import base64
import os
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from floor.preparation import (
    REQUIRED_VIEWER_API,
    PreparationError,
    build_project,
    commit_new_project,
    default_solid_command,
    list_projects,
    prepare_project,
    resolve_project,
    resolve_viewer_bundle,
    validate_new_project,
)


ROOT = Path(__file__).resolve().parents[1]


class FrameworkCommandTest(unittest.TestCase):
    def test_default_uses_the_solid_cli_from_the_shop_python_environment(self) -> None:
        with patch("floor.preparation.sys.executable", "/opt/shop-env/bin/python"):
            self.assertEqual(default_solid_command(), ("/opt/shop-env/bin/solid",))


class ProjectResolutionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name) / "projects"
        self.home.mkdir()

    def test_accepts_lowercase_kebab_case(self) -> None:
        self.assertEqual(resolve_project("v8-engine", self.home), self.home / "v8-engine")

    def test_accepts_project_names_without_enforcing_a_style_convention(self) -> None:
        for name in ("v8_engine", "V8 engine", ".prototype"):
            with self.subTest(name=name):
                self.assertEqual(resolve_project(name, self.home), self.home / name)

    def test_rejects_missing_and_unsafe_names(self) -> None:
        for name in (None, "", "../v8", ".", "..", "v8/engine", "v8\\engine", "/tmp/v8", "bad\0name"):
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

    def test_creation_refuses_a_name_used_by_any_existing_entry_without_mutation(self) -> None:
        for name, directory in (("occupied-directory", True), ("occupied-file", False)):
            entry = self.home / name
            entry.mkdir() if directory else entry.write_text("keep me")
            before = entry.stat()
            with self.subTest(name=name), self.assertRaises(PreparationError) as raised:
                validate_new_project(name, self.home)
            self.assertEqual(raised.exception.stage, "project-name")
            self.assertEqual(entry.stat(), before)

    def test_listing_keeps_valid_and_unopenable_entries_independent(self) -> None:
        valid = self.home / "valid_project"
        _make_repository(valid)
        (valid / "pyproject.toml").write_text('[tool.libresolid-studio]\nprofile = "builder"\n')
        subprocess.run(["git", "-C", str(valid), "add", "pyproject.toml"], check=True)
        subprocess.run([
            "git", "-C", str(valid), "-c", "user.name=Shop Test", "-c", "user.email=shop@example.invalid",
            "commit", "-q", "-m", "profile",
        ], check=True)
        (self.home / "not-a-repository").mkdir()
        (self.home / "Bad Name").mkdir()
        (self.home / "README.md").write_text("working-folder notes")

        values = {item.name: item for item in list_projects(self.home)}

        self.assertNotIn("README.md", values)
        self.assertTrue(values["valid_project"].openable)
        self.assertEqual(values["valid_project"].profile, "builder")
        self.assertEqual(values["valid_project"].branch, "main")
        self.assertIsNotNone(values["valid_project"].last_commit)
        self.assertFalse(values["not-a-repository"].openable)
        self.assertIn("repository", values["not-a-repository"].reason or "")
        self.assertFalse(values["Bad Name"].openable)
        self.assertIn("repository", values["Bad Name"].reason or "")


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

    def prepare(
        self,
        name: str = "new-engine",
        *,
        profile: str | None = None,
        allow_build_failure: bool = False,
        project_home: Path | None = None,
    ):
        """Open one project the way the registry does: verify, build, record."""
        home = self.home if project_home is None else project_home
        with patch.dict(os.environ, self.git_environment):
            prepared = prepare_project(
                name,
                project_home=home,
                solid_command=self.command,
                profile=profile,
            )
            outcome = build_project(prepared, allow_failure=allow_build_failure)
            prepared = replace(prepared, build_error=outcome.error)
            commit_new_project(prepared)
            return prepared

    def test_missing_project_is_scaffolded_committed_built_and_validated(self) -> None:
        prepared = self.prepare()
        project = self.home / "new-engine"
        self.assertEqual(prepared.project_root, project.resolve())
        self.assertFalse((self.home / "new_engine").exists())
        self.assertEqual(prepared.model, Path("root"))
        self.assertEqual(prepared.artifact_root, (project / "_build").resolve())
        self.assertTrue(prepared.viewer_bundle.is_file())
        self.assertEqual(prepared.viewer_api_version, 4)
        self.assertEqual(self.call_log.read_text().splitlines()[0], "new:new_engine")
        self.assertTrue((project / "root" / "__init__.py").is_file())
        self.assertFalse((project / "pyproject.toml").exists())
        self.assertEqual(
            subprocess.run(["git", "-C", str(project), "rev-list", "--count", "HEAD"], check=True, text=True, capture_output=True).stdout.strip(),
            "1",
        )
        self.assertEqual(
            set(subprocess.run(["git", "-C", str(project), "ls-files"], check=True, text=True, capture_output=True).stdout.splitlines()),
            {".gitignore", "root/__init__.py", "screenshot.png"},
        )

    def test_creation_records_the_chosen_profile_in_the_initial_commit(self) -> None:
        self.prepare("profiled-project", profile="builder")
        project = self.home / "profiled-project"
        self.assertIn('profile = "builder"', (project / "pyproject.toml").read_text())
        committed = subprocess.run(
            ["git", "-C", str(project), "show", "HEAD:pyproject.toml"],
            check=True,
            text=True,
            capture_output=True,
        ).stdout
        self.assertIn('profile = "builder"', committed)

    def test_build_failure_can_be_reported_without_abandoning_preparation(self) -> None:
        prepared = self.prepare("fail-build", allow_build_failure=True)
        self.assertIn("build exploded", prepared.build_error or "")
        self.assertTrue(prepared.project_root.is_dir())

    def test_missing_project_home_is_created_for_a_first_launch(self) -> None:
        home = self.home.parent / "fresh-projects"
        prepared = self.prepare("new-engine", project_home=home)

        self.assertEqual(prepared.project_root, home / "new-engine")
        self.assertTrue((home / "new-engine" / "root" / "__init__.py").is_file())

    def test_existing_exact_repository_acquires_an_uncommitted_screenshot(self) -> None:
        project = self.home / "existing"
        _make_repository(project)
        before = _git_state(project)
        prepared = self.prepare("existing")
        self.assertEqual(prepared.project_root, project.resolve())
        self.assertEqual(_git_state(project)[0], before[0])
        self.assertEqual(_git_state(project)[1], "?? screenshot.png\n")
        self.assertEqual(
            self.call_log.read_text().splitlines(),
            ["viewer:", "models:--json", "build:", "snapshot:--renderer"],
        )

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
        }
        for name, stage in cases.items():
            with self.subTest(name=name), self.assertRaises(PreparationError) as raised:
                self.prepare(name)
            self.assertEqual(raised.exception.stage, stage)
            self.assertIn(str(self.home / name), str(raised.exception))
            if name != "fail-new":
                self.assertTrue((self.home / name).exists(), "failed project evidence must be preserved")

    def test_accepts_a_valid_unchanged_publication(self) -> None:
        """F2 need not rewrite a manifest when the model is already current."""
        prepared = self.prepare("stale")
        self.assertTrue((prepared.artifact_root / "viewer.json").is_file())

    def test_named_model_publishes_into_its_own_build_directory(self) -> None:
        """A project declaring named models builds each into `_build/<name>`,
        so the shop must take the model's directory from the framework rather
        than assume the project's whole `_build` is one publication."""
        prepared = self.prepare("named-robot")
        project = self.home / "named-robot"

        self.assertEqual(prepared.artifact_root, (project / "_build" / "alpha").resolve())
        self.assertTrue((prepared.artifact_root / "viewer.json").is_file())
        self.assertIsNone(prepared.build_error)

    def test_refuses_a_build_directory_the_framework_places_outside_the_project(self) -> None:
        """The reported directory is served, watched and packaged, so one that
        is not inside the project fails the open instead of opening it."""
        for name in ("escaped-build", "no-default"):
            with self.subTest(name=name), self.assertRaises(PreparationError) as raised:
                self.prepare(name)
            self.assertEqual(raised.exception.stage, "models")

    def test_rejects_a_missing_or_incompatible_viewer_before_building(self) -> None:
        project = self.home / "existing"
        _make_repository(project)
        cases = (
            ({"FAKE_SOLID_VIEWER_MISSING": "1"}, "pip install \"solid-node[viewer]\""),
            ({"FAKE_SOLID_VIEWER_API": "3"}, "viewer API 4 is required but installed viewer API is 3"),
        )
        for environment, expected in cases:
            with self.subTest(environment=environment), patch.dict(os.environ, {**self.git_environment, **environment}):
                # The shop resolves the bundle for itself, so the refusal is
                # the running shop's, not one project's.
                with self.assertRaises(PreparationError) as raised:
                    resolve_viewer_bundle(self.command)
                self.assertEqual(raised.exception.stage, "viewer")
                self.assertIn(expected, str(raised.exception))
                with self.assertRaises(PreparationError) as refused:
                    self.prepare("existing")
                self.assertEqual(refused.exception.stage, "viewer")
        self.assertFalse((project / "_build").exists(), "no build may run without a usable viewer")

    def test_required_viewer_api_matches_the_declared_widget_interface(self) -> None:
        declaration = (ROOT / "floor" / "frontend" / "src" / "solid-node-widget.d.ts").read_text()
        self.assertIn(f"SOLID_NODE_VIEWER_API_VERSION: {REQUIRED_VIEWER_API}", declaration)

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
        solid = ROOT / ".venv" / "bin" / "solid"
        framework = ROOT / "solid-node"
        if not solid.is_file() or not framework.is_dir():
            self.skipTest("development workspace solid-node installation is unavailable")
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            subprocess.run([str(solid), "new", "acceptance"], cwd=home, check=True, capture_output=True, text=True)
            project = home / "acceptance"
            built = subprocess.run([str(solid), "build"], cwd=project, capture_output=True, text=True)
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
import base64
import os
import sys
import tempfile

command = sys.argv[1]
argument = sys.argv[2] if len(sys.argv) > 2 else ""
cwd = Path.cwd()
with Path(os.environ["SOLID_CALL_LOG"]).open("a") as calls:
    calls.write(f"{command}:{argument}\n")


def model_name(project):
    """A project named `named-*` declares one named model, as a project with
    a [tool.solid-node.models] table does; every other one is unnamed."""
    return "alpha" if project.name.startswith("named-") else None


def build_dir(project):
    name = model_name(project)
    return project / "_build" / name if name else project / "_build"


if command == "new":
    if argument == "fail_new":
        print("scaffold exploded", file=sys.stderr)
        raise SystemExit(9)
    # The real CLI normalizes its scaffold directory to a Python package name.
    project = cwd / argument.replace("-", "_")
    (project / "root").mkdir(parents=True)
    (project / "root" / "__init__.py").write_text("# scaffold\n")
    (project / ".gitignore").write_text("_build/\n")
    if argument == "stale":
        (project / "_build").mkdir()
        (project / "_build" / "part.stl").write_text("solid old")
        (project / "_build" / "viewer.json").write_text(json.dumps({"version": 1, "root": {"model": "part.stl"}}))
elif command == "models":
    name = model_name(cwd)
    reported = build_dir(cwd)
    if cwd.name == "escaped-build":
        reported = cwd.parent / "_build"
    print(json.dumps({
        "root": str(cwd),
        "build_root": str(cwd / "_build"),
        "default": name,
        "models": [{
            "name": name,
            "reference": "root.part:Part",
            "default": cwd.name != "no-default",
            "build_dir": str(reported),
            "state": "unbuilt",
        }],
    }))
elif command == "build":
    if cwd.name == "fail-build":
        print("build exploded", file=sys.stderr)
        raise SystemExit(10)
    build = build_dir(cwd)
    build.mkdir(exist_ok=True, parents=True)
    if cwd.name == "bad-json":
        (build / "viewer.json").write_text("{")
    elif cwd.name == "missing-model":
        (build / "viewer.json").write_text(json.dumps({"root": {"model": "missing.stl"}}))
    elif cwd.name == "stale":
        pass
    else:
        (build / "part.stl").write_text("solid part")
        (build / "viewer.json").write_text(json.dumps({"version": 1, "root": {"model": "part.stl"}}))
elif command == "snapshot":
    output = Path(sys.argv[sys.argv.index("-o") + 1])
    output.write_bytes(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAFklEQVR4nGP8/+8dAwMDEwMDAwMDAwAjPwLvkz8BYAAAAABJRU5ErkJggg=="))
elif command == "viewer":
    # The shop asks this without a project, so the test steers it through the
    # environment rather than through a file inside one.
    if os.environ.get("FAKE_SOLID_VIEWER_MISSING"):
        print("pip install \"solid-node[viewer]\"", file=sys.stderr)
        raise SystemExit(18)
    bundle = Path(tempfile.gettempdir()) / f"fake-solid-widget-{os.getpid()}.js"
    bundle.write_text("globalThis.SolidNodeWidget={apiVersion:4,mount(){return Promise.resolve({apiVersion:4,artifactChanged(){return Promise.resolve()},manifestChanged(){return Promise.resolve()},reload(){return Promise.resolve()},assembly(){return{name:'root',path:[],color:null,model:false,children:[]}},setRoot(){},setVisible(){},view(){return{}},dispose(){}})}};")
    print(json.dumps({"path": str(bundle), "apiVersion": int(os.environ.get("FAKE_SOLID_VIEWER_API", "4"))}))
'''
