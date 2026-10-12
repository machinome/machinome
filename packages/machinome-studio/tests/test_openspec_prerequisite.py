# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""The shop refuses to start without a runnable OpenSpec CLI."""

from __future__ import annotations

import contextlib
import io
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from floor import __main__, orchestrator
from floor.openspec import OpenSpecUnavailable, resolve_openspec_command


@contextlib.contextmanager
def _isolated_environment(*, path: str):
    """Never inherit the developer's own configuration file or FLOOR_PORT.

    Keeps only PATH, set explicitly by the caller, and a temporary, empty
    XDG_CONFIG_HOME so no default studio configuration file exists.
    """
    with tempfile.TemporaryDirectory() as home:
        environ = {"PATH": path, "XDG_CONFIG_HOME": str(Path(home) / "xdg")}
        with patch.dict(os.environ, environ, clear=True):
            yield


@contextlib.contextmanager
def _path_without_openspec():
    with tempfile.TemporaryDirectory() as empty:
        with _isolated_environment(path=empty):
            yield


@contextlib.contextmanager
def _path_with_broken_openspec():
    with tempfile.TemporaryDirectory() as folder:
        stub = Path(folder) / "openspec"
        stub.write_text("#!/bin/sh\necho 'boom' >&2\nexit 1\n", encoding="utf-8")
        stub.chmod(stub.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        with _isolated_environment(path=folder):
            yield


class OpenSpecResolutionTest(unittest.TestCase):
    def test_resolves_a_runnable_cli_from_the_ambient_environment(self) -> None:
        command = resolve_openspec_command()
        self.assertTrue(command)
        self.assertTrue(Path(command[0]).exists())

    def test_refuses_a_cli_that_cannot_be_found(self) -> None:
        with _path_without_openspec(), self.assertRaises(OpenSpecUnavailable) as raised:
            resolve_openspec_command()
        message = str(raised.exception)
        self.assertIn("openspec", message)
        self.assertIn("@fission-ai/openspec", message)

    def test_refuses_a_cli_that_is_present_but_does_not_run(self) -> None:
        with _path_with_broken_openspec(), self.assertRaises(OpenSpecUnavailable) as raised:
            resolve_openspec_command()
        self.assertIn("openspec", str(raised.exception))


class OpenSpecStartupPrerequisiteTest(unittest.TestCase):
    def test_the_orchestrator_refuses_to_start_without_the_cli(self) -> None:
        stderr = io.StringIO()
        with (
            _path_without_openspec(),
            patch.object(sys, "argv", ["floor", "--projects-dir", "/work/projects"]),
            patch.object(orchestrator.uvicorn, "Server") as server,
            patch.object(orchestrator, "create_app") as create_app,
            contextlib.redirect_stderr(stderr),
            self.assertRaises(SystemExit) as raised,
        ):
            orchestrator.main()
        self.assertEqual(raised.exception.code, 1)
        self.assertIn("openspec", stderr.getvalue())
        server.assert_not_called()
        create_app.assert_not_called()

    def test_the_hub_entrypoint_refuses_to_start_without_the_cli(self) -> None:
        stderr = io.StringIO()
        with (
            _path_without_openspec(),
            patch.object(sys, "argv", ["floor", "--projects-dir", "/work/projects"]),
            patch.object(__main__, "SessionRegistry") as registry,
            patch.object(__main__, "create_app") as create_app,
            patch.object(__main__.uvicorn, "run") as run,
            contextlib.redirect_stderr(stderr),
            self.assertRaises(SystemExit) as raised,
        ):
            __main__.main()
        self.assertEqual(raised.exception.code, 1)
        self.assertIn("openspec", stderr.getvalue())
        registry.assert_not_called()
        create_app.assert_not_called()
        run.assert_not_called()

    def test_the_hub_entrypoint_starts_when_the_cli_runs(self) -> None:
        with (
            # PATH stays real so the ambient OpenSpec CLI still resolves;
            # only XDG_CONFIG_HOME is isolated, so no developer configuration
            # file or FLOOR_PORT is read.
            _isolated_environment(path=os.environ.get("PATH", "")),
            patch.object(sys, "argv", ["floor", "--projects-dir", "/work/projects", "--machinome-command", "fake-solid"]),
            patch.object(__main__, "SessionRegistry", return_value=object()),
            patch.object(__main__, "create_app", return_value=object()),
            patch.object(__main__.uvicorn, "run") as run,
        ):
            __main__.main()
        self.assertEqual(run.call_args.kwargs["port"], 9000)


if __name__ == "__main__":
    unittest.main()
