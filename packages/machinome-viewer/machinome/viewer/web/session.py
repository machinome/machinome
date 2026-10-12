# machinome-viewer - the browser viewer for machinome models
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The development server in the framework's process: a session.

`machinome develop` asks the web viewer, through the seam `machinome.viewer`,
to serve the project's build directory. The session runs the development
server (`machinome.viewer.web.server`) in a thread this package owns, on a
port it binds before the thread starts, so a port another listener holds is
refused at once. It tells every open page that a build was published by
sending `reload` on the page's reload socket, which stays open and which the
page answers by fetching the build, and it stops the server when the command
ends. `machinome-viewer serve` keeps serving in the foreground, as before.
"""

import asyncio
import socket
import threading
import time

from machinome.viewer import ViewerError

#: The name of the thread the server runs in.
THREAD = 'machinome-viewer-web'

#: The address the server listens on, every interface, as
#: `machinome-viewer serve` listens.
HOST = '0.0.0.0'


class Session:
    """One development server, serving one build directory."""

    #: Seconds `start` waits for the server to listen, and `stop` for it to
    #: stop.
    TIMEOUT = 30.0

    def __init__(self, build_dir, port=None):
        import uvicorn
        from machinome.viewer.web.server import WebViewer, uvicorn_config

        self.viewer = WebViewer(build_dir, port=port)
        self.port = self.viewer.port
        # The loop is the thread's own, made by `asyncio.run` below: the
        # process's event loop policy is left as it is.
        self.server = uvicorn.Server(uvicorn.Config(
            self.viewer.app, host=HOST, port=self.port,
            log_config=uvicorn_config))
        self.loop = None
        self.thread = None

    def start(self):
        """Bind the port, start the server's thread and return once the
        server listens; raise `ViewerError` naming the port when it cannot
        be bound or the server stops first."""
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            listener.bind((HOST, self.port))
        except OSError as error:
            listener.close()
            raise ViewerError(
                f'the web viewer cannot serve on port {self.port}: '
                f'{error.strerror}') from None
        self.thread = threading.Thread(target=self._run, args=(listener,),
                                       name=THREAD, daemon=True)
        self.thread.start()
        deadline = time.monotonic() + self.TIMEOUT
        while not self.server.started:
            if not self.thread.is_alive():
                self.thread = None
                listener.close()
                raise ViewerError(
                    f'the web viewer stopped before it listened on port '
                    f'{self.port}')
            if time.monotonic() > deadline:
                self.stop()
                raise ViewerError(
                    f'the web viewer did not listen on port {self.port} '
                    f'within {self.TIMEOUT:.0f} s')
            time.sleep(0.005)
        return self

    def _run(self, listener):
        asyncio.run(self._serve(listener))

    async def _serve(self, listener):
        self.loop = asyncio.get_running_loop()
        await self.server.serve(sockets=[listener])

    def reload(self):
        """Send `reload` on every open page's reload socket, on the
        server's loop, and return once it is sent."""
        loop = self.loop
        if loop is None or self.thread is None or not self.viewer.sockets:
            return
        asyncio.run_coroutine_threadsafe(
            self.viewer.broadcast('reload'), loop).result(self.TIMEOUT)

    def stop(self):
        """Stop the server and return once its thread has ended."""
        if self.thread is None:
            return
        self.server.should_exit = True
        self.thread.join(self.TIMEOUT)
        self.thread = None
