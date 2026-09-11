.. _status-and-roadmap:

Project status and direction
=============================

Solid Node is a working framework for modelling and simulating mechanical
assemblies. The latest published release is 0.6.0; this manual describes
the upcoming 0.7 release.

0.7's declarative and motion APIs have been shaped by a broader range of
mechanical projects: clocks, printers, robot arms and hands, walking
mechanisms, actuators and laboratory equipment. The tutorial teaches the
underlying ideas
with a small framework-owned demonstration. The V8 engine, Metamaquina 2
and Clock 01 are three external examples for exploring complete machines.

What it does today
------------------

It combines CAD and imported parts into named assemblies, describes
prescribed motion and interactive inputs, builds incrementally, exports
operable browser models, and tests geometric and kinematic contracts.
See :doc:`why-solid-node` and :doc:`changelog`.

Limits to keep in mind
----------------------

* Linux is the validated development platform. Cross-platform packaging
  and the experimental studio harness are not a portability promise.
* This is not a general dynamics solver. Prescribed motion does not prove
  that forces, friction, material strength or tolerances will make a
  physical mechanism work.
* Tests prove the contracts and sampled states you write, not every
  possible state or manufacturing outcome.
* The project is pre-1.0. Read migration notes before upgrading; examples
  and experimental interfaces can change.
* The separate viewer's 0.1.0 is founded but not yet published. Preview
  users need matching source installations.

Direction
---------

Future work includes richer manufacturing information, better inspection
tools, and further mechanical contracts driven by real projects.
These are directions, not release commitments. Declarative models and
flexible parts are already implemented and are no longer roadmap items.
