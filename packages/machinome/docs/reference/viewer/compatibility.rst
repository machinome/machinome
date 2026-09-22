==========================
Versions and compatibility
==========================

Three version numbers
=====================

The current source declares:

* **Package |package-version|** — the Python distribution and its bundled
  widget, released with Machinome 0.7.0 and numbered with it. The widget is
  not published on npm; it ships inside the Python distribution.
* **Viewer API |viewer-api|** — the browser-host interface/capabilities.
* **Document versions |document-versions|** — model schemas this bundle reads.

Ask the installation rather than inferring compatibility from a package name:

.. code-block:: console

   machinome-viewer describe

The JSON's ``version``, ``apiVersion`` and ``documentVersions`` are distinct.
The framework exposes its own lookup as ``machinome viewer``. The browser
bundle exposes ``MachinomeViewer.apiVersion`` and ``MachinomeViewer.API_VERSION``;
each mounted viewer also exposes ``apiVersion``.

Document capabilities
=====================

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - Version
     - What the viewer must understand
   * - 1
     - The original node tree and animation expressions.
   * - 2
     - Drivers and instructions.
   * - 3
     - Flexible parts represented as analytic shape specifications.
   * - 4
     - Shared expression bindings.
   * - 5
     - A compiled running program and retained coordinate bank.
   * - 6
     - Running laws reading the coordinate they drive.
   * - 7
     - Selected relation blocks in running programs.
   * - 8
     - A clocked machine with drivers, stored states, events and bounds.
   * - 9
     - Running ``Play`` relations retaining clearance/contact history.
   * - 10
     - Explicit running time drives with independently admitted motion.
   * - 11
     - Source-timed running motion through ordinary chains and selected blocks.

These are producer-selected schemas, not modes you change by editing a JSON
version field. The viewer accepts current ``machinome-export`` and legacy
``solid-node-export`` family identifiers. It rejects unsupported versions,
unknown flexible technologies/specifications, malformed expressions and
unresolved driver IDs with an explanation. Keep the producer and bundle
compatible; do not remove the version gate to make a document load.

Migrating a host
================

API 20 established the Machinome browser names:

.. list-table::
   :header-rows: 1

   * - Surface
     - Current name
   * - JavaScript bundle
     - ``machinome-viewer.js``
   * - Browser global
     - ``MachinomeViewer``
   * - Declarative mount
     - ``data-machinome-widget``
   * - Layout/sidebar attributes
     - ``data-machinome-layout``, ``data-machinome-sidebar``
   * - Component CSS prefixes
     - ``machinome-nav``, ``machinome-inspector``

Old SolidNode browser globals, mount attributes and CSS aliases are not
provided. Reading a legacy model document does not restore old host names.
API 21 added :js:meth:`ViewerHandle.setView`; API 22 added running ``Play``
execution; API 23 adds explicit running time drives; API 24 preserves determined
source timing, including dwell and landing, through running dependencies.
A host that needs a
feature can check the declared API before
using it. Do not assume an old pinned bundle implements the current manual.

Source-timing migration
=======================

Re-export running models with the corrected producer and use an API-24 viewer.
New running exports declare document version 11 even when an individual model
has only affine motion. An old viewer refuses that version before operation.
Do not lower the version by hand: the payload shape is unchanged, but the
execution semantics are not. Posed, looping and clocked version selection is
unchanged.

Legacy running exports still load in the corrected viewer and use corrected
physics. An old export cannot prevent an old viewer from executing its old
arithmetic. New producer identities include the source-timing generation, so
endpoint-era snapshots refuse restore into re-exported programs. Restart from
the model's initial state and replay the intended commands instead.

Dependency boundary
===================

Machinome builds and publishes models. This package renders their documents,
executes the published mechanical program in JavaScript, and provides the
development/capture processes. It does not import Machinome or load project
Python code. Flexible parts are evaluated with the bundled molejo runtime;
they do not require a server-side CAD rebuild for each browser frame.

See the `framework upgrade guide
<https://machinome.readthedocs.io/en/latest/project/upgrading.html>`_ for changes to
model authoring rather than viewer hosting.
