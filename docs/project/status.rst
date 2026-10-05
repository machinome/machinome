.. _status:

Project status and direction
============================

Machinome |release| was released on |release_date|. It continues
Machinome 0.7, the published continuation of solid-node 0.6.0 under the
Machinome name and the `machinome GitHub organisation
<https://github.com/machinome>`_; the distribution, import package, command
and configuration table are all ``machinome``. The :doc:`upgrading page
<upgrading>` lists every breaking change from 0.7 and maps the 0.6 names to
the new.

What |version| is
-----------------

The framework describes machines through shared parameters, named
assemblies, joints, relations, drivers, instructions and controls. It
supports posed machines, running machines with retained history and
mechanical stops, and clocked machines with retained state written at
events. Geometry and operation are checked in Python, and versioned
documents carry them to the independent browser viewer.

A plain installation is the core alone: each CAD kernel and node family is
an extra named for the module that needs it (:doc:`/start/install`), and
every name is imported from the one module that defines it. A test compares
parts on the B-rep engine, over boundary representations, or on the mesh
engine, over triangle meshes (:doc:`/howto/fast-tests`); the verdicts it
decides are kept between runs. OpenSCAD and SolidPython parts are one node
family among the others, installed by their extras. Leaves written outside
machinome subclass a declared, versioned leaf contract. Production profiles
read a bill of materials, stock, mass and maker instructions off the model,
and an export records the revision it was made from.

B-rep STEP parts and assembly import, sheet cutting profiles, flexible
parts, surface markings, named project models, native geometry builds and
incremental artifact reuse are implemented. A part declares its connectors
as frames and an assembly places it by a mate, one sentence that gives the
part its rest placement, its joint and the assembly its coordinate
(:doc:`/concepts/joints`); ``machinome vet`` checks that a project stays
inside the framework's universe (:ref:`vet`). :doc:`changelog` has the
release summary, and the :doc:`release note </releases/release-0.8>` the
story.

The development has been empirical and agent-assisted: clock gear
trains, printer axes, calculator registers and interlocks supplied the
requirements for the declarations and the simulation rules. Those
machines live in the `Machinome Foundry
<https://github.com/machinome-foundry>`_, the GitHub organisation that
keeps simulations of open-source machines built with the framework, each
beside the design it simulates and each stating the design's licence and
the simulation's, and are shown live on `machinome.org
<https://machinome.org/foundry/>`_; the :doc:`examples </examples>` page
says what to look for there.

Packages
--------

Machinome is licensed |framework_licence|, at the recipient's choice.
Machinome Viewer is an optional, independent AGPL-3.0-or-later package,
installed through the ``viewer`` extra. The framework builds and tests
without it; interactive development requires it. Machinome Mechanics
|mechanics_version| is the optional helper package behind the
``mechanics`` extra. Both release with the framework.

Running documents this release exports declare schema 11, source-timed
motion, schema 12 when they carry a ``Follow`` relation, or schema 13
when a running ``Bound`` uses finite profile contact, and need the
matching viewer |viewer_version|, API |viewer_api|,
reading document versions |document_versions|. Check the installed viewer's
report with ``machinome viewer`` rather than inferring capability from a
package name. See :doc:`changelog` and :doc:`upgrading`.

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
validated. Production profiles record what a maker states; they do not
certify a process, a material or a part.

Direction
---------

The node types, the two engines and the OpenSCAD family are laid out as
the packages they are meant to become, but the split has not started: every
one ships inside the ``machinome`` distribution, and nothing is published
as a separate package. Further work follows findings from real machines:
performance on larger assemblies, inspection, and mechanical contracts.
These are directions, not promised release features.
