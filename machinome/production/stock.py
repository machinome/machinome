"""Chosen starting stock and its explicit dimensions."""

from dataclasses import dataclass
from .material import Material, positive


@dataclass(frozen=True)
class Sheet:
    material: Material
    thickness_mm: float

    def __init__(self, material, *, thickness_mm):
        if not isinstance(material, Material):
            raise ValueError("Sheet requires a Material")
        positive(thickness_mm, "thickness_mm")
        object.__setattr__(self, "material", material)
        object.__setattr__(self, "thickness_mm", thickness_mm)
