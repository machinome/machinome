"""Deterministic, inspection-only print packages from a published build."""

from __future__ import annotations

import io
import json
import re
import tempfile
import unicodedata
import zipfile
from pathlib import Path
from typing import BinaryIO


BUILD_VOLUME = (250, 210, 220)
_PIECE_ID = re.compile(r"[0-9a-f]{12}")
_ZIP_DATE = (1980, 1, 1, 0, 0, 0)


class BuildPackageError(ValueError):
    """The current publication cannot produce a trustworthy package."""


def _slug(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-") or "piece"


def _zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, _ZIP_DATE)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info


def _pieces(artifact_root: Path) -> list[tuple[str, int, Path]]:
    root = artifact_root.resolve()
    try:
        document = json.loads((root / "viewer.json").read_text())
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise BuildPackageError("the current piece publication is unavailable") from error
    raw_pieces = document.get("pieces") if isinstance(document, dict) else None
    if not isinstance(raw_pieces, list) or not raw_pieces:
        raise BuildPackageError("the current publication has no piece inventory")

    result: list[tuple[str, int, Path]] = []
    ids: set[str] = set()
    filenames: set[str] = set()
    for raw in raw_pieces:
        if not isinstance(raw, dict):
            raise BuildPackageError("the piece inventory is malformed")
        piece_id = raw.get("id")
        name = raw.get("name")
        count = raw.get("count")
        models = raw.get("models")
        if (
            not isinstance(piece_id, str) or _PIECE_ID.fullmatch(piece_id) is None
            or piece_id in ids or not isinstance(name, str) or not name.strip()
            or not isinstance(count, int) or isinstance(count, bool) or count < 1
            or not isinstance(models, list) or not models
            or any(not isinstance(model, str) or not model for model in models)
        ):
            raise BuildPackageError("the piece inventory is malformed")
        reference = sorted(models)[0]
        if Path(reference).suffix.lower() != ".stl":
            raise BuildPackageError(f"piece {piece_id} does not reference an STL")
        candidate = (root / reference).resolve()
        if root not in candidate.parents or not candidate.is_file():
            raise BuildPackageError(f"piece {piece_id} references an unavailable artifact")
        filename = f"{_slug(name)}-{piece_id}.stl"
        if filename in filenames:
            raise BuildPackageError("distinct pieces resolve to the same package filename")
        ids.add(piece_id)
        filenames.add(filename)
        result.append((filename, count, candidate))
    return sorted(result, key=lambda item: item[0].rsplit("-", 1)[-1])


def _readme(pieces: list[tuple[str, int, Path]]) -> bytes:
    width, depth, height = BUILD_VOLUME
    lines = [
        "# Print package",
        "",
        "This package contains one STL for each distinct piece in the completed model.",
        "Print each file the number of times listed below.",
        "",
        f"Inspection build volume: {width} × {depth} × {height} mm.",
        "",
        "| File | Copies to print |",
        "| --- | ---: |",
    ]
    lines.extend(f"| `{filename}` | {count} |" for filename, count, _ in pieces)
    lines.append("")
    return "\n".join(lines).encode()


def write_build_package(artifact_root: Path, output: BinaryIO) -> None:
    pieces = _pieces(artifact_root)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        archive.writestr(_zip_info("README.md"), _readme(pieces))
        for filename, _, source in pieces:
            archive.writestr(_zip_info(filename), source.read_bytes())


def build_package(artifact_root: Path) -> bytes:
    output = io.BytesIO()
    write_build_package(artifact_root, output)
    return output.getvalue()


def open_build_package(artifact_root: Path) -> tempfile.SpooledTemporaryFile[bytes]:
    output = tempfile.SpooledTemporaryFile(max_size=8 * 1024 * 1024, mode="w+b")
    try:
        write_build_package(artifact_root, output)
        output.seek(0)
        return output
    except Exception:
        output.close()
        raise


def package_filename(project: str) -> str:
    return f"{_slug(project)}-print-package.zip"
