=====================
Project configuration
=====================

A project's ``pyproject.toml`` may carry one table for the studio,
``[tool.machinome-studio]``. It is the only place a project selects its
profile and its agents' runtimes; there is no launcher option and no
environment variable for either. The framework's own ``[tool.machinome]``
table is neither read nor written by the studio.

.. code-block:: toml

   [tool.machinome-studio]
   profile = "fordesmac"

   [tool.machinome-studio.agents]
   foreman = "claude:opus"
   designer = "opencode:anthropic:claude-sonnet-4-5:high"
   machinist = "claude:sonnet:medium"

``profile``
    The profile every session of the project opens with, as the lowercase
    kebab-case name of a profile the studio ships: ``builder`` or
    ``fordesmac`` (:doc:`profiles`). Absent, the project opens under
    ``fordesmac``. A value that is not such a name makes the project
    unreadable; a name the studio does not ship makes it unopenable, and
    the studio does not substitute the default. Creating a project from
    the hub writes this key.

``agents.<agent>``
    One value per agent, keyed by the agent's identifier in the profile.
    The value names the backend, the provider where the backend has more
    than one, the model, and optionally a reasoning level, in that order,
    joined by ``:``.

    * ``claude:<model>`` or ``claude:<model>:<reasoning>``, where the model
      is one of |claude-models| and the reasoning level one of
      |claude-efforts|;
    * ``opencode:<provider>:<model>`` or
      ``opencode:<provider>:<model>:<reasoning>``, where the provider and
      model are identifiers from the OpenCode installation's connected
      catalogue and the reasoning level is one of that model's variants.

    An agent the table does not name opens on Claude with the model and
    effort its profile declares. A value that omits the reasoning level
    keeps the profile's effort. The parts cannot be declared separately.

What is rejected, and what is ignored
=====================================

The studio refuses to open a project, naming the file and the value, when
a runtime value names an unknown or retired backend, has more or fewer
parts than its backend admits, leaves a part empty, names a Claude model or
reasoning level outside the sets above, or names a reasoning level for a
backend that cannot enforce one; when an agent key is not a lowercase
kebab-case identifier; or when the table carries a key it does not define.
In particular there is no ``effort``, ``tools`` or ``permission`` key: a
reasoning level is only ever the last part of an agent's value, and tools
and permissions are the profile's alone.

A value keyed to an agent the project's profile does not declare is
ignored, and the studio reports the keys it ignored, so a project that
changed profile keeps working and a misspelt identifier is visible.

The former ``[tool.libresolid-studio]`` table is an error naming the
rename; the studio never reads it silently.

What the studio writes
======================

Creating a project writes ``profile``. Applying a runtime change in the
Agents area with persistence ticked writes that one agent's value,
preserving everything else in the file, comments included, and only if the
file is unchanged since the controls were loaded; otherwise the change is
refused and nothing is written. Nothing else in the project's
configuration is ever touched.
