# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Resolve the project folder and port every way of starting the hub shares.

Each entry point (``machinome-studio``, ``python -m floor.orchestrator`` and
``python -m floor``) parses its own options and then calls
:func:`resolve_launch`, which applies one precedence rule per setting:
the command-line option, then the environment, then the studio configuration
file, then a built-in default. The configuration file's location and every
value it may hold are read here, and nowhere else, so the three entry points
never disagree about where a launch's settings come from.

The function takes the environment as an explicit mapping and reads every
variable it consults — the configuration file's location, ``FLOOR_PORT``,
and the home directory used to expand a leading ``~`` — from that mapping
alone, never from the process environment directly, so a test can supply an
isolated one.
"""

from __future__ import annotations

import argparse
import tomllib
from collections.abc import Mapping
from pathlib import Path

MIN_PORT = 1
MAX_PORT = 65535
DEFAULT_PORT = 9000

CONFIG_ENV_VAR = "MACHINOME_STUDIO_CONFIG"
XDG_CONFIG_ENV_VAR = "XDG_CONFIG_HOME"
HOME_ENV_VAR = "HOME"
PORT_ENV_VAR = "FLOOR_PORT"

STUDIO_TABLE = "studio"
# A literal tuple, not built from the two constants below: the documentation
# test reads it straight from source with ast.literal_eval.
STUDIO_KEYS = ("projects", "port")
PROJECTS_KEY, PORT_KEY = STUDIO_KEYS


class LaunchError(ValueError):
    """A failed launch prerequisite: an unresolved setting or a bad file."""


def config_file_path(environ: Mapping[str, str]) -> Path | None:
    """Where the studio configuration file is looked for.

    Returns ``None`` when neither ``XDG_CONFIG_HOME`` nor ``HOME`` is an
    absolute path and ``MACHINOME_STUDIO_CONFIG`` is unset: there is then no
    default location, which is not itself an error.
    """
    named = environ.get(CONFIG_ENV_VAR, "")
    if named:
        return Path(named)
    xdg = environ.get(XDG_CONFIG_ENV_VAR, "")
    if xdg and Path(xdg).is_absolute():
        return Path(xdg) / "machinome-studio" / "config.toml"
    home = environ.get(HOME_ENV_VAR, "")
    if home and Path(home).is_absolute():
        return Path(home) / ".config" / "machinome-studio" / "config.toml"
    return None


def _named(environ: Mapping[str, str]) -> bool:
    return bool(environ.get(CONFIG_ENV_VAR, ""))


def _validate_file_port(value: object, path: Path) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not (MIN_PORT <= value <= MAX_PORT):
        raise LaunchError(f"{path}: studio.port must be an integer from 1 to 65535")
    return value


def _validate_projects(value: object, path: Path, environ: Mapping[str, str]) -> Path:
    if not isinstance(value, str):
        raise LaunchError(f"{path}: studio.projects must be a string")
    if value == "~" or value.startswith("~/"):
        home = environ.get(HOME_ENV_VAR, "")
        if not home or not Path(home).is_absolute():
            raise LaunchError(
                f"{path}: studio.projects starts with ~ but the home directory "
                "is unknown (HOME is not an absolute path)"
            )
        return Path(home) if value == "~" else Path(home) / value[2:]
    candidate = Path(value)
    if value.startswith("~") or not candidate.is_absolute():
        raise LaunchError(
            f"{path}: studio.projects must be an absolute path, ~, or a path "
            f"starting with ~/, got {value!r}"
        )
    return candidate


def read_config(environ: Mapping[str, str]) -> dict[str, object]:
    """Read and validate the studio configuration file.

    Returns ``{}`` when there is no file to read: no default location and no
    ``MACHINOME_STUDIO_CONFIG``, or a default-location file that does not
    exist. Every other failure — a named file that is missing or unreadable,
    or a present file that is malformed — raises :class:`LaunchError`. A
    present file is read and validated whether or not the command line will
    end up overriding every value it holds.
    """
    path = config_file_path(environ)
    if path is None:
        return {}
    named = _named(environ)
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        if named:
            raise LaunchError(f"{path}: no such file (named by {CONFIG_ENV_VAR})") from None
        return {}
    except OSError as error:
        raise LaunchError(f"{path}: cannot be read: {error.strerror}") from error
    try:
        parsed = tomllib.loads(raw.decode("utf-8"))
    except UnicodeDecodeError as error:
        raise LaunchError(f"{path}: not valid TOML: {error}") from error
    except tomllib.TOMLDecodeError as error:
        raise LaunchError(f"{path}: not valid TOML: {error}") from error
    unknown_top = sorted(set(parsed) - {STUDIO_TABLE})
    if unknown_top:
        raise LaunchError(
            f"{path}: unknown key {unknown_top[0]!r}; the file accepts [studio] "
            "with projects and port"
        )
    studio = parsed.get(STUDIO_TABLE, {})
    if not isinstance(studio, dict):
        raise LaunchError(f"{path}: studio must be a table")
    unknown = sorted(set(studio) - set(STUDIO_KEYS))
    if unknown:
        raise LaunchError(
            f"{path}: unknown key 'studio.{unknown[0]}'; [studio] accepts projects and port"
        )
    resolved: dict[str, object] = {}
    if PORT_KEY in studio:
        resolved[PORT_KEY] = _validate_file_port(studio[PORT_KEY], path)
    if PROJECTS_KEY in studio:
        resolved[PROJECTS_KEY] = _validate_projects(studio[PROJECTS_KEY], path, environ)
    return resolved


def _resolve_projects(
    arguments: argparse.Namespace,
    environ: Mapping[str, str],
    config: dict[str, object],
) -> Path:
    projects_dir = getattr(arguments, "projects_dir", None)
    if projects_dir is not None:
        return projects_dir
    if PROJECTS_KEY in config:
        return config[PROJECTS_KEY]  # type: ignore[return-value]
    path = config_file_path(environ)
    if path is not None:
        raise LaunchError(
            f"no project folder: pass --projects-dir or set projects under [studio] in {path}"
        )
    raise LaunchError(
        "no project folder: pass --projects-dir "
        "(no configuration file: neither XDG_CONFIG_HOME nor HOME is an absolute path)"
    )


def _resolve_port(
    arguments: argparse.Namespace,
    environ: Mapping[str, str],
    config: dict[str, object],
) -> int:
    option_port = getattr(arguments, "port", None)
    if option_port is not None:
        if not (MIN_PORT <= option_port <= MAX_PORT):
            raise LaunchError(f"--port must be an integer from 1 to 65535, got {option_port}")
        return option_port
    raw_env = environ.get(PORT_ENV_VAR, "")
    if raw_env:
        try:
            env_port = int(raw_env)
        except ValueError:
            env_port = None
        if env_port is None or not (MIN_PORT <= env_port <= MAX_PORT):
            raise LaunchError(f"FLOOR_PORT must be an integer from 1 to 65535, got {raw_env!r}")
        return env_port
    if PORT_KEY in config:
        return config[PORT_KEY]  # type: ignore[return-value]
    return DEFAULT_PORT


def resolve_launch(
    arguments: argparse.Namespace,
    environ: Mapping[str, str],
) -> tuple[Path, int]:
    """Resolve the project folder and port for one launch.

    Reads the studio configuration file exactly once and applies, for each
    setting, the first source that supplies it: the command-line option,
    then the environment (the port only), then the configuration file, then
    the built-in default. Raises :class:`LaunchError` naming the missing
    setting or the malformed file when a launch cannot be resolved.
    """
    config = read_config(environ)
    projects_dir = _resolve_projects(arguments, environ, config)
    port = _resolve_port(arguments, environ, config)
    return projects_dir, port
