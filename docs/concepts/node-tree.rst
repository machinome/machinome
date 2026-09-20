The node tree
=============

A project is a tree of nodes. Leaves make one part each; internal nodes
combine their children. An assembly's children are separate parts that
move relative to each other; a fusion's children are fused into one rigid
piece. Every node has a **name**, which addresses it in the viewer tree,
in tests and in driver ids, and a **build identity**, which decides which
cached artifact backs it. The two are independent.

Names
-----

A node's name defaults to its class name. When a node is a child of
another, the name is the attribute the parent holds it under:

.. code-block:: python

    class Counter(AssemblyNode):
        base = Base()
        handle = Crank()

The children appear as ``base`` and ``handle``, not ``Base`` and
``Crank``. Children held in a list get indexed names, ``planets-0``,
``planets-1``. An explicit ``name=`` always wins over the derived name,
and attributes starting with an underscore are ignored by the derivation.

The same attribute path qualifies a **driver id**. Two instances of one
axis class held as ``x_axis`` and ``y_axis`` publish their same-named
driver as ``x_axis.position`` and ``y_axis.position``, one string each,
identical in the exported document's driver table, in ``set_state``, in
instruction targets and in a simulation's state. The id must be a legal
expression identifier, which an indexed list name is not (``planets-0``
would parse as a subtraction): a driver-declaring node held in a list
makes the tree unqualifiable and fails loudly, rather than letting two
siblings share one value.

References
----------

A node is named by **reference**: a model name the project declares, a
qualifier (``package.module:Class``), a file path, or a file path plus
class (``path/to/file.py:Class``). With no reference, a command operates
on the project's default model, declared in ``[tool.machinome]`` in the
nearest ancestor ``pyproject.toml``, which is also how the project root
is found, so every command behaves the same from any directory.

A bare path resolves to the single node class defined in that file. When
a file defines several, the path is ambiguous and fails naming the
candidates; name the class you mean. ``machinome test`` on such a path runs
the node classes its companion tests declare with ``node = TheClass``.

Build identity and caching
--------------------------

Every generated artifact lives in the build directory (``_build`` by
default; ``SOLID_BUILD_DIR`` moves it): the STL of every rigid part, a
``.brep`` beside it for an exact part, a ``.dxf`` beside a sheet part, a
marking artifact per declared marking, and the ``viewer.json`` document
that publishes the whole. Artifacts mirror the project's package layout.

A declarative node's identity is its class plus the resolved value of
every declared parameter, derived by the framework, so no keyword can be
forgotten. A node built as ``Gear(teeth=20)`` and one built as
``Gear(teeth=21)`` are two artifacts; two ``Gear(teeth=20)`` instances,
and every copy of a ``repeat()``, share one, however many times the part
appears and under whatever names. A constructor-form node is keyed over
the arguments that reach ``super().__init__()``, so a value kept on
``self`` but not forwarded silently shares a stale artifact between
variants; that is the bookkeeping declarations remove.

Consequences:

* Renaming a node never invalidates its cache: names address the tree
  and are not part of the identity.
* Any parameter change produces a new artifact, however deeply buried in
  a long value; the key embeds a bounded readable prefix plus a hash.
* Driver, port and joint values are deliberately **not** part of the
  identity. A part's placement and a flexible part's pose change with
  every instant; keying artifacts on them would mint a new part per
  frame. Identity stays structural, and state stays in the instant.
* A joint's arguments, a marking and a site-declared joint never enter
  the identity either.

Freshness
---------

An artifact rebuilds when its stamp no longer equals the node's source
time, compared as exact nanoseconds. The **source set** is the node's own
file plus the transitive closure of project-local modules it imports,
resolved statically; internal nodes union their children's sets, so a
leaf's edit invalidates the assemblies above it and nothing sideways.
When stamps disagree but a digest of the tracked sources matches what
produced the artifact (a clone, a branch switch), the artifact is
restamped rather than rebuilt.

What that means in practice:

* Editing a module that defines no node correctly invalidates exactly the
  nodes that import it.
* The walk never follows a package's ``__init__.py``. A value reached
  through the package rather than the module that defines it is not
  tracked, and its edit serves a stale model.
* A current leaf is not rendered at all. Nothing may depend on a render
  side effect, and geometry that depends on something the import walk
  cannot see (a data file read at runtime, an environment variable) can
  look current when it is not. ``StlNode``, ``StepNode`` and markings
  track their own files.
* The digest is scoped to the node. Two node classes in one file share
  one stamp, but each node's digest covers the file minus the other
  classes' bodies, so editing one class rebuilds that node and the
  fusions above it and only restamps the other.

Printed solids
--------------

A **topmost rigid node** is one printed solid: a rigid node whose parent
is not rigid, or a rigid root. Whole-model assertions work in that unit
and do not descend into it: leaves inside a fusion are ingredients of one
solid, never compared against each other and not individually required
to be connected. A flexible leaf is never a printed solid.

Published documents carry a ``pieces`` inventory, one entry per distinct
built artifact with its size, volume, watertightness and count. Identity
there is content-derived, so a repeated part is one piece with a count
and handed variants are two.
