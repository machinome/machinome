.. _markings:

Markings
========

A calculator's answer is the angular position of a printed number roll.
Model one without the digits and the register is computed perfectly and
is **unreadable** — which, for a calculator, is the one thing it is for.
The same gap eats every dial face, index mark, scale, warning label and
part number in a catalogue of machines.

A **marking** is how a part says what it carries on its surface:

.. code-block:: python

    from machinome.node import CadQueryNode
    from machinome.node.markings import Marking, Svg, Wrapped

    class ResultsDial(CadQueryNode):

        digits = Marking(
            Svg('results_dial.svg'),
            Wrapped(axis=(0, 0, 1), radius=9.45, at=(0, 0, 18.45)),
            color='#FFFFFF',
        )

        def render(self):
            ...

Three things, in that order: the **artwork** (a drawing file), the
**placement** (where on the part it sits) and its **colour**. The part
is unchanged — same solid, same bytes, same piece — and it now carries
its digits wherever its assembly puts it.

What a marking is not
---------------------

The interesting half of the definition. A marking is **not a solid**. It
has no volume and no bounds; a part's STL, its exact geometry, its piece
id, ``assertNoSolidInterference``, ``assertNoDisconnectedSolids`` and
every clearance contract give exactly the answers they give without it,
faceted and exact alike.

It is **not a child**. ``children`` is unchanged, the tree is unchanged,
an assembly's part count is unchanged, and no marking is addressable as
a part. It is **not a printed piece**: a piece is one thing to print,
and a decal is a surface you paint, apply or co-print — reporting it as
a piece would put a part in the bill of materials that no maker handles.

And it is **not the part's artifact identity**. A marking is not a
parameter, so it never reaches ``uniq_id``: adding one to a part that is
already built changes no artifact key, and the STL on disk is still the
STL that part's sources produce.

That is the whole reason this exists rather than "just model each glyph
as its own leaf". Glyphs modelled as leaves are parts no maker handles,
with volume, and they stand in front of every interference test the
machine has.

Where a marking may be declared
-------------------------------

On a **rigid** node — a leaf adapter or a :ref:`fusion <fusion>`. An
assembly has no artifact to carry a decal and no frame of its own to
place it in, and a flexible part's surface is a function of machine
state; both are refused when the class is created, naming the class and
the attribute.

A marking is an ordinary class attribute, so it is inherited, and a
subclass drops one by assigning ``None`` — a variant part that is the
same solid without its label:

.. code-block:: python

    class UnlabelledDial(ResultsDial):

        digits = None

It may also be written in a **plain mixin** that is not a node at all,
which is how a project usually spells a family of fitted parts:

.. code-block:: python

    # decals.py
    class ResultsFace:

        digits = Marking(Svg('results_dial.svg'), Wrapped(...),
                         color='#FFFFFF')

    # dials.py
    class FittedDial(ResultsFace, ResultsDialType1):
        ...

The artwork path then resolves against **the mixin's** module, where the
drawing lives, and the marking is refused on the node that wears it if
that node is not rigid — the mixin itself says nothing about rigidity.

A marking's name has to be free on its node, exactly as a parameter's
does: it may not take the name of a parameter, a child, a port or a
joint coordinate, and it may not shadow an attribute every node carries
(``color`` first among them — ``color = Marking(...)`` would make
``self.color`` a marking and break colorization).

The artwork
-----------

``Svg(path, scale=None)``. ``path`` is relative to the directory of the
module that **declared** the marking, and a path that is not there is
refused at the declaration, in the same family as a missing
:ref:`STL source <missing-source-file>`.

The drawing is reduced to its **closed regions**. The file's own origin
is kept, its Y axis is flipped into model orientation, and each closed
region becomes one face carrying its enclosed regions as **holes** — so
a digit's counter is a hole in the decal with no rule of your own.

**Open paths are ignored, and counted.** A drawing's sheet border is an
open path, and it is usually a registration mark rather than part of the
drawing. The Curta's own ``results_dial.svg`` is the case worth knowing:
its border measures 59.376 mm wide, and the roll it belongs to has a
radius of 9.45 mm — whose circumference is 2π × 9.45 = 59.376 mm. The
border *is* the unwrapped circumference. Dropping it silently would
leave you wondering why the digits do not sit where the drawing says, so
each build logs one line at INFO naming the file and how many open paths
it ignored. A drawing with no closed region at all is refused.

Artwork coordinates are read as millimetres. ``scale`` multiplies every
one of them, for a file authored in something else; it is a property of
the file, which is why it is here and not on a placement. ``scale`` is
**positive**: a negative value mirrors the drawing, which reverses the
decal's winding and renders every glyph backwards, and a non-positive
``scale`` is refused naming the value.

Placement
---------

Both placements work in the part's **own adjusted frame** — the frame
its artifact is written in — and both land the artwork point ``origin``
(by default ``(0, 0)``) on the placement's origin. Vectors need not be
unit length. Nothing about an assembly, a joint or an instant enters:
that is what makes the decal ride the part's placement for free.

``Flat(at, normal, x_axis, origin=(0, 0))`` puts the artwork on the
plane through ``at``: artwork X runs along ``x_axis`` orthogonalized
against ``normal``, artwork Y along ``normal × x_axis``. An ``x_axis``
parallel to ``normal`` leaves nothing to orthogonalize and is refused.

``Wrapped(axis, radius, at, start=0, origin=(0, 0), pitch=None,
zero=None)`` wraps it onto a cylinder. **Artwork X is arc length**, so a
point at artwork x sits at the angle ``start + degrees(x / radius)``,
and **artwork Y is height along the axis** from ``at``. A positive angle
turns right-handed about ``axis``.

The angular zero is stated, never left for a reader to infer from
geometry. Give ``zero=`` and that direction is it, projected
perpendicular to the axis. Omit it and the zero is **the next principal
axis in right-hand order**: ``+Z`` wraps from ``+X``, ``+X`` from
``+Y``, ``+Y`` from ``+Z``, and ``-Z`` from ``-X``. There is exactly one
axis direction for which the derivation is undefined — the one parallel
to (1, 1, 1) — and it is refused naming ``zero`` as the remedy rather
than silently choosing.

``pitch``, in degrees, stamps the whole artwork every ``pitch`` degrees
around the circle, for an artwork that is one repeated unit. It must
divide 360 a whole number of times; anything else leaves the last copy
overlapping the first, and is refused naming the nearest whole count.
A drawing that already carries all ten digits across one circumference
— the Curta's does — needs no pitch at all.

What the build writes
---------------------

One artifact per marking, beside the part's own ``.stl`` and under the
same basename, with the attribute name in the path
(``…-<uniq_id>.marking-digits.stl``), so two markings on one part never
collide and the file says which declaration wrote it.

It holds the artwork's surface in the part's adjusted frame, as an open
sheet of triangles on the **nominal** cylinder or plane, with **no
offset**: any separation a renderer needs to avoid z-fighting is that
renderer's constant, not a claim about where the part's surface is. A
wrapped decal is subdivided so it follows its cylinder to within the
part's own tessellation precision — its declared ``linear_deflection``
where it declares one, and the framework's 0.1 mm where it does not —
because two vertices of a flat triangle wrapped by their coordinates
alone describe a chord, not an arc.

The sheet's triangles wind so their normal points **away from the
part** — radially outward from the wrap axis for a wrapped marking,
along the declared normal for a flat one — whatever orientation the
drawing tool gave the artwork's regions, so a renderer may offset,
lift or light a decal along its own normals without asking the part
which side it is on. The offset above is the sheet's **magnitude**;
this is its **direction** — the two describe where the surface sits
and which way it faces, not one claim twice.

The mesh is deliberately not watertight. It is a surface, not a solid:
nothing imports it as a part, fuses it, or measures its volume.

Currency: what rebuilds what
----------------------------

A marking has a currency of its own, and the direction that matters is
this one:

* **Edit the artwork** and only the decal is rebuilt. The part's STL and
  its exact geometry stay current and are not rewritten, because the
  artwork is tracked by the marking and is deliberately **not** in the
  part's own source set.
* **A lost or stale decal** always comes back on the next build, and it
  costs no render: the part's solid is never re-derived on a decal's
  account.
* **Edit the declaration** — the placement numbers, the colour, the
  artwork path — and the part rebuilds, as it does for any edit to the
  module that declares it. The class body is in the node's scoped source
  digest, which is scoped per class and not per statement. One part, one
  rebuild; the alternative is a cache clever enough to be wrong.

What a consumer sees
--------------------

A rigid node's published entry gains an optional ``markings`` list, one
entry per declared marking in declaration order, each carrying ``name``,
a ``model`` reference to its artifact, its ``color`` and its own
``mtime`` — the marking's, so a consumer that reloads on change sees a
redrawn decal without the part appearing to change. The key is absent
on a part that declares none.

The growth is **additive** and moves no document version: a marking adds
no solid, enters no operation, no binding and no program, so a consumer
that ignores the key draws exactly the picture it draws today, and a
document whose tree declares no marking is byte-identical to the one
published before markings existed. A marking entry carries **no
placement** — the artifact is already in the part's frame, so a consumer
applies the part's own operations to it — and **no piece**.

``machinome export`` copies each named marking under ``models/`` beside the
meshes, under the same portability rules, so an export stays
self-contained.

Not yet, and on purpose
-----------------------

* **The browser viewer does not draw markings yet.** It is a separate
  package with its own release; a model that declares a marking
  publishes it and, for now, looks exactly as it does today. The
  OpenSCAD path — ``machinome develop`` without the viewer extra, and
  ``machinome snapshot --renderer openscad`` — does not draw them at all.
* **DXF artwork**, **text from a font** and **projection onto an
  arbitrary surface** are not supported. Each needs a rule of its own,
  and every marking in a real catalogue already exists as a drawing
  file.
* **Manufacturing process** — painted, vinyl, co-printed — and the
  outputs it implies are a later cycle, arriving with process and
  material. A marking today says what a part carries and where, not how
  it gets there.
