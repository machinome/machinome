## MODIFIED Requirements

### Requirement: Export artifact contents

The system SHALL export a node by building all STLs and writing an output
directory containing `manifest.json`, a `models/` directory, and — unless
widget-less export is requested — `index.html` plus the prebuilt
`solid-widget.js` bundle, both copied from the installed viewer package. If
the viewer package is not installed, export SHALL fail with
`WidgetBundleMissing` naming `pip install "solid-node[viewer]"` and
`--no-widget` as the alternatives.

The `models/` directory SHALL also hold a copy of every **marking** artifact
the manifest names under the `markings` capability, preserving that artifact's
path relative to the selected build directory exactly as a model's is, so the
export stays self-contained: a consumer reading the manifest from a static host
resolves every marking without a solid-node process and without any path
outside the export directory. A marking artifact outside its resolved build
directory SHALL fail export before the requested output is created or
modified, as a model artifact outside it already does.

#### Scenario: Widget-less export

- **WHEN** export runs with `widget=False` (`--no-widget`)
- **THEN** only `manifest.json` and `models/` are written, whether or not the
  viewer is installed

#### Scenario: Export without the viewer

- **WHEN** export runs with the widget requested in an installation without
  `solid-node-viewer`
- **THEN** it fails naming the extra and `--no-widget`, and writes no output
  directory

#### Scenario: An export carries the markings it names

- **WHEN** a node whose parts declare markings is exported
- **THEN** every marking reference in `manifest.json` resolves to a copied
  artifact beneath the export's `models/` directory, with no parent traversal

### Requirement: Manifest contract

The manifest SHALL retain the document name `manifest.json` and SHALL declare
`format: "solid-node-export"`, `animation: {fps, frames}`, a
`drivers` table, an `instructions` table, and a
`root` tree with the same observable schema and child-name behavior as the
normal-build `viewer.json`. When the exported root declares a time base the
`animation` object SHALL also carry numeric `loop`, the declared seconds of
machine time one turn of `$t` covers, and SHALL omit the key otherwise; the
browser-snapshot document SHALL publish `loop` under the same rule. `loop` is
additive within the current schema version — a consumer that does not read
it plays `frames / fps` as before — and `--fps` / `--frames` keep their
meaning as the timeline's playback resolution. A rigid node SHALL emit one
`model` reference and
stop recursion; a non-rigid node whose render result is a list or tuple SHALL
recurse into its children; a flexible leaf SHALL emit one `flexible` object
and stop recursion. Each node SHALL carry `name`, `type`, `color`,
`mtime`, and its operations as unevaluated expressions so `$t`
animation is preserved rather than baked to the constants of one instant. A
rigid model reference SHALL be derived relative to the selected build directory
that owns the artifact, SHALL remain rooted beneath the export's `models/`
directory with no parent traversal, and SHALL resolve to a copied artifact so
the export remains portable and self-contained regardless of the caller's
working directory. An artifact outside that build directory SHALL make export
fail before it creates or modifies the requested output. Changes to the shared
tree shape or operation serialization are breaking and MUST bump `version` and
update every producer and consumer of the shared schema together.

When the serialized document contains a subexpression occurring more than
once, the manifest SHALL carry a non-empty `bindings` table beside `drivers`
and `instructions`, under the shared-subexpression requirement above, and SHALL
declare `version: 4`. When it contains no such subexpression the `bindings` key
SHALL be absent and the document SHALL declare `version: 3` when the serialized
tree contains at least one flexible leaf and `version: 2` otherwise — so a
document with nothing to bind is byte-identical to the one published before
bindings existed, and an old consumer refuses only what it genuinely cannot
render.

The bump to `version: 4` SHALL NOT be treated as additive. A consumer ignoring
`bindings` would resolve a binding name to nothing and place the machine in a
wrong pose, so a consumer that cannot resolve the table SHALL refuse the
document rather than render it. Consumers SHALL accept versions 2, 3 and 4.

When the serialized root declares `time = Time.running()` the document SHALL
declare `version: 5` and SHALL carry the `program` object defined by the
requirement "A running root's document publishes the compiled program",
whatever its tree content — the version ladder below 5 is derived from the
CONTENT because flexible leaves and shared subexpressions are properties of
the tree, while a compiled program is a property of the ROOT'S DECLARATION,
and a running root with a trivial program is still a machine a version 4
consumer would animate wrongly. A root declaring no time base or a looping
one SHALL NEVER declare `version: 5`, SHALL NOT carry a `program` key, and
SHALL be byte-identical to the document published before the program existed.

The bump to `version: 5` SHALL NOT be treated as additive. A consumer
ignoring `program` would read a document whose joint placements are bare
coordinate names it can bind nothing to, so a consumer that cannot read
version 5 SHALL refuse the document by name rather than render it or animate
it as a loop.

The `instructions` table SHALL publish, under `version: 5`, EVERY declared
instruction, each entry carrying exactly one of `targets` (where the drivers
land) and `by` (how far they travel from where they stand), both keyed by
qualified driver id and both in design units, beside `duration` in seconds.
Under versions 2, 3 and 4 an instruction stating `by` SHALL continue to be
OMITTED from the table, because a consumer of those versions reads `targets`
off every entry.

A rigid node that declares markings under the `markings` capability SHALL
additionally carry a `markings` list, one entry per declared marking in
declaration order, each entry carrying the marking's `name`, a `model`
reference to its artifact under the same rules and the same portability
guarantee as the node's own `model`, its `color` in `#RRGGBB` form, and its own
`mtime` — the marking artifact's, not the node's, so a consumer that reloads on
change sees a redrawn decal without the part appearing to change. The key SHALL
be ABSENT on a node that declares no marking.

A marking entry SHALL NOT publish its placement: the artifact already holds the
artwork's surface in the part's own frame, so a consumer applies the part's
operations to it exactly as it applies them to the part's model, and no
consumer reproduces the placement arithmetic. A marking SHALL NOT carry a
`piece`, and SHALL NOT appear in the piece inventory.

The `markings` list SHALL be treated as ADDITIVE and SHALL NOT bump `version`.
A consumer that ignores it renders exactly the picture it renders today,
because a marking adds no solid, enters no operation, no binding and no
program, and describes nothing the existing fields describe differently — which
is the `piece` precedent, and the standing rule that a producer emits the
lowest version its content needs. A document whose tree declares no marking
SHALL therefore be byte-identical to the document published before markings
existed.

#### Scenario: A running root's document declares version 5

- **WHEN** a root declaring `time = Time.running()` is exported
- **THEN** `manifest.json` declares `version: 5` and carries a `program`
  object beside `drivers`, `instructions` and `bindings`

#### Scenario: An untimed document is unchanged in every byte

- **WHEN** a root declaring no time base, and one declaring
  `time = Time(loop=2.0)`, are exported
- **THEN** neither document carries a `program` key, each declares the
  version its content already needed, and each is byte-identical to the
  document exported before this change

#### Scenario: Both instruction forms are published under version 5

- **WHEN** a running root declares `Instruction(by={'crank': 10.0},
  duration=0.5)` beside `Instruction({'crank': 40.0}, duration=0.5)`
- **THEN** the version 5 document's `instructions` table has an entry for
  each, the first carrying `by` and no `targets`, the second carrying
  `targets` and no `by`, both keyed by qualified driver id

#### Scenario: A relative instruction stays out of a version 4 table

- **WHEN** an untimed root declares only relative instructions
- **THEN** its document's `instructions` table is empty and the rest of the
  document is unchanged

#### Scenario: A declared time base is exported

- **WHEN** a root declaring `time = Time(loop=43200)` is exported
- **THEN** `manifest.json` carries `animation.loop == 43200` beside the
  requested `fps` and `frames`, its version is unchanged by the key, and its
  operations carry `$t` multiplied by the loop rather than a constant

#### Scenario: An undeclared root exports no loop

- **WHEN** a root declaring no time base is exported
- **THEN** `manifest.json`'s `animation` object has no `loop` key and is
  byte-identical to the manifest exported before this change

#### Scenario: A document with nothing shared is unchanged

- **WHEN** a tree whose expressions repeat no subexpression is exported
- **THEN** `manifest.json` has no `bindings` key, declares the version its
  content already needed, and is byte-identical to the manifest exported
  before bindings existed

#### Scenario: A document with sharing declares the new version

- **WHEN** a tree whose expressions repeat a subexpression is exported
- **THEN** `manifest.json` declares `version: 4` and carries a non-empty
  `bindings` array

#### Scenario: A flexible document with sharing declares the new version

- **WHEN** a tree holding a flexible leaf and repeating a subexpression is
  exported
- **THEN** `manifest.json` declares `version: 4` rather than `3`, and its
  flexible leaf's `params` may reference the table

#### Scenario: Export starts in a project subdirectory

- **WHEN** a project model is exported from a working directory below its
  project root to an output directory elsewhere
- **THEN** every model reference contains no parent traversal and resolves to
  its copied artifact beneath the output's `models/` directory

#### Scenario: Export uses a configured or selected build directory

- **WHEN** export uses a relative configured build root or a named model's
  selected build directory
- **THEN** model references preserve artifact paths relative to that resolved
  directory and resolve beneath the export's `models/` directory

#### Scenario: A model artifact is outside its build directory

- **WHEN** a rigid node names an STL whose canonical path is outside its
  resolved build directory
- **THEN** direct export raises `ExportModelPathError`, CLI export exits
  nonzero with that diagnostic, and the requested output is not created or
  modified


#### Scenario: A part publishes the markings it carries

- **WHEN** a rigid node declaring `digits` and then `arrows` is exported
- **THEN** its entry carries a `markings` list of two entries in that order,
  each with `name`, `model`, `color` and `mtime`, and neither carries a
  placement or a `piece`

#### Scenario: A document with no marking is unchanged in every byte

- **WHEN** a tree whose parts declare no marking is exported
- **THEN** no node's entry has a `markings` key, the document declares the
  version its content already needed, and it is byte-identical to the
  manifest exported before markings existed

#### Scenario: A marking's mtime is its own

- **WHEN** a marking's artwork is edited and the project is exported again
- **THEN** that marking entry's `mtime` has moved and the node's own `mtime`
  and `model` have not

#### Scenario: The picture is unchanged for a consumer that ignores markings

- **WHEN** a consumer written against the previous document reads a document
  whose parts carry markings
- **THEN** it finds the same `format`, `version`, `animation` and `root` tree,
  with every previously published node field unchanged

#### Scenario: The OpenSCAD renderer does not draw markings

- **WHEN** a model whose parts declare markings is photographed with the
  OpenSCAD snapshot renderer, or opened by `solid develop` without the viewer
  extra
- **THEN** it renders exactly as the same model without the markings, and
  neither the build nor the render fails
