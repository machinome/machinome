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

An artwork path whose real path is not under the real path of the
declaring module's project root SHALL be refused the same way, with
`ValueError`, naming the resolved path and the project root; a module
that lies in no project is not judged.

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

#### Scenario: Artwork outside the project is refused

- **WHEN** a marking declares `Svg('../../outside.svg')` and that path
  resolves to an existing file above the declaring module's project root
- **THEN** creating the class raises `ValueError` naming the resolved path
  and the project root
