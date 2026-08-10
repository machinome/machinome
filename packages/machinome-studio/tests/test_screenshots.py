from __future__ import annotations

from io import BytesIO
import unittest

from PIL import Image

from floor.screenshots import _transparent_background


class TransparentBackgroundTest(unittest.TestCase):
    def test_only_edge_connected_pale_background_becomes_transparent(self) -> None:
        image = Image.new("RGB", (5, 5), (255, 254, 238))
        image.putpixel((2, 2), (255, 214, 37))
        # An enclosed pale pixel represents a deliberately light feature, not
        # canvas background, and must stay opaque.
        for x, y in ((1, 1), (1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2), (3, 3)):
            image.putpixel((x, y), (255, 214, 37))
        image.putpixel((2, 2), (250, 249, 230))
        raw = BytesIO()
        image.save(raw, "PNG")

        with Image.open(BytesIO(_transparent_background(raw.getvalue()))) as result:
            rgba = result.convert("RGBA")
        self.assertEqual(rgba.getpixel((0, 0))[3], 0)
        self.assertEqual(rgba.getpixel((1, 1)), (255, 214, 37, 255))
        self.assertEqual(rgba.getpixel((2, 2)), (250, 249, 230, 255))
