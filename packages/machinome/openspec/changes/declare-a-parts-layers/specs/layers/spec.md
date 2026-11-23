## ADDED Requirements

### Requirement: A layer is defined once and named by its key

The framework SHALL offer `Layer(key, *, label)` from `machinome.layers`, the
one module that defines it. `key` SHALL be the name a published document
carries for the layer and `label` the name a person reads; both SHALL be
required and SHALL be non-empty strings, and any other value SHALL be refused
naming the argument. A layer SHALL NOT change once made, and a layer SHALL be
equal only to itself, so a project defines each layer once, in its own module,
and imports that object wherever a part declares it.

#### Scenario: A project defines its layers

- **WHEN** a project's `simulation/layers.py` defines
  `ELECTRICAL = Layer('electrical', label='Electrical path')`
- **THEN** `ELECTRICAL.key` is `'electrical'`, `ELECTRICAL.label` is
  `'Electrical path'`, and assigning either is refused

#### Scenario: A layer without a label

- **WHEN** a project writes `Layer('electrical')` or `Layer('', label='Wires')`
- **THEN** the call is refused naming the argument that is missing or empty

### Requirement: A node class declares the layers it is on

A node class SHALL be able to declare `layers` in its body: one `Layer`, or a
non-empty tuple of `Layer`s in which no layer repeats. `layers` SHALL be a
reserved class-body name on a node class: any other value, a string, a list,
an empty tuple, a repeated layer, a child declaration or a parameter among
them, SHALL be refused where the class is written, naming the class and the
form. A class SHALL be on every layer it declares and every layer its bases
declare, a plain mixin's included, so a subclass's declaration adds to its
bases' and never replaces them; a mixin's declaration SHALL be checked by the
same form, the refusal naming the node class and the mixin. Layers SHALL be
declared only in a class body: a node instance that assigns `layers` SHALL be
refused when its model is published, naming the node. A declaration SHALL NOT
change any part's geometry, artifact identity, piece or any other published
field.

#### Scenario: A subsystem declares its layer

- **WHEN** `class Electrical(AssemblyNode)` declares `layers = ELECTRICAL`
- **THEN** the class is accepted and is on the electrical layer

#### Scenario: A part on two layers

- **WHEN** `class Key(StepNode)` declares `layers = (ELECTRICAL, MECHANICAL)`
- **THEN** the part is on both layers

#### Scenario: A value that is not a layer

- **WHEN** a node class declares `layers = 'electrical'`, `layers = [ELECTRICAL]`
  or `layers = (ELECTRICAL, ELECTRICAL)`
- **THEN** the class is refused as it is written, naming the class and saying
  that `layers` takes one `Layer` or a tuple of them, each once

#### Scenario: A subclass adds a layer

- **WHEN** a part class declaring `layers = MECHANICAL` derives from a base
  declaring `layers = ELECTRICAL`
- **THEN** the subclass is on both layers

#### Scenario: A layer assigned on an instance

- **WHEN** a node assigns `self.layers = ELECTRICAL` in its constructor and its
  model is published
- **THEN** the publication is refused naming the node and saying that layers
  are declared in the class body

### Requirement: A node is on the layers of every node above it

A node in the published tree SHALL be on the layers its class declares and on
every layer of every node above it in that tree. A child SHALL be able to add
layers and SHALL NOT be able to remove one. A node that is not published SHALL
contribute no layer: a part fused into a rigid node, whose document entry is
the rigid node's, and a child omitted from its parent's render.

#### Scenario: A part inside a tagged subsystem

- **WHEN** an assembly declaring `ELECTRICAL` holds a wire whose class
  declares nothing and a lamp whose class declares `MECHANICAL`
- **THEN** the wire is on the electrical layer and the lamp on both

#### Scenario: A part fused into another

- **WHEN** a fusion that declares no layer fuses a part whose class declares
  `ELECTRICAL`
- **THEN** the fusion is on no layer and the document names no layer for it

### Requirement: One key names one layer in a machine

Two different `Layer` objects that share a key SHALL NOT both be declared in
one published tree: the document SHALL be refused when it is produced, naming
the key, both layers and the path of a node declaring each, and no document
SHALL be published. Two objects sharing a key in two different models SHALL
NOT conflict.

#### Scenario: A layer defined twice

- **WHEN** one part declares `Layer('electrical', label='Electrical path')` and
  another part of the same model declares a second
  `Layer('electrical', label='Wires')`
- **THEN** `machinome build` publishes no document and reports the refusal
  naming the key, both labels and both parts' paths

#### Scenario: Two models of one project

- **WHEN** two models of one project each define their own layer keyed
  `electrical`
- **THEN** each model publishes its document

### Requirement: A document carries a model's layers

A document whose published tree declares at least one layer SHALL carry, at
its top level, `layers`: a list with one entry `{"key": <string>, "label":
<string>}` per distinct layer, each key a non-empty string appearing once and
each label a non-empty string, in the order a depth-first walk of the
published tree in child order first meets each layer. A node entry whose node
declares layers SHALL carry `layers`: the list of the keys that node itself
declares, each once, every one of them a key of the top-level list; it SHALL
NOT carry a key only because a node above it declares it. A node is on the
layers its entry names and on every layer named by an entry above it in the
tree. Both keys SHALL be absent where nothing is declared. The fields SHALL be
additive: they SHALL NOT change the document's version, and a consumer that
ignores them shows the whole machine.

#### Scenario: A part's layers are read off the document

- **WHEN** a document's top-level list holds `electrical` and `mechanical`, an
  assembly's entry names `electrical` and a part below it names `mechanical`
- **THEN** the part is on both layers, and its entry does not name
  `electrical`

#### Scenario: A model that declares no layer

- **WHEN** a model declares no layer
- **THEN** its document carries no `layers` key at its top level or on any
  node, and declares the version it declared before layers existed

### Requirement: Every producer publishes the same layers

The build's `viewer.json`, the export's `manifest.json` and the browser
viewer's capture staging SHALL carry the same `layers` list and the same node
keys for the same model. A model that declares no layer SHALL be published by
each of them byte-identical to the document it published before layers
existed.

#### Scenario: The build and the export agree

- **WHEN** a model declaring layers is built and exported
- **THEN** `viewer.json` and `manifest.json` carry equal `layers` lists and
  equal `layers` on every node entry

#### Scenario: An untagged model is unchanged

- **WHEN** a model that declares no layer is built after this capability
- **THEN** its `viewer.json` is byte-identical to the one built before it
