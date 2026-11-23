# model-app Specification

## Purpose
TBD - created by archiving change show-a-models-own-app. Update Purpose after archive.
## Requirements
### Requirement: A model's own app takes the place of the automatic panel

When a published document names its model's app, and the viewer is mounted
with continuous rendering and with its on-screen chrome presented (the
default), the viewer SHALL show that app in the area the host gave it, in
place of every automatic panel the document would otherwise get (posed,
running or clocked), of its instruction buttons and of its animation bar.
Every page that mounts the viewer — the export page, the development page, a
host's own page such as the Studio's — SHALL show the app with no change of
its own. A mount with the chrome suppressed, and every on-demand mount (a
still taken in the browser, a film's take), SHALL NOT load or show the app
and SHALL fetch nothing of it; the handle SHALL be whole either way. A
document that names no app SHALL be mounted exactly as before this
capability existed: the same panels, the same elements and the same sizing.

The viewer's own bundle SHALL NOT contain React or any other user-interface
framework; an app brings its own.

#### Scenario: An export of a model with an app shows the app

- **WHEN** a reader opens the export page of a model whose document names an
  app
- **THEN** the app is drawn in the viewer's area, the model's picture is
  where the app placed it, and no clocked, running or posed panel and no
  animation bar is drawn

#### Scenario: The development page shows the app

- **WHEN** a maker opens `machinome develop`'s page on the same model
- **THEN** the app is drawn in the viewer's pane beside the inspector's
  sidebar

#### Scenario: A host that builds its own panel gets no app

- **WHEN** a host mounts the same document with the chrome suppressed
- **THEN** neither the app nor any panel is drawn, no file of the app is
  requested, and the machine's handle answers as before

#### Scenario: A still taken in the browser carries no app

- **WHEN** a still of the model is taken by the web viewer
- **THEN** the image shows the model alone

#### Scenario: A model without an app is unchanged

- **WHEN** a document naming no app is mounted
- **THEN** its panels, its canvas's place in the container and its sizing
  are those of the viewer before this capability

### Requirement: An app owns its layout and places the model's picture

An app SHALL fill the area the host gave the viewer and SHALL place the
model's picture — the drawn model and the full-screen control in its corner —
where it chooses. The picture SHALL take the size of the place the app gives
it and follow that place as it grows and shrinks. The parts of the page that
are not the viewer's panels SHALL stay as they are: the inspector's sidebar
and navigator beside the viewer's area, orbiting the picture, touching parts
the document declares touchable, and the full-screen root, so that full
screen shows the whole app with its picture.

#### Scenario: The picture fills the place it is given

- **WHEN** an app places the picture in the upper part of its area above a
  keyboard
- **THEN** the model is drawn at that place's size and redrawn at the new
  size when the window is resized

#### Scenario: Full screen takes the whole app

- **WHEN** the maker activates the full-screen control in the picture's
  corner
- **THEN** the app, its picture and everything around it in the viewer's
  layout go full screen together

### Requirement: An app operates the machine through the mount's handle

An app SHALL be given the mount's handle and nothing else of the viewer. The
viewer SHALL provide a small React helper, imported by an app as
`@machinome/viewer/app`, offering: a component that places the picture; a
hook answering a clocked machine's committed bank and whether a transition is
being drawn, which re-renders the app after every change of either, whoever
made it; a hook that plays a declared instruction as the panel's button does,
its refusal answered as the machine's own error; and a hook answering the
handle. A hook that reads a clocked machine, used on a model that is not a
clocked machine, SHALL refuse naming that.

#### Scenario: The keyboard follows a pressed key

- **WHEN** an app's key plays the instruction `Key Q` on a clocked model
- **THEN** the app re-renders with the committed bank in which the key is
  held and with a transition being drawn, and re-renders again when the
  drawing lands

#### Scenario: A change made elsewhere reaches the app

- **WHEN** a host script moves the machine through the handle while the app
  is shown
- **THEN** the app re-renders with the new bank

#### Scenario: A refused instruction is the app's to report

- **WHEN** an app plays an instruction the machine refuses
- **THEN** the helper's call raises the machine's refusal and the bank is
  unchanged

### Requirement: An app that cannot be shown is refused in its place

When a model's app cannot be shown — the document says why it could not be
built, its script or stylesheet cannot be loaded, its script starts no app
this viewer can start, its start fails, it places no picture, it fails while
drawing, or it reads a clocked machine on a model that is not one — the
viewer SHALL show the model's picture filling the viewer's area and, over
it, a notice reading "This model's app is not shown:" followed by the reason,
SHALL write the same sentence to the browser's console, SHALL NOT present
the automatic panel in the app's place, and SHALL complete the mount. A
document whose app record is malformed SHALL be refused by name, naming the
record.

#### Scenario: A script that does not load

- **WHEN** a document names an app script that the server answers with 404
- **THEN** the model is drawn filling the area, the notice names the script
  and the failure, no panel is drawn, and the mount resolves

#### Scenario: The producer could not build the app

- **WHEN** a document records that its app could not be built, with the
  producer's sentence
- **THEN** the notice carries that sentence and the model is drawn

#### Scenario: An app that places no picture

- **WHEN** an app renders without placing the picture
- **THEN** it is taken away and the notice says it places no picture, with
  the model drawn filling the area

#### Scenario: A malformed record

- **WHEN** a document's `app` record names both a script and a refusal
- **THEN** the mount is refused naming the record

### Requirement: A republished document keeps or replaces the app in place

When a document is republished or reloaded in place, the viewer SHALL keep a
running app whose files are unchanged, which then hears the change like any
subscriber; SHALL replace an app whose files changed by the new one, the
picture standing in the viewer's area between the two; SHALL take an app away
and present the automatic panel when the document no longer names one; and
SHALL take the panel away and show the app when the document now names one.
A replacement that fails SHALL be refused in place as an app that cannot be
shown.

#### Scenario: An edited app replaces the running one

- **WHEN** the maker edits the app and the rebuilt document names its new
  script
- **THEN** the page shows the new app without reloading the page or the
  model's geometry

#### Scenario: The open development page shows the edited app, the picture standing

- **WHEN** the development page is open on a model with an app and is told
  that a document naming the app's new files was published
- **THEN** the page shows the new app without being loaded again, the
  model's picture stays drawn on the same canvas, and no part's geometry is
  fetched again

#### Scenario: An unrelated rebuild keeps the app

- **WHEN** the model is rebuilt and its document names the same app files
- **THEN** the running app is kept with its own state

### Requirement: Disposing the viewer disposes its app

Disposing a viewer SHALL leave full screen first, then take the app away
while the handle still answers it, removing its stylesheet and every element
it added, and SHALL start no app whose script was still loading.

#### Scenario: A host unmounts a viewer showing an app

- **WHEN** a host disposes the viewer while its app is shown
- **THEN** the app's own clean-up runs, the container is empty, and the
  app's stylesheet is no longer in the page

### Requirement: The viewer bundles a model's app with its own toolchain

The web viewer SHALL offer the seam's operation that bundles a model's app.
Given the app's entry file, the project's root and an output directory, it
SHALL bundle the app's own TypeScript, JavaScript and CSS files with the
viewer's own build tool, its own copy of React and React DOM, and the
helper, into one script and at most one stylesheet in the output directory,
each named by its content, and SHALL answer their names and the project files
the bundle read. A project SHALL need no package manifest of its own. The
same sources SHALL bundle to the same bytes wherever the project lies on
disk. The script SHALL carry React's MIT notice and the helper's licence and
source. The operation SHALL refuse, by name and writing nothing: an import
of anything but the app's own files, React, React DOM and the helper; a file
read from outside the project's root; source that does not build, with its
file and line; a viewer installed without the toolchain; a checkout whose
JavaScript dependencies are not installed, naming the command that installs
them; and a machine with no Node.js. It SHALL NEVER install a dependency.

#### Scenario: An app with a stylesheet is bundled

- **WHEN** the viewer bundles an app whose entry imports a component and a
  stylesheet
- **THEN** it writes one script and one stylesheet named by their content,
  the script opening with React's MIT notice, and answers their names and
  the app's files it read

#### Scenario: An import the viewer does not provide

- **WHEN** an app imports `three`
- **THEN** the bundling is refused naming the import and what an app may
  import, and nothing is written

#### Scenario: Two copies bundle alike

- **WHEN** the same app is bundled from two copies of a project in
  different directories
- **THEN** the scripts are byte-identical and have the same name

### Requirement: The app capability has an explicit reader capability

The viewer SHALL advertise viewer API 31 or a later one for reading a
document's app record, showing a model's app and notifying a page of a clocked
machine's changes, and SHALL keep reading document versions 1 to 14. The app
record SHALL be additive within those versions: it SHALL NOT change the
document versions read, and a viewer before this capability, which ignores
it, shows the automatic panel.

#### Scenario: A host requires the capability

- **WHEN** a host reads the mount handle's API version
- **THEN** it is 31 or later, and the document versions reported are 1 to 14

