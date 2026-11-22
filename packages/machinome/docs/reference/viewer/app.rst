==============
A model's app
==============

.. needs:: viewer

A model may carry its own app: a React application kept in the project's
source beside the model, which the viewer shows in place of its automatic
panel. :doc:`/howto/give-a-model-its-app` walks through writing one; this page
is the lookup for what an app imports and what the viewer does with it.

Where an app is shown
=====================

The viewer shows a model's app wherever it would present its own operating
panel: the export page, the ``machinome develop`` page and a host page that
mounts the viewer with the default options. The app takes the place of every
automatic panel (posed, running or clocked), of the instruction buttons and of
the animation bar. A mount with ``driverControls: 'none'`` shows neither the
panel nor the app and requests no file of the app; so does every on-demand
mount, a still taken with ``machinome snapshot --viewer web`` among them. The
handle is whole either way.

The app fills the area the host gave the viewer and places the model's picture
where it renders ``<Viewport/>``. The inspector's sidebar and navigator stay
beside it, the picture can be orbited, declared part controls stay touchable,
and full screen takes the whole app with its picture, the full-screen control
standing in the picture's corner.

The helper
==========

An app imports its own files, ``react``, ``react-dom`` and the helper
``@machinome/viewer/app``, which offers four names:

.. code-block:: tsx

   import { Viewport, useMachine, usePlay, useViewer } from '@machinome/viewer/app';

.. js:function:: Viewport({className, style})

   A component rendering a ``div`` into which the viewer moves the model's
   picture: the canvas and its corner full-screen control. The app sizes the
   ``div`` through ``className`` or ``style``; the picture takes its size and
   follows it as it grows and shrinks. An app renders one. An app that renders
   none is refused: *it places no <Viewport/>, so the model would not be seen*.

.. js:function:: useMachine()

   Return ``{bank, drawing}`` for a clocked machine: ``bank`` is the committed
   bank, frozen, keyed by qualified ID in native units, as
   :js:meth:`MachineHandle.state` answers it; ``drawing`` is whether a
   transition is being drawn, as :js:meth:`MachineHandle.drawing` answers it.
   While a transition is drawn the bank already stands at its end.

   The component re-renders after every change of either, whoever made it: the
   app itself, a script on the host page, the clock's transport, the end of a
   drawing, a republished document. Between two changes it gets the same object
   again. On a model that is not a clocked machine it refuses the app: *this
   model is not a clocked machine; useMachine() reads a clocked machine's bank*.

.. js:function:: usePlay()

   Return a function ``play(name)`` that plays the declared instruction
   ``name`` as the panel's button does: one request, its transition drawn over
   the instruction's declared duration. It returns the ``ClockedRequest``; a
   request the machine refuses throws the machine's own error, for the app to
   report where it wants, and changes nothing. On a model that is not a
   clocked machine it refuses the app: *this model is not a clocked machine;
   usePlay() plays a clocked machine's instructions*.

.. js:function:: useViewer()

   Return the mount's :doc:`ViewerHandle <viewer-handle>`, whole, on any
   model: an app can read the assembly, move the camera, drive a posed or
   running model through its handle, or subscribe to
   :js:meth:`ViewerHandle.onMachineChange` itself.

An error thrown while the app renders refuses it: *it failed as it rendered:*
followed by the error's message.

An app's stylesheet applies to the whole page it is shown in, the Studio's or
a host's included. Scope its selectors under the app's own root class.

What the reader sees when an app cannot be shown
================================================

When the app cannot be shown, the viewer draws the model filling its area and,
over it, a notice reading *This model's app is not shown:* followed by the
reason; the same sentence goes to the browser's console. No automatic panel is
drawn in the app's place, and the mount completes. The reasons are listed in
:ref:`viewer-app-refusals`. A document whose ``app`` record is malformed is
refused as a whole, naming the record.

When a document is republished, an app whose files are unchanged keeps
running, with its own state; an app whose files changed is replaced, the
picture standing in between; and the panel returns when the document names no
app any more.

The contract an app bundle speaks
=================================

The viewer bundles an app itself, so an app's author writes components and
never this contract; it is stated here for a host that builds its own.

A bundled app is a classic script. As it runs, it dispatches the event
``machinome:app`` on its own element, ``document.currentScript``, with the
detail ``{contract: 1, start}``. After the script loads, the viewer calls
``start(host)`` with ``host = {contract, element, viewport, viewer, refuse}``:
the element the app fills, the picture's element, the mount's handle and a
function ``refuse(reason)``. ``start`` returns a function the viewer calls
when it takes the app away. No global name is claimed, so two viewers on one
page can show two apps.
