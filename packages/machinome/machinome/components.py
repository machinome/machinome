"""Neutral catalogue identities, independent of models and production."""

from dataclasses import dataclass


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be nonempty text")


@dataclass(frozen=True)
class Standard:
    name: str
    designation: str
    grade: str | None = None

    def __init__(self, name, *, designation, grade=None):
        _text(name, "standard name")
        _text(designation, "designation")
        if grade is not None:
            _text(grade, "grade")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "designation", designation)
        object.__setattr__(self, "grade", grade)


@dataclass(frozen=True)
class Product:
    manufacturer: str
    part_number: str
    conforms_to: tuple[Standard, ...] = ()

    def __init__(self, manufacturer, part_number, *, conforms_to=()):
        _text(manufacturer, "manufacturer")
        _text(part_number, "part number")
        if not isinstance(conforms_to, tuple) or any(
            not isinstance(s, Standard) for s in conforms_to
        ):
            raise ValueError("conforms_to must be a tuple of Standard records")
        object.__setattr__(self, "manufacturer", manufacturer)
        object.__setattr__(self, "part_number", part_number)
        object.__setattr__(self, "conforms_to", conforms_to)
