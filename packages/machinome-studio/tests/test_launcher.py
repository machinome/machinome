# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""``resolve_launch`` resolves the project folder and port from an explicit
environment mapping and a studio configuration file, never the real one."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from floor.launcher import (
    DEFAULT_PORT,
    LaunchError,
    config_file_path,
    read_config,
    resolve_launch,
)


def arguments(*, projects_dir=None, port=None) -> SimpleNamespace:
    return SimpleNamespace(projects_dir=projects_dir, port=port)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class ConfigFileLocationTest(unittest.TestCase):
    def test_named_file_wins_over_everything(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            named = Path(home) / "elsewhere.toml"
            environ = {
                "MACHINOME_STUDIO_CONFIG": str(named),
                "XDG_CONFIG_HOME": str(Path(home) / "xdg"),
                "HOME": home,
            }
            self.assertEqual(config_file_path(environ), named)

    def test_absolute_xdg_config_home_is_used(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            xdg = str(Path(home) / "xdg")
            environ = {"XDG_CONFIG_HOME": xdg, "HOME": home}
            self.assertEqual(
                config_file_path(environ),
                Path(xdg) / "machinome-studio" / "config.toml",
            )

    def test_relative_xdg_config_home_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            environ = {"XDG_CONFIG_HOME": "relative/xdg", "HOME": home}
            self.assertEqual(
                config_file_path(environ),
                Path(home) / ".config" / "machinome-studio" / "config.toml",
            )

    def test_home_is_used_when_xdg_is_absent(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            environ = {"HOME": home}
            self.assertEqual(
                config_file_path(environ),
                Path(home) / ".config" / "machinome-studio" / "config.toml",
            )

    def test_no_default_location_when_neither_is_absolute(self) -> None:
        environ = {"XDG_CONFIG_HOME": "relative", "HOME": "relative"}
        self.assertIsNone(config_file_path(environ))
        self.assertIsNone(config_file_path({}))

    def test_missing_default_file_is_not_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            environ = {"HOME": home}
            self.assertEqual(read_config(environ), {})

    def test_missing_named_file_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            named = Path(home) / "missing.toml"
            environ = {"MACHINOME_STUDIO_CONFIG": str(named)}
            with self.assertRaises(LaunchError) as raised:
                read_config(environ)
            self.assertEqual(
                str(raised.exception),
                f"{named}: no such file (named by MACHINOME_STUDIO_CONFIG)",
            )


class PrecedenceTest(unittest.TestCase):
    def test_option_wins_over_everything(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            config = Path(home) / ".config/machinome-studio/config.toml"
            write(config, '[studio]\nprojects = "/from/file"\nport = 9100\n')
            environ = {"HOME": home, "FLOOR_PORT": "9300"}
            projects_dir, port = resolve_launch(
                arguments(projects_dir=Path("/from/option"), port=9200), environ
            )
            self.assertEqual(projects_dir, Path("/from/option"))
            self.assertEqual(port, 9200)

    def test_environment_wins_over_file_for_port(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            config = Path(home) / ".config/machinome-studio/config.toml"
            write(config, '[studio]\nprojects = "/from/file"\nport = 9100\n')
            environ = {"HOME": home, "FLOOR_PORT": "9300"}
            _, port = resolve_launch(arguments(), environ)
            self.assertEqual(port, 9300)

    def test_file_wins_over_default(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            config = Path(home) / ".config/machinome-studio/config.toml"
            write(config, '[studio]\nprojects = "/from/file"\nport = 9100\n')
            environ = {"HOME": home}
            projects_dir, port = resolve_launch(arguments(), environ)
            self.assertEqual(projects_dir, Path("/from/file"))
            self.assertEqual(port, 9100)

    def test_default_port_is_9000(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            environ = {"HOME": home}
            _, port = resolve_launch(arguments(projects_dir=Path("/work")), environ)
            self.assertEqual(port, DEFAULT_PORT)

    def test_no_configuration_file_behaves_as_before(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            environ = {"HOME": home}
            projects_dir, port = resolve_launch(
                arguments(projects_dir=Path("/work/projects")), environ
            )
            self.assertEqual(projects_dir, Path("/work/projects"))
            self.assertEqual(port, DEFAULT_PORT)


class HomeExpansionTest(unittest.TestCase):
    def test_tilde_alone_expands_to_home(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            config = Path(home) / ".config/machinome-studio/config.toml"
            write(config, '[studio]\nprojects = "~"\n')
            environ = {"HOME": home}
            projects_dir, _ = resolve_launch(arguments(), environ)
            self.assertEqual(projects_dir, Path(home))

    def test_tilde_slash_expands_against_the_mapping_home(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            config = Path(home) / ".config/machinome-studio/config.toml"
            write(config, '[studio]\nprojects = "~/machines"\n')
            environ = {"HOME": home}
            projects_dir, _ = resolve_launch(arguments(), environ)
            self.assertEqual(projects_dir, Path(home) / "machines")

    def test_the_real_home_is_never_read(self) -> None:
        # A fabricated HOME that does not exist on disk must still work:
        # expansion is pure string substitution against the mapping, never
        # Path.expanduser(), which would consult the process's real home.
        fabricated_home = "/nonexistent/fabricated/home"
        with tempfile.TemporaryDirectory() as elsewhere:
            config = Path(elsewhere) / "config.toml"
            write(config, '[studio]\nprojects = "~/machines"\n')
            environ = {"MACHINOME_STUDIO_CONFIG": str(config), "HOME": fabricated_home}
            projects_dir, _ = resolve_launch(arguments(), environ)
            self.assertEqual(projects_dir, Path(fabricated_home) / "machines")

    def test_other_tilde_forms_are_refused_as_relative(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            config = Path(home) / ".config/machinome-studio/config.toml"
            write(config, '[studio]\nprojects = "~name/machines"\n')
            environ = {"HOME": home}
            with self.assertRaises(LaunchError) as raised:
                resolve_launch(arguments(), environ)
            self.assertEqual(
                str(raised.exception),
                f"{config}: studio.projects must be an absolute path, ~, or a "
                "path starting with ~/, got '~name/machines'",
            )

    def test_tilde_with_unset_home_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as elsewhere:
            config = Path(elsewhere) / "config.toml"
            write(config, '[studio]\nprojects = "~/machines"\n')
            environ = {"MACHINOME_STUDIO_CONFIG": str(config)}
            with self.assertRaises(LaunchError) as raised:
                resolve_launch(arguments(), environ)
            self.assertEqual(
                str(raised.exception),
                f"{config}: studio.projects starts with ~ but the home "
                "directory is unknown (HOME is not an absolute path)",
            )

    def test_tilde_with_relative_home_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as elsewhere:
            config = Path(elsewhere) / "config.toml"
            write(config, '[studio]\nprojects = "~/machines"\n')
            environ = {"MACHINOME_STUDIO_CONFIG": str(config), "HOME": "relative/home"}
            with self.assertRaises(LaunchError):
                resolve_launch(arguments(), environ)


class PortRangeTest(unittest.TestCase):
    def test_option_port_zero_is_refused(self) -> None:
        with self.assertRaises(LaunchError) as raised:
            resolve_launch(arguments(projects_dir=Path("/work"), port=0), {})
        self.assertEqual(
            str(raised.exception), "--port must be an integer from 1 to 65535, got 0"
        )

    def test_option_port_too_large_is_refused(self) -> None:
        with self.assertRaises(LaunchError) as raised:
            resolve_launch(arguments(projects_dir=Path("/work"), port=70000), {})
        self.assertEqual(
            str(raised.exception),
            "--port must be an integer from 1 to 65535, got 70000",
        )

    def test_floor_port_out_of_range_is_refused(self) -> None:
        environ = {"FLOOR_PORT": "70000"}
        with self.assertRaises(LaunchError) as raised:
            resolve_launch(arguments(projects_dir=Path("/work")), environ)
        self.assertEqual(
            str(raised.exception),
            "FLOOR_PORT must be an integer from 1 to 65535, got '70000'",
        )

    def test_floor_port_non_numeric_is_refused(self) -> None:
        environ = {"FLOOR_PORT": "not-a-number"}
        with self.assertRaises(LaunchError) as raised:
            resolve_launch(arguments(projects_dir=Path("/work")), environ)
        self.assertEqual(
            str(raised.exception),
            "FLOOR_PORT must be an integer from 1 to 65535, got 'not-a-number'",
        )

    def test_file_port_out_of_range_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            config = Path(home) / ".config/machinome-studio/config.toml"
            write(config, '[studio]\nprojects = "/work"\nport = 70000\n')
            environ = {"HOME": home}
            with self.assertRaises(LaunchError) as raised:
                resolve_launch(arguments(), environ)
            self.assertEqual(
                str(raised.exception),
                f"{config}: studio.port must be an integer from 1 to 65535",
            )

    def test_boolean_file_port_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            config = Path(home) / ".config/machinome-studio/config.toml"
            write(config, '[studio]\nprojects = "/work"\nport = true\n')
            environ = {"HOME": home}
            with self.assertRaises(LaunchError) as raised:
                resolve_launch(arguments(), environ)
            self.assertEqual(
                str(raised.exception),
                f"{config}: studio.port must be an integer from 1 to 65535",
            )


class MissingProjectFolderTest(unittest.TestCase):
    def test_no_folder_with_a_default_file_location_names_it(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            environ = {"HOME": home}
            expected = Path(home) / ".config/machinome-studio/config.toml"
            with self.assertRaises(LaunchError) as raised:
                resolve_launch(arguments(), environ)
            self.assertEqual(
                str(raised.exception),
                "no project folder: pass --projects-dir or set projects under "
                f"[studio] in {expected}",
            )

    def test_no_folder_and_no_default_location(self) -> None:
        environ: dict[str, str] = {}
        with self.assertRaises(LaunchError) as raised:
            resolve_launch(arguments(), environ)
        self.assertEqual(
            str(raised.exception),
            "no project folder: pass --projects-dir (no configuration file: "
            "neither XDG_CONFIG_HOME nor HOME is an absolute path)",
        )


class MalformedFileTest(unittest.TestCase):
    def test_not_valid_toml(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            config = Path(home) / ".config/machinome-studio/config.toml"
            write(config, "this is not [ toml\n")
            environ = {"HOME": home}
            with self.assertRaises(LaunchError) as raised:
                resolve_launch(arguments(), environ)
            self.assertTrue(str(raised.exception).startswith(f"{config}: not valid TOML: "))

    def test_unknown_top_level_key(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            config = Path(home) / ".config/machinome-studio/config.toml"
            write(config, 'host = "0.0.0.0"\n')
            environ = {"HOME": home}
            with self.assertRaises(LaunchError) as raised:
                resolve_launch(arguments(), environ)
            self.assertEqual(
                str(raised.exception),
                f"{config}: unknown key 'host'; the file accepts [studio] with projects and port",
            )

    def test_studio_not_a_table(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            config = Path(home) / ".config/machinome-studio/config.toml"
            write(config, 'studio = "nope"\n')
            environ = {"HOME": home}
            with self.assertRaises(LaunchError) as raised:
                resolve_launch(arguments(), environ)
            self.assertEqual(str(raised.exception), f"{config}: studio must be a table")

    def test_unknown_key_inside_studio(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            config = Path(home) / ".config/machinome-studio/config.toml"
            write(config, "[studio]\nhost = \"0.0.0.0\"\n")
            environ = {"HOME": home}
            with self.assertRaises(LaunchError) as raised:
                resolve_launch(arguments(), environ)
            self.assertEqual(
                str(raised.exception),
                f"{config}: unknown key 'studio.host'; [studio] accepts projects and port",
            )

    def test_projects_not_a_string(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            config = Path(home) / ".config/machinome-studio/config.toml"
            write(config, "[studio]\nprojects = 9\n")
            environ = {"HOME": home}
            with self.assertRaises(LaunchError) as raised:
                resolve_launch(arguments(), environ)
            self.assertEqual(
                str(raised.exception), f"{config}: studio.projects must be a string"
            )

    def test_projects_relative_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            config = Path(home) / ".config/machinome-studio/config.toml"
            write(config, '[studio]\nprojects = "relative/machines"\n')
            environ = {"HOME": home}
            with self.assertRaises(LaunchError) as raised:
                resolve_launch(arguments(), environ)
            self.assertEqual(
                str(raised.exception),
                f"{config}: studio.projects must be an absolute path, ~, or a "
                "path starting with ~/, got 'relative/machines'",
            )

    def test_malformed_file_is_reported_even_when_options_override_everything(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            config = Path(home) / ".config/machinome-studio/config.toml"
            write(config, 'studio = "nope"\n')
            environ = {"HOME": home}
            with self.assertRaises(LaunchError) as raised:
                resolve_launch(
                    arguments(projects_dir=Path("/from/option"), port=9200), environ
                )
            self.assertEqual(str(raised.exception), f"{config}: studio must be a table")

    def test_unreadable_file(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            config = Path(home) / ".config/machinome-studio/config.toml"
            write(config, '[studio]\nprojects = "/work"\n')
            config.chmod(0o000)
            try:
                environ = {"HOME": home}
                with self.assertRaises(LaunchError) as raised:
                    resolve_launch(arguments(), environ)
                self.assertTrue(str(raised.exception).startswith(f"{config}: cannot be read: "))
            finally:
                config.chmod(0o600)


if __name__ == "__main__":
    unittest.main()
