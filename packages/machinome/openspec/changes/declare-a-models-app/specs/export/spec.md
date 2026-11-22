## MODIFIED Requirements

### Requirement: Export artifact contents

The system SHALL export a node by building all STLs and writing an output
directory containing `manifest.json`, a `models/` directory, and — unless
widget-less export is requested — `index.html` plus the prebuilt
`machinome-viewer.js` bundle, both copied from the installed viewer package. If
the viewer package is not installed, export SHALL fail with
`WidgetBundleMissing` naming `pip install "machinome[viewer]"` and
`--no-widget` as the alternatives.

The `models/` directory SHALL also hold a copy of every **marking** artifact
the manifest names under the `markings` capability, preserving that artifact's
path relative to the selected build directory exactly as a model's is, so the
export stays self-contained: a consumer reading the manifest from a static host
resolves every marking without a machinome process and without any path
outside the export directory. A marking artifact outside its resolved build
directory SHALL fail export before the requested output is created or
modified, as a model artifact outside it already does.

When the exported root declares an app under the `model-app` capability, the
output directory SHALL also hold the app's bundled script and, when it has
one, its stylesheet, beside `manifest.json`, named in the manifest's `app`
record; an app that cannot be bundled SHALL fail export before the requested
output is created or modified, and a widget-less export of such a root SHALL
be refused before anything is built.

#### Scenario: Widget-less export

- **WHEN** export runs with `widget=False` (`--no-widget`)
- **THEN** only `manifest.json` and `models/` are written, whether or not the
  viewer is installed

#### Scenario: Export without the viewer

- **WHEN** export runs with the widget requested in an installation without
  `machinome-viewer`
- **THEN** it fails naming the extra and `--no-widget`, and writes no output
  directory

#### Scenario: An export carries the markings it names

- **WHEN** a node whose parts declare markings is exported
- **THEN** every marking reference in `manifest.json` resolves to a copied
  artifact beneath the export's `models/` directory, with no parent traversal

#### Scenario: An export carries the app it names

- **WHEN** a node whose root declares an app is exported with its widget
- **THEN** the manifest's `app` record names a script and a stylesheet that
  are files beside `manifest.json` in the export directory

#### Scenario: An app that cannot be bundled fails the export

- **WHEN** a node whose app's file does not exist is exported
- **THEN** the export fails naming the class and the file, and writes no
  output directory

#### Scenario: A widget-less export of a model with an app is refused

- **WHEN** export runs with `widget=False` on a node whose root declares an
  app
- **THEN** it fails naming the class and the app before any part is built,
  and writes no output directory
