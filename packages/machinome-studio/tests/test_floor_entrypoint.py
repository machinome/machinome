from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from floor import __main__


class FloorEntrypointTest(unittest.TestCase):
    def test_starts_without_a_project_or_profile_and_rejects_old_arguments(self) -> None:
        with (
            patch.object(sys, "argv", ["floor"]),
            patch.object(__main__, "primary_shop_root", return_value=Path("/shop")),
            patch.object(__main__, "default_solid_command", return_value=("solid",)),
            patch.object(__main__, "SessionRegistry") as registry,
            patch.object(__main__, "create_app", return_value=object()),
            patch.object(__main__.uvicorn, "run"),
        ):
            __main__.main()
        self.assertEqual(registry.call_args.args, (Path.cwd() / "projects",))
        self.assertTrue(registry.call_args.kwargs["start_agents"] is False)

        for arguments in (["floor", "engine"], ["floor", "--profile", "builder"]):
            with self.subTest(arguments=arguments), patch.object(sys, "argv", arguments), self.assertRaises(SystemExit) as raised:
                __main__.main()
            self.assertEqual(raised.exception.code, 2)

    def test_defaults_to_port_9000_and_accepts_an_explicit_port(self) -> None:
        for arguments, expected in ((["floor"], 9000), (["floor", "--port", "9123"], 9123)):
            with (
                self.subTest(arguments=arguments),
                patch.dict(os.environ, {}, clear=True),
                patch.object(sys, "argv", arguments),
                patch.object(__main__, "primary_shop_root", return_value=Path("/shop")),
                patch.object(__main__, "default_solid_command", return_value=("solid",)),
                patch.object(__main__, "SessionRegistry", return_value=object()),
                patch.object(__main__, "create_app", return_value=object()),
                patch.object(__main__.uvicorn, "run") as run,
            ):
                __main__.main()
            self.assertEqual(run.call_args.kwargs["port"], expected)

    def test_passes_the_working_folder_to_the_empty_registry_and_app(self) -> None:
        folder = Path("/work/projects")
        with (
            patch.object(sys, "argv", ["floor", "--project-home", str(folder), "--solid-command", "fake-solid"]),
            patch.object(__main__, "primary_shop_root", return_value=Path("/primary-shop")),
            patch.object(__main__, "SessionRegistry", return_value=object()) as registry,
            patch.object(__main__, "create_app", return_value=object()) as create_app,
            patch.object(__main__.uvicorn, "run"),
        ):
            __main__.main()
        self.assertEqual(registry.call_args.args, (folder,))
        self.assertEqual(registry.call_args.kwargs["shop_root"], Path("/primary-shop"))
        self.assertEqual(registry.call_args.kwargs["solid_command"], "fake-solid")
        self.assertEqual(create_app.call_args.args, (folder,))


if __name__ == "__main__":
    unittest.main()
