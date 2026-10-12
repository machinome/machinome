#!/usr/bin/env python3
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""Finite Machinome CLI used by the scoped MCP tool tests."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


capture = os.environ.get("FAKE_SCOPED_MACHINOME_CAPTURE")
if capture:
    with Path(capture).open("a") as stream:
        stream.write(json.dumps({"argv": sys.argv[1:], "cwd": os.getcwd()}) + "\n")

command = sys.argv[1]
reference = next(
    (item for item in sys.argv[2:] if not item.startswith("-") and "x" not in item),
    "",
)
if reference == "fail":
    print(f"{command} failed", file=sys.stderr)
    raise SystemExit(17)

if command == "snapshot":
    output = Path(sys.argv[sys.argv.index("-o") + 1])
    output.write_bytes(b"\x89PNG\r\n\x1a\nFAKE")
elif command not in {"build", "test"}:
    raise SystemExit(2)

print(f"{command} ok")
