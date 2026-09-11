Why Solid Node
==================

Design the relationships
----------------------------

A machine is more than a collection of correct parts. A shaft has to fit
its bearings. Two gears have to agree on both ratio and tooth placement.
A linkage has to reach its working positions without crossing the frame.
Solid Node lets you describe these relationships in the same Python
project that describes the geometry.

The assembly is a tree of named parts and mechanisms. Parameters define
what gets built. Joints describe how a body may move. Relations describe
what drives what. Drivers and a time base supply the inputs. You can
inspect the resulting machine in a browser and ask mechanical questions
of it in tests.

In :doc:`Clock 01 <example-clock-01>`, the hands follow the actual gear
train. They do not follow a second, ideal-clock animation that could hide
a wrong ratio. One description connects the parts you see to the motion you test.

Keep the CAD work you already have
--------------------------------------

Use the modelling tools that suit the parts. CadQuery and build123d
produce exact OCCT solids. SolidPython and OpenSCAD give access to their
modelling language and libraries; JSCAD brings JavaScript models into the
assembly. STEP and STL adapters wrap existing files. Sheet parts keep a
cut profile and its thickness together. Flexible parts use
`molejo <https://molejo.readthedocs.io>`_ to describe a shape that changes
with the machine.

You can wrap an existing design incrementally. Clock 01 uses Luke
Wallin's 3DPrintedClocks geometry; its Solid Node layer supplies the
assembly, motion, controls and tests. The same approach applies to
downloaded hardware, printer designs and robot assemblies.

Make changes you can check
------------------------------

Change a declared parameter and the value flows to the children that
receive it. The build reuses current part geometry and rebuilds affected
artifacts. Moving a rigid part changes its placement without creating a
new solid for every frame.

Tests can ask whether a printed piece is connected, whether separate
parts interfere, or whether a fit permits a small motion and blocks a
larger one. A test can sample a pendulum swing or a full gear cycle.
Scenarios can adjust an input, run an instruction, and check the state
at an exact simulation tick.

These are specific geometric and kinematic checks. They do not replace
material testing, tolerance analysis, or a physical prototype. Motion
laws prescribe positions; Solid Node does not infer forces, friction,
wear or a mechanism's dynamics from its geometry.

Share an operable design
----------------------------

An export contains the assembly, meshes, motion expressions and controls.
Readers can inspect and operate it in a browser without installing the
Python CAD stack. The same viewer can be embedded in a project website
or documentation.

The framework is Apache-2.0. The optional browser viewer is the separate
AGPL-3.0-only `solid-node-viewer
<https://github.com/LibreSolid/solid-node-viewer>`_ package. Example
designs retain their own licences; Clock 01 is CERN-OHL-S-2.0.

Next, :doc:`open the clock <quickstart>`.
