from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from floor import __main__


ROOT = Path(__file__).resolve().parents[1]


class FloorEntrypointTest(unittest.TestCase):
    def test_project_name_is_required_and_arbitrary_project_paths_are_rejected(self) -> None:
        for arguments in (["floor"], ["floor", "--project", "/work/engine"]):
            with self.subTest(arguments=arguments), patch.object(sys, "argv", arguments), patch.object(__main__, "prepare_project") as prepare, self.assertRaises(SystemExit) as raised:
                __main__.main()
            self.assertEqual(raised.exception.code, 2)
            prepare.assert_not_called()

    def test_defaults_to_port_9000(self) -> None:
        prepared = _prepared()
        with patch.dict(os.environ, {}, clear=True), patch.object(sys, "argv", ["floor", "engine"]), patch.object(__main__, "primary_shop_root", return_value=ROOT), patch.object(__main__, "prepare_project", return_value=prepared), patch.object(__main__, "create_app"), patch.object(__main__.uvicorn, "run") as run:
            __main__.main()
        self.assertEqual(run.call_args.kwargs["port"], 9000)

    def test_accepts_an_explicit_port(self) -> None:
        with patch.object(sys, "argv", ["floor", "engine", "--port", "9123"]), patch.object(__main__, "primary_shop_root", return_value=ROOT), patch.object(__main__, "prepare_project", return_value=_prepared()), patch.object(__main__, "create_app"), patch.object(__main__.uvicorn, "run") as run:
            __main__.main()
        self.assertEqual(run.call_args.kwargs["port"], 9123)

    def test_requires_and_prepares_a_named_workspace_project(self) -> None:
        prepared = _prepared()
        with (
            patch.object(sys, "argv", ["floor", "v8-engine"]),
            patch.object(__main__, "primary_shop_root", return_value=ROOT),
            patch.object(__main__, "prepare_project", return_value=prepared) as prepare,
            patch.object(__main__, "create_app") as create_app,
            patch.object(__main__.uvicorn, "run"),
        ):
            __main__.main()
        prepare.assert_called_once()
        self.assertEqual(prepare.call_args.args[0], "v8-engine")
        create_app.assert_called_once()
        self.assertEqual(create_app.call_args.args, (prepared.project_root,))
        self.assertEqual(create_app.call_args.kwargs["profile"].id, "builder")

    def test_profile_is_validated_before_project_preparation(self) -> None:
        from floor.profiles import ProfileError
        with (
            patch.object(sys, "argv", ["floor", "engine", "--profile", "broken"]),
            patch.object(__main__, "load_profile", side_effect=ProfileError("profile broken: invalid")),
            patch.object(__main__, "prepare_project") as prepare,
            self.assertRaises(SystemExit) as raised,
        ):
            __main__.main()
        self.assertEqual(raised.exception.code, 1)
        prepare.assert_not_called()

    def test_profile_load_uses_the_primary_shop_root_from_a_checkout_path(self) -> None:
        primary = Path("/primary-shop")
        prepared = _prepared()
        with (
            patch.object(sys, "argv", ["floor", "engine"]),
            patch.object(__main__, "primary_shop_root", return_value=primary),
            patch.object(__main__, "load_profile", return_value=object()) as load_profile,
            patch.object(__main__, "prepare_project", return_value=prepared) as prepare,
            patch.object(__main__, "create_app"),
            patch.object(__main__.uvicorn, "run"),
        ):
            __main__.main()
        self.assertEqual(load_profile.call_args.kwargs["shop_root"], primary)
        self.assertEqual(prepare.call_args.kwargs["shop_root"], primary)


def _prepared():
    return __import__("floor.preparation", fromlist=["PreparedProject"]).PreparedProject(
        name="engine", project_root=__main__.Path("/work/projects/engine"), model=__main__.Path("root"), artifact_root=__main__.Path("/work/projects/engine/_build")
    )
