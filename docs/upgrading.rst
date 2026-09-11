Upgrading from 0.6 to 0.7
=============================

0.7 is in preparation. Use a separate environment to try the preview
and keep the source revision with your project. See :doc:`quickstart`
for preview installation; do not assume the published 0.6 package
contains the APIs in this manual.

Update port imports
-----------------------

Ports now live in ``solid_node.motion.ports``, not
``solid_node.node``. There is no compatibility re-export:

.. code-block:: python

   from solid_node.node import AssemblyNode, CadQueryNode
   from solid_node.parameters import Length, Count
   from solid_node.motion.ports import RotationalPort, TranslationalPort, Time
   from solid_node.motion.joints import Revolute, Prismatic
   from solid_node.simulation import Driver, Instruction, Sim

Joints and relations are new ways to express motion, not a requirement
to rewrite every existing ``rotate()`` or ``translate()``.

Adopt declarations incrementally
------------------------------------

Constructor-based nodes still work. For new or migrated nodes, declare
typed parameters and children in the class body. The framework derives
parameter resolution, propagation, guards and build identity.

Keep CAD construction inside the leaf's ``render()``.
Moving to declarations does not require rewriting your CAD geometry.
See :doc:`declaring` for derived dimensions, repeated children,
optional structure and ``--set``.

If you used an unreleased declarative preview, import its parameter
kinds from ``solid_node.parameters``, not ``solid_node.node``.

Separate rest from motion
-----------------------------

Keep child creation and rest placement in ``render()``.
Move runtime bindings and transformations to ``simulate()``.
A legacy ``render()`` that reads time, drivers or ports remains
supported but warns and reruns per binding.

Do not reconstruct children in ``simulate()``, accumulate motion
from a previous instant, or use a driver as a build parameter.

Choose a time base
----------------------

Without a declaration, timeline time keeps its normalized 0–1 meaning.
Opt into seconds with ``time = Time(loop=<seconds>)`` on the root.
Update motion formulas and test spans together.

With that declaration, ``set_keyframe()`` and test decorators
take seconds. ``solid snapshot --time`` still takes a timeline
fraction. Stepped ``Sim`` time is always seconds and must lie
on its fixed tick grid.

Check joint frames in preview projects
------------------------------------------

A class-body joint is expressed in the declaring body's own frame.
A joint passed where a parent declares a child is expressed in that
parent's frame. If you used an earlier 0.7 preview with parent-frame
class joints, recheck anchors and axes; a translated body's default
pivot is now its own origin. See :doc:`motion` and :doc:`driving`.

Install a matching viewer
-----------------------------

The browser viewer is now the independent, AGPL-3.0-only
`solid-node-viewer <https://github.com/LibreSolid/solid-node-viewer>`_
package. The framework stays Apache-2.0 and works without it.
Install the ``viewer`` extra for browser development or widget exports.

Use a viewer supporting document schemas 1–4 for this framework source.
Repeated symbolic subexpressions can produce schema 4. Hosts that
bundle a widget should update it and check ``solid viewer``
instead of relying on an older bundle accepting a new document.
See :doc:`embedding` for the current API.

Verify the project
----------------------

Build every named model, rerun its mechanical and scenario tests, inspect
representative poses, and regenerate exports. A green state-only test
does not establish geometric fit. Treat changes to parameters, joint
frames and timing laws as design changes that need their own evidence.

The fresh-environment requirement in the 0.6 release notes concerns the
OCCT transition from 0.5; it is not a new 0.7 port-import requirement.
