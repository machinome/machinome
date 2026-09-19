# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from floor.app import Broker
from floor.profiles import load_profile
from floor.sessions import Session
from floor.source_files import (
    SourceConflict,
    SourceUnavailable,
    SourceWorkspace,
)


class SourceWorkspaceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name) / "project"
        (self.project / "root").mkdir(parents=True)
        (self.project / "root" / "__init__.py").write_text("# model\n")
        (self.project / "docs").mkdir()
        (self.project / "docs" / "tracked.md").write_text("tracked\n")
        (self.project / ".gitignore").write_text("_build/\nignored/\n*.secret\n")
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.project)], check=True)
        subprocess.run(["git", "-C", str(self.project), "add", "--all"], check=True)
        subprocess.run(
            [
                "git", "-C", str(self.project), "-c", "user.name=Source Test",
                "-c", "user.email=source@example.invalid", "commit", "-q",
                "-m", "fixture",
            ],
            check=True,
        )
        self.workspace = SourceWorkspace(self.project, max_bytes=32)

    def test_lists_tracked_and_untracked_nonignored_files_and_synthesizes_directories(self) -> None:
        (self.project / "new").mkdir()
        (self.project / "new" / "agent.py").write_text("agent = True\n")
        (self.project / "ignored").mkdir()
        (self.project / "ignored" / "hidden.py").write_text("hidden = True\n")
        (self.project / "token.secret").write_text("secret\n")
        (self.project / "_build").mkdir()
        (self.project / "_build" / "viewer.json").write_text("{}")

        entries = {(entry.path, entry.kind) for entry in self.workspace.entries()}

        self.assertIn(("root", "directory"), entries)
        self.assertIn(("root/__init__.py", "file"), entries)
        self.assertIn(("new", "directory"), entries)
        self.assertIn(("new/agent.py", "file"), entries)
        self.assertNotIn(("ignored", "directory"), entries)
        self.assertFalse(any(path.startswith((".git/", "_build/")) for path, _ in entries))
        self.assertNotIn(("token.secret", "file"), entries)

    def test_reads_bounded_utf8_with_a_stable_revision(self) -> None:
        first = self.workspace.read("root/__init__.py")
        second = self.workspace.read("root/__init__.py")

        self.assertEqual(first.content, "# model\n")
        self.assertEqual(first.revision, second.revision)
        self.assertEqual(len(first.revision), 64)

    def test_reads_only_bounded_visible_png_files(self) -> None:
        image = b"\x89PNG\r\n\x1a\npreview"
        (self.project / "preview.png").write_bytes(image)

        self.assertEqual(self.workspace.read_png("preview.png"), image)

        (self.project / "malformed.png").write_bytes(b"not a png")
        (self.project / "large.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"x" * 33)
        (self.project / "alias.png").symlink_to(self.project / "preview.png")
        for path in ("malformed.png", "large.png", "alias.png", "../preview.png"):
            with self.subTest(path=path), self.assertRaises(SourceUnavailable):
                self.workspace.read_png(path)

    def test_rejects_binary_oversized_symlink_ignored_and_escaping_paths(self) -> None:
        (self.project / "binary.dat").write_bytes(b"\x00binary")
        (self.project / "large.txt").write_text("x" * 33)
        (self.project / "ignored").mkdir()
        (self.project / "ignored" / "hidden.py").write_text("hidden\n")
        (self.project / "link.py").symlink_to(self.project / "root" / "__init__.py")

        for path in (
            "binary.dat",
            "large.txt",
            "ignored/hidden.py",
            "link.py",
            "../outside.py",
            "/tmp/outside.py",
        ):
            with self.subTest(path=path), self.assertRaises(SourceUnavailable):
                self.workspace.read(path)

    def test_two_workspaces_never_cross_project_roots(self) -> None:
        other = Path(self.temporary.name) / "other"
        other.mkdir()
        (other / "only.py").write_text("other = True\n")
        subprocess.run(["git", "init", "-q", "-b", "main", str(other)], check=True)
        subprocess.run(["git", "-C", str(other), "add", "only.py"], check=True)
        other_workspace = SourceWorkspace(other)

        self.assertEqual(other_workspace.read("only.py").content, "other = True\n")
        with self.assertRaises(SourceUnavailable):
            self.workspace.read("only.py")

    def test_save_is_revision_checked_atomic_and_preserves_mode(self) -> None:
        source = self.project / "root" / "__init__.py"
        source.chmod(0o744)
        opened = self.workspace.read("root/__init__.py")

        saved = self.workspace.save("root/__init__.py", "# changed\n", opened.revision)

        self.assertEqual(source.read_text(), "# changed\n")
        self.assertEqual(saved.content, "# changed\n")
        self.assertEqual(stat.S_IMODE(source.stat().st_mode), 0o744)
        self.assertFalse(any(item.name.startswith(".machinome-studio-save-") for item in source.parent.iterdir()))

        with self.assertRaises(SourceConflict):
            self.workspace.save("root/__init__.py", "# stale\n", opened.revision)
        self.assertEqual(source.read_text(), "# changed\n")

    def test_save_never_creates_or_recreates_a_target(self) -> None:
        with self.assertRaises(SourceUnavailable):
            self.workspace.save("new.py", "new = True\n", "0" * 64)
        self.assertFalse((self.project / "new.py").exists())

        opened = self.workspace.read("root/__init__.py")
        os.unlink(self.project / "root" / "__init__.py")
        with self.assertRaises(SourceUnavailable):
            self.workspace.save("root/__init__.py", "recreated = True\n", opened.revision)
        self.assertFalse((self.project / "root" / "__init__.py").exists())


class SessionSourceSaveTest(unittest.IsolatedAsyncioTestCase):
    async def test_accepted_save_queues_and_attempts_delivery_for_active_roles(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        project = Path(temporary.name) / "project"
        project.mkdir()
        source = project / "model.py"
        source.write_text("before = True\n")
        subprocess.run(["git", "init", "-q", "-b", "main", str(project)], check=True)
        subprocess.run(["git", "-C", str(project), "add", "model.py"], check=True)
        root = Path(__file__).resolve().parents[1]
        profile = load_profile("builder", shop_root=root)
        broker = Broker(profile=profile, session_id="source-session")
        broker.manifest("builder", "Builder")
        broker.register_direct_delivery("builder", "turn-1")
        broker.turn_started("builder", "turn-1")

        class RecordingOrchestrator:
            def __init__(self) -> None:
                self.roles: list[str] = []

            async def deliver_pending_notices(self, role: str) -> None:
                self.roles.append(role)

        orchestrator = RecordingOrchestrator()
        session = Session(
            "source-session",
            "project",
            SimpleNamespace(
                project_root=project,
                artifact_root=project / "_build",
                build_environment=None,
                machinome_command=("machinome",),
                build_error=None,
            ),
            profile,
            broker,
            orchestrator=orchestrator,  # type: ignore[arg-type]
        )
        opened = session.source_workspace.read("model.py")

        saved = await session.save_source("model.py", "after = True\n", opened.revision)

        pending = broker.pending_system_notices("builder")
        self.assertEqual(orchestrator.roles, ["builder"])
        self.assertEqual((pending[0].path, pending[0].revision), ("model.py", saved.revision))


if __name__ == "__main__":
    unittest.main()
