#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check this instruction package; optionally build deterministic ZIP archives."""

from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

try:
    import yaml
except ImportError:
    sys.exit("Install the development dependencies from requirements-dev.txt first.")


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("machinome", "machinome-simulate")
PACKAGE_FILES = (
    ".gitignore",
    "README.md",
    "LICENSE",
    "NOTICE",
    "requirements-dev.txt",
    "scripts/check.py",
    "docs/evaluation.md",
)
LINK = re.compile(r"\[[^\]\n]+\]\(([^\s)]+)\)")


def check_links(path: Path, boundary: Path) -> None:
    for target in LINK.findall(path.read_text(encoding="utf-8")):
        url = urlsplit(target)
        if url.scheme or url.netloc or not url.path:
            continue
        resolved = (path.parent / unquote(url.path)).resolve()
        if not resolved.is_relative_to(boundary) or not resolved.is_file():
            raise ValueError(f"{path.relative_to(ROOT)}: invalid local reference {target}")


def validate() -> dict[str, list[Path]]:
    found = {path.name for path in (ROOT / "skills").iterdir()}
    if found != set(SKILLS):
        raise ValueError(f"Expected exactly {SKILLS}; found {sorted(found)}")

    for filename in PACKAGE_FILES:
        path = ROOT / filename
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Missing or symlinked package file: {filename}")
        if path.suffix == ".md":
            check_links(path, ROOT)

    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    if "Version 2.0, January 2004" not in license_text or "END OF TERMS AND CONDITIONS" not in license_text:
        raise ValueError("Root LICENSE must contain the complete Apache-2.0 terms")

    entries = {}
    for name in SKILLS:
        directory = ROOT / "skills" / name
        paths = sorted(directory.rglob("*"))
        if directory.is_symlink() or any(path.is_symlink() for path in paths):
            raise ValueError(f"{name}: ship real files, not workspace symlinks")

        skill_path = directory / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        frontmatter = re.match(r"\A---\n(.*?)\n---\n", content, re.DOTALL)
        if not frontmatter:
            raise ValueError(f"{name}: missing YAML frontmatter")
        data = yaml.safe_load(frontmatter.group(1))
        if not isinstance(data, dict) or set(data) != {"name", "description", "license"}:
            raise ValueError(f"{name}: use the package's portable name/description/license fields")
        if data["name"] != name or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
            raise ValueError(f"{name}: invalid or mismatched skill name")
        description = data["description"]
        if not isinstance(description, str) or not 1 <= len(description.strip()) <= 1024:
            raise ValueError(f"{name}: description must contain 1–1024 characters")
        if data["license"] != "Apache-2.0":
            raise ValueError(f"{name}: incorrect license declaration")
        if len(content.splitlines()) >= 500:
            raise ValueError(f"{name}: move detailed guidance into references")

        for filename, original in (("LICENSE.txt", "LICENSE"), ("NOTICE", "NOTICE")):
            if (directory / filename).read_bytes() != (ROOT / original).read_bytes():
                raise ValueError(f"{name}: {filename} differs from the package's {original}")

        files = [path for path in paths if path.is_file()]
        links = set(LINK.findall(content))
        for path in files:
            if path.suffix == ".md":
                check_links(path, directory)
            if path.parent == directory / "references":
                if path.relative_to(directory).as_posix() not in links:
                    raise ValueError(f"{name}: reference is not routed from SKILL.md: {path.name}")
        entries[name] = files
        print(f"OK {name}: {len(content.splitlines())} entry-point lines; {len(files)} files")
    return entries


def write_zip(name: str, members: list[tuple[str, Path]]) -> None:
    buffer = BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as archive:
        for arcname, source in sorted(members):
            info = ZipInfo(arcname, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, source.read_bytes())
    destination = ROOT / "dist" / name
    destination.parent.mkdir(exist_ok=True)
    destination.write_bytes(buffer.getvalue())
    print(f"Built {destination.relative_to(ROOT)} ({destination.stat().st_size} bytes)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true", help="also write the package and individual skill ZIPs to dist/")
    args = parser.parse_args()
    try:
        entries = validate()
        if args.build:
            all_files = [ROOT / path for path in PACKAGE_FILES]
            for name, files in entries.items():
                write_zip(f"{name}.zip", [(path.relative_to(ROOT / "skills").as_posix(), path) for path in files])
                all_files.extend(files)
            write_zip("machinome-skills.zip", [(f"machinome-skills/{path.relative_to(ROOT).as_posix()}", path) for path in all_files])
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
