2. An input moves a body
========================

A part on its own is a shape. A machine starts when an input moves a
body. This chapter adds the crank and the one line that connects a
person's hand to it.

The crank
---------

Create ``counter/crank.py``. The crank is one printed piece: an arbor that
runs in the base's bore, an arm at the top, and a knob at the end of the
arm.

.. literalinclude:: counter/c02_input.py
   :language: python
   :pyobject: Crank

One line is new: ``turn = Revolute(axis=(0, 0, 1), unit='deg')``. A
**joint** says where a body may move, next to the body, once. A
``Revolute`` turns the body about a line; ``axis`` is that line's
direction and, by default, it passes through the body's own origin. The
crank's arbor is on its own ``z`` axis, so nothing more is needed. The
joint creates no hole and changes no geometry. It names a **coordinate**,
``turn``, in degrees.

The assembly
------------

Now the machine. Replace ``counter/counter.py``:

.. literalinclude:: counter/c02_input.py
   :language: python
   :pyobject: Counter

.. code-block:: toml

    [tool.machinome]
    model = "counter.counter:Counter"

Three declarations and one statement:

``crank = Driver(default=0.0, range=(0.0, 3600.0), unit='deg')``
    A **driver** is a named input of the machine: a handle a person or a
    program moves. Its ``default`` is where it starts, its ``range`` is
    what a slider travels over, and its ``unit`` is what the readout
    shows. The range is presentation, not a limit: nothing clamps to it.

``base = Base()`` and ``handle = Crank()``
    **Child declarations.** A node constructed in a class body is not one
    shared object; each ``Counter`` realizes its own base and its own
    crank when it is constructed, named after the attributes that hold
    them. The bore is at the base's origin and the arbor is on the
    crank's, so neither needs placing.

``crank.drives(handle.turn)``
    A **relation**: the crank driver's value is the crank's ``turn``
    coordinate. Written in the class body, over the declarations, with no
    import. Binding a joint's coordinate moves the body: the framework
    applies the rotation the joint describes, about the joint's own line.

Save, and the viewer grows a ``crank`` slider:

.. machinome:: /_exports/counter-02
   :height: 400px

Drag it. The crank turns about its arbor. The slider covers ten turns.

What just travelled
-------------------

Nothing here runs in the browser as Python. The build published the crank
with its rotation as an expression over the name ``crank``, and the viewer
evaluates that expression when the slider moves. That is also why the
driver is read in ``simulate()`` in :doc:`/start/first-machine` and
never in ``render()``: ``render()`` builds the machine at rest, once;
``simulate()`` runs on every instant, with the inputs bound. A relation
written in the class body is solved for you at the end of that phase,
which is why this chapter's ``Counter`` has no ``simulate()`` at all.

One more thing the framework did: it refused nothing here, but it would
have. A driver's value belongs to the instant; assigning to one
(``self.crank = 12``) raises and names ``set_state``, the one way to bind
a value from Python. Reading a driver no instant has bound raises and
names it. And a coordinate two things bind at once, say this relation
and an assignment ``self.handle.turn = 90`` in ``simulate()``, is refused
by name rather than silently overwritten.

Next: :doc:`03-dimensions`.
