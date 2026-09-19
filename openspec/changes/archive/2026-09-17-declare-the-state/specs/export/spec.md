## ADDED Requirements

### Requirement: A clocked model is refused publication

A tree in which anything declares a `State` SHALL be REFUSED publication, by
name, at the one function EVERY document producer passes through — the place
a document's body is assembled, so that no producer can reach a document by a
route the refusal does not cover. The refusal SHALL name the states by their
qualified ids and SHALL say that the document version carrying declared
states is not defined yet, so a reader knows the model is correct and the
wire format is missing rather than the reverse.

The refusal SHALL reach EVERY entry point that produces a document, and each
SHALL be verified rather than assumed: publishing a build, exporting a
model, the development server's own publish, and a browser-rendered
snapshot — the last of which stages a baked document WITHOUT entering the
symbolic-driver walk, and is therefore the case that proves the refusal is
not placed on that walk alone. No document SHALL be written and no partial
output SHALL be left behind by a refused publication.

The refusal SHALL NOT reach anything that produces no document: rendering,
assembling, STL building, the test runner, and a snapshot taken with the
OpenSCAD renderer SHALL each be untouched, so a clocked model can be built,
photographed, inspected and tested in Python while it cannot be published.

The refusal SHALL NOT be an option a producer can bypass. No document version
SHALL be emitted for a clocked model, and in particular a clocked model SHALL
NOT be published at an existing version with its states rendered as their
initial values: the geometry would be correct only at the initial state and
would then silently stop following the machine, which is exactly the failure
the non-additive version rule exists to prevent.

#### Scenario: A clocked model is refused by name

- **WHEN** a root whose tree declares `units = State(default=0)` is
  serialized
- **THEN** publication is refused naming `units` and saying the document
  version carrying declared states is not defined yet, and no document is
  written

#### Scenario: Every document producer refuses a clocked model

- **WHEN** a clocked model is published through a build, through an export,
  through the development server's publish, and through a browser-rendered
  snapshot
- **THEN** each is refused naming the states, no document file is written by
  any of them, and no staging directory or partial artifact is left behind

#### Scenario: Everything that writes no document is untouched

- **WHEN** a clocked model is rendered, assembled, has its STLs built, is run
  under the test runner, and is photographed with the OpenSCAD renderer
- **THEN** each succeeds, and only the document producers are refused

#### Scenario: A stateless model publishes unchanged

- **WHEN** a model that declares no `State` is serialized
- **THEN** its document is identical byte for byte to the one it published
  before this capability existed
