===============
Troubleshooting
===============

The page is blank or the model does not load
================================================

Serve the document over HTTP/HTTPS, not ``file://``. Check the browser's
network errors for the manifest, bundle and model paths. A document served
under a subdirectory needs its models beside it (or a correct ``baseUrl``).
Give the mount container a nonzero height and ensure WebGL is available.
A custom host must catch and display mount failures; see :doc:`embedding`.

The viewer is missing or stale
==============================

Run ``machinome-viewer describe`` in the same environment as the framework.
For a source checkout, install the locked frontend dependencies and rebuild:

.. code-block:: console

   npm ci --prefix machinome_viewer/widget
   npm run build --prefix machinome_viewer/widget

The package rebuilds a stale source bundle on lookup, serve or capture only
when the build tools/dependencies already exist. It never installs npm
dependencies automatically. A failed rebuild refuses the stale artifact and
prints a remedy. Installed distributions carry their bundle and need no npm.

An unsupported document version is reported
===========================================

Compare the model's version with ``documentVersions`` in the viewer report.
Install a matching viewer and regenerate any export that still carries an old
bundle. Editing the document's version number does not add the missing
runtime capability. See :doc:`compatibility`.

Time or a driver appears to do nothing
===========================================

The 0–1 timeline is not elapsed simulation time. For a running model, call
``run().move()`` and advance ticks; for a clocked model, call
``machine().move()``. ``setDriver()`` changes the posed driver table, not
those retained banks. Use qualified IDs from the declarations and distinguish
native driver values from design-unit movement requests.

A running request's promise completes when the command retires, not when it
is queued. Awaiting it while the run is paused, without advancing ticks,
can wait indefinitely. The built-in panel starts the run automatically;
a custom host must call ``start()`` or ``step()``. See :doc:`reference/running`.

The development page says the model is stale
================================================

An offline banner means the reload connection is unavailable. Check that the
framework development process and viewer server are still running on the
expected port. A build-error overlay reports the producer's error, while
the last model stays mounted. Fix the build rather than mistaking the old
geometry for the new result.

A snapshot fails
================

Install the snapshot extra **and** Chromium in the environment executing the
command. Check that staging contains ``viewer.json`` and every model it names.
Use ``--time 0`` for a running document. A clocked elapsed state cannot be
selected with ``--time`` either. Camera arguments beginning with a minus sign
are easiest to pass with ``=`` (for example, ``--view=-80,60,40,0,0,0``).
Capture errors go to standard error and exit nonzero; see :doc:`reference/cli`.

The sidebar or controls do not fit
======================================

Collapse the sidebar, widen the container, or set the documented inspector
CSS variables. The operating panel scrolls independently. For a completely
custom panel, set ``driverControls: 'none'``; this does not disable declared
part gestures. Set ``partControls: 'none'`` separately if needed. See
:doc:`reference/layouts` and :doc:`reference/mount`.
