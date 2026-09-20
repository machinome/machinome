.. _status:

Project status and direction
============================

**Machinome |release| was released on |release_date|.** It continues the
published solid-node 0.6.0 under the Machinome name and the `machinome
GitHub organisation <https://github.com/machinome>`_; the distribution,
import package, command and configuration table are all ``machinome``.
:doc:`upgrading` maps the old names to the new.

What |version| is
-----------------

The framework describes machines through shared parameters, named
assemblies, joints, relations, drivers, instructions and controls. It
supports posed machines, running machines with retained history and
mechanical stops, and clocked machines with retained state written at
events. Geometry and operation are checked in Python, and versioned
documents carry them to the independent browser viewer.

Exact STEP parts and assembly import, sheet cutting profiles, flexible
parts, surface markings, named project models, native geometry builds
and incremental artifact reuse are implemented. :doc:`changelog` has the
release summary, and the :doc:`release note </releases/release-0.7>`
the story.

The development has been empirical and agent-assisted: clock gear
trains, printer axes, calculator registers and interlocks supplied the
requirements for the declarations and the simulation rules. Those
machines live in the `Machinome Foundry
<https://github.com/machinome-foundry>`_, the GitHub organisation that
keeps simulations of open-source machines built with the framework, each
beside the design it simulates and each stating the design's licence and
the simulation's. The three :doc:`examples </examples>` come from there;
browse the rest for a machine like yours.

Packages
--------

Machinome is Apache-2.0. Machinome Viewer is an optional, independent
AGPL-3.0-only package; the matching release is |viewer_version|, API
|viewer_api|, reading document versions |document_versions|, installed
through the ``viewer`` extra. The framework builds and tests without it;
interactive development requires it. Machinome Mechanics
|mechanics_version| is the optional helper package behind the
``mechanics`` extra. Both release with the framework.

Machinome Studio, the agent harness the framework is developed with,
remains experimental and unpublished; the reserved ``studio`` extra is not
an installable route from a package index. Browser-delivery experiments
are not a released capability.

Limits
------

Linux is the validated development platform. The framework is pre-1.0:
read :doc:`upgrading` before changing versions.

Simulation describes declared kinematics, state transitions and stops.
It is not a general dynamics solver. Geometric tests and static support
checks establish their stated contracts, not material strength,
friction, manufacturability or physical safety. The example simulations
do not claim that every design has been manufactured or physically
validated.

Direction
---------

Further work follows findings from real machines: production information
(process and material, from which mass follows), performance on larger
assemblies, inspection, and mechanical contracts. These are directions,
not promised release features.
