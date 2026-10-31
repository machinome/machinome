Machinome 0.9: one repository, one release
==========================================

Released on 31 October 2026.

Machinome 0.9 changes where the packages come from rather than what a
machine can say. The framework and every package that grew beside it, the
mechanics helpers, the browser viewer, the skills for assistants, the films
and the studio, are developed in one repository, released together under
one version and one licence, and documented in this one manual. The machine
you describe, the documents you publish and the verdicts your tests reach
are what they were in 0.8.

One repository
--------------

Each package is a directory of the repository, named as the distribution it
builds, and each installs as an extra of the framework: the node types and
the two engines as in 0.8, and ``machinome[mechanics]``,
``machinome[viewer]``, ``machinome[viewer-openscad]``,
``machinome[skills]``, ``machinome[movie]`` and ``machinome[studio]``. Each
is imported from its address under ``machinome``: ``machinome.mechanics``,
``machinome.viewer.web``, ``machinome.movie``, ``machinome.studio``. A bare
``pip install machinome`` is still the core alone, and now carries no node
type at all: a project of STL or JSCAD parts names its extra, as every other
node type's project does.

One version and one licence
---------------------------

Every package is numbered 0.9.0, and an extra installs the package of the
framework's own release, so ``pip install --upgrade "machinome[...]"`` moves
the set together. Every package is licensed |framework_licence|, at the
recipient's choice.

One command
-----------

``machinome`` learns its commands from the packages installed beside it.
``machinome viewer`` describes, serves and photographs through the browser
viewer; ``machinome movie`` makes a narrated film of a machine; ``machinome
skills`` installs the machinome skills where your assistants read them; and
``machinome studio`` opens the studio's project hub. ``machinome -h`` lists
every command an installed package adds, after the framework's own.

Viewers chosen by name
----------------------

A still, a development session and an export each use the viewer you name:
``--viewer web`` for the browser viewer, ``--viewer openscad`` for OpenSCAD,
or ``viewer = "web"`` under ``[tool.machinome]`` for the whole project. The
browser viewer serves and captures inside the command's own process, so a
rebuild reaches the open page without a reconnect.

Fewer rebuilds
--------------

A node is rebuilt only for edits to what it names in its sources: editing a
definition no node names restamps the parts instead of rebuilding them, so a
tuning edit to one part of a large machine no longer re-derives the rest.

One manual
----------

The pages of the browser viewer, the mechanics helpers, the films, the
skills and the studio are part of this manual, and every page says at its
top which extras it needs.

Upgrading
---------

0.9 moves and renames without aliases. :doc:`/project/upgrading` lists every
move a 0.8 project makes and what to change for each: the node types' extras,
the helpers' and the viewer's addresses, the viewer flag and the commands.
Exports keep document versions 1 to 13, read by the matching viewer 0.9.0
with API 29, so a 0.8 viewer reads a 0.9 export.

See :doc:`/project/changelog` for the complete list of what 0.9 brings.
