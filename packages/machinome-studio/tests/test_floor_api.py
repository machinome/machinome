# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import io
import json
import os
import socket
import stat
import subprocess
import tempfile
import time
import unittest
import zipfile
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from tests.fixtures.shop_process import isolated_launch_directory, subprocess_environment


ROOT = Path(__file__).resolve().parents[1]
FAKE_SOLID = ROOT / "tests" / "fixtures" / "fake_solid.py"


class FloorAPITest(unittest.TestCase):
    def setUp(self) -> None:
        self.port = _free_port()
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.project_home = Path(self.temporary.name) / "projects"
        self.project_home.mkdir()
        self.shop = self.enterContext(isolated_launch_directory())
        self.process = subprocess.Popen(
            [
                "python", "-m", "floor", "--port", str(self.port),
                "--projects-dir", str(self.project_home),
                "--solid-command", str(FAKE_SOLID),
            ],
            cwd=self.shop,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            env=subprocess_environment({
                **os.environ,
                "GIT_AUTHOR_NAME": "Shop Test",
                "GIT_AUTHOR_EMAIL": "shop@example.invalid",
                "GIT_COMMITTER_NAME": "Shop Test",
                "GIT_COMMITTER_EMAIL": "shop@example.invalid",
            }),
        )
        self.addCleanup(self._stop_floor)
        _wait_for(lambda: _request(self.url("/health"), "GET") == {"status": "open"})

    def test_shop_starts_on_an_empty_hub_without_preparing_a_project(self) -> None:
        projects = _request(self.url("/api/entries"), "GET")
        self.assertEqual(projects["working_folder"], str(self.project_home))
        self.assertEqual(projects["entries"], [])
        event, snapshot = _read_sse_event(self.url("/api/stream"))
        self.assertEqual(event, "snapshot")
        self.assertEqual(snapshot["entries"], [])
        self.assertEqual(_status(self.url("/api/runs/shop-floor"), "GET"), 404)

    def test_two_projects_hold_independent_sessions_brokers_rosters_and_conversations(self) -> None:
        self._make_project("alpha")
        self._make_project("bravo")
        alpha = self._open("alpha")
        bravo = self._open("bravo")

        self.assertNotEqual(alpha, bravo)
        for session_id in (alpha, bravo):
            manifested = _request(
                self.url(f"/api/sessions/{session_id}/agents"), "POST",
                {"role": "builder", "label": "Builder"},
            )
            self.assertEqual(manifested["state"], "waiting")
        _request(self.url(f"/api/sessions/{alpha}/conversation"), "POST", {"text": "Alpha only"})
        _request(self.url(f"/api/sessions/{bravo}/conversation"), "POST", {"text": "Bravo only"})

        alpha_state = _request(self.url(f"/api/sessions/{alpha}"), "GET")
        bravo_state = _request(self.url(f"/api/sessions/{bravo}"), "GET")
        self.assertEqual(alpha_state["agents"], bravo_state["agents"])
        self.assertEqual(
            [entry["text"] for entry in _request(self.url(f"/api/sessions/{alpha}/conversation"), "GET")["entries"]],
            ["Alpha only"],
        )
        self.assertEqual(
            [entry["text"] for entry in _request(self.url(f"/api/sessions/{bravo}/conversation"), "GET")["entries"]],
            ["Bravo only"],
        )

    def test_runtime_routes_refuse_sessions_without_a_persistent_agent_backend(self) -> None:
        self._make_project("runtime-less")
        session_id = self._open("runtime-less")
        _request(
            self.url(f"/api/sessions/{session_id}/agents"), "POST",
            {"role": "builder", "label": "Builder"},
        )
        route = self.url(f"/api/sessions/{session_id}/agents/builder/runtime")
        self.assertEqual(_status(route, "GET"), 409)
        self.assertEqual(_status(route, "PATCH", {
            "backend": "claude", "provider": None,
            "model": "opus", "effort": "high", "persist": False,
        }), 409)

    def test_unknown_session_is_refused_and_a_closed_id_cannot_reach_a_reopened_project(self) -> None:
        self._make_project("engine")
        first = self._open("engine")
        self.assertEqual(_status(self.url("/api/sessions/missing/agents"), "POST", {"role": "builder", "label": "Builder"}), 404)
        self.assertEqual(_status(self.url(f"/api/sessions/{first}"), "DELETE"), 202)
        _wait_for(lambda: self._project("engine")["state"] == "closed")
        second = self._open("engine")
        self.assertNotEqual(first, second)
        self.assertEqual(_status(self.url(f"/api/sessions/{first}"), "GET"), 404)
        self.assertEqual(_status(self.url(f"/api/sessions/{first}/conversation"), "POST", {"text": "stale"}), 404)
        self.assertEqual(_request(self.url(f"/api/sessions/{second}/conversation"), "GET")["entries"], [])

    def test_second_open_joins_the_existing_session(self) -> None:
        self._make_project("engine")
        first = self._open("engine")
        response = _request(self.url("/api/sessions"), "POST", {"path": "engine"})
        self.assertEqual(response, {"state": "open", "session_id": first})

    def test_project_and_hub_streams_have_disjoint_scopes(self) -> None:
        self._make_project("alpha")
        self._make_project("bravo")
        alpha = self._open("alpha")
        bravo = self._open("bravo")
        for session_id in (alpha, bravo):
            _request(
                self.url(f"/api/sessions/{session_id}/agents"), "POST",
                {"role": "builder", "label": "Builder"},
            )
        _request(self.url(f"/api/sessions/{alpha}/conversation"), "POST", {"text": "Alpha only"})
        _request(self.url(f"/api/sessions/{bravo}/conversation"), "POST", {"text": "Bravo only"})

        event, project = _read_sse_event(self.url(f"/api/sessions/{alpha}/stream"))
        self.assertEqual(event, "snapshot")
        self.assertEqual([entry["text"] for entry in project["conversation"]], ["Alpha only"])
        event, hub = _read_sse_event(self.url("/api/stream"))
        self.assertEqual(event, "snapshot")
        self.assertNotIn("conversation", hub)
        self.assertEqual({item["path"] for item in hub["entries"]}, {"alpha", "bravo"})

    def test_inventory_lists_unopenable_entries_without_blocking_a_valid_project(self) -> None:
        self._make_project("valid_project")
        (self.project_home / "not-a-repository").mkdir()
        (self.project_home / "Bad Name").mkdir()
        (self.project_home / "README.md").write_text("working-folder notes")
        projects = {item["name"]: item for item in self._entries()}
        self.assertNotIn("README.md", projects)
        self.assertTrue(projects["valid_project"]["openable"])
        self.assertFalse(projects["not-a-repository"]["openable"])
        self.assertIn("repository", projects["not-a-repository"]["reason"])
        self.assertFalse(projects["Bad Name"]["openable"])
        self.assertIn("repository", projects["Bad Name"]["reason"])
        self.assertEqual(self._project("valid_project")["state"], "closed")
        self.assertTrue(self._open("valid_project"))

    def test_creation_writes_the_chosen_profile_and_rejects_every_collision(self) -> None:
        response = _request(
            self.url("/api/projects"), "POST", {"name": "new_engine", "profile": "builder"}
        )
        self.assertEqual(response["state"], "opening")
        _wait_for(lambda: self._project("new_engine")["state"] == "open")
        self.assertIn('profile = "builder"', (self.project_home / "new_engine" / "pyproject.toml").read_text())
        self.assertEqual(
            subprocess.run(
                ["git", "-C", str(self.project_home / "new_engine"), "show", "HEAD:pyproject.toml"],
                check=True, text=True, capture_output=True,
            ).stdout.count('profile = "builder"'),
            1,
        )

        (self.project_home / "occupied").write_text("not a directory")
        self.assertEqual(_status(self.url("/api/projects"), "POST", {"name": "occupied", "profile": "builder"}), 409)
        self.assertEqual(_status(self.url("/api/projects"), "POST", {"name": "../escape", "profile": "builder"}), 409)

    def test_a_failed_initial_build_still_opens_and_artifacts_are_project_scoped(self) -> None:
        project = self._make_project("broken-model")
        (project / ".fake-solid-state.json").write_text(json.dumps({"fail": "model exploded"}))
        session_id = self._open("broken-model")
        run = _request(self.url(f"/api/sessions/{session_id}"), "GET")
        self.assertTrue(any(event["kind"] == "model_build_unavailable" for event in run["events"]))
        self.assertEqual(_status(self.url(f"/api/sessions/{session_id}/artifacts/viewer.json"), "GET"), 404)

        healthy = self._make_project("healthy")
        healthy_id = self._open("healthy")
        self.assertTrue(healthy_id)
        self.assertIn("part.stl", _raw(self.url(f"/api/sessions/{healthy_id}/artifacts/viewer.json")))
        self.assertEqual(_status(self.url(f"/api/sessions/{session_id}/artifacts/../healthy/_build/viewer.json"), "GET"), 404)

    def test_build_package_download_is_session_scoped_and_deterministic(self) -> None:
        project = self._make_project("printable")
        viewer = {
            "version": 1,
            "root": {"name": "part", "model": "part.stl", "piece": "0123456789ab"},
            "pieces": [{
                "id": "0123456789ab", "name": "Fixture Part", "count": 4,
                "models": ["part.stl"], "sources": ["root/__init__.py"],
                "size": [10, 20, 30], "volume": 6000, "watertight": True,
            }],
        }
        (project / ".fake-solid-state.json").write_text(json.dumps({
            "model_content": "solid fixture\nendsolid fixture\n",
            "viewer": viewer,
        }))
        session_id = self._open("printable")
        url = self.url(f"/api/sessions/{session_id}/build-package")
        with urlopen(url, timeout=5) as response:  # nosec: local test service
            first = response.read()
            self.assertEqual(response.headers.get_content_type(), "application/zip")
            self.assertEqual(response.headers["Cache-Control"], "no-store")
            self.assertEqual(
                response.headers["Content-Disposition"],
                'attachment; filename="printable-print-package.zip"',
            )
        with urlopen(url, timeout=5) as response:  # nosec: local test service
            self.assertEqual(response.read(), first)
        with zipfile.ZipFile(io.BytesIO(first)) as archive:
            self.assertEqual(archive.namelist(), ["README.md", "fixture-part-0123456789ab.stl"])
            self.assertIn("| `fixture-part-0123456789ab.stl` | 4 |", archive.read("README.md").decode())
        self.assertEqual(_status(self.url("/api/sessions/unknown/build-package"), "GET"), 404)

    def test_closed_project_screenshot_is_inventory_metadata_and_an_exact_safe_route(self) -> None:
        project = self._make_project("preview")
        image = b"\x89PNG\r\n\x1a\npreview"
        (project / "screenshot.png").write_bytes(image)
        listed = self._project("preview")
        self.assertIsInstance(listed["screenshot_revision"], str)
        self.assertEqual(_status(self.url("/api/screenshot?path=preview"), "GET"), 200)
        self.assertEqual(_status(self.url("/api/screenshot?path=missing"), "GET"), 404)
        (project / "screenshot.png").unlink()
        (project / "screenshot.png").symlink_to(project / "root" / "__init__.py")
        self.assertIsNone(self._project("preview")["screenshot_revision"])
        self.assertEqual(_status(self.url("/api/screenshot?path=preview"), "GET"), 404)

    def test_a_folder_of_projects_is_entered_rather_than_listed_flat(self) -> None:
        (self.project_home / "sandbox").mkdir()
        self._make_project("sandbox/windmill")
        self._make_project("top-level")

        top = {item["name"]: item for item in self._entries()}
        self.assertEqual(top["sandbox"]["kind"], "folder")
        self.assertEqual(top["sandbox"]["projects"], 1)
        self.assertNotIn("windmill", top)

        inside = {item["name"]: item for item in self._entries("sandbox")}
        self.assertEqual(inside["windmill"]["kind"], "project")
        self.assertEqual(inside["windmill"]["path"], "sandbox/windmill")
        self.assertTrue(self._open("sandbox/windmill"))

    def test_two_models_of_one_repository_open_as_two_sessions(self) -> None:
        self._make_project("clocks", models=("wall_clock_01", "wall_clock_02"))

        listed = {item["name"]: item for item in self._entries()}
        self.assertEqual(listed["clocks"]["kind"], "folder")
        self.assertEqual(listed["clocks"]["projects"], 2)

        models = {item["name"]: item for item in self._entries("clocks")}
        self.assertEqual(sorted(models), ["wall_clock_01", "wall_clock_02"])

        first = self._open("clocks/wall_clock_01")
        second = self._open("clocks/wall_clock_02")
        self.assertNotEqual(first, second)

        # Each session builds and serves its own model's publication.
        self.assertIn("part.stl", _raw(self.url(f"/api/sessions/{first}/artifacts/viewer.json")))
        self.assertIn("part.stl", _raw(self.url(f"/api/sessions/{second}/artifacts/viewer.json")))
        for model in ("wall_clock_01", "wall_clock_02"):
            self.assertTrue((self.project_home / "clocks" / "_build" / model / "viewer.json").is_file())

        for session_id in (first, second):
            _request(
                self.url(f"/api/sessions/{session_id}/agents"), "POST",
                {"role": "builder", "label": "Builder"},
            )
        _request(self.url(f"/api/sessions/{first}/conversation"), "POST", {"text": "First clock only"})
        self.assertEqual(
            [entry["text"] for entry in _request(self.url(f"/api/sessions/{second}/conversation"), "GET")["entries"]],
            [],
        )

    def test_a_model_preview_is_served_per_model(self) -> None:
        project = self._make_project("clocks", models=("wall_clock_01", "wall_clock_02"))
        image = b"\x89PNG\r\n\x1a\nfirst clock"
        (project / "screenshots").mkdir()
        (project / "screenshots" / "wall_clock_01.png").write_bytes(image)

        models = {item["name"]: item for item in self._entries("clocks")}
        self.assertIsInstance(models["wall_clock_01"]["screenshot_revision"], str)
        self.assertIsNone(models["wall_clock_02"]["screenshot_revision"])
        self.assertEqual(_status(self.url("/api/screenshot?path=clocks/wall_clock_01"), "GET"), 200)
        self.assertEqual(_status(self.url("/api/screenshot?path=clocks/wall_clock_02"), "GET"), 404)
        self.assertEqual(_status(self.url("/api/screenshot?path=clocks/wall_clock_09"), "GET"), 404)

    def test_a_multi_model_card_previews_its_models_from_the_hub_listing(self) -> None:
        project = self._make_project("clocks", models=("wall_clock_01", "wall_clock_02"))
        image = b"\x89PNG\r\n\x1a\nfirst clock"
        (project / "screenshots").mkdir()
        (project / "screenshots" / "wall_clock_01.png").write_bytes(image)
        self._make_project("sandbox/windmill")

        listed = {item["name"]: item for item in self._entries()}

        self.assertEqual(listed["sandbox"]["previews"], [])
        previews = listed["clocks"]["previews"]
        self.assertEqual(
            [preview["path"] for preview in previews],
            ["clocks/wall_clock_01", "clocks/wall_clock_02"],
        )
        self.assertIsInstance(previews[0]["revision"], str)
        self.assertIsNone(previews[1]["revision"])
        self.assertEqual(
            _status(self.url(f"/api/screenshot?path={previews[0]['path']}"), "GET"), 200,
        )

    def test_backend_detection_is_read_only_and_repeatable(self) -> None:
        first = _request(self.url("/api/backends"), "GET")["backends"]
        second = _request(self.url("/api/backends/detect"), "POST")["backends"]
        self.assertEqual({item["id"] for item in first}, {"claude", "opencode"})
        self.assertEqual([item["id"] for item in first], [item["id"] for item in second])
        self.assertTrue(all(set(item) == {"id", "found", "executable", "version", "model"} for item in first))

    def test_source_routes_list_read_and_revision_check_atomic_saves_per_session(self) -> None:
        alpha_project = self._make_project("source-alpha")
        bravo_project = self._make_project("source-bravo")
        (alpha_project / "agent.py").write_text("agent = True\n")
        (alpha_project / "ignored.py").write_text("ignored = True\n")
        with (alpha_project / ".gitignore").open("a") as ignore:
            ignore.write("ignored.py\n")
        alpha = self._open("source-alpha")
        bravo = self._open("source-bravo")

        entries = _request(self.url(f"/api/sessions/{alpha}/source"), "GET")["entries"]
        paths = {entry["path"] for entry in entries}
        self.assertIn("agent.py", paths)
        self.assertIn("root/__init__.py", paths)
        self.assertNotIn("ignored.py", paths)
        self.assertFalse(any(path == ".git" or path.startswith((".git/", "_build")) for path in paths))

        opened = _request(self.url(f"/api/sessions/{alpha}/source/root/__init__.py"), "GET")
        mode = stat.S_IMODE((alpha_project / "root" / "__init__.py").stat().st_mode)
        saved = _request(
            self.url(f"/api/sessions/{alpha}/source/root/__init__.py"),
            "PUT",
            {"content": "# maker edit\n", "expected_revision": opened["revision"]},
        )
        self.assertNotEqual(opened["revision"], saved["revision"])
        self.assertEqual((alpha_project / "root" / "__init__.py").read_text(), "# maker edit\n")
        self.assertEqual(stat.S_IMODE((alpha_project / "root" / "__init__.py").stat().st_mode), mode)

        self.assertEqual(
            _status(
                self.url(f"/api/sessions/{alpha}/source/root/__init__.py"),
                "PUT",
                {"content": "# stale\n", "expected_revision": opened["revision"]},
            ),
            409,
        )
        self.assertEqual((alpha_project / "root" / "__init__.py").read_text(), "# maker edit\n")
        self.assertEqual(_status(self.url(f"/api/sessions/{alpha}/source/new.py"), "PUT", {"content": "new\n", "expected_revision": "0" * 64}), 404)
        self.assertEqual(_status(self.url(f"/api/sessions/{bravo}/source/agent.py"), "GET"), 404)
        self.assertEqual((bravo_project / "root" / "__init__.py").read_text(), "# model\n")

    def test_source_preview_route_serves_only_valid_png_bytes(self) -> None:
        project = self._make_project("source-preview")
        image = b"\x89PNG\r\n\x1a\npreview"
        (project / "preview.png").write_bytes(image)
        (project / "malformed.png").write_bytes(b"not a png")
        session_id = self._open("source-preview")

        with urlopen(self.url(f"/api/sessions/{session_id}/source-preview/preview.png"), timeout=5) as response:  # nosec: local test service
            self.assertEqual(response.read(), image)
            self.assertEqual(response.headers.get_content_type(), "image/png")
            self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
            self.assertEqual(response.headers["Cache-Control"], "no-cache")

        self.assertEqual(_status(self.url(f"/api/sessions/{session_id}/source-preview/malformed.png"), "GET"), 404)
        self.assertEqual(_status(self.url(f"/api/sessions/{session_id}/source-preview/root/__init__.py"), "GET"), 404)

    def _make_project(self, name: str, profile: str = "builder", models: tuple[str, ...] = ()) -> Path:
        project = self.project_home / name
        (project / "root").mkdir(parents=True)
        (project / "root" / "__init__.py").write_text("# model\n")
        (project / ".gitignore").write_text("_build/\n.fake-solid-builds\n.fake-solid-state.json\n")
        declared = "".join(
            f"\n[tool.solid-node.models]\n" + "".join(f'{model} = "root:Root"\n' for model in models)
            for _ in (models,) if models
        )
        (project / "pyproject.toml").write_text(f'[tool.libresolid-studio]\nprofile = "{profile}"\n{declared}')
        if models:
            (project / ".fake-solid-state.json").write_text(json.dumps({"models": list(models)}))
        subprocess.run(["git", "init", "-q", "-b", "main", str(project)], check=True)
        subprocess.run(["git", "-C", str(project), "add", "--all"], check=True)
        subprocess.run([
            "git", "-C", str(project), "-c", "user.name=Shop Test", "-c", "user.email=shop@example.invalid",
            "commit", "-q", "-m", "fixture",
        ], check=True)
        return project

    def _open(self, path: str) -> str:
        response = _request(self.url("/api/sessions"), "POST", {"path": path})
        self.assertIn(response["state"], {"opening", "open"})
        _wait_for(lambda: self._project(path)["state"] in {"open", "failed"})
        project = self._project(path)
        self.assertEqual(project["state"], "open", project.get("failure"))
        return str(project["session_id"])

    def _entries(self, folder: str = "") -> list[dict[str, object]]:
        return _request(self.url(f"/api/entries?folder={folder}"), "GET")["entries"]

    def _project(self, path: str) -> dict[str, object]:
        folder, _, _ = path.rpartition("/")
        return next(item for item in self._entries(folder) if item["path"] == path)

    def url(self, path: str) -> str:
        return f"http://127.0.0.1:{self.port}{path}"

    def _stop_floor(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        if self.process.stderr is not None:
            self.process.stderr.close()


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _wait_for(predicate, timeout: float = 8) -> None:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            if predicate():
                return
        except (OSError, StopIteration) as error:
            last_error = error
        time.sleep(0.05)
    raise AssertionError(f"condition did not become true: {last_error}")


def _request(url: str, method: str, body: dict[str, str] | None = None) -> dict[str, object]:
    request = Request(
        url,
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=5) as response:  # nosec: local test service
        data = response.read()
        return json.loads(data) if data else {}


def _status(url: str, method: str, body: dict[str, str] | None = None) -> int:
    try:
        request = Request(
            url,
            data=json.dumps(body).encode() if body is not None else None,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=5) as response:  # nosec: local test service
            return response.status
    except HTTPError as error:
        return error.code


def _raw(url: str) -> str:
    with urlopen(url, timeout=5) as response:  # nosec: local test service
        return response.read().decode()


def _read_sse_event(url: str) -> tuple[str, dict[str, object]]:
    event = ""
    data = ""
    with urlopen(url, timeout=5) as response:  # nosec: local test service
        for raw_line in response:
            line = raw_line.decode().rstrip("\r\n")
            if not line:
                return event, json.loads(data)
            if line.startswith("event: "):
                event = line.removeprefix("event: ")
            elif line.startswith("data: "):
                data = line.removeprefix("data: ")
    raise AssertionError("stream ended before its first event")


if __name__ == "__main__":
    unittest.main()
