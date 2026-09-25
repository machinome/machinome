What a build publishes
======================

Every command that loads a model, ``build``, ``develop``, ``test``,
``snapshot``, ``export``, goes through one pipeline: the tree is
enumerated, every part's artifact is brought current, and a document is
published that names them all. This page states what that document is,
which version it declares, and what the viewer must be to read it.

The build directory
-------------------

``_build/`` (``SOLID_BUILD_DIR`` moves it; a named model builds in
``_build/<name>/``) is written directly and holds, per node,
``<script>-<uniq_id>.stl``, plus ``.brep`` for an exact node, ``.dxf``
for a sheet part, ``.marking-<name>.stl`` per declared marking, and the
``.scad`` of OpenSCAD-family parts. Artifacts of different parameter sets
coexist. Each artifact is written whole or not at all, every artifact a
document names is in place before the document, and a successful
publication sweeps files the document no longer references. Builds of
one project serialize on an advisory lock beside the build directory.

``viewer.json`` is the document. ``errors.json`` is written, atomically,
on a failed build and removed after the next successful one; a failed
build after a success may leave a partially updated model beside it.
``machinome build`` exits 0 when the model built or was current, 66 when
the reference resolves to nothing, and another nonzero status when the
build failed.

The document
------------

``{format: "machinome-export", version, animation: {fps, frames, loop?},
drivers, instructions, controls?, states?, bindings?, program?, clocked?,
root, pieces}``. Each tree node carries ``name``, ``type``, ``color``,
``mtime``, ``operations``, and either ``children``, a rigid node's
``model`` path with its ``piece`` id (plus ``markings`` when it declares
any), or a flexible leaf's ``flexible`` shape specification. Operations
serialize as ``['r', angle, axis]`` and ``['t', vector]`` with raw
expressions: a symbolic ``$t``, a qualified driver id, or under a running
root a banked coordinate's id. ``bindings`` is a table of shared
subexpressions the serializer publishes whenever one repeats across the
document. ``drivers``, ``instructions`` and ``controls`` are tables keyed
by qualified id. None of it is hand-authored.

Document versions
-----------------

The version says what a consumer must understand, and the producer
emits the lowest its content needs:

.. list-table::
   :header-rows: 1
   :widths: 12 88

   * - Version
     - Required capability
   * - 1
     - The legacy node-tree schema, without a driver table.
   * - 2
     - Driver and instruction tables; the base document.
   * - 3
     - Flexible parts carried as shape specifications.
   * - 4
     - Shared expression ``bindings``.
   * - 5
     - A running root's compiled ``program`` and coordinate bank.
   * - 6
     - Running laws that read the coordinate they drive.
   * - 7
     - Selected relation blocks in a running program.
   * - 8
     - A clocked machine: ``states``, committing relations and bounds.
   * - 9
     - Explicit running ``Play`` relations for retained clearance.
   * - 10
     - Running relations driven by the root's clock (``time.drives``).
   * - 11
     - Source-timed running dependencies, preserving dwell and landing timing.
   * - 12
     - A retained ``Follow`` between two moving clearance surfaces.
   * - 13
     - A running ``Bound`` whose limit uses finite convex profile contact.

A posed model is 2 to 4. A root declaring ``Time.running()`` now publishes 11,
12 when its program carries a ``Follow`` relation, or 13 when a running
``Bound`` uses finite profile contact; older running exports
used 5, 6, 7, 9 or 10 according to their laws.
A tree declaring a ``State``
publishes 8 whatever else it holds. Markings and controls are additive within their
version. The bumps from 5 upward are **not** additive: a consumer that
cannot read the declared version refuses the document by name rather
than rendering part of a machine it does not understand.

The viewer
----------

The viewer is the separate ``machinome-viewer`` package,
AGPL-3.0-or-later, installed through the ``viewer`` extra, and reached
only as a separate
process: ``machinome develop`` starts its server on the build directory,
``machinome export`` copies its page and bundle, ``machinome snapshot
--renderer web`` hands it the model for a headless capture. ``machinome
viewer`` prints the installed package's ``version``, ``apiVersion`` and
``documentVersions``, three separate contracts; a report without
``documentVersions`` means 1 to 4. This manual matches viewer
|viewer_version|, API |viewer_api|, reading |document_versions|.

When the installed viewer cannot read the version a model publishes,
``build``, ``develop`` and ``export`` still publish it and warn once,
naming the version written, the versions the viewer renders and its
package version; the build, the STL files, the tests and ``--no-web`` are
unaffected. ``machinome snapshot --renderer web`` refuses before it
starts the browser, because a capture is a one-shot. The viewer's own
manual states what its panels do for posed, running and clocked
documents.

See `using the viewer
<https://machinome-viewer.readthedocs.io/en/latest/using-the-viewer.html>`_
for operation and its `API reference
<https://machinome-viewer.readthedocs.io/en/latest/reference/index.html>`_
for host integration. The framework does not duplicate those contracts.

.. warning::

   A host that pins its own copy of the viewer bundle must upgrade it
   with the framework. A solid-node 0.5 viewer predates the version gate
   and silently draws only the part of a newer machine it can evaluate.

An export
---------

``machinome export -o export`` writes a self-contained directory:

.. code-block:: text

    export/
    ├── manifest.json
    ├── models/
    ├── index.html
    └── machinome-viewer.js

The manifest and models are the document and its artifacts; the page and
bundle come from the installed viewer package, and ``--no-widget`` omits
them, which is the only way to export without the viewer installed and
the form this manual's committed exports take. ``--fps`` and ``--frames``
govern the ``$t`` timeline of a model without a declared ``Time``;
drivers have no frame grid. An export never freezes a pose.

The page's URL options select an initial state: ``?t=0.25&autoplay=0`` a
paused timeline pose, ``?layout=inspector&sidebar=open`` the assembly
inspector, ``?layout=viewer`` the plain viewer. Timeline time does not
seek a running machine's history or a clocked machine's clock; those are
the JavaScript handles' job, documented with a complete host page in the
`viewer manual <https://machinome-viewer.readthedocs.io/en/latest/embedding.html>`_.
Values there are in native driver units, and declared ranges never clamp.

The framework's :doc:`Sphinx directive </reference/sphinx>` embeds an
export in documentation and completes a widget-less export with the
installed viewer at build time.

Snapshots
---------

``machinome snapshot`` renders one pose to a PNG: the OpenSCAD renderer by
default, fast and without a browser, or the viewer's headless browser
with ``--renderer web`` and a real alpha channel. ``--time`` selects a
timeline fraction, ``--drive`` binds drivers by qualified id, and
``--set`` changes build parameters instead. Under a running root the
image is the untimed rest pose at those driver values; a state carrying
history is not posed from the command line. Neither renderer falls back
to the other.
