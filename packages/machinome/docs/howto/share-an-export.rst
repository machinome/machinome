======================
Sharing and snapshots
======================

Share a static export
=====================

The framework creates exports; the viewer reads them. Follow the framework's
`export guide <https://machinome.readthedocs.io/en/latest/embedding.html>`_
to publish your model with ``machinome export``. Keep the complete directory:

.. code-block:: text

   export/
   ├── index.html
   ├── machinome-viewer.js
   ├── manifest.json
   └── models/

Serve it over HTTP or HTTPS, not ``file://``. For a local review:

.. code-block:: console

   python -m http.server 8080 --bind 127.0.0.1 --directory /path/to/export

Open ``http://localhost:8080/``. To publish it, copy the entire directory to
your static host, preserving relative paths. The reader needs no Python or CAD
runtime. An export made with ``--no-widget`` has no page or viewer bundle;
provide a host as described in :doc:`embedding`.

The bundle carries AGPL-3.0-only and third-party notices. Preserve those notices
and consult the repository's `LICENSE
<https://github.com/machinome/machinome-viewer/blob/main/LICENSE>`_ when
redistributing or modifying it. The framework's Apache license is not the
license of the browser bundle.

Link to a chosen presentation
=================================

The shipped page accepts these query parameters:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Parameter
     - Effect
   * - ``t=0.25``
     - Select the normalized animation fraction.
   * - ``autoplay=0``
     - Start the timeline paused.
   * - ``layout=inspector``
     - Show the viewer with an assembly sidebar (the shipped page's default).
   * - ``layout=viewer``
     - Show the plain viewer.
   * - ``sidebar=open`` or ``sidebar=collapsed``
     - Choose the initial inspector sidebar state; the page defaults to collapsed.

For example, ``index.html?t=0.25&autoplay=0&sidebar=open`` opens a posed model
at one quarter of its timeline. **It does not advance a running simulation
or seek a clocked machine's elapsed clock.** Use the appropriate JavaScript
handle when a host needs to operate retained machine state.

Capture a still
===============

For a Machinome project, use the framework's ``machinome snapshot --renderer web``
command. The framework prepares the build and launches this package's capture
process. Consult its `CLI reference
<https://machinome.readthedocs.io/en/latest/cli.html>`_ for model and
output arguments.

For an already staged directory containing ``viewer.json`` and its models:

.. code-block:: console

   machinome-viewer capture /path/to/staged-build -o preview.png \
     --imgsize 1280x720 --time 0.25 \
     --view=80,-60,40,0,0,0 --up=0,0,1 --fov 35

Capture requires the :doc:`snapshot extra and Chromium <installation>`.
The camera tuple is eye X/Y/Z followed by target X/Y/Z. Camera coordinates
are model units, field of view is degrees, and image dimensions are pixels.

A running document is captured at rest; nonzero ``--time`` is refused because
it is not elapsed running time. A clocked document starts from its declared
bank, with ``--time`` affecting only its ordinary animation timeline.
This command does not accept a saved running/clocked session. To capture
another retained state, arrange for the producer to publish that state as a
pose rather than trying to seek it with ``--time``.

The capture command adds its page and bundle to the staging directory.
Use a disposable staged copy, not a directory whose contents must remain
unchanged. See :doc:`reference/cli` for every option and failure behavior.
