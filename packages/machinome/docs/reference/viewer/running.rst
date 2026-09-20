================
Running machines
================

``viewer.run()`` returns a ``RunHandle`` when the document carries a running
program (versions 5, 6, 7, 9 or 10). It returns null for posed and clocked models.
The run retains a coordinate bank and advances in fixed ticks, normally in
a worker. Use the handle as an interface; do not import its internal engine.

Autonomous retained motion
==========================

A version 10 document can declare running time drives. Advancing the run gives
each such relation its own share of elapsed time without a host ``rate()``
command. Mounting still starts paused; call ``start()`` or ``step()`` to advance.
Time is read-only simulation time, not an operator driver or a bank coordinate.
Only the model's declared operator inputs appear in ``viewer.drivers()``.

A model's stop/enable input and the transport's ``pause()`` are different:
disabling a relation can hold its position while elapsed time continues;
pausing the transport stops ticks altogether. Each time drive admits motion
independently. A bound that stops one does not stop an unrelated drive, and the
stopped relation retries at the next tick's current global time without catching
up the skipped interval. For nonlinear laws this is not a resumable local phase.

Zero-duration operator moves, such as winding Astrarium while stopped, do not
advance time. The ordinary bank, tick and commands suffice for save/restore/reset;
there is no extra hidden time-drive state. These are declared kinematic
relationships, not inferred dynamics, torque or energy conservation.

Read the run
============

.. js:method:: RunHandle.identity()

   Return the published program identity string. A changed mechanical program
   is not interchangeable with the one that produced a saved state.

.. js:method:: RunHandle.dt()

   Return simulated seconds per tick, fixed by ``ViewerOptions.run.dt``.

.. js:method:: RunHandle.tick()

   Return the current committed tick number.

.. js:method:: RunHandle.elapsed()

   Return elapsed simulation seconds. This never wraps at 1 or at a loop end.

.. js:method:: RunHandle.state()

   Return a copy of the latest committed bank keyed by qualified ID. Input
   driver entries are in native units; mechanical coordinates use the units
   their published coordinate declarations describe. The bank is not a setter.

.. js:method:: RunHandle.coordinates()

   Return the coordinate declarations keyed by ID. Entries contain ``kind``
   (``'input'`` or ``'coordinate'``), ``initial``, ``unit`` and ``domain``
   (the last two can be null). Treat this table as read-only.

.. js:attribute:: RunHandle.runsInWorker

   Boolean reporting actual execution location. False means worker creation
   failed and the same engine is running asynchronously on the rendering
   thread. It does not mean the mechanical simulation was disabled.

Advance the run
===============

.. js:method:: RunHandle.start()

   Start earning simulation ticks from browser frame time; return ``void``.
   Does not issue an input request. Playback uses ``viewer.setSpeed()``.

.. js:method:: RunHandle.pause()

   Stop automatic advance and return ``void``. Retains bank and pending
   commands. Use ``cancel()`` if an input request should also be abandoned.

.. js:method:: RunHandle.running()

   Return whether automatic advancement is enabled.

.. js:method:: RunHandle.step(ticks)

   Integrate exactly ``ticks`` ticks (default 1) and return ``Promise<void>``
   after the result is committed. Works while paused or started; pause first
   for a deterministic script with no concurrent frame advances. Supply a
   nonnegative integer. A refused integration rejects the promise.

Request motion
==============

Input IDs are exact qualified names from ``viewer.drivers()``. A request
moves a declared input, not an arbitrary computed coordinate. Movement and
rates are in **design units**, unlike posed ``setDriver()`` values.

.. js:method:: RunHandle.move(input, request)

   Submit ``{by: travel, duration: seconds}`` or
   ``{to: target, duration: seconds}``. Exactly one of ``by``/``to`` is needed.
   Supply finite travel/target and a nonnegative duration representable as a
   whole number of ``dt`` ticks. Duration defaults to 0, which settles at the
   current tick without advancing time. Returns ``Promise<Outcome[]>`` when
   the command retires, **not when it is queued**. A zero-duration move publishes
   its committed frame before completion, so paused readouts and geometry update
   without requiring a subsequent tick.

.. js:method:: RunHandle.rate(input, rate)

   Submit a finite rate in design units per simulated second. Returns
   ``Promise<Outcome[]>`` when the command retires. Nonzero rates continue
   until stopped, cancelled or refused; ``rate(input, 0)`` stops the active
   rate command. Do not await a continuing rate as if it were an acknowledgement.

.. js:method:: RunHandle.trigger(name)

   Submit the named declared instruction; return ``Promise<Outcome[]>`` on
   retirement of its input commands. The instruction supplies targets/travels
   and duration. Unknown names and input-ownership conflicts reject the
   request; claiming one input twice is not implicit cancellation.

.. js:method:: RunHandle.cancel(input)

   Cancel the active command on that input; return ``void``. Cancellation is
   submitted in command order and is reported through outcomes. It does not
   rewind the admitted motion.

Only one command owns an input at a time. Release/cancel it before issuing
another command for that input. Distinct inputs can have distinct commands.
Invalid requests reject their promises with an explanation. A command that
retires returns outcomes shaped as:

.. code-block:: javascript

   { handle: 1, input: 'units_entry', status: 'completed', admitted: 1 }

``handle`` is the command identifier; ``admitted`` is actual travel in design
units. Terminal statuses are ``completed``, ``blocked``, ``refused`` and
``cancelled``. A blocked command can have admitted part of its requested
motion. Inspect the outcome instead of equating promise resolution with success.

Scripted example
----------------

For the committed Pascaline test export (whose input is ``units_entry``),
mounted with the default ``dt = 1 / 240``:

.. code-block:: javascript

   const run = viewer.run();
   if (!run) throw new Error('This example needs a running document');
   run.pause();
   const completion = run.move('units_entry', { by: 1, duration: 1 });
   await run.step(240);
   const outcomes = await completion;
   console.log(run.elapsed(), outcomes);

Do not await ``completion`` before calling ``step()`` on a paused run: no
ticks would execute. An interactive host can call ``run.start()`` instead.
Use your own model's declared IDs, units and suitable tick size.

Observe and save
================

.. js:method:: RunHandle.onCommit(listener)

   Subscribe to committed frames and return an unsubscribe function. A frame
   contains ``tick``, ``clock`` (elapsed seconds), ``bank``, ``moved`` IDs,
   ``crossings``, ``stops`` and current ``commands``. Readouts should follow
   these committed values, not extrapolate from the input request.

   A stop record's ``inputs`` lists real operator input IDs. Version 10 stops
   also carry ``time_drives`` when time admissions were blocked: a nonempty,
   sorted list of published time-drive IDs. That field is absent otherwise;
   older documents keep their existing stop-record shape.

.. js:method:: RunHandle.onOutcome(listener)

   Subscribe to retired ``Outcome`` objects and return an unsubscribe function.
   Observe both host requests and requests from the built-in panel.

.. js:method:: RunHandle.snapshot()

   Return ``Promise<RunState>`` containing ``program`` identity, ``dt``, ``tick``,
   ``bank`` and pending ``commands``. Treat it as a saved value, not editable
   live state. Await it before serializing.

.. js:method:: RunHandle.restore(state)

   Restore a snapshot; return ``Promise<void>``. An incompatible program or
   step size is refused. Pause before restoring when the host needs a stable
   inspection point; this is a session operation, not an animation seek.

.. js:method:: RunHandle.reset()

   Return ``Promise<void>`` after resetting to the program's initial bank and
   tick. Clears commands and retained history. Use ``pause()`` first when the
   host wants the reset state to remain still.

Disposing the parent viewer releases the run. Reacquire the handle after a
republish changes the program; do not keep operating an old execution session.
