## ADDED Requirements

### Requirement: The package mounts a composed inspector into one host element

The package SHALL offer an inspector layout that a host mounts into a
single element it supplies — named directly or by selector — against a
published tree document, composing in that element an assembly sidebar
holding the package's own navigator and the viewer with its own on-screen
chrome. Mounting SHALL accept every option the plain viewer mount accepts,
plus whether the sidebar starts open or collapsed and the navigator's own
options, and SHALL resolve to a handle that exposes the mounted viewer
handle and the mounted navigator handle, reports whether the sidebar is
open, opens and closes it, and disposes the whole layout.

The layout SHALL give the viewer an element of its own inside the target
rather than the target itself, so that the viewer's own teardown cannot
remove the sidebar. Mounting SHALL require no UI framework of the host and
SHALL publish no file beyond the one bundle.

When the viewer refuses the document, the layout SHALL leave the target
empty and report the viewer's own refusal unchanged, rather than
presenting a sidebar around a viewer that does not exist.

#### Scenario: A host mounts an inspector with one call

- **WHEN** a host mounts the inspector into one element against a
  published document
- **THEN** that element contains the viewer with its chrome and an
  assembly sidebar showing the document's tree, and the returned handle
  gives the host the viewer handle and the navigator handle

#### Scenario: A document the viewer refuses

- **WHEN** the inspector is mounted against a document the viewer cannot
  render
- **THEN** the mount is refused with the viewer's own message, and the
  host's element is left empty

#### Scenario: The inspector disposes as one

- **WHEN** a host disposes the inspector handle
- **THEN** the navigator is unsubscribed, the viewer stops rendering and
  releases its resources, the host's element is empty, and disposing a
  second time changes nothing

### Requirement: A maker opens and closes the assembly sidebar

The layout SHALL present a labelled control that opens and closes the
sidebar, reports whether the sidebar is currently open, names the region
it controls, and is operable from the keyboard. That control SHALL remain
present and in the same place whether the sidebar is open or collapsed, so
that using it never moves keyboard focus away from it. A collapsed sidebar
SHALL be removed from the layout and from assistive technology, not merely
covered, and the viewer SHALL take the space it leaves without the host
calling anything.

The sidebar SHALL start in the state the mount options ask for, collapsed
unless asked otherwise, and SHALL NOT persist its state across page loads
in browser storage, a cookie or the address bar: a page reloaded shows the
state its own options declare.

#### Scenario: A maker opens the sidebar from the keyboard

- **WHEN** a maker moves keyboard focus to the sidebar control and
  activates it on a collapsed sidebar
- **THEN** the sidebar appears with the assembly tree in it, the control
  reports itself expanded, and keyboard focus is still on the control

#### Scenario: The viewer takes the space back

- **WHEN** a maker collapses an open sidebar
- **THEN** the sidebar is gone from the layout and from assistive
  technology, and the viewer's canvas is wider than it was, framed and
  projected for its new size

#### Scenario: The sidebar remembers nothing

- **WHEN** a maker opens the sidebar and then reloads the page
- **THEN** the sidebar is back in the state the page's own options
  declare, and nothing was written to browser storage or the address bar

#### Scenario: A host opens the sidebar without a maker

- **WHEN** a host calls the handle's own sidebar operation
- **THEN** the sidebar opens or closes exactly as the control does, and
  the control reports the new state

### Requirement: The inspector layout is styled by one stylesheet a host can theme

The layout SHALL be presented by one stylesheet the bundle carries, added
to the document it is mounted into exactly once however many inspectors
are mounted there, and identifiable so a host can find it. The package
SHALL publish no additional file for it.

Every element the layout builds SHALL carry a stable class name under one
documented prefix, distinct from the navigator's, and the metrics and
palette of the default presentation — sidebar width, ground, text, border
and focus ring — SHALL be CSS custom properties a host overrides without
reaching into the layout's elements. The default presentation SHALL be
legible on a light and on a dark page. A host SHALL be able to suppress
the injected stylesheet, which SHALL also be the default for the
navigator's own stylesheet, and present the same class contract from its
own rules.

#### Scenario: Two inspectors inject one stylesheet

- **WHEN** two inspectors are mounted in one document
- **THEN** the document carries exactly one identifiable inspector
  stylesheet, and both are presented by it

#### Scenario: A host themes the layout

- **WHEN** a host overrides the layout's documented custom properties from
  its own stylesheet
- **THEN** the sidebar adopts that width and palette with no change to the
  package and no host code touching its elements

#### Scenario: A page that forbids inline style blocks

- **WHEN** a host mounts an inspector asking for no injected stylesheet
- **THEN** neither the layout's nor the navigator's stylesheet is added to
  the document, and every element still carries its documented class names

### Requirement: The standalone page selects which layout it mounts

The standalone export page SHALL keep mounting from the published
container attribute, and SHALL additionally accept a layout selection —
both as an attribute on the same container and as a query-string option on
the page, the query string taking precedence — choosing between the plain
viewer and the inspector, and an option selecting the sidebar's initial
state by the same two channels.

**A container carrying no layout selection SHALL mount the plain viewer**,
so that every page written before this capability existed, and every
export directory already published, behaves exactly as it did. A layout
selection the page does not recognise SHALL be refused by name in the
container rather than silently mounting anything.

The page the package ships SHALL select the inspector with its sidebar
collapsed. The published container attribute, the page's file name and the
bundle's file name SHALL be unchanged, so a framework copying the page and
the bundle copies the same two files under the same names.

#### Scenario: An export directory published before this capability

- **WHEN** a browser opens an export page whose container carries no
  layout selection
- **THEN** the plain viewer is mounted exactly as it was, with no sidebar
  and no layout elements in the page

#### Scenario: The shipped page opens with the model

- **WHEN** a maker opens the page the package ships
- **THEN** the viewer fills the page with its chrome, the sidebar is
  collapsed, and its control is present to open it

#### Scenario: A link asks for the sidebar

- **WHEN** a page is opened with the query-string option that opens the
  sidebar
- **THEN** the sidebar is open on load, whatever the container's own
  attribute said

#### Scenario: A layout nobody published

- **WHEN** a container asks for a layout the page does not recognise
- **THEN** the container reports the unrecognised value by name and
  mounts nothing
