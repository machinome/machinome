"""Explicit occurrence selection with a complete acquisition recipe."""

from dataclasses import dataclass
from .process import Printed, Cut, Sourced
from .mass import MeasuredMass, SolidMass
from .errors import DeclarationError


@dataclass(frozen=True, eq=False)
class Item:
    target: object
    process: Printed | Cut | Sourced
    mass: MeasuredMass | SolidMass | None = None

    def __init__(self, target, process, *, mass=None):
        if not isinstance(process, (Printed, Cut, Sourced)):
            raise DeclarationError("Item requires Printed, Cut or Sourced")
        if mass is not None and not isinstance(
            mass, (MeasuredMass, SolidMass)
        ):
            raise DeclarationError(
                "Item mass must be MeasuredMass, SolidMass or None"
            )
        if isinstance(target, tuple) and not target:
            raise DeclarationError("Item target tuple cannot be empty")
        object.__setattr__(self, "target", target)
        object.__setattr__(self, "process", process)
        object.__setattr__(self, "mass", mass)

    def __get__(self, instance, owner=None):
        return self if instance is None else instance._bound_item(self)


@dataclass(frozen=True)
class BoundItem:
    target_paths: tuple[str, ...]
    process: Printed | Cut | Sourced
    mass_basis: MeasuredMass | SolidMass | None
    declaration_path: str
