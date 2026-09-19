.. _status-and-roadmap:

Project status and direction
============================

**Machinome 0.7 is in release preparation.** It continues the published
solid-node 0.6.0 release under the Machinome name and the
`machinome GitHub organisation <https://github.com/machinome>`_.
The framework package declares 0.7.0; that version in a source checkout
does not mean it has been published.

What the 0.7 source implements
------------------------------

The framework describes machines through shared parameters, named
assemblies, joints, mechanical relations, drivers and instructions.
It supports direct poses, running simulations and event-driven machines
with stored state. Geometry and operation are checked in Python, and
versioned exports carry them to the independent browser viewer.

The development has been empirical and agent-assisted. Clock gear trains,
printer axes, calculator registers and interlocks supplied concrete
requirements for the declarations and simulation rules. The
:doc:`tutorial <quickstart>` starts with a small model; V8,
Metamaquina 2 and Clock 01 are the three :doc:`external examples <examples>`.

Exact STEP parts and assembly import, sheet cutting profiles, flexible
parts, surface markings, named project models, native geometry builds
and incremental artifact reuse are implemented. They are not future
roadmap items. See :doc:`changelog` for the release summary.

Package boundaries
--------------------

Machinome is Apache-2.0. Machinome Viewer is an optional, independent
AGPL-3.0-only package. Its current matching source is 0.2.0, API 20,
supporting document schemas 1–8; it is still unpublished. The framework
builds and tests without it, while interactive browser development
requires it.

Machinome Studio is a separate experimental harness. It remains
unpublished; the reserved ``studio`` extra is not yet an installable
route from a package index. Browser-delivery experiments are not a
released framework capability.

Limits and direction
----------------------

Linux is the validated development platform. The framework remains
pre-1.0, so read :doc:`upgrading` before changing versions.

Simulation describes declared kinematics, state transitions and stops.
It is not a general dynamics solver. Geometric tests and static support
checks establish their stated contracts, not material strength, friction,
manufacturability or physical safety. The example simulations do not
claim that every design has been manufactured or physically validated.

Further work follows findings from real machines: performance on larger
assemblies, useful manufacturing information, inspection and mechanical
contracts. These are directions, not promised release features.
