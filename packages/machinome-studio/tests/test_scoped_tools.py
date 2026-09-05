# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
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
                "openspec_setup", "openspec_run",
                "floor_assign", "floor_direction", "floor_acknowledge",
                "floor_report", "floor_complete",
                "load_skill",
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
            "--- a/new/note.txt\n+++ b/new/note.txt\n@@ -1 +1 @@\n-two\n+three\n",
            "new/note.txt",
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
                "*** Begin Patch\n*** Update File: part.txt\n-alpha\n+omega\n*** End Patch\n",
            )
        self.assertIn("unified diff", str(codex.exception))
        self.assertIn("*** Begin Patch", str(codex.exception))

        stale = self.assertRaises(ValueError)
        with stale:
            self.tools.apply_patch(
                "--- a/part.txt\n+++ b/part.txt\n@@ -2 +2 @@\n-delta\n+omega\n",
                "part.txt",
            )
        message = str(stale.exception)
        self.assertIn("line 2", message)
        self.assertIn("part.txt", message)
        self.assertIn("'delta\\n'", message)
        self.assertIn("'beta\\n'", message)
        self.assertEqual((self.project / "part.txt").read_text(), "alpha\nbeta\ngamma\n")

    def test_one_patch_changes_creates_and_deletes_several_files(self) -> None:
        (self.project / "other.txt").write_text("one\ntwo\n")
        result = self.tools.apply_patch(unified_diff=(
            "--- a/part.txt\n+++ b/part.txt\n"
            "@@ -1,3 +1,3 @@\n alpha\n-beta\n+BETA\n gamma\n"
            "--- a/other.txt\n+++ b/other.txt\n"
            "@@ -1,2 +1,2 @@\n-one\n+ONE\n two\n"
            "--- /dev/null\n+++ b/added/fresh.txt\n"
            "@@ -0,0 +1,2 @@\n+first\n+second\n"
            "--- a/drawing.svg\n+++ /dev/null\n"
            "@@ -1 +0,0 @@\n-<svg>alpha</svg>\n"
        ))

        self.assertEqual((self.project / "part.txt").read_text(), "alpha\nBETA\ngamma\n")
        self.assertEqual((self.project / "other.txt").read_text(), "ONE\ntwo\n")
        self.assertEqual((self.project / "added/fresh.txt").read_text(), "first\nsecond\n")
        self.assertFalse((self.project / "drawing.svg").exists())
        self.assertEqual(
            {entry["path"]: entry["change"] for entry in result["files"]},
            {
                "part.txt": "changed",
                "other.txt": "changed",
                "added/fresh.txt": "created",
                "drawing.svg": "deleted",
            },
        )

    def test_a_patch_produced_by_git_diff_applies_unedited(self) -> None:
        (self.project / "other.txt").write_text("one\ntwo\n")
        self.tools.apply_patch(
            "diff --git a/part.txt b/part.txt\n"
            "index fbbee86..cd964df 100644\n"
            "--- a/part.txt\n+++ b/part.txt\n"
            "@@ -1,3 +1,3 @@\n alpha\n-beta\n+BETA\n gamma\n"
            "diff --git a/other.txt b/other.txt\n"
            "index 814f4a4..4c1ee58 100644\n"
            "--- a/other.txt\n+++ b/other.txt\n"
            "@@ -1,2 +1,2 @@\n-one\n+ONE\n two\n"
            "diff --git a/fresh.txt b/fresh.txt\n"
            "new file mode 100644\n"
            "index 0000000..3e75765\n"
            "--- /dev/null\n+++ b/fresh.txt\n"
            "@@ -0,0 +1 @@\n+new\n"
        )
        self.assertEqual((self.project / "part.txt").read_text(), "alpha\nBETA\ngamma\n")
        self.assertEqual((self.project / "other.txt").read_text(), "ONE\ntwo\n")
        self.assertEqual((self.project / "fresh.txt").read_text(), "new\n")

    def test_a_hunk_applies_where_its_context_matches_despite_drifted_line_numbers(self) -> None:
        self.tools.write_file("drift.txt", "".join(f"line{n}\n" for n in range(1, 21)))

        # The context is intact but the header points four lines too early,
        # exactly what happens after an earlier edit shifts the file.
        self.tools.apply_patch(
            "--- a/drift.txt\n+++ b/drift.txt\n"
            "@@ -5,3 +5,3 @@\n line9\n-line10\n+LINE10\n line11\n"
        )
        self.assertEqual(
            (self.project / "drift.txt").read_text().splitlines()[9], "LINE10"
        )

        # A header pointing too late searches backwards just as well.
        self.tools.apply_patch(
            "--- a/drift.txt\n+++ b/drift.txt\n"
            "@@ -17,3 +17,3 @@\n line2\n-line3\n+LINE3\n line4\n"
        )
        self.assertEqual(
            (self.project / "drift.txt").read_text().splitlines()[2], "LINE3"
        )

    def test_drifted_hunks_apply_in_order_and_prefer_the_nearest_match(self) -> None:
        self.tools.write_file(
            "repeat.txt",
            "head\nsame\ntail\nmiddle\nsame\nfoot\nlast\nsame\nend\n",
        )

        # Three identical 'same' lines: each hunk must land on the one nearest
        # its own header rather than on the first match in the file.
        self.tools.apply_patch(
            "--- a/repeat.txt\n+++ b/repeat.txt\n"
            "@@ -6,3 +6,3 @@\n middle\n-same\n+SECOND\n foot\n"
            "@@ -20,3 +20,3 @@\n last\n-same\n+THIRD\n end\n"
        )
        self.assertEqual(
            (self.project / "repeat.txt").read_text(),
            "head\nsame\ntail\nmiddle\nSECOND\nfoot\nlast\nTHIRD\nend\n",
        )

    def test_a_hunk_whose_context_is_absent_still_fails_without_writing(self) -> None:
        self.tools.write_file("drift.txt", "".join(f"line{n}\n" for n in range(1, 21)))
        absent = self.assertRaises(ValueError)
        with absent:
            self.tools.apply_patch(
                "--- a/drift.txt\n+++ b/drift.txt\n"
                "@@ -5,3 +5,3 @@\n line9\n-nonexistent\n+LINE10\n line11\n"
            )
        message = str(absent.exception)
        self.assertIn("drift.txt", message)
        self.assertIn("'nonexistent\\n'", message)
        self.assertEqual(
            (self.project / "drift.txt").read_text(),
            "".join(f"line{n}\n" for n in range(1, 21)),
        )

    def test_a_multi_file_patch_changes_nothing_when_any_file_fails(self) -> None:
        (self.project / "other.txt").write_text("one\ntwo\n")
        failure = self.assertRaises(ValueError)
        with failure:
            self.tools.apply_patch(unified_diff=(
                "--- a/part.txt\n+++ b/part.txt\n"
                "@@ -1,3 +1,3 @@\n alpha\n-beta\n+BETA\n gamma\n"
                "--- /dev/null\n+++ b/added/fresh.txt\n"
                "@@ -0,0 +1 @@\n+first\n"
                "--- a/other.txt\n+++ b/other.txt\n"
                "@@ -1,2 +1,2 @@\n-STALE\n+ONE\n two\n"
            ))

        message = str(failure.exception)
        self.assertIn("other.txt", message)
        self.assertIn("line 1", message)
        self.assertIn("'STALE\\n'", message)
        self.assertEqual((self.project / "part.txt").read_text(), "alpha\nbeta\ngamma\n")
        self.assertEqual((self.project / "other.txt").read_text(), "one\ntwo\n")
        self.assertFalse((self.project / "added").exists())

    def test_patch_targets_are_contained_and_agree_with_any_given_path(self) -> None:
        escape = self.assertRaises(ValueError)
        with escape:
            self.tools.apply_patch(unified_diff=(
                "--- a/part.txt\n+++ b/part.txt\n"
                "@@ -1,3 +1,3 @@\n alpha\n-beta\n+BETA\n gamma\n"
                "--- a/../outside.txt\n+++ b/../outside.txt\n"
                "@@ -1 +1 @@\n-out\n+OUT\n"
            ))
        self.assertIn("outside active project", str(escape.exception))
        self.assertEqual((self.project / "part.txt").read_text(), "alpha\nbeta\ngamma\n")

        disagreement = self.assertRaises(ValueError)
        with disagreement:
            self.tools.apply_patch(
                "--- a/other.txt\n+++ b/other.txt\n@@ -1 +1 @@\n-one\n+ONE\n",
                "part.txt",
            )
        self.assertIn("part.txt", str(disagreement.exception))
        self.assertIn("other.txt", str(disagreement.exception))

        several = self.assertRaises(ValueError)
        with several:
            self.tools.apply_patch(
                "--- a/part.txt\n+++ b/part.txt\n@@ -1 +1 @@\n-alpha\n+ALPHA\n"
                "--- a/other.txt\n+++ b/other.txt\n@@ -1 +1 @@\n-one\n+ONE\n",
                "part.txt",
            )
        self.assertIn("describes 2 files", str(several.exception))
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

    def test_solid_test_passes_the_kernel_through_as_the_framework_flag(self) -> None:
        self.assertTrue(self.tools.solid_test(kernel="faceted")["ok"])
        self.assertTrue(self.tools.solid_test("part.txt", failfast=True, kernel="exact")["ok"])
        self.assertTrue(self.tools.solid_test()["ok"])
        calls = [json.loads(line)["argv"] for line in self.capture.read_text().splitlines()]
        self.assertEqual(calls[0], ["test", "--faceted"])
        self.assertEqual(calls[1], ["test", "--failfast", "--exact", "part.txt"])
        self.assertEqual(calls[2], ["test"])
        with self.assertRaises(ValueError):
            self.tools.solid_test(kernel="fast")

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
            lambda: self.tools.apply_patch(
                "--- a/../outside.txt\n+++ b/../outside.txt\n@@ -1 +1 @@\n-outside\n+inside\n"
            ),
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

    def skill_registry(self) -> dict[str, Path]:
        """Register one skill outside the project, as the shop does at launch."""
        root = Path(self.temporary.name) / "shop-skills" / "solid-node"
        (root / "reference").mkdir(parents=True)
        (root / "SKILL.md").write_text("---\nname: solid-node\n---\n\nMACHINING INSTRUCTIONS\n")
        (root / "reference" / "gears.md").write_text("GEAR TABLE\n")
        return {"solid-node": root}

    def test_load_skill_returns_instructions_and_names_its_bundled_resources(self) -> None:
        registry = self.skill_registry()
        tools = ProjectTools(
            self.project,
            solid_command=(sys.executable, str(FAKE_SOLID)),
            skills=registry,
        )
        loaded = tools.load_skill("solid-node")
        self.assertIn("MACHINING INSTRUCTIONS", loaded)
        self.assertIn("reference/gears.md", loaded)
        self.assertNotIn("GEAR TABLE", loaded)
        self.assertEqual(tools.load_skill("solid-node", "reference/gears.md"), "GEAR TABLE\n")

    def test_load_skill_rejects_unregistered_names_and_escaping_resources(self) -> None:
        registry = self.skill_registry()
        outside = Path(self.temporary.name) / "shop-skills" / "secret.md"
        outside.write_text("SECRET\n")
        tools = ProjectTools(
            self.project,
            solid_command=(sys.executable, str(FAKE_SOLID)),
            skills=registry,
        )
        with self.assertRaisesRegex(ValueError, "solid-node"):
            tools.load_skill("solid-node-api")
        for escape in ("../secret.md", str(outside), "reference/../../secret.md"):
            with self.subTest(resource=escape):
                with self.assertRaisesRegex(ValueError, "outside"):
                    tools.load_skill("solid-node", escape)

    def test_a_session_without_registered_skills_cannot_load_one(self) -> None:
        with self.assertRaisesRegex(ValueError, "no skill"):
            self.tools.load_skill("solid-node")

    def test_a_registered_skill_directory_is_not_reachable_as_a_project_path(self) -> None:
        registry = self.skill_registry()
        tools = ProjectTools(
            self.project,
            solid_command=(sys.executable, str(FAKE_SOLID)),
            skills=registry,
        )
        for path in (str(registry["solid-node"] / "SKILL.md"), str(registry["solid-node"])):
            with self.subTest(path=path):
                with self.assertRaisesRegex(ValueError, "outside active project"):
                    tools.read_file(path)
                with self.assertRaisesRegex(ValueError, "outside active project"):
                    tools.list_dir(path)

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
                skills=self.skill_registry(),
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
        self.assertEqual(initialized["result"]["serverInfo"]["name"], "libresolid-studio-floor-tools")
        listed = rpc(2, "tools/list")
        self.assertEqual({tool["name"] for tool in listed["result"]["tools"]}, set(TOOL_NAMES))
        image = rpc(3, "tools/call", {"name": "read_file", "arguments": {"path": "image.png"}})
        self.assertEqual(image["result"]["content"][0]["type"], "image")
        escaped = rpc(4, "tools/call", {"name": "read_file", "arguments": {"path": "../outside.txt"}})
        self.assertTrue(escaped["result"]["isError"])
        skill = rpc(5, "tools/call", {"name": "load_skill", "arguments": {"name": "solid-node"}})
        self.assertFalse(skill["result"]["isError"])
        self.assertIn("MACHINING INSTRUCTIONS", skill["result"]["content"][0]["text"])

        process.stdin.close()
        self.assertEqual(process.wait(timeout=3), 0)

    def test_stdio_mcp_protocol_omits_skill_loading_without_a_registry(self) -> None:
        process = subprocess.Popen(
            mcp_command(self.project, (sys.executable, str(FAKE_SOLID))),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**os.environ, "PYTHONPATH": str(ROOT)},
        )
        self.addCleanup(lambda: process.kill() if process.poll() is None else None)
        assert process.stdin is not None
        assert process.stdout is not None
        process.stdin.write(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}) + "\n")
        process.stdin.flush()
        listed = json.loads(process.stdout.readline())
        self.assertEqual(
            {tool["name"] for tool in listed["result"]["tools"]},
            set(TOOL_NAMES) - {"load_skill"},
        )
        process.stdin.close()
        self.assertEqual(process.wait(timeout=3), 0)


if __name__ == "__main__":
    unittest.main()
