"""Immutable report records, with root-relative occurrence traceability."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    occurrences: tuple[str, ...]
    declarations: tuple[str, ...]
    message: str
    check_status: str = "checked"


@dataclass(frozen=True)
class BomLine:
    line_id: str
    status: str
    process: object | None
    requested_process: object | None
    quantity: int
    occurrence_paths: tuple[str, ...]
    declaration_paths: tuple[str, ...]
    source_paths: tuple[Path, ...]
    finding_codes: tuple[str, ...]
    geometry_id: str | None = None
    material: object | None = None
    requirement: object | None = None
    offer: object | None = None


@dataclass(frozen=True)
class StockLine:
    stock: object
    finished_count: int
    purchased_quantity: int | None
    occurrence_paths: tuple[str, ...]


@dataclass(frozen=True)
class ResolvedStep:
    step_id: str
    scope_path: str
    subject_paths: tuple[str, ...]
    instruction_path: Path
    instruction_text: str
    instruction_sha256: str


@dataclass(frozen=True)
class MassBasis:
    occurrence_path: str
    grams: float | None
    basis: str
    reason: str | None = None
    evidence_path: Path | None = None


@dataclass(frozen=True)
class MassSummary:
    known_grams: float
    complete: bool
    unknown_occurrences: tuple[str, ...]
    basis: tuple[MassBasis, ...]


@dataclass(frozen=True)
class ExportResult:
    path: Path
    coverage_complete: bool
    findings: tuple[Finding, ...]
    executed_code_provenance: str
