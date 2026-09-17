# Static Export Specification

## Purpose

The static export channel: `export_node` producing a self-contained,
offline, embeddable artifact (manifest + STL models + optional React-free
widget viewer). Encodes ADR-020 (static export and embeddable viewer
widget); the manifest is a versioned public contract shared by the exporter,
the widget, and the Sphinx extension.

Code: `solid_node/core/export.py`, `solid_node/manager/export.py`; the
widget files come from the installed solid-node-viewer package through
`solid_node/viewers/bundle.py`.
## Requirements
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

A published marking artifact's triangles SHALL wind so that each triangle's
normal points **away from the part**: radially outward from the wrap axis for a
`Wrapped` placement, and along the declared `normal` for a `Flat` one. The
promise SHALL hold whatever orientation the drawing tool gave the regions the
artwork was read from. A consumer MAY therefore treat a decal's own vertex and
face normals as the outward direction — to lift it clear of the surface it lies
on, to offset it, or to light it — without inspecting the part the decal
belongs to, and SHALL NOT be required to infer a side from the part's geometry.
This is a promise about the ARTIFACT, not an offset: the surface still sits on
the nominal cylinder or plane with no separation of its own.

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

#### Scenario: A consumer reads a decal's outward side off the decal

- **WHEN** a document publishing a wrapped marking and a flat marking is read
  and each marking artifact's face normals are computed
- **THEN** every wrapped face normal points away from its wrap axis and every
  flat face normal points along the placement's declared normal, so displacing
  each vertex along its own normal moves the decal clear of the part and never
  into it

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

### Requirement: Model deduplication

The system SHALL copy one STL per distinct rigid artifact into `models/`,
keyed by the STL path relative to the build dir — identical instances share
one file, and same-named scripts in different directories do not collide.

#### Scenario: Repeated part

- **WHEN** an assembly instantiates the same parameterized part four times
- **THEN** `models/` contains that part's STL once and all four tree nodes
  reference it

### Requirement: Embeddable widget behavior

The export channel SHALL ship the installed viewer's bundle as an auto-mounting
bundle, so an export directory renders on any static host with no solid-node
process running. It SHALL keep its published names — the bundle
`solid-widget.js`, the auto-mount attribute
`data-solid-widget="<manifest url>"`, and the browser global
`SolidNodeWidget` — and SHALL auto-mount every element carrying that attribute
once the page is ready, presenting animation as an always-visible inline bar.
The page query string SHALL set the initial state: `?t=<0..1>` for time,
`?autoplay=0` to start paused. How the model itself is rendered — tree
composition, camera, colour, and animation semantics — is the
`viewer-package` capability of solid-node-viewer, which the export channel
embeds rather than reimplements.

#### Scenario: Static pose embed

- **WHEN** the export's `index.html` is loaded with `?t=0.25&autoplay=0`
- **THEN** the model renders paused at `$t = 0.25`

#### Scenario: Serving requires no backend

- **WHEN** the export directory is served by any static file host or opened
  through an iframe
- **THEN** the widget renders and animates with no solid-node process running

#### Scenario: An existing host page keeps working

- **WHEN** a hand-written page embeds an export by the documented bundle
  filename, auto-mount attribute, and browser global
- **THEN** it mounts and renders as before

### Requirement: Export manifests carry the piece inventory

The exported `manifest.json` SHALL include the printed-piece inventory defined
by the `printed-pieces` capability, with each piece's `models` references rooted
beneath the export's `models/` directory so they resolve to the copied artifacts
inside the export. The export SHALL therefore remain self-contained: a consumer
reading the inventory from a static host resolves every piece without a
solid-node process and without any path outside the export directory.

Model deduplication is unchanged — one copied STL per distinct rigid artifact —
and the inventory SHALL be reported on top of it, so several deduplicated
artifacts with identical content still resolve to a single piece.

#### Scenario: An export publishes its pieces

- **WHEN** a node is exported
- **THEN** `manifest.json` contains a `pieces` list beside `root`, every rigid
  node carries a `piece` id present in that list, and every model the inventory
  names is a copied artifact beneath `models/`

#### Scenario: Distinct artifacts with identical content are one piece

- **WHEN** an export copies two distinct rigid artifacts whose STL content is
  identical
- **THEN** `models/` still contains both copied files and the inventory reports
  one piece whose `models` names both, with a count covering every instance of
  either

### Requirement: A shared subexpression is published once

A published document — the export `manifest.json` and the normal-build
`viewer.json` alike — SHALL publish each subexpression that occurs more than
once among its expressions exactly once, as a named entry in an ordered
`bindings` table, and SHALL reference that entry by name everywhere the
subexpression occurred.

The expressions this covers are every operation's expression strings and every
flexible leaf's `params` values. A subexpression that is a single number or a
single name — a literal or a driver id — SHALL NOT be bound: it is shorter
written out than referenced.

`bindings` SHALL be a JSON array of objects, each carrying a `name` and an
`expression`, and SHALL be ordered so that an entry's expression names only
`$t`, qualified driver ids declared in the document's `drivers` table, and
entries appearing **earlier** in the array. A consumer SHALL therefore be able
to evaluate the table in one forward pass, into the same scope in which it
resolves `$t` and driver values, before evaluating any operation or `params`
expression.

An entry SHALL NOT carry the inputs its expression depends on. The ordering
guarantee is what lets a consumer derive them: an entry's inputs are the names
it mentions together with the inputs of the entries it names.

A reference SHALL be the binding's name written where an expression would
otherwise be, with nothing marking it as a reference. It is an ordinary name
in the expression language and SHALL be resolved as `$t` and a driver id are
resolved.

The table SHALL be ordered deterministically for a given tree, so that
republishing an unchanged model produces a byte-identical document.

An expression the producer cannot read SHALL be published **verbatim and
unshared**, and SHALL NOT prevent the document from being written. Sharing is
an improvement to a document that already published and already rendered, so an
expression the framework fails to understand SHALL cost only that expression's
share of the improvement. The producer SHALL warn once per such expression,
naming the offending text and identifying the expression — truncated, because a
published expression may be megabytes — and the rest of the document SHALL be
bound as usual.

The producer SHALL refuse to write a document only when the table it would
publish would be wrong: an entry naming a later entry, a name colliding with a
declared driver id, or a rewritten expression that does not reproduce what the
producer built. Those are defects in the framework, not in the model, and SHALL
be reported as such.

#### Scenario: A subexpression reused across operations is published once

- **WHEN** a document is published in which one subexpression appears in the
  operations of several nodes
- **THEN** its text appears once, as one `bindings` entry, and each of those
  operations carries that entry's name in place of the subexpression

#### Scenario: No expression text is repeated

- **WHEN** a document carrying repeated subexpressions, every one of them
  readable by the producer, is published
- **THEN** no operator application, call, or parenthesised group appears twice
  anywhere in the document's expressions and bindings taken together

#### Scenario: An expression the producer cannot read is still published

- **WHEN** a tree carries an expression the producer cannot read, beside
  expressions it can
- **THEN** the document is written, that expression appears verbatim and
  unshared, every readable expression is bound as usual, and a warning names
  the offending text and identifies the expression without printing all of it

#### Scenario: An unreadable expression does not silence the rest

- **WHEN** a tree carries one unreadable expression and a subexpression shared
  between two readable ones
- **THEN** the shared subexpression is still published once as a binding, and
  the document declares the version that table needs

#### Scenario: A bare number or name is not bound

- **WHEN** a document is published in which a literal and a driver id each
  occur many times
- **THEN** neither becomes a `bindings` entry, and both stay written out where
  they occur

#### Scenario: The table is ordered so one forward pass suffices

- **WHEN** a document carrying bindings is published
- **THEN** every name each entry's expression mentions is either `$t`, a
  qualified id present in the `drivers` table, a name defined by the
  expression language's own functions, or the name of an entry appearing
  earlier in the array

#### Scenario: Republishing an unchanged model changes nothing

- **WHEN** an unchanged model is published twice
- **THEN** the two documents are byte-identical, bindings and their order
  included

#### Scenario: The published document evaluates to what the flat one did

- **WHEN** a document carrying bindings is published, and each binding is
  substituted back into the expressions that reference it
- **THEN** the reconstructed expressions evaluate, at every value of `$t` and
  of every driver, to what the expressions the producer built evaluate to

### Requirement: Binding names cannot collide with anything the consumer resolves

Binding names SHALL be `_b0`, `_b1`, … in table order, so that a name is short
and cannot collide with `$t` or with any function the expression language
defines.

Where a qualified driver id in the same document would collide with a name the
table is about to use, the producer SHALL lengthen the prefix by a leading
underscore and re-derive the names, repeating until no collision remains. A
model SHALL NOT be refused because of the names its drivers were given, and a
driver id SHALL NOT be altered to make room.

#### Scenario: Ordinary names

- **WHEN** a document with bindings is published from a tree declaring no
  driver whose id begins with an underscore
- **THEN** its bindings are named `_b0`, `_b1`, … in table order

#### Scenario: A driver named like a binding

- **WHEN** a tree declares a driver whose qualified id is `_b0` and its
  document carries bindings
- **THEN** the document is published, the driver keeps the id `_b0` in its
  expressions and in the `drivers` table, and the bindings are named under a
  longer prefix that collides with nothing

### Requirement: What a binding name means to a consumer

The table is resolved before the document's other names, and dependence flows
through it. A consumer SHALL read a published document by these rules.

**Bindings resolve first.** A name appearing in an operation's expression, in a
flexible leaf's `params`, or in another binding SHALL be resolved as a binding
before it is treated as a driver id. A binding name SHALL NOT be reported as an
undeclared driver: a consumer that refuses a document naming an id absent from
the `drivers` table SHALL make that check after the table's names are known.

**Dependence flows through a binding.** Where a consumer bounds re-evaluation by
the inputs an expression depends on — `$t`, a driver id, or both — an expression
naming a binding SHALL be treated as depending on every input that binding
transitively depends on. An operation whose whole expression is a binding name
that resolves through the table to `$t` is a time-dependent operation and SHALL
be re-evaluated when time changes, exactly as it was when its expression was
written out in full.

**Every other name is unchanged.** A name that is neither `$t`, nor a binding,
nor a declared driver id means what it means today: a function of the
expression language where the language defines one, and otherwise the same
unresolved name it was before bindings existed. This change introduces no new
name kind and no new resolution failure.

#### Scenario: An operation that is only a binding name still follows time

- **WHEN** an operation's expression is a binding name, and that binding
  resolves through the table to an expression over `$t`
- **THEN** a consumer bounding re-evaluation by inputs re-evaluates that
  operation when time changes, as it did when the expression was written out

#### Scenario: A driver reached through a binding is a dependence of the operation

- **WHEN** a binding's expression names a declared driver id, and an operation
  names that binding
- **THEN** the operation depends on that driver, and changing the driver's
  value re-evaluates the operation

#### Scenario: A binding name is not an undeclared driver

- **WHEN** a document declaring an empty `drivers` table carries bindings, and
  its operations name them
- **THEN** a consumer that refuses documents naming undeclared driver ids
  accepts it, because every name its expressions carry is `$t`, a binding, or
  a function of the expression language

### Requirement: Publication preserves sharing from motion construction

The ordinary build and export producers SHALL preserve shared framework motion
values through final publication without first rendering their fully expanded
strings. Operations and flexible parameters SHALL participate together in the
existing shared-subexpression binding contract. Publication SHALL retain the
document's current format, version ladder, expression vocabulary, deterministic
ordering, name-collision handling and legacy unreadable-text fallback.

SCAD-local sharing syntax and internal graph identifiers SHALL NOT occur as new
syntax in generated viewer expressions. A compact standalone scalar recognized
by the framework SHALL be lowered into the existing document language, rather
than forwarded as unreadable legacy text. Publishing SHALL preserve live
values and restore driver bindings according to the existing symbolic mode.

#### Scenario: A shared law reaches rigid and flexible outputs

- **WHEN** a framework motion value is reused in rigid operations and flexible
  parameters in a build or export
- **THEN** their document shares repeated compounds through its ordered
  bindings and no producer step constructs the fully expanded formulas

#### Scenario: Existing viewer consumes the result

- **WHEN** the new producer publishes a shared machine to a schema-4-capable
  viewer
- **THEN** the viewer evaluates its operations and flexible parameters with
  the existing expression language and controls, without a format upgrade

#### Scenario: Deterministic publication

- **WHEN** the same machine is published repeatedly with unchanged content
- **THEN** bindings and expression text are identical regardless of prior
  unrelated publications in the same process

#### Scenario: Nothing requires sharing

- **WHEN** a document contains no repeated compound expression
- **THEN** it omits bindings and retains the existing version and expression
  spelling appropriate to its content

#### Scenario: Legacy text sits beside native motion

- **WHEN** a document combines native shared motion and unreadable legacy text
- **THEN** native motion receives sharing, the legacy text remains verbatim with
  a truncated warning, and the existing table validity checks still apply

#### Scenario: A framework compact scalar returns through custom serialization

- **WHEN** a custom operation supplies the framework's compact standalone scalar
  text to a node-tree document producer
- **THEN** the scalar publishes through the existing expression language and
  bindings instead of introducing SCAD-local syntax into the document

### Requirement: A running root's document publishes the compiled program

A document declaring `version: 5` OR ABOVE SHALL carry a top-level
`program` object,
beside `drivers`, `instructions` and `bindings` and ahead of `root`, holding
what COMPILE TIME decided about the machine and nothing the tick computes.

Every expression it carries SHALL be written in the document's existing
expression language and SHALL participate in the same ordered `bindings`
table the tree's expressions use, so no subexpression is published twice and
no producer-local sharing syntax appears anywhere in the document. The
object SHALL be ordered deterministically for a given tree, so republishing
an unchanged model produces a byte-identical document.

The producer SHALL declare `version: 7` for a program carrying a BLOCK —
a set of two or more edges whose dependencies are cyclic, ordered per
piece under the simulation requirement "A selection decides which sources
a law reads" — `version: 6` for a program with no block at least one of
whose LAW edges names one of its own `gives` among its `needs` — a law
that reads the coordinate it drives — and `version: 5` for a program with
neither, whose document SHALL be byte-identical to the one it published
before this rule existed. The shape of the document SHALL NOT otherwise change: the self-read
is `needs ∩ gives`, no key is added for it, and the free names of a law
edge's expressions SHALL still be exactly the ids in `needs`. NO KEY is
added for a block either: a consumer SHALL re-derive it as the strongly
connected components of the graph over the edges' own `needs` and
`gives`, with `needs ∩ gives` excluded, and SHALL re-derive its SELECTORS
as the jump nodes of its members' published plans whose `level` —
placeholders resolved transitively into their own jumps' levels — names
no id the block gives.

Each version says what a lower consumer would get wrong. **Version 6**
carries a law edge that reads the coordinate it drives: a runtime that
evaluated such an edge as the difference of its two endpoint evaluations
would read the self-read at BOTH ends, freeze the branch it selects and
move the part by a different mechanism without saying so. **Version 7**
carries a block: the published ORDER of its members is a listing, not an
execution order, so a runtime that executes them in it moves the machine
by whatever that order happens to give — silently, and by a different
amount for each order it might have chosen.

Where a self-read edge's driven coordinate ends a tick at a crossing,
what it is COMMITTED at is behaviour rather than a document key: a
runtime that commits it a single float short of the far side re-engages
the gate and diverges from the corpus's bank on a LATER tick, far outside
the agreement window, which is where that rule is pinned.

`program` SHALL carry:

- `identity`: the compiled program's identity — a digest over the root
  class, the bank's ids, the inputs' declarations, the spans and every
  edge's ends, direction and expression — so a state taken against one
  program is refused against another.
- `clock`: the free name elapsed simulation seconds bind to, under the
  requirement "A running document's clock is a published name".
- `coordinates`: one entry per BANK id, in the compiled program's own order
  — inputs first, then joint coordinates, each sorted — each carrying
  `kind` (`"input"` for a declared driver, `"coordinate"` for a joint
  coordinate), `initial` (the value the untimed REST POSE gave it), and,
  for a joint coordinate, `unit` (the joint's declared unit, or `null`). An
  input entry SHALL NOT repeat `unit`, `dtype`, `scale`, `range` or
  `default`: the document's `drivers` table publishes them under the same
  qualified id, and the two tables SHALL name exactly the same set of ids.
- `intermediates`: the sorted qualified ids of every value a compiled edge
  determines that the bank does NOT hold — a plain port, a derived
  coordinate — which a consumer recomputes from the bank on every tick and
  never stores. A value NO compiled edge determines SHALL NOT be listed:
  the end of a relation left to the ordinary enumeration is not part of
  the program and SHALL NOT be published as one, so every id here is
  named in the `gives` of an `edges` entry.
- `edges`: one entry per compiled edge, IN PROGRAM ORDER, defined by the
  requirement "The published edges say what each one reads, gives and
  computes". PROGRAM ORDER is a topological order of the dependency graph
  with each BLOCK contracted to one node; a block's members SHALL appear
  CONTIGUOUSLY at that node's position, in an order deterministic for a
  given tree. A consumer SHALL NOT execute a block's members in that
  order: it SHALL re-derive the block and its selectors, cut the stretch
  at the selectors' crossings, and order the members on each piece, as
  the producer does. It SHALL fold a published `skeleton` by the SAME
  rules the simulation requirement "A selection decides which sources a
  law reads" states — the same folding arithmetic, the same rule about
  which primitives hold a zero branch on an interval of their level, and
  the same distinction between the single compile-time fold and the
  run-time substitution of the branches actually read — because those
  rules decide the ORDER the members run in on every piece, and the
  conformance corpus pins the bank that order produces.
- `spans`: one entry per banked coordinate whose joint declares a range,
  keyed by its qualified id, carrying `low` and `high`, each `null` for
  unbounded, a number, or `{"expression": <text>}` for a bound stated as an
  expression over that coordinate's OWN id and, for a bound that reads
  other coordinates, the qualified ids it reads — the same ids the
  `coordinates` table publishes.
- `sources`: for each bank id and each intermediate, the sorted list of
  INPUT ids that reach it through the program — the candidate table a
  stop's blocked group is filtered out of.
- `limits`: the constants the algorithm is defined by, as numbers, so a
  consumer cannot silently differ from the producer: `crossing_tolerance`,
  `subdivisions`, `bisection_rounds`, `max_crossings` and `agreement` (the
  relative window inside which two increments on one coordinate are called
  equal).

The producer SHALL REFUSE to publish a program naming a coordinate or
intermediate whose qualified id could not be computed from its position in
the tree, naming the node and the reason: a fallback name derived from a
class name is not unique across two instances of that class, and publishing
it would put two different values under one name in one expression scope.
That refusal SHALL be over the coordinates the program COMPUTES — the
bank's, and the ends its compiled edges read and give — and over nothing
else: a value the ordinary enumeration recomputes from the bank, whose
relation reaches no bank coordinate, is not part of the program, is
published nowhere in it, and SHALL NOT refuse the document however its
node is named. A machine whose optional part this render omits, and a
machine whose `.repeat()` children own a port a relation drives, SHALL
therefore publish.

The producer SHALL REFUSE a running root on which a declared driver or a
joint coordinate qualifies to the id `time`, naming it and the reservation:
`time` is the one snapshot entry that is global by contract and the name a
running document's clock is published under.

Every entry of `program.coordinates`, input or joint coordinate, SHALL
carry a `domain` field, so a consumer's readouts and jog controls need no
second reading of the tree. For a JOINT COORDINATE its value SHALL be the
declared domain of the port the joint owns — `rotational`,
`translational` or `signal`, as the port kinds name them — beside its
unit. For an INPUT its value SHALL be `null`: a driver declaration states
a default, a range, a unit, a dtype and a scale, and no domain, and the
producer SHALL NOT derive one from the unit. The document SHALL NOT
publish a `dt`: the step is the executing runtime's choice, the supported
law class is exact across its kinks and locates its jumps and stops
inside whatever tick they fall in, and the conformance corpus pins each
machine's step per scenario.

Publication SHALL succeed over a tree a live running simulation owns and
SHALL leave that simulation's ownership, bank and ability to advance
intact: the publication binder is admitted over a run-owned slot and the
run's binder is restored afterwards.

#### Scenario: Coordinates publish their domain

- **WHEN** the Pascaline module's running root is exported
- **THEN** every `program.coordinates` entry carries `domain`, each arbor
  coordinate reading `rotational` beside its unit, and each dial — a
  declared driver, which states no domain — reading `null`

#### Scenario: Publishing does not disturb a live run

- **WHEN** a running simulation is halfway through a move and the tree's
  document is serialized in the same process
- **THEN** the document is produced, the simulation's bank and commands
  are unchanged, and the next tick advances exactly as it would have

#### Scenario: The program names the bank and the edges

- **WHEN** a running root with three drivers, nine joint coordinates and
  nine relations is published
- **THEN** `program.coordinates` has twelve entries with the drivers' ids
  first, each joint coordinate entry carries the rest pose's value and the
  joint's unit, and `program.edges` lists the nine relations in the order
  the run propagates them

#### Scenario: The drivers table is the one declaration

- **WHEN** a version 5 document is published
- **THEN** every `program.coordinates` entry whose `kind` is `"input"` is a
  key of the document's `drivers` table and every key of that table is such
  an entry, and no declaration field is repeated inside `program`

#### Scenario: A plain port is an intermediate, not a bank entry

- **WHEN** a running root drives a plain port from a driver and drives a
  joint coordinate from that port
- **THEN** that port's qualified id is in `program.intermediates`, is not in
  `program.coordinates`, the edge that computes it names it in `gives`,
  and `program.sources` names the driver that reaches it

#### Scenario: A plain port the program does not compute is published nowhere

- **WHEN** a running root drives a plain readout port from a joint
  coordinate and no relation carries that port back to a bank coordinate
- **THEN** the document is published, that port's qualified id is in
  neither `program.intermediates` nor `program.coordinates` nor
  `program.sources`, no `edges` entry names it, and the pose expression
  the port drives still resolves to the joint coordinate's qualified id

#### Scenario: A repeated child's driven port does not refuse the document

- **WHEN** a running root drives the `height` port of its `.repeat()`
  children, whose list-held names are not legal id segments
- **THEN** the document is published, no copy's port appears in
  `program`, and the same root without `Time.running()` publishes the
  document it always has

#### Scenario: An omitted part's driven coordinate does not refuse the document

- **WHEN** a running root's parameter omits an optional part whose joint
  one of its drivers drives
- **THEN** the document is published, the omitted part's coordinate
  appears nowhere in `program`, and the same root with the part fitted
  publishes it as a bank coordinate

#### Scenario: An omitted part the program still reads is refused

- **WHEN** a running root's parameter omits a part whose coordinate a
  chain of relations reaching a bank coordinate passes through, so a
  compiled edge still reads and gives it
- **THEN** publication is refused naming that node and saying a fallback
  class name is not unique, and no document is written

#### Scenario: A declared range travels as a span

- **WHEN** a running root declares
  `range=(lambda turn: 36 * floor(turn / 36), None)` on a joint
- **THEN** `program.spans` carries that coordinate with `low` an expression
  over that coordinate's own id and `high` `null`

#### Scenario: A bound reading other coordinates travels as a span naming them

- **WHEN** a running root declares
  `range=(0, Bound(lambda turn, a, b: 90 * (abs(a) <= 0.05) * (abs(b) <= 0.05), reads=(p1.lift, p2.lift)))`
  on `plug.turn`
- **THEN** `program.spans` carries `plug.turn` with `high` an expression
  whose free names are drawn from `plug.turn`, `plug.p1.lift` and
  `plug.p2.lift` -- here `plug.p1.lift` and `plug.p2.lift`, the two the
  expression actually reads, its own coordinate not appearing in it --
  every one of them a key of `program.coordinates`, and the document's
  version is `5`

#### Scenario: A program with a self-read law is a version 6 document

- **WHEN** a running root states
  `(ring & wheel.turn).drives(wheel.turn, law=missing_tooth)` and is
  exported
- **THEN** the document declares `version: 6`, the law edge's `needs`
  holds `ring` and `wheel.turn` and its `gives` holds `wheel.turn`, the
  expression's free names are exactly those in `needs`, and no key was
  added to `program` for the read

#### Scenario: A program with no self-read law is unchanged

- **WHEN** a running root that declares no self-read law is exported
  before and after this change
- **THEN** both documents declare `version: 5` and are byte-identical,
  the program's ordering and its minted names included

#### Scenario: A self-read law publishes its plan like any other

- **WHEN** the same self-read law gates on
  `(wheel + g) - 360 * floor((wheel + g) / 360) >= 2 * g`
- **THEN** its edge carries one plan whose `jumps` hold the `floor` node
  over `(wheel.turn + g) / 360` and the comparison over the remainder,
  each marked affine, and whose `skeleton` does not name `wheel.turn` at
  all

#### Scenario: The program's expressions share the document's bindings

- **WHEN** a running root's law and one of its jump plans read the same
  subexpression
- **THEN** that subexpression appears once, as a `bindings` entry, and both
  the law's expression and the plan reference it by name; no `program`
  expression carries producer-local sharing syntax

#### Scenario: Republishing an unchanged running model changes nothing

- **WHEN** an unchanged running model is published twice
- **THEN** the two documents are byte-identical, the program's ordering and
  its minted names included

#### Scenario: An id that cannot be qualified is refused

- **WHEN** a COMPILED edge of a running root's program reaches a value on
  a node whose qualified id is not computable — its instance path is not
  derivable, or a name on that path is not a legal id segment
- **THEN** publication fails naming that node and saying a fallback class
  name is not unique, and no document is written

#### Scenario: A driver named like the clock is refused

- **WHEN** a running root declares a driver whose qualified id is `time`
- **THEN** the simulation refuses at construction, naming the id and that
  `time` is reserved for the clock

#### Scenario: A program carrying a block declares version 7

- **WHEN** a running root whose relations form a block — two laws each
  reading a coordinate the other determines, each behind a comparison on
  a third input — is exported
- **THEN** the document declares `version: 7`, its `program.edges` lists
  the two members contiguously, and no key beyond the ones this
  requirement lists appears anywhere in `program`

#### Scenario: A program with no block is byte-identical

- **WHEN** a running root with no block is exported before and after this
  rule exists
- **THEN** the two documents are byte-identical and declare the version
  they always did

### Requirement: The published edges say what each one reads, gives and computes

Each `program.edges` entry SHALL carry `kind` (`"law"`, `"wiring"`,
`"formula"` or `"check"`), `needs` and `gives` as lists of qualified ids
(`gives` empty for a check), `description` — the relation or derived
coordinate AS WRITTEN — and `stated_by`, the class that stated it, so a
consumer's refusal names what a reader can find in the model. The free
names each of the entry's expressions reads SHALL be exactly the ids in
`needs`, so no separate name list is published. That holds for a BLOCK's
members exactly as for any other edge: a block is published as its member
edges and never as an entry of its own, so nothing about an entry's shape
says whether it belongs to one.

**A law** SHALL carry three lists aligned with `gives`: `expressions`, the
law applied once to a symbolic token per source, or `null` where the law is
a constant and contributes nothing; `affine`, whether that driven end's
value is affine in its sources along a tick's path; and `plans`, `null`
where the expression carries no discontinuous primitive and otherwise a
JUMP PLAN carrying `skeleton` — the whole expression with every jump node
replaced by a branch placeholder — and `jumps`, the jump nodes IN THE
EXPRESSION'S POSTORDER, each with `name` (the placeholder the skeleton
reads it under), `primitive` (`floor`, `ceil`, `sign`, `%`, or a
comparison), `level` (the expression of the level quantity whose surfaces
it crosses, with every jump inside it already replaced by its own
placeholder) and `affine` (whether that level quantity is affine in the
sources). A `%` node SHALL NOT appear as a placeholder in the skeleton: the
skeleton SHALL already carry `a − q * b`, `q` being that node's
placeholder.

Branch placeholders SHALL be minted AT PUBLICATION and be unique across the
WHOLE document — `_j0`, `_j1`, … in edge order and then postorder — under a
prefix lengthened by a leading underscore for as long as any published id
matches `<prefix>` followed by digits. A placeholder that repeated across
two plans would let two different jump nodes share one published
subexpression.

**A wiring** SHALL carry `factor`: its value is `source × factor` and its
increment `Δsource × factor`.

**A formula and a check** SHALL carry `factors` aligned with `needs`,
`constant`, and `slot` — the derived coordinate's own id — and SHALL be
evaluated by these rules and no others:

- forward, where `slot` is in `gives`: the value is
  `constant + Σ needs[i] × factors[i]`;
- backward, where `gives` is one term of the formula: `needs` carries the
  slot FIRST with factor `0.0`, then the other terms, then the solved-for
  term itself with its own coefficient LAST, and the value is
  `(slot − constant − Σ other × factor) ÷ own`;
- an INCREMENT is the same arithmetic with `constant` replaced by zero;
- a check determines nothing: it PREDICTS `constant + Σ needs[i] ×
  factors[i]` over every need but the slot, and a tick in which that
  disagrees with the increment the slot received, relatively beyond
  `limits.agreement`, is a conflict that commits nothing.

#### Scenario: A law with a jump publishes its plan

- **WHEN** a running root's law is
  `4 + 72 * clamp01((angle − 360 * floor(angle / 360) − 113.5) / 11.25)`
- **THEN** its edge carries one expression, `affine: [false]`, and one plan
  whose `jumps` holds a single `floor` entry whose `level` is that source's
  id divided by 360, marked affine, and whose `skeleton` reads that entry's
  placeholder where the `floor` stood

#### Scenario: Placeholders are unique across the document

- **WHEN** a running root carries three laws each holding one `floor`
- **THEN** the three plans' placeholders are three distinct names, and no
  `bindings` entry is referenced from two of the three skeletons in place of
  two different jump nodes

#### Scenario: A remainder is written out in the skeleton

- **WHEN** a running root's law contains `angle % 360`
- **THEN** the plan's jump entry carries `primitive: "%"` and the skeleton
  carries the subtraction of that placeholder times the divisor rather than
  the placeholder alone

#### Scenario: A derived coordinate publishes its coefficients

- **WHEN** a running root declares `left = wrist + 2 * tool` and the rest
  render solves it backward into one term
- **THEN** that edge is a formula whose `needs` names the slot first with
  coefficient `0.0`, the other terms next, and the solved-for term last with
  its own coefficient

#### Scenario: A check publishes what it predicts

- **WHEN** a running root's derived coordinate and every one of its terms
  are determined by other edges
- **THEN** the program carries a `check` edge with empty `gives`, naming the
  slot and the coefficients it predicts from

#### Scenario: A block's members publish as ordinary law edges

- **WHEN** a running root carrying a block is exported
- **THEN** each member is an ordinary `law` entry carrying `expressions`,
  `affine` and `plans`, the free names of each expression are exactly
  that entry's `needs`, and the coordinate each member reads from another
  member is an ordinary id of `needs` with no marking of any kind

#### Scenario: A selector is derivable from the published plan

- **WHEN** a block member's law gates a source behind a comparison on a
  coordinate the block does not determine
- **THEN** that comparison appears in the member's plan as a jump entry
  whose `level` names only ids the block does not give, and whose
  placeholder the member's `skeleton` reads where the comparison stood

### Requirement: A committed bank poses the geometry

Under a running root the producer SHALL serialize the tree with every JOINT
COORDINATE of the linked tree bound to a symbolic token of its own qualified
id, beside every declared driver's token, through the same internal binding
path the symbolic driver mode uses and never through the numeric snapshot
door. The document's ordinary pose expressions SHALL therefore name bank
ids: a joint's own placement operation SHALL be that coordinate's id, or an
expression over the ids of a joint owning several; a plain port, a derived
coordinate and a flexible leaf's `params` SHALL be expressions over whatever
bank ids drive them; and a driver that poses geometry without passing
through a joint SHALL keep publishing its driver id.

A consumer therefore evaluates, per frame, exactly the expressions it
evaluates for any other document, from a scope holding the whole bank rather
than the driver values alone. No second table of poses SHALL be published,
and flexible parts SHALL follow this rule unchanged.

The producer SHALL restore every coordinate it bound — its value, its
binder and its freshness marks — and SHALL re-place the joints from what
their coordinates then hold, so a caller that held a posed tree still holds
one. A declared range SHALL NOT judge a symbolic binding.

The restore SHALL leave the tree able to be POSED again, not only read: a
tree whose coordinates an enumeration bound before the publication SHALL,
after the publication, clear and re-solve exactly as it would have if
nothing had been published. Whatever record the framework keeps of which
coordinates an enumeration bound — the record the next pass reads to decide
what is stale — SHALL therefore be restored beside the coordinates
themselves, because the publication's own enumeration replaces it while
binding none of those coordinates itself.

PUBLISHING SHALL REFUSE NO DECLARATION a pose accepts. In particular, a
relation a CHILD assembly declares into its own coordinate, whose value a
relation the ROOT declares then READS to drive another coordinate, is a
legal shape under a running root: the tree poses, a simulation runs it, and
its document publishes, naming that coordinate's id wherever it poses
geometry. A relation's SOURCE SHALL NEVER be reported as one of its
binders.

#### Scenario: A joint's placement is its coordinate's name

- **WHEN** a running root drives a register wheel through a carry law and
  its document is published
- **THEN** that wheel's rotation operation is the single name of its joint
  coordinate, and the carry law appears only inside `program`

#### Scenario: A plain port follows the bank

- **WHEN** a running root's readout port is driven from a joint coordinate
  at ratio −1
- **THEN** that port's pose expression is an expression over the joint
  coordinate's qualified id

#### Scenario: A flexible part follows the bank

- **WHEN** a running root holds a flexible leaf whose shape parameter is
  driven from a joint coordinate
- **THEN** its `params` expression names that coordinate's qualified id and
  its `spec` is unchanged

#### Scenario: Every name the document reads is declared

- **WHEN** a version 5 document is published
- **THEN** every free name its operation and `params` expressions read, after
  the bindings table is resolved, is the clock name, a key of the `drivers`
  table, a key of `program.coordinates`, or a `program.intermediates` entry

#### Scenario: The tree is left as it was found

- **WHEN** a posed running tree is serialized and the producer returns
- **THEN** every joint coordinate holds the value, binder and placement it
  held before, and rendering it again reproduces the same pose

#### Scenario: A child states the relation and the root reads it

- **WHEN** a running root whose child assembly declares
  `key.insert.drives(p1.lift, …)` and whose own body declares
  `plug.p1.lift.drives(d1.lift, ratio=-1)` is posed and its document is
  published
- **THEN** the document is published, `d1`'s placement names `d1.lift`, and
  nothing is refused — with the root's law reading forward only, as well as
  with one that inverts

#### Scenario: A posed tree re-solves after publication

- **WHEN** a running tree posed by `set_state` is published and then posed
  again
- **THEN** every coordinate holds the value that pose computes, each bound
  by the relation that states it, and no coordinate is reported as bound by
  two statements

### Requirement: A running document's clock is a published name

Under a running root the producer SHALL bind `time` symbolically for the
serialization, so a version 5 document carries the free name `time` — and
NOT the animation variable `$t` — wherever the model reads the clock, and
SHALL publish that name as `program.clock`. A consumer running the machine
SHALL bind it to ELAPSED SIMULATION SECONDS, which never wrap; a consumer
with no run — a still capture, a thumbnail — SHALL bind it to ZERO, the
instant the rest pose is defined at.

Every other reading of an unbound `time` under a running root SHALL be
unchanged: outside the document producer it SHALL go on reading the bare
animation variable exactly as it does today, so the OpenSCAD path, a bare
render and a numeric pose are untouched.

The `animation` object of a version 5 document SHALL carry `fps` and
`frames` as it always has and SHALL omit `loop`, which a running base does
not have.

#### Scenario: A running document carries no animation variable

- **WHEN** a running root whose `simulate()` reads `self.time` is published
- **THEN** its document carries the free name `time`, declares it as
  `program.clock`, and no expression anywhere in the document reads `$t`

#### Scenario: The Python preview is unchanged

- **WHEN** a running root's `time` is read outside a simulation and outside
  the document producer
- **THEN** it reads exactly what it read before this change

### Requirement: The two runtimes share a conformance corpus

The framework SHALL provide a generator that writes a JSON conformance
fixture from its own run, covering a set of small running roots, and the
framework's own suite SHALL replay that committed fixture and reproduce it.
The fixture is the contract between the framework's run and any other
runtime executing a published program: every expected value in it SHALL be
a value the framework's run PRODUCED, never a value recomputed a second way,
so a disagreement means the other runtime drifted.

The fixture SHALL carry, per machine: its name, its `dt`, the published
document's program-bearing keys — `format`, `version`, `drivers`,
`instructions`, `bindings` and `program` — verbatim; a SCRIPT of commands
(moves by a travel or to a value, rates, instruction triggers, a snapshot
and a restore) each naming the tick it is applied before and the handle its
outcomes are reported under; and EVERY TICK of the run, oldest first, each
carrying the whole committed bank, the crossings located in that tick, the
stops located in that tick, and every command created so far with its status
and the travel it has admitted. A sampled fixture SHALL NOT be accepted: a
divergence that heals between two samples is a divergence.

Agreement SHALL be EXACT for discrete state — tick numbers, command
statuses, coordinate, relation, primitive, bound and input names, crossing
surface levels, and the ORDER of every list — and within a stated RELATIVE
tolerance for floats: the bank's values, a crossing's or stop's fraction of
the tick, a stop's evaluated bound and a command's admitted travel. That
tolerance SHALL be the run's own agreement window, the same number the
document publishes as `program.limits.agreement`, because a consumer inside
it cannot manufacture a disagreement the run itself would not.

The generator SHALL REFUSE to write a corpus that does not exercise each of:
the five discontinuous primitives, a multi-source law, a stop located inside
a tick, a bound stated as an expression, a bound reading another
coordinate, a stop reached by the motion of what a bound reads — one whose
coordinate holds the same value before and after its tick — a command
retired `blocked`, a rate, a snapshot and restore, an instruction in each
of its two forms, a tick carrying both a crossing and a stop, a law that
READS THE COORDINATE IT DRIVES — one whose driven coordinate holds at its
gate while the input that reached it goes on moving — a tick in which a
self-read crossing and a stop both fall, a SWITCHED SOURCE — a law edge
reading a coordinate another member of its own block determines — a
SELECTION CROSSING located inside a tick, a tick in which a selection
crossing and a stop both fall, and an IN-BLOCK GATE CROSSING located
STRICTLY INSIDE a tick — a crossing recorded under a block member that
only a jump reading a coordinate ANOTHER member of that block determines
can account for, the member's own driven end excluded. The framework's
suite SHALL test that refusal directly, so the corpus's width is visible
without running the generator.

The corpus SHALL DISCRIMINATE the order in which a block's members are
run, because a document publishes a block's members as a listing and not
as an execution order: a consumer that ran them in the order they are
published, rather than ordering each piece of the tick for itself, SHALL
disagree with the corpus by more than the stated tolerance on the bank of
at least one tick. A framework test SHALL assert this directly, on a
named scenario, rather than inferring it from the feature list.

A framework test SHALL assert that each fixture machine's REAL published
document reproduces the fixture's own program-bearing keys, so the fixture
cannot drift from the producer it claims to come from.

#### Scenario: The framework reproduces its own corpus

- **WHEN** the committed fixture is replayed through the framework's run,
  machine by machine, applying each script entry before the tick it names
- **THEN** every tick's bank, crossings, stops and command outcomes match the
  fixture, exactly for discrete state and within the stated relative
  tolerance for floats

#### Scenario: The corpus carries the document it was run against

- **WHEN** a fixture machine's document is published afresh
- **THEN** its `program`, `drivers`, `instructions` and `bindings` equal the
  fixture's copy

#### Scenario: A corpus missing a primitive is refused

- **WHEN** the generator is asked to write a corpus whose machines contain
  no `%` law
- **THEN** it refuses naming the uncovered feature and writes nothing

#### Scenario: Every tick is present

- **WHEN** a fixture machine runs for forty ticks
- **THEN** the fixture lists forty tick entries, in order, with no gaps

#### Scenario: A corpus missing a bound reading another coordinate is refused

- **WHEN** the generator is asked to write a corpus whose machines declare
  no bound reading another coordinate, or record no stop whose coordinate
  did not move
- **THEN** it refuses naming the uncovered feature and writes nothing

#### Scenario: A corpus missing a law that reads its own driven coordinate is refused

- **WHEN** the generator is asked to write a corpus none of whose machines
  states a law reading the coordinate it drives, or none of whose ticks
  holds such a coordinate at its gate while the input reaching it moves on
- **THEN** it refuses naming the uncovered feature and writes nothing

#### Scenario: A corpus missing a switched source is refused

- **WHEN** the generator is asked to write a corpus none of whose
  machines carries a block, or none of whose ticks locates a selection
  crossing
- **THEN** it refuses naming the uncovered feature and writes nothing

#### Scenario: A corpus missing an in-block gate crossing is refused

- **WHEN** the generator is asked to write a corpus none of whose ticks
  records a crossing, strictly inside the tick, under a block member that
  only a gate on a coordinate another member of that block determines can
  account for
- **THEN** it refuses naming the uncovered feature and writes nothing

#### Scenario: The corpus catches a consumer that runs a block in the published order

- **WHEN** a corpus scenario carrying a block is replayed through the
  framework's run with the block's members run in the order the document
  publishes them, instead of ordered for each piece of the tick
- **THEN** the replay disagrees with the corpus by more than the stated
  tolerance on the bank of at least one tick, while the same replay with
  the members ordered per piece reproduces the corpus

### Requirement: A running document publishes the controls its parts carry

A version 5 document whose root's tree declares at least one control
SHALL carry a top-level `controls` object, beside `instructions`, keyed
by the control's QUALIFIED name and ordered by it, so republishing an
unchanged model produces a byte-identical document.

Each entry SHALL carry, in this order:

- `kind`: `"button"`, `"turn"` or `"slide"`.
- `part`: the LIST of node names, from the document's root down, of the
  node a person touches — the names the document's own tree publishes,
  so a consumer walks to it without parsing a dotted string.
- for a button, `instruction`: the QUALIFIED instruction name, which
  SHALL be a key of the same document's `instructions` table.
- for a turn or slide, `input`: the qualified driver id, which SHALL be a key of
  the same document's `drivers` table; and `per_unit`, defined below.
- `joint`: the LIST of node names of the node the control's coordinate
  poses.
- `coordinate`: that coordinate's qualified id, which SHALL be a key of
  `program.coordinates`.
- `axis`: the selected joint's axis, as three numbers in its interaction frame.
- `origin`: a point on the selected joint's axis, as three numbers in that
  same frame, including the actual pivot of an off-centre rotational joint.
- when needed for a translational or explicitly selected coordinate,
  `operation_span`: the half-open pair of operation indices identifying
  the selected joint's complete placement in the named node.

For an entry with an operation span, the interaction frame SHALL be carried
into the world by the joint node's parent and the node operations outside
and after the selected block, evaluated at the current committed state.
The producer SHALL derive the selected block from the actual placement's
ownership, not an independently authored axis or a search for expression
text. The selected coordinate SHALL pose exactly the identified block.

Existing inferred rotational entries SHALL omit the span and retain their
existing axis and origin values in the joint node's own frame, their field
order and their byte-identical publication. No expression SHALL be added
to the controls table for recovering a current interaction frame.

The entry SHALL NOT repeat the coordinate's `domain` or `unit`, which
`program.coordinates` publishes under the same id, and SHALL carry no
EXPRESSION, so the `controls` table SHALL NOT participate in the
document's `bindings` table and SHALL NOT change it.

`per_unit` SHALL be the coordinate units the part moves per DESIGN unit
the input travels, MEASURED from the compiled program at the REST BANK
with that input displaced by a small amount in each direction and by
nothing else. The two readings SHALL agree within a stated relative
window; a disagreement SHALL be REFUSED naming both readings, the
coordinate and the input. A measurement of ZERO in both directions SHALL
be REFUSED saying the part does not move with that input at rest. The
published value is a reading AT REST: a law whose response to that input
changes with state makes a pointer built on it lead or lag the part,
which costs the gesture tightness and never correctness, because the
part is posed only by what the run commits.

The table SHALL be ADDITIVE within version 5. It SHALL NOT move the
document's version, because a consumer that ignores it still drives the
machine from the declarations the document already published and still
renders the truth. A document whose tree declares NO control SHALL OMIT
the key entirely and SHALL be byte-identical to the document the
producer publishes without this table, for every version — 1, 2, 3, 4
and 5 alike. The compiled program's `identity`, ordering and published
shape SHALL be unchanged by the presence or absence of a control, so a
snapshot taken against a program is neither refused nor accepted
differently because one was declared.

A control whose part THIS render OMITTED SHALL be left out of the table
rather than refused, because the document does not contain that part;
every other unresolvable part is refused where the control is declared.

The producers that publish the model's own declarations — the build's
`viewer.json` and the export's `manifest.json` — SHALL publish this
table. The headless browser-snapshot capture SHALL NOT: it bakes one
instant and already publishes an empty `instructions` table, and a
button naming an instruction that document does not list would be
inconsistent.

#### Scenario: A running document publishes its controls

- **WHEN** a running root declaring
  `controls = {'units dial': Button(units.dial, 'Add one'),
  'turn units': Turn(units.dial, units_entry)}` is built and exported
- **THEN** each document carries a `controls` object with those two
  keys, the button entry naming `Add one` — a key of its own
  `instructions` table — and the turn entry naming `units_entry`, a key
  of its own `drivers` table

#### Scenario: The gesture's geometry comes from the tree

- **WHEN** the part is a leaf under a node posed by
  `turn = Revolute(axis=(1, 0, 0))`, at ratio `-36` from its input
- **THEN** the entry's `part` is the leaf's node-name path, `joint` is
  the posing node's node-name path, `coordinate` is that node's joint
  coordinate id, `axis` is `[1, 0, 0]`, `origin` is `[0, 0, 0]`, and
  `per_unit` is `-36.0`

#### Scenario: An off-centre joint publishes the point it turns about

- **WHEN** the posing node declares `Revolute(axis=(1, 0, 0), at=(0, 3, 0))`
- **THEN** the entry's `origin` is `[0, 3, 0]` — the point the placement
  turns the part about, in that node's own frame — and `axis` is still
  `[1, 0, 0]`

#### Scenario: A part reached by two inputs publishes the declared one

- **WHEN** a coordinate is reached by two inputs and the author declared
  `Turn` against one of them
- **THEN** the entry's `input` is the declared one and `per_unit` is
  measured against that input alone, the other input's contribution
  being held at zero

#### Scenario: A document with no controls is unchanged in every byte

- **WHEN** a running root declaring no control, a looping root and an
  untimed root are each published
- **THEN** none of the three documents carries a `controls` key, each
  declares the version it declared before this change, and each is
  byte-identical to the document published before this change

#### Scenario: The program and the corpus are untouched

- **WHEN** a running root's controls are added, changed or removed
- **THEN** its `program` object — `identity`, `coordinates`, `edges`,
  `spans`, `sources` and `limits` — is unchanged in every byte, and the
  regenerated conformance corpus is identical to the committed one

#### Scenario: A part does not move with its input at rest

- **WHEN** a `Turn` or `Slide` names an input whose displacement at the rest bank
  moves the control's coordinate by nothing
- **THEN** publication is refused naming the part, the input and the
  coordinate, and saying the part does not move with that input at rest

#### Scenario: A part the render omitted drops its control

- **WHEN** a parameter makes the render omit the part a declared control
  names
- **THEN** the published document's tree does not contain that part, its
  `controls` table has no entry for that control, the other controls are
  published unchanged, and the build is not refused

#### Scenario: Republishing an unchanged model changes nothing

- **WHEN** a running model carrying controls is published twice
- **THEN** the two documents are byte-identical, the `controls` table's
  key order and each entry's field order included

#### Scenario: A baked capture publishes no controls

- **WHEN** a running root carrying controls is captured with the
  headless browser snapshot
- **THEN** that document carries no `controls` key, exactly as it
  carries an empty `instructions` table, and is otherwise the document
  the capture published before this change

#### Scenario: A sliding selector publishes its physical direction

- **WHEN** a selector's prismatic coordinate moves by six millimetres per
  design unit of the Slide's named input
- **THEN** its exported entry names kind slide, that input and coordinate,
  a per-unit ratio of six and the actual prismatic placement block

#### Scenario: Two controls identify two placements on one body

- **WHEN** a crank that both lifts and turns is exported with explicitly
  selected Slide and Turn controls
- **THEN** their part and joint-node paths agree, their selected coordinate
  ids and placement spans differ, and each span identifies the placement of
  the coordinate it names

#### Scenario: An inner motion does not rotate an outer joint's axis

- **WHEN** a body has non-parallel inner and outer joint placements and
  both are separately selected by controls
- **THEN** the published blocks distinguish the joints so their axis frames
  can be recovered at every committed pose without applying the inner
  joint's motion to the outer joint's axis

#### Scenario: A press on a prismatic coordinate is publishable

- **WHEN** a Button names a selector posed by a prismatic joint
- **THEN** its entry carries the instruction and the prismatic placement
  span without requiring or inventing a rotational placement

#### Scenario: Unsupported joint placement is not guessed

- **WHEN** a selected control coordinate cannot be associated with exactly
  its complete block of actual placement operations
- **THEN** publication refuses the control naming its coordinate and joint
  rather than publishing an invented or ambiguous interaction frame

#### Scenario: Existing inferred turn publication does not change

- **WHEN** an existing single-joint model with inferred Button and Turn
  controls is exported after this change
- **THEN** its controls and program are byte-identical to the previous
  export, and no operation-span field is added to those entries

### Requirement: A clocked root's document publishes its compiled machine

A document serialized from a CLOCKED root — one in whose tree anything
declares a `State` — SHALL declare `version: 8` and SHALL carry a top-level
`clocked` object, beside `drivers`, `states`, `instructions` and `bindings`
and ahead of `root`, holding what COMPILE TIME decided about the machine and
nothing a request computes.

The version SHALL be a property of the ROOT'S DECLARATION and not of the
tree's content, exactly as `version: 5` is: a clocked root with one state, no
flexible leaf and nothing shared is still a machine a lower consumer would
animate wrongly. `version: 8` SHALL dominate every other rung, so a clocked
document carrying a flexible leaf or a non-empty `bindings` table still
declares 8. A root that declares no `State` SHALL NEVER declare `version: 8`,
SHALL NOT carry a `clocked` key, and SHALL publish the document it published
before this rule existed, byte for byte.

The bump SHALL NOT be treated as additive. A clocked tree's pose expressions
read its declared states as FREE NAMES, which a consumer of a lower version
can bind to nothing, so a consumer that cannot read version 8 SHALL REFUSE it
by name rather than render it. A clocked model SHALL NOT be published at a
lower version with its states rendered as their initial values: the geometry
would be right only at the initial state and would then silently stop
following the machine.

The one function every document producer passes through SHALL go on asking,
structurally and without rendering, whether the tree declares a `State`, and
SHALL REFUSE a clocked tree published WITHOUT its compiled machine, naming
the states. That refusal is a PRODUCER error and not a model error: it is
what stops a producer from reaching a lower-version document by a route the
check does not cover, which is why the check is placed there and not on the
symbolic walk that a browser-rendered snapshot bypasses.

Every expression the object carries SHALL be written in the document's
existing expression language and SHALL participate in the SAME ordered
`bindings` table the tree's expressions use, so no subexpression is published
twice and no producer-local sharing syntax appears anywhere in the document.
The object SHALL be ordered deterministically for a given tree, so
republishing an unchanged model produces a byte-identical document.

`clocked` SHALL carry:

- `identity`: a digest over the root class, the bank's ids with their declared
  `dtype` and `scale`, every committing relation's ends, event primitive and
  law, and every compiled constraint's coordinate, side and level — so a bank
  taken against one machine is refused against another, and so a changed range
  changes the identity.
- `clock`: the free name elapsed simulation seconds bind to, under the
  requirement "A clocked document's clock and animation variable", or `null`
  where the root declares no elapsed base.
- `own`: the free name every published bound reads its own coordinate's
  start-of-request value under. It SHALL be a legal name of the document's
  expression language, minted so that it collides with no published id, and a
  consumer SHALL evaluate that bound's `value` over the bank at the request's
  start and hold the result under this name for the whole request.
- `commits`: one entry per committing relation, in the tree's own order,
  defined by the requirement "A published commit says what it reads, writes
  and fires on".
- `bounds`: one entry per COMPILED CONSTRAINT — one side of one bounded
  coordinate's declared range — defined by the requirement "A published bound
  says where a clocked request stops".
- `limits`: the constants the shared locator is defined by, as numbers, so a
  consumer cannot silently differ from the producer: `crossing_tolerance` —
  which a clocked path introduces no NEW use of but does REACH, when a kinked
  event level's crossings are merged and when a jumped constraint level's cuts
  are folded — and `max_crossings`. The object SHALL NOT publish a
  subdivision count, a bisection count or an increment-agreement window: a
  clocked path never searches, never bisects and never compares two
  increments, and publishing them would state a contract this discipline has
  not got.

A version 8 document SHALL carry EVERY declared instruction in its
`instructions` table, in the shape a version 5 document carries them: each
entry carrying exactly one of `targets` (where the drivers land) and `by` (how
far they travel from where they stand), both keyed by qualified driver id and
both in design units, beside `duration` in seconds. A RELATIVE instruction
SHALL NOT be omitted here: the omission below version 5 exists because a
shipped consumer of those versions reads `targets` off every entry, and a
consumer of this version is a new consumer, so omitting one would be a producer
discarding a declaration for a reason that does not apply. An instruction
naming a STATE as a target SHALL NOT appear in any document: the machine's
compile refuses it before a document exists, and every producer compiles before
it publishes. This version SHALL give a published instruction NO execution
meaning — a clocked machine has no command surface — and what a consumer may do
with one is not settled by this capability.

`clocked` SHALL NOT carry a table of the BANK. A clocked bank holds no joint
coordinate — it is every declared driver and every declared state at its
declared default, with the clock at zero where there is one — so every value
in it is already published by the `drivers` and `states` tables and by
`clock`, and repeating a declaration inside `clocked` is forbidden for the
same reason it is forbidden inside `program`. A value set as SESSION SETUP
SHALL NOT be published: a document says where the machine RESTS.

`clocked` and `program` SHALL NEVER appear in one document. A `State` under a
root declaring `Time.running()` is refused where declared defaults are bound,
so the two are mutually exclusive by construction.

Publication SHALL compile the machine through the same construction a
simulation makes, so the published machine is the simulation's by
construction rather than by two implementations agreeing, and SHALL leave the
tree posed exactly as it found it — every node's snapshot restored and the
tree re-rendered — so a producer that arrives holding a posed tree still
holds one afterwards. The clocked compiler SHALL be imported only where that
compile happens, so a model that declares no `State` loads none of it.

#### Scenario: A clocked model publishes version 8

- **WHEN** a root whose tree declares `units = State(default=0)` is serialized
- **THEN** the document declares `version: 8`, carries a `clocked` object with
  `identity`, `clock`, `own`, `commits`, `bounds` and `limits`, and the pose
  expressions of the parts its states move read those states by qualified id

#### Scenario: A stateless model publishes unchanged

- **WHEN** a model that declares no `State` is serialized before and after
  this capability exists
- **THEN** the two documents are identical byte for byte, and the later one
  carries no `clocked` key and no `states` key

#### Scenario: The version dominates the content ladder

- **WHEN** a clocked root carrying a flexible leaf and a repeated
  subexpression is serialized
- **THEN** the document declares `version: 8`, carries `bindings` and a
  `flexible` node, and the same tree with its `State` removed declares the
  version its content alone gives it

#### Scenario: Every document producer publishes a clocked model

- **WHEN** a clocked model is published through a build, through an export and
  through the development server's publish
- **THEN** each writes a version 8 document carrying the same `clocked`
  object, and each logs that the installed viewer cannot read it while writing
  it anyway

#### Scenario: A producer that publishes a clocked model without compiling it is refused

- **WHEN** a document body is assembled for a clocked tree with no compiled
  machine supplied
- **THEN** it is refused naming the states, and no document is written

#### Scenario: Republishing an unchanged clocked model changes nothing

- **WHEN** an unchanged clocked model is published twice
- **THEN** the two documents are byte-identical, the `clocked` object's
  ordering and its minted names included

#### Scenario: Publication leaves the tree as it found it

- **WHEN** a clocked model posed at chosen driver values has its document
  serialized in the same process
- **THEN** the document is produced and every node holds the snapshot and the
  rendered operations it held before

#### Scenario: A clocked model is still built, tested and photographed

- **WHEN** a clocked model is rendered, assembled, has its STLs built, is run
  under the test runner, and is photographed with the OpenSCAD renderer
- **THEN** each succeeds, and the OpenSCAD image shows the INITIAL BANK —
  every state at its declared default, with `--drive` posing declared drivers
  and a state named there refused by name

#### Scenario: A clocked document publishes both instruction forms

- **WHEN** a clocked root declares an absolute instruction and a relative one,
  each naming a declared driver
- **THEN** the version 8 document's `instructions` table carries both, the
  first with `targets` and no `by` and the second with `by` and no `targets`,
  and the document gives neither any execution meaning

#### Scenario: A stateless tree enters no clocked path when published

- **WHEN** a driven, stateless model is published
- **THEN** no clocked code path is entered at any point

### Requirement: A clocked document publishes its states beside its drivers

A version 8 document SHALL carry a top-level `states` table beside `drivers`,
keyed by each declared state's qualified id and ordered by it, each entry
carrying `default`, `range`, `unit`, `dtype` and `scale` under exactly the
rules the `drivers` table follows: `default` in NATIVE units, `range` in
DESIGN units and never a clamp, `dtype` published by name because a document
is JSON, and `scale` and `unit` verbatim.

The two tables SHALL name DISJOINT sets of ids, and the split SHALL be the
HANDLE rule: every key of `drivers` is an input a person may move, and no key
of `states` ever is — a state is written by the machine at an event, and a
consumer that offered one as a handle would be offering what the framework
refuses. A version 8 consumer SHALL therefore drive the machine only from
`drivers` and from the clock.

Every free name a version 8 document's pose expressions read SHALL be a key
of `drivers`, a key of `states`, the published clock, or a name of the
document's own `bindings` table.

A document that declares no state SHALL NOT carry the key at all, so every
existing document is unchanged.

#### Scenario: States publish their declarations

- **WHEN** a clocked root holding two children of one class declaring
  `digit = State(default=0, range=(0, 9), dtype=int)` is published
- **THEN** the `states` table holds exactly `a.digit` and `b.digit`, each
  carrying that default, that range in design units, and `dtype: "int"`

#### Scenario: A state is not a handle

- **WHEN** a version 8 document is published
- **THEN** no key of `states` is a key of `drivers`, no `instructions` entry
  targets a key of `states`, and the document carries no `controls` key

#### Scenario: Every pose expression resolves

- **WHEN** a clocked root's dials are posed from its states and its drivers
- **THEN** every free name in every operation of the tree is a key of
  `drivers`, a key of `states`, the published clock or a `bindings` name

### Requirement: A published commit says what it reads, writes and fires on

Each `clocked.commits` entry SHALL carry `sources` and `targets` as lists of
qualified ids IN WRITTEN ORDER, `description` — the relation AS WRITTEN — and
`stated_by`, the class that stated it, so a consumer's refusal names what a
reader can find in the model. Every id in `sources` SHALL be a key of
`drivers`, a key of `states` or the published clock; every id in `targets`
SHALL be a key of `states`.

`at` SHALL carry `primitive` — `floor`, `ceil`, `sign`, or one of the six
comparisons — and `level`, the expression of the LEVEL QUANTITY whose surfaces
that primitive crosses. The level SHALL carry no jump node inside it, one
event being ONE surface family. A remainder SHALL NOT appear as an event
primitive, nor anywhere within a level: a remainder IS a jump, and a level
carries none. The SURFACES of a primitive and the BRANCH it reads on a piece are
the ones the published jump vocabulary already defines and SHALL NOT be
published again.

`law` SHALL be a list of expressions ALIGNED WITH `targets`: the project's law
applied once to a symbolic token per source, which is exactly what the
framework inspects it as. A law returning a plain number SHALL publish a
numeric literal and never a null — a commit's law IS the value written, so a
constant is an answer and not an absence. A consumer SHALL evaluate those
expressions at the moving input's landing and at the PRE-EVENT value of every
state.

A published law SHALL say what the framework's executor COMPUTES, which is not
always what the author's text spells. The executor calls the project's own
callable with numbers, and that callable's REMAINDER takes the sign of the
DIVISOR, while the document's `%` primitive is the truncated remainder — the
sign of the DIVIDEND — that both runtimes already evaluate identically. A
published law SHALL therefore carry a remainder in the floored form, composed
from the document's own `%` and its arithmetic, so that the published graph and
the callable give the SAME double for every pair of operands, the SIGN of a
zero result excepted, which compares equal as a number in either runtime. The
document's `%` SHALL keep its existing meaning everywhere else — a published
CHAIN, BOUND and constraint LEVEL included — because the framework evaluates
THOSE through the graph, and a published graph must say what was evaluated.

A target declaring `dtype: "int"` SHALL be rounded ONCE, at the commit, to the
nearest whole NATIVE unit, and a value exactly halfway between two of them
SHALL take the EVEN one. NO conversion by `scale` SHALL be applied at a commit:
a commit law speaks native units already. The consumer SHALL read the
declaration from the `states` table and no key SHALL be added for it. The rule
is stated rather than left to a consumer because the runtimes' own rounding
functions disagree — one takes a half toward positive infinity, another away
from zero — on a value a counting machine lands on constantly.

A commit whose law cannot be evaluated — a remainder by zero being the case the
framework raises on — SHALL refuse the WHOLE request and commit nothing, which
is the atomicity a clocked request already has. A document cannot express a
raise, so a consumer that computes a NON-FINITE value for a commit SHALL refuse
the request rather than bank it.

`shapes` SHALL carry one entry per input that can MOVE this relation's event
level, keyed by that input's id, whose value is the level's structural shape
in that input — `"affine"`, solved by one division, or `"kinked"`, cut at its
own breakpoints and each piece solved the same way. An input ABSENT from
`shapes` cannot move the level, and a consumer SHALL NOT examine the relation
for it. A CURVED level is refused at simulation construction and SHALL
therefore never appear. The kink BREAKPOINTS SHALL NOT be published: they are
the continuous selections in the published expression, which a consumer
re-derives.

#### Scenario: A commit publishes its event and its law

- **WHEN** a clocked root states
  `(crank & units & tens).commits((units, tens), at=floor(crank / 360), law=advance)`
- **THEN** its `commits` entry names `crank`, `units`, `tens` as sources in
  that order, `units` and `tens` as targets, `at.primitive` is `"floor"`,
  `at.level` is the crank id divided by 360, and `law` holds two expressions
  whose free names are drawn from the sources

#### Scenario: An event level that reads the state it commits publishes it

- **WHEN** a clearing relation states
  `at = ring >= START + PITCH * (10 - digit)` over the digit it writes
- **THEN** `at.primitive` is `">="`, `at.level` is the difference whose zero
  is that surface, and the digit's id appears in it as an ordinary free name
  with no marking of any kind

#### Scenario: A relation an input cannot move is not listed for it

- **WHEN** a clocked root has one relation on a crank level and one on a ring
  level
- **THEN** the first entry's `shapes` names the crank and not the ring, and
  the second names the ring and not the crank

#### Scenario: A law taking a remainder of a negative publishes what the executor computes

- **WHEN** a commit law states a remainder over a quantity a request drives
  NEGATIVE
- **THEN** the value the framework banks is the remainder carrying the
  divisor's sign, the published law evaluated under the document's own
  expression semantics gives that same double, and no bare `%` stands where
  the two would differ

#### Scenario: An integer state landing on an exact half takes the even unit

- **WHEN** a commit law lands a `dtype: "int"` state exactly halfway between
  two whole native units
- **THEN** the banked value is the EVEN one, and that is the value the
  conformance corpus records for a second runtime to reproduce

#### Scenario: A kinked event level says so

- **WHEN** a committing relation's `at` is `floor(max(crank, 0) / 360)`
- **THEN** its `shapes` entry for the crank reads `"kinked"`, and the
  continuous selection stands in the published level for a consumer to cut at

### Requirement: A published bound says where a clocked request stops

Each `clocked.bounds` entry SHALL be ONE COMPILED CONSTRAINT — one side of one
bounded coordinate's declared range — and SHALL carry `coordinate` (the joint
coordinate's qualified id), `side` (`"low"` or `"high"`), `unit`, `node` and
`joint` naming what a stop report must name, and `description`.

`value` SHALL be the CHAIN: one expression over the bank's ids giving that
coordinate's value, composed by substitution from the relations that determine
it, down to declared drivers and declared states, which stay free names. An
intermediate port SHALL be composed THROUGH and never appear. Every free name
of `value` SHALL be a key of `drivers` or of `states`.

`bound` SHALL be the declared bound compiled to an expression, reading the
coordinate's own start-of-request value under the document's published `own`
name and every coordinate it declares itself to read through that
coordinate's own chain. A numeric bound SHALL publish a number.

The LEVEL SHALL NOT be published: it is `value − bound` on the high side and
`bound − value` on the low side, `side` says which, and publishing it as well
would publish the bound twice. A consumer SHALL take the threshold
`max(0, level)` at the request's start, SHALL admit the largest fraction of
the travel at which no constraint's level exceeds its own threshold, SHALL
land on the LAST REPRESENTABLE value of the input that satisfies it — deciding
membership by EVALUATING the level there and never by comparing a float to a
bound — and SHALL judge every constraint again over the bank the request ends
at, refusing the whole request where one is violated.

`plan` SHALL be the level's JUMP PLAN where the level carries a discontinuous
primitive and `null` otherwise, in exactly the shape a published program's
jump plan has: `skeleton`, the whole level with every jump node replaced by a
branch placeholder, and `jumps`, the jump nodes in the expression's postorder,
each with `name`, `primitive` and `level`. Placeholders SHALL be minted at
publication and be unique across the WHOLE document, under the same rule the
program's are, because a placeholder repeated across two plans would let two
different jump nodes share one published subexpression.

`shapes` SHALL carry one entry per input that can move the level, keyed by
that input's id, carrying the SKELETON's structural shape and one shape per
published jump, aligned with `plan.jumps`. An input absent cannot move the
level and SHALL NOT be examined for it. A CURVED level is refused at
simulation construction and SHALL never appear.

A declared range that NOTHING binds SHALL still be published, its `value` a
constant and its `shapes` empty: a decorative range on a part that rests is a
range the machine really declares, and a consumer examining it finds it moves
with nothing.

A clocked document SHALL NOT publish a `spans` table: a clocked simulation
banks no joint coordinate, so there is no banked coordinate for a span to be
keyed by, and a bounded coordinate is reached only through its chain.

#### Scenario: A numeric range publishes its chain

- **WHEN** a clocked root declares `range=(0, 9)` on a lift a driver reaches
  through one relation
- **THEN** two entries appear, `low` and `high`, each with the same `value`
  chain over that driver's id, `bound` a number, `plan` null, and `shapes`
  naming that driver

#### Scenario: A ratchet publishes a bound reading its own coordinate

- **WHEN** a clocked root declares
  `range=(lambda turn: PITCH * floor(turn / PITCH), None)` on a crank's joint
- **THEN** one `low` entry appears whose `bound` reads the document's `own`
  name, whose `plan` carries the `floor` node with its level, and whose
  `shapes` entry for the crank carries a shape for the skeleton and one for
  that jump

#### Scenario: A freeze publishes both sides reading the own coordinate

- **WHEN** a clocked root states both bounds of a selector's joint over that
  coordinate's own value and a comparison on the crank's phase
- **THEN** both entries publish, each reading the `own` name and the crank's
  id, and the crank's `shapes` entry names the comparison's jump

#### Scenario: A chain through a port carries no port

- **WHEN** a selector is wired `setting.drives(knob.travel, ratio=6)` through
  a plain `Port` and the knob's joint declares a range
- **THEN** the entry's `value` is an expression over the selector's driver id
  alone, the port's id appears nowhere in the document's `clocked` object, and
  no `intermediates` list is published

#### Scenario: A decorative range publishes as a constant

- **WHEN** a clocked root declares a range on a part no relation, wiring,
  formula or author code binds
- **THEN** its entries publish with a constant `value` and an empty `shapes`

### Requirement: A clocked document's clock and animation variable

Under a clocked root declaring `time = Time.elapsed()` the producer SHALL bind
`time` symbolically for the serialization, so a version 8 document carries the
free name `time` — and NOT the animation variable — wherever the model reads
the clock, and SHALL publish that name as `clocked.clock`. A consumer running
the machine SHALL bind it to ELAPSED SIMULATION SECONDS, which never wrap and
never run backwards; a consumer with no run SHALL bind it to ZERO, the instant
the rest pose is defined at.

Under a clocked root that declares NO time base, `clocked.clock` SHALL be
`null` and nothing about the animation variable SHALL change: such a root has
no clock, a pose leaves an unbound `time` the untimed symbolic animation
variable exactly as it does today, and a geometry that is a formula of time
SHALL go on animating on the document's own `animation` timeline while the
bank stands. A consumer previewing such a document without driving it SHALL
show the INITIAL BANK — every driver and every state at its declared default —
posed, with the animation variable sweeping.

The `animation` object of a version 8 document SHALL carry `fps` and `frames`
as it always has and SHALL omit `loop`, neither of the bases a clocked root
may declare having one.

Every reading of an unbound `time` outside the document producer SHALL be
unchanged, so the OpenSCAD path, a bare render and a numeric pose are
untouched.

#### Scenario: An elapsed clocked document carries the clock by name

- **WHEN** a clocked root declaring `Time.elapsed()` whose part is posed from
  `self.time` is published
- **THEN** the operation reads the free name `time`, `clocked.clock` is
  `"time"`, and no expression anywhere in the document reads the animation
  variable

#### Scenario: A clocked root with no base keeps the animation variable

- **WHEN** a clocked root that declares no time base and whose part is posed
  from `self.time` is published
- **THEN** `clocked.clock` is `null`, the operation reads the animation
  variable exactly as it does for a root declaring no base at all, and the
  `animation` object carries `fps` and `frames` and no `loop`

#### Scenario: The Python preview is unchanged

- **WHEN** a clocked root's `time` is read outside a simulation and outside
  the document producer
- **THEN** it reads exactly what it read before this change

### Requirement: The two runtimes share a clocked conformance corpus

The framework SHALL provide a generator that writes a JSON conformance fixture
from its own CLOCKED executor, covering a set of small clocked roots, and the
framework's own suite SHALL replay that committed fixture and reproduce it.
The fixture is the contract between the framework's clocked executor and any
other runtime executing a version 8 document: every expected value in it SHALL
be a value the framework's executor PRODUCED, never a value recomputed a
second way, so a disagreement means the other runtime drifted.

The fixture SHALL carry, per machine: its name; the published document's
machine-bearing keys — `format`, `version`, `drivers`, `states`,
`instructions`, `bindings` and `clocked` — VERBATIM; a SCRIPT of steps, each
a request naming one input and exactly one of a travel and a target value, or
a snapshot, a restore or a reset; and, per step, the whole bank after it, the
travel ADMITTED, every event fired in path order — each carrying the relations
that fired, the fraction of the requested travel, the input's value there and
the targets with their new values — and every bound met, each carrying the
coordinate, the side, the bound evaluated at the landing, the coordinate's
value there, the input's value and the fraction.

A step the executor REFUSED SHALL be recorded as the refusal's KIND and the
qualified names its message must name, together with the bank AFTER it, which
SHALL be the bank before it: a refused request commits nothing. The message
TEXT SHALL NOT be pinned — prose is edited for clarity, and a fixture that
pinned it would make every such edit a regeneration — while the kind and the
names are the contract a second runtime must reproduce.

**Agreement SHALL be EXACT, bit for bit, for every value including floats**,
and the fixture SHALL state that as a field of its own rather than leave it to
a reader's convention. A clocked executor has no window inside which it
declines to distinguish two values: there is no step, every event is solved by
division, and two relations are ONE event exactly when their landings are the
SAME floating-point value — so a consumer agreeing only within a tolerance
would merge events this framework keeps apart and split events it joins, which
is precisely what the discipline exists to be right about.

The claim SHALL rest on operations that are exact or identically rounded in
both runtimes, and the fixture SHALL exercise no others: IEEE addition,
subtraction, multiplication, division and square root; the truncated
remainder, which is exact; the floored remainder composed from it, whose
correction is one addition; floor, ceiling, absolute value, sign, minimum,
maximum and the comparisons, which select rather than round; and the LANDING
WALK, which is a bisection in the ORDINAL space of a double's own bits and
which a second runtime SHALL reproduce as a bit walk rather than by stepping a
small quantity. A TRANSCENDENTAL function and a POWER are OUTSIDE the claim —
neither is correctly rounded, and two runtimes' libraries need not agree in the
last bit — so the generator SHALL REFUSE a machine carrying one in a published
commit law, event level, constraint level or chain. That is a stated
limitation, not a hidden assumption: a machine that needed one would need a
tolerance declared for ITSELF, beside the file's own, rather than a window the
whole fixture relaxes into.

The generator SHALL REFUSE to write a corpus that does not exercise each of:
the four event primitives (`floor`, `ceil`, `sign` and a comparison); a commit
law taking a remainder of a NEGATIVE operand; a multi-source commit law; a
commit writing several targets; an integer state rounded once; an integer state
whose law lands exactly halfway between two whole native units; a scaled state;
a rising step that fires; a falling step that fires nothing; a kinked event
level cut at its breakpoints; two relations landing on ONE float; two surfaces
one representable value apart taken as two events; two relations writing one
state at one landing refusing the request; an event level that reads the state
it commits; one state written by two relations on two inputs; a request
clipped at a numeric bound; a request clipped at a bound stated as an
expression; a bound reading ANOTHER coordinate; a bound reading its OWN
coordinate; a bound pair both of whose sides read the own coordinate; a
constraint level partitioned at its own jump surfaces; a kinked constraint
level; a request admitted at ZERO travel; a declared range nothing binds; a
bank standing outside a bound and moving back inside it; an end-of-request
judgement refusing a request whose own commit carried a coordinate out of
range; a chain composed through an intermediate port; a snapshot; a restore; a
reset; a banked clock; an event located on the clock; a time request refused
for running backwards; a time request no bound clips; a request refused
for exceeding the crossing maximum; a STRICT surface reached exactly at a
request's endpoint and fired by the request that begins on it; and a request
stopped at a bound from a coordinate standing at exactly ZERO. The framework's
suite SHALL test that refusal directly, so the corpus's width is visible
without running the generator.

A framework test SHALL assert that each fixture machine's REAL published
document reproduces the fixture's own copy, so the fixture cannot drift from
the producer it claims to come from.

The corpus SHALL include one machine carrying, together, several banked wheels
of ONE class, a state written at two different events by two relations on two
inputs, an event level that reads the state it commits, a bound reading its
own coordinate, a bound pair that freezes a coordinate while another input is
off its rest, and a chain composed through an intermediate port — because the
cases a second runtime gets wrong are the interactions, and a corpus of
machines that each carry one feature exercises none of them.

#### Scenario: The framework reproduces its own corpus

- **WHEN** the committed fixture is replayed through the framework's clocked
  executor, machine by machine, applying each script step in order
- **THEN** every bank, admitted travel, event and stop matches the fixture
  exactly, floats included

#### Scenario: The corpus carries the document it was run against

- **WHEN** a fixture machine's document is published afresh
- **THEN** its `clocked`, `drivers`, `states`, `instructions` and `bindings`
  equal the fixture's copy

#### Scenario: A corpus missing an event primitive is refused

- **WHEN** the generator is asked to write a corpus whose machines state no
  `sign` event
- **THEN** it refuses naming the uncovered feature and writes nothing

#### Scenario: A corpus missing a tie is refused

- **WHEN** the generator is asked to write a corpus in which no two relations
  land on one floating-point value
- **THEN** it refuses naming the uncovered feature and writes nothing

#### Scenario: A corpus missing a clip is refused

- **WHEN** the generator is asked to write a corpus none of whose requests is
  clipped at a declared bound, or none of which is admitted at zero travel
- **THEN** it refuses naming the uncovered feature and writes nothing

#### Scenario: A corpus missing a strict surface reached exactly is refused

- **WHEN** the generator is asked to write a corpus none of whose requests
  ends exactly on a STRICT comparison's surface
- **THEN** it refuses naming the uncovered feature and writes nothing

#### Scenario: A corpus missing a stop from a coordinate at zero is refused

- **WHEN** the generator is asked to write a corpus none of whose requests is
  stopped at a bound with the moving input standing at exactly `0.0`
- **THEN** it refuses naming the uncovered feature and writes nothing

#### Scenario: A machine whose machinery is not exactly reproducible is refused

- **WHEN** the generator is asked to include a machine whose commit law or
  whose event level calls a trigonometric function
- **THEN** it refuses naming the operation the exactness claim does not cover,
  and writes nothing

#### Scenario: A refused request is recorded as its kind and its names

- **WHEN** a corpus step asks a clocked machine for a request its own commit
  carries out of range
- **THEN** the fixture records the refusal's kind and the coordinate and side
  its message names, and the bank after the step equals the bank before it
