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

A document carrying a mechanical program is photographed at its REST
STATE: the run is created and never started, so no step of it is taken
and the program's clock name resolves to zero, which is the instant the
rest state is defined at. An animation instant means nothing to such a
document -- it publishes no animation cycle -- so a non-zero ``--time``
on one is refused by name before any browser starts. A still of a state
the machine reached is a different picture and is not offered here.
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


def carries_program(document):
    """Whether a staged document carries a compiled mechanical program.

    Version 5 is version 4 plus ``program``; a document declaring the
    running version must carry one, whether or not the key is there,
    which is the first thing the widget's loader refuses.
    """
    if not isinstance(document, dict):
        return False
    return document.get("program") is not None or document.get("version") == 5


def mount_options(time=0.0, view=None, up=None, fov=None):
    """The options the mount page hands to the viewer.

    ``view`` is ``(eye, target)``, each a three-tuple; ``up`` a three-tuple;
    ``fov`` degrees. Absent camera options leave the viewer to frame the
    whole model itself.

    The on-screen chrome is suppressed, for a posed document and a
    running one alike: a photograph is of the model, and a control panel
    drawn over the canvas would be in the picture -- opaque pixels where
    the transparent background promises there are none.

    The PART affordance is suppressed with it: a still photograph is the
    last place a hover cursor or a highlight should be able to appear.
    This capture publishes no ``controls`` table at all (solid-node
    ADR-112 §6), so it can never matter -- belt and braces.
    """
    options = {"animation": "external", "time": time,
               "driverControls": "none", "partControls": "none"}
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
        document = self.staged_document()
        self.assert_instant(document, options)
        self.add_viewer(options)
        self.capture(output, imgsize)

    def staged_document(self):
        """The staged ``viewer.json``, or a refusal naming what is
        missing. Read before anything is copied or started."""
        path = os.path.join(self.staging, DOCUMENT)
        if not os.path.isfile(path):
            raise CaptureError(f"Staged document not found: {path}")
        try:
            with open(path) as handle:
                return json.load(handle)
        except ValueError as error:
            raise CaptureError(
                f"Staged document is not readable JSON: {path}: {error}"
            ) from error

    def assert_instant(self, document, options):
        """Refuse an animation instant a running document cannot have.

        Before any browser starts, which is the posture this capability
        already takes toward everything it cannot do.
        """
        time = options.get("time", 0.0)
        if not time or not carries_program(document):
            return
        raise CaptureError(
            f"--time {time} means nothing to a staged document carrying a "
            "mechanical program: a running document publishes no animation "
            "cycle, so honouring an instant would photograph the rest state "
            "while claiming another. Photograph the rest state with "
            "--time 0, which is the default. A still of a state the machine "
            "reached is a different picture and is not offered here."
        )

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
SolidNodeWidget.mount('#host', '{DOCUMENT}', {payload}).then((viewer) => {{
  requestAnimationFrame(() => requestAnimationFrame(() => {{
    var run = viewer.run();
    if (run) {{
      // The instant this picture was taken at. A run is created paused
      // and nothing here starts it, so a document carrying a program is
      // photographed at its rest state.
      document.body.dataset.tick = String(run.tick());
      document.body.dataset.clock = String(run.elapsed());
      document.body.dataset.state = JSON.stringify(run.state());
    }}
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
