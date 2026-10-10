## ADDED Requirements

### Requirement: A frame read off a child declaration is a place

Reading an attribute off a child declaration in a class body, where that
attribute is a FRAME the declared class carries (see the `mates`
capability), SHALL yield a FRAME REFERENCE: a place in the tree, like a
path reference to a port, never the frame's resolved numbers, which
belong to a realized instance and do not exist in a class body. A frame
reference SHALL be usable as either end of a mate and SHALL name no
coordinate: using it as an end of a relation, or reading an attribute
through it, SHALL be refused at class definition naming the path.

A frame reached through a repeated or a list-held child declaration
SHALL be refused as a mate end by the rules the `mates` capability
states; reading it SHALL NOT be refused merely for being written.

A class body reading an attribute off a declaration that the declared
class does not carry as a frame, a port, a joint or a child SHALL keep
raising exactly as it does today.

A child declaration that a mate moves SHALL realize its children as
instances of a class carrying the mate's joint, created once when the
declaring assembly's class is created and shared by every child that
declaration realizes, identical to the declared class in name, identity
and source — the rule a declaration-site joint already follows — so
every enumerator that reads the realized child's class reports the
mate's joint by the ordinary rules.

#### Scenario: A child's frame is named in the parent's body

- **WHEN** an assembly declares `art3 = Art3()`, `Art3` declaring the
  frame `hinge`, and its class body reads `art3.hinge`
- **THEN** the read yields a frame reference naming `art3.hinge`, and no
  instance of `Art3` is constructed

#### Scenario: A frame reference is not a coordinate

- **WHEN** a class body states `art3.hinge.drives(belt.travel)`
- **THEN** class definition raises, naming `art3.hinge` and saying a
  frame is a connector, not a coordinate

#### Scenario: A misspelled frame is still a misspelling

- **WHEN** a class body reads `art3.hnige` and `Art3` declares no
  attribute of that name
- **THEN** class definition raises naming the path and listing what
  `Art3` declares

#### Scenario: A mated child is realized as its own class

- **WHEN** an assembly mates its child `art3` and is realized
- **THEN** the realized child's class reports the name `Art3`, is a
  subclass of `Art3`, reports the mate's joint, and the child's identity
  equals that of an unmated `Art3` built with the same arguments
