# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
"""The manual is a reader-facing part of the studio, pinned to its source.

These checks hold the shape the user-documentation spec describes: the
pages a reader is sent to, release facts derived from the package and
stated once, no publication caveat outside the status page, no project name
and no development checkout on a page that teaches, every launcher option
documented, sibling-manual links only to pages that exist, and a build that
imports nothing of the runtime.
"""

from __future__ import annotations

import ast
import re
import runpy
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

PAGES = (
    "index",
    "installation",
    "opening-a-project",
    "the-floor",
    "working-with-agents",
    "troubleshooting",
    "reference/cli",
    "reference/project-configuration",
    "reference/profiles",
    "project/status",
)

# Phrases that describe a publication state. They belong on the status page
# and nowhere a reader lands to learn how the studio works.
CAVEATS = re.compile(
    r"in preparation|not yet published|awaiting publication|"
    r"release preparation|still unpublished|is unreleased|unpublished|"
    r"not published|package index",
    re.IGNORECASE,
)
STATUS_PAGE = "project/status.rst"

# The projects the studio was exercised on. A reader learns nothing from a
# name and everything from the kind of machine; the names stay in the
# archived changes and the working record.
PROJECT_NAMES = re.compile(
    r"Pascaline|Curta|Kossel|Prusa|Hangprinter|Snappy|RepRap|InMoov|Inmoov|"
    r"AlbertPro|YouCanBuildDog|Strandbeest|3DPrintedClocks|OpenVMP|Don1|"
    r"\bThor\b|fender.bender|SpiderBot|Berkeley|\bAbacus\b|"
    r"\bprojects/[A-Za-z0-9]"
)

# A reader-facing page never mentions a worktree, a slot, or a sibling
# checkout: those are facts about a development workspace, not the package.
CHECKOUTS = re.compile(
    r"worktree|WTs/|\bslot\b|machinome-viewer/|machinome-mechanics/|"
    r"\bmolejo/|\.\./machinome|dev-env|sprint-\d"
)

# Sibling-manual pages this manual may link to. Each was opened in the
# sibling's built HTML before it was added here; add a target the same way.
SIBLING_LINKS = {
    "https://machinome.readthedocs.io/",
    "https://machinome.readthedocs.io/en/latest/start/install.html",
    "https://machinome-viewer.readthedocs.io/",
    "https://machinome-viewer.readthedocs.io/en/latest/using-the-viewer.html",
}
SIBLING_URL = re.compile(r"https://machinome(?:-viewer)?\.readthedocs\.io[^\s>`)]*")


def pages() -> list[tuple[str, str]]:
    return [
        (path.relative_to(DOCS).as_posix(), path.read_text())
        for path in sorted(DOCS.rglob("*.rst"))
        if "_build" not in path.parts
    ]


def module_docstrings() -> list[tuple[str, str]]:
    documents = []
    for module in sorted((ROOT / "floor").rglob("*.py")):
        docstring = ast.get_docstring(ast.parse(module.read_text())) or ""
        documents.append((module.relative_to(ROOT).as_posix(), docstring))
    return documents


def reader_facing() -> list[tuple[str, str]]:
    documents = pages()
    documents.append(("README.md", (ROOT / "README.md").read_text()))
    documents.append(("CHANGELOG.md", (ROOT / "CHANGELOG.md").read_text()))
    documents.extend(module_docstrings())
    return documents


def source_constant(module: str, name: str):
    tree = ast.parse((ROOT / module).read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
    raise AssertionError(f"{module} declares no {name}")


def conf() -> dict:
    return runpy.run_path(str(DOCS / "conf.py"))


class ManualShapeTest(unittest.TestCase):
    def test_every_page_exists_and_is_in_the_navigation(self) -> None:
        index = (DOCS / "index.rst").read_text()
        for page in PAGES:
            with self.subTest(page=page):
                self.assertTrue((DOCS / f"{page}.rst").is_file(), page)
                if page != "index":
                    self.assertIsNotNone(
                        re.search(rf"^\s+{re.escape(page)}\s*$", index, re.M),
                        f"{page} is not in the navigation",
                    )

    def test_manual_and_hosting_configuration_exist(self) -> None:
        for name in (
            "docs/conf.py", "docs/requirements.txt", ".readthedocs.yaml",
            "workflow/README.md", "workflow/documentation.md", "CHANGELOG.md",
        ):
            with self.subTest(name=name):
                self.assertTrue((ROOT / name).is_file(), name)

    def test_records_are_not_in_the_manual(self) -> None:
        self.assertFalse((DOCS / "shop-history.md").exists())
        self.assertFalse((DOCS / "foreman-listener.md").exists())
        self.assertTrue((ROOT / "workflow/archive/shop-history.md").is_file())
        self.assertTrue((ROOT / "workflow/foreman-listener.md").is_file())
        excluded = conf()["exclude_patterns"]
        for record in ("adrs", "design", "product"):
            with self.subTest(record=record):
                self.assertIn(record, excluded)

    def test_the_build_imports_nothing_of_the_runtime(self) -> None:
        text = (DOCS / "conf.py").read_text()
        self.assertNotRegex(text, r"^\s*(import|from)\s+floor\b", )
        for module in ("fastapi", "uvicorn", "watchdog", "tomlkit", "machinome"):
            with self.subTest(module=module):
                self.assertNotRegex(text, rf"^\s*(import|from)\s+{module}\b")

    def test_readthedocs_builds_from_requirements_alone(self) -> None:
        text = (ROOT / ".readthedocs.yaml").read_text()
        self.assertIn("requirements: docs/requirements.txt", text)
        self.assertIn("configuration: docs/conf.py", text)
        self.assertIn("fail_on_warning: true", text)
        for forbidden in ("pre_build", "apt_packages", "nodejs", "pip install", "submodules"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, text)

    def test_docs_extra_matches_requirements(self) -> None:
        project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
        requirements = (ROOT / "docs/requirements.txt").read_text().split()
        self.assertTrue(requirements)
        self.assertEqual(project["optional-dependencies"]["docs"], requirements)

    def test_the_package_describes_itself(self) -> None:
        docstring = ast.get_docstring(ast.parse((ROOT / "floor/__init__.py").read_text()))
        self.assertIn("Machinome Studio", docstring or "")
        self.assertIn("--projects-dir", docstring or "")


class ReleaseFactsTest(unittest.TestCase):
    def test_version_comes_from_the_package(self) -> None:
        project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
        namespace = conf()
        self.assertEqual(namespace["release"], project["version"])
        self.assertNotIn(project["version"], (DOCS / "conf.py").read_text())
        for relative, text in pages():
            with self.subTest(page=relative):
                self.assertNotIn(project["version"], text)

    def test_derived_facts_match_the_source(self) -> None:
        namespace = conf()
        self.assertEqual(
            namespace["required_viewer_api"],
            str(source_constant("floor/preparation.py", "REQUIRED_VIEWER_API")),
        )
        self.assertEqual(
            set(namespace["claude_models"]),
            source_constant("floor/preparation.py", "CLAUDE_MODELS"),
        )
        self.assertEqual(
            set(namespace["claude_efforts"]),
            source_constant("floor/preparation.py", "CLAUDE_EFFORTS"),
        )
        volume = source_constant("floor/build_package.py", "BUILD_VOLUME")
        self.assertEqual(namespace["build_volume"], " × ".join(map(str, volume)) + " mm")
        for name in (
            "machinome-version", "required-viewer-api", "claude-models",
            "claude-efforts", "build-volume",
        ):
            with self.subTest(substitution=name):
                self.assertIn(f".. |{name}| replace::", namespace["rst_prolog"])

    def test_pages_use_the_substitutions(self) -> None:
        namespace = conf()
        for relative, text in pages():
            with self.subTest(page=relative):
                self.assertNotIn(namespace["machinome_version"], text)
                self.assertNotIn(namespace["build_volume"], text)
                self.assertIsNone(re.search(r"API \d", text), "a literal viewer API number")
        index = (DOCS / "index.rst").read_text()
        for name in ("|release|", "|machinome-version|", "|required-viewer-api|"):
            with self.subTest(substitution=name):
                self.assertIn(name, index)
        self.assertIn("|build-volume|", (DOCS / "the-floor.rst").read_text())
        configuration = (DOCS / "reference/project-configuration.rst").read_text()
        self.assertIn("|claude-models|", configuration)
        self.assertIn("|claude-efforts|", configuration)

    def test_readme_and_changelog_state_the_version(self) -> None:
        project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
        namespace = conf()
        readme = (ROOT / "README.md").read_text()
        self.assertIn(f"Machinome Studio {project['version']}", readme)
        self.assertIn(f"Machinome {namespace['machinome_version']}", readme)
        self.assertIn("docs/project/status.rst", readme)
        self.assertIn("docs/index.rst", readme)
        changelog = (ROOT / "CHANGELOG.md").read_text()
        sections = re.split(r"^## ", changelog, flags=re.M)[1:]
        self.assertTrue(sections and sections[0].startswith("Unreleased"), changelog[:80])
        self.assertIn(f"Machinome Studio {project['version']}", sections[0])
        self.assertIn(f"Machinome {namespace['machinome_version']}", sections[0])


class CaveatTest(unittest.TestCase):
    def test_no_caveat_outside_the_status_page(self) -> None:
        for relative, text in reader_facing():
            if relative == STATUS_PAGE:
                continue
            with self.subTest(document=relative):
                found = CAVEATS.search(text)
                if found is not None:
                    self.fail(
                        f"{relative} says {found.group(0)!r}; "
                        "publication state belongs on the status page"
                    )

    def test_the_status_page_states_where_the_studio_stands(self) -> None:
        text = (DOCS / STATUS_PAGE).read_text()
        for needed in ("|release|", "|machinome-version|", "|required-viewer-api|", "clone", "Linux", "CHANGELOG.md"):
            with self.subTest(needed=needed):
                self.assertIn(needed, text)

    def test_no_project_name_or_checkout_on_a_reader_facing_page(self) -> None:
        for relative, text in reader_facing():
            with self.subTest(document=relative):
                found = PROJECT_NAMES.search(text)
                self.assertIsNone(found, f"{relative} names {found and found.group(0)!r}")
                found = CHECKOUTS.search(text)
                self.assertIsNone(found, f"{relative} mentions {found and found.group(0)!r}")

    def test_no_page_names_the_old_viewer_grant(self) -> None:
        for relative, text in reader_facing():
            with self.subTest(document=relative):
                self.assertNotIn("AGPL-3.0-only", text)


class ReferenceTest(unittest.TestCase):
    def test_codex_reference_matches_the_qualified_runtime(self) -> None:
        namespace = conf()
        self.assertEqual(namespace["codex_version"], source_constant("floor/codex_auth.py", "PINNED_VERSION"))
        self.assertEqual(set(namespace["codex_models"]), set(source_constant("floor/backends/codex_policy.py", "MODEL_FINGERPRINTS")))
        self.assertEqual(tuple(namespace["codex_efforts"]), source_constant("floor/backends/codex_policy.py", "EFFORTS"))
        configuration = (DOCS / "reference/project-configuration.rst").read_text()
        for value in ("codex:<model>", "|codex-models|", "|codex-efforts|", "medium"):
            self.assertIn(value, configuration)

    def test_codex_login_recovery_and_limits_are_documented(self) -> None:
        for page in ("installation.rst", "reference/cli.rst", "troubleshooting.rst"):
            with self.subTest(page=page):
                self.assertIn("python -m floor.codex_auth login", (DOCS / page).read_text())
        status = (DOCS / "project/status.rst").read_text()
        self.assertNotIn("Codex was retired", status)
        self.assertIn("|codex-version|", status)
        self.assertIn("Linux x86_64", status)
        self.assertIn("not an OS sandbox", (DOCS / "working-with-agents.rst").read_text())
        self.assertIn("never silently replaces", (DOCS / "troubleshooting.rst").read_text())

    def test_every_launcher_option_is_documented(self) -> None:
        reference = (DOCS / "reference/cli.rst").read_text()
        options: set[str] = set()
        for module in ("floor/__main__.py", "floor/orchestrator.py"):
            tree = ast.parse((ROOT / module).read_text())
            for node in ast.walk(tree):
                if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
                    continue
                if node.func.attr != "add_argument":
                    continue
                hidden = any(
                    keyword.arg == "help"
                    and isinstance(keyword.value, ast.Attribute)
                    and keyword.value.attr == "SUPPRESS"
                    for keyword in node.keywords
                )
                if hidden:
                    continue
                options.update(
                    argument.value for argument in node.args
                    if isinstance(argument, ast.Constant)
                    and isinstance(argument.value, str)
                    and argument.value.startswith("-")
                )
        self.assertTrue(options)
        for option in sorted(options):
            with self.subTest(option=option):
                self.assertIn(f"``{option}", reference)
        self.assertIn("FLOOR_PORT", reference)
        self.assertIn("python -m floor.orchestrator", reference)
        self.assertIn("python -m floor ", reference)

    def test_project_configuration_reference_names_the_table(self) -> None:
        page = (DOCS / "reference/project-configuration.rst").read_text()
        for needed in (
            "[tool.machinome-studio]", "[tool.machinome-studio.agents]",
            "libresolid-studio", "[tool.machinome]", "fordesmac",
        ):
            with self.subTest(needed=needed):
                self.assertIn(needed, page)

    def test_profiles_reference_matches_the_shipped_profiles(self) -> None:
        page = (DOCS / "reference/profiles.rst").read_text()
        for profile_dir in sorted(path for path in (ROOT / "profiles").iterdir() if path.is_dir()):
            profile = tomllib.loads((profile_dir / "profile.toml").read_text())
            with self.subTest(profile=profile_dir.name):
                self.assertIn(f"``{profile_dir.name}``", page)
                self.assertIn(profile["work_mode"], page)
            for agent in profile["agents"]:
                with self.subTest(profile=profile_dir.name, agent=agent["id"]):
                    row = f"* - ``{agent['id']}``"
                    self.assertIn(row, page)
                    window = page[page.index(row):page.index(row) + 700]
                    self.assertIn(agent["label"], window)
                    claude = agent["backends"]["claude"]
                    self.assertIn(f"``{claude['model']}``", window)
                    self.assertIn(claude["effort"], window)
                    for tool in claude["tools"]:
                        self.assertIn(f"``{tool}``", window)
                    prompt = (profile_dir / agent["prompt"]).read_text()
                    declared = re.search(r"^skills:\s*\[(.*)\]", prompt, re.M)[1]
                    for skill in filter(None, (name.strip() for name in declared.split(","))):
                        self.assertIn(f"``{skill}``", window)
        for capability in source_constant("floor/profiles.py", "_PROFILE_TOOLS"):
            with self.subTest(capability=capability):
                self.assertIn(f"``{capability}``", page)

    def test_sibling_links_are_verified_pages(self) -> None:
        seen = set()
        for relative, text in reader_facing():
            for url in SIBLING_URL.findall(text):
                url = url.rstrip(".,)")
                seen.add(url)
                with self.subTest(document=relative, url=url):
                    self.assertIn(url, SIBLING_LINKS)
        self.assertTrue(seen, "the manual links to no sibling manual")


if __name__ == "__main__":
    unittest.main()
