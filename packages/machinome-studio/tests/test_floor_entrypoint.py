# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from floor import __main__


class FloorEntrypointTest(unittest.TestCase):
    def test_requires_projects_dir_and_rejects_old_arguments(self) -> None:
        for arguments in (
            ["floor"],
            ["floor", "engine"],
            ["floor", "--profile", "builder"],
            ["floor", "--project-home", "/tmp/projects"],
            ["floor", "--cwd", "/tmp/shop"],
        ):
            with self.subTest(arguments=arguments), patch.object(sys, "argv", arguments), self.assertRaises(SystemExit) as raised:
                __main__.main()
            self.assertEqual(raised.exception.code, 2)

    def test_defaults_to_port_9000_and_accepts_an_explicit_port(self) -> None:
        folder = "/work/projects"
        for arguments, expected in (
            (["floor", "--projects-dir", folder], 9000),
            (["floor", "--projects-dir", folder, "--port", "9123"], 9123),
        ):
            with (
                self.subTest(arguments=arguments),
                # PATH stays: the shop resolves its one ambient prerequisite,
                # the OpenSpec CLI, before it binds a listener.
                patch.dict(os.environ, {"PATH": os.environ.get("PATH", "")}, clear=True),
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
        with tempfile.TemporaryDirectory() as unrelated:
            previous = Path.cwd()
            os.chdir(unrelated)
            try:
                with (
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


if __name__ == "__main__":
    unittest.main()
