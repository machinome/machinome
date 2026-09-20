# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The common versioned node-tree document serializer.

Export and published build snapshots have one observable node schema while
their rigid-model paths remain producer-owned: export maps models into a
portable copied ``models/`` tree, whereas a build maps them relative to its
published root.  Keeping that difference in a supplied mapper makes the tree
walk itself one source of truth without making builds portable by accident.

Version 2 adds named drivers.  An operation records whatever value
``render()`` computed, so a document serialized from a numerically stepped
node would publish the constants of one instant -- exactly the defect ``$t``
already had, and which export already answers by returning the node to
symbolic animation time before serializing.  ``symbolic_drivers`` extends
that same producer obligation to drivers: bind every declared driver of the
tree to its qualified token, serialize, restore.  It is a distinct internal
path and never ``set_state``, whose numbers-only contract is what keeps a
bound pose a pure function of numbers.

The accompanying ``drivers`` table publishes each qualified id's declared
metadata, so a consumer can present the inputs an expression names.  It is
presentation metadata: ``range`` in particular is never a clamp.  A tree
declaring no drivers serializes an empty table and is byte-for-byte the
document version 1 published, which is what lets a consumer that cannot yet
evaluate driver expressions keep rendering every document that has none --
and fail loudly on one that has them, rather than render a wrong pose.

Beside it, the ``instructions`` table says what the machine can be TOLD to
do: each declared instruction's qualified name, its design-unit targets
keyed by qualified driver id, and its duration.  It is additive within
version 2 (ADR-056 stage 3b): an instruction targets a driver, so a
document carrying instructions necessarily carries a non-empty ``drivers``
table, which a consumer without driver evaluation already refuses loudly --
no consumer can misread the added key.  Both tables come from ONE walk:
``drive_tree`` visits every assembly after binding its drivers, so the
instruction declarations are collected in the same descent that builds the
symbolic expressions.

Version 3 adds the ``flexible`` node shape: a part whose GEOMETRY follows
the machine travels as its shape spec plus one expression per parameter,
never as a mesh, so the consumer evaluates shape the way it already
evaluates pose.  The version is a property of the CONTENT, not of the
producer -- ``document_version`` reads it off the finished tree -- because
a document holding no flexible node is byte-identical to the version 2 it
has always been, and claiming otherwise would make an old consumer refuse
documents it renders perfectly.

Version 4 adds the ``bindings`` table (ADR-080). Native motion values now
retain graphs during construction, so reuse never expands their ancestry.
``bind_document`` (below) compiles the native roots and legacy expression
strings that ``operations`` and flexible ``params`` carry across the document
(``machinome.core.expressions``), and rewrites every occurrence of a
subexpression that repeats -- except a bare number or a bare driver id,
shorter written out than referenced -- into a reference to a named entry
in an ordered ``bindings`` table, so a consumer resolves it in one forward
pass before any operation or ``params`` expression.  Detected at
serialization, without first flattening the native graphs: nothing about
how a project writes kinematics or the viewer's scalar grammar changes.
The version is a property of the CONTENT once more: a document with
nothing to share carries no ``bindings`` key and is byte-identical to what
this module has always published, while a non-empty table is the one
version bump in this ladder that is NOT additive -- a consumer ignoring
``bindings`` would resolve a reference to nothing and render a wrong pose,
so a consumer that cannot read version 4 must refuse it rather than render
it.
"""

from contextlib import contextmanager

from machinome.core.expressions import bind_expressions
from machinome.node.qualified import (
    DriverToken, declared_drivers_of, driver_id, drive_tree,
)
from machinome.motion.ports import CLOCK_NAME, declared_time
from machinome.scad_expression import symbol
from machinome.simulation.enumeration import tree_declares_drivers


DOCUMENT_FORMAT = 'machinome-export'

#: The version a document without flexible content declares -- which is
#: every document the producer emitted before flexible parts existed, and
#: byte-for-byte the same one.
DOCUMENT_VERSION = 2

#: The version a document carrying at least one flexible node declares.
#: A new tree shape is a breaking change (ADR-034), so it needs a bump;
#: emitting it only where the content needs it is the drivers-table
#: precedent, and it is what keeps an old consumer refusing exactly the
#: documents it genuinely cannot render.
FLEXIBLE_DOCUMENT_VERSION = 3

#: The version a document carrying a non-empty `bindings` table declares
#: (ADR-080). A consumer ignoring `bindings` would resolve a binding name
#: to nothing and render a wrong pose, so this bump is not additive: a
#: document with nothing shared omits the key and keeps declaring
#: `DOCUMENT_VERSION` or `FLEXIBLE_DOCUMENT_VERSION`, byte-identical to
#: what the framework published before bindings existed.
BINDINGS_DOCUMENT_VERSION = 4

#: The version a RUNNING root's document declares (OpenSpec change
#: `publish-the-mechanical-program`). Unlike the ladder below it, this
#: one is a property of the ROOT'S DECLARATION rather than of the tree's
#: content: flexible leaves and shared subexpressions are properties of
#: the tree, while a compiled program is a property of what the root
#: declares, and a running root with a trivial program is still a machine
#: a version 4 consumer would animate wrongly. The bump is not additive:
#: a consumer ignoring `program` would read a document whose joint
#: placements are bare coordinate names it can bind nothing to, so a
#: consumer that cannot read version 5 must refuse it by name.
RUNNING_DOCUMENT_VERSION = 5

#: The version a running root's document declares when its compiled
#: program carries at least one LAW edge naming one of its own ``gives``
#: among its ``needs`` -- a law that READS the coordinate it drives
#: (OpenSpec change ``read-the-driven-coordinate``). A property of the
#: CONTENT again: a program with no such edge publishes byte-identically
#: at 5. The bump is not additive and it is not cosmetic -- a version 5
#: consumer evaluates a law edge as the difference of its two endpoint
#: evaluations, which with the read at BOTH ends freezes the branch it
#: selects and moves the part by a different mechanism without saying so.
SELF_READ_DOCUMENT_VERSION = 6

#: The version a running root's document declares when its compiled
#: program carries a BLOCK -- a set of two or more edges whose
#: dependencies are cyclic, ordered once per PIECE of a tick rather than
#: once per program (OpenSpec change ``select-the-source``). A property
#: of the CONTENT like the one below it: a program with no block
#: publishes byte-identically at 6 or 5. The bump is not additive and it
#: is not cosmetic -- the published ORDER of a block's members is a
#: LISTING, not an execution order, so a version 6 consumer that
#: Kahn-orders the published edges either refuses the program by name or
#: executes that listing and moves the machine by whatever it happens to
#: give, silently, and by a different amount for each order it might have
#: chosen.
BLOCK_DOCUMENT_VERSION = 7

#: The version a CLOCKED root's document declares -- one in whose tree
#: anything declares a `State` (OpenSpec change
#: ``publish-the-clocked-machine``). A property of the ROOT'S
#: DECLARATION, exactly as version 5 is: a clocked root with one state,
#: no flexible leaf and nothing shared is still a machine a lower
#: consumer would animate wrongly. It DOMINATES every other rung, a
#: clocked document being a clocked document whatever else it holds.
#: The bump is not additive -- a clocked tree's pose expressions read
#: its declared states as FREE NAMES, which a lower consumer can bind
#: to nothing -- so a consumer that cannot read version 8 refuses it by
#: name rather than rendering a wrong pose. Publishing a clocked model
#: at a lower version with its states rendered as their initial values
#: was rejected outright: the geometry would be right only at the
#: initial state and would then silently stop following the machine.
CLOCKED_DOCUMENT_VERSION = 8

#: A running document carrying an explicit backlash/clearance edge.
PLAY_DOCUMENT_VERSION = 9

#: Explicit time-drive admissions require independent stop identities.
TIME_DRIVE_DOCUMENT_VERSION = 10


_MISSING = object()


def running_root(node):
    """Whether `node` declares `time = Time.running()`."""
    base = declared_time(type(node))
    return base is not None and base.mode == 'running'


@contextmanager
def symbolic_drivers(node):
    """Serialize ``node`` in symbolic driver mode, then restore it.

    Yields ``{qualified_id: declaration}`` for every driver in the tree.
    The instruction half of the same walk is available through
    ``symbolic_document``; this name stays for a caller that only wants
    the drivers.
    """
    with symbolic_document(node) as (declarations, _):
        yield declarations


@contextmanager
def symbolic_document(node):
    """Serialize ``node`` in symbolic driver mode, then restore it.

    Yields ``(declarations, instructions)``: ``{qualified_id:
    declaration}`` for every driver in the tree, with each one bound to a
    token whose string is its own id, with ordinary arithmetic preserving
    graph references until publication; and
    ``{qualified_name: (path, instruction)}`` for every instruction the
    same descent found.  The mode binds ALL the drivers -- never a subset,
    so no render can find a hole -- and afterwards restores exactly the
    snapshot each node held and re-renders under it, so a caller that had a
    numeric pose still has one.

    A tree that declares no drivers is not walked at all: it has nothing to
    bind, and a walk would render it for no reason.  Its document is the
    version 1 document with two empty tables added -- including the
    instruction one, because an instruction moves a driver and a tree with
    no drivers has nothing for one to move.

    Under a RUNNING root the same walk does two more things, because
    under that base a COMMITTED BANK is what poses the geometry (OpenSpec
    change ``publish-the-mechanical-program``, design section 3).  Every
    JOINT COORDINATE of the linked tree is bound to a symbolic token of
    its own qualified id, beside every driver's, so a joint's placement
    publishes as that coordinate's id and every plain port, derived
    coordinate and flexible ``params`` expression publishes as an
    expression over the bank; and ``time`` is bound to its own name, so a
    version 5 document carries the free name the program publishes as its
    clock rather than the 0..1 animation variable.

    The coordinate binding goes where the driver binding goes -- inside
    the walk's own ``visit``, after that node's drivers are bound and
    before anything renders -- through ``CoordinateDelivery``, the path a
    run's own ``set_state`` takes, with a ``RunBinder`` installed as the
    root's ``_run_binder`` for the duration.  That is what makes the
    relations record as SOLVED rather than refuse as doubly bound, and
    what lets publication run over a tree a live run owns: the binder is
    admitted over a run-owned slot, and every slot's value, binder and
    freshness marks are put back afterwards with its joint re-placed, so
    the run goes on as if nothing had happened.

    The ENUMERATION's own record travels back with them: each assembly's
    note of what its previous phase bound, which its next phase clears.
    This walk's phases overwrite that note and, under a running root, put
    nothing in it -- they bind no joint coordinate, because the delivery
    bound them all outside the enumeration -- so a tree an enumeration
    POSED would otherwise be left holding that pose's values with nothing
    left that knows to clear them, and the next pass would read one
    relation's two ends asymmetrically. The untimed path needs none of
    this: with no delivery its own phases bind the same coordinates
    through the relations, so the note it writes is the one the re-render
    wants (OpenSpec change `a-read-is-not-a-binding`).
    """
    running = running_root(node)
    if not running and not tree_declares_drivers(node):
        yield {}, {}
        return

    previous = {}
    instructions = {}
    # The CLOCKED root that declares the ELAPSED base: its document
    # carries the free name `time` wherever the model reads the clock,
    # never the animation variable, because a version 8 consumer poses
    # the machine at its BANKED instant and `$t` is a 0..1 animation
    # timeline (OpenSpec change ``publish-the-clocked-machine``, design
    # section 10). The base is asked FIRST, so a tree that declares no
    # elapsed base pays for no walk: a stateless untimed root reaches
    # this line and stops at the `and`.
    base = declared_time(type(node))
    elapsed = (not running and base is not None and base.mode == 'elapsed'
               and _tree_declares_states(node))
    delivery = _coordinate_publication(node) if running else None
    held = (node.__dict__.get('_run_binder', _MISSING) if running
            else _MISSING)
    if delivery is not None:
        node.__dict__['_run_binder'] = delivery.binder

    def remember(target):
        if id(target) not in previous:
            previous[id(target)] = (target, dict(target._states),
                                    target.__dict__.get('_solver_bound',
                                                        _MISSING))

    def symbolic(target, path, name, declaration):
        remember(target)
        return DriverToken(driver_id(path, name))

    def collect(target, path, children):
        for name, instruction in getattr(target, 'instructions', {}).items():
            instructions['.'.join(path + (name,))] = (path, instruction)
        if delivery is None:
            # Not a running root. A control issues a movement request
            # and only a running simulation takes one, so a tree that
            # declares one and is published untimed is refused by name.
            # `_declares_controls` is the class's OWN table, set by
            # `NodeMeta`, so this walk recognizes a control without
            # importing the simulation layer -- and a subclass that
            # empties the table reads False.
            if getattr(type(target), '_declares_controls', False):
                _refuse_control_without_a_run(node, target)
            if elapsed:
                # The ONE line the clocked branch adds, and the line the
                # running branch already has: `time` is global by
                # contract and propagates flat, so every node holding a
                # snapshot gets it. No coordinate delivery and no run
                # binder -- a clocked bank holds no joint coordinate, so
                # a joint's placement publishes as the expression over
                # drivers and states the untimed enumeration produces.
                remember(target)
                target._states[CLOCK_NAME] = symbol(CLOCK_NAME)
            return
        remember(target)
        # `time` is global by contract and propagates flat, so every node
        # holding a snapshot gets it -- exactly as `set_state` delivers it.
        target._states[CLOCK_NAME] = symbol(CLOCK_NAME)
        _publish_coordinates(delivery, target, path)
        for child in children:
            if getattr(child, '_states', None) is None:
                # A LEAF holds no snapshot, so the walk never visits it on
                # its own -- and a joint may be declared on one.
                _publish_coordinates(delivery, child, path + (child.name,))

    declarations = drive_tree(node, symbolic, collect)
    try:
        yield declarations, instructions
    finally:
        for target, states, _bound in previous.values():
            target._states.clear()
            target._states.update(states)
        if delivery is not None:
            delivery.restore()
            # And the ENUMERATION's own record, beside the coordinates it
            # belongs to: each assembly's `_solver_bound` is what its next
            # phase clears, and this walk's own phases overwrote it. Under
            # a running root they had nothing to put in it -- the delivery
            # bound every joint coordinate OUTSIDE the enumeration, so
            # every relation into one records as solved by the run and
            # binds nothing -- so without this the re-render below would
            # inherit the restored pose's values with nothing left that
            # knows to clear them, and read one relation's two ends
            # asymmetrically (OpenSpec change `a-read-is-not-a-binding`).
            # Absence is restored as absence: `clear_solved` POPS the
            # record, so a node that held none must hold none again.
            for target, _states, bound_slots in previous.values():
                if bound_slots is _MISSING:
                    target.__dict__.pop('_solver_bound', None)
                else:
                    target.__dict__['_solver_bound'] = bound_slots
            if held is _MISSING:
                node.__dict__.pop('_run_binder', None)
            else:
                node.__dict__['_run_binder'] = held
        # Re-render under the restored snapshot: an operation holds the
        # value its render computed, so nothing else would drop the tokens.
        # Unless the prior binding had holes -- a tree nobody bound could
        # not be rendered before this either, and inventing a value to
        # re-render it with is exactly what the unbound contract forbids.
        # Its stale operations are swept by whatever renders it next.
        if all(name in states
               for target, states, _bound in previous.values()
               for name in declared_drivers_of(type(target))):
            drive_tree(node, lambda target, path, name, declaration:
                       target._states[name])


def _tree_declares_states(node):
    from machinome.simulation.enumeration import tree_declares_states

    return tree_declares_states(node)


def _refuse_control_without_a_run(root, target):
    """The publication half of the refusal ``Sim.__init__`` makes.

    Both are passed through by every real project: a simulation is
    constructed before any run, and a document is published by every
    build and every export.
    """
    name = sorted(getattr(target, 'controls', {}))[0]
    raise TypeError(
        f"{type(target).__name__} declares the control '{name}', and "
        f"{type(root).__name__} declares no running time base. A control "
        f"is how a person issues a movement request, and only a running "
        f"simulation takes one: declare time = Time.running() on the root, "
        f"or drop the control.")


def _coordinate_publication(node):
    """The delivery this publication binds its coordinates through.

    `CoordinateDelivery` is what `set_state` already uses to bind a joint
    coordinate under a running root: it saves each slot's value, binder
    and freshness marks, binds through `set_coordinate` so the joint's own
    placement applies, and restores them in reverse with the joint
    re-placed from what its coordinates then hold. A publication needs
    exactly that, and a second implementation of it would be a second
    thing to keep in step.
    """
    from machinome.motion.ports import RunBinder
    from machinome.node.assembly import CoordinateDelivery

    return CoordinateDelivery(RunBinder())


def _publish_coordinates(delivery, target, path):
    from machinome.node.assembly import CoordinateDelivery

    names = CoordinateDelivery.names(type(target))
    if not names:
        return
    delivery.deliver(target, {name: symbol(driver_id(path, name))
                              for name in names}, path, {})


def drivers_table(declarations):
    """The document's ``drivers`` table: each qualified id's declaration.

    ``dtype`` is published by name because a document is JSON and a Python
    type is not; everything else travels verbatim.  A declaration's
    ``range`` is carried for presentation only -- nothing in the framework
    or the viewer clamps to it -- and is carried in the DESIGN units it
    was declared in, beside a ``default`` that is native.  The producer
    deliberately does not convert it: a client that received one reading
    of a scaled driver's bounds could not tell which one it was, while a
    client holding both the range and the ``scale`` converts once, exactly
    as ``Driver.native`` converts an instruction target.
    """
    return {
        identifier: {
            'default': declaration.default,
            'range': (list(declaration.range)
                      if declaration.range is not None else None),
            'unit': declaration.unit,
            'dtype': (declaration.dtype.__name__
                      if declaration.dtype is not None else None),
            'scale': declaration.scale,
        }
        for identifier, declaration in sorted(declarations.items())
    }


def states_table(states):
    """The document's ``states`` table: each declared state's qualified
    id and its declaration, under exactly ``drivers_table``'s rules.

    A ``State`` takes exactly ``Driver``'s five fields with exactly
    their meanings, so the two tables follow ONE rule and this delegates
    rather than restating it: ``default`` NATIVE, ``range`` in DESIGN
    units and never a clamp, ``dtype`` by name because a document is
    JSON, ``unit`` and ``scale`` verbatim, keys sorted.

    They are TWO tables and not one, and the SPLIT is the handle rule:
    every key of ``drivers`` is an input a person may move, and no key
    of ``states`` ever is -- a state is written by the machine at an
    event, ``move`` naming one is refused by name, and one table with a
    ``kind`` field would put that mistake one field-read away (OpenSpec
    change ``publish-the-clocked-machine``, design section 3).
    """
    return drivers_table(states)


def instructions_table(instructions, version_five_or_above=False):
    """The document's ``instructions`` table: what the machine can be told.

    ``instructions`` is what ``symbolic_document`` collected --
    ``{qualified_name: (declaring path, instruction)}``.  A declaration
    names its targets class-locally (``{'motor': 0.0}``), so the declaring
    node's path is what turns them into targets on ``x_axis.motor``: the
    same qualification, through the same ``driver_id``, that keyed the
    driver table, so a client resolves a target against a declared driver
    by string equality rather than by two schemes agreeing.

    Targets stay in DESIGN units, verbatim, and the duration in seconds.
    The conversion to native state belongs to the driver declaration --
    the one place that knows what a native unit is worth -- and happens
    once, in the client, exactly as ``Driver.native`` performs it.

    A RELATIVE instruction -- one stating ``by=`` rather than ``targets=``
    -- is OMITTED below version 5: the shipped viewer reads ``targets``
    off every entry of this table and would fail on one without them, so
    a root whose instructions are all relative publishes an empty table
    and the rest of its document is unchanged (OpenSpec change
    ``run-owns-the-coordinates``).  ``version_five_or_above`` says the
    document is one of those a NEW consumer reads -- version 5 for a
    running root, version 8 for a clocked one -- where EVERY declared
    instruction travels and each entry carries exactly one of ``targets``
    (where the drivers land) and ``by`` (how far they travel from where
    they stand), both keyed by qualified driver id and both in design
    units.  The flag never meant "running": it means the version is
    high enough that omitting a relative instruction would be a producer
    discarding a declaration for a reason that does not apply to this
    consumer (OpenSpec change ``publish-the-clocked-machine``, design
    section 14).
    """
    table = {}
    for name, (path, instruction) in sorted(instructions.items()):
        if instruction.targets is not None:
            stated = {'targets': {driver_id(path, target): value
                                  for target, value
                                  in instruction.targets.items()}}
        elif version_five_or_above:
            stated = {'by': {driver_id(path, target): value
                             for target, value in instruction.by.items()}}
        else:
            continue
        table[name] = dict(stated, duration=instruction.duration)
    return table


def animation_block(root, fps=30, frames=360):
    """The document's ``animation`` object: ``fps`` and ``frames`` as the
    producer chose them, plus ``loop`` when the root declares a time
    base.

    ``loop`` is the seconds of machine time one turn of ``$t`` covers,
    read off the root's class exactly as the driver table is read off
    declarations.  It is additive within the current schema version: the
    tree shape and the operation serialization -- the two things the
    version guards -- do not change, the published expressions already
    carry ``$t * loop``, and a consumer that does not read the key plays
    ``frames / fps`` exactly as before.  An undeclared root publishes the
    object it always did, byte for byte.
    """
    block = {'fps': fps, 'frames': frames}
    base = declared_time(type(root))
    if base is not None and base.loop is not None:
        # A `loop` of None is the RUNNING base, which has no loop: its
        # document is byte-identical to an undeclared root's, so the key
        # is absent rather than null.
        block['loop'] = base.loop
    return block


def document_version(root, bindings=(), program=None, clocked=None):
    """The LOWEST schema version the serialized tree ``root`` needs.

    Read off the document rather than tracked while building it, so the
    producers that share this walk cannot disagree about what they just
    emitted.  A tree carrying a flexible node carries a shape no version 2
    consumer knows and says so; a tree carrying none is unchanged in every
    byte and claims nothing new, which is what lets a consumer that cannot
    render flexible parts keep rendering every document that has none --
    and refuse loudly only on one that has them, rather than render
    nothing where a spring belongs.

    ``bindings``, when non-empty, always wins (ADR-080): a consumer
    ignoring the table would resolve a binding name to nothing and render
    a wrong pose, so the bump is not additive the way ``loop`` and
    ``instructions`` were.  With nothing bound this answers exactly what it
    always has, so a document with nothing to share stays byte-identical
    to the one published before bindings existed.

    ``program``, when given, always wins, and is the one step of the
    ladder that is NOT read off the content: a compiled program is a
    property of the ROOT'S DECLARATION, and a running root with nothing
    shared and no flexible leaf is still a machine a version 4 consumer
    would animate wrongly. Within it the CONTENT decides once more:
    explicit time-drive admissions select version 10, Play selects 9,
    and otherwise a program carrying a BLOCK is a version 7 document, one carrying none
    but a law edge that reads the coordinate it drives is a version 6
    document, and one with neither is the byte-identical version 5 it
    always was. Seven dominates six, because a block says nothing about
    self-reads and a self-read says nothing about blocks.

    ``clocked``, when given, always wins and is the other step read off
    the ROOT'S DECLARATION rather than the content: a clocked document
    is a clocked document whatever else it holds, so a clocked tree
    carrying a flexible leaf and a non-empty ``bindings`` table still
    declares 8. ``clocked`` and ``program`` can never both be given: a
    ``State`` under a root declaring ``Time.running()`` is refused where
    declared defaults are bound, so the two ladders never meet.
    """
    if clocked is not None:
        return CLOCKED_DOCUMENT_VERSION
    if program is not None:
        if program.get('time_drives'):
            return TIME_DRIVE_DOCUMENT_VERSION
        if any(edge.get('kind') == 'play'
               for edge in program.get('edges', ())):
            return PLAY_DOCUMENT_VERSION
        if _carries_a_block(program):
            return BLOCK_DOCUMENT_VERSION
        return (SELF_READ_DOCUMENT_VERSION if _reads_its_own(program)
                else RUNNING_DOCUMENT_VERSION)
    if bindings:
        return BINDINGS_DOCUMENT_VERSION
    return _tree_version(root)


def _reads_its_own(program):
    """Whether a published program carries a LAW edge that reads the
    coordinate it drives.

    Read off the document, like every other step of the ladder: the
    self-read is ``needs`` intersected with ``gives`` and no key was
    added for it, so this is the same question a consumer asks.
    """
    for edge in program.get('edges', ()):
        if edge.get('kind') != 'law':
            continue
        if set(edge.get('needs', ())) & set(edge.get('gives', ())):
            return True
    return False


def _carries_a_block(program):
    """Whether a published program carries a BLOCK.

    Read off the document exactly as a consumer re-derives it, because no
    key is added for it: the strongly connected components of the graph
    over the edges' own ``needs`` and ``gives``, with ``needs`` met with
    ``gives`` excluded -- the same exclusion a version 6 consumer already
    makes for the self-read.
    """
    edges = [edge for edge in program.get('edges', ())
             if edge.get('kind') != 'check']
    determiner = {}
    for index, edge in enumerate(edges):
        for name in edge.get('gives', ()):
            determiner[name] = index
    after = {}
    for index, edge in enumerate(edges):
        gives = set(edge.get('gives', ()))
        after[index] = {determiner[name] for name in edge.get('needs', ())
                        if name in determiner and name not in gives}
    # Two edges on one cycle are enough: reachability from each edge back
    # to itself through at least one other.
    for start in after:
        seen, pending = set(), list(after[start])
        while pending:
            node = pending.pop()
            if node in seen:
                continue
            seen.add(node)
            pending.extend(after[node])
        if start in seen:
            return True
    return False


def _tree_version(root):
    if 'flexible' in root:
        return FLEXIBLE_DOCUMENT_VERSION
    for child in root.get('children', ()):
        if _tree_version(child) != DOCUMENT_VERSION:
            return FLEXIBLE_DOCUMENT_VERSION
    return DOCUMENT_VERSION


class _Slot:
    """One rewritable expression location inside a serialized document:
    an operation's angle or one translation component, or a flexible
    leaf's one ``params`` entry."""

    __slots__ = ('container', 'key')

    def __init__(self, container, key):
        self.container = container
        self.key = key

    def get(self):
        return self.container[self.key]

    def set(self, value):
        self.container[self.key] = value


def _collect_slots(root, slots):
    for operation in root['operations']:
        if operation[0] == 'r':
            slots.append(_Slot(operation, 1))
        else:
            translation = operation[1]
            for index in range(len(translation)):
                slots.append(_Slot(translation, index))
    if 'flexible' in root:
        params = root['flexible']['params']
        for key in params:
            slots.append(_Slot(params, key))
    for child in root.get('children', ()):
        _collect_slots(child, slots)


def _collect_program_slots(program, slots):
    """Every expression location the published program carries: a law's
    expressions, a jump plan's skeleton and each of its jumps' level
    quantities, and an expression span bound."""
    for edge in program['edges']:
        for index in range(len(edge.get('expressions', ()))):
            slots.append(_Slot(edge['expressions'], index))
        for plan in edge.get('plans', ()):
            if plan is None:
                continue
            slots.append(_Slot(plan, 'skeleton'))
            for jump in plan['jumps']:
                slots.append(_Slot(jump, 'level'))
    for span in program['spans'].values():
        for side in ('low', 'high'):
            if isinstance(span[side], dict):
                slots.append(_Slot(span[side], 'expression'))


def _collect_clocked_slots(clocked, slots):
    """Every expression location the published clocked object carries: a
    commit's event level and its laws, and a compiled constraint's
    chain, its bound, its jump plan's skeleton and each of its jumps'
    level quantities.

    A NUMERIC bound is a number and not an expression, so it is not a
    slot; the binding pass would pass it through untouched either way,
    and not collecting it says so.
    """
    for commit in clocked['commits']:
        slots.append(_Slot(commit['at'], 'level'))
        for index in range(len(commit['law'])):
            slots.append(_Slot(commit['law'], index))
    for bound in clocked['bounds']:
        slots.append(_Slot(bound, 'value'))
        if not isinstance(bound['bound'], (int, float)):
            slots.append(_Slot(bound, 'bound'))
        plan = bound['plan']
        if plan is None:
            continue
        slots.append(_Slot(plan, 'skeleton'))
        for jump in plan['jumps']:
            slots.append(_Slot(jump, 'level'))


def bind_document(root, driver_ids, program=None, clocked=None):
    """Publish each subexpression that repeats across ``root``'s operation
    and flexible ``params`` expressions once, named, and rewrite every
    occurrence to reference it in place (ADR-080).

    ``driver_ids`` is every qualified id the document's expressions may
    read -- the ``drivers`` table's keys, and under a running root the
    bank's coordinates and the program's intermediates beside them -- so a
    minted name can never collide with one (design.md D4).

    ``program``, when given, is the published program object, whose own
    expression slots are compiled in the SAME pass: the whole document
    shares one table, so a subexpression a law shares with its own jump
    plan's level quantity is published once and nothing anywhere carries
    producer-local ``let(...)`` syntax.  ``clocked`` is the same for the
    published clocked object, so a subexpression a COMMIT LAW shares
    with the pose expression that displays it is published once.

    Returns the ordered ``bindings`` list: ``[]`` when nothing in the tree
    repeats, in which case ``root`` is left untouched and the caller omits
    the ``bindings`` key entirely, publishing the byte-identical document
    it always has.
    """
    slots = []
    _collect_slots(root, slots)
    if program is not None:
        _collect_program_slots(program, slots)
    if clocked is not None:
        _collect_clocked_slots(clocked, slots)
    expressions = [slot.get() for slot in slots]
    rewritten, bindings, _warnings = bind_expressions(expressions, driver_ids)
    for slot, text in zip(slots, rewritten):
        slot.set(text)
    return bindings


def compiled_program(node):
    """``(program, rest bank)`` for a running root, ``(None, None)`` for
    every other root.

    The simulation layer's compiler is imported HERE and nowhere else in
    the producers, so a model that declares no running time pays for none
    of it (capability ``cli-startup-cost``).
    """
    if not running_root(node):
        return None, None
    from machinome.simulation.program import program_of

    return program_of(node)


def compiled_clocked(node):
    """``(clocked machine, rest bank)`` for a CLOCKED root, ``(None,
    None)`` for every other root.

    ``compiled_program``'s twin, and the ONE place in the producers that
    imports the clocked compiler: a model that declares no ``State``
    loads none of it (capability ``cli-startup-cost``).
    """
    from machinome.simulation.enumeration import tree_declares_states

    if not tree_declares_states(node):
        return None, None
    from machinome.simulation.clocked import clocked_of

    return clocked_of(node)


def clocked_block(clocked, initial):
    """The document's ``clocked`` object: what compile time decided
    about the machine, with its expression slots still native graphs for
    ``bind_document`` to compile with the tree's."""
    return clocked.published(initial)


def program_block(program, initial):
    """The document's ``program`` object: what compile time decided about
    the machine, with its expression slots still native graphs for
    ``bind_document`` to compile with the tree's."""
    return program.published(initial)


class ClockedDocumentError(ValueError):
    """A clocked tree reached a document body WITHOUT its compiled
    machine: a producer error, not a model error."""


def _refuse_an_uncompiled_clocked_model(node, clocked):
    """Refuse a CLOCKED model published without its compiled machine, by
    name.

    Placed in ``document_body`` -- the one function EVERY document
    producer passes through -- rather than in ``symbolic_document``,
    which a browser-rendered snapshot bypasses entirely: a capture bakes
    one instant and has nothing symbolic to bind, so it stages its
    document straight from here. A gate on the symbolic walk would leave
    that producer publishing a document a consumer would animate wrongly
    (OpenSpec change ``declare-the-state``, design section 10).

    The gate is not deleted; it is RE-AIMED. It asks the one structural
    question it has always asked -- does this tree declare a ``State``?
    -- and refuses when the answer is yes and no compiled machine was
    passed. That is what stops a fifth producer, added later, from
    reaching a lower-version document by a route nobody re-checked
    (OpenSpec change ``publish-the-clocked-machine``, design section 2).

    A clocked model is still never published at a lower version with its
    states rendered as their initial values: the geometry would be
    correct only at the initial state and would then silently stop
    following the machine, which is the failure the non-additive version
    rule exists to prevent.

    A tree that declares no state is answered by one structural walk that
    renders nothing, exactly as ``tree_declares_drivers`` answers its own.
    """
    if clocked is not None:
        return
    from machinome.simulation.enumeration import tree_declares_states

    if not tree_declares_states(node):
        return
    from machinome.simulation.enumeration import qualified_states

    named = ', '.join(sorted(qualified_states(node)))
    raise ClockedDocumentError(
        f'{type(node).__name__} is a CLOCKED model -- its tree declares '
        f'the state(s) {named} -- and this document body was assembled '
        f'without its compiled machine. A clocked model publishes '
        f'version {CLOCKED_DOCUMENT_VERSION}, whose `clocked` object is '
        f'what a consumer binds those states through, and a document '
        f'published without it would carry pose expressions reading '
        f'free names nothing resolves. This is a PRODUCER error: call '
        f'compiled_clocked(node) beside compiled_program(node) and pass '
        f'the machine as clocked=.')


def document_body(node, root, drivers, instructions, program=None,
                  initial=None, fps=30, frames=360, controls=None,
                  clocked=None):
    """Everything a published document carries except the two keys a
    producer owns -- the model paths it resolves in ``root``, and
    ``pieces``.

    One place, so the three producers that share this walk cannot
    disagree about what they just emitted. ``root``'s expressions are
    rewritten in place by the binding pass.

    ``clocked`` is the compiled CLOCKED machine, beside ``program``
    and mutually exclusive with it: a ``State`` under a running root is
    refused where declared defaults are bound. Given one, the body
    carries a ``states`` table beside ``drivers`` and a ``clocked``
    object beside ``program``'s position, and declares version
    ``CLOCKED_DOCUMENT_VERSION``. Given a clocked TREE and no machine,
    this refuses: see ``_refuse_an_uncompiled_clocked_model``.

    ``controls`` is the table ``Program.published_controls`` compiled,
    published beside ``instructions`` and ADDITIVELY: the key is absent
    when the table is empty, exactly as ``bindings`` is, which is what
    makes "every document that declares no control is unchanged in every
    byte" true by construction rather than by inspection. It carries no
    EXPRESSION, so it never enters ``bind_document`` and cannot change
    the ``bindings`` table, and it does not move the version -- a
    consumer that ignores it still drives the machine from the
    declarations the document already published and still renders the
    truth.
    """
    _refuse_an_uncompiled_clocked_model(node, clocked)
    block = None if program is None else program_block(program, initial)
    machine = None if clocked is None else clocked_block(clocked, initial)
    states = None if clocked is None else states_table(clocked.states)
    identifiers = set(drivers)
    if program is not None:
        identifiers |= program.published_names()
    if clocked is not None:
        identifiers |= set(states) | clocked.published_names()
    bindings = bind_document(root, sorted(identifiers), block, machine)
    body = {
        'format': DOCUMENT_FORMAT,
        'version': document_version(root, bindings, block, machine),
        'animation': animation_block(node, fps, frames),
        'drivers': drivers,
    }
    if states is not None:
        body['states'] = states
    body['instructions'] = instructions
    if controls:
        body['controls'] = controls
    if bindings:
        body['bindings'] = bindings
    if block is not None:
        body['program'] = block
    if machine is not None:
        body['clocked'] = machine
    return body


def compiled_controls(program, initial):
    """The document's ``controls`` table, or ``{}`` where there is no
    program to measure the gestures against.

    Called by the producers that publish the model's OWN declarations --
    the build's ``viewer.json`` and the export's ``manifest.json``. The
    headless browser-snapshot capture calls neither this nor
    ``instructions_table``: it BAKES one instant, its tree holds numbers
    rather than expressions, and a button naming an instruction that
    document does not list would be an inconsistent document.
    """
    if program is None:
        return {}
    return program.published_controls(initial)


def marking_entries(node, marking_path):
    """One entry per marking a rigid node declares, in declaration order.

    No placement: the artifact already holds the artwork's surface in
    the part's own frame, so a consumer applies the part's operations to
    it exactly as it applies them to the part's model, and no consumer
    reproduces the placement arithmetic. No ``piece`` either: a piece is
    one thing to print, and a decal is a surface the maker applies.

    The ``mtime`` is the MARKING's -- the maximum over its own tracked
    set, the artwork included -- so a consumer that reloads on change
    sees a redrawn decal without the part appearing to change.
    """
    # `getattr`, as the producers already ask a node whether it is
    # `exact`: a node DOUBLE -- the parity fixtures, the lifecycle
    # fakes -- is a stand-in for the two or three attributes a producer
    # reads, and a part that declares no marking publishes nothing here
    # either way.
    declared = getattr(node, 'declared_markings', None)
    if declared is None:
        return []
    entries = []
    for name, marking in declared().items():
        artifact = node.marking_file(name)
        entries.append({
            'name': name,
            'model': marking_path(node, artifact),
            'color': marking.color,
            'mtime': node.marking_mtime(marking),
        })
    return entries


def serialize_node(node, model_path, piece_id=None, *, graph_values=False,
                   marking_path=None):
    """Serialize one node using ``model_path`` for rigid artifacts.

    The established parent-linking rule must run before recursion because a
    render may create and bind a fresh child on each invocation.  A rigid node
    is a terminal model reference; a flexible leaf is a terminal ``flexible``
    object carrying the spec its geometry travels as; a non-list/tuple
    non-rigid render keeps the existing partial-node representation for
    lifecycle validation to handle.

    ``piece_id``, when supplied, is called as ``piece_id(node, model)`` for
    every rigid node -- ``model`` being the reference just resolved above --
    and its return value is published as ``piece``. It defaults to ``None``
    so every existing caller keeps its previous, piece-free document.

    ``marking_path`` is resolved the same way: called as
    ``marking_path(node, artifact)`` for each marking a rigid node
    declares, it returns the reference published as that marking's
    ``model``. The ``markings`` list is ADDITIVE and absent on a node
    that declares none, so a consumer that ignores it renders exactly
    the picture it renders today -- and a caller that resolves no
    marking publishes the document it published before markings
    existed.
    """
    data = {
        'name': node.name,
        'type': node._type,
        'color': node.color,
        'mtime': node.mtime,
        'operations': [operation._graph_serialized()
                       if graph_values and hasattr(operation, '_graph_serialized')
                       else operation.serialized for operation in node.operations],
    }
    if node.rigid:
        model = model_path(node)
        data['model'] = model
        if piece_id is not None:
            data['piece'] = piece_id(node, model)
        if marking_path is not None:
            markings = marking_entries(node, marking_path)
            if markings:
                data['markings'] = markings
        return data

    if node.flexible:
        # No model reference and no piece: its geometry is the spec, and
        # a part that deforms is no printed solid.  The recursion stops
        # here for the same reason it stops at a rigid node -- a leaf.
        data['flexible'] = node.flexible_document(graph=graph_values)
        return data

    children = node.render()
    if type(children) not in (list, tuple):
        return data

    node._link_children(children)
    data['children'] = [
        serialize_node(child, model_path, piece_id,
                       graph_values=graph_values,
                       marking_path=marking_path)
        for child in children
    ]
    return data
