Run tests fast
==============

Every intersection, containment, connectivity and weld question a test
asks is decided by one of two engines, and which one is a property of the
run, not of the model.

.. _comparison-engine:

The two engines
---------------

The **B-rep** engine compares two parts that have B-rep geometry, a
boundary representation (CadQuery, build123d, STEP, sheet and molejo
parts), on their solids. Boundary contact is exactly empty, a nominally
exact fit is not interference, and there is no tolerance anywhere. It is
the default, and the engine a release or a CI run uses.

The **mesh** engine compares every pair on the parts' meshes, the path a
part without B-rep geometry always takes, at tessellation precision. It
is the fast development loop: a flexible part such as a valve spring
costs about 14 ms per comparison on meshes against about 430 ms on the
B-rep engine, and on one engine's root suite the run went from 28 minutes
to a minute and a half with the same verdict on every comparison.

Select the engine
-----------------

.. code-block:: bash

    $ machinome test --mesh
    $ machinome test --brep

Without a flag the ``SOLID_TEST_ENGINE`` environment variable decides
(``brep`` or ``mesh``), and without that the run is on the B-rep engine.
The ``machinome`` command loads the project's ``.env`` at startup, so
record the fast loop once, in that ignored checkout-local file:

.. code-block:: text

    SOLID_TEST_ENGINE=mesh

A CI runner has no such file and needs no configuration: its runs are on
the B-rep engine. ``machinome new`` ignores ``.env``, so the choice never
travels.

The mesh engine is installed by the ``mesh`` extra (``pip install
"machinome[mesh]"``, or ``machinome[all]``). Without it a run on the mesh
engine refuses at its start, before it builds anything, naming that line.
A run on the B-rep engine needs it only for a pair it compares on meshes,
one with a part that has no B-rep geometry.

A run on the mesh engine says what it is: a line before the first build
names the engine, and the summary line ends with ``(mesh engine, volume
epsilon E mm³)``, so a green fast run is never mistaken for a B-rep one in
a log or a commit message. A mesh verdict is at the precision of the STL
tessellation, a chord may deviate from the true surface by up to 0.1 mm,
so a clearance thinner than that can read as overlap and interference
thinner than that can be missed. Commit evidence and release checks come
from the run on the B-rep engine.

The volume epsilon
------------------

Where solids meet exactly, a boss seated on a plate, a shaft at zero
nominal clearance in its bore, their meshes overlap by slivers the B-rep
engine never sees. The volume epsilon is your stated size for that noise:

.. code-block:: bash

    $ machinome test --mesh --volume-epsilon 0.5

or ``SOLID_TEST_VOLUME_EPSILON=0.5`` beside the engine line in ``.env``
reports every intersection of at most 0.5 mm³ as empty for the whole run,
before any assertion reads it. The default is 0, and a project whose
clearances exceed the tessellation deviation needs none. The epsilon
exists only for the mesh engine; the B-rep engine refuses it, because it
has nothing to absorb. It is not a production allowance: where parts
must run free, encode physical clearance in the model and state a fit
contract with a manufacturing margin in length.

.. _placement-quantum:

The placement quantum
---------------------

Every intersection verdict is remembered: two comparisons of the same
pair in the same relative placement are one question, answered once in a
run and kept for the next (see :ref:`verdict-store`). "Same placement" is
decided by the pair's relative matrix, and
recomposing one rigid motion by two multiplication orders leaves float
noise between the results, around 1e-13 on a real assembly, so keyed on
exact bytes a sweep re-asks a question it already answered.

The **placement quantum** absorbs that noise: the relative matrix is
divided by the quantum and rounded to integer cells, and two placements
in the same cell are one question.

.. code-block:: bash

    $ machinome test --placement-quantum 1e-9

or ``SOLID_TEST_PLACEMENT_QUANTUM`` in ``.env``; the default is 1e-9 mm,
and ``0`` restores the exact-bytes key. Unlike the epsilon it applies
under both engines, because it identifies a question rather than a
quantity of material. At the default, two placements sharing a cell move
every point of one solid by at most a few nanometres at metre scale, far
below the B-rep engine's own precision or any clearance a machine is
designed to hold; a pair that straddles a cell boundary simply misses and
recomputes. Raising it well past the default is a judgement about
arithmetic noise, never about material, and the run names a non-default
quantum on its summary line.

.. _verdict-store:

Verdicts kept between runs
--------------------------

A second run of an unchanged project does not ask its questions again.
Every verdict a run decides is kept in the ``.verdicts`` directory of the
project's build directory (``_build/.verdicts`` by default), and a later
``machinome test`` that asks the same question of the same state is
served the kept verdict without running a boolean. Most of a slow suite's
time is spent deciding verdicts, so the second run of a suite that took
twenty minutes can finish in well under one. Every model a project
declares shares the one store, so a part two models build identically is
decided once.

A question is identified by state, never by a path or a time:

* a rigid part by the content of the artifact its compared geometry was
  read from, the ``.brep`` on the B-rep engine and the ``.stl`` on the
  mesh one. A rebuild that reproduces the same bytes, or a project
  moved or copied with its build directory, still reuses the store; a
  part whose content changed is a new question, even if its file kept
  its modification time and size;
* a flexible part by its bound values and its shape specification,
  together with the content of the sources that define it, so the same
  spring at the same length is the same question and at another length a
  new one;
* the pair's relative placement, rounded by the placement quantum as
  above, the engine, and the quantum itself.

Each kept verdict is also bound to the framework's own source code, to
the installed versions of the geometry kernels and of molejo, and to the
platform. Upgrading the framework or a kernel, or editing the framework
in a development checkout, starts the store afresh with no action from
you; the first run after it costs what a first run costs.

The store never changes a verdict. It keeps the engine's own answer,
emptiness, volume and which engine decided it, and the volume epsilon is
applied after a kept verdict is read, exactly as after one decided in the
same run: a flush contact still comes back non-empty at 0.0 mm³ and still
fails at the strict default. A comparison whose answer cannot be tied to
state, or whose artifact changed after it was read, is simply decided
again. Two runs of one project at once are safe, and a damaged, foreign or
unwritable store is ignored rather than reported.

To run without it, for a measurement or an experiment that patches the
framework, pass ``--no-verdict-store`` or set
``SOLID_TEST_VERDICT_STORE=off`` in ``.env``; ``--verdict-store`` turns it
back on for one run. Such a run neither reads nor writes the store, and
says so at the end of its summary line with ``(verdict store off)``. A run
with the store on prints exactly what it printed before the store
existed. Deleting the ``.verdicts`` directory is always safe: the next
run decides again what it is no longer served, and reaches the same
verdicts.

More levers
-----------

* Test a justified slice of a repeating motion rather than a sparse full
  cycle: ``@testing_steps(4, end=0.125)`` covers one eighth of a turn
  where the geometry repeats.
* Under a scenario, ``sim.cadence_costs`` reports what each cadence cost,
  so an expensive geometric check is a visible, chosen expense.
* Declare coarser ``angular_deflection`` on vendor STEP parts: fewer
  triangles in every mesh comparison (:doc:`imported-parts`).
* A whole-model ``assertNoSolidInterference`` costs by interacting pairs,
  not by total triangles: a sweep-and-prune index emits only pairs whose
  bounds overlap, and a pair whose surfaces come nowhere near each other
  is decided empty without a kernel call.
