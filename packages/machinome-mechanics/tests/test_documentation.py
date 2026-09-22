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


ROOT = Path(__file__).resolve().parents[1]

# The pages of the Machinome 0.7 manual this manual links to. A framework page
# renamed later fails here before a reader finds the dead link.
FRAMEWORK_PAGES = {
    "",
    "start/install.html",
    "concepts/relations.html",
    "concepts/values.html",
    "reference/assertions.html",
    "project/upgrading.html",
}

# Projects that motivated a helper during its cycle. Their evidence lives in
# the archived changes and workflow records; the reference describes the
# kind of machine instead.
CONSUMER_PROJECTS = (
    "Thor", "OpenTorque", "Open Robot Actuator", "Prusa", "Hangprinter",
    "Kossel", "Pascaline", "Deepseek", "InMoov", "OpenFlexure", "Snappy",
    "V8 project", "gearbox project", "3DPrintedClocks", "CycloidalDrive",
    "OpenCycloid", "Leonardo", "Spiderbot", "AlbertPro", "Dragon R1",
    "Strandbeest", "Metamaquina",
)


def reader_facing_pages():
    return sorted((ROOT / "docs").rglob("*.rst")) + [ROOT / "README.md"]


def test_the_manual_states_the_release():
    """0.1.0 is released with Machinome 0.7.0; nothing reader-facing says otherwise."""
    for page in reader_facing_pages():
        text = page.read_text().lower()
        for phrase in ("unreleased", "not published", "pending publication",
                       "awaiting publication", "in preparation for release"):
            assert phrase not in text, (page, phrase)
    changelog = (ROOT / "CHANGELOG.md").read_text()
    current = " ".join(re.split(r"^## ", changelog, flags=re.M)[1].split())
    assert current.startswith("0.1.0 — 20 September 2026"), current[:40]
    assert "Machinome 0.7.0" in current
    import tomllib
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    assert project["version"] == "0.1.0"
    assert "Machinome 0.7.0" in (ROOT / "README.md").read_text()


def test_the_manual_links_existing_framework_pages():
    links = set()
    for page in reader_facing_pages():
        links.update(re.findall(
            r"machinome\.readthedocs\.io/en/latest/([A-Za-z0-9_./-]*)", page.read_text()))
    assert links
    assert links <= FRAMEWORK_PAGES, sorted(links - FRAMEWORK_PAGES)


def test_the_reference_names_no_consumer_projects():
    named = {
        (page.name, project)
        for page in reader_facing_pages()
        for project in CONSUMER_PROJECTS
        if project in page.read_text()
    }
    assert not named, sorted(named)
