"""Typed primary acquisition recipes; finishing belongs in maker Steps."""

from dataclasses import dataclass
from machinome.components import Standard, Product
from .material import Material
from .stock import Sheet
from .sourcing import Offer


@dataclass(frozen=True)
class Printed:
    material: Material | None = None

    def __post_init__(self):
        if self.material is not None and not isinstance(
            self.material, Material
        ):
            raise ValueError("Printed material must be Material or None")


@dataclass(frozen=True)
class Cut:
    stock: Sheet

    def __post_init__(self):
        if not isinstance(self.stock, Sheet):
            raise ValueError("Cut requires Sheet stock")


@dataclass(frozen=True)
class Sourced:
    requirement: Standard | Product
    offer: Offer | None = None

    def __init__(self, requirement, *, offer=None):
        if not isinstance(requirement, (Standard, Product)):
            raise ValueError("Sourced requires a Standard or Product")
        if offer is not None:
            if not isinstance(offer, Offer):
                raise ValueError("Sourced offer must be an Offer")
            matched = (
                offer.product == requirement
                if isinstance(requirement, Product)
                else requirement in offer.product.conforms_to
            )
            if not matched:
                raise ValueError(
                    "Offer product does not explicitly match the requirement"
                )
        object.__setattr__(self, "requirement", requirement)
        object.__setattr__(self, "offer", offer)
