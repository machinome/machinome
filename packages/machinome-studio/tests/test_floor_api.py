from __future__ import annotations

import json
import os
import socket
import stat
import subprocess
import tempfile
import time
import unittest
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
        projects = _request(self.url("/api/projects"), "GET")
        self.assertEqual(projects["working_folder"], str(self.project_home))
        self.assertEqual(projects["projects"], [])
        event, snapshot = _read_sse_event(self.url("/api/stream"))
        self.assertEqual(event, "snapshot")
        self.assertEqual(snapshot["projects"], [])
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
            "backend": "codex", "provider": None,
            "model": "gpt-5.6-sol", "effort": "high", "persist": False,
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
        response = _request(self.url("/api/projects/engine/session"), "POST")
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
        self.assertEqual({item["name"] for item in hub["projects"]}, {"alpha", "bravo"})

    def test_inventory_lists_unopenable_entries_without_blocking_a_valid_project(self) -> None:
        self._make_project("valid_project")
        (self.project_home / "not-a-repository").mkdir()
        (self.project_home / "Bad Name").mkdir()
        (self.project_home / "README.md").write_text("working-folder notes")
        projects = {item["name"]: item for item in _request(self.url("/api/projects"), "GET")["projects"]}
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
        self.assertEqual(_status(self.url("/projects/broken-model/artifacts/viewer.json"), "GET"), 404)

        healthy = self._make_project("healthy")
        healthy_id = self._open("healthy")
        self.assertTrue(healthy_id)
        self.assertIn("part.stl", _raw(self.url("/projects/healthy/artifacts/viewer.json")))
        self.assertEqual(_status(self.url("/projects/broken-model/artifacts/../healthy/_build/viewer.json"), "GET"), 404)

    def test_closed_project_screenshot_is_inventory_metadata_and_an_exact_safe_route(self) -> None:
        project = self._make_project("preview")
        image = b"\x89PNG\r\n\x1a\npreview"
        (project / "screenshot.png").write_bytes(image)
        listed = self._project("preview")
        self.assertIsInstance(listed["screenshot_revision"], str)
        self.assertEqual(_status(self.url("/projects/preview/screenshot.png"), "GET"), 200)
        self.assertEqual(_status(self.url("/projects/missing/screenshot.png"), "GET"), 404)
        (project / "screenshot.png").unlink()
        (project / "screenshot.png").symlink_to(project / "root" / "__init__.py")
        self.assertIsNone(self._project("preview")["screenshot_revision"])
        self.assertEqual(_status(self.url("/projects/preview/screenshot.png"), "GET"), 404)

    def test_backend_detection_is_read_only_and_repeatable(self) -> None:
        first = _request(self.url("/api/backends"), "GET")["backends"]
        second = _request(self.url("/api/backends/detect"), "POST")["backends"]
        self.assertEqual({item["id"] for item in first}, {"codex", "claude", "opencode"})
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

    def _make_project(self, name: str, profile: str = "builder") -> Path:
        project = self.project_home / name
        (project / "root").mkdir(parents=True)
        (project / "root" / "__init__.py").write_text("# model\n")
        (project / ".gitignore").write_text("_build/\n.fake-solid-builds\n.fake-solid-state.json\n")
        (project / "pyproject.toml").write_text(f'[tool.solid-node-studio]\nprofile = "{profile}"\n')
        subprocess.run(["git", "init", "-q", "-b", "main", str(project)], check=True)
        subprocess.run(["git", "-C", str(project), "add", "--all"], check=True)
        subprocess.run([
            "git", "-C", str(project), "-c", "user.name=Shop Test", "-c", "user.email=shop@example.invalid",
            "commit", "-q", "-m", "fixture",
        ], check=True)
        return project

    def _open(self, name: str) -> str:
        response = _request(self.url(f"/api/projects/{name}/session"), "POST")
        self.assertIn(response["state"], {"opening", "open"})
        _wait_for(lambda: self._project(name)["state"] in {"open", "failed"})
        project = self._project(name)
        self.assertEqual(project["state"], "open", project.get("failure"))
        return str(project["session_id"])

    def _project(self, name: str) -> dict[str, object]:
        projects = _request(self.url("/api/projects"), "GET")["projects"]
        return next(item for item in projects if item["name"] == name)

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
