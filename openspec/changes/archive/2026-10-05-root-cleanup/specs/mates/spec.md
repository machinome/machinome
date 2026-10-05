## MODIFIED Requirements

### Requirement: A mate attaches frames through an existing child joint

The system SHALL accept `moving_child.frame.on(fixed_frame, moving_child.joint)` in an assembly class body where the explicit declaration reference names an existing one-coordinate Revolute or Prismatic joint on that exact directly declared moving child. It SHALL accept a class-declared or declaration-site joint, including a supported inherited joint, with its existing name and unit. The mate SHALL place the frames by the existing rest-placement rule and SHALL reuse the joint rather than install, rename, replace, reorder or mutate it. Its axis, anchor, range, arguments, original class/site frame and Bound read declarer SHALL be preserved. The frame SHALL not supply axis or anchor defaults to the referenced joint. Class-shared joint metadata and existing child specialization SHALL not be changed by attachment.

The mate name SHALL name the attachment handle only and SHALL not be required to be a free attribute name on the child. Existing end scope, one mate per moving child, fixed-end, inheritance, list/repeat and render-placement restrictions SHALL remain. Strings, a bare foreign class Joint declaration, implicit whole-node selection, another child's joint, deeper descendant joints, ports, derived coordinates, Orbit, Free or components of multi-coordinate joints SHALL be refused by name. No joint_name keyword or other naming-string API SHALL be introduced.

#### Scenario: The complete declared-reference example runs

- **WHEN** the following declarations are realized and rendered

```python
from machinome.node.assembly import AssemblyNode
from machinome.node.frames import Frame
from machinome.motion.joints import Revolute

class Dial(AssemblyNode):
    axle = Frame()
    turn = Revolute(axis=(0, 0, 1))

class Register(AssemblyNode):
    ones_seat = Frame(at=(10, 0, 0))
    ones = Dial()
    ones_mount = ones.axle.on(ones_seat, ones.turn)
```

- **THEN** ones rests with its axle at (10, 0, 0), its original turn joint remains, and no ones_mount joint or assembly coordinate is created

#### Scenario: Sibling dials retain their repeated local names

- **WHEN** a register attaches two children with uniquely named mates referencing each child's turn joint
- **THEN** the original ones.turn and tens.turn endpoints remain distinct and neither is renamed after its mate

#### Scenario: A site joint keeps its original scope and carried line

- **WHEN** a child is declared with a site Revolute or Prismatic whose arguments and Bound read the declaring parent, then attached through that explicit child-joint reference
- **THEN** its original resolved arguments, parent frame/carry, bound reads and joint order remain unchanged and no mate-generated scope replaces them

#### Scenario: A class joint keeps its own Bound scope

- **WHEN** a class-declared joint's Bound reads that child's declared coordinate and the parent attaches its frames through that joint
- **THEN** the read still resolves in the child and a same-named parent coordinate cannot substitute for it

#### Scenario: Joint metadata stays independent of attachment sites

- **WHEN** two assemblies attach instances of the same child class at different frames and a third instance remains unattached
- **THEN** each original joint's name, owner, arguments and order are unchanged and attachment state does not leak into another instance or class

#### Scenario: An invalid joint reference is refused

- **WHEN** the attachment names another child's joint, a deeper descendant, a whole node, a string, a port, an Orbit or a Free coordinate
- **THEN** it is refused naming the reference and the requirement for an explicit scalar Revolute or Prismatic of the moving child

#### Scenario: Existing placement restrictions remain

- **WHEN** a reused-joint mate closes a second mate on the same child, uses a moving fixed sibling, or the parent render also places that child
- **THEN** the existing named refusal applies

### Requirement: A part declares named frames

The system SHALL accept a **frame** as a class-body declaration on a node
class: an attribute holding `Frame(at=(0, 0, 0), z=(0, 0, 1), x=None)`,
an origin `at` and a right-handed triad whose third axis is `z`, stated
in the declaring node's OWN rest frame — the frame its own `render()`
states its geometry in, the frame a class-declared joint is read in.
`Frame` SHALL be imported from `machinome.node.frames`, its one import
path: the node root does not resolve it (`node-model`, "The node package's
root exports nothing"). The framework SHALL transform nothing
when it reads a frame: the numbers are the declarer's own.

A frame SHALL be declarable on any node kind — a leaf adapter, a fusion,
an imported part and an `AssemblyNode` alike — because a frame is drawn
on nothing and an assembly's frames are its connectors to the assembly
above it.

A frame SHALL take its name from the attribute it is assigned to, SHALL
be reported in declaration order by an enumerator exported beside it,
without constructing an instance, and SHALL be inherited through the
method resolution order like any class attribute — including from a
plain mixin that is not a node. A subclass assigning `None` to that
attribute SHALL declare no frame of that name.

A frame's name SHALL NOT clash with a declared parameter, a declared
child, a port, a joint coordinate, a marking or a mate of the same
class, and SHALL NOT shadow an attribute every node carries; either
clash SHALL be refused when the class is created, naming the class, the
attribute and what it collides with.

A frame SHALL NOT be a parameter, a child, a port, a joint or a part: it
SHALL contribute no solid, no operation and no artifact, and adding,
removing or changing a frame SHALL change no node's identity and no
artifact key.

#### Scenario: A part declares a connector

- **WHEN** a forearm class body assigns
  `hinge = Frame(at=(0, 0, 81.5), z=(0, 1, 0), x=(1, 0, 0))`
- **THEN** the class is created, the frame is named `hinge`, and the
  class reports one declared frame, read off the class without
  constructing an instance

#### Scenario: An assembly declares its own connector

- **WHEN** an `AssemblyNode` subclass assigns
  `elbow_pin = Frame(at=(0, 160, 68), z=(0, 0, 1))`
- **THEN** the class is created and reports the frame `elbow_pin`

#### Scenario: A frame is inherited and can be dropped

- **WHEN** a base part declares `hinge` and `foot`, and a subclass
  assigns `foot = None`
- **THEN** the base reports `hinge` then `foot`, and the subclass reports
  `hinge` alone

#### Scenario: A frame declared in a plain mixin belongs to the node

- **WHEN** a plain class that is not a node declares a frame, and a node
  class inherits it
- **THEN** the node class reports that frame

#### Scenario: A frame cannot take a declared name

- **WHEN** a part declares the parameter `hinge`, or the joint `hinge`,
  and also a frame named `hinge`
- **THEN** creating the class raises, naming the class, the attribute and
  what it collides with

#### Scenario: A frame cannot shadow a node attribute

- **WHEN** a part declares a frame named `color`
- **THEN** creating the class raises, naming the class, the attribute and
  the node attribute it would shadow

#### Scenario: A frame is not identity

- **WHEN** two otherwise identical part classes differ only in a frame
  one of them declares
- **THEN** their realized instances have the same identity and key the
  same artifacts
