"""Per-occurrence measured mass or an explicit homogeneous-solid assumption."""

from dataclasses import dataclass
from pathlib import Path
import math
import inspect


@dataclass(frozen=True)
class MeasuredMass:
    grams: float
    evidence: str | Path

    def __init__(self, grams, *, evidence):
        if (
            isinstance(grams, bool)
            or not isinstance(grams, (int, float))
            or not math.isfinite(grams)
            or grams < 0
        ):
            raise ValueError("measured grams must be finite and nonnegative")
        if not isinstance(evidence, (str, Path)) or not str(evidence):
            raise ValueError("MeasuredMass requires a local evidence file")
        object.__setattr__(self, "grams", grams)
        object.__setattr__(self, "evidence", evidence)
        object.__setattr__(
            self,
            "_source_file",
            Path(inspect.currentframe().f_back.f_code.co_filename).absolute(),
        )


@dataclass(frozen=True)
class SolidMass:
    """Request volume times density, assuming a homogeneous solid."""
