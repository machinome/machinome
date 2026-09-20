======================
Command-line reference
======================

``machinome-viewer`` has three operations. ``python -m machinome_viewer`` is
equivalent and is useful for selecting the exact Python environment. Use
``--help`` after the command or subcommand for its installed syntax.
There is no viewer-side CAD build command.

describe
========

.. code-block:: console

   machinome-viewer describe

Print one JSON object to standard output and exit 0:

.. code-block:: json

   {
     "path": "/installation/machinome_viewer/widget/dist/machinome-viewer.js",
     "index": "/installation/machinome_viewer/widget/index.html",
     "apiVersion": 22,
     "documentVersions": [1, 2, 3, 4, 5, 6, 7, 8, 9],
     "version": "0.2.0"
   }

Paths above are illustrative; actual paths are absolute installation paths.
A missing/stale bundle that cannot be rebuilt produces a remedy on standard
error, **no JSON on standard output**, and exit 1. Build logs do not pollute
the JSON stream. In a source checkout the lookup may rebuild a stale bundle;
it never installs npm dependencies for you.

This is also the mapping returned by the standard-library-only callable
registered as ``bundle`` in the Python entry-point group ``machinome.viewer``.
The lookup is the only Python integration seam; rendering, serving and capture
remain separate processes. Applications can use this command instead of
importing anything from the viewer.

serve
=====

.. code-block:: console

   machinome-viewer serve --build-dir /path/to/build --port 8000

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Argument
     - Meaning
   * - ``--build-dir PATH``
     - Required published build directory, containing ``viewer.json`` and models.
   * - ``--port INTEGER``
     - Listen port; default ``MACHINOME_PORT`` from the environment, otherwise 8000.
   * - ``--dev``
     - Deprecated, accepted and ignored with a notice.
   * - ``--frontend-port INTEGER``
     - Deprecated, accepted and ignored with a notice.
   * - ``--start-frontend``
     - Deprecated, accepted and ignored with a notice.

There is one static development page, no separate npm development server.
The command stays in the foreground until stopped. It serves existing files
and remains reachable when a build is missing or failed. It never imports
project source or builds CAD. ``machinome develop`` owns that work when using
the framework.

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
     - Development connection; a connection receives ``reload``. The framework
       development workflow owns republishing and restarting its serving process.

``mountDevelopment()`` uses these routes. A static-export host should use
``mount()``/``mountInspector()`` and needs none of them.

capture
========

.. code-block:: console

   machinome-viewer capture STAGING -o OUTPUT.png [options]

Photograph a staged document as a transparent PNG. Requires Playwright and
Chromium (see :doc:`../installation`). The staging directory must already
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

Use ``--view=-80,60,40,0,0,0`` when a tuple starts with a negative value.
Running documents are captured at rest and refuse nonzero ``--time``.
Clocked documents start at their initial bank; time selects only their
ordinary timeline. No snapshot/session restore argument is provided.

Successful capture exits 0. A handled capture error prints to standard error
and exits 1. Invalid argument syntax or time outside [0, 1] exits 2. No
subcommand prints the command help and exits 0.
