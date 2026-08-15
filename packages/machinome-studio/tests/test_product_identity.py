from __future__ import annotations

import json
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProductIdentityTest(unittest.TestCase):
    def test_python_distribution_uses_machine_readable_identity(self) -> None:
        configuration = tomllib.loads((ROOT / "pyproject.toml").read_text())

        self.assertEqual(configuration["project"]["name"], "libresolid-studio")
        self.assertIn("LibreSolid Studio", configuration["project"]["description"])

    def test_plugin_uses_machine_and_customer_facing_identities(self) -> None:
        plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
        marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())

        self.assertEqual(plugin["name"], "libresolid-studio")
        self.assertEqual(plugin["displayName"], "LibreSolid Studio")
        self.assertIn("LibreSolid Studio", plugin["description"])
        self.assertEqual(marketplace["plugins"][0]["name"], "libresolid-studio")
        self.assertIn("LibreSolid Studio", marketplace["plugins"][0]["description"])

    def test_browser_document_uses_customer_facing_identity(self) -> None:
        browser_document = (ROOT / "floor" / "frontend" / "index.html").read_text()

        self.assertIn("<title>LibreSolid Studio</title>", browser_document)

    def test_chat_children_have_stable_grid_rows_when_failure_list_is_absent(self) -> None:
        styles = (ROOT / "floor" / "frontend" / "src" / "styles.css").read_text()

        self.assertIn(".conversation-header { grid-row: 1;", styles)
        self.assertIn(".role-failure-list { grid-row: 2;", styles)
        self.assertIn(".conversation-transcript { grid-row: 3;", styles)
        self.assertIn(".conversation-composer { grid-row: 4;", styles)

    def test_backend_integrations_use_product_derived_identity(self) -> None:
        opencode = (ROOT / "floor" / "backends" / "opencode.py").read_text()

        self.assertIn('f"{role}-{secrets.token_hex(6)}"', opencode)
        self.assertIn('prefix="libresolid-studio-opencode-"', opencode)
        self.assertIn('f"LibreSolid Studio: {role}"', opencode)

    def test_setup_survives_a_relocated_workspace_virtualenv(self) -> None:
        setup = (ROOT / "scripts" / "setup").read_text()

        self.assertIn('"$VENV_PYTHON" -m pip', setup)
        self.assertNotIn('PIP="$VENV/bin/pip"', setup)


if __name__ == "__main__":
    unittest.main()
