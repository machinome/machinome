=================
The viewer handle
=================

Returned by :js:func:`MachinomeViewer.mount`, or available as
``inspector.viewer``. Methods returning ``void`` are synchronous; await the
update methods that return promises. Stop using a disposed handle. After
republishing a different machine, reacquire ``run()``/``machine()`` handles.

Camera and lifecycle
====================

.. js:attribute:: ViewerHandle.apiVersion

   Integer API version implemented by this mount.

.. js:method:: ViewerHandle.view()

   Return a detached snapshot ``{camera, target}``, each a three.js vector
   with ``x``, ``y``, ``z``. Editing the returned vectors does not move the
   viewer. Pass the snapshot to a new mount or ``setView()``.

.. js:method:: ViewerHandle.setView(view)

   Adopt a ``ViewInput`` and render immediately; return ``void``. Available
   since API 21. Requires finite 3D camera/target vectors at distinct positions.
   Invalid input or a disposed viewer throws without changing the previous
   view. Preserves up vector, field of view, tree, machine state and timeline;
   a later read returns a fresh snapshot.

.. js:method:: ViewerHandle.dispose()

   Stop rendering, release geometry/materials, listeners and execution resources,
   and empty the mount container. Return ``void``. Dispose attached navigators
   first, or use the composing inspector's ``dispose()``.

.. js:method:: ViewerHandle.reload()

   Return ``Promise<void>`` after replacing the document/tree, preserving camera
   and orbit target. Use targeted updates below when only some content changed.
   Loading/parsing failures reject the promise.

.. js:method:: ViewerHandle.artifactChanged(path)

   Refetch one document-relative model path (for example ``'models/hub.stl'``)
   and replace the geometry of its referencing nodes. Return ``Promise<void>``.
   It does not add/remove nodes or reload the whole document. Camera, time and
   surviving navigation choices remain; fetch errors reject.

.. js:method:: ViewerHandle.manifestChanged()

   Refetch and reconcile the document in place; return ``Promise<void>``.
   Update placements/colors, add/remove nodes, and fetch geometry whose identity
   changed. Preserve view, timeline, and still-valid paths/driver values.
   A compatible republished running program keeps its state; changed machine
   identity can reset retained state. Inspect the new operating handle after
   republishing. Fetch/validation failures reject.

Assembly inspection
===================

Paths are arrays of sibling names **relative to the published root**, not
dot-separated strings. The root's own name is omitted: the spinner's hub is
``['Hub']``. ``[]`` names the root; ``null`` means full assembly for focus.
Use the paths returned by ``assembly()`` rather than deriving them from labels.

.. js:method:: ViewerHandle.assembly()

   Return an ``AssemblyNode`` snapshot of the whole published tree:
   ``{name, path, color, model, children}``. ``path`` is a string array;
   ``color`` is a string or null; ``model`` is a boolean indicating geometry;
   ``children`` recursively contains the same structure. No three.js objects
   or live mutable tree state are exposed. Throws if no assembly is available.

.. js:method:: ViewerHandle.setRoot(path)

   Focus and frame the subtree at ``path``, or the full assembly for ``null``;
   return ``void``. Unknown paths throw. Focus controls the visible/operable
   assembly layer without deleting the rest of the tree.

.. js:method:: ViewerHandle.setVisible(path, visible)

   Show/hide a known path; return ``void``. Unknown paths throw. Hiding a parent
   obscures descendants without rewriting their individual visibility choices.
   Focusing elsewhere does not clear explicitly hidden paths.

.. js:method:: ViewerHandle.navigation()

   Return a serializable snapshot ``{root: string[] | null, hidden: string[][]}``
   with the focus and explicitly hidden paths. Returned arrays are copies.
   It does not need a loaded tree and never throws. There is no
   ``restoreNavigation()`` method; reapply valid paths with ``setVisible()``
   and ``setRoot()`` if your host persists this state.

.. js:method:: ViewerHandle.onAssemblyChange(listener)

   Subscribe to accepted tree, focus and visibility operations. The callback
   receives ``{assembly, navigation}`` snapshots, including changes made by the
   built-in UI. Return value is a zero-argument unsubscribe function. This is
   an observation channel: do not drive the viewer from inside its callback.

Timeline and playback
=====================

.. js:method:: ViewerHandle.setTime(time)

   Set normalized timeline time, clamp to [0, 1], and render synchronously;
   return ``void``. Supply a finite number. It neither advances a running
   program nor seeks a clocked bank. Use ``animation: 'external'`` when the
   host owns this timeline so automatic animation does not overwrite it.

.. js:method:: ViewerHandle.speed()

   Return the current positive playback multiplier.

.. js:method:: ViewerHandle.setSpeed(speed)

   Set the multiplier and return ``void``. Nonpositive or non-finite values
   throw. Changes the rate of timed playback/running ticks/elapsed-clock play,
   never tick size or retained state. A loop-less posed document accepts the
   setting but does not use it until a timed loop is published.

Posed drivers and instructions
==================================

The posed driver table is distinct from a running or clocked **bank**. On
those models, use :doc:`running` or :doc:`clocked` to read and move retained
state. Direct posed writes do not issue mechanical requests.

.. js:method:: ViewerHandle.drivers()

   Return a copy of the declarations keyed by qualified driver ID. Each entry
   has ``default``, ``range`` (array or null), ``unit`` (string or null),
   ``dtype`` (for example ``'int'`` or null), and ``scale`` (number or null).
   Default/range are native values. For display, design value = native value
   × scale (or unchanged if scale is null).

.. js:method:: ViewerHandle.driver(id)

   Return the posed driver's current value in **native units**. Unknown IDs
   throw. This is not a read of a running/clocked bank.

.. js:method:: ViewerHandle.setDriver(id, value)

   Set a posed driver in native units and render immediately; return ``void``.
   Unknown IDs throw. The host must supply finite values and integer native
   values for integer declarations: this setter does not validate or round
   them for you. Ranges do not clamp. Setting a driver cancels an instruction
   ramp currently controlling that driver.

.. js:method:: ViewerHandle.onDriverChange(listener)

   Subscribe with ``(id, value) => ...``; values are native. Return an
   unsubscribe function. Reports posed edits and ramp changes, including
   built-in controls, not running/clocked bank commits.

.. js:method:: ViewerHandle.instructions()

   Return instruction declarations keyed by qualified name. An entry has
   ``duration`` in seconds and ``targets`` (absolute) or ``by`` (relative)
   mapping input IDs to **design-unit** values. The document discipline
   determines how an instruction executes.

.. js:method:: ViewerHandle.trigger(name)

   On a posed model, start the named instruction's ramps and return a
   ``TriggerHandle``. Unknown names throw. Clocked models explicitly refuse
   this method and direct callers to ``machine().trigger()``. Use
   ``run().trigger()`` for running models; the posed table is not their bank.

.. js:attribute:: TriggerHandle.done

   ``Promise<void>`` resolving when every ramp has landed, been cancelled or
   been replaced. Resolution alone does not prove the original target was
   reached. It is not a running request's outcome report.

.. js:method:: TriggerHandle.cancel()

   Stop this trigger's remaining ramps at their current values, settle ``done``,
   and return ``void``.

Operating handles and part controls
=======================================

.. js:method:: ViewerHandle.run()

   Return the :doc:`RunHandle <running>` for a running document, otherwise null.

.. js:method:: ViewerHandle.machine()

   Return the :doc:`MachineHandle <clocked>` for a clocked document, otherwise
   null. ``run()`` and ``machine()`` cannot both be non-null.

.. js:method:: ViewerHandle.controls()

   Return all declared part controls as ``PartControlView[]``, even with
   ``partControls: 'none'``; return ``[]`` if none are declared. Each includes
   ``name``, ``kind`` (``button``, ``turn`` or ``slide``), ``part`` and ``joint``
   paths, ``coordinate``, ``axis`` and ``origin``. A button names its
   ``instruction``; a motion control names its ``input`` and ``perUnit``.
   ``operationSpan`` may identify the motion's operation interval.

   ``rect`` is the current on-screen ``{x, y, width, height}`` or null when
   hidden/off-screen. ``point`` is a reachable ``{x, y}`` under the actual
   nearest-hit picking rule, or null; a rectangle's center may be a hole.
   ``gesturePoint`` is a reachable drag handle or null. These screen locations
   are **viewport CSS pixels**, matching browser pointer coordinates, not
   model units or pixels relative to the canvas. Read them again after camera,
   layout or machine movement. Treat the returned data as read-only.

   With viewer API 27, two ``Turn`` controls may name one part when they
   select different joints. Each has its own named drag handle and
   ``gesturePoint``. Dragging the undecided body requests neither turn;
   select the handle for the intended joint. Two turns selecting the same
   joint still refuse at load.
