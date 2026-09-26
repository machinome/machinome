===============
The project hub
===============

Start the hub
=============

.. code-block:: console

   $ python -m floor.orchestrator --projects-dir ~/machines

``--projects-dir`` is required and names the folder that holds your
projects, exactly as given: the studio neither appends a directory name nor
guesses one from where it was started. The folder may be anywhere and may
be empty. The command prints the hub's address, ``http://127.0.0.1:9000``
unless ``--port`` or ``FLOOR_PORT`` says otherwise, and keeps running: it
is the service that holds every open project's agents, viewer and
conversation. Stop it with Ctrl-C when you are done; stopping ends every
open session. :doc:`reference/cli` lists the options.

Before it listens, the studio checks that the ``openspec`` command runs and
refuses to start when it does not. A project's design record is kept with
that tool, and a studio that could not keep it would lose the record
silently; there is no reduced mode.

What the hub lists
==================

The hub lists the folder you started it on, one card per entry:

* **A project** is a directory that is the root of its own Git repository.
  Its card shows the name, whether the project is open, the profile it
  opens under, its branch and last commit, and a preview of its model once
  one has been rendered.
* **A folder** is a directory that is not a repository but holds projects
  somewhere below it. Its card says how many projects it holds and previews
  up to three of them; enter it to list them. A project whose manifest
  declares several models is listed as a folder of those models, one
  openable entry per model, named as the manifest names them.
* **A directory that cannot be opened** is listed with the reason, so
  nothing you put in the folder disappears. A directory that is not a
  repository and holds no project is the usual case.

Regular files are not listed. While you are inside a folder, a trail at the
top names the working folder and each folder between; choose one to go
back up. The browser location carries the folder or project you are
looking at.

**Backends.** For Claude Code and OpenCode, the hub reports
whether it found the program on this machine and, when it did, its path,
its version and the models the shipped profiles would ask of it. This is
observation only: the hub does not install, enable or locate a backend.
Codex availability is checked separately when opening a project that
selects it or loading runtime choices in Agents; an executable-version
summary alone does not qualify it.

Create a project
================

**New project** asks for a name and a profile. The name is a directory
name: anything the filesystem accepts that no entry of the folder being
listed already uses, with no naming convention imposed. The profile is
required; :doc:`working-with-agents` describes the two the studio ships.
The studio creates the project as a direct child of the folder you are
listing, from the framework's own scaffold, records the profile in the
project's ``pyproject.toml``, makes the directory an independent Git
repository with that scaffold as its first commit, and opens it. The card
shows the project as creating until it is open. No runtime selection is
written: the agents use their profile's defaults until the project says
otherwise (:doc:`reference/project-configuration`).

Creation is not offered while the hub is listing the models of one
project.

Open a project
==============

Opening is one action from the card. Before anything starts, the studio
reads the project's ``pyproject.toml`` without changing it, resolves the
profile it declares (``fordesmac`` when it declares none), validates the
profile and every runtime selection, and verifies that the directory is
its own repository. It then asks the framework where the entry's model
publishes, builds that model with ``machinome build``, starts the
profile's agents in that repository, and begins watching the project's
source.

When the project already holds a complete published model, the session
opens on it at once and the build runs behind it: the card and the
workspace say the model is being brought up to date until the build
settles. A project that has never been built waits for its first build,
because there is nothing to show yet. A model whose build fails still
opens, with the Model area saying why, so the conversation and the source
remain usable and the failure can be repaired.

The card shows the project as opening, then as open or as failed with the
reason. A profile that does not resolve, a malformed runtime selection, a
missing or too-old browser viewer, or an agent that would not start leaves
no partial session behind, and the hub and every other project remain
available. :doc:`troubleshooting` lists the reasons and their remedies.

Several projects may be open at once, each with its own agents,
conversation, model and build; two models of one repository are two
sessions over one checkout. A second browser opening an open project joins
its session. The open project's address shows its workspace, which
:doc:`the-floor` describes.

Previews
========

The preview on a card is a fixed-size picture of the entry's own model,
rendered through the framework's snapshot command with the browser
renderer. It is refreshed after a build that changed what the model
publishes and before a commit made through the studio's Git tools, and is
kept in the project as ``screenshot.png`` at the root, or
``screenshots/<model>.png`` for a named model of a multi-model project,
staged with such commits so the picture travels with the project. A render
that fails changes nothing: the build stands, the commit goes through, and
the previous picture, if any, remains. A card without a picture shows a
placeholder.

Close a project
===============

Close a project from its workspace. Closing ends the session's agents,
stops watching the project, and returns you to the folder that lists it. A
session keeps nothing: its conversation and the agents' state end with it,
and reopening the project starts afresh. The project's repository holds
everything that was committed. If an agent is in the middle of work, the
studio warns before discarding it.
