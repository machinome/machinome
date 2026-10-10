"""Ordered maker instructions with declaring-module file attribution."""

from dataclasses import dataclass
from pathlib import Path
import inspect
from .errors import DeclarationError


@dataclass(frozen=True)
class Markdown:
    path: str | Path

    def __post_init__(self):
        if not isinstance(self.path, (str, Path)) or not str(self.path):
            raise DeclarationError("Markdown requires a local file path")


@dataclass(frozen=True, eq=False)
class Step:
    subjects: tuple
    instructions: Markdown

    def __init__(self, *subjects, instructions):
        if not subjects or not isinstance(instructions, Markdown):
            raise DeclarationError(
                "Step requires subjects and Markdown instructions"
            )
        object.__setattr__(self, "subjects", subjects)
        object.__setattr__(self, "instructions", instructions)
        object.__setattr__(
            self,
            "_source_file",
            Path(inspect.currentframe().f_back.f_code.co_filename).absolute(),
        )
