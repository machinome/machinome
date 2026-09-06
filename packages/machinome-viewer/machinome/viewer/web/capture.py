# solid-node-viewer - the browser viewer for solid-node models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

"""Photograph a staged document through the viewer in a headless browser.

``solid snapshot --renderer web`` describes the node it is photographing in
a staging directory -- a ``viewer.json`` beside the model files it names --
and hands that directory to ``solid-node-viewer capture``. This module adds
the viewer bundle and a mount page to it, serves it over a loopback HTTP
server, opens it in headless Chromium and screenshots the canvas with the
background left transparent.

Everything about the node lives in the staged document. The options that
come in from the command line describe the photograph only: its size, the
animation instant, and the camera.
"""

import json
import os
import shutil
import threading
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from solid_node_viewer.bundle import (
    BUNDLE_NAME, bundle_path, has_bundle, missing_bundle_remedy,
)

PLAYWRIGHT_REMEDY = (
    "Install the browser renderer with "
    "`pip install 'solid-node-viewer[snapshot]'` and then download Chromium "
    "with `playwright install chromium`."
)

MOUNT_PAGE = 'index.html'
DOCUMENT = 'viewer.json'


class CaptureError(Exception):
    """The photograph could not be taken; the message names why."""


class _QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def mount_options(time=0.0, view=None, up=None, fov=None):
    """The options the mount page hands to the viewer.

    ``view`` is ``(eye, target)``, each a three-tuple; ``up`` a three-tuple;
    ``fov`` degrees. Absent camera options leave the viewer to frame the
    whole model itself.
    """
    options = {"animation": "external", "time": time}
    if view is not None:
        eye, target = view
        options["view"] = {"camera": list(eye), "target": list(target)}
    if up is not None:
        options["up"] = list(up)
    if fov is not None:
        options["fov"] = fov
    return options


class Capture:
    """One photograph of one staged document."""

    def __init__(self, staging):
        self.staging = staging

    def render(self, output, imgsize, options):
        """Photograph the staged document into ``output``.

        ``imgsize`` is ``(width, height)`` in pixels; ``options`` come from
        :func:`mount_options`.
        """
        self.assert_not_root()
        if not os.path.isfile(os.path.join(self.staging, DOCUMENT)):
            raise CaptureError(
                f"Staged document not found: "
                f"{os.path.join(self.staging, DOCUMENT)}"
            )
        self.add_viewer(options)
        self.capture(output, imgsize)

    def add_viewer(self, options):
        """Put the bundle and a mount page beside the staged document."""
        if not has_bundle():
            raise CaptureError(missing_bundle_remedy())
        shutil.copy2(bundle_path(), os.path.join(self.staging, BUNDLE_NAME))
        self.write_mount_page(options)

    def write_mount_page(self, options):
        payload = json.dumps(options)
        page = f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
html,body,#host{{margin:0;width:100%;height:100%;overflow:hidden;
background:transparent}}
canvas{{background:transparent}}
</style></head><body><div id="host"></div>
<script src="{BUNDLE_NAME}"></script><script>
SolidNodeWidget.mount('#host', '{DOCUMENT}', {payload}).then(() => {{
  requestAnimationFrame(() => requestAnimationFrame(() => {{
    document.body.dataset.ready = '1';
  }}));
}}).catch((error) => {{ document.body.dataset.error = String(error); }});
</script></body></html>"""
        with open(os.path.join(self.staging, MOUNT_PAGE), "w") as output:
            output.write(page)

    @contextmanager
    def serve(self):
        handler = partial(_QuietHandler, directory=self.staging)
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_address[1]}"
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def capture(self, output, imgsize):
        width, height = imgsize
        playwright = self.playwright()
        with self.serve() as base_url, playwright() as runtime:
            browser = self.launch(runtime.chromium)
            try:
                context = browser.new_context(
                    viewport={"width": width, "height": height},
                    device_scale_factor=1,
                )
                page = context.new_page()
                page.goto(f"{base_url}/{MOUNT_PAGE}")
                page.wait_for_function(
                    "document.body.dataset.ready || document.body.dataset.error"
                )
                error = page.locator("body").get_attribute("data-error")
                if error:
                    raise CaptureError(f"Browser viewer failed to mount: {error}")
                output_dir = os.path.dirname(os.path.abspath(output))
                os.makedirs(output_dir, exist_ok=True)
                # Clip a page screenshot to the canvas rather than
                # photographing the element: a large model keeps its canvas
                # moving after the mount resolves -- the viewer is still
                # framing it -- and Playwright's element screenshot waits for
                # the box to stop moving until it times out.
                canvas = page.locator("canvas").bounding_box()
                if canvas is None:
                    raise CaptureError("Browser viewer produced no canvas to photograph")
                page.screenshot(
                    path=output,
                    omit_background=True,
                    clip=canvas,
                    timeout=300_000,
                )
                context.close()
            finally:
                browser.close()

    def playwright(self):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as error:
            raise CaptureError(PLAYWRIGHT_REMEDY) from error
        return sync_playwright

    def launch(self, browser_type):
        try:
            return browser_type.launch(
                args=[
                    "--use-gl=angle",
                    "--use-angle=swiftshader",
                    "--enable-unsafe-swiftshader",
                ]
            )
        except Exception as error:
            if "Executable doesn't exist" in str(error):
                raise CaptureError(PLAYWRIGHT_REMEDY) from error
            raise

    def assert_not_root(self):
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            raise CaptureError(
                "The web renderer cannot run as root because Chromium cannot "
                "use its sandbox. Run the command as an unprivileged user."
            )
