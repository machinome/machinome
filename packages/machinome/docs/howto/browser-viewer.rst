====================
Using the viewer
====================

The viewer presents the controls the model declares. A static part, a posed
mechanism, a running simulation and a clocked machine do not have the same
controls. A missing slider is not necessarily a missing feature: the machine
may only accept requests through its inputs.

Inspect the assembly
====================

Drag the canvas to orbit and use the wheel to zoom; right-drag pans the camera.
Open **Assembly** to see the model's named parts and subassemblies. Expand a
branch to inspect its children, use its visibility checkbox to hide or show
it, and focus a branch to frame and operate that portion of the machine.
**Full assembly** returns to the published root.

Hiding a parent hides its descendants on screen but keeps their own visibility
choices. Focusing another subtree does not discard those choices. A live
republish preserves paths still present; a removed focused node falls back
to the full assembly.

The tree is keyboard-operable: **Up/Down** move between visible rows,
**Home/End** go to the first/last row, **Right/Left** expand or collapse and
move through branches, **Space** toggles visibility, and **Enter** focuses
the selected node. Collapsing the sidebar removes its hidden controls from
keyboard navigation.

The standalone export starts with its sidebar collapsed. The development
page starts with it open. Narrow containers may need the sidebar closed to
leave room for the 3D model; the operating panel scrolls when its controls
do not fit.

Press **f** to watch the model full screen, or use the full-screen button;
press **Escape**, or the button again, to return. The button sits at the end
of a running machine's transport bar or the animation timeline when the
model has one, and otherwise as a small permanent control in the viewer's
bottom-right corner. Where the browser or the embedding page does not
permit full screen, such as an iframe without the permission, the button is
not shown and **f** does nothing.

Three kinds of motion
=====================

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Model
     - What you operate
     - What is retained
   * - Posed
     - Driver values and a 0–1 animation timeline
     - The selected pose, not a simulated history
   * - Running
     - Movement requests, jogging, instructions, run/pause/step
     - A coordinate bank advanced in fixed simulation ticks
   * - Clocked
     - One input request per gesture; an optional elapsed clock
     - Driver/state values committed by the machine's events

Posed models
============

Sliders and editable readouts control the drivers at the focused assembly
layer. Values are displayed in the design units the model declares. For
example, a motor can retain integer microsteps while its readout shows mm.
An instruction button moves one or more drivers to its declared targets.

A driver range controls slider presentation; it does **not** clamp direct
posed values. A model must express its own limits and constraints.

The animation timeline selects a normalized fraction from 0 to 1, independent
of the driver values. When the model declares a loop duration, playback follows
that duration at 1× and the readout shows machine time. Speed changes playback
rate. Without a loop, timing follows the document's frame count and frame rate.

Running machines
================

A running machine has memory: its coordinates are not arbitrary position
sliders. Use **nudge** to ask for a relative travel over a duration, hold
**jog** to request motion at a rate, or press a named instruction. Editing
the nudge amount, duration or jog rate configures the next request and does
not move the machine by itself.

The built-in input controls start a paused run when asking it to move.
**Pause** stops advancing simulation time; **Step** advances one tick;
**Reset** returns to the initial state. Playback speed changes how quickly
ticks execute, not the fixed size of a tick. The elapsed readout never wraps
like the posed timeline, and there is no history scrubber.

Requests report their outcome and admitted travel. A declared stop can block
motion; an invalid request can be refused. Do not treat every finished
request as reaching its target. Pausing or hiding the page does not secretly
accumulate an unlimited catch-up simulation.

If the model declares **Button**, **Turn** or **Slide** part controls, the
named parts are also touchable. Their highlight, tooltip and reachable drag
handles identify the available gestures. A visible part without a declaration
is not automatically a control.

Clocked machines
================

Each input gesture requests one movement. The machine solves that path,
applies events in order, and retains the result. State readouts are read-only:
they are written by the mechanism, not set directly by the viewer.
Mechanical stops can admit only part of a request. A refused request leaves
the committed bank unchanged.

The built-in panel draws a manual gesture at the tempo of the first declared
instruction that states a travel on that input. The drawing time scales with
the travel the machine admits. If no instruction states a travel on that input,
the panel uses a short interval (0.2 seconds). A pressed instruction is drawn
over its declared duration. Another gesture first lands the previous drawing.
This drawing illustrates an already solved request; it is not a second
simulation.

A model declaring an elapsed clock adds **Play**, **Step by seconds** and
**Speed** controls. Clock time only moves forward. A model without a clock
has no clock transport: its bank stands until you request an input movement.
The optional 0–1 animation timeline remains separate from elapsed seconds.
Reset/session operations are available to embedding hosts; the inspector does
not add a duplicate clocked Reset button.

During development
==================

When the framework republishes a model, the viewer updates the document and
changed geometry while keeping the camera and surviving inspection choices.
A build-error pane tells you what failed; fix the source and save again.
An offline banner means the development connection was lost and the visible
model may be stale. It does not mean that the still-visible geometry is a
successful current build. See :doc:`troubleshooting`.
