==================
The viewer command
==================

``machinome viewer`` reports and runs the installed viewer. Its three verbs,
``describe``, ``serve`` and ``capture``, ask the viewer named by
``--viewer NAME``, the browser viewer ``web`` by default; the command reads
no project's ``viewer`` key, and a viewer that cannot do what a verb needs is
refused by name, naming the viewers that can, with nothing printed on
standard output and exit 1. ``python -m machinome.viewer.web`` runs the same
command, with the same verbs and options, and is useful for selecting the
exact Python environment. Use ``--help`` after the command or a verb for its
installed syntax. There is no viewer-side CAD build command.
:ref:`viewer-command` is its synopsis in the command line reference.

describe
========

.. code-block:: console

   machinome viewer describe

Print one JSON object to standard output and exit 0:

.. code-block:: json

   {
     "path": "/installation/machinome/viewer/web/widget/dist/machinome-viewer.js",
     "index": "/installation/machinome/viewer/web/widget/index.html",
     "apiVersion": 29,
     "documentVersions": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
     "version": "0.8.1"
   }

Paths above are illustrative; actual paths are absolute installation paths.
A missing/stale bundle that cannot be rebuilt produces a remedy on standard
error, **no JSON on standard output**, and exit 1. Build logs do not pollute
the JSON stream. In a source checkout the lookup may rebuild a stale bundle;
it never installs npm dependencies for you.

``machinome viewer`` with no verb prints the same report, and takes no
option. The framework reaches the package through its viewer seam, in its own
process, as the viewer named ``web``: ``machinome develop``, ``machinome
snapshot`` and ``machinome export`` describe, serve and capture through the
package's provider operations, and so do these verbs. Applications can use
this command instead of importing anything from the viewer.

serve
=====

.. code-block:: console

   machinome viewer serve --build-dir /path/to/build --port 8000

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Argument
     - Meaning
   * - ``--build-dir PATH``
     - Required published build directory, containing ``viewer.json`` and models.
   * - ``--port INTEGER``
     - Listen port; default ``MACHINOME_PORT`` from the environment, otherwise 8000.
   * - ``--viewer NAME``
     - The viewer that serves; default ``web``, the one viewer that serves.

There is one static development page, no separate npm development server.
Once the server listens, the command prints ``Serving at
http://0.0.0.0:PORT (Ctrl+C to stop)`` on standard output, and
``machinome develop`` prints the same line. The command stays in the
foreground until stopped: Ctrl-C stops the server
and exits 0, and a termination signal stops it and ends the process by that
signal. A port another program listens on is one ``Error:`` line on standard
error and exit 1. It serves existing files and remains reachable when a build
is missing or failed. It never imports project source or builds CAD.
``machinome develop`` owns that work when using the framework.

.. warning::

   ``serve`` binds **0.0.0.0**, not just localhost, and provides no
   authentication. Only use it for trusted development, not public hosting.
   There is no CLI ``--host`` option.

Development host endpoints
--------------------------

These are useful to a host replacing the supplied development page:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Endpoint
     - Response
   * - ``GET /``
     - The shipped development page.
   * - ``GET /_viewer``
     - ``{available, apiVersion, remedy}``; check before fetching the bundle.
   * - ``GET /_viewer/bundle.js``
     - Current viewer bundle, or 503 with a remedy if unavailable/stale.
   * - ``GET /build/<path>``
     - A file inside the published build directory, with ``Cache-Control: no-store``;
       missing/out-of-directory files return 404.
   * - ``GET /_build_error``
     - Producer-written ``errors.json`` content or an empty object.
   * - ``WS /ws/reload``
     - Development connection; a connection receives ``reload`` when it opens,
       and again, on the same connection, each time ``machinome develop``
       publishes a build, the framework serving through this package in its
       own process.

``mountDevelopment()`` uses these routes. A static-export host should use
``mount()``/``mountInspector()`` and needs none of them.

capture
=======

.. code-block:: console

   machinome viewer capture STAGING -o OUTPUT.png [options]

Photograph a staged document as a transparent PNG. Requires Playwright and
Chromium (see :doc:`/start/install`). The staging directory must already
contain ``viewer.json`` and its referenced models. Capture writes its page
and bundle into that directory before starting a temporary local server and
headless browser; use a disposable staging copy.

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Argument
     - Meaning / default
   * - ``STAGING``
     - Required directory containing the prepared document.
   * - ``-o PATH``, ``--output PATH``
     - Required output PNG path; choose a new path if preserving an existing image.
   * - ``--imgsize WIDTHxHEIGHT``
     - Positive integer pixels; default ``1920x1080``.
   * - ``--time NUMBER``
     - Normalized animation time in [0, 1]; default 0, not elapsed simulation time.
   * - ``--view ex,ey,ez,tx,ty,tz``
     - Eye and target in model units; omitted means fit the model.
   * - ``--up x,y,z``
     - Camera up vector; default Z-up (0, 0, 1).
   * - ``--fov NUMBER``
     - Vertical field of view in degrees; default 50.
   * - ``--viewer NAME``
     - The viewer that photographs; default ``web``. A viewer that reads no
       published document, such as ``openscad``, is refused.

Use ``--view=-80,60,40,0,0,0`` when a tuple starts with a negative value.
Running documents are captured at rest and refuse nonzero ``--time``.
Clocked documents start at their initial bank; time selects only their
ordinary timeline. No snapshot/session restore argument is provided.

Successful capture exits 0 and leaves the staging directory in place. A
handled capture error prints one ``Error:`` line to standard error, writes no
image and exits 1. Invalid argument syntax or time outside [0, 1] exits 2,
before any viewer is asked.
