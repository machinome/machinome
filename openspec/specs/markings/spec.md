# markings Specification

## Purpose
TBD - created by archiving change carry-markings-on-a-part. Update Purpose after archive.
## Requirements
### Requirement: A marking is declared on a rigid part

The system SHALL accept a **marking** as a class-body declaration on a node
class: an attribute holding `Marking(artwork, placement, color=...)`, where
`artwork` names the drawing, `placement` says where on the part it sits, and
`color` is its colour. `Marking`, together with the artwork source `Svg` and
the placements `Wrapped` and `Flat`, SHALL be importable from
`solid_node.node.markings` and SHALL also resolve from `solid_node.node`.

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

### Requirement: A marking's artwork is a declared drawing file

The system SHALL take a marking's artwork from `Svg(path, scale=None)`, where
`path` names an SVG file relative to the directory of the Python module that
**declared** the marking — so a subclass inheriting a marking reads the file
the declaring module meant. A path that does not exist, or that resolves to
something that is not a regular file, SHALL be refused when the class is
created, naming the class, the attribute, the declared value and the absolute
path it resolved to, in the same failure family as a leaf whose declared source
file is missing.

The artwork SHALL be reduced to the drawing's **closed regions**: the file's
own origin is preserved, its Y axis is flipped into model orientation, and each
closed region becomes one face carrying its enclosed regions as holes, so a
digit's counters are holes without any rule of the project's. Open paths SHALL
be ignored, and when the marking is built the system SHALL log at INFO the
artwork file and how many open paths it ignored, because a drawing's sheet
border is an open path that registers the artwork and is not part of it —
dropped silently it would leave a modeller wondering why the drawing does not
fit. Artwork containing no closed region SHALL be refused, naming the file.

Artwork coordinates SHALL be read as millimetres. `scale`, when given, SHALL
multiply every artwork coordinate, for a file authored in other units.

#### Scenario: A drawing's glyphs become the marking

- **WHEN** a marking's artwork is an SVG holding ten digits drawn as closed
  outlines with counters
- **THEN** the marking is built from ten regions and each counter is a hole

#### Scenario: A sheet border is reported, not drawn

- **WHEN** a marking's artwork is an SVG whose closed regions are surrounded
  by an open rectangular border
- **THEN** the border contributes nothing to the marking, the build logs at
  INFO the artwork file and the number of open paths it ignored, and the
  regions are placed at the coordinates the file gives them

#### Scenario: A drawing with nothing closed is refused

- **WHEN** a marking's artwork is an SVG of open paths only
- **THEN** the build fails naming the file and saying it holds no closed region

#### Scenario: A missing artwork file is refused at the declaration

- **WHEN** a part declares a marking whose `Svg` path does not exist
- **THEN** creating the class raises, naming the class, the attribute, the
  declared value and the absolute path, and no artifact is written

#### Scenario: An artwork authored in other units is scaled

- **WHEN** a marking declares `Svg('label.svg', scale=25.4)`
- **THEN** every artwork coordinate is multiplied by 25.4 before it is placed

### Requirement: A marking is placed on a cylinder or on a plane

The system SHALL place a marking's artwork by one of two placements, in the
part's **own adjusted frame** — the frame the part's artifact is written in.
Both SHALL land the artwork point `origin`, which defaults to `(0, 0)`, at the
placement's origin. Vectors need not be unit length.

`Flat(at, normal, x_axis, origin=(0, 0))` SHALL place the artwork on the plane
through `at` with the given normal: artwork X runs along `x_axis`
orthogonalized against `normal`, and artwork Y along `normal × x_axis`. An
`x_axis` parallel to `normal` SHALL be refused, naming both.

`Wrapped(axis, radius, at, start=0, origin=(0, 0), pitch=None, zero=None)`
SHALL wrap the artwork onto the cylinder of that radius about that axis through
`at`: artwork X is **arc length**, so a point at artwork x sits at the angle
`start + degrees(x / radius)`, and artwork Y is **height along the axis** from
`at`. A positive angle SHALL turn right-handed about `axis`. `radius` SHALL be
positive.

The angle's zero direction SHALL be stated, not inferred. When `zero` is given
it SHALL be that direction, projected perpendicular to `axis` and refused when
parallel to it. When `zero` is omitted the zero direction SHALL be derived
deterministically from the axis so that for a principal axis it is **the next
principal axis in right-hand order** — `+Z` wraps from `+X`, `+X` from `+Y`,
`+Y` from `+Z` — and the one axis direction for which the derivation is
undefined SHALL be refused naming `zero` as the remedy.

`pitch`, when given, SHALL stamp the whole artwork repeatedly every `pitch`
degrees around the axis. `pitch` SHALL be positive and SHALL divide 360
degrees a whole number of times; any other value SHALL be refused naming the
value and the nearest whole count.

#### Scenario: The artwork wraps at the declared radius

- **WHEN** a part declares `Wrapped(axis=(0, 0, 1), radius=9.45,
  at=(0, 0, 18.45))` over an artwork 6 mm tall
- **THEN** every point of the built marking lies on the cylinder of radius
  9.45 about the Z axis, and spans 6 mm of Z above z = 18.45

#### Scenario: Arc length is preserved around the wrap

- **WHEN** an artwork 59.376 mm wide is wrapped at radius 9.45
- **THEN** it closes on itself exactly once, because the circumference is
  59.376 mm

#### Scenario: The angular zero is the next principal axis

- **WHEN** a marking is wrapped about `(0, 0, 1)` with `start=0` and its
  artwork origin at artwork x = 0
- **THEN** that point of the artwork sits on the `+X` side of the axis

#### Scenario: A stated zero wins

- **WHEN** the same marking declares `zero=(0, 1, 0)`
- **THEN** that point of the artwork sits on the `+Y` side of the axis

#### Scenario: A zero parallel to the axis is refused

- **WHEN** a marking declares `Wrapped(axis=(0, 0, 1), ..., zero=(0, 0, 1))`
- **THEN** it is refused naming both directions

#### Scenario: An axis with no derivable zero is refused

- **WHEN** a marking declares `Wrapped(axis=(1, 1, 1), ...)` and no `zero`
- **THEN** it is refused naming the axis and `zero` as the remedy

#### Scenario: A repeating artwork is stamped around the circle

- **WHEN** a marking declares `pitch=36`
- **THEN** the artwork is stamped ten times, at 36-degree intervals

#### Scenario: A pitch that does not divide the circle is refused

- **WHEN** a marking declares `pitch=50`
- **THEN** it is refused naming the value and the nearest whole count

#### Scenario: A flat marking lies on its declared plane

- **WHEN** a part declares `Flat(at=(0, -40, 12), normal=(0, -1, 0),
  x_axis=(1, 0, 0))`
- **THEN** every point of the built marking lies on the plane y = -40, with
  artwork X along `+X`

#### Scenario: A flat marking needs two independent directions

- **WHEN** a part declares `Flat(at=(0, 0, 0), normal=(0, 0, 1),
  x_axis=(0, 0, 2))`
- **THEN** it is refused naming the normal and the x axis

#### Scenario: A marking rides its part's placement

- **WHEN** a part carrying a marking is placed by an assembly and turned by a
  joint
- **THEN** the marking's geometry is unchanged and appears wherever the part's
  own placement puts it, at every instant, with nothing declared about time

### Requirement: A marking is built as its own artifact beside the part

The system SHALL build one artifact per declared marking, beside the part's
own STL and under the same basename, holding the artwork's surface in the
part's adjusted frame. The surface SHALL sit on the nominal cylinder or plane
with **no offset**: any separation a renderer needs to avoid z-fighting is that
renderer's constant and is not a claim about where the part's surface is.

A wrapped marking's surface SHALL follow its cylinder to within the part's own
tessellation precision — the part's declared linear deflection where it
declares one, and the framework's default otherwise — so a wrapped artwork is
an arc and not a chord.

The marking artifact SHALL go through the same artifact lifecycle as the
part's other artifacts: written atomically and stamped, regenerated when
stale, and not rewritten when current.

Every declared marking's currency SHALL be checked on every build of its part,
whether or not the part's own solid is current, and a stale or missing marking
artifact SHALL be regenerated **without the part's solid being re-derived**: a
lost decal comes back, and it costs no render. A part whose solid is current
SHALL NOT have that currency check skipped, and a part whose markings are all
current SHALL NOT have its solid re-derived on their account either.

#### Scenario: A build produces the decal

- **WHEN** a project containing a part that declares one marking is built
- **THEN** an artifact for that marking exists beside the part's `.stl`,
  holding the artwork's surface

#### Scenario: Two markings on one part are two artifacts

- **WHEN** a part declares `digits` and `arrows`
- **THEN** two distinct marking artifacts exist, each named for its attribute

#### Scenario: A current marking is not rewritten

- **WHEN** a part whose artifacts, markings included, are all current is
  prepared
- **THEN** no artifact is rewritten

#### Scenario: A missing marking alone forces regeneration

- **WHEN** a part's STL is current but one marking artifact has been deleted
- **THEN** the build regenerates that marking artifact, the part's render is
  not run, and the STL is not re-derived

#### Scenario: A wrapped decal follows its cylinder

- **WHEN** an artwork whose regions span several millimetres of arc is wrapped
  at radius 9.45
- **THEN** no point of the built surface departs from that cylinder by more
  than the part's declared tessellation precision

### Requirement: A marking has its own currency, separate from the solid's

The marking artifact's tracked sources SHALL be the part's own tracked source
set **together with the artwork file**, and the artwork file SHALL NOT join the
part's tracked source set.

Therefore editing the **artwork** SHALL regenerate that marking's artifact and
SHALL leave the part's STL and BREP current, and a stale or missing marking
SHALL never cause the part's solid to be re-derived.

Editing the **declaration** — the placement, the colour, or the artwork path —
changes the part's own source, and therefore rebuilds the part's solid as any
other source edit does.

#### Scenario: Editing the artwork rebuilds only the decal

- **WHEN** the SVG a marking names is modified after a build
- **THEN** the marking's artifact is regenerated, and the part's STL and BREP
  report current and are not rewritten

#### Scenario: A deleted decal leaves the solid alone

- **WHEN** a marking artifact is deleted and the project is rebuilt
- **THEN** the marking artifact is written again, the part's render is not run,
  and its STL and BREP are not re-derived

#### Scenario: Editing the declaration rebuilds the part

- **WHEN** a marking's declared placement is edited
- **THEN** the part's artifacts are regenerated, as they are for any edit to
  the module that declares the part

### Requirement: A marking contributes no solid and is not a part

A marking SHALL contribute no solid. A part's volume, bounds, STL bytes, BREP
bytes and piece id SHALL be identical whether or not it declares markings, and
`assertNoIntersectingSolids`, `assertNoDisconnectedSolids` and every pairwise
interference sweep SHALL return the same verdict, under the faceted and the
exact comparison kernel alike.

A marking SHALL NOT be a node and SHALL NOT be a child. A part's `children`,
the shape of the tree, an assembly's part count and the published piece
inventory SHALL be unchanged by a marking, and a marking SHALL NOT be
addressable as a part.

A marking SHALL NOT enter the part's artifact identity: adding or removing a
marking declaration SHALL leave the part's `uniq_id` exactly as it was, because
a marking is not a parameter.

#### Scenario: The solid is byte-identical with and without markings

- **WHEN** two node classes of the same name and the same parameters build the
  same solid, one of them additionally declaring a marking
- **THEN** their STL artifacts hold identical bytes, their BREP artifacts hold
  identical bytes, and both report the same piece id

#### Scenario: A marking changes no geometric verdict

- **WHEN** an assembly whose parts carry markings runs
  `assertNoIntersectingSolids` and `assertNoDisconnectedSolids`, faceted and
  exact
- **THEN** every verdict equals the verdict the same assembly gives with the
  markings removed

#### Scenario: A marking is not in the tree

- **WHEN** a part declaring two markings is rendered and assembled
- **THEN** its `children` is empty, the assembly's part count is what it is
  without the markings, and no node of the tree is named for a marking

#### Scenario: A marking does not key the artifact

- **WHEN** two node classes of the same name and the same parameters are
  realized, one declaring a marking and one declaring none
- **THEN** both report the same `uniq_id`, so the marking changed no artifact
  key

