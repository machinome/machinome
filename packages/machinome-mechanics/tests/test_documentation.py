"""Keep the helpers' pages in the Machinome manual complete and running.

The pages are the framework manual's (change `join-mechanics`): the
reference section `reference/mechanics/` and the how-to
`howto/mechanism-formulas`, whose example project sits beside it. These
tests hold them to the package: one reference entry per export with its
actual signature, links inside the manual, and every example run.
"""

import ast
import doctest
import inspect
from pathlib import Path
import re
import sys
import tomllib

import machinome.mechanics as mechanics


PACKAGE = Path(__file__).resolve().parents[1]
REPOSITORY = Path(__file__).resolve().parents[3]
DOCS = REPOSITORY / "packages" / "machinome" / "docs"
SECTION = DOCS / "reference" / "mechanics"
HOWTO = DOCS / "howto" / "mechanism-formulas.rst"
EXAMPLES = DOCS / "howto" / "mechanism-formulas"

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

# The flags Sphinx's doctest builder runs examples under by default.
SPHINX_DOCTEST_FLAGS = (doctest.ELLIPSIS | doctest.IGNORE_EXCEPTION_DETAIL
                        | doctest.DONT_ACCEPT_TRUE_FOR_1)


def manual_pages():
    """The section's pages and the how-to."""
    return sorted(SECTION.glob("*.rst")) + [HOWTO]


def reader_facing_pages():
    return (manual_pages() + [PACKAGE / "README.md"]
            + sorted((PACKAGE / "machinome" / "mechanics").glob("*.py")))


def test_every_export_has_one_reference_with_the_actual_signature():
    signatures = [
        signature
        for page in SECTION.glob("*.rst")
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


def test_the_changelog_states_the_release():
    """0.1.0 is released with Machinome 0.7.0; the README states no version."""
    changelog = (PACKAGE / "CHANGELOG.md").read_text()
    # The newest release section; the work since it sits under one
    # "Unreleased" section at the top until a release renames that heading.
    sections = re.split(r"^## ", changelog, flags=re.M)[1:]
    assert [section for section in sections
            if section.startswith("Unreleased")] in ([], sections[:1])
    current = next(" ".join(section.split()) for section in sections
                   if not section.startswith("Unreleased"))
    assert current.startswith("0.1.0"), current[:40]
    assert "23 September 2026" in current.partition(" ### ")[0][:40]
    assert "Machinome 0.7.0" in current
    project = tomllib.loads((PACKAGE / "pyproject.toml").read_text())["project"]
    assert project["version"] == current.split()[0]
    readme = (PACKAGE / "README.md").read_text()
    assert not re.search(r"(?<![\w.-])\d+\.\d+(?:\.\d+)?", readme), readme


def test_no_reader_page_states_a_publication_caveat():
    for page in reader_facing_pages():
        text = page.read_text().lower()
        for phrase in ("unreleased", "not published", "pending publication",
                       "awaiting publication", "in preparation for release"):
            assert phrase not in text, (page, phrase)


def test_the_pages_link_inside_the_manual():
    for page in manual_pages() + sorted(
            (PACKAGE / "machinome" / "mechanics").glob("*.py")):
        assert "readthedocs.io" not in page.read_text(), page
    readme = (PACKAGE / "README.md").read_text()
    assert re.findall(r"https?://[^\s>)]*readthedocs\.io[^\s>)]*", readme) == [
        "https://machinome.readthedocs.io"]


def test_the_reference_names_no_consumer_projects():
    """Manual pages and the docstrings help() shows describe machines by kind."""
    named = {
        (page.name, project)
        for page in reader_facing_pages()
        for project in CONSUMER_PROJECTS + ("projects/",)
        if project in page.read_text()
    }
    assert not named, sorted(named)


def test_every_example_in_the_manual_runs(monkeypatch):
    """Every `>>>` example of the pages runs as Sphinx's doctest builder
    would, the how-to's example project on the path."""
    monkeypatch.syspath_prepend(str(EXAMPLES))
    attempted = {}
    for page in manual_pages():
        result = doctest.testfile(str(page), module_relative=False,
                                  optionflags=SPHINX_DOCTEST_FLAGS,
                                  verbose=False, report=True)
        assert result.failed == 0, (page.name, result)
        attempted[page.name] = result.attempted
    assert all(count > 0 for name, count in attempted.items()
               if name != "index.rst"), attempted
