#!/usr/bin/env python3
"""T: the relicensing transform of the machinome repository.

Turns any checkout of the repository into its relicensed form:
GPL-2.0-or-later OR CERN-OHL-S-2.0+ at the recipient's choice, with the
consent of all contributors. Runs with the current directory at the root of
the tree (a plain checkout; no .git needed) and is idempotent: a second run
changes nothing. Used once to make the licence commit on top of origin/main
(bf24687) and then by `git filter-branch --tree-filter` over every later
commit, so that no tree after the licence commit carries the old grant.

Assets (LICENSE statement and the two licence texts) live beside this script
unless RELICENSE_ASSETS points elsewhere. Standard library only.
"""
import os
import re
import sys
from pathlib import Path

ASSETS = Path(os.environ.get("RELICENSE_ASSETS", Path(__file__).resolve().parent))
EXPR = "GPL-2.0-or-later OR CERN-OHL-S-2.0+"
PROSE = "GPL-2.0-or-later or CERN-OHL-S-2.0-or-later"
VERBOSE = bool(os.environ.get("RELICENSE_VERBOSE"))

HEADER = re.compile(
    rb"^([ \t]*#[ \t]*)SPDX-License-Identifier: (?:Apache-2\.0|AGPL-3\.0-or-later)[ \t]*(\r?)$",
    re.M,
)
HEADER_NEW = b"\\1SPDX-License-Identifier: " + EXPR.encode() + b"\\2"

changed = []


def note(path):
    changed.append(str(path))


def rewrite_text(path, fn):
    """Apply fn(text) -> text to a UTF-8 file; write only when it changes."""
    p = Path(path)
    if not p.is_file():
        return
    old = p.read_text(encoding="utf-8")
    new = fn(old)
    if new != old:
        p.write_text(new, encoding="utf-8")
        note(p)


def replace_literal(path, pairs):
    def fn(text):
        for old, new in pairs:
            text = text.replace(old, new)
        return text
    rewrite_text(path, fn)


# 1. Headers: every file but LICENSE and LICENSES/.
def headers():
    root = Path(".")
    for dirpath, dirnames, filenames in os.walk(root):
        d = Path(dirpath)
        dirnames[:] = [n for n in dirnames if n != ".git" and not (d == root and n == "LICENSES")]
        for name in filenames:
            p = d / name
            if d == root and name == "LICENSE":
                continue
            if p.is_symlink() or not p.is_file():
                continue
            data = p.read_bytes()
            if b"\0" in data or b"SPDX-License-Identifier" not in data:
                continue
            new = HEADER.sub(HEADER_NEW, data)
            if new != data:
                p.write_bytes(new)
                note(p)


# 2. Licence files.
def licence_files():
    statement = (ASSETS / "LICENSE").read_bytes()
    lic = Path("LICENSE")
    if not lic.exists() or lic.read_bytes() != statement:
        lic.write_bytes(statement)
        note(lic)
    Path("LICENSES").mkdir(exist_ok=True)
    for name in ("GPL-2.0-or-later.txt", "CERN-OHL-S-2.0.txt"):
        src = (ASSETS / "LICENSES" / name).read_bytes()
        dst = Path("LICENSES") / name
        if not dst.exists() or dst.read_bytes() != src:
            dst.write_bytes(src)
            note(dst)
    notice = Path("NOTICE")
    if notice.exists():
        notice.unlink()
        note(notice)


# 3. pyproject.toml
def pyproject():
    replace_literal("pyproject.toml", [
        ('requires = ["setuptools>=65.5,<77"]', 'requires = ["setuptools>=77"]'),
        ('license = { text = "Apache-2.0" }',
         'license = "%s"\nlicense-files = ["LICENSE", "LICENSES/*.txt"]' % EXPR),
    ])


# 4. MANIFEST.in
def manifest():
    def fn(text):
        return re.sub(r"^include NOTICE[ \t]*$", "recursive-include LICENSES *.txt", text, flags=re.M)
    rewrite_text("MANIFEST.in", fn)


# 5. CREDITS.md
CREDITS_BLOCK = """## Project License

**Machinome** is offered under two licences, at the recipient's choice:

- the GNU General Public License, version 2 or any later version
  (`GPL-2.0-or-later`); or
- the CERN Open Hardware Licence Version 2 - Strongly Reciprocal, version 2.0
  or any later version (`CERN-OHL-S-2.0+`).

Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes and contributors. The
statement is in `LICENSE` and the full texts are in `LICENSES/`.

---

"""


def credits():
    def fn(text):
        text = re.sub(r"^## Project License\n.*?(?=^## Third-Party Dependencies)",
                      CREDITS_BLOCK, text, count=1, flags=re.M | re.S)
        text = re.sub(r"^- \*\*License Compatibility:\*\*.*\n", "", text, flags=re.M)
        return text
    rewrite_text("CREDITS.md", fn)


# 6. AI-USE.md
def ai_use():
    replace_literal("AI-USE.md", [
        ("repository's licence, Apache-2.0, holds the copyright the `NOTICE` states,",
         "repository's licence, %s at the\nrecipient's choice, holds the copyright `LICENSE` states," % PROSE),
    ])


# 7. framework-identity spec
def spec():
    replace_literal("openspec/specs/framework-identity/spec.md", [
        ("beside the Apache framework", "beside the framework"),
        ("the independent Apache `machinome-mechanics` distribution",
         "the independent `machinome-mechanics` distribution"),
    ])


# 8. README.rst (pre-release trees)
def readme():
    replace_literal("README.rst", [
        ("The framework is **Apache-2.0**. The optional\n"
         "`Machinome Viewer <https://github.com/machinome/machinome-viewer>`_\n"
         "is **AGPL-3.0-or-later**, installed through ``viewer``.",
         "Machinome is licensed **%s**, at\n"
         "the recipient's choice. The optional\n"
         "`Machinome Viewer <https://github.com/machinome/machinome-viewer>`_\n"
         "is **AGPL-3.0-or-later**, installed through ``viewer``." % PROSE),
    ])


# 9. docs/architecture.md (pre-release trees)
def architecture():
    replace_literal("docs/architecture.md", [
        ("(ADR-068/103); the framework is Apache-2.0 and complete for non-interactive",
         "(ADR-068/103); the framework is licensed GPL-2.0-or-later or\n"
         "CERN-OHL-S-2.0-or-later, at the recipient's choice, and complete for non-interactive"),
        ("ADR-076 live in the independent Apache-2.0 `machinome-mechanics` package",
         "ADR-076 live in the independent `machinome-mechanics` package"),
    ])


# 9b. Manual pages that named the grant before the 0.8 release stated it
# through |framework_licence| (pre-release trees only; the literals are gone
# at main). The mechanics package's own licence in manuals.rst is a fact
# about another package and stays.
def docs_pages():
    replace_literal("docs/why.rst", [
        ("The framework is Apache-2.0. The independent browser viewer is",
         "The framework is licensed %s, at the\nrecipient's choice. The independent browser viewer is" % PROSE),
    ])
    replace_literal("docs/project/status.rst", [
        ("Machinome is Apache-2.0. Machinome Viewer is an optional, independent",
         "Machinome is licensed %s, at the\nrecipient's choice. Machinome Viewer is an optional, independent" % PROSE),
    ])
    replace_literal("docs/start/install.rst", [
        ("The framework is one package, ``machinome``, licensed Apache-2.0. The",
         "The framework is one package, ``machinome``, licensed %s\nat the recipient's choice. The" % PROSE),
    ])


# 10. HISTORY.rst: an Unreleased entry until a release states the licence.
HISTORY_TITLE = "=======\nHistory\n=======\n\n"
HISTORY_ENTRY = """Unreleased
----------

* **Machinome is GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, at the
  recipient's choice.** Every release up to 0.7.1 is Apache-2.0; from here
  the framework is relicensed, with the consent of all contributors, under
  the GNU General Public License version 2 or any later version, or the
  CERN Open Hardware Licence Version 2 - Strongly Reciprocal version 2.0 or
  any later version, so that a design under CERN-OHL-S can use the
  framework under its own licence. Contributions are accepted under both.
  Decided by the pilot on 4 October 2026.

"""


def history():
    def fn(text):
        if re.search(r"^Unreleased$", text, re.M) or re.search(r"^Machinome 0\.8\.0", text, re.M):
            return text
        if not text.startswith(HISTORY_TITLE):
            raise SystemExit("HISTORY.rst: unexpected title block")
        return HISTORY_TITLE + HISTORY_ENTRY + text[len(HISTORY_TITLE):]
    rewrite_text("HISTORY.rst", fn)


def main():
    if not Path("pyproject.toml").is_file():
        raise SystemExit("relicense.py: run at the root of a machinome checkout")
    headers()
    licence_files()
    pyproject()
    manifest()
    credits()
    ai_use()
    spec()
    readme()
    architecture()
    docs_pages()
    history()
    if VERBOSE:
        print("relicense.py: %d paths changed" % len(changed), file=sys.stderr)
        for p in changed:
            print("  " + p, file=sys.stderr)


if __name__ == "__main__":
    main()
