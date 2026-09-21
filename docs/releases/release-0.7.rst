Machinome 0.7: Source code for machines
=======================================

Released on 20 September 2026.

Machinome gives a machine source code: its parts, their shared dimensions,
the relationships that connect them, and the rules by which the whole
machine operates. Geometry, motion and tests can be read and changed
together.

This is the continuation of solid-node 0.6.0. The framework and its GitHub
organisation have been renamed to avoid confusion with Tim Berners-Lee's
Solid project. Source now lives at
`machinome/machinome <https://github.com/machinome/machinome>`_,
and the distribution, import package and command are all ``machinome``.
The full history is retained.

Describe the whole
------------------

Version 0.7 adds a declarative language for shared parameters, derived
dimensions, children, guards and optional or repeated structure.
A joint states a body's freedom; a relation states how that coordinate
follows another. Ratios, mechanism laws and relations over several
coordinates connect motion across the assembly tree.

The work grew out of real models. Clock gear trains needed motion to
follow their declared ratios. Delta printers and parallel mechanisms
needed relations over several coordinates. Calculator registers needed
memory, and their interlocks needed to stop an operation where the
mechanism stops it.

Operate and remember
---------------------

A machine may be posed directly from its inputs, run through time,
or operated as a sequence of requests that retain state at events.
``Time.running()`` supplies running mechanics, including crossings,
jumps and mechanical stops. ``State`` and committing relations give
a clocked machine memory; ``Time.elapsed()`` adds a clock when its
events need one.

These are kinematic and state models, not a general physics solver.
Tests check the geometric and behavioural contracts the author states.
Physical validation and manufacturing decisions remain necessary.

Keep useful design source
---------------------------

The machine can contain exact CAD solids, imported STEP and STL parts,
sheet profiles and flexible parts. STEP assembly import turns a vendor
document's products and placements into editable project source.
Surface markings put numbers and artwork on parts without changing
their solids or printed-piece identity.

Native geometry builds, shared expression graphs and incremental artifact
reuse support the edit-and-test loop. Named models let a project keep
several assemblies with separate build directories.

Explore and share
------------------

The independent Machinome Viewer executes the published model in the
browser: direct input controls, running transport, or clocked requests
and state readouts as the machine requires. A static export carries that
experience to a web page. The matching viewer 0.7.0 reports API 23 and
reads schemas 1–10, including explicit running clearance pickup through
``Play`` and motion the running clock drives.

The manual teaches one machine from a part to a machine with memory, a
hand-cranked tally counter, then keeps how-to guides and concept pages
for the rules. Three examples, Metamaquina 2, the Pascaline module and
the Curta Type I, offer a posed, a running and a clocked machine to
inspect alongside their own source.

Adopting 0.7
-------------

Read :doc:`/project/upgrading` for the complete migration map. Update imports,
commands, project tables, environment settings and browser integration
together. No old import or command alias is installed. Constructor-based
models remain supported, so declarations can be adopted incrementally.

The framework remains Apache-2.0. The viewer is a separate AGPL-3.0-only
package selected by ``machinome[viewer]``; non-interactive builds and
tests work without it. The independent mechanics helpers have their own
extra. Machinome Studio remains experimental and unpublished.

See :doc:`/start/install` for installation and :doc:`/project/changelog`
for the capability summary and historical release notes.
