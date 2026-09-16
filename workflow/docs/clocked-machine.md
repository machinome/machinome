# The clocked machine: untimed plus memory

**Status:** design note recording a direction the pilot settled in
conversation on 2026-09-16, with the context the next agent needs to cut a
proposal from it. Nothing here is ratified. It does not name an API spelling,
does not authorize a change to `Time.running()`, and does not claim the fast
Curta is already a clocked machine. Where this note and a baseline spec or an
accepted ADR disagree, the note is stale.

Written against framework `main` `debd760` (ADR-124 highest), viewer `main`
`4a63aaa` (ADR-061 highest, API 16, documents 1..7), and the originating
project `projects/Calculators/Curta-Type-I-3x` on branch `direct-operation`
at `9fb725f` (with `pyproject.toml` dirty: the manifest's models table).

## The finding

The Curta carries two models, both declared in its manifest:

- `fast_curta` (`simulation/curta.py:Curta`): every part position is a
  closed-form expression of the drivers. `initial_result`, `initial_turns`,
  `operand`, `crank_turns`, `subtract`, `carriage_position`, `clear` go into
  `simulation/arithmetic.py:calculate`, which returns the settled registers,
  and `simulation/cycle.py:dial_positions` prescribes the in-stroke wheel
  motion from those same values. It is fast in both runtimes because it is
  one expression-DAG evaluation per pose. It does not operate: turning the
  crank past a revolution does not carry the result forward, so the maker
  edits `initial_result` and `crank_turns` by hand.
- `operating_curta` (`simulation/running.py:OperatingCurta`): `Time.running()`
  with the direct-operation controls of
  `simulation/docs/direct-operation-2026-09-15.md`. Registers are the
  retained angles of the real wheels, carries are lever travels latched by
  the measured cam profile and released by the wheel's own angle
  (`simulation/running_laws.py`). It operates, and it is the model that
  produced every Curta finding the framework took up (ADR-121, ADR-123,
  ADR-124). After the `curta-speed` campaign it still costs about 0.73 s per
  0.1 s Python tick and about 40 ms per crank tick in the browser at
  `dt = 1/240`, which is well behind real time (`workflow/warts.md`,
  "Originating Curta follow-up: seconds per Python tick").

The pilot's question was whether the operating machine can have the fast
machine's speed. The answer settled in conversation is that the Curta is a
**clocked machine**: a few retained values, closed-form positions between
events, and a commit of the retained values at each event. Its interlocks
hold the selectors, the carriage and the clearing ring while the crank is off
rest, so nothing about its state changes except at the end of a stroke. The
running executor pays for generality the Curta does not use: it retains every
coordinate and locates jumps on every coordinate at a fixed cadence.

## The direction

A third state discipline, next to "none" (untimed and looping poses today)
and "integrated" (`Time.running()`): **memory**. The pilot's words for it:
"untimed plus memory", and "declared state again, but this time in the right
place, not disrupting the `Time.running()` architecture that is pure
simulation by ticks".

1. **A state variable is a driver written by the machine, not by the
   maker.** It enters expressions exactly as a driver does; the fast Curta's
   `initial_result` and `initial_turns` are already that, minus the writing.
   It is not a control and never appears as a handle in the panel: the
   direct-operation redesign removed the register-editor sliders on purpose
   and this does not bring them back. It is settable through a snapshot or
   session setup, and readable as the machine's readout.
2. **A commit law writes it at an event.** The event is a crossing of an
   expression of the machine's inputs (a crank angle crossing a multiple of
   360, a pendulum phase crossing its release point). Inputs are monotone
   between the maker's requests, so the crossing is located exactly, with
   none of the search the running executor performs for self-reads. The
   commit evaluates the law at the crossing, reading the pre-event state of
   every state variable (synchronous update, as clocked registers do), and
   the pose continues from the committed values. Several crossings inside one
   request commit in order, each reading the state the previous one left.
3. **Between events nothing is retained.** Every position is the existing
   expression DAG evaluated at the current inputs and the current state. The
   viewer already evaluates that DAG per frame for the fast Curta; the Python
   `Sim` already evaluates it per pose. The addition on both sides is the
   commit at the crossing, not a new executor.
4. **A held value is a state variable whose commit is a fold, not an
   event.** Partial clearing on the Curta needs the ring's furthest reach
   during a sweep, or reversing the ring un-clears the dials it already
   zeroed. That is one scalar `max` over the sweep. It is still one cheap
   retained value; it is not a reason to integrate the machine.
5. **Interlocks are expression bounds.** ADR-113 admits a bound that reads
   other coordinates. The selectors, carriage lift and clearing ring get a
   range that closes while the crank is off rest. This is what makes the
   closed form honest: without the locks, moving a selector at a crank phase
   of 180 degrees would retroactively move a tooth that had already passed.
   Where the real machine permits a mid-stroke action, the closed form is
   wrong there and the audit of the interlock list is the acceptance work.
6. **Snapshot and replay improve.** A snapshot is inputs plus state; a replay
   is the input history; events are exact crossings of monotone inputs. That
   is a stronger determinism claim than the run's, whose result depends on
   `dt`.

## Time without running

`Time.running()` today bundles two decisions: ADR-104, a time base of
elapsed seconds that never wrap, and ADR-105/106/107, the mechanics that
retain every coordinate and integrate every law. The clocked machine needs
the first without the second whenever time is one of its inputs. A pendulum
is a formula of elapsed time; a counter beside it is a state variable
committed when the pendulum's phase, an expression of time, crosses its
release. Events on time and events on inputs are the same kind of event.

The honest decomposition is therefore two axes, and the current API ties
them:

| time base | none | memory | integrated |
| --- | --- | --- | --- |
| untimed | poses today | the Curta | — |
| looping (`Time(loop=)`) | the clocks today | refused, or a replay from a snapshot at each wrap | — |
| elapsed (ADR-104) | — | pendulum plus counter | `Time.running()` |

Memory and looping time do not mix: a loop that replays from zero replays
every commit and the state climbs across loops. Take the refusal first; a
looping demo that restores a snapshot at each wrap is a demo need that has
not appeared yet. Whether the time base and the state discipline become two
declarations, or `Time.running()` stays as the sugar for elapsed plus
integrated, is for the proposal.

## Clocked inside `Time.running()`

Semantically admissible and worth nothing for speed. A running machine
already retains every coordinate, and a value committed at an event is, in
running terms, a self-read law whose value changes only through a switch:
exactly what ADR-121 admitted and exactly how the operating Curta's wheels
work. So the run subsumes the clocked discipline; a state declaration under
`Time.running()` would compile to that self-read switch law, one retained
coordinate among all the others, while every other coordinate is still
integrated at the cadence. Mixing the two does not give a running machine the
clocked machine's speed.

The one reason to define the meaning anyway is portability: a project should
write "this register is a state committed at the stroke end" once and have
it mean the same under a clocked root and a running root, so a machine proven
running can be shipped clocked without rewriting its state. Define that
meaning in the proposal; implement it when a project needs it.

## Why `Time.running()` stays

Running mode is the evidence mode and the clocked mode is the delivery mode.
The operating Curta composes its arithmetic from local laws, so that the
machine adds is an outcome that can fail, and the findings the framework took
up came from that. A clocked model's commit law already contains the answer:
it can show the mechanism but cannot discover that the mechanism fails to
add. Running mode also keeps what the clocked mode cannot express:
path-dependent state with no closed form (accumulating backlash, a follower
that leaves its cam, slip), stops solved from the group of inputs that push a
coordinate (ADR-108), and the 0.9 dynamics stage of `roadmap.md`, where
velocities are retained and integrated. A pendulum whose amplitude depends on
the impulse it receives is not clocked; it runs.

The relationship to record: running is the interpreter over the parts;
clocked is the program the pilot compiles from it once the parts have proven
it. Its contract is a test: the clocked model's commit law must agree with the
running model's readout at every stroke end, across one shared scenario
corpus. That is the condition for a project to keep both models, and it is a
documented pattern, not a default. A project with no memory (the clocks, the
robots, the printers) keeps its pose formula; a mechanism under study keeps
only its running model; the Curta keeps both, with `simulation/cycle.py`
already shared between them. The risk of two models is drift, and the shared
corpus is the mitigation.

## What a proposal has to settle

- The declaration of a state variable and of its commit law and event, on the
  root, in the spirit of `Driver`, `Port` and `.drives(law=)`. No per-relation
  protocol, no event objects inside laws: that was the `running(r)` protocol
  the pilot rejected on 2026-09-13
  (`workflow/open-run-simulation/design.md`, "Decision 2026-09-13"), and the
  difference here is that a state is a value with one commit law, and the
  author writes the closed forms they already write.
- Commit semantics: synchronous reads of pre-event state, ordered commits for
  several crossings in one request, the fold form for held values, and what
  happens when a commit law reads a state variable that another commit law at
  the same event writes.
- Exactness of the crossing: a crossing of an affine expression of a
  monotone input is solved; a crossing of a curved expression of time (a
  pendulum phase) is located by the machinery ADR-123 already applies to
  pieces, and the commit reads the pose at the located point.
- Memory across pose requests in the untimed `Sim`, which today has none; and
  the refusal of memory under a looping time base.
- The document: a new version (not additive) carrying state variables, their
  initial values, commit laws and events; the viewer's execution of the commit
  on its existing expression DAG; and a conformance corpus scenario set for
  it, on the pattern of ADR-111. Two changes in two repositories.
- The meaning of a state declaration under `Time.running()`, defined and
  not implemented.
- The interlock audit for the Curta as the first acceptance target, and the
  oracle test against `operating_curta`'s readout.

## Before the proposal: a project-level spike

Do this first, in the Curta repository, on its own branch, with no framework
change. Wrap the fast Curta's `Sim` in a small harness that detects crank
crossings of 360 and writes `initial_result` and `initial_turns` from the
`result` and `turns_counter` ports, holds the clearing reach, and closes the
selector, carriage and ring ranges while the crank is off rest. Then replay
the scenarios the running tests already cover (`simulation/test_running*.py`:
the page-53 calibration sequence, carries and borrows through both banks,
subtraction with the reversing lever at every carriage position, partial
crank release and resume, partial clearing in both directions, mechanically
blocked attempts) against both models and compare readouts at every stroke
end. Measure both. Each disagreement is either a missing interlock in the
harness or a place where the Curta is not a clocked machine; that list, with
the measurements, is the requirement the proposal is cut from. Record the
spike's result here before opening the change.
