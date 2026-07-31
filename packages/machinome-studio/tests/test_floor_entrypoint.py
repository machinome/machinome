from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

from floor import __main__


class FloorEntrypointTest(unittest.TestCase):
    def test_project_name_is_required_and_arbitrary_project_paths_are_rejected(self) -> None:
        for arguments in (["floor"], ["floor", "--project", "/work/engine"]):
            with self.subTest(arguments=arguments), patch.object(sys, "argv", arguments), patch.object(__main__, "prepare_project") as prepare, self.assertRaises(SystemExit) as raised:
                __main__.main()
            self.assertEqual(raised.exception.code, 2)
            prepare.assert_not_called()

    def test_defaults_to_port_9000(self) -> None:
        prepared = _prepared()
        with patch.dict(os.environ, {}, clear=True), patch.object(sys, "argv", ["floor", "engine"]), patch.object(__main__, "prepare_project", return_value=prepared), patch.object(__main__, "create_app"), patch.object(__main__.uvicorn, "run") as run:
            __main__.main()
        self.assertEqual(run.call_args.kwargs["port"], 9000)

    def test_accepts_an_explicit_port(self) -> None:
        with patch.object(sys, "argv", ["floor", "engine", "--port", "9123"]), patch.object(__main__, "prepare_project", return_value=_prepared()), patch.object(__main__, "create_app"), patch.object(__main__.uvicorn, "run") as run:
            __main__.main()
        self.assertEqual(run.call_args.kwargs["port"], 9123)

    def test_requires_and_prepares_a_named_workspace_project(self) -> None:
        prepared = _prepared()
        with (
            patch.object(sys, "argv", ["floor", "v8-engine"]),
            patch.object(__main__, "prepare_project", return_value=prepared) as prepare,
            patch.object(__main__, "create_app") as create_app,
            patch.object(__main__.uvicorn, "run"),
        ):
            __main__.main()
        prepare.assert_called_once()
        self.assertEqual(prepare.call_args.args[0], "v8-engine")
        create_app.assert_called_once_with(
            prepared.project_root,
            artifact_root=prepared.artifact_root,
            solid_command=prepared.solid_command,
            build_environment=prepared.build_environment,
        )


def _prepared():
    return __import__("floor.preparation", fromlist=["PreparedProject"]).PreparedProject(
        name="engine", project_root=__main__.Path("/work/projects/engine"), model=__main__.Path("root"), artifact_root=__main__.Path("/work/projects/engine/_build")
    )
