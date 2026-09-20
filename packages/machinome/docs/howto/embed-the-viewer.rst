====================
Embedding the viewer
====================

Use an iframe when the exported page already has the controls you need.
Use the JavaScript API when your page owns the layout, camera or operating
panel. Both use the same viewer bundle.

Embed a complete export
=======================

.. code-block:: html

   <iframe src="export/index.html?autoplay=0"
           title="Interactive model of my machine"
           style="width: 100%; height: 500px; border: 0;"></iframe>

Keep the export's page, bundle, manifest and model directory together. Host
them over HTTP/HTTPS and give the iframe a useful title and nonzero height.
Query parameters are described in :doc:`sharing`.

Mount in your own page
==========================

Load ``machinome-viewer.js`` and call ``MachinomeViewer.mount()`` or
``MachinomeViewer.mountInspector()``. These return promises: the model and
its geometry must load before the handle is usable. Catch a rejection and
show the reader a meaningful error. Do not mount twice into the same container.

This is the complete page used by the example on the manual's home page:

.. literalinclude:: examples/embed.html
   :language: html

Its script uses only the public interface:

.. literalinclude:: examples/embed.js
   :language: javascript

The ``spinner/`` directory is a committed viewer test export, not a model
built by this documentation. Replace ``spinner/manifest.json`` with your own
export's URL and keep its referenced ``models/`` beside it. The default
mesh base is the document URL's directory, even under a nested site path.
Use ``baseUrl`` only when the models really live elsewhere.

.. raw:: html

   <div class="viewer-demo">
     <button type="button" data-viewer-demo="examples/embed.html">Run this example</button>
     <p>Orbit, select a timeline pose, or open Assembly to inspect the spinner.</p>
   </div>

The example pauses its timeline and selects time explicitly. It leaves orbit
controls and the assembly navigator active. ``pagehide`` disposes the mount
when leaving; a single-page application should likewise dispose it when
unmounting its component. A host that restores a page from the back/forward
cache must remount any disposed viewer.

Choose a layout
===============

* :js:func:`MachinomeViewer.mount` gives you the canvas and optional built-in
  operating controls.
* :js:func:`MachinomeViewer.mountNavigator` adds the assembly tree in a separate
  container, using an existing viewer handle.
* :js:func:`MachinomeViewer.mountInspector` composes the viewer, navigator and
  collapsible sidebar, with one disposal method.
* :js:func:`MachinomeViewer.mountDevelopment` additionally connects to the
  development server's reload/error endpoints. It is not a static-export mount.

See :doc:`reference/layouts` for options, keyboard behavior and CSS hooks.

A declarative mount
===================

The bundled page also supports this no-host-code spelling:

.. code-block:: html

   <div data-machinome-widget="export/manifest.json"
        data-machinome-layout="inspector"
        data-machinome-sidebar="collapsed"
        style="width: 100%; height: 500px;"></div>
   <script src="export/machinome-viewer.js"></script>

The bundle discovers these elements on page load. With no layout attribute,
the default is the plain viewer; the shipped export page explicitly selects
the inspector. Query-string layout/sidebar choices override attributes.
Choose either declarative mounting or an explicit mount for a container,
not both. A host needing a handle should mount explicitly.

Control the right kind of machine
====================================

Always inspect the loaded model before choosing its operating API:

.. code-block:: javascript

   const run = viewer.run();
   const machine = viewer.machine();
   if (run) {
     // Submit requests and advance simulation ticks: reference/running.
   } else if (machine) {
     // Make synchronous input requests: reference/clocked.
   } else {
     // Set posed driver values: reference/viewer-handle.
   }

Use the exact qualified IDs returned by the declarations; do not guess an
input's name from a part label. :doc:`reference/running` and
:doc:`reference/clocked` include scripted examples and explain when requests
complete. :js:meth:`ViewerHandle.setDriver` writes native values in the posed
driver table; it is not a command to a retained running or clocked bank.

Hosting requirements
====================

The container must have a measurable width and height. A resize observer
adjusts the canvas when your layout changes. Cross-origin document/model
requests need the serving host's CORS permission; serving everything from
one origin is simplest.

Running models normally use a blob worker bundled into the same JavaScript
file. If worker creation is refused (for example by a Content Security Policy),
the same engine runs on the rendering thread and ``run.runsInWorker`` is false.
Do not require a separate worker file. A restrictive host policy must also
account for injected component styles; navigator/inspector ``styles: 'none'``
lets the host supply their CSS. See :doc:`reference/layouts`.

For an externally posed still, ``renderMode: 'on-demand'`` removes the
background frame loop. It requires external animation and all interactive
controls disabled, and rejects running/clocked documents and instructions.
It is not the mode for an interactive machine. See :doc:`reference/mount`.
