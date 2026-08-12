from __future__ import annotations

import json
import inspect
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from floor.mcp_server import ProjectTools, TOOL_NAMES, TOOL_SCHEMAS, mcp_command


ROOT = Path(__file__).resolve().parents[1]
FAKE_SOLID = ROOT / "tests" / "fixtures" / "fake_scoped_solid.py"


class ScopedProjectToolsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.project = root / "project"
        self.project.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.project, check=True)
        subprocess.run(
            ["git", "config", "user.name", "Tool Test"], cwd=self.project, check=True
        )
        subprocess.run(
            ["git", "config", "user.email", "tools@example.invalid"],
            cwd=self.project,
            check=True,
        )
        (self.project / ".gitignore").write_text("ignored.txt\n")
        (self.project / "part.txt").write_text("alpha\nbeta\ngamma\n")
        (self.project / "drawing.svg").write_text("<svg>alpha</svg>\n")
        (self.project / "image.png").write_bytes(b"\x89PNG\r\n\x1a\nFAKE")
        (self.project / "ignored.txt").write_text("hidden\n")
        subprocess.run(["git", "add", ".gitignore", "part.txt", "drawing.svg", "image.png"], cwd=self.project, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "initial"], cwd=self.project, check=True)
        self.capture = root / "solid.jsonl"
        self.environment = patch.dict(os.environ, {"FAKE_SCOPED_SOLID_CAPTURE": str(self.capture)})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.tools = ProjectTools(
            self.project,
            solid_command=(sys.executable, str(FAKE_SOLID)),
        )

    def test_exposes_only_ratified_tools(self) -> None:
        self.assertEqual(
            set(TOOL_NAMES),
            {
                "list_dir", "find_files", "search_content", "read_file", "stat",
                "write_file", "edit_file", "apply_patch", "delete_file", "move_file", "make_dir",
                "git_status", "git_diff", "git_log", "git_show", "git_rev_parse_toplevel",
                "git_merge_base_is_ancestor", "git_head", "git_add", "git_commit",
                "solid_build", "solid_test", "solid_snapshot",
                "floor_assign", "floor_direction", "floor_acknowledge",
                "floor_report", "floor_complete",
            },
        )
        for forbidden in ("push", "reset", "checkout", "branch", "rebase"):
            self.assertNotIn(forbidden, TOOL_NAMES)
        self.assertFalse(
            any(fragment in name for name in TOOL_NAMES for fragment in ("http", "request", "url"))
        )

    def test_filesystem_read_write_and_patch_behavior(self) -> None:
        self.assertEqual(self.tools.read_file("part.txt", offset=2, limit=1), "beta\n")
        self.assertEqual(self.tools.read_file("drawing.svg"), "<svg>alpha</svg>\n")
        image = self.tools.read_file("image.png")
        self.assertEqual(image._mime_type, "image/png")
        self.assertTrue(image.data.startswith(b"\x89PNG"))

        listing = self.tools.list_dir(".", recursive=True)
        self.assertIn("part.txt", listing)
        self.assertNotIn("ignored.txt", listing)
        self.assertEqual(self.tools.find_files("*.txt"), ["part.txt"])
        self.assertEqual(self.tools.search_content("beta"), ["part.txt:2:beta"])
        self.assertTrue(self.tools.stat("part.txt")["exists"])

        self.tools.write_file("new/note.txt", "one\n", must_not_exist=True)
        self.tools.edit_file("new/note.txt", "one", "two")
        self.tools.apply_patch(
            "new/note.txt",
            "--- a/new/note.txt\n+++ b/new/note.txt\n@@ -1 +1 @@\n-two\n+three\n",
        )
        self.tools.move_file("new/note.txt", "new/moved.txt")
        self.assertEqual((self.project / "new/moved.txt").read_text(), "three\n")
        self.tools.delete_file("new/moved.txt")
        self.tools.make_dir("empty/child")
        self.assertTrue((self.project / "empty/child").is_dir())

    def test_every_tool_documents_itself_and_its_parameters(self) -> None:
        for name in TOOL_NAMES:
            with self.subTest(tool=name):
                documentation = getattr(ProjectTools, name).__doc__
                self.assertTrue(
                    documentation and documentation.strip(),
                    f"{name} has no docstring, so agents see only its name",
                )
                for parameter, schema in TOOL_SCHEMAS[name]["properties"].items():
                    self.assertTrue(
                        schema.get("description", "").strip(),
                        f"{name}.{parameter} has no description",
                    )

    def test_patch_failures_explain_the_expected_format_and_the_mismatch(self) -> None:
        codex = self.assertRaises(ValueError)
        with codex:
            self.tools.apply_patch(
                "part.txt",
                "*** Begin Patch\n*** Update File: part.txt\n-alpha\n+omega\n*** End Patch\n",
            )
        self.assertIn("unified diff", str(codex.exception))
        self.assertIn("*** Begin Patch", str(codex.exception))

        several = self.assertRaises(ValueError)
        with several:
            self.tools.apply_patch(
                "part.txt",
                "--- a/part.txt\n+++ b/part.txt\n@@ -1 +1 @@\n-alpha\n+omega\n"
                "--- a/other.txt\n+++ b/other.txt\n@@ -1 +1 @@\n-one\n+two\n",
            )
        self.assertIn("one file per call", str(several.exception))

        stale = self.assertRaises(ValueError)
        with stale:
            self.tools.apply_patch(
                "part.txt",
                "--- a/part.txt\n+++ b/part.txt\n@@ -2 +2 @@\n-delta\n+omega\n",
            )
        message = str(stale.exception)
        self.assertIn("line 2", message)
        self.assertIn("part.txt", message)
        self.assertIn("'delta\\n'", message)
        self.assertIn("'beta\\n'", message)
        self.assertEqual((self.project / "part.txt").read_text(), "alpha\nbeta\ngamma\n")

    def test_git_tools_are_project_scoped_and_report_exit_status(self) -> None:
        self.tools.write_file("new.txt", "new\n")
        self.assertIn("new.txt", self.tools.git_status()["stdout"])
        self.assertTrue(self.tools.git_add(["new.txt"])["ok"])
        committed = self.tools.git_commit("add new")
        self.assertTrue(committed["ok"])
        head = self.tools.git_head()
        self.assertEqual(head["branch"], "main")
        self.assertEqual(len(head["sha"]), 40)
        self.assertTrue(self.tools.git_merge_base_is_ancestor(head["sha"])["is_ancestor"])
        self.assertIn("add new", self.tools.git_log(limit=1)["stdout"])
        self.assertEqual(self.tools.git_show("HEAD", "new.txt")["stdout"], "new\n")
        self.assertEqual(self.tools.git_rev_parse_toplevel(), str(self.project))

    def test_solid_tools_preserve_exit_status_and_snapshot_stays_outside_project(self) -> None:
        self.assertTrue(self.tools.solid_build()["ok"])
        failed = self.tools.solid_test("fail", failfast=True)
        self.assertFalse(failed["ok"])
        self.assertEqual(failed["exit_code"], 17)
        before = self.tools.git_status()["stdout"]
        image = self.tools.solid_snapshot(
            time=0.5,
            camera="1,2,3,4,5,6,7",
            imgsize="320x200",
            projection="ortho",
            colorscheme="Cornfield",
            view="axes,edges",
            autocenter=True,
            viewall=True,
        )
        self.assertTrue(image.data.startswith(b"\x89PNG"))
        self.assertEqual(self.tools.git_status()["stdout"], before)
        calls = [json.loads(line) for line in self.capture.read_text().splitlines()]
        snapshot = next(call for call in calls if call["argv"][0] == "snapshot")
        output = Path(snapshot["argv"][snapshot["argv"].index("-o") + 1])
        self.assertNotEqual(output.parent, self.project)
        self.assertFalse(output.exists())

    def test_every_path_bearing_tool_rejects_escape_before_action(self) -> None:
        outside = Path(self.temporary.name) / "outside.txt"
        outside.write_text("outside\n")
        (self.project / "escape").symlink_to(outside)
        calls = (
            lambda: self.tools.list_dir(".."),
            lambda: self.tools.search_content("x", ".."),
            lambda: self.tools.read_file("../outside.txt"),
            lambda: self.tools.stat("escape"),
            lambda: self.tools.write_file("../outside.txt", "changed"),
            lambda: self.tools.edit_file("../outside.txt", "outside", "changed"),
            lambda: self.tools.apply_patch("../outside.txt", ""),
            lambda: self.tools.delete_file("../outside.txt"),
            lambda: self.tools.move_file("../outside.txt", "inside.txt"),
            lambda: self.tools.move_file("part.txt", "../outside.txt"),
            lambda: self.tools.make_dir("../outside-dir"),
            lambda: self.tools.git_diff("../outside.txt"),
            lambda: self.tools.git_log("../outside.txt"),
            lambda: self.tools.git_show("HEAD", "../outside.txt"),
            lambda: self.tools.git_add(["../outside.txt"]),
            lambda: self.tools.solid_build("../outside.txt"),
            lambda: self.tools.solid_test("../outside.txt"),
            lambda: self.tools.solid_snapshot("../outside.txt"),
        )
        for call in calls:
            with self.subTest(call=call):
                with self.assertRaisesRegex(ValueError, "outside active project"):
                    call()
        self.assertEqual(outside.read_text(), "outside\n")
        self.assertFalse((Path(self.temporary.name) / "outside-dir").exists())
        self.assertFalse(self.capture.exists(), "solid must not run after rejected paths")

    def test_floor_tools_map_to_only_the_injected_session(self) -> None:
        tools = ProjectTools(
            self.project,
            solid_command=(sys.executable, str(FAKE_SOLID)),
            floor_url="http://127.0.0.1:9123",
            floor_session="opaque-session",
        )
        for name in (
            "floor_assign", "floor_direction", "floor_acknowledge",
            "floor_report", "floor_complete",
        ):
            parameters = inspect.signature(getattr(tools, name)).parameters
            self.assertNotIn("server", parameters)
            self.assertNotIn("url", parameters)
            self.assertNotIn("route", parameters)

        with patch("floor.agent._request", return_value={"accepted": True}) as request:
            self.assertEqual(
                tools.floor_assign("foreman", "designer", "draw-1", "Draw it"),
                {"accepted": True},
            )
            tools.floor_direction("foreman", "machinist", "Use the release")
            tools.floor_acknowledge("designer", "draw-1")
            tools.floor_report("designer", "foreman", "Released", "draw-1")
            tools.floor_complete("designer", "draw-1")

        self.assertEqual(
            request.call_args_list[0].args,
            (
                "http://127.0.0.1:9123",
                "/api/sessions/opaque-session/envelopes",
                "POST",
                {
                    "kind": "assignment",
                    "sender": "foreman",
                    "recipient": "designer",
                    "body": "Draw it",
                    "assignment_id": "draw-1",
                },
            ),
        )
        self.assertEqual(request.call_args_list[1].args[3]["kind"], "direction")
        self.assertEqual(
            request.call_args_list[2].args[1],
            "/api/sessions/opaque-session/agents/designer/acknowledgments",
        )
        self.assertEqual(request.call_args_list[3].args[3]["kind"], "report")
        self.assertEqual(
            request.call_args_list[4].args[1],
            "/api/sessions/opaque-session/agents/designer/completions",
        )

    def test_stdio_mcp_protocol_lists_and_calls_scoped_tools(self) -> None:
        process = subprocess.Popen(
            mcp_command(
                self.project,
                (sys.executable, str(FAKE_SOLID)),
                floor_url="http://127.0.0.1:9123",
                floor_session="opaque-session",
            ),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**os.environ, "PYTHONPATH": str(ROOT)},
        )
        self.addCleanup(lambda: process.kill() if process.poll() is None else None)
        assert process.stdin is not None
        assert process.stdout is not None

        def rpc(identifier: int, method: str, params: dict | None = None) -> dict:
            request = {"jsonrpc": "2.0", "id": identifier, "method": method}
            if params is not None:
                request["params"] = params
            process.stdin.write(json.dumps(request) + "\n")
            process.stdin.flush()
            return json.loads(process.stdout.readline())

        initialized = rpc(
            1,
            "initialize",
            {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "test", "version": "1"}},
        )
        self.assertEqual(initialized["result"]["serverInfo"]["name"], "solid-node-studio-floor-tools")
        listed = rpc(2, "tools/list")
        self.assertEqual({tool["name"] for tool in listed["result"]["tools"]}, set(TOOL_NAMES))
        image = rpc(3, "tools/call", {"name": "read_file", "arguments": {"path": "image.png"}})
        self.assertEqual(image["result"]["content"][0]["type"], "image")
        escaped = rpc(4, "tools/call", {"name": "read_file", "arguments": {"path": "../outside.txt"}})
        self.assertTrue(escaped["result"]["isError"])

        process.stdin.close()
        self.assertEqual(process.wait(timeout=3), 0)


if __name__ == "__main__":
    unittest.main()
