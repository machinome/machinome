============
Command line
============

.. code-block:: console

   $ machinome-studio [--projects-dir PATH] [--port PORT]

``machinome-studio``
    The studio, on ``PATH`` wherever it is installed. Serves the project hub
    and, for each project opened from it, its session: the profile's agents,
    the model build and watch, the browser viewer and the conversation.
    Prints ``shop-floor open at http://127.0.0.1:PORT`` once the hub is
    available and runs until interrupted; Ctrl-C ends every open session.

Two module entry points, run from the environment ``scripts/setup``
created, start the same way and take the same options:

.. code-block:: console

   $ python -m floor.orchestrator [--projects-dir PATH] [--port PORT]
   $ python -m floor [--projects-dir PATH] [--port PORT]

``python -m floor.orchestrator``
    The same studio ``machinome-studio`` starts.

``python -m floor``
    The same hub and workspace without agents: projects open, build and
    show their model, and the conversation has nobody to answer it. Useful
    for inspecting a project or a build without a backend.

Options
=======

``--projects-dir PATH``
    The folder whose entries the hub lists, used exactly as given: the
    studio does not append a directory name, derive one from the working
    directory, or look at Git metadata to find it. It may be anywhere, need
    not be near the studio, and may be empty. When it is not given, the
    :ref:`configuration file <configuration-file>`'s ``projects`` key is
    used; when neither supplies it, the studio refuses to start.

``--port PORT``
    The local port to serve on. When it is not given, ``FLOOR_PORT`` is
    used when set, then the configuration file's ``port`` key, then
    ``9000``.

All three ways of starting the hub listen on ``127.0.0.1`` only. The exit status is ``2``
for an unknown option and ``1`` for a failed prerequisite, including a
project folder that neither an option nor the configuration file supplies,
with the reason on standard error prefixed ``error:``.

There is no option to choose a project, a profile, a backend or a model:
the project is chosen in the browser, and the rest is the project's own
configuration, :doc:`project-configuration`.

.. _configuration-file:

Configuration file
===================

All three ways of starting the hub read one studio configuration file, a
TOML file with the project folder and the port, so a maker who starts the
hub often can write both once.

**Location.** ``MACHINOME_STUDIO_CONFIG``, when set, names the file
directly; it must exist. Otherwise the file is looked for at
``$XDG_CONFIG_HOME/machinome-studio/config.toml`` when ``XDG_CONFIG_HOME``
is an absolute path, or at ``$HOME/.config/machinome-studio/config.toml``
when ``HOME`` is an absolute path. When neither variable is an absolute
path there is no default file, which is not itself an error: a missing
file at either location simply means every setting comes from an option,
the environment, or the built-in default.

**Keys.** One table, ``[studio]``, with two keys:

.. code-block:: toml

   [studio]
   projects = "~/machines"
   port = 9000

``studio.projects``
    The project folder, as an absolute path, or ``~`` or a path starting
    with ``~/``, which is expanded against ``HOME``. No other ``~`` form is
    expanded. A relative path is refused.

``studio.port``
    The local port, an integer from 1 to 65535.

Nothing else is accepted: an unknown table, an unknown key, or a value of
the wrong type or range refuses startup naming the file and the key, even
when an option or the environment would have supplied every setting
anyway.

**Precedence.** Each setting is resolved once, the first source that
supplies it winning:

.. list-table::
   :header-rows: 1

   * - Setting
     - Option
     - Environment
     - File
     - Default
   * - project folder
     - ``--projects-dir``
     - —
     - ``studio.projects``
     - none: refuse
   * - port
     - ``--port``
     - ``FLOOR_PORT``
     - ``studio.port``
     - ``9000``

**Refusals.** Every case below prints ``error: <reason>`` on standard
error and exits ``1``, before the ``openspec`` check, the registry or the
listener:

* No project folder, and a default file location exists: names that file.
* No project folder, and no default file location exists (neither
  ``XDG_CONFIG_HOME`` nor ``HOME`` is an absolute path): says so.
* A file named by ``MACHINOME_STUDIO_CONFIG`` that does not exist, or
  cannot be read.
* A file that is not valid TOML, has a table or key other than
  ``[studio]``, ``projects`` and ``port``, or gives either key a value of
  the wrong type or range.
* ``studio.projects`` starting with ``~`` when ``HOME`` is not an absolute
  path.
* ``FLOOR_PORT`` or ``--port`` outside 1–65535.

Codex login
===========

.. code-block:: console

   $ python -m floor.codex_auth login

Provision or renew Studio's separate Codex login with the hub stopped.
The command checks the supported runtime, acquires exclusive ownership of
the Studio credential store and starts native device authorization. It
does not read or copy an ordinary Codex login. See :doc:`../installation`
for the supported installation and storage location.
