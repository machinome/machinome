from __future__ import annotations

import json
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProductIdentityTest(unittest.TestCase):
    def test_python_distribution_uses_machine_readable_identity(self) -> None:
        configuration = tomllib.loads((ROOT / "pyproject.toml").read_text())

        self.assertEqual(configuration["project"]["name"], "solid-node-studio")
        self.assertIn("SolidNode Studio", configuration["project"]["description"])

    def test_plugin_uses_machine_and_customer_facing_identities(self) -> None:
        plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
        marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())

        self.assertEqual(plugin["name"], "solid-node-studio")
        self.assertEqual(plugin["displayName"], "SolidNode Studio")
        self.assertIn("SolidNode Studio", plugin["description"])
        self.assertEqual(marketplace["plugins"][0]["name"], "solid-node-studio")
        self.assertIn("SolidNode Studio", marketplace["plugins"][0]["description"])

    def test_browser_document_uses_customer_facing_identity(self) -> None:
        browser_document = (ROOT / "floor" / "frontend" / "index.html").read_text()

        self.assertIn("<title>SolidNode Studio</title>", browser_document)

    def test_backend_integrations_use_product_derived_identity(self) -> None:
        codex = (ROOT / "floor" / "backends" / "codex.py").read_text()
        hermes = (ROOT / "floor" / "backends" / "hermes.py").read_text()
        opencode = (ROOT / "floor" / "backends" / "opencode.py").read_text()

        self.assertIn('"name": "solid-node-studio-orchestrator"', codex)
        self.assertIn('"title": "SolidNode Studio orchestrator"', codex)
        self.assertIn('f"solid-node-studio-{role}"', codex)
        self.assertIn('"name": "solid-node-studio-orchestrator"', hermes)
        self.assertIn('"title": "SolidNode Studio orchestrator"', hermes)
        self.assertIn('f"solid-node-studio-{secrets.token_hex(6)}"', opencode)
        self.assertIn('prefix="solid-node-studio-opencode-"', opencode)
        self.assertIn('f"SolidNode Studio: {role}"', opencode)

    def test_setup_survives_a_relocated_workspace_virtualenv(self) -> None:
        setup = (ROOT / "scripts" / "setup").read_text()

        self.assertIn('"$VENV_PYTHON" -m pip', setup)
        self.assertNotIn('PIP="$VENV/bin/pip"', setup)


if __name__ == "__main__":
    unittest.main()
