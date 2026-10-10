Machinome 0.8: a lean core
==========================

Released on 5 October 2026.

Machinome 0.8 changes how the framework is put together rather than what a
machine can say. A project installs only what its parts use, finds every
name at one address, and compares its parts on engines named for what they
consume. The machine you describe, the documents you publish and the
verdicts your tests reach are what they were in 0.7.

Install only what you use
-------------------------

A plain ``pip install machinome`` is the core: the node tree, motion,
simulation, the build and the test framework, with no CAD kernel. Each
kernel is an extra named for the module that needs it: ``machinome[cadquery]``
for ``CadQueryNode``, ``machinome[build123d]``, ``machinome[step]``,
``machinome[molejo]``, ``machinome[openscad]`` and ``machinome[solid2]`` for
the OpenSCAD family, and ``machinome[brep]`` and ``machinome[mesh]`` for the
two comparison engines. ``machinome[all]`` installs every one. A module whose
kernel is missing says so at the line that imports it, with the line that
installs it.

The tutorial's machine is CadQuery, so ``pip install
"machinome[viewer,cadquery]"`` is still all it takes to follow the manual.
:doc:`/start/install` lists every extra and what it installs.

One path for every name
-----------------------

Every name is imported from the module that defines it, and from nowhere
else: ``from machinome.node.assembly import AssemblyNode``, ``from
machinome.node.cadquery import CadQueryNode``, ``from machinome.node.frames
import Frame``. Each node type is one module under ``machinome.node``, named
for its technology. The package's root exports nothing, and a former
spelling fails at its import line with the line to write instead.
``machinome new`` and ``machinome import-step`` write their imports the same
way.

Two engines, named for what they consume
----------------------------------------

A test compares parts on one of two engines. The B-rep engine works on
boundary representations, the parametric surfaces of CadQuery, build123d,
STEP and sheet parts; it is the default, and what a release run uses. The
mesh engine works on triangle meshes, at tessellation precision, and is the
fast loop a developer selects with ``machinome test --mesh`` or
``SOLID_TEST_ENGINE=mesh`` in a checkout's ``.env``. Every operation on a
B-rep shape is the B-rep engine's, written on the OCCT kernel alone, and a
part's ``shape()`` is the kernel's own shape, so a B-rep part builds, fuses
and tests without CadQuery. :doc:`/howto/fast-tests` explains the choice.

OpenSCAD is one family among the node types
-------------------------------------------

``Solid2Node``, ``OpenScadNode``, the SCAD writer and the OpenSCAD snapshot
renderer are one node package, ``machinome.node.openscad``, with
``machinome.node.solid2`` over it, installed by their extras. The core
describes a node's presentation in its own terms and names no technology; a
build writes the ``.scad`` of an OpenSCAD-family part, from which OpenSCAD
renders its STL, and no other. A project of B-rep, STEP or STL parts needs
neither SolidPython nor OpenSCAD.

The leaf bases a node type written outside machinome subclasses are a
declared contract with a version, so such a package states the contract it
was written against and is refused, by name, when it does not match.

What is kept between runs
-------------------------

A second ``machinome test`` of an unchanged project is served every verdict
the first one decided: verdicts are kept under the build root, keyed on the
state of the parts rather than on a path or a time, and an upgrade of the
framework or a kernel starts the store afresh. Deleting ``.verdicts`` is
always safe (:ref:`verdict-store`).

An export records the commit it was made from, and whether the project had
changes beside it, so a page or a film can be held to the model it shows.
Production profiles turn the model you already have into a bill of
materials, stock, mass and maker instructions, without changing its
simulation.

Licence
-------

From this release Machinome is licensed |framework_licence|, at the
recipient's choice. The browser viewer is the separate ``machinome-viewer``
package, licensed AGPL-3.0-or-later and installed through
``machinome[viewer]``.

Upgrading
---------

0.8 removes and renames without aliases. :doc:`/project/upgrading` lists
every breaking change of 0.8 and what to change for each: the extras to
install, the import lines, the engine flags and the test variable, a node's
shape, the leaf contract, the OpenSCAD family's addresses and the modules
that are gone. A project's kept verdicts recompute once after the upgrade,
and a part whose module was rewritten rebuilds once, to the same bytes.
Exports keep document versions 1 to 13, so a 0.7 viewer reads them.

See :doc:`/project/changelog` for the complete list of what 0.8 brings.

0.8.1: corrections from real machines
-------------------------------------

Released on 10 October 2026.

Machinome 0.8.1 is 0.8.0 corrected by the machines built on it in its
first week. Testing a wall clock and a combination lock found the exact
checks slow where two parts touch and where every pair is measured: a
touching pair's empty common is now confirmed from the parts' nearest
boundaries before a slow classifier is asked, and distances run on every
core, so the clock's slowest pair takes half a second where it took over
five minutes. A build of a fresh checkout finishes, an edit behind a
library's ``__init__.py`` rebuilds what uses it, and a production reads a
built model once. Refusals and failing tests name what they concern: the
part by its path, the mate that states a range, the first failing instant,
the attribute a leaf must declare.

Nothing is added to the vocabulary and the published document does not
move: exports keep document versions 1 to 13, and the matching viewer
0.8.1 is 0.8.0 renumbered. A few corrections refuse what 0.8.0 let pass;
:doc:`/project/upgrading` opens with them and what to change, and
:doc:`/project/changelog` lists every correction.
