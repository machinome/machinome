## MODIFIED Requirements

### Requirement: A marking is declared on a rigid part

The system SHALL accept a **marking** as a class-body declaration on a node
class: an attribute holding `Marking(artwork, placement, color=...)`, where
`artwork` names the drawing, `placement` says where on the part it sits, and
`color` is its colour. `Marking`, together with the artwork source `Svg` and
the placements `Wrapped` and `Flat`, SHALL be imported from
`machinome.node.markings`, their one import path: the node root resolves none
of them (`node-model`, "The node package's root exports nothing").

A marking SHALL take its name from the attribute it is assigned to, SHALL be
recorded in declaration order, and SHALL be inherited through the method
resolution order like any class attribute — including from a **plain mixin**
class that is not itself a node, whose marking is collected when a node class
inherits it, refused there if that node is not rigid, and whose artwork path
resolves against the mixin's own module. A subclass assigning `None` to that
attribute SHALL declare no marking of that name, so a variant part can be the
same solid without its label.

A marking SHALL be declared only on a **rigid** node. A marking declared on an
`AssemblyNode`, on a flexible leaf, or on any other non-rigid node SHALL be
refused when the class is created, with an error naming the class and the
attribute.

A marking's attribute name SHALL NOT clash with a declared parameter, a
declared child, a port or a joint coordinate of the same class, and SHALL NOT
shadow an attribute the node class already carries — `color`, `files`,
`model`, `mtime` and every other attribute a node is read for — because a
marking is read as an attribute of its node and would hide that attribute for
good, exactly as a parameter of that name would. A clash of either kind SHALL
be refused when the class is created, naming the class, the attribute and what
it collides with.

A `Marking` whose artwork is not an artwork source, whose placement is not a
placement, or whose `color` is missing or is not in `#RRGGBB` form SHALL be
refused when the class is created, naming the class and the attribute; an
invalid colour SHALL raise `ValueError`, as an invalid node colour does.

#### Scenario: A part declares the artwork it carries

- **WHEN** a rigid leaf's class body assigns
  `digits = Marking(Svg('results_dial.svg'), Wrapped(axis=(0, 0, 1),
  radius=9.45, at=(0, 0, 18.45)), color='#FFFFFF')`
- **THEN** the class is created, the marking is named `digits`, and the node
  reports one declared marking

#### Scenario: A subclass drops an inherited marking

- **WHEN** a subclass of a part that declares `digits` assigns
  `digits = None`
- **THEN** the subclass declares no marking, while the base class still
  declares its own

#### Scenario: Two markings keep their declaration order

- **WHEN** a part declares `digits` and then `arrows`
- **THEN** its declared markings are reported in that order

#### Scenario: An assembly cannot carry a marking

- **WHEN** an `AssemblyNode` subclass declares a marking
- **THEN** creating the class raises, naming the class and the attribute, and
  saying a marking belongs on a rigid part

#### Scenario: A flexible leaf cannot carry a marking

- **WHEN** a flexible leaf subclass declares a marking
- **THEN** creating the class raises, naming the class and the attribute

#### Scenario: A marking cannot take a parameter's name

- **WHEN** a part declares the parameter `digits` and a marking named `digits`
- **THEN** creating the class raises, naming the class, the attribute and the
  parameter it collides with

#### Scenario: A marking cannot shadow a node attribute

- **WHEN** a part declares a marking named `color`
- **THEN** creating the class raises, naming the class, the attribute and the
  node attribute it would shadow, as a parameter of that name is already
  refused

#### Scenario: A marking declared in a plain mixin belongs to the node

- **WHEN** a plain class that is not a node declares a marking in its body and
  a rigid node class in another module inherits that class
- **THEN** the node class reports that marking, and its artwork path resolves
  against the directory of the module that declared it

#### Scenario: A marking must state a valid colour

- **WHEN** a part declares `Marking(..., color='white')`
- **THEN** creating the class raises `ValueError`, naming the class and the
  attribute
