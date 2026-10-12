Give your assistant the machinome skills
========================================

An assistant that reads `Agent Skills <https://agentskills.io>`_ can build
and simulate machines with machinome when it has the machinome skills. There
are two:

- ``machinome`` builds and changes parts and assemblies: parametric nodes,
  placement, motion, geometry contracts and visual verification.
- ``machinome-simulate`` adds a simulation layer to an existing mechanical
  design, CAD source, STL, STEP or URDF, keeping its geometry as it is and
  recording the evidence of the reconstruction.

Install them
------------

.. code-block:: bash

    pip install "machinome[skills]"
    machinome skills install

Run the second line in the project. At a terminal it shows the tools it
knows, numbered, with the ones it found in the project marked, and Enter
installs for the marked ones; answer with numbers or ids to choose others.
Where no terminal can answer, it installs into ``.agents/skills/``, which
several assistants read. Name the tools yourself with ``--tools``:

.. code-block:: bash

    machinome skills install --tools claude,codex

``--tools all`` installs for every tool and ``--tools none`` for none. The
ids are the ones OpenSpec uses, and ``agents`` stands for
``.agents/skills/``. ``machinome skills list`` prints every tool with the
directory it reads in a project and in your home, then the copies already
installed under the project.

To have the skills in every project, install them into your home instead:

.. code-block:: bash

    machinome skills install --personal --tools claude

After upgrading the package, bring the copies up to date:

.. code-block:: bash

    machinome skills update

``update`` rewrites the copies older than the package you installed, says
which ones are current, and leaves alone a copy written by a newer package;
``--force`` rewrites every copy the command wrote. ``update`` and ``list``
take ``--personal`` too.

What the command will not do
----------------------------

Each copy is the skill's directory as the package ships it, with a marker
added to the front matter of its ``SKILL.md``:

.. parsed-literal::

    metadata:
      installed-by: machinome-skills
      version: "|release|"

That marker is how the command knows a copy is its own. It refuses to
write over a skill of the same name that carries no marker, and tells you
the line to run with ``--force`` if you mean to replace it. It never
deletes a file or a directory, and a file you add inside a copy stays
there. If you edit a copy and want to keep your edits, remove the marker:
the copy is then yours, and neither ``install`` nor ``update`` writes to it
without ``--force``.

Ask for a skill
---------------

Ask the assistant to use a skill by name, or let it choose one. For
example:

    Use machinome to add an adjustable shaft sleeve and prove its running
    clearance.

    Use machinome-simulate to assemble this printer's existing STL parts and
    expose its X, Y and Z motion. Start with the frame and X carriage.

What the assistant needs
------------------------

To build and verify a machine the assistant needs access to the project's
files, the ability to run commands and to look at images, and machinome
with the project's CAD tools installed in the project's environment. The
skills install none of them. An assistant without commands or images can
help plan the work, and the skills tell it to say which verification it
could not do.

The skills take the API from the official documentation of the version
installed in the project, not from the skills themselves; see
:doc:`/howto/simulate-existing` for the simulation layer they build.
