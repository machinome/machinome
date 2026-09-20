"""Keep the published helper reference complete as the Python API evolves."""

import ast
import inspect
from pathlib import Path
import re

import machinome_mechanics as mechanics


def test_every_export_has_one_reference_with_the_actual_signature():
    reference = Path(__file__).resolve().parents[1] / "docs" / "reference"
    signatures = [
        signature
        for page in reference.glob("*.rst")
        for signature in re.findall(r"^\.\. py:function:: (.+)$", page.read_text(), re.M)
    ]
    names = [signature.split("(", 1)[0] for signature in signatures]
    assert sorted(names) == sorted(mechanics.__all__), (
        "Each public helper needs exactly one user reference entry", names
    )
    for documented in signatures:
        name = documented.split("(", 1)[0]
        actual = name + str(inspect.signature(getattr(mechanics, name)))
        # Compare syntax trees to ignore inconsequential signature spacing.
        assert ast.dump(ast.parse(f"def {documented}: pass")) == ast.dump(
            ast.parse(f"def {actual}: pass")
        ), f"Stale signature for {name}: {documented}; expected {actual}"
