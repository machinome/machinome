============
Command line
============

The studio has two entry points, run from the environment ``scripts/setup``
created. Both take the same options.

.. code-block:: console

   $ python -m floor.orchestrator --projects-dir PATH [--port PORT]
   $ python -m floor --projects-dir PATH [--port PORT]

``python -m floor.orchestrator``
    The studio. Serves the project hub and, for each project opened from
    it, its session: the profile's agents, the model build and watch, the
    browser viewer and the conversation. Prints
    ``shop-floor open at http://127.0.0.1:PORT`` once the hub is available
    and runs until interrupted; Ctrl-C ends every open session.

``python -m floor``
    The same hub and workspace without agents: projects open, build and
    show their model, and the conversation has nobody to answer it. Useful
    for inspecting a project or a build without a backend.

Options
=======

``--projects-dir PATH``
    Required. The folder whose entries the hub lists, used exactly as
    given: the studio does not append a directory name, derive one from the
    working directory, or look at Git metadata to find it. It may be
    anywhere, need not be near the studio, and may be empty.

``--port PORT``
    The local port to serve on. Defaults to ``FLOOR_PORT`` when that
    environment variable is set, and to ``9000`` otherwise.

Both entry points listen on ``127.0.0.1`` only. The exit status is ``2``
for an unknown option and ``1`` for a failed prerequisite, with the reason
on standard error prefixed ``error:``.

There is no option to choose a project, a profile, a backend or a model:
the project is chosen in the browser, and the rest is the project's own
configuration, :doc:`project-configuration`.
