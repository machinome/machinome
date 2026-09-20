==========================
Mounting and configuration
==========================

.. js:function:: MachinomeViewer.mount(target, sourceUrl, options)

   Load a published ``manifest.json`` or ``viewer.json`` into a container.

   :param target: An ``HTMLElement`` or CSS selector resolving to one.
   :param sourceUrl: String URL of the published document, not its directory.
   :param options: Optional ``ViewerOptions`` object described below.
   :returns: ``Promise<ViewerHandle>`` after the document and geometry load.

   Mounting needs a measurable container and WebGL. Missing targets, failed
   requests, malformed/unsupported documents, and unsupported options reject
   the promise. Handle the error in your host. Use one mount per container,
   then :js:meth:`ViewerHandle.dispose` before removing or replacing it.

.. js:attribute:: MachinomeViewer.apiVersion

   Integer browser API version: |viewer-api| in this source build.

.. js:attribute:: MachinomeViewer.API_VERSION

   The same API version under its constant spelling.

Viewer options
==============

All properties are optional. ``mountInspector`` and ``mountDevelopment``
accept these too, with the additions/defaults in :doc:`layouts`.

.. js:attribute:: ViewerOptions.baseUrl

   String mesh base. Defaults to the source document's directory, with query
   parameters removed. Relative model paths resolve against this base.

.. js:attribute:: ViewerOptions.animation

   ``'inline'`` (default), ``'toggle'``, ``'none'`` or ``'external'``.
   Inline shows the timeline bar for animated geometry; toggle starts the bar
   collapsed behind a toggle. None hides timeline chrome but permits automatic
   animation. External hides it and leaves normalized time to the host's
   ``setTime()`` calls. This option does not replace running/clocked transport.

.. js:attribute:: ViewerOptions.autoplay

   Boolean, default ``true``: start ordinary timeline animation automatically.
   Set ``false`` for a chosen still. Running autostart has its own option below.

.. js:attribute:: ViewerOptions.time

   Initial normalized animation fraction, default ``0``, clamped to [0, 1].
   A non-finite initial value falls back to 0. Not elapsed running/clock time.

.. js:attribute:: ViewerOptions.speed

   Playback multiplier, default ``1``. Must be finite and positive. A declared
   loop plays in real time at 1×. Also controls running/elapsed-clock playback;
   it never changes the run's fixed tick size. A loop-less posed document uses
   its frame-count/frame-rate duration rather than this multiplier.

.. js:attribute:: ViewerOptions.driverControls

   ``'inline'`` (default) or ``'none'``. Controls the built-in operating panel;
   all driving methods remain available when the panel is hidden.

.. js:attribute:: ViewerOptions.partControls

   ``'inline'`` (default) or ``'none'``. Independently controls declared part
   gestures, highlights, cursor and tooltip. ``controls()`` still returns
   declarations and current screen locations when gestures are disabled.

.. js:attribute:: ViewerOptions.view

   Optional ``ViewInput`` with ``camera`` and ``target``. Defaults to fitting
   the visible model. Vectors use model coordinates, normally millimetres.
   A previous ``viewer.view()`` result can be passed to a new mount.

.. js:attribute:: ViewInput.camera

   Eye position as a three-number array or a three.js ``Vector3``. Prefer
   arrays so your host does not need its own three.js dependency.

.. js:attribute:: ViewInput.target

   Orbit/look-at target in the same vector form. For a usable view, provide
   finite coordinates and keep camera and target distinct.

.. js:attribute:: ViewerOptions.up

   Up vector in the same form, default ``[0, 0, 1]`` (Z-up).

.. js:attribute:: ViewerOptions.fov

   Vertical field of view in degrees, default ``50``. A non-finite or
   nonpositive mount value falls back to 50; supply a sensible camera angle.

.. js:attribute:: ViewerOptions.className

   Optional CSS class string assigned to the renderer's canvas.

.. js:attribute:: ViewerOptions.role

   Optional ARIA role assigned to the canvas, for example ``'img'``.

.. js:attribute:: ViewerOptions.ariaLabel

   Optional accessible canvas label. Describe the model; built-in controls
   have their own labels and keyboard semantics.

.. js:attribute:: ViewerOptions.renderMode

   ``'continuous'`` (default) or ``'on-demand'``. On-demand renders explicitly
   without a background animation-frame loop and requires **all four**:
   ``animation: 'external'``, ``autoplay: false``, ``driverControls: 'none'``,
   ``partControls: 'none'``. It accepts only externally posed documents without
   instructions, a running program or a clocked machine. Invalid combinations
   reject the mount. Use it for controlled stills, not interactive simulation.

Running options
===============

.. js:attribute:: ViewerOptions.run

   Optional object configuring a running document. It does not turn a posed
   model into a simulation or configure a clocked machine.

.. js:attribute:: ViewerOptions.run.dt

   Positive finite simulated seconds per tick; default ``1 / 240``. Fixed
   for the lifetime of the mount. Changing it requires a new mount and makes
   saved states from the old step size incompatible.

.. js:attribute:: ViewerOptions.run.record

   Number of recent ticks to retain, default ``600`` (2.5 seconds at the
   default step). A positive integer enables bounded recording; ``null``
   disables recording. It is not an unlimited history or a seek control.

.. js:attribute:: ViewerOptions.run.autostart

   Boolean, default ``false``. Start advancing the running simulation after
   mounting. Independent of the ordinary timeline's ``autoplay`` option.

.. js:attribute:: ViewerOptions.run.nudge

   Optional object configuring what the built-in nudge buttons request.

.. js:attribute:: ViewerOptions.run.nudge.amount

   Finite relative travel in design units, default ``1``. The positive/negative
   buttons choose direction. Setting the option does not move a coordinate.

.. js:attribute:: ViewerOptions.run.nudge.seconds

   Finite nonnegative simulated duration, default ``0.2`` seconds.

.. js:attribute:: ViewerOptions.run.jog

   Optional object configuring built-in hold-to-jog requests.

.. js:attribute:: ViewerOptions.run.jog.rate

   Finite rate in design units per simulated second, default ``1``.
   Releasing a jog control cancels its request.

Example: external still
=======================

.. code-block:: javascript

   const viewer = await MachinomeViewer.mount('#still', 'export/manifest.json', {
     renderMode: 'on-demand',
     animation: 'external',
     autoplay: false,
     driverControls: 'none',
     partControls: 'none',
     time: 0.25,
   });
   viewer.setView({ camera: [80, -60, 40], target: [0, 0, 0] });
   // Capture/read the rendered canvas, then release it.
   viewer.dispose();
