## MODIFIED Requirements

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
`scale` SHALL be positive, and a non-positive `scale` SHALL be refused naming
the value: a negative scale mirrors every region of the drawing, which reverses
the side the built decal faces and renders every glyph backwards, and a zero
scale collapses the artwork to a point.

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

#### Scenario: A non-positive scale is refused

- **WHEN** a marking declares `Svg('label.svg', scale=-1.0)`, or `scale=0`
- **THEN** it is refused naming the value

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

The artifact's triangles SHALL wind so that each triangle's normal points
**away from the part** — radially outward from the wrap axis for a `Wrapped`
placement, and along the declared `normal` for a `Flat` one — whatever
orientation the drawing tool gave the closed regions the artwork was read
from. The winding SHALL therefore be a property of this producer and not of
the artwork file or of the library that read it: a drawing whose regions
arrive facing the other way SHALL produce the same outward-facing decal as one
whose regions arrive facing the right way, byte for byte.

Orienting the artwork SHALL change nothing about a decal built from regions
that already face outward. Such a decal's bytes SHALL be unchanged, and the
marking artifact's producer recipe SHALL be unchanged, so no decal already on
disk is stale on this account.

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

#### Scenario: A wrapped decal faces outward from reversed artwork

- **WHEN** a part's artwork yields its closed regions facing the opposite way
  and the part declares `Wrapped(axis=(0, 0, 1), radius=9.45, ...)`
- **THEN** every triangle of the built decal has a normal pointing away from
  that axis

#### Scenario: A flat decal faces along its declared normal

- **WHEN** the same reversed artwork is placed with `Flat(at=..., normal=n,
  x_axis=...)`
- **THEN** every triangle of the built decal has a normal pointing along `n`

#### Scenario: Correctly faced artwork is untouched

- **WHEN** a decal whose artwork regions already face outward is rebuilt
- **THEN** its bytes and its producer recipe are what they were before the
  producer oriented anything
