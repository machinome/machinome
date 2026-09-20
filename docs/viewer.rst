
.. _viewer:

======================
The development viewer
======================

``machinome develop [reference]`` is where you spend your time: it builds
the node, opens a viewer, watches the source files, and rebuilds
whenever you save — the CAD equivalent of a web framework's
development server.

The **browser viewer** is a separate package,
`machinome-viewer <https://github.com/machinome/machinome-viewer>`_,
installed with ``pip install "machinome[viewer]"``. It is the sole
interactive viewer opened by ``machinome develop``; without it the command fails
before starting the development processes and names the extra to install.
``--web`` remains an explicit spelling of the default, and ``--no-web`` runs
only the watch-and-build loop for an external host.

The two packages are licensed differently: machinome under Apache-2.0
and the viewer under AGPL-3.0-only. The framework is complete without the
viewer — it builds, tests, exports (``--no-widget``), develops with
``--no-web``, and takes fixed-pose snapshots through OpenSCAD — and reaches
the browser viewer only as a separate process when it is installed.

For the 0.7 preview, use matching source installations as described in
:doc:`quickstart`; the independent viewer is not yet published.

The viewer has its own `user manual
<https://machinome-viewer.readthedocs.io/en/latest/index.html>`_. See
`Using the viewer
<https://machinome-viewer.readthedocs.io/en/latest/using-the-viewer.html>`_
for assembly navigation, posed/running/clocked controls and troubleshooting.
This page covers the framework's development workflow; the independent manual
is the reference for operating and embedding the viewer itself.

The web viewer
==============

With the ``viewer`` extra installed, ``machinome develop`` serves the browser
viewer at http://localhost:8000. It shows the assembled model with orbit
controls, a navigation tree of the nodes, and plays the animation of
nodes that use `self.time`.

Edit and save any source file, and the affected parts are rebuilt in
the background and reloaded in the browser — no manual refresh.

Driving the model
=================

A model that declares :doc:`drivers <driving>` grows controls in this
same viewer: one slider per driver and one button per instruction
declared at the focused assembly layer, with a breadcrumb to walk the
focus down into subassemblies and back up. Sliders show a numeric
readout in the driver's design units, and dragging one re-evaluates
only the expressions that read it. Click a readout to type a value;
the slider range is presentation metadata, not a mechanical limit.

A declared ``Time(loop=...)`` displays machine time and plays
at real time. Use the speed selector to accelerate Clock 01's twelve-hour
loop. Moving time does not reset independent driver values.

The full description of the control
surface — scoping rules included — is in :doc:`Driving a machine
<driving>`; it applies unchanged to static exports and embedded
widgets (:doc:`Embedding models <embedding>`).

When an edit doesn't compile or fails to render, the viewer shows the
build error and keeps running: fix the code, save, and the model comes
back. If the `machinome develop` process itself is not running (or was
restarted), the viewer shows a persistent offline banner until it
reconnects.

Document versions, and a running root
=====================================

The document a build or an export publishes declares a schema
**version**, and the installed viewer reports which versions it renders
(``machinome viewer``, the ``documentVersions`` field; a viewer that predates
the field renders 1 to 4). A root declaring ``time = Time.running()``
publishes **version 5, 6 or 7**, according to its laws, carrying the
compiled program beside the geometry — see :doc:`Scenario tests <scenarios>`, "What a running root
publishes".

That bump is not additive, so a viewer that cannot read the declared version
refuses the document by name rather than rendering part of a machine.
``machinome build``, ``machinome develop`` and ``machinome export`` publish it anyway
and warn once, naming the version written, the versions the installed
viewer renders and its package version — the build, the STLs, the tests
and ``--no-web`` are unaffected by a browser that cannot render.
``machinome snapshot --renderer web`` is the one channel that REFUSES
instead: a capture is a one-shot, and a failure inside a headless page
would reach you as an opaque non-zero exit.

The matching viewer source, 0.2.0, reports API 22 and reads document
schemas 1–9. It is not yet published. It executes running documents
(5, 6, 7 or 9, depending on the laws) and clocked documents (8).

For a running machine the panel offers nudges, hold-to-jog controls,
instruction buttons, and run/pause/step transport. Coordinates retain
history, so the panel requests movement instead of setting arbitrary
positions. Declared ``Button``, ``Turn`` and ``Slide`` controls also
let a person operate the named parts directly.

For a clocked machine the panel offers input handles and read-only
state values. Each gesture makes one request and reports admitted
travel, stops or a refusal. An instruction's duration controls the
drawing of its transition. A declared elapsed clock adds play, step
and speed controls; time cannot be scrubbed backwards. These models
have distinct host APIs, described in :doc:`embedding`.

Ports
=====

The backend port is 8000 by default, configurable with the
``MACHINOME_PORT`` environment variable. The `machinome` command loads a
``.env`` file from the working directory at startup, so a project can
pin its ports there — and several projects can run side by side. The
viewer's server inherits that environment.

OpenSCAD snapshots are a separate capability
============================================

OpenSCAD remains a supported modelling and output technology. To photograph
one numerically bound pose through its renderer:

.. code-block:: bash

    $ machinome snapshot --renderer openscad

That fixed-pose snapshot renderer remains the default for ``machinome snapshot``.
It is not an interactive viewer: OpenSCAD has no notion of the independent
driver controls and instructions, and flexible geometry is evaluated only at
the selected state. Use the browser viewer to drive a machine by hand.

Hacking on the viewer itself
============================

The browser viewer's source — the three.js widget, its static
development page and the server ``machinome develop`` launches — lives in
the `machinome-viewer repository
<https://github.com/machinome/machinome-viewer>`_, not in machinome.
Clone it and follow its source-build instructions in the same environment
as Machinome. The current viewer serves a static inspector and rebuilds
an out-of-date bundle on demand; it has no separate frontend dev server.
``--web-dev`` is retained as a compatibility request and has no effect
with this viewer. To step into the viewer's server under a debugger,
run ``machinome-viewer serve --build-dir _build``. ``--debug-builder`` does
the same for the builder — see the :doc:`command line reference <cli>`.
