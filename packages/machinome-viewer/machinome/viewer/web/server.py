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
import subprocess
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Response, WebSocket
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect

from solid_node_viewer.bundle import (
    APP_DIR, api_version, app_build_path, bundle_path, has_bundle,
    missing_bundle_remedy,
)


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


class WebDevServer:
    """Run the development app's own npm server, proxied by :class:`WebViewer`.

    Only a source checkout has the app's sources and ``node_modules``; this is
    for working on the viewer itself, not for viewing a project.
    """

    def __init__(self, port=None):
        self.port = port if port is not None else frontend_port()
        self.app_dir = str(APP_DIR)

    def start(self):
        proc = subprocess.Popen(
            ['npm', 'run', 'start'], cwd=self.app_dir,
            env=dict(os.environ, PORT=str(self.port)),
        )
        proc.communicate()


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

        if dev:
            self._setup_proxy_server()
        else:
            self._setup_frontend_server()

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
            return FileResponse(candidate)

    def _setup_viewer_bundle(self):
        @self.app.get('/_viewer')
        async def get_viewer_status():
            available = has_bundle()
            return {
                'available': available,
                'apiVersion': api_version(),
                'remedy': None if available else missing_bundle_remedy(),
            }

        @self.app.get('/_viewer/bundle.js')
        async def get_viewer_bundle():
            if not has_bundle():
                return JSONResponse({
                    'remedy': missing_bundle_remedy(),
                }, status_code=503)
            return FileResponse(bundle_path(), media_type='application/javascript')

    def _setup_frontend_server(self):
        frontend_dir = app_build_path()
        if not frontend_dir.is_dir():
            # A source checkout that has not built the app. Say so on the
            # page rather than failing to start: the build routes, the
            # error surface and the bundle are still worth serving.
            @self.app.get('/')
            async def missing_app():
                return JSONResponse({
                    'remedy': f'Development app not built at {frontend_dir}. '
                              f'Build it with: cd {APP_DIR} && npm ci && '
                              'npm run build.',
                }, status_code=503)
            return

        @self.app.get('/')
        async def read_root():
            return FileResponse(frontend_dir / 'index.html')

        self.app.mount('/', StaticFiles(directory=frontend_dir), name='frontend')

    def _setup_proxy_server(self):
        @self.app.get('/')
        async def proxy_root():
            return await self._proxy('/')

        @self.app.get('/{path:path}')
        async def proxy_path(path: str):
            return await self._proxy('/' + path)

    async def _proxy(self, path: str):
        async with httpx.AsyncClient() as client:
            response = await client.request(
                'GET', f'http://localhost:{self.frontend}{path}')
        return Response(content=response.content,
                        media_type=response.headers.get('content-type'))
