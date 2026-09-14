# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Controls: which part a person presses, and which part a person turns.

An `Instruction` says what a machine can be told; a control says HOW a
person tells it -- by touching a part of the machine rather than a
button on a panel beside it. `Button(part, instruction)` is a press on
`part` submitting the named instruction; `Turn(part, input)` is a drag
on `part`, about the rotational coordinate that part rides, issued as a
sequence of relative moves on `input`.

A control MOVES NOTHING. It names a request the run already accepts, so
ownership, admission, stops and outcomes stay exactly what `trigger`,
`move` and `rate` state, and a control carries no state of its own and
never repeats an instruction's definition.

**The part is a NODE, and the framework never guesses which one.** The
Pascaline module is the evidence: `tens.input.turn` is reached by
`tens_entry` AND by `units_entry` -- the carry from the column below
moves the tens dial too -- so no document can say which of the two a
hand on the tens dial means; and its number drum turns with an input a
hand may not touch at all, because the ratchet is on the input arbor and
the drum sits under the lid. Only the author knows. So the binding is
declared, and the GEOMETRY of the gesture is not: the tree already
carries the joint, its axis and the point it turns about.

What is checked HERE is what the value written in the class body IS: a
coordinate, a driver, a repeat or a plain number is refused in the
constructor, at the line that wrote it. What the DECLARING CLASS holds
needs the class, which does not exist while its body runs, so
`check_declared_on` is called by `NodeMeta.__new__` the moment it does
-- the same split, and the same two places, a relation already has.
`NodeMeta` recognizes a control by its own `control_kind`, duck-typed,
so `solid_node/node/` still imports nothing from this package.
"""

from solid_node.motion.couplings import (BroadcastRef, PathRef,
                                         _coordinate_of, _coordinates_of,
                                         _is_declaration_list, _named_in_body)
from solid_node.node.declarative import (ChildDeclaration, RepeatDeclaration,
                                         declared_children)
from solid_node.node.qualified import DriverDeclaration, declared_drivers_of


class Control:
    """The shared base of the control kinds: a reference to ONE part.

    `control_kind` is the whole of the protocol the node layer sees --
    the file's own style, which recognizes a coordinate by "it IS a port
    declaration" and a joint by "it OWNS one" rather than importing
    either.
    """

    control_kind = None

    def __init__(self, part):
        self.part = _part_ref(part, type(self).__name__)

    @property
    def written(self):
        """The part as the class body wrote it, for a message."""
        return self.part.written

    def check_declared_on(self, owner, name):
        """Refuse a part whose first segment is not a child `owner`
        declares -- everything else about the path was checked, segment
        by segment, as `read_through` built it.

        `PathRef.check_declared_on` performs the same test and says "in
        the relation"; a control is not a relation, and the message
        names the control instead.
        """
        first = self.part.root._name
        if first is None:
            raise TypeError(
                f"the control '{name}' of {owner.__name__} names a part "
                f"held in a LIST. A declaration held in a list is named "
                f"<attribute>-<index> and names one child per entry, so it "
                f"cannot be a control's part. Hold the "
                f"{self.part.root.node_class.__name__} on its own "
                f"attribute, or state the control inside it.")
        if declared_children(owner).get(first) is self.part.root:
            return
        declares = ', '.join(declared_children(owner)) or 'none'
        raise TypeError(
            f"{owner.__name__}: '{first}', the first segment of "
            f"{self.part.written} in the control '{name}', is not a child "
            f"{owner.__name__} declares. A control's part is walked from "
            f"the assembly that declares the control; {owner.__name__} "
            f"declares: {declares}.")

    def references(self):
        """What this control names besides its part, for a repr."""
        return ''


class Button(Control):
    """A press on `part` submits the named instruction.

    It is the panel's instruction button, moved onto the part, and it
    carries no movement of its own: the instruction states the travel
    and the duration, once, where it is declared. The name is resolved
    through the DECLARING NODE's own path, exactly as an instruction's
    target names are, so a button declared on a child at `('column',)`
    naming `'Add one'` names `'column.Add one'` -- a key of the tree's
    instruction table by construction rather than by two schemes
    agreeing.
    """

    control_kind = 'button'

    def __init__(self, part, instruction):
        super().__init__(part)
        if not isinstance(instruction, str):
            raise TypeError(
                f'a Button names its instruction by the name it is '
                f'declared under, as a string, not {instruction!r}. An '
                f'instruction is an entry of the instructions table, and '
                f'the button references it rather than repeating it.')
        self.instruction = instruction

    def references(self):
        return f' -> {self.instruction!r}'

    def __repr__(self):
        return f'<button on {self.part.written}{self.references()}>'


class Turn(Control):
    """A drag on `part`, about the rotational coordinate it rides, as a
    sequence of relative moves on `input`.

    `input` is the `Driver` DECLARATION, read off the class body that
    declares it -- never a qualified id string, which would give one
    value a second address and reopen the hole
    `solid_node.node.qualified` exists to close. A driver of a CHILD is
    named by declaring the control on the child, exactly as an
    instruction over a child's driver is; reading one off a child
    declaration is already refused by `read_through`.

    `Slide`, for a prismatic coordinate, is the obvious sibling and is
    deliberately not in this release: a `Turn` over a translational
    coordinate is refused by name.
    """

    control_kind = 'turn'

    def __init__(self, part, input):
        super().__init__(part)
        if isinstance(input, str):
            raise TypeError(
                f"a Turn names its input by its DECLARATION -- the "
                f"`Driver(...)` the class body assigns -- not by the "
                f"string {input!r}. A driver is addressed by the qualified "
                f"id its position in the tree gives it, and a second "
                f"address for one value is what that qualification "
                f"prevents.")
        if not isinstance(input, DriverDeclaration):
            raise TypeError(
                f'a Turn is a drag on a part issued as moves on an INPUT, '
                f'and an input is a Driver declared on the class stating '
                f'the control; got {input!r}.')
        self.input = input

    def references(self):
        return f' -> driver {self.input._name!r}'

    def check_declared_on(self, owner, name):
        super().check_declared_on(owner, name)
        declared = declared_drivers_of(owner)
        for local, declaration in declared.items():
            if declaration is self.input:
                return
        known = ', '.join(sorted(declared)) or 'none'
        raise TypeError(
            f"{owner.__name__}: the control '{name}' turns "
            f"{self.part.written} with a Driver {owner.__name__} does not "
            f"declare. A Turn's input is a driver of the class stating the "
            f"control -- a child's driver is named by declaring the control "
            f"on the child -- and {owner.__name__} declares: {known}.")

    def local_input_of(self, owner):
        """The class-local name `owner` declares this control's input
        under, checked by identity."""
        for local, declaration in declared_drivers_of(owner).items():
            if declaration is self.input:
                return local
        raise TypeError(
            f'{owner.__name__} declares no driver that is this control\'s '
            f'input; class definition refuses that, so reaching here means '
            f'the control was moved onto another class after it was '
            f'validated.')

    def __repr__(self):
        return f'<turn on {self.part.written}{self.references()}>'


def _part_ref(value, kind):
    """`value` as a reference to ONE part of the tree.

    A bare child declaration normalizes to a path of no segments,
    exactly as `couplings.coordinate_ref` does for a relation's end.
    Everything else is refused right here, naming what was written: the
    line in the class body is where the author can see it.
    """
    if isinstance(value, BroadcastRef):
        raise TypeError(
            f"a {kind} names ONE part, and '{value.written}' passes "
            f"through the repeated declaration "
            f"'{value.repeat._name}' of {value.repeat.node_class.__name__} "
            f"(count={value.repeat.count!r}): a repeated child names one "
            f"part per copy. Name one copy's own attribute, or state the "
            f"control inside {value.repeat.node_class.__name__}.")
    if isinstance(value, PathRef):
        _refuse_coordinate(value.terminal, value.written, kind)
        return value
    _refuse_coordinate(value, _named(value), kind)
    if isinstance(value, ChildDeclaration):
        return PathRef(value, (), value)
    if isinstance(value, RepeatDeclaration):
        raise TypeError(
            f"a {kind} names ONE part, and '{_named(value)}' is a repeated "
            f"declaration of {value.node_class.__name__} "
            f"(count={value.count!r}): a repeated child names one part per "
            f"copy. Name one copy's own attribute, or state the control "
            f"inside {value.node_class.__name__}.")
    if isinstance(value, DriverDeclaration):
        raise TypeError(
            f"a {kind} names a PART -- a node whose geometry a hand "
            f"touches -- and '{_named(value)}' is a Driver, which is an "
            f"INPUT: a value the run advances, with no geometry to touch.")
    if _is_declaration_list(value):
        name = _named(value)
        raise TypeError(
            f"a {kind} names ONE part, and '{name}' holds {len(value)} "
            f"children, each with its own arguments -- named '{name}-0', "
            f"'{name}-1', and so on. Name one child by its own attribute.")
    raise TypeError(
        f'a {kind} names a PART: a child the declaring assembly holds, or '
        f'a path of declared children through one (units.input.dial). '
        f'{value!r} is none of those.')


def _refuse_coordinate(value, written, kind):
    if _coordinate_of(value) is None and _coordinates_of(value) is None:
        return
    raise TypeError(
        f"a {kind} names a PART -- a node whose geometry a hand touches -- "
        f"not a coordinate, and '{written}' names one. A control's gesture "
        f"is about the coordinate the part RIDES, which the framework "
        f"finds from the tree: name the body that moves.")


def _named(value):
    """The name the class body gives `value`.

    `__set_name__` has not run while the body is still executing, so the
    EXECUTING NAMESPACE is asked first -- the same reason
    `couplings._named_in_body` exists, and the only way an error raised
    inside a class body can say `bank` rather than a list repr.
    """
    return (getattr(value, '_name', None) or _named_in_body(value)
            or getattr(value, 'name', None) or repr(value))
