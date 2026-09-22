# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Controls: which part a person presses, turns, or slides.

An `Instruction` says what a machine can be told; a control says HOW a
person tells it -- by touching a part of the machine rather than a
button on a panel beside it. `Button(part, instruction)` is a press on
`part` submitting the named instruction; `Turn(part, input)` is a drag
on `part`, about the rotational coordinate that part rides, and
`Slide(part, input)` is a drag ALONG the translational one, each issued
as a sequence of relative moves on `input`.

A body with ONE freedom needs nothing more: the framework walks up from
the part to the nearest joint the run banks. A body with two -- the
Curta's crank, which lifts and turns about the same line, and its
register carriage, which does the same -- has no nearest joint, and
`coordinate=` is where the author says which of its freedoms this
control means. It names an existing joint DECLARATION, by the same path
a relation's end is written (`crank.lift`), and it adds no joint, no
edge and no source: the selection is a reading of the tree.

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
so `machinome/node/` still imports nothing from this package.
"""

from machinome.motion.couplings import (BroadcastRef, OwnRef, PathRef,
                                         _coordinate_of, _coordinates_of,
                                         _is_declaration_list, _named_in_body)
from machinome.node.declarative import (ChildDeclaration, RepeatDeclaration,
                                         declared_children)
from machinome.node.qualified import (DriverDeclaration,
                                       StateDeclaration,
                                       declared_drivers_of)


class Control:
    """The shared base of the control kinds: a reference to ONE part.

    `control_kind` is the whole of the protocol the node layer sees --
    the file's own style, which recognizes a coordinate by "it IS a port
    declaration" and a joint by "it OWNS one" rather than importing
    either.
    """

    control_kind = None

    # The domain the gesture's coordinate must have, or `None` for a
    # control that is not a gesture at all: a press asks for a declared
    # instruction and needs no direction, so a `Button` names a sliding
    # part as readily as a turning one.
    required_domain = None

    def __init__(self, part, coordinate=None):
        self.part = _part_ref(part, type(self).__name__)
        self.coordinate = (None if coordinate is None
                           else _coordinate_ref(coordinate,
                                                type(self).__name__))

    @property
    def written(self):
        """The part as the class body wrote it, for a message."""
        return self.part.written

    @property
    def selected(self):
        """The coordinate selection as the class body wrote it, or
        `None` where the author left the coordinate to inference."""
        return (None if self.coordinate is None
                else self.coordinate.described())

    @property
    def selected_declaration(self):
        """The joint the explicit selection names, as far as the
        CLASSES alone can say -- no instance needed, which is what lets
        a joint owning several coordinates be refused before anything
        tries to walk to the node it poses."""
        if isinstance(self.coordinate, PathRef):
            return self.coordinate.terminal
        return self.coordinate.declared

    def selected_node(self, declaring):
        """The realized node the explicit selection's joint POSES,
        resolved on the instance that declares this control.

        A path names the node its coordinate belongs to, exactly as a
        relation's end does; a joint written bare in the class body is
        a joint of the DECLARING node, and poses it.
        """
        if isinstance(self.coordinate, PathRef):
            # The terminal is the whole JOINT, not one of its coordinates.
            # Drop that final segment even for a Free declaration, whose
            # coordinate count may itself have been changed by an override.
            path = self.coordinate
            node = path._step(declaring, path.root._name, path.written)
            for segment in path.segments[:-1]:
                node = path._step(node, segment, path.written)
            return node
        return declaring

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
        if declared_children(owner).get(first) is not self.part.root:
            declares = ', '.join(declared_children(owner)) or 'none'
            raise TypeError(
                f"{owner.__name__}: '{first}', the first segment of "
                f"{self.part.written} in the control '{name}', is not a "
                f"child {owner.__name__} declares. A control's part is "
                f"walked from the assembly that declares the control; "
                f"{owner.__name__} declares: {declares}.")
        self.check_selection_declared_on(owner, name)

    def check_selection_declared_on(self, owner, name):
        """Refuse a selected coordinate `owner` cannot reach: a path
        whose first segment is not a child it declares, or a bare joint
        it does not declare.

        The same test the part gets, for the same reason -- the classes
        are all known the moment `NodeMeta` builds this one, and a
        reference borrowed from another class is a mistake that should
        never survive to a render.
        """
        from machinome.motion.joints import declared_joints

        if self.coordinate is None:
            return
        if isinstance(self.coordinate, PathRef):
            first = self.coordinate.root._name
            if declared_children(owner).get(first) is self.coordinate.root:
                return
            declares = ', '.join(declared_children(owner)) or 'none'
            raise TypeError(
                f"{owner.__name__}: '{first}', the first segment of "
                f"{self.selected} in the control '{name}', is not a child "
                f"{owner.__name__} declares. A control's coordinate is "
                f"walked from the assembly that declares the control; "
                f"{owner.__name__} declares: {declares}.")
        declared = declared_joints(owner)
        if any(self.coordinate.declared is joint
               for joint in declared.values()):
            return
        known = ', '.join(declared) or 'none'
        raise TypeError(
            f"{owner.__name__}: the control '{name}' names the joint "
            f"'{self.selected}', which {owner.__name__} does not declare. "
            f"A control's coordinate is a joint of the class stating the "
            f"control or of a child it declares -- reached by path "
            f"(crank.turn) -- and {owner.__name__} declares: {known}.")

    def references(self):
        """What this control names besides its part, for a repr."""
        return ''

    @property
    def about(self):
        """The selection, for a repr: empty where there is none."""
        return '' if self.coordinate is None else f' at {self.selected}'


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

    A press has no direction, so a button names a translational
    coordinate as readily as a rotational one: what it asks for is an
    instruction, and the instruction states the travel.
    """

    control_kind = 'button'

    def __init__(self, part, instruction, *, coordinate=None):
        super().__init__(part, coordinate)
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
        return (f'<button on {self.part.written}{self.about}'
                f'{self.references()}>')


class Drag(Control):
    """The shared base of the two gestures: a drag on `part`, issued as
    a sequence of relative moves on `input`.

    `input` is the `Driver` DECLARATION, read off the class body that
    declares it -- never a qualified id string, which would give one
    value a second address and reopen the hole
    `machinome.node.qualified` exists to close. A driver of a CHILD is
    named by declaring the control on the child, exactly as an
    instruction over a child's driver is; reading one off a child
    declaration is already refused by `read_through`.

    A subclass is the whole of the difference: its `control_kind` and
    the `required_domain` its coordinate must have. Neither states an
    axis, a pivot, a direction or a scale -- the tree carries the first
    three and the compiled program the fourth.
    """

    def __init__(self, part, input, *, coordinate=None):
        super().__init__(part, coordinate)
        kind = type(self).__name__
        if isinstance(input, str):
            raise TypeError(
                f"a {kind} names its input by its DECLARATION -- the "
                f"`Driver(...)` the class body assigns -- not by the "
                f"string {input!r}. A driver is addressed by the qualified "
                f"id its position in the tree gives it, and a second "
                f"address for one value is what that qualification "
                f"prevents.")
        if isinstance(input, StateDeclaration):
            raise TypeError(
                f"a {kind}'s input is a DRIVER, and '{input._name}' is a "
                f"State. A state is written by the machine at an event, "
                f"through the committing relation that names it as a "
                f"target -- a hand does not drag it, and the direct "
                f"operation a control exists for is what a register "
                f"editor is not. Name the driver whose motion the event "
                f"is located on.")
        if not isinstance(input, DriverDeclaration):
            raise TypeError(
                f'a {kind} is a drag on a part issued as moves on an '
                f'INPUT, and an input is a Driver declared on the class '
                f'stating the control; got {input!r}.')
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
            f"{owner.__name__}: the control '{name}' drags "
            f"{self.part.written} with a Driver {owner.__name__} does not "
            f"declare. A {type(self).__name__}'s input is a driver of the "
            f"class stating the control -- a child's driver is named by "
            f"declaring the control on the child -- and {owner.__name__} "
            f"declares: {known}.")

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
        return (f'<{self.control_kind} on {self.part.written}{self.about}'
                f'{self.references()}>')


class Turn(Drag):
    """A drag on `part`, ABOUT the rotational coordinate it rides."""

    control_kind = 'turn'
    required_domain = 'rotational'


class Slide(Drag):
    """A drag on `part`, ALONG the translational coordinate it rides.

    The prismatic sibling of `Turn`, and identical to it in everything
    but the domain it requires: the Curta's setting selectors run in
    their slots, its crank lifts before it turns, and a vertical pointer
    movement translated into a fake rotational input would misdescribe
    every one of them.
    """

    control_kind = 'slide'
    required_domain = 'translational'


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


def _is_joint(value):
    """Whether `value` is a joint DECLARATION: something that OWNS a
    coordinate rather than being one.

    The file's own duck-typed style, and the distinction the selection
    turns on: `units.turn` written in a class body is a `Revolute` that
    owns the port `units.turn`, while `gauge.hand` may be a plain
    `RotationalPort` -- a value an author's own `render()` turns, which
    no run banks and no gesture can be about.
    """
    if _coordinates_of(value) is not None:
        return True
    owned = _coordinate_of(value)
    return owned is not None and owned is not value


def _coordinate_ref(value, kind):
    """`value` as a reference to ONE JOINT of the tree.

    The same normalization a relation's end gets, narrowed to what a
    control may select: the joint declaration itself, written bare in
    the class body that declares it, or a path of declared children
    ending on one (`crank.turn`, `register.marker.turn`). A qualified
    id string is refused for the reason a `Turn`'s input is: one value,
    one address.

    Whether the joint actually poses this control's part, whether the
    run banks its coordinate and whether it owns only one are questions
    about the TREE, and are asked where the tree exists -- at compile,
    by `_selected_joint`.
    """
    if isinstance(value, BroadcastRef):
        raise TypeError(
            f"a {kind} names ONE coordinate, and '{value.written}' passes "
            f"through the repeated declaration '{value.repeat._name}' of "
            f"{value.repeat.node_class.__name__} "
            f"(count={value.repeat.count!r}): a repeated child names one "
            f"joint per copy. Name one copy's own attribute, or state the "
            f"control inside {value.repeat.node_class.__name__}.")
    if isinstance(value, PathRef):
        if value.root._name is None:
            raise TypeError(
                f"a {kind}'s coordinate is held in a LIST. A declaration "
                f"held in a list is named <attribute>-<index> and names one "
                f"child per entry, so it cannot be a control's coordinate. "
                f"Hold the {value.root.node_class.__name__} on its own "
                f"attribute, or state the control inside it.")
        if not _is_joint(value.terminal):
            raise TypeError(
                f"a {kind}'s coordinate names a JOINT -- the declaration "
                f"that POSES the part -- and '{value.written}' does not. A "
                f"control's gesture is a joint's motion; a plain port an "
                f"author's own render() turns is not one, and a single "
                f"coordinate of a joint that owns several is not one "
                f"either.")
        return value
    if isinstance(value, str):
        raise TypeError(
            f"a {kind} names its coordinate by the joint DECLARATION -- "
            f"the `Revolute(...)` or `Prismatic(...)` the class body "
            f"assigns, or a path of declared children to one -- not by the "
            f"string {value!r}. A coordinate is addressed by the qualified "
            f"id its position in the tree gives it, and a second address "
            f"for one value is what that qualification prevents.")
    if _is_joint(value):
        return OwnRef(value)
    raise TypeError(
        f"a {kind}'s coordinate names a JOINT: the declaration that poses "
        f"the part, written as the class body writes it "
        f"(crank.turn), or a joint of the declaring class itself. "
        f"{value!r} is none of those.")


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
