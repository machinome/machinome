"""Chosen material with explicit optional density, in kg/m³."""

from dataclasses import dataclass
import math


def positive(value, name):
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value <= 0
    ):
        raise ValueError(f"{name} must be finite and positive")


@dataclass(frozen=True)
class Material:
    name: str
    density_kg_m3: float | None = None

    def __init__(self, name, *, density_kg_m3=None):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("material name must be nonempty text")
        if density_kg_m3 is not None:
            positive(density_kg_m3, "density_kg_m3")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "density_kg_m3", density_kg_m3)
