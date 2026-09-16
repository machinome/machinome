# solid-node-viewer - the browser viewer for solid-node models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only

"""The development server: a published build in front of the viewer.

``solid develop`` publishes a project's build directory -- ``viewer.json``,
the model files it names and ``errors.json`` when a build fails -- and
launches this server on it as a separate process. The server knows the
build only as a directory: it never imports project source, never waits for
an artifact, and stays up whether or not a build has been published, so the
browser can keep polling the error surface and reconnecting the reload
socket while the maker fixes their code.
"""

import json
import logging
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import FileResponse, JSONResponse
from starlette.websockets import WebSocketDisconnect

from solid_node_viewer.bundle import (
    BundleStale, api_version, bundle_path, develop_page_path, has_bundle,
    missing_bundle_remedy,
)
from solid_node_viewer.currency import ensure_current


logger = logging.getLogger('viewer.server')

DEFAULT_PORT = 8000
DEFAULT_FRONTEND_PORT = 3000

uvicorn_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "access": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelname)5s - %(name)15s - %(message)s",
            "use_colors": True,
        },
    },
    "handlers": {
        "default": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.access": {"handlers": ["default"], "level": "INFO", "propagate": False},
    },
}


def backend_port():
    """The port the server listens on: ``SOLID_NODE_PORT`` or 8000."""
    return int(os.environ.get('SOLID_NODE_PORT', DEFAULT_PORT))


def frontend_port():
    """The npm dev server port: ``SOLID_NODE_FRONTEND_PORT`` or 3000."""
    return int(os.environ.get('SOLID_NODE_FRONTEND_PORT', DEFAULT_FRONTEND_PORT))


class WebViewer:
    """Serve one published build directory and the installed viewer bundle."""

    def __init__(self, build_dir, dev=False, port=None, frontend=None):
        self.build_dir = Path(build_dir)
        self.port = port if port is not None else backend_port()
        self.frontend = frontend if frontend is not None else frontend_port()
        self.app = FastAPI()

        self._setup_build_error()
        self._setup_build_snapshot()
        self._setup_viewer_bundle()
        self._setup_reload_websocket()
        # The development page is a static file this package carries
        # (design D13); `dev` no longer selects between it and a proxied
        # npm dev server (design D14 -- there is no longer a second
        # frontend process to proxy to). Kept as a constructor parameter
        # so `cli.py` goes on accepting `--dev`/`--start-frontend`
        # harmlessly for a released framework.
        self._setup_development_page()

    def start(self):
        logger.info('START - will listen on port %s', self.port)
        uvicorn.run(self.app, host='0.0.0.0', port=self.port,
                    log_config=uvicorn_config)

    def errors_file(self):
        return self.build_dir / 'errors.json'

    def _setup_reload_websocket(self):
        @self.app.websocket('/ws/reload')
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            await websocket.send_text('reload')
            try:
                while True:
                    await websocket.receive_text()
            except WebSocketDisconnect:
                return

    def _setup_build_error(self):
        @self.app.get('/_build_error')
        async def get_status():
            errors_file = self.errors_file()
            if errors_file.exists():
                with open(errors_file, 'r') as stream:
                    return JSONResponse(json.load(stream))
            return JSONResponse({})

    def _setup_build_snapshot(self):
        @self.app.get('/build/{requested_path:path}')
        async def get_build_file(requested_path: str):
            build_dir = self.build_dir.resolve()
            candidate = (build_dir / requested_path).resolve()
            try:
                candidate.relative_to(build_dir)
            except ValueError:
                raise HTTPException(status_code=404)
            if not candidate.is_file():
                raise HTTPException(
                    status_code=404, detail='Published build artifact not found')
            # Never cached: the widget re-fetches a republished document
            # with a plain fetch(), and a browser's heuristic freshness
            # would hand it the previous one for a while.
            return FileResponse(candidate, headers={'Cache-Control': 'no-store'})

    def _setup_viewer_bundle(self):
        # ADR-059: currency is checked PER REQUEST, not once at start.
        # This is the surface a developer keeps open across edits -- the
        # whole point of `solid develop` -- so a reload must serve what
        # they just wrote. The check is a newest-mtime scan of the build
        # inputs (a median 2.88 ms over 77 files) and the response is one
        # per page load, so this is free; the rebuild it may trigger is
        # ~0.35 s, and only when something actually changed.
        def current_or_remedy():
            """`None` when the bundle can be served, or why it cannot."""
            if not has_bundle():
                return missing_bundle_remedy()
            try:
                ensure_current()
            except BundleStale as error:
                logger.warning('refusing to serve a stale viewer bundle: %s', error)
                return str(error)
            return None

        @self.app.get('/_viewer')
        async def get_viewer_status():
            remedy = current_or_remedy()
            return {
                'available': remedy is None,
                'apiVersion': api_version(),
                'remedy': remedy,
            }

        @self.app.get('/_viewer/bundle.js')
        async def get_viewer_bundle():
            remedy = current_or_remedy()
            if remedy is not None:
                return JSONResponse({'remedy': remedy}, status_code=503)
            return FileResponse(bundle_path(), media_type='application/javascript')

    def _setup_development_page(self):
        page = develop_page_path()

        @self.app.get('/')
        async def read_root():
            # A defensive route for the file being absent (design D13):
            # it can only mean a broken installation, but answering 503
            # with the file's own path is cheaper than a FileResponse
            # raising inside uvicorn, and every other route -- the
            # build, bundle and error surfaces -- stays available.
            if not page.is_file():
                return JSONResponse({
                    'remedy': f'Development page not found at {page}. This '
                              'installation is missing a package file.',
                }, status_code=503)
            return FileResponse(page)
