# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""The studio's pages are part of the Machinome manual, pinned to its source.

The studio's manual folds into the framework's (change ``join-studio``):
three how-to guides, ``howto/open-a-studio-project``,
``howto/studio-workspace`` and ``howto/studio-agents``, and the reference
section ``reference/studio/``, built with the manual from
``packages/machinome/docs/``. The package keeps its changelog and its
working record; it carries no manual of its own. These checks hold what the
pages state to the package: the release facts the manual's configuration
declares equal the source constants they state, every launcher option and
configuration key is documented, the command is ``machinome studio``, and no
page a reader lands on names a catalogue project, a development checkout, the
former launcher or the former module.
"""

from __future__ import annotations

import ast
import re
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = Path(__file__).resolve().parents[3]
MANUAL = REPOSITORY / "packages" / "machinome" / "docs"
PACKAGE = ROOT / "machinome" / "studio"

PAGES = (
    "howto/open-a-studio-project.rst",
    "howto/studio-workspace.rst",
    "howto/studio-agents.rst",
    "reference/studio/index.rst",
    "reference/studio/command.rst",
    "reference/studio/project-configuration.rst",
    "reference/studio/profiles.rst",
    "reference/studio/troubleshooting.rst",
)

# Phrases that describe a publication state. They belong on the framework's
# status page and nowhere a reader lands to learn how the studio works.
CAVEATS = re.compile(
    r"in preparation|not yet published|awaiting publication|"
    r"release preparation|still unpublished|is unreleased|unpublished|"
    r"not published|package index",
    re.IGNORECASE,
)

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

# The ways the studio was run before it joined the repository: its console
# script, its former module, its setup script, its checkout's paths and its
# former repository. The command is ``machinome studio``.
FORMER = re.compile(
    r"python -m floor|\$ machinome-studio|machinome-studio --|"
    r"``machinome-studio \[|scripts/setup|floor/static|floor/frontend|"
    r"npm --prefix|github\.com/machinome/machinome-studio"
)


def page(name: str) -> str:
    return (MANUAL / name).read_text()


def pages() -> list[tuple[str, str]]:
    return [(name, page(name)) for name in PAGES]


def module_docstrings() -> list[tuple[str, str]]:
    documents = []
    for module in sorted(PACKAGE.rglob("*.py")):
        if "frontend" in module.relative_to(PACKAGE).parts:
            continue
        docstring = ast.get_docstring(ast.parse(module.read_text())) or ""
        documents.append((module.relative_to(ROOT).as_posix(), docstring))
    return documents


def reader_facing() -> list[tuple[str, str]]:
    documents = pages()
    documents.append(("README.md", (ROOT / "README.md").read_text()))
    documents.extend(module_docstrings())
    return documents


def source_constant(module: str, name: str):
    tree = ast.parse((PACKAGE / module).read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
    raise AssertionError(f"{module} declares no {name}")


def conf_literal(name: str):
    """A literal the manual's configuration assigns at its top level, read
    without running it."""
    tree = ast.parse((MANUAL / "conf.py").read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
    raise AssertionError(f"docs/conf.py assigns no {name}")


class ManualShapeTest(unittest.TestCase):
    def test_the_pages_are_in_the_manual(self) -> None:
        for name in PAGES:
            with self.subTest(page=name):
                self.assertTrue((MANUAL / name).is_file(), name)
        for name in ("docs", ".readthedocs.yaml"):
            with self.subTest(absent=name):
                self.assertFalse((ROOT / name).exists(), name)
        for name in ("workflow/README.md", "workflow/documentation.md", "CHANGELOG.md"):
            with self.subTest(name=name):
                self.assertTrue((ROOT / name).is_file(), name)

    def test_the_pages_are_in_the_navigation(self) -> None:
        index = (MANUAL / "index.rst").read_text()
        for entry in ("howto/open-a-studio-project", "howto/studio-workspace",
                      "howto/studio-agents", "reference/studio/index"):
            with self.subTest(entry=entry):
                self.assertRegex(index, rf"(?m)^\s+{re.escape(entry)}\s*$")
        section = page("reference/studio/index.rst")
        for entry in ("command", "project-configuration", "profiles", "troubleshooting"):
            with self.subTest(section=entry):
                self.assertRegex(section, rf"(?m)^\s+{entry}\s*$")

    def test_records_are_not_in_the_manual(self) -> None:
        self.assertTrue((ROOT / "workflow/archive/shop-history.md").is_file())
        self.assertTrue((ROOT / "workflow/foreman-listener.md").is_file())
        self.assertTrue((ROOT / "workflow/adrs/README.md").is_file())
        for name in ("shop-history.md", "foreman-listener.md", "architecture-overview.md"):
            with self.subTest(record=name):
                self.assertEqual(list(MANUAL.rglob(name)), [])
        for name in ("design", "product", "spikes"):
            with self.subTest(record=name):
                self.assertTrue((ROOT / "workflow" / name).is_dir(), name)
                self.assertFalse((MANUAL / name).exists(), name)

    def test_the_manual_imports_nothing_of_the_studio(self) -> None:
        text = (MANUAL / "conf.py").read_text()
        self.assertNotRegex(text, r"(?m)^\s*(import|from)\s+(floor|machinome\.studio)\b")

    def test_the_package_declares_no_manual_of_its_own(self) -> None:
        project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
        self.assertNotIn("docs", project.get("optional-dependencies", {}))
        self.assertEqual(project["urls"], {"Homepage": "https://github.com/machinome/machinome"})

    def test_the_package_describes_itself(self) -> None:
        docstring = ast.get_docstring(ast.parse((PACKAGE / "__init__.py").read_text())) or ""
        self.assertIn("Machinome Studio", docstring)
        self.assertIn("machinome studio", docstring)


class ReleaseFactsTest(unittest.TestCase):
    def test_the_studio_is_numbered_with_the_manual(self) -> None:
        project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
        self.assertEqual(conf_literal("release"), project["version"])
        for relative, text in pages():
            with self.subTest(page=relative):
                self.assertNotIn(project["version"], text)

    def test_the_stated_facts_are_the_source_s(self) -> None:
        facts = {
            "studio_viewer_api": str(source_constant("preparation.py", "REQUIRED_VIEWER_API")),
            "studio_codex_version": source_constant("codex_auth.py", "PINNED_VERSION"),
            "studio_codex_efforts": source_constant("backends/codex_policy.py", "EFFORTS"),
            "studio_build_volume": " × ".join(map(str, source_constant("build_package.py", "BUILD_VOLUME"))) + " mm",
        }
        for name, value in facts.items():
            with self.subTest(fact=name):
                self.assertEqual(conf_literal(name), value)
        sets = {
            "studio_claude_models": source_constant("preparation.py", "CLAUDE_MODELS"),
            "studio_claude_efforts": source_constant("preparation.py", "CLAUDE_EFFORTS"),
            "studio_codex_models": set(source_constant("backends/codex_policy.py", "MODEL_FINGERPRINTS")),
        }
        for name, value in sets.items():
            with self.subTest(fact=name):
                self.assertEqual(set(conf_literal(name)), value)
        conf = (MANUAL / "conf.py").read_text()
        for name in (*facts, *sets):
            with self.subTest(substitution=name):
                self.assertIn(f".. |{name}| replace::", conf)

    def test_pages_use_the_substitutions(self) -> None:
        volume = conf_literal("studio_build_volume")
        for relative, text in pages():
            with self.subTest(page=relative):
                self.assertNotIn(volume, text)
                self.assertIsNone(re.search(r"API \d", text), "a literal viewer API number")
                self.assertNotIn("|machinome-version|", text)
        index = page("reference/studio/index.rst")
        for name in ("|release|", "|studio_viewer_api|"):
            with self.subTest(substitution=name):
                self.assertIn(name, index)
        self.assertIn("|studio_build_volume|", page("howto/studio-workspace.rst"))
        configuration = page("reference/studio/project-configuration.rst")
        self.assertIn("|studio_claude_models|", configuration)
        self.assertIn("|studio_claude_efforts|", configuration)

    def test_the_changelog_records_the_join(self) -> None:
        changelog = (ROOT / "CHANGELOG.md").read_text()
        sections = re.split(r"^## ", changelog, flags=re.M)[1:]
        self.assertTrue(sections and sections[0].startswith("Unreleased"), changelog[:80])
        unreleased = " ".join(sections[0].split())
        self.assertIn("### Joined to the Machinome repository", sections[0])
        self.assertIn("numbered with Machinome", unreleased)
        self.assertIn("`machinome studio`", unreleased)


class CaveatTest(unittest.TestCase):
    def test_no_caveat_on_a_reader_facing_page(self) -> None:
        for relative, text in reader_facing():
            with self.subTest(document=relative):
                found = CAVEATS.search(text)
                if found is not None:
                    self.fail(
                        f"{relative} says {found.group(0)!r}; "
                        "publication state belongs on the framework's status page"
                    )

    def test_the_section_states_where_the_studio_stands(self) -> None:
        text = " ".join(page("reference/studio/index.rst").split())
        for needed in ("``machinome-studio``", '``machinome[studio]``', "``machinome studio``",
                       "|studio_viewer_api|", "Linux"):
            with self.subTest(needed=needed):
                self.assertIn(needed, text)
        status = " ".join((MANUAL / "project/status.rst").read_text().split())
        self.assertIn("``machinome-studio``", status)
        self.assertIn("experimental", status)

    def test_no_project_name_or_checkout_on_a_reader_facing_page(self) -> None:
        for relative, text in reader_facing():
            with self.subTest(document=relative):
                found = PROJECT_NAMES.search(text)
                self.assertIsNone(found, f"{relative} names {found and found.group(0)!r}")
                found = CHECKOUTS.search(text)
                self.assertIsNone(found, f"{relative} mentions {found and found.group(0)!r}")

    def test_no_page_runs_the_studio_the_former_way(self) -> None:
        for relative, text in reader_facing():
            with self.subTest(document=relative):
                found = FORMER.search(text)
                self.assertIsNone(found, f"{relative} says {found and found.group(0)!r}")
        # A page of the manual links its siblings with :doc:, never a URL.
        for relative, text in pages():
            with self.subTest(page=relative):
                self.assertNotIn("readthedocs.io", text)


class ReferenceTest(unittest.TestCase):
    def test_hub_documents_all_supported_backends_as_detection_only(self) -> None:
        text = page("howto/open-a-studio-project.rst")
        self.assertIn("Claude Code, OpenCode and Codex", text)
        self.assertIn("detected", text)
        self.assertIn("does not qualify it", text)

    def test_codex_reference_matches_the_qualified_runtime(self) -> None:
        configuration = page("reference/studio/project-configuration.rst")
        for value in ("codex:<model>", "|studio_codex_models|", "|studio_codex_efforts|", "medium"):
            with self.subTest(value=value):
                self.assertIn(value, configuration)

    def test_codex_login_recovery_and_limits_are_documented(self) -> None:
        for name in ("howto/studio-agents.rst", "reference/studio/command.rst",
                     "reference/studio/troubleshooting.rst"):
            with self.subTest(page=name):
                self.assertIn("python -m machinome.studio.codex_auth login", page(name))
        status = page("reference/studio/index.rst")
        self.assertNotIn("Codex was retired", status)
        self.assertIn("|studio_codex_version|", status)
        self.assertIn("Linux x86_64", status)
        self.assertIn("not an OS sandbox", page("howto/studio-agents.rst"))
        self.assertIn("never silently replaces", page("reference/studio/troubleshooting.rst"))

    def test_every_launcher_option_is_documented(self) -> None:
        reference = page("reference/studio/command.rst")
        options: set[str] = set()
        for module in ("__main__.py", "orchestrator.py", "cli.py"):
            tree = ast.parse((PACKAGE / module).read_text())
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
        for needed in ("FLOOR_PORT", "machinome studio [--projects-dir PATH] [--port PORT]",
                       "python -m machinome.studio.orchestrator", "python -m machinome.studio "):
            with self.subTest(needed=needed):
                self.assertIn(needed, reference)

    def test_the_configuration_file_is_documented(self) -> None:
        reference = page("reference/studio/command.rst")
        for needed in ("machinome-studio", "MACHINOME_STUDIO_CONFIG", "config.toml", "[studio]"):
            with self.subTest(needed=needed):
                self.assertIn(needed, reference)
        for key in source_constant("launcher.py", "STUDIO_KEYS"):
            with self.subTest(key=key):
                self.assertIn(key, reference)

    def test_pages_that_start_the_hub_show_the_command(self) -> None:
        for name, text in (
            ("howto/open-a-studio-project.rst", page("howto/open-a-studio-project.rst")),
            ("README.md", (ROOT / "README.md").read_text()),
        ):
            with self.subTest(page=name):
                self.assertIn("machinome studio --projects-dir", text)

    def test_project_configuration_reference_names_the_table(self) -> None:
        text = page("reference/studio/project-configuration.rst")
        for needed in (
            "[tool.machinome-studio]", "[tool.machinome-studio.agents]",
            "libresolid-studio", "[tool.machinome]", "openspec-builder", "fordesmac",
        ):
            with self.subTest(needed=needed):
                self.assertIn(needed, text)

    def test_profiles_reference_matches_the_shipped_profiles(self) -> None:
        text = page("reference/studio/profiles.rst")
        for profile_dir in sorted(path for path in (PACKAGE / "profiles").iterdir() if path.is_dir()):
            profile = tomllib.loads((profile_dir / "profile.toml").read_text())
            with self.subTest(profile=profile_dir.name):
                heading = re.compile(rf"^``{re.escape(profile_dir.name)}``\n=+$", re.M)
                self.assertRegex(
                    text, heading,
                    f"{profile_dir.name!r} must have its own section heading, "
                    "not merely a mention",
                )
                self.assertIn(profile["work_mode"], text)
            for agent in profile["agents"]:
                with self.subTest(profile=profile_dir.name, agent=agent["id"]):
                    row = f"* - ``{agent['id']}``"
                    self.assertIn(row, text)
                    window = text[text.index(row):text.index(row) + 700]
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
        for capability in source_constant("profiles.py", "_PROFILE_TOOLS"):
            with self.subTest(capability=capability):
                self.assertIn(f"``{capability}``", text)

    def test_the_readme_sends_the_reader_to_the_manual(self) -> None:
        readme = (ROOT / "README.md").read_text()
        self.assertIn("<https://machinome.readthedocs.io>", readme)


if __name__ == "__main__":
    unittest.main()
