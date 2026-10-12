# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""One separately provisioned native Codex login, leased by Studio.

This module never discovers, imports or copies normal Codex credentials.
Only Codex itself writes OAuth credentials and refreshes this native store.
"""
from __future__ import annotations

import argparse
import asyncio
import fcntl
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import uuid
from collections.abc import Mapping


LOGIN_COMMAND = "python -m floor.codex_auth login"
PINNED_VERSION = "codex-cli 0.157.1"


class CodexAuthError(RuntimeError):
    """A credential-free diagnostic safe for browser display."""


def studio_home(environment: Mapping[str, str] | None = None) -> Path:
    environment = os.environ if environment is None else environment
    state = environment.get("XDG_STATE_HOME", "")
    if not state or not Path(state).is_absolute():
        operator_home = environment.get("HOME", "")
        if not operator_home or not Path(operator_home).is_absolute():
            raise CodexAuthError("Studio requires an absolute HOME or XDG_STATE_HOME")
        state = str(Path(operator_home) / ".local/state")
    return Path(state) / "machinome-studio/codex"


def private_directory(path: Path) -> None:
    if path.is_symlink():
        raise CodexAuthError("Studio Codex storage must not be a symlink")
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    info = path.stat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
        raise CodexAuthError("Studio Codex storage must be an operator-owned directory")
    if stat.S_IMODE(info.st_mode) != 0o700:
        raise CodexAuthError("Studio Codex storage must have mode 0700")


class AuthLease:
    """Exclusive across login commands and independent hubs; never unlink it."""
    def __init__(self, home: Path):
        self.home = home
        self._descriptor: int | None = None

    def acquire(self) -> None:
        if self._descriptor is not None:
            return
        private_directory(self.home)
        descriptor = os.open(self.home / "studio.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
        try:
            info = os.fstat(descriptor)
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600:
                raise CodexAuthError("Studio Codex lease must be an operator-owned mode-0600 file")
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise CodexAuthError("Studio Codex login is already owned. Stop the other hub before login or starting another hub.") from None
        except BaseException:
            os.close(descriptor)
            raise
        self._descriptor = descriptor

    def release(self) -> None:
        if self._descriptor is not None:
            os.close(self._descriptor)
            self._descriptor = None

    @property
    def descriptor(self) -> int:
        if self._descriptor is None:
            raise CodexAuthError("Studio Codex auth lease is not held")
        return self._descriptor


# Native state emitted by the qualified runtime; configuration is supplied only
# through reviewed overrides. Entries outside this set are never imported.
NATIVE_ENTRIES = frozenset({
    "auth.json", "studio.lock", "studio-threads.json", "sessions", "archived_sessions",
    "log", "tmp", "sqlite", "state_5.sqlite", "state_5.sqlite-wal", "state_5.sqlite-shm",
    "logs_2.sqlite", "logs_2.sqlite-wal", "logs_2.sqlite-shm", "session_index.jsonl",
    ".migration_marker", ".sandbox_migration", "thread-writer-locks", "version.json", ".tmp", "installation_id", "skills",
    *(f"{name}_{version}.sqlite{suffix}" for name, version in (("goals", 1), ("memories", 1), ("queue", 1), ("thread_history", 1))
      for suffix in ("", "-wal", "-shm")),
})


def cleanup_journal_temporaries(home: Path) -> None:
    """Under the exclusive lease, recover interrupted owned atomic writes."""
    for entry in home.iterdir():
        if not entry.name.startswith(".studio-threads-"):
            continue
        suffix = entry.name.removeprefix(".studio-threads-")
        info = entry.lstat()
        if (len(suffix) != 8 or not all(char in "abcdefghijklmnopqrstuvwxyz0123456789_" for char in suffix)
            or not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) != 0o600 or info.st_size > 1024 * 1024):
            raise CodexAuthError("Invalid Studio thread-journal temporary file; remove it before use")
        entry.unlink()


def validate_home(home: Path, *, require_auth: bool = False) -> None:
    private_directory(home)
    for entry in home.iterdir():
        if entry.is_symlink():
            raise CodexAuthError("Studio Codex home contains a symlink; remove it before use")
        if entry.name not in NATIVE_ENTRIES:
            raise CodexAuthError(f"Unexpected Studio Codex configuration/state entry {entry.name!r}; remove it before use")
        if entry.name == "skills" and any(entry.iterdir()):
            raise CodexAuthError("Studio Codex native skills must be empty; only profile skills are available")
        if entry.name == ".sandbox_migration" or entry.name.startswith("thread_history_1.sqlite"):
            info = entry.lstat()
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o002:
                raise CodexAuthError("Invalid owned native bookkeeping file")
            if entry.name == ".sandbox_migration" and (info.st_size != 3 or entry.read_bytes() != b"v1\n" or stat.S_IMODE(info.st_mode) != 0o600):
                raise CodexAuthError("Invalid pinned native sandbox migration marker")
        if entry.name == "thread-writer-locks":
            info = entry.lstat()
            if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o002:
                raise CodexAuthError("Invalid owned native writer-lock directory")
            children = list(entry.iterdir())
            if len(children) > 256:
                raise CodexAuthError("Too many native writer locks")
            for child in children:
                name = child.name
                try:
                    valid_name = name == ".coordination.lock" or (name.endswith(".lock") and str(uuid.UUID(name[:-5])) == name[:-5])
                except ValueError:
                    valid_name = False
                info = child.lstat()
                if not valid_name or not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_size != 0 or info.st_mode & 0o002:
                    raise CodexAuthError("Invalid pinned native writer-lock metadata")
    if not require_auth:
        return
    auth = home / "auth.json"
    if not auth.is_file():
        raise CodexAuthError(f"Studio Codex is not logged in. Run {LOGIN_COMMAND}")
    info = auth.stat()
    if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600 or info.st_size > 1024 * 1024:
        raise CodexAuthError(f"Invalid Studio Codex credential storage. Run {LOGIN_COMMAND}")
    try:
        value = json.loads(auth.read_bytes())
        tokens = value.get("tokens")
        valid = (value.get("auth_mode") in (None, "chatgpt") and not value.get("OPENAI_API_KEY")
                 and isinstance(tokens, dict) and all(isinstance(tokens.get(key), str) and tokens[key]
                                                     for key in ("access_token", "refresh_token", "id_token", "account_id")))
    except (ValueError, TypeError, AttributeError, OSError):
        valid = False
    if not valid:
        raise CodexAuthError(f"Studio requires its dedicated file-backed ChatGPT login. Run {LOGIN_COMMAND}")


def child_environment(home: Path, private: Path) -> dict[str, str]:
    """No operator auth/provider/proxy/config variables cross this boundary."""
    environment = {key: value for key, value in os.environ.items()
                   if key in {"LANG", "LC_ALL", "SSL_CERT_FILE", "SSL_CERT_DIR"}}
    for directory in (private / "home", private / "config", private / "data", private / "state", private / "tmp"):
        private_directory(directory)
    environment.update(HOME=str(private / "home"), CODEX_HOME=str(home),
                       XDG_CONFIG_HOME=str(private / "config"), XDG_DATA_HOME=str(private / "data"),
                       XDG_STATE_HOME=str(private / "state"), TMPDIR=str(private / "tmp"))
    return environment


def codex_binary() -> Path:
    command = shutil.which("codex")
    if command is None:
        raise CodexAuthError("Install Codex CLI 0.157.1 before using Studio Codex")
    # Runtime package shims dispatch the actual platform binary. Qualification
    # resolves/fingerprints that artifact; login uses the same resolved binary.
    resolved = Path(command).resolve()
    if resolved.name.endswith(".js"):
        package = resolved.parent.parent
        relative = Path("vendor/x86_64-unknown-linux-musl/bin/codex")
        candidates = [root / relative for root in (
            package / "node_modules/@openai/codex-linux-x64", package.parent / "codex-linux-x64", package
        ) if (root / relative).is_file()]
        if len(candidates) != 1:
            raise CodexAuthError("Unsupported Codex package layout; install the qualified Linux CLI")
        resolved = candidates[0].resolve()
    with tempfile.TemporaryDirectory(prefix="studio-codex-version-") as temporary:
        private = Path(temporary)
        home = private / "codex"
        private_directory(home)
        version = subprocess.run([str(resolved), "--version"], cwd=private, env=child_environment(home, private),
                                 capture_output=True, text=True, timeout=10, check=True).stdout.strip()
    if version != PINNED_VERSION:
        raise CodexAuthError(f"Unsupported Codex version; install {PINNED_VERSION}")
    return resolved


def login() -> None:
    home = studio_home()
    lease = AuthLease(home)
    lease.acquire()
    try:
        cleanup_journal_temporaries(home)
        validate_home(home)
        binary = codex_binary()
        with tempfile.TemporaryDirectory(prefix="studio-codex-login-") as temporary:
            private = Path(temporary)
            from .backends.codex_policy import command, settings, controlled_catalogue, check_policy, validate_schema
            from .backends.codex_qualification import CodexQualifier
            from .backends.codex_wire import CodexConnection
            environment = child_environment(home, private)
            validate_schema(binary, private, environment)
            catalogue = private / "catalogue.json"
            catalogue.write_text(json.dumps(controlled_catalogue(binary)))
            policy = settings(catalogue)

            async def preflight() -> None:
                await CodexQualifier().qualify([])
                connection = await CodexConnection.start(command(binary, policy), cwd=str(private),
                                                         env=environment, pass_fds=(lease.descriptor,))
                try:
                    await check_policy(connection, policy)
                finally:
                    await connection.close()
            asyncio.run(preflight())
            validate_home(home)
            # Login runs no inference/threads/tools. It can only provision this
            # authoritative store, using ordinary native device authentication.
            result = subprocess.run(command(binary, policy)[:-3] + ["login", "--device-auth"],
                                    cwd=private, env=environment,
                                    pass_fds=(lease.descriptor,), check=False)
            if result.returncode:
                raise CodexAuthError(f"Studio Codex login failed; run {LOGIN_COMMAND} again")
        auth = home / "auth.json"
        if auth.is_file() and not auth.is_symlink():
            auth.chmod(0o600)
        validate_home(home, require_auth=True)
    finally:
        lease.release()


def main() -> None:
    from floor.backends.codex_policy import CodexPolicyError
    parser = argparse.ArgumentParser(description="Provision Studio's separate Codex login; stop the hub first.")
    parser.add_argument("operation", choices=("login",))
    parser.parse_args()
    try:
        login()
    except (CodexAuthError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f"{error if isinstance(error, CodexAuthError) else 'Studio Codex login could not start'}\n")
    except CodexPolicyError:
        parser.exit(1, "Studio Codex qualification or native policy failed; use the pinned supported CLI and remove conflicting managed configuration before retrying\n")
    except Exception:
        parser.exit(1, "Studio Codex login preflight failed; no login was provisioned by this attempt\n")


if __name__ == "__main__":
    main()
