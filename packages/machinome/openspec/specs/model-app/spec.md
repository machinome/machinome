# model-app Specification

## Purpose
TBD - created by archiving change declare-a-models-app. Update Purpose after archive.
## Requirements
### Requirement: A model's root declares its app

A node class SHALL be able to declare its model's app as `app = '<path>'` in
its body: a TypeScript or JavaScript file (`.tsx`, `.ts`, `.jsx` or `.js`),
named relative to the file that declares the class. `app` SHALL be a reserved
class-body name on a node class: a value that is not a non-empty relative
path to such a file SHALL be refused where the class is written, naming the
class, the attribute and the form. A class SHALL inherit its base's app,
which stays relative to the file of the class that declared it. Only the
declaration of the root a document is published for SHALL be read; a child
whose class declares an app SHALL contribute nothing.

#### Scenario: An app beside the model

- **WHEN** `simulation/machine.py` declares `class Enigma(AssemblyNode)` with
  `app = 'app/index.tsx'`
- **THEN** the model's app is `simulation/app/index.tsx`

#### Scenario: A value that is not an app

- **WHEN** a node class declares `app = 'panel.py'`
- **THEN** the class is refused as it is written, naming the class, `app` and
  the files an app may be

#### Scenario: An app declared on a child

- **WHEN** a child of the published root declares an app and the root does
  not
- **THEN** the document carries no app

### Requirement: A build publishes the model's app beside its document

When the root of a build declares an app, the build SHALL ask the viewer that
bundles, chosen as every viewer operation is chosen, to bundle it into the
build directory beside `viewer.json`, and the document SHALL name the bundled
script and, when the app has one, its stylesheet, in a top-level `app`
record. The files SHALL be named by their content, so an unchanged app SHALL
NOT republish the document. A file of an earlier app that the document no
longer names SHALL be removed with the build's other unreferenced files, and
the files it names SHALL be kept. The record SHALL be additive and SHALL NOT
change the document's version. A build whose root declares no app SHALL ask
no viewer for one and SHALL publish a document byte-identical to the one it
published before this capability. A still taken in the browser SHALL carry
no app.

#### Scenario: A model with an app is built

- **WHEN** `machinome build` completes a model whose root declares an app
- **THEN** `viewer.json` carries an `app` record naming a script and a
  stylesheet that are files beside it in the build directory

#### Scenario: An unchanged model is not republished for its app

- **WHEN** the same model is built twice with nothing changed
- **THEN** the second build finds the document equal to the published one
  and does not republish it or rewrite the app's files

#### Scenario: An edited app replaces the old one

- **WHEN** a file of the app is edited and the model is built again
- **THEN** the document names a new script and the previous script is no
  longer in the build directory

#### Scenario: A model without an app is unchanged

- **WHEN** a model whose root declares no app is built
- **THEN** no viewer is asked to bundle anything and the document is
  byte-identical to the one published before this capability

### Requirement: An app that cannot be bundled is named, not substituted

When a declared app cannot be bundled — its file does not exist, its file is
outside the project, the viewer that bundles is not installed or does not
bundle, or that viewer refuses the app's sources or cannot bundle in this
installation — the build SHALL publish the document as for any model, with
an `app` record carrying the sentence that says why, naming the root's class
and the declared path; SHALL log that sentence once as an error; SHALL NOT
record it as the build's failure; and its exit status SHALL reflect whether
the model built. No other app, and not the viewer's automatic panel, SHALL
be named in its place.

#### Scenario: A declared file that does not exist

- **WHEN** `machinome build` completes a model whose root declares
  `app = 'app/index.tsx'` and no such file exists
- **THEN** the document is published with an `app` record whose refusal
  names the class and the absolute path, one error is logged, no build error
  is recorded, and the command exits 0

#### Scenario: A file outside the project

- **WHEN** a root's app resolves to a file outside the project's root
- **THEN** the record's refusal names the file and the project's root, and
  no viewer is asked to bundle it

#### Scenario: No viewer to bundle with

- **WHEN** a model with an app is built in an installation without the web
  viewer
- **THEN** the record's refusal names the viewer and the line that installs
  its extra, and the model's parts and document are published

### Requirement: Developing a model follows its app

`machinome develop` SHALL watch the files the app's bundle read beside the
model's own sources, and, where the app was refused before its files were
known, the directory of its declared file. An edit to one of them, and to
none of the model's own sources, SHALL be republished by the builder that
already holds the loaded model: the app bundled again, the document
published with the new record and the previous app's files removed, without
loading the model again and without re-rendering any part; the builder SHALL
then go on watching. Where the published document was replaced by another
producer since that builder published it, or the builder has published
nothing, the edit SHALL rebuild as a source edit does, and the build SHALL
say so. Every open development page SHALL then show the edited app in place,
the model's picture standing, without a page load.

#### Scenario: An edit to the app republishes it in place

- **WHEN** a maker edits a component of the app while `machinome develop` is
  serving the model
- **THEN** the document is republished naming the new script by the builder
  that was watching, the model is not loaded again, and no part is
  re-rendered

#### Scenario: The open development page shows the edited app, the picture standing

- **WHEN** a maker edits the text a component of the app draws while the
  development page is open
- **THEN** the page shows the new text without being loaded again, the
  model's picture stays drawn in the same place, and no part's geometry is
  fetched again

#### Scenario: A repaired app is seen

- **WHEN** an app that did not build is repaired while `machinome develop`
  runs
- **THEN** the next document names the bundled script in place of the
  refusal, published by the same builder

#### Scenario: Another producer published meanwhile

- **WHEN** `machinome build` publishes the same model while a `develop`
  builder watches it, and the maker then edits the app
- **THEN** the edit rebuilds the model as a source edit does, and the build
  says why

### Requirement: An export carries its model's app

`machinome export` of a model whose root declares an app SHALL bundle it with
the viewer that embeds and SHALL write the bundled files beside
`manifest.json`, naming them in the manifest's `app` record, so the export
stays self-contained. When the app cannot be bundled the export SHALL fail
before it creates or modifies the output directory, naming why. An export
without the widget of a model whose root declares an app SHALL be refused
before anything is built, naming the class and the declared path.

#### Scenario: An export with its app

- **WHEN** a model with an app is exported with its widget
- **THEN** the export directory holds the app's script and stylesheet beside
  `manifest.json`, the manifest names them, and the export's page shows the
  app with no machinome process running

#### Scenario: An app that does not build fails the export

- **WHEN** a model whose app does not build is exported
- **THEN** the command exits 1 with the viewer's sentence and no output
  directory is created

#### Scenario: A widget-less export of a model with an app

- **WHEN** a user runs `machinome export --no-widget` on a model whose root
  declares an app
- **THEN** the command exits 1 naming the class and the app, and writes
  nothing

