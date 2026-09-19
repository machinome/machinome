.. _embedding:

=====================================
Embedding machines in pages and docs
=====================================

``machinome export`` publishes a machine as a static directory.
Its geometry, expressions, controls and any compiled simulation travel
together, so a reader can inspect and operate it in the browser.
No server-side CAD runtime is required.

What an export contains
=======================

::

    export/
    ├── manifest.json
    ├── models/
    ├── index.html
    └── machinome-viewer.js

The manifest and models are the data. The page and bundle come from
the independent `Machinome Viewer
<https://github.com/machinome/machinome-viewer>`_ package, installed
through ``machinome[viewer]``. ``--no-widget`` omits those viewer
files. The viewer is AGPL-3.0-only and its bundle carries its source and
licence notice.

Serve the directory over HTTP. The page provides the appropriate
controls for the machine: a timeline and input sliders for a posed
model, running controls for a running model, or request handles and
state readouts for a clocked model.

Document and viewer versions
=============================

New manifests identify themselves as ``machinome-export``. Their
schema version describes what the consumer must understand:

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - Version
     - Required capability
   * - 1
     - The legacy node-tree schema, without a driver table.
   * - 2
     - Driver and instruction tables; the current base document schema.
   * - 3
     - Flexible parts carried as shape specifications.
   * - 4
     - Shared expression ``bindings``.
   * - 5
     - A running root's compiled program and coordinate bank.
   * - 6
     - Running laws that read the coordinate they drive.
   * - 7
     - Selected relation blocks in a running program.
   * - 8
     - A clocked machine: stored states, committing relations and bounds.

The current producer starts ordinary documents at 2, advances them for
content that needs 3 or 4, and publishes running machines at 5, 6 or 7
according to their laws. A tree declaring ``State`` publishes 8
regardless of its other content. See :doc:`scenarios`.

The matching viewer source is **0.2.0**, with **API 20**, accepting
**document schemas 1–8** and both the new and legacy
``solid-node-export`` families. It is still unpublished.
``machinome viewer`` reports the installed package's ``version``,
``apiVersion`` and ``documentVersions``; these are three separate
contracts. Its package declaration is ``machinomeViewerApi``.
API 20 also records the renamed browser global, bundle and DOM/CSS names.

An incompatible viewer refuses the document. Build and export still
publish with a warning; a web snapshot refuses before opening the browser.
A viewer report without ``documentVersions`` is treated as reading 1–4.

.. warning::

   A solid-node 0.5.x viewer predates the version gate and may silently
   draw only part of a newer machine. Upgrade a pinned viewer bundle
   with the framework and migrate the host names in :doc:`upgrading`.

Embedding in a web page
========================

The simplest host uses the exported page:

.. code-block:: html

    <iframe src="export/index.html"
            style="width: 100%; height: 480px; border: 0;">
    </iframe>

``?t=0.25&autoplay=0`` selects a paused timeline pose.
``?layout=inspector&sidebar=open`` selects the assembly inspector
with its sidebar open; ``?layout=viewer`` selects the plain viewer.
The standalone page selects the inspector, collapsed, by default.
Timeline time does not seek a running machine's history or a clocked
machine's elapsed clock. Use the JavaScript handles for those operations.

The JavaScript API
===================

Load ``machinome-viewer.js`` and mount through its browser global:

.. code-block:: javascript

    const viewer = await MachinomeViewer.mount('#model', 'manifest.json', {
      view: { camera: [80, -60, 40], target: [0, 0, 0] },
      up: [0, 0, 1],
      fov: 22.5,
      driverControls: 'none',
      partControls: 'none',
    });

``target`` is an element or selector. Camera vectors are three
numbers; field of view is in degrees. Defaults are Z-up and 50°.
``driverControls: 'none'`` hides the built-in operating panel;
``partControls: 'none'`` independently disables part gestures.
The corresponding APIs remain available.

Choose the operating handle
----------------------------

For a posed document, ``drivers()`` and ``instructions()``
list its declarations. ``driver(id)`` and ``setDriver(id, value)``
read and write **native** units; driver ranges do not clamp.
``onDriverChange(fn)`` subscribes and returns an unsubscribe function.
``trigger(name)`` returns ``{done, cancel()}`` and plays the
instruction as a ramp.

For a running document, ``run()`` returns the running handle:

* ``move(input, {by, duration})``, ``move(input, {to, duration})``,
  ``rate(input, rate)`` and ``trigger(name)`` submit operations in
  design units. Their promises resolve with outcomes when commands retire.
* ``start()``, ``pause()``, ``running()`` and
  ``step(ticks)`` control execution.
* ``state()``, ``coordinates()``, ``elapsed()``, ``tick()``
  and ``dt()`` describe the run. ``onCommit(fn)`` and
  ``onOutcome(fn)`` subscribe to its results.
* ``cancel(input)``, ``snapshot()``, ``restore(snapshot)``
  and ``reset()`` manage the session.

For a clocked document, ``machine()`` returns the synchronous
machine handle:

* ``move(input, {by})``, ``move(input, {to})`` and
  ``trigger(name)`` each solve one request and return its admitted
  travel, path ends, commits and stops. Requests use design units;
  bank values and returned path ends use native units.
* ``state()``, ``drivers()``, ``states()``, ``order()``
  and ``identity()`` describe the machine and its bank.
* ``snapshot()``, ``restore(snapshot)`` and ``reset()``
  manage retained state. A snapshot from another machine is refused.
* ``clock()`` returns the clock's name or ``null``.
  ``move('time', {by: seconds})`` advances a declared elapsed clock;
  ``clockPlaying()`` and ``setClockPlaying(playing)`` control
  its browser transport.

``run()`` is null on a clocked document; ``machine()`` is null
on a running document; both are null on a posed document. Direct
``setDriver`` is not a substitute for a running or clocked request.
Clocked host requests land immediately; the built-in panel draws their
transitions. ``controls()`` lists declared part controls and their
current screen locations even when gestures are suppressed.

Navigation, playback and lifecycle
-----------------------------------

``assembly()`` reads the tree; ``setRoot(path | null)`` focuses
a subtree; ``setVisible(path, visible)`` changes visibility.
Paths are arrays of sibling names relative to the document root.
``navigation()`` returns the current focus and hidden paths, and
``onAssemblyChange(fn)`` subscribes to changes.

``setTime(fraction)`` selects the normalized animation timeline.
``speed()`` and ``setSpeed(value)`` control playback speed where
the document supplies timed playback. They do not rewrite machine state.

``view()`` reads the camera. ``reload()`` reloads the model;
``manifestChanged()`` and ``artifactChanged(path)`` apply
targeted updates. Call ``dispose()`` when removing the viewer.

For the bundled assembly sidebar use
``MachinomeViewer.mountInspector(target, url, options)``; its handle
exposes ``viewer``, ``navigator``, ``sidebarOpen()``,
``setSidebar(open)`` and ``dispose()``.
A custom layout can instead attach
``MachinomeViewer.mountNavigator(target, viewer, options)``.
The viewer repository documents their full styling and keyboard contracts.

Embedding in Sphinx documentation
=================================

The ``machinome.sphinx`` extension provides a directive that embeds an
export in the built HTML. In ``conf.py``:

.. code-block:: python

    extensions = [
        # ...
        'machinome.sphinx',
    ]

Then, in any document:

.. code-block:: rst

    .. machinome:: exports/my_model
       :height: 300px
       :t: 0.25
       :autoplay: no

The argument is the path to an export directory, relative to the
current document (or to the documentation source directory, with a
leading ``/``). The directory is copied into the HTML output and
embedded as an ``<iframe>``.

Options:

``:height:``
    Height of the embedded viewer. Default: ``480px``. The width
    always follows the page.

``:t:``
    Initial animation time, 0.0 to 1.0.

``:autoplay:``
    ``yes`` (default) or ``no``. With ``no``, the animation starts
    paused — combine with ``:t:`` for a static pose.

The exports are generated ahead of the documentation build and
committed (or produced by a CI step) — the Sphinx build itself never
runs the CAD stack. A missing or invalid export directory fails the
build with a message saying which ``machinome export`` invocation would
create it.

An embedded export whose document version the installed viewer does not
render makes the directive **warn**, naming the export, the version it
declares and the versions the viewer renders. It does not fail the
build: the export is a committed artifact this build does not produce
and cannot fix, and the embedded widget refuses such a document in the
page, visibly. The check reads the version off the ``manifest.json``
the directive already opens, and loads no CAD runtime to do it.

The directive's options are ``:height:``, ``:t:`` and ``:autoplay:``
only — like the URL surface, it cannot yet preset a driver or
suppress the control chrome, so a driven model embeds with its
controls showing at their defaults.

Exports referenced by the directive may be made with ``--no-widget``:
the extension completes them with the viewer files from the installed
``machinome-viewer`` package at build time, so the repository only needs
to carry each model's ``manifest.json`` and STLs, and every embedded
model shares one copy of the viewer source. A documentation build
therefore needs the ``viewer`` extra installed; without it the build
warns — and fails under ``-W`` — naming the extra.
