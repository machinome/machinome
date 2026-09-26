# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Dedicated Studio credentials never borrow the ordinary Codex login."""
import os
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from floor.codex_auth import AuthLease, CodexAuthError, studio_home, validate_home, cleanup_journal_temporaries, codex_binary


class CodexAuthTests(unittest.TestCase):
    def test_pinned_authenticated_bookkeeping_is_not_configuration(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            home.chmod(0o700)
            marker = home / ".sandbox_migration"
            marker.write_bytes(b"v1\n")
            marker.chmod(0o600)
            locks = home / "thread-writer-locks"
            locks.mkdir()
            (locks / ".coordination.lock").touch()
            (locks / "0199341b-1234-7123-8123-123456789abc.lock").touch()
            for suffix in ("", "-wal", "-shm"):
                (home / ("thread_history_1.sqlite" + suffix)).touch()
            validate_home(home)
            for path, data in ((locks / "AGENTS.md", b"instructions"),
                               (locks / ".coordination.lock", b"nonempty"),
                               (marker, b"v2\n")):
                original = path.read_bytes() if path.exists() else None
                path.write_bytes(data)
                with self.assertRaises(CodexAuthError):
                    validate_home(home)
                if original is None:
                    path.unlink()
                else:
                    path.write_bytes(original)
            database = home / "thread_history_1.sqlite"
            database.unlink()
            database.mkdir()
            with self.assertRaises(CodexAuthError):
                validate_home(home)
            database.rmdir()
            database.symlink_to(marker)
            with self.assertRaises(CodexAuthError):
                validate_home(home)
    def test_unsupported_native_version_is_refused_under_private_metadata_environment(self):
        with patch("floor.codex_auth.shutil.which", return_value="/synthetic/codex"), \
             patch("floor.codex_auth.subprocess.run", return_value=SimpleNamespace(stdout="codex-cli 0.157.2")) as run:
            with self.assertRaisesRegex(CodexAuthError, "Unsupported Codex version"):
                codex_binary()
            self.assertNotEqual(run.call_args.kwargs["env"]["HOME"], os.environ.get("HOME"))
            self.assertNotIn("OPENAI_API_KEY", run.call_args.kwargs["env"])
    def test_interrupted_owned_journal_write_recovers_without_accepting_symlinks(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary) / "codex"
            lease = AuthLease(home)
            lease.acquire()
            try:
                leftover = home / ".studio-threads-abc12345"
                leftover.write_text("[partial")
                leftover.chmod(0o600)
                cleanup_journal_temporaries(home)
                self.assertFalse(leftover.exists())
                validate_home(home)
                leftover.symlink_to(home / "auth.json")
                with self.assertRaises(CodexAuthError):
                    cleanup_journal_temporaries(home)
                self.assertTrue(leftover.is_symlink())
            finally:
                lease.release()
    def test_stable_state_path_ignores_codex_home(self):
        self.assertEqual(studio_home({"HOME": "/operator", "CODEX_HOME": "/secret", "XDG_STATE_HOME": "/state"}), Path("/state/machinome-studio/codex"))
        self.assertEqual(studio_home({"HOME": "/operator", "XDG_STATE_HOME": "relative"}), Path("/operator/.local/state/machinome-studio/codex"))

    def test_second_owner_and_login_cannot_take_lease(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary) / "codex"
            first = AuthLease(home)
            first.acquire()
            try:
                with self.assertRaisesRegex(CodexAuthError, "Stop.*hub"):
                    AuthLease(home).acquire()
                self.assertEqual(home.stat().st_mode & 0o777, 0o700)
            finally:
                first.release()
            second = AuthLease(home)
            second.acquire()
            second.release()

    def test_unexpected_configuration_and_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary) / "codex"
            home.mkdir(mode=0o700)
            (home / "config.toml").write_text('[mcp_servers.untrusted]\ncommand="bad"\n')
            with self.assertRaisesRegex(CodexAuthError, "config"):
                validate_home(home)
            (home / "config.toml").unlink()
            (home / "auth.json").symlink_to(Path(temporary) / "operator-auth")
            with self.assertRaisesRegex(CodexAuthError, "symlink"):
                validate_home(home)

    def test_no_login_has_actionable_remedy_without_reading_operator_home(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary) / "codex"
            home.mkdir(mode=0o700)
            with self.assertRaisesRegex(CodexAuthError, "floor.codex_auth login"):
                validate_home(home, require_auth=True)

    def test_auth_validation_redacts_malformed_secret(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary) / "codex"
            home.mkdir(mode=0o700)
            auth = home / "auth.json"
            auth.write_text('{"auth_mode":"api_key","OPENAI_API_KEY":"SECRET"}')
            auth.chmod(0o600)
            with self.assertRaises(CodexAuthError) as caught:
                validate_home(home, require_auth=True)
            self.assertNotIn("SECRET", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
