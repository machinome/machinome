# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from floor import __main__, orchestrator


def _isolated_environment(*, xdg_config_home: str, path: str | None = None, **extra: str) -> dict[str, str]:
    """The minimal environment an in-process entry-point call may see.

    Never inherits the developer's own configuration file or FLOOR_PORT: PATH
    (the shop's one ambient prerequisite) is kept explicitly when supplied,
    and XDG_CONFIG_HOME is always a temporary, empty location.
    """
    environ = {"XDG_CONFIG_HOME": xdg_config_home}
    if path is not None:
        environ["PATH"] = path
    environ.update(extra)
    return environ


class FloorEntrypointTest(unittest.TestCase):
    def test_rejects_old_arguments(self) -> None:
        for arguments in (
            ["floor", "engine"],
            ["floor", "--profile", "builder"],
            ["floor", "--project-home", "/tmp/projects"],
            ["floor", "--cwd", "/tmp/shop"],
        ):
            with self.subTest(arguments=arguments), patch.object(sys, "argv", arguments), self.assertRaises(SystemExit) as raised:
                __main__.main()
            self.assertEqual(raised.exception.code, 2)

    def test_missing_projects_dir_with_no_file_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as xdg:
            stderr = io.StringIO()
            with (
                patch.dict(os.environ, _isolated_environment(xdg_config_home=xdg, path=os.environ.get("PATH", "")), clear=True),
                patch.object(sys, "argv", ["floor"]),
                contextlib.redirect_stderr(stderr),
                self.assertRaises(SystemExit) as raised,
            ):
                __main__.main()
            self.assertEqual(raised.exception.code, 1)
            self.assertIn("error: no project folder", stderr.getvalue())

    def test_the_isolated_environment_never_reads_the_developers_own_file(self) -> None:
        real_config = Path(os.path.expanduser("~/.config/machinome-studio/config.toml"))
        with tempfile.TemporaryDirectory() as xdg:
            stderr = io.StringIO()
            with (
                patch.dict(os.environ, _isolated_environment(xdg_config_home=xdg, path=os.environ.get("PATH", "")), clear=True),
                patch.object(sys, "argv", ["floor"]),
                contextlib.redirect_stderr(stderr),
                self.assertRaises(SystemExit),
            ):
                __main__.main()
            self.assertNotIn(str(real_config), stderr.getvalue())
            self.assertIn(xdg, stderr.getvalue())

    def test_defaults_to_port_9000_and_accepts_an_explicit_port(self) -> None:
        folder = "/work/projects"
        for arguments, expected in (
            (["floor", "--projects-dir", folder], 9000),
            (["floor", "--projects-dir", folder, "--port", "9123"], 9123),
        ):
            with tempfile.TemporaryDirectory() as xdg:
                with (
                    self.subTest(arguments=arguments),
                    # PATH stays: the shop resolves its one ambient prerequisite,
                    # the OpenSpec CLI, before it binds a listener.
                    patch.dict(os.environ, _isolated_environment(xdg_config_home=xdg, path=os.environ.get("PATH", "")), clear=True),
                    patch.object(sys, "argv", arguments),
                    patch.object(__main__, "default_machinome_command", return_value=("machinome",)),
                    patch.object(__main__, "SessionRegistry", return_value=object()),
                    patch.object(__main__, "create_app", return_value=object()),
                    patch.object(__main__.uvicorn, "run") as run,
                ):
                    __main__.main()
                self.assertEqual(run.call_args.kwargs["port"], expected)

    def test_passes_projects_dir_directly_to_the_empty_registry_and_app(self) -> None:
        folder = Path("/work/any-project-directory-name")
        with tempfile.TemporaryDirectory() as unrelated, tempfile.TemporaryDirectory() as xdg:
            previous = Path.cwd()
            os.chdir(unrelated)
            try:
                with (
                    patch.dict(os.environ, _isolated_environment(xdg_config_home=xdg, path=os.environ.get("PATH", "")), clear=True),
                    patch.object(sys, "argv", ["floor", "--projects-dir", str(folder), "--machinome-command", "fake-solid"]),
                    patch.object(__main__, "SessionRegistry", return_value=object()) as registry,
                    patch.object(__main__, "create_app", return_value=object()) as create_app,
                    patch.object(__main__.uvicorn, "run"),
                ):
                    __main__.main()
            finally:
                os.chdir(previous)
        self.assertEqual(registry.call_args.args, (folder,))
        self.assertEqual(
            registry.call_args.kwargs["shop_root"],
            Path(__main__.__file__).resolve().parents[1],
        )
        self.assertEqual(registry.call_args.kwargs["machinome_command"], "fake-solid")
        self.assertTrue(registry.call_args.kwargs["start_agents"] is False)
        self.assertEqual(create_app.call_args.args, (folder,))

    def test_port_zero_exits_one_before_any_server_starts(self) -> None:
        with tempfile.TemporaryDirectory() as xdg:
            stderr = io.StringIO()
            with (
                patch.dict(os.environ, _isolated_environment(xdg_config_home=xdg, path=os.environ.get("PATH", "")), clear=True),
                patch.object(sys, "argv", ["floor", "--projects-dir", "/work/projects", "--port", "0"]),
                patch.object(__main__, "SessionRegistry") as registry,
                patch.object(__main__, "create_app") as create_app,
                patch.object(__main__.uvicorn, "run") as run,
                contextlib.redirect_stderr(stderr),
                self.assertRaises(SystemExit) as raised,
            ):
                __main__.main()
            self.assertEqual(raised.exception.code, 1)
            self.assertIn("--port must be an integer from 1 to 65535, got 0", stderr.getvalue())
            registry.assert_not_called()
            create_app.assert_not_called()
            run.assert_not_called()

    def test_configuration_file_supplies_the_folder_and_port(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            config = Path(home) / ".config/machinome-studio/config.toml"
            config.parent.mkdir(parents=True)
            config.write_text('[studio]\nprojects = "/from/file"\nport = 9111\n', encoding="utf-8")
            with (
                patch.dict(os.environ, {"HOME": home, "PATH": os.environ.get("PATH", "")}, clear=True),
                patch.object(sys, "argv", ["floor"]),
                patch.object(__main__, "SessionRegistry", return_value=object()) as registry,
                patch.object(__main__, "create_app", return_value=object()) as create_app,
                patch.object(__main__.uvicorn, "run") as run,
            ):
                __main__.main()
            self.assertEqual(registry.call_args.args, (Path("/from/file"),))
            self.assertEqual(create_app.call_args.args, (Path("/from/file"),))
            self.assertEqual(run.call_args.kwargs["port"], 9111)

    def test_options_override_the_configuration_file(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            config = Path(home) / ".config/machinome-studio/config.toml"
            config.parent.mkdir(parents=True)
            config.write_text('[studio]\nprojects = "/from/file"\nport = 9111\n', encoding="utf-8")
            with (
                patch.dict(os.environ, {"HOME": home, "PATH": os.environ.get("PATH", "")}, clear=True),
                patch.object(sys, "argv", ["floor", "--projects-dir", "/from/option", "--port", "9222"]),
                patch.object(__main__, "SessionRegistry", return_value=object()) as registry,
                patch.object(__main__, "create_app", return_value=object()),
                patch.object(__main__.uvicorn, "run") as run,
            ):
                __main__.main()
            self.assertEqual(registry.call_args.args, (Path("/from/option"),))
            self.assertEqual(run.call_args.kwargs["port"], 9222)


class OrchestratorEntrypointTest(unittest.TestCase):
    """The same launch-resolution refusals, stopping before the server starts."""

    def test_missing_projects_dir_with_no_file_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as xdg:
            stderr = io.StringIO()
            with (
                patch.dict(os.environ, _isolated_environment(xdg_config_home=xdg, path=os.environ.get("PATH", "")), clear=True),
                patch.object(sys, "argv", ["machinome-studio"]),
                patch.object(orchestrator.uvicorn, "Server") as server,
                patch.object(orchestrator, "create_app") as create_app,
                contextlib.redirect_stderr(stderr),
                self.assertRaises(SystemExit) as raised,
            ):
                orchestrator.main()
            self.assertEqual(raised.exception.code, 1)
            self.assertIn("error: no project folder", stderr.getvalue())
            server.assert_not_called()
            create_app.assert_not_called()

    def test_port_zero_exits_one_before_any_server_starts(self) -> None:
        with tempfile.TemporaryDirectory() as xdg:
            stderr = io.StringIO()
            with (
                patch.dict(os.environ, _isolated_environment(xdg_config_home=xdg, path=os.environ.get("PATH", "")), clear=True),
                patch.object(sys, "argv", ["machinome-studio", "--projects-dir", "/work/projects", "--port", "0"]),
                patch.object(orchestrator.uvicorn, "Server") as server,
                patch.object(orchestrator, "create_app") as create_app,
                contextlib.redirect_stderr(stderr),
                self.assertRaises(SystemExit) as raised,
            ):
                orchestrator.main()
            self.assertEqual(raised.exception.code, 1)
            self.assertIn("--port must be an integer from 1 to 65535, got 0", stderr.getvalue())
            server.assert_not_called()
            create_app.assert_not_called()


if __name__ == "__main__":
    unittest.main()
