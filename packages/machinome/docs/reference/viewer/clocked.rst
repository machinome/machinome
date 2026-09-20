================
Clocked machines
================

``viewer.machine()`` returns a ``MachineHandle`` for a version 8 clocked
document; otherwise it returns null. ``viewer.run()`` is null on this model.
One request moves one input, solves its path, applies events, and commits a
new bank. Calls are synchronous, not fixed-tick worker operations.

Read the machine
================

.. js:method:: MachineHandle.identity()

   Return the published machine identity string used to validate snapshots.

.. js:method:: MachineHandle.order()

   Return the bank's qualified IDs in document-defined order. Treat the result
   as read-only; do not infer declaration order from sorted object keys.

.. js:method:: MachineHandle.state()

   Return the committed bank as a copy, keyed by qualified ID, in **native
   units**. It can already hold an instruction's final state while its
   transition is still being drawn on screen.

.. js:method:: MachineHandle.drivers()

   Return the declared input-driver table. Entries have ``default``, ``range``,
   ``unit``, ``dtype`` and ``scale``, like ``viewer.drivers()``. Only declared
   drivers (and a declared clock) can receive movement requests.

.. js:method:: MachineHandle.states()

   Return the stored-state declarations in the same table shape. States are
   written by committing relations, not by ``move()`` or ``setDriver()``.

Request and inspect motion
==============================

.. js:method:: MachineHandle.move(input, request)

   Make ``{by: travel}`` or ``{to: target}``, in **design units**, and return a
   ``ClockedRequest`` immediately. Exactly one of ``by``/``to`` is required;
   values must be finite. Typed integer inputs convert once to native units
   with half-to-even rounding. Unknown IDs, state IDs, conflicting events or
   an invalid pose throw without committing a partial bank.

   Mechanical bounds clip admissible travel rather than forcing the requested
   endpoint. A zero-travel stopped request is still a valid result. Direct
   host ``move()`` lands immediately; it does not draw a timed transition.
   An active prior drawing is landed before the new request is made.

.. js:method:: MachineHandle.trigger(name)

   Execute the named instruction as one request and return its ``ClockedRequest``
   synchronously. Unknown names throw. The bank commits immediately, and the
   viewer **draws** that transition over the instruction's declared duration.
   Unlike ``move()``, this method deliberately starts a drawing. It returns no
   completion promise. Another request/session action first lands that drawing.

Request result
--------------

``ClockedRequest`` contains:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Field
     - Meaning
   * - ``input``
     - Qualified input ID.
   * - ``by`` / ``to``
     - The requested design-unit travel/target; unused field is null.
   * - ``origin`` / ``end``
     - Actual path endpoints in **native input units**.
   * - ``admitted``
     - Actual travel in **design units**.
   * - ``commits``
     - Events in path order. Each has ``relations`` names, ``fraction``,
       native input ``value`` and the ``targets`` it wrote.
   * - ``stops``
     - Encountered stops: ``coordinate``, ``side`` (low/high), evaluated
       ``bound``, coordinate ``value``, native ``input`` landing and
       request-path ``fraction``. Empty when no stop was met.

Use the returned endpoints instead of recomputing them from scale and admitted
travel: the exact floating-point landing matters at an event boundary.
Unlike a running outcome, this result has no ``status`` field. A refusal is
an exception, not a returned partially successful request.

Example: operate and restore
---------------------------------

For the committed calculator test export, which declares ``operand`` and
``crank`` inputs:

.. code-block:: javascript

   const machine = viewer.machine();
   if (!machine) throw new Error('This example needs a clocked document');
   const saved = machine.snapshot();
   machine.move('operand', { to: 4 });
   const stroke = machine.move('crank', { by: 360 });
   console.log(stroke.admitted, stroke.stops, machine.state());
   machine.restore(saved);

The test export is a calculator-shaped mechanics fixture, not a claim to be
the complete CAD assembly of a particular calculator.

Session operations
==================

.. js:method:: MachineHandle.snapshot()

   Return ``{identity, bank}`` as a saved ``ClockedSnapshot``. Bank values are
   native. Snapshotting during drawing reads the committed bank, not a visual
   interpolation frame.

.. js:method:: MachineHandle.restore(snapshot)

   Restore a compatible snapshot and return ``void``. A different identity or
   invalid bank is refused. Lands any active drawing first. Use this to return
   to an earlier session state rather than moving elapsed time backwards.

.. js:method:: MachineHandle.reset()

   Return to the declared initial bank, land any drawing and stop clock
   playback; return ``void``.

Elapsed clock
=============

.. js:method:: MachineHandle.clock()

   Return the declared elapsed-clock ID or null. The clock's bank value is
   elapsed seconds starting at zero, separate from normalized animation time.

.. js:method:: MachineHandle.clockPlaying()

   Return whether the elapsed-clock transport is playing. False on a machine
   without a clock; reading it requires no guard.

.. js:method:: MachineHandle.setClockPlaying(playing)

   Start/stop clock transport and return ``void``. Refused when the model
   declares no clock. Frames advance that clock in seconds, scaled by
   ``viewer.setSpeed()``. Pausing leaves the committed bank where it stands.

To advance a declared clock explicitly:

.. code-block:: javascript

   const clock = machine.clock();
   if (clock !== null) {
     machine.setClockPlaying(false);
     machine.move(clock, { by: 0.5 });  // one half-second request
   }

Backward clock requests are refused. ``viewer.setTime(0.5)`` changes the
ordinary timeline, not this elapsed clock.

Refused cadence verbs
=====================

.. js:method:: MachineHandle.step()

   Always throws: a clocked machine has no simulation tick. To advance a clock,
   request a number of seconds on its declared clock input.

.. js:method:: MachineHandle.rate(input, rate)

   Always throws: a clocked request has no continuing rate/cadence. Use a
   finite ``move()`` request or the clock's transport.

Disposing the parent viewer releases its machine presentation. Reacquire the
handle after publishing a different clocked machine.
