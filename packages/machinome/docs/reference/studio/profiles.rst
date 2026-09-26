================
Shipped profiles
================

A profile declares its standing agents, which one speaks with the maker,
its work mode, and for each agent the prompt it follows, the skills it may
load, the agents it may assign, the agent it reports to, and its Claude
defaults: the model and effort it opens with when the project selects
nothing (:doc:`project-configuration`), and its capabilities. Profiles are
the studio's; a project chooses one and cannot alter it.

Capabilities
============

An agent's capabilities name groups of the studio's bounded operations,
every one rooted at the active project:

``Read``
    Read a file; inspect a path.
``Glob``
    List a directory; find files by pattern.
``Grep``
    Search file contents.
``Write``
    Write, delete or move a file; make a directory.
``Edit``
    Edit a file in place; apply a patch.
``Bash``
    Git status, diff, log, show, head, add and commit; the framework's
    build, test and snapshot; the messages of the team: assignment,
    direction, acknowledgement, report and completion. There is no shell.
``OpenSpec``
    The project's OpenSpec record: set it up, and run the OpenSpec command
    inside the project.
``WebSearch``, ``WebFetch``
    Declared for the librarian; they resolve to nothing today, which is why
    it is out of service.

Loading a skill follows the agent's declared skills, not its capabilities.

``builder``
===========

Work mode: direct. One agent, speaking with the maker.

.. list-table::
   :header-rows: 1
   :widths: 12 12 30 14 32

   * - Agent
     - Label
     - Role
     - Claude default
     - Capabilities and skills
   * - ``builder``
     - Builder
     - Speaks with the maker; designs, builds, tests and commits; keeps
       the project's OpenSpec record.
     - ``sonnet``, medium
     - ``Bash``, ``Read``, ``Write``, ``Edit``, ``Glob``, ``Grep``,
       ``OpenSpec``; skills ``machinome-api``, ``machinome``.

``fordesmac``
=============

Work mode: delegated. Foreman speaks with the maker and alone assigns the
three specialists, who report only to Foreman.

.. list-table::
   :header-rows: 1
   :widths: 12 12 30 14 32

   * - Agent
     - Label
     - Role
     - Claude default
     - Capabilities and skills
   * - ``foreman``
     - Foreman
     - Speaks with the maker; assigns and directs the specialists; keeps
       design one increment ahead of machining.
     - ``sonnet``, medium
     - ``Bash``, ``Read``, ``Write``, ``Edit``, ``Glob``, ``Grep``; no
       skills.
   * - ``designer``
     - Designer
     - Owns the design record and releases increment drawings.
     - ``opus``, medium
     - ``Bash``, ``Read``, ``Write``, ``Edit``, ``Glob``, ``Grep``; skill
       ``machinome-api``.
   * - ``machinist``
     - Machinist
     - Builds the released slice test first; owns code and tests.
     - ``sonnet``, medium
     - ``Bash``, ``Read``, ``Write``, ``Edit``, ``Glob``, ``Grep``; skills
       ``machinome-api``, ``machinome``.
   * - ``librarian``
     - Librarian
     - Researches external libraries into ``docs/notes/``; provisionally
       out of service.
     - ``sonnet``, medium
     - ``Bash``, ``Read``, ``Write``, ``Glob``, ``Grep``, ``WebSearch``,
       ``WebFetch``; skills ``machinome-api``, ``machinome``.

Every agent's prompt is the profile's, not the project's, and a prompt may
name only skills its profile allows.
