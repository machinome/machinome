# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
"""The shop's dependency on the external OpenSpec CLI.

This is the one ambient ``PATH`` executable the shop depends on. Everything
else the shop runs resolves from the loaded package or its own Python
environment; see ADR 0027 for why the boundary is relaxed here and nowhere
else.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

OPENSPEC_EXECUTABLE = "openspec"

# The CLI resolves its root by walking up to the nearest directory holding
# this file. The shop replicates that walk so a call can be refused before a
# process starts, rather than discovered after one has written somewhere.
RECORD_MARKER = Path("openspec") / "config.yaml"

# Subcommands that read or write OpenSpec state belonging to the machine
# rather than to the active project.
OUTSIDE_PROJECT_SUBCOMMANDS = frozenset({"store", "config", "feedback", "completion"})

SETUP_COMMIT_MESSAGE = "chore(openspec): prepare the project's spec record"

# Seeded once, then owned by the project. The CLI folds `context` into every
# artifact's instructions and each `rules` entry into that artifact's, so the
# vocabulary reaches the agent exactly when it is writing one.
HOUSE_RULES = """schema: spec-driven

context: |
  This is a mechanical project. Its parts are machined from parametric
  source, and this record is their durable design record: what the parts
  promise each other, and why they are shaped the way they are.

  A capability is an interface between parts, never a part. Name what has to
  agree between two things — `lid-body-interface`, `shaft-bearing-fit` — not
  the thing itself.

  A requirement is a measurable guarantee about that interface: a fit, a
  clearance, a tolerance, a load path, an assembly order.

  A scenario is one fit or assembly test. Each becomes a test in the project,
  written to fail before the geometry makes it pass.

  Knob values are not design decisions. Parameter schemas, derived
  relationships, guards, and observable behaviour are.

rules:
  proposal:
    - "Name the interfaces the change establishes or alters, not the parts you plan to edit."
    - "Say what physically goes wrong today; a proposal without a failure is a preference."
  specs:
    - "Write a MODIFIED requirement as the complete replacement block, every unchanged line included. Detail you omit is silently lost when the change is archived."
    - "State every tolerance, clearance, and load with its unit."
  design:
    - "Record the alternatives you rejected and the measurement that decided it."
  tasks:
    - "Order the work so a failing fit or assembly test exists before the geometry that satisfies it."
    - "Archiving a new capability writes `Purpose: TBD` into its spec. Replace that line with what the interface is for before you commit: a spec left stamped `Purpose: TBD` records nothing."
"""

INSTALL_HINT = "install Node.js and run `npm install -g @fission-ai/openspec`"

_VERSION_TIMEOUT_SECONDS = 30


class OpenSpecUnavailable(RuntimeError):
    """The OpenSpec CLI is missing or cannot be run."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"the `{OPENSPEC_EXECUTABLE}` CLI is required to run the shop: {reason}; {INSTALL_HINT}")


def resolve_openspec_command() -> tuple[str, ...]:
    """Return the OpenSpec command, proving it is present and runnable.

    Resolution is deliberately eager: a shop that cannot record a design
    should say so at startup rather than several turns into a design change.
    """
    located = shutil.which(OPENSPEC_EXECUTABLE)
    if located is None:
        raise OpenSpecUnavailable(f"`{OPENSPEC_EXECUTABLE}` was not found on PATH")
    try:
        completed = subprocess.run(
            [located, "--version"],
            capture_output=True,
            text=True,
            timeout=_VERSION_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise OpenSpecUnavailable(f"`{located}` could not be executed ({error})") from error
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip().splitlines()
        reported = f": {detail[0]}" if detail else ""
        raise OpenSpecUnavailable(f"`{located} --version` exited {completed.returncode}{reported}")
    return (located,)


def resolve_openspec_root(start: Path) -> Path | None:
    """The root the CLI would resolve from ``start``, without running it."""
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / RECORD_MARKER).is_file():
            return candidate
    return None


def openspec_environment(environment: dict[str, str]) -> dict[str, str]:
    """Strip OpenSpec overrides so the child resolves what we verified."""
    return {name: value for name, value in environment.items() if not name.startswith("OPENSPEC")}
