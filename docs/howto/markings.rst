.. _markings:

Put digits and labels on a part
===============================

A calculator's answer is the angular position of a printed number roll.
Model the roll without its digits and the register is computed perfectly
and unreadable. The same gap eats every dial face, index mark, scale,
warning label and part number in a catalogue of machines. A **marking**
is how a part says what it carries on its surface.

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

Three things, in that order: the **artwork**, the **placement** and the
**colour**. The part is unchanged, same solid, same bytes, same piece,
and it now carries its digits wherever its assembly puts it. The
tutorial's counter drums wear ten digits this way.

What a marking is not
---------------------

A marking is **not a solid**: it has no volume and no bounds, and the
part's STL, exact geometry, piece id, interference and connectivity
contracts give exactly the answers they give without it. It is **not a
child**: the tree, the part count and the pieces inventory are unchanged.
It is **not a printed piece**: a decal is a surface you paint, apply or
co-print, and reporting it as a piece would put a part in the bill of
materials that no maker handles. And it is **not part of the part's build
identity**: adding one to a built part rebuilds no solid.

That is why this exists rather than modelling each glyph as its own leaf.
Glyphs modelled as leaves are parts no maker handles, with volume, and
they stand in front of every interference test the machine has.

Where a marking may be declared
-------------------------------

On a rigid node: a leaf adapter or a fusion. An assembly has no artifact
to carry a decal and a flexible part's surface moves; both are refused
when the class is created. A marking is an ordinary class attribute, so
it is inherited, a subclass drops one by assigning ``None``, and it may be
written in a plain mixin that is not a node, in which case the artwork
path resolves against the mixin's module. Its name must be free on the
node: not a parameter, child, port or joint, and not ``color``.

The artwork
-----------

``Svg(path, scale=None)``. The path is relative to the module that
declared the marking, and a path that is not there is refused at the
declaration. The drawing is reduced to its **closed regions**, each one
face carrying its enclosed regions as holes, so a digit's counter is a
hole with no rule of your own. The file's origin is kept and its Y axis
is flipped into model orientation, so a drawing authored in a drawing
program reads the right way up.

Open paths are ignored and counted, in one INFO line per build naming the
file: a sheet border is a registration mark, not part of the drawing. A
drawing with no closed region at all is refused. Coordinates are read as
millimetres; ``scale`` multiplies them and must be positive, because a
negative scale mirrors every glyph. Only SVG artwork is supported: no DXF,
no text from a font, no projection onto an arbitrary surface.

Placement
---------

Both placements work in the part's own frame, the frame its artifact is
written in, and both land the artwork point ``origin`` (default
``(0, 0)``) on the placement's origin. Vectors need not be unit length.

``Flat(at, normal, x_axis, origin=(0, 0))``
    puts the artwork on the plane through ``at``: artwork X along
    ``x_axis`` orthogonalized against ``normal``, artwork Y along
    ``normal × x_axis``. An ``x_axis`` parallel to ``normal`` is refused.

``Wrapped(axis, radius, at, start=0, origin=(0, 0), pitch=None, zero=None)``
    wraps it onto a cylinder. **Artwork X is arc length**, so a point at
    artwork x sits at the angle ``start + degrees(x / radius)``,
    right-handed about ``axis``, and **artwork Y is height** along the
    axis from ``at``. The angular zero is ``zero=`` projected across the
    axis when given; otherwise the next principal axis in right-hand
    order (``+Z`` wraps from ``+X``, ``+X`` from ``+Y``, ``+Y`` from
    ``+Z``). ``pitch``, in degrees, stamps the whole artwork every
    ``pitch`` degrees and must divide 360 exactly; a drawing that already
    carries all ten digits round one circumference needs none.

Reading direction: seen from outside the cylinder, increasing angle runs
to the viewer's right, so a drawing with its X to the right reads
unmirrored. The counter's drums lay their digits in decreasing order so
that turning forward brings the next digit to the post.

What the build writes and what a viewer sees
--------------------------------------------

One artifact per marking, beside the part's STL and under the same
basename with the attribute name in it. It holds the artwork's surface as
an open sheet of triangles on the nominal cylinder or plane with no
offset (any separation a renderer needs to avoid z-fighting is the
renderer's constant), wound to face away from the part, subdivided to the
part's tessellation precision. It is deliberately not watertight: a
surface, not a solid.

Editing the artwork rebuilds only the decal, never the solid; editing the
declaration rebuilds the part like any edit to its module. The published
document gives the part an additive ``markings`` list, one entry per
marking with its name, model, colour and its own change time, and no
placement, because the artifact is already in the part's frame.
``machinome export`` copies each under ``models/``.

The browser viewer draws markings from API 14 onward, so the counter's
digits appear in every export on these pages. The OpenSCAD path, the
default ``machinome snapshot`` renderer included, does not draw them; use
``--renderer web`` for a photograph with digits.

Manufacturing process, painted, vinyl or co-printed, and the outputs it
implies are not modelled. A marking says what a part carries and where,
not how it gets there.
