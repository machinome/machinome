==============
Browser viewer
==============

The browser viewer turns a published model into an interactive 3D assembly:
orbit the camera, look inside subassemblies, operate declared controls, and
watch the machine respond.

Use it through ``machinome develop``, share a self-contained export, or embed
the same viewer in your own page. The browser reads the model's published
geometry and mechanical relationships; it does not need Python or a CAD
backend to display and operate an export. The viewer is the package
``machinome-viewer``, installed by ``machinome[viewer]`` and numbered with the
framework; it declares viewer API |viewer_api| and reads document versions
|document_versions|. The framework reaches the package through its viewer
seam, in its own process, as the viewer named ``web``.

The browser entry point is ``MachinomeViewer`` from ``machinome-viewer.js``.
Handles below are returned objects, not constructors you instantiate.
Method names are grouped by interface so they are searchable in the
:ref:`general index <genindex>`.

.. toctree::
   :maxdepth: 1

   mount
   viewer-handle
   layouts
   running
   clocked
   cli
   compatibility
   troubleshooting

Start with :doc:`/howto/embed-the-viewer` for a complete working page. The
reference documents the current public mounts and handles, not internal
TypeScript exports used as implementation/test seams.
