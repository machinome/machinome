# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import json
import re
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProductIdentityTest(unittest.TestCase):
    def test_python_distribution_uses_machine_readable_identity(self) -> None:
        configuration = tomllib.loads((ROOT / "pyproject.toml").read_text())

        self.assertEqual(configuration["project"]["name"], "machinome-studio")
        self.assertIn("Machinome Studio", configuration["project"]["description"])

    def test_plugin_uses_machine_and_customer_facing_identities(self) -> None:
        plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
        marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())

        self.assertEqual(plugin["name"], "machinome-studio")
        self.assertEqual(plugin["displayName"], "Machinome Studio")
        self.assertIn("Machinome Studio", plugin["description"])
        self.assertEqual(marketplace["plugins"][0]["name"], "machinome-studio")
        self.assertIn("Machinome Studio", marketplace["plugins"][0]["description"])

    def test_browser_document_uses_customer_facing_identity(self) -> None:
        browser_document = (ROOT / "floor" / "frontend" / "index.html").read_text()

        self.assertIn("<title>Machinome Studio</title>", browser_document)

    def test_browser_document_links_the_studio_favicon(self) -> None:
        """The tab carries the studio's own favicon pack, versioned as the
        identity's application guide asks, because browsers cache favicons
        hard."""
        browser_document = (ROOT / "floor" / "frontend" / "index.html").read_text()

        self.assertIn(
            '<link rel="icon" href="/assets/favicon/favicon.svg?v=2" type="image/svg+xml" />',
            browser_document,
        )
        self.assertIn(
            '<link rel="icon" href="/assets/favicon/favicon.ico?v=2" sizes="16x16 32x32 48x48" />',
            browser_document,
        )
        self.assertIn(
            '<link rel="apple-touch-icon" href="/assets/favicon/favicon-180.png" />',
            browser_document,
        )

    def test_the_favicon_is_the_intact_symbol_on_a_black_plate(self) -> None:
        """The studio's favicon carries the identity symbol's path verbatim,
        white on a black plate, and ships every raster the links and the
        builder promise."""
        favicon = ROOT / "floor" / "frontend" / "public" / "assets" / "favicon"
        symbol = (ROOT / "floor" / "frontend" / "public" / "assets" / "brand" / "v1" / "mark-white.svg").read_text()
        svg = (favicon / "favicon.svg").read_text()

        path = re.search(r' d="([^"]+)"', symbol).group(1)
        self.assertIn(f' d="{path}"', svg)
        self.assertIn('<rect width="100" height="100" rx="24" fill="#000000"/>', svg)
        self.assertIn('fill="#FFFFFF"', svg)
        for name in ("favicon.ico", *(f"favicon-{size}.png" for size in (16, 32, 48, 64, 180, 192, 512))):
            self.assertTrue((favicon / name).is_file(), name)

    def test_the_brand_directory_is_the_complete_identity_release(self) -> None:
        """`brand/v1` is the identity's approved release copied intact: every
        asset its manifest lists is present, nothing else is, and the derived
        logo font travels with its licence."""
        brand = ROOT / "floor" / "frontend" / "public" / "assets" / "brand" / "v1"
        manifest = json.loads((brand / "manifest.json").read_text())

        self.assertEqual(manifest["version"], "1.0")
        self.assertEqual(manifest["identity"], "Machinome")
        self.assertEqual(manifest["colors"]["orange"], "#D94E32")
        present = sorted(
            str(path.relative_to(brand)) for path in brand.rglob("*") if path.is_file()
        )
        self.assertEqual(sorted(manifest["assets"] + ["manifest.json"]), present)
        self.assertIn("SIL OPEN FONT LICENSE", (brand / "fonts" / "OFL.txt").read_text())

    def test_interface_fonts_ship_with_their_notices(self) -> None:
        fonts = ROOT / "floor" / "frontend" / "public" / "assets" / "fonts"

        for font, notice in (
            ("SpaceGrotesk.ttf", "SpaceGrotesk-OFL.txt"),
            ("IBMPlexMono-Regular.ttf", "IBMPlexMono-OFL.txt"),
        ):
            self.assertTrue((fonts / font).is_file(), font)
            self.assertIn("SIL OPEN FONT LICENSE", (fonts / notice).read_text())

    def test_the_interface_wears_the_identity_and_keeps_the_logo_font_out_of_text(self) -> None:
        """Space Grotesk for the interface, IBM Plex Mono for the technical
        text, the accent a token; the wordmark and its `Studio` qualifier in
        the title bar; and the logo-only font never named as a text face, as
        the identity's application guide requires."""
        styles = (ROOT / "floor" / "frontend" / "src" / "styles.css").read_text()
        markup = (ROOT / "floor" / "frontend" / "src" / "main.tsx").read_text()

        self.assertIn('font-family: "Space Grotesk"', styles)
        self.assertIn('font-family: "IBM Plex Mono"', styles)
        self.assertIn("--machinome-orange: #D94E32", styles)
        self.assertNotIn("Machinome Logo", styles)
        self.assertNotIn("Machinome Logo", markup)
        self.assertNotIn("Inter,", styles)
        self.assertIn("--accent:", styles)
        self.assertIn('const WORDMARK = "/assets/brand/v1/wordmark-white.svg";', markup)
        self.assertEqual(markup.count('<img className="workspace-wordmark" src={WORDMARK} width="180" height="25" alt="" />'), 2)
        self.assertIn('<span className="workspace-qualifier">Studio</span>', markup)
        self.assertIn('aria-label="Machinome Studio"', markup)

    def test_chat_children_have_stable_grid_rows_when_failure_list_is_absent(self) -> None:
        styles = (ROOT / "floor" / "frontend" / "src" / "styles.css").read_text()

        self.assertIn(".conversation-header { grid-row: 1;", styles)
        self.assertIn(".role-failure-list { grid-row: 2;", styles)
        self.assertIn(".conversation-transcript { grid-row: 3;", styles)
        self.assertIn(".conversation-composer { grid-row: 4;", styles)

    def test_backend_integrations_use_product_derived_identity(self) -> None:
        opencode = (ROOT / "floor" / "backends" / "opencode.py").read_text()

        self.assertIn('f"{role}-{secrets.token_hex(6)}"', opencode)
        self.assertIn('prefix="machinome-studio-opencode-"', opencode)
        self.assertIn('f"Machinome Studio: {role}"', opencode)

    def test_setup_survives_a_relocated_workspace_virtualenv(self) -> None:
        setup = (ROOT / "scripts" / "setup").read_text()

        self.assertIn('"$VENV_PYTHON" -m pip', setup)
        self.assertNotIn('PIP="$VENV/bin/pip"', setup)


if __name__ == "__main__":
    unittest.main()
