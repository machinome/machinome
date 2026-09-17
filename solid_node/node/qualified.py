# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Instance-qualified driver identity: the id, the token, the walk.

A driver name is declared class-locally, so it says nothing about WHICH
instance holds it. Everything that has to address a driver from outside
the node -- the serialized document, the simulation bank, an
instruction target, `set_state` -- is a flat namespace, and two
instances of one class collide there. The cure (ADR-056 stage 3a) is an
id derived from the node's position in the tree:

    <dotted path from the addressing root>.<class-local driver name>

`x_axis.motor`. A driver declared on the root itself keeps its bare
name. The id is COMPUTED, never stored: a render rebuilds the tree
every pass, so identity has to derive from tree position, and a
registry of assigned ids would be exactly the state ADR-056's one
guardrail forbids.

The path segments are the names `_link_child` derives from the
attribute the parent holds a child under -- the same names the
serialized document already publishes for nodes -- so the id in the
document and the key in a bank are the same string by construction.
That has one hard consequence: a name exists only AFTER its parent
linked the child. A pass that has not linked cannot qualify, and
falling back to the bare local name would silently give two instances
one id, which is the defect this module exists to remove. So it
raises instead.

Two things live here rather than in the simulation layer, for one
reason: `solid_node/node/` never imports `solid_node/simulation/`.

- `DriverDeclaration` is the marker the node layer recognizes, AND the
  descriptor that hands the bound value back. The node layer has to
  know that a class attribute IS a driver declaration -- to qualify it,
  to deliver a state entry to it, to tell an ambiguous bare name from
  an unambiguous one -- and delivering the entry and handing it back
  are the same responsibility over the same `_states` dict, so the
  read lives here rather than in `simulation/driver.py`. What a driver
  MEANS (native units, dtype rounding, ramps) stays in the simulation
  layer, which owns the `Driver` that subclasses this. `Port` next
  door is the same shape for the same reason.
- `DriverToken` is the symbolic read of one driver. Its compatibility
  facade subclasses solid2's `OpenSCADConstant`, but ordinary arithmetic
  and degree math retain a native graph. Only publication produces text.
"""

import re

from solid_node.scad_expression import GraphValue
from solid_node.expression_graph import ExpressionNode

from .phase import note_read


class DriverIdError(ValueError):
    """A driver's qualified id cannot be computed, or would not be a
    legal identifier in the runtimes that evaluate it."""


class DriverDeclaration:
    """Marker base for a driver declaration, and the descriptor that
    reads one (see the module docstring).

    A driver is declared as a class attribute and read as an attribute
    of the instance -- `x = Driver(...)` is read `self.x` -- which is
    exactly how a `Port` is declared and read, and for the same
    reason: the declaration is class metadata shared by every
    instance, while the value belongs to one node's snapshot. It is
    the ONLY way to read a driver value; there is no mapping view of
    the snapshot to read it through instead.

    A DATA descriptor, deliberately. A `__get__`-only descriptor loses
    to an instance attribute of the same name, so `self.x = 5` would
    silently shadow the driver for every later read and surface as
    wrong geometry rather than as an error. Defining `__set__` makes
    the instance dict lose instead -- and keeps `_attr_name_for`,
    which derives child names by scanning a node's `__dict__`,
    seeing exactly what it saw before.
    """

    # Set by __set_name__; a default so an unbound declaration that
    # was never assigned to a class attribute still reports something.
    _name = None

    #: What this declaration is called in a message. A `State` is a
    #: driver the machine writes (OpenSpec change ``declare-the-state``),
    #: so it shares every mechanism here and differs in the noun and in
    #: who may write it.
    _kind = 'driver'

    def __set_name__(self, owner, name):
        kind = self._kind
        for klass in owner.__mro__[1:]:
            existing = vars(klass).get(name)
            if existing is None or isinstance(existing, DriverDeclaration):
                # Absent, or an inherited declaration this one
                # overrides -- base-first discovery lets a subclass
                # redeclare, and that stays legal.
                continue
            raise TypeError(
                f"{kind} '{name}' on {owner.__name__} would shadow "
                f"{klass.__name__}.{name}, which a {kind} read would then "
                f"hide for good. A {kind} is read as an attribute of its "
                f"node, so its name has to be free on that node: rename "
                f"the {kind}.")
        # object.__setattr__ because the simulation layer's Driver is a
        # frozen dataclass. A private non-field slot, not a `name`
        # field, so where a declaration is bound never enters the
        # generated __eq__/__hash__/__repr__.
        object.__setattr__(self, '_name', name)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        note_read(f'read {self._kind}', self._name)
        try:
            return instance._states[self._name]
        except (AttributeError, KeyError):
            # AttributeError: a node with no snapshot at all (a leaf).
            # KeyError: a snapshot that has no entry for this driver.
            # Both mean the same thing to the caller, and neither is a
            # value this layer may invent -- the declaration states a
            # default, and binding it is the loader's or the
            # simulation's job, never a silent fallback here.
            raise AttributeError(
                f"{self._kind} '{self._name}' of "
                f"{type(instance).__name__} is not bound; "
                f"{self._unbound_advice()}") from None

    def _unbound_advice(self):
        return f'bind it with set_state({self._name}=...)'

    def __set__(self, instance, value):
        raise AttributeError(
            f"{self._kind} '{self._name}' of {type(instance).__name__} "
            f"cannot be assigned: its value belongs to the bound snapshot. "
            f"{self._assignment_advice(value)}")

    def _assignment_advice(self, value):
        return f'Use set_state({self._name}={value!r}).'

    def drives(self, other, ratio=None, offset=None, law=None):
        """This driver drives `other`: a root driver reaches a joint at
        any depth without every class between them forwarding a port.

        A driver is a SOURCE only -- naming one as the DRIVEN end is
        refused where it is written, for the reason an assignment to one
        is refused: its value belongs to the bound snapshot.
        """
        from solid_node.motion.couplings import relate

        return relate(self, other, ratio, offset, law)

    def commits(self, targets, at=None, law=None, **rejected):
        """This driver, as the one source of a committing relation.

        The verb lives on the coupling layer exactly as `drives` does;
        this is the face a bare `Driver` declaration offers it through.
        """
        from solid_node.motion.couplings import commit

        return commit(self, targets, at=at, law=law, **rejected)

    def __and__(self, other):
        from solid_node.motion.couplings import group_with

        return group_with(self, other)


class StateDeclaration(DriverDeclaration):
    """Marker base for a STATE declaration: a driver the machine writes
    (OpenSpec change ``declare-the-state``).

    It subclasses the driver marker rather than standing beside it
    because everything the NODE LAYER does with a declaration is the
    same for both: it is class metadata, it qualifies by the dotted path
    plus the local name, it is delivered into the node's snapshot, and
    it is read as an attribute of the node that declares it. Everything
    that DIFFERS is about who writes it -- `set_state` refuses one, an
    instruction and a control cannot target one, `drives` refuses one as
    its driven end -- and every one of those refusals lives where its
    facts are, never here.

    What a state MEANS -- native units, the single rounding at a commit,
    the committing relation that writes it -- stays in the simulation
    layer's `State`, exactly as what a driver means stays in `Driver`.
    `solid_node.node` still imports nothing from `solid_node.simulation`.
    """

    _kind = 'state'

    def _unbound_advice(self):
        return ('it is bound by the enumeration that binds declared '
                'defaults, and written by its committing relation at an '
                'event')

    def _assignment_advice(self, value):
        return ('A state is written by the machine at an event, through '
                'the committing relation that names it as a target, and '
                'set as session setup with Sim(model, state={...}) or '
                'sim.restore(...).')


# A segment of a qualified id must be a name in every runtime that
# evaluates the expression it lands in -- jokenizer in the widget,
# OpenSCAD on the scad path. `_attr_name_for` derives `<attr>-<index>`
# for a list-held child, which is a perfectly good NODE name and parses
# as a subtraction here. v1 forbids it loudly; bijective sanitization is
# a recorded, compatible extension for when a project needs drivers on
# list-held children.
_LEGAL_SEGMENT = re.compile(r'[A-Za-z_][A-Za-z0-9_]*')


def driver_id(path, name):
    """The qualified id of driver `name` on a node at `path`.

    `path` is the tuple of linked child names from the addressing root
    down to the declaring node, so a root-declared driver qualifies to
    its bare name.
    """
    for segment in path:
        if not _LEGAL_SEGMENT.fullmatch(segment):
            raise DriverIdError(
                f"cannot qualify driver '{name}' through node segment "
                f"'{segment}': a qualified driver id must be a legal "
                f"identifier in the runtimes that evaluate it, and "
                f"'{segment}' is not (a list-held child is named "
                f"<attribute>-<index>). Hold the node on its own "
                f"attribute, or move the driver off it.")
    return '.'.join(path + (name,))


def instance_path(node, root):
    """`node`'s path of linked names below `root`, `()` for the root.

    Walks `_parent` upwards, which is the link `_link_child` makes. A
    node that never reached `root` that way is not linked under it, and
    its name is therefore not derived -- so there is no id to compute
    and no bare-name fallback to fall back to.
    """
    parts = []
    current = node
    while current is not root:
        parent = getattr(current, '_parent', None)
        if parent is None:
            raise DriverIdError(
                f"cannot qualify {type(node).__name__} '{node.name}': it is "
                f"not linked under {type(root).__name__} '{root.name}', so "
                f"its instance path is not computable. Qualification only "
                f"happens in a pass that links parents to children before "
                f"recursing.")
        parts.append(current.name)
        current = parent
    return tuple(reversed(parts))


class DriverToken(GraphValue):
    """A symbolic read of one driver: a constant whose string IS its
    qualified id.

    The graph facade retains SolidPython type compatibility while preserving
    operand references through arithmetic and degree math. The qualified id
    is final when the token is created; compound text is an output only.
    """

    def __init__(self, qualified_id):
        self.driver_id = qualified_id
        super().__init__(ExpressionNode('name', text=qualified_id))


# Per-class cache of the declaration scan. Class attributes do not
# change at runtime, and a stepping loop asks this question for every
# node of the tree on every tick.
_declared_cache = {}
_declared_state_cache = {}


def declared_drivers_of(node_class):
    """Every driver declared on `node_class`, by class-local name.

    Reads the class dictionaries directly, so nothing is instantiated:
    the declaration is class metadata, exactly as `declared_ports` reads
    a mechanism's connection points. Walked base-first so a subclass
    redeclaring an inherited driver wins.

    A STATE is not a driver here, whatever it subclasses: the two tables
    address two different disciplines -- a driver is what a request and
    an instruction may move, a state is what a committing relation
    writes -- and every consumer of this one (the simulation bank, the
    published driver table, an instruction target) means the first.
    `declared_states_of` is the other half.
    """
    cached = _declared_cache.get(node_class)
    if cached is None:
        found = {}
        for klass in reversed(node_class.__mro__):
            for name, value in vars(klass).items():
                if (isinstance(value, DriverDeclaration)
                        and not isinstance(value, StateDeclaration)):
                    found[name] = value
        cached = _declared_cache[node_class] = found
    return cached


def declared_states_of(node_class):
    """Every state declared on `node_class`, by class-local name.

    `declared_drivers_of`'s twin, by the same rule and the same
    base-first walk, so a state qualifies exactly as a driver does and
    the two can be enumerated in one pass.
    """
    cached = _declared_state_cache.get(node_class)
    if cached is None:
        found = {}
        for klass in reversed(getattr(node_class, '__mro__', ())):
            for name, value in vars(klass).items():
                if isinstance(value, StateDeclaration):
                    found[name] = value
        cached = _declared_state_cache[node_class] = found
    return cached


def drive_tree(root, resolve, visit=None, collected=None):
    """Walk `root`'s tree in linked order, binding driver values, and
    return `{qualified_id: declaration}` for every driver found.

    This is the one mechanism every qualified pass shares: the
    simulation's enumeration, the document's symbolic serialization
    mode, and the loader's default binding all differ only in what
    `resolve(node, path, name, declaration)` returns.

    The ORDER is the load-bearing part, and mirrors
    `InternalNode.as_scad` and `core/serializer.serialize_node`: bind
    EVERY node's drivers over the tree, linking each child before
    recursing into it so a child's own read already knows its derived
    name and parent -- then render the tree, ONCE, which is where
    expressions are built and an unbound driver would fail loudly. That
    is what makes eager qualification correct rather than lucky, and
    (`whole-tree-fixpoint`) it is also what a NESTED driver needs: a
    render() now drives every descendant's simulate phase in one pass,
    so a node two levels down would otherwise have its phase run, and
    fail on its own still-unbound driver, before this walk ever
    reached it to bind one.

    Binding writes the node's snapshot directly rather than going
    through `set_state`. That is deliberate: `_validate_state` judges
    every value a plain number, and the symbolic mode's values are
    deliberately not numbers. The numeric door stays as strict as it
    was; this is a different door, and it never leaves holes -- it binds
    every declared driver of the tree or raises.

    `visit(node, path, children)`, when given, is called for every
    assembly in the walk after its drivers are bound and before anything
    in the tree renders, so a caller that also needs something else
    declared per node (instructions, a joint coordinate) pays for one
    walk rather than two. `children` is what the walk is about to
    descend into, handed over rather than looked up again: a LEAF holds
    no snapshot, so the walk never visits it on its own, and a caller
    that has to reach a leaf's declarations -- a joint may be declared
    on one -- would otherwise have to re-derive the structure and risk
    getting a different generation of a legacy render's children.

    `collected`, when given a dict, receives every declared STATE of the
    tree by the same qualified id -- from THIS pass, never a second one
    (OpenSpec change ``declare-the-state``). States are BOUND either
    way, because a tree that declares one cannot be rendered without
    them; the dict is only how a caller that needs the table gets it.
    """
    # Deferred: `assembly` is `qualified`'s own caller (AssemblyNode's
    # module already imports THIS one, for `declared_drivers_of` and
    # `driver_id`), so the import has to wait until this function is
    # actually called, once both modules exist.
    from .assembly import _rest_children

    found = {}

    def deliver(node, path):
        states = getattr(node, '_states', None)
        if states is None:
            # A leaf holds no snapshot and no children of its own: the
            # same tolerance set_state has always had.
            return
        for name, declaration in declared_drivers_of(type(node)).items():
            identifier = driver_id(path, name)
            found[identifier] = declaration
            states[name] = resolve(node, path, name, declaration)
        # A STATE is bound in the SAME pass, never in a second walk
        # (OpenSpec change ``declare-the-state``, design section 16): a
        # tree that declares none pays one cached dict lookup per node
        # and nothing else, and one that declares some has every state
        # bound before anything in the tree renders, exactly as a
        # declared driver default is.
        declared_here = declared_states_of(type(node))
        for name, declaration in declared_here.items():
            identifier = driver_id(path, name)
            claimed = found.get(identifier)
            if claimed is not None:
                raise DriverIdError(
                    f"the qualified id '{identifier}' is claimed by two "
                    f"declarations of one tree: the State '{name}' of "
                    f"{type(node).__name__} and the Driver '{name}' it "
                    f"inherits ({claimed!r}). A qualified id names at "
                    f"most one declaration -- it is the key of the bank, "
                    f"the name a document publishes and the name a "
                    f"request addresses -- so rename one of them.")
            if collected is not None:
                collected[identifier] = declaration
            states[name] = resolve(node, path, name, declaration)
        # Rest-only: discovers structure and links exactly as a render()
        # would, without opening a phase or an enumeration, so every
        # node's OWN drivers are bound before ANY of them simulates.
        children = _rest_children(node)
        if visit is not None:
            visit(node, path, children)
        for child in children:
            deliver(child, path + (child.name,))

    deliver(root, ())
    if getattr(root, '_states', None) is not None:
        root.render()
    return found
