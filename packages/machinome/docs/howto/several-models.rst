Keep several machines in one project
====================================

A project that holds a family of machines, one repository, one shared
library, one model per machine, declares them by name:

.. code-block:: toml

    [tool.machinome]
    model = "wall_clock_01"

    [tool.machinome.models]
    wall_clock_01 = "design.wall_clock_01.clock:WallClock01"
    wall_clock_02 = "design.wall_clock_02.clock:WallClock02"

Beside the table, ``model`` names the default by its key; leave it out
and a command given no reference lists the names instead of guessing. A
name is one word of letters, digits, underscores and hyphens, and may not
be the name of a directory at the project root.

Each declared model is a reference of its own, ``machinome build
wall_clock_02``, ``machinome develop wall_clock_01``, and owns its own
build directory, ``_build/<name>/``, with its own document, error record
and build lock, so building one never touches another. A reference that
is not a declared name, a sub-assembly by qualifier or path, builds in
``_build/`` itself.

.. code-block:: bash

    $ machinome models
    $ machinome build --all
    $ machinome test --all

``machinome models`` lists every model with its state, ``unbuilt``,
``published`` or ``failed``, read from the build directories without
importing project code. ``build --all`` builds every model in declaration
order into its own directory, reporting each outcome and exiting nonzero
when any failed. ``test --all`` runs every model's tests as one run.

The tutorial is itself such a project: one model per chapter, and the
framework's suite runs ``build --all`` and ``test --all`` over it.
