Run tests fast
==============

Every intersection, containment, connectivity and weld question a test
asks is decided by one of two kernels, and which one is a property of the
run, not of the model.

.. _comparison-kernel:

The two kernels
---------------

The **exact** kernel compares two exact parts (CadQuery, build123d, STEP,
sheet and molejo parts) on their boundary-representation solids. Boundary
contact is exactly empty, a nominally exact fit is not interference, and
there is no tolerance anywhere. It is the default, and the kernel a
release or a CI run uses.

The **faceted** kernel compares every pair on the parts' meshes, the path
a part without exact geometry always takes, at tessellation precision. It
is the fast development loop: a flexible part such as a valve spring
costs about 14 ms per comparison on meshes against about 430 ms on the
exact kernel, and on one engine's root suite the run went from 28 minutes
to a minute and a half with the same verdict on every comparison.

Select the kernel
-----------------

.. code-block:: bash

    $ machinome test --faceted
    $ machinome test --exact

Without a flag the ``SOLID_TEST_KERNEL`` environment variable decides
(``exact`` or ``faceted``), and without that the run is exact. The
``machinome`` command loads the project's ``.env`` at startup, so record
the fast loop once, in that ignored checkout-local file:

.. code-block:: text

    SOLID_TEST_KERNEL=faceted

A CI runner has no such file and needs no configuration: its runs are
exact. ``machinome new`` ignores ``.env``, so the choice never travels.

A faceted run says what it is: a line before the first build names the
kernel, and the summary line ends with ``(faceted kernel, volume epsilon
E mm³)``, so a green fast run is never mistaken for an exact one in a log
or a commit message. A faceted verdict is at the precision of the STL
tessellation, a chord may deviate from the true surface by up to 0.1 mm,
so a clearance thinner than that can read as overlap and interference
thinner than that can be missed. Commit evidence and release checks come
from the exact run.

The volume epsilon
------------------

Where solids meet exactly, a boss seated on a plate, a shaft at zero
nominal clearance in its bore, their meshes overlap by slivers the exact
kernel never sees. The volume epsilon is your stated size for that noise:

.. code-block:: bash

    $ machinome test --faceted --volume-epsilon 0.5

or ``SOLID_TEST_VOLUME_EPSILON=0.5`` beside the kernel line in ``.env``
reports every intersection of at most 0.5 mm³ as empty for the whole run,
before any assertion reads it. The default is 0, and a project whose
clearances exceed the tessellation deviation needs none. The epsilon
exists only for the faceted kernel; the exact kernel refuses it, because
it has nothing to absorb. It is not a production allowance: where parts
must run free, encode physical clearance in the model and state a fit
contract with a manufacturing margin in length.

.. _placement-quantum:

The placement quantum
---------------------

Every intersection verdict is asked once per run and remembered: two
comparisons of the same pair in the same relative placement are one
question. "Same placement" is decided by the pair's relative matrix, and
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
under both kernels, because it identifies a question rather than a
quantity of material. At the default, two placements sharing a cell move
every point of one solid by at most a few nanometres at metre scale, far
below the exact kernel's own precision or any clearance a machine is
designed to hold; a pair that straddles a cell boundary simply misses and
recomputes. Raising it well past the default is a judgement about
arithmetic noise, never about material, and the run names a non-default
quantum on its summary line.

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
