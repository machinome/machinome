================
Machinome Studio
================

**Say what the machine should do. Watch a team build it.**

Machinome Studio is a local harness in which a maker builds a mechanical
CAD project with the `Machinome framework <https://machinome.readthedocs.io/>`_
by talking to agents in the browser. It opens a project hub over a folder
of projects. Opening a project starts a session of its own: the agents the
project's profile declares, a conversation with the one agent who speaks
for the team, a live view of the model that follows every change to its
source, the project's files, each agent's work as it happens, and the
printable pieces of the last complete build.

The maker describes the machine in ordinary words. The agents design it,
write it in the framework's declarative source, test it, inspect it and
commit it, inside that project's own Git repository and nowhere else. The
maker remains the authority for the decisions that matter, and the project
holds the record of every one that was made.

.. note::

   This manual describes Machinome Studio |release|. The studio runs
   against Machinome |machinome-version| installed with its ``viewer``
   extra, and opens a project only with a browser viewer declaring API
   |required-viewer-api| or later. :doc:`project/status` says where the
   studio stands and what it needs.

Start here
==========

* **Setting up?** :doc:`Install the studio <installation>`, then start the
  hub.
* **Starting a project?** :doc:`Open or create one from the hub
  <opening-a-project>`.
* **Working on one?** :doc:`The project workspace <the-floor>`: the
  conversation, the model, the source, the agents and the build.
* **Choosing a team?** :doc:`The profiles and their agents
  <working-with-agents>`, and :doc:`what a project may configure
  <reference/project-configuration>`.
* **Something will not open?** :doc:`troubleshooting`.
* **Modelling the mechanics yourself?** That is the `framework manual
  <https://machinome.readthedocs.io/>`_. The studio runs the framework and
  shows its viewer; it restates neither.

.. toctree::
   :maxdepth: 1
   :caption: User guide

   installation
   opening-a-project
   the-floor
   working-with-agents
   troubleshooting

.. toctree::
   :maxdepth: 1
   :caption: Reference

   reference/cli
   reference/project-configuration
   reference/profiles

.. toctree::
   :maxdepth: 1
   :caption: Project

   project/status

.. toctree::
   :caption: Machinome ecosystem

   Framework manual <https://machinome.readthedocs.io/>
   Viewer manual <https://machinome-viewer.readthedocs.io/>
   Source code <https://github.com/machinome/machinome-studio>
