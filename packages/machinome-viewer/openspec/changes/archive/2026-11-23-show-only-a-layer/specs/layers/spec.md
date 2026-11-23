## ADDED Requirements

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

### Requirement: The viewer reads a document's layers

The viewer SHALL read the `layers` a document carries and SHALL put every part
on its effective layers: the layers its own entry names and those named by
every entry above it. A document whose `layers` list is not a list of entries
each with a non-empty string `key` and a non-empty string `label`, which names
a key twice, or one of whose node entries carries `layers` that are not a list
of distinct keys of that list, SHALL be refused by name before anything is
drawn. A document without `layers` SHALL be mounted exactly as before this
capability. A viewer before this capability, which ignores the fields, shows
the whole machine.

#### Scenario: A part inherits its subsystem's layer

- **WHEN** a document's `circuit` entry names `electrical` and its child
  `lamp` names `mechanical`
- **THEN** the viewer reports `lamp` on `electrical` and `mechanical`

#### Scenario: A node names a layer the document does not list

- **WHEN** a node entry names `electrical` and the top-level `layers` list
  holds no such key
- **THEN** the document is refused naming the node and the key, and nothing
  is drawn

### Requirement: A host reads the layers a document declares

The mount's handle SHALL answer the document's layers, in the document's
order, each a frozen object carrying its `key` and `label`, and an empty list
for a document that declares none. It SHALL answer the same list, and the same
objects, until a document whose layers differ is installed. It SHALL answer
one layer by its key, and SHALL refuse an unknown key by name, listing the
keys the document declares; it SHALL NOT answer an unknown key with nothing.

#### Scenario: An app lists the layers

- **WHEN** an app reads the layers of a document declaring `electrical`
  labelled "Electrical path" and `mechanical` labelled "Rotor stepping"
- **THEN** it receives the two layers in that order with their keys and labels

#### Scenario: An unknown key

- **WHEN** an app asks for the layer `optical` of that document
- **THEN** the call is refused naming `optical` and the keys `electrical` and
  `mechanical`

### Requirement: Showing a layer shows only the parts on it

The mount's handle SHALL let a page show one layer of the document, handed
back as the viewer answered it or as any object carrying one of the
document's keys: every part on that layer SHALL be drawn and every other part
SHALL be hidden. Showing nothing (`null`) SHALL show the whole machine. One
layer SHALL be shown at a time. A string, or a layer whose key the document
does not declare, SHALL be refused by name, changing nothing. Showing a layer
SHALL NOT move the camera. Every accepted call SHALL be reported to the
handle's assembly-change subscribers as a change of the visibility state.

#### Scenario: The electrical path alone

- **WHEN** the Enigma's app shows the layer `electrical`
- **THEN** the copper parts, the wires, the keys and the lamps are drawn, the
  case and every other part are hidden, and the camera stays where it was

#### Scenario: Back to the whole machine

- **WHEN** the app then shows nothing
- **THEN** every part the navigator has not hidden is drawn again

#### Scenario: A string is not a layer

- **WHEN** an app calls `show('electrical')`
- **THEN** the call is refused saying that it takes a layer the viewer
  answered, or null, and the picture and the subscribers are untouched

### Requirement: A part the shown layer leaves out is absent

A part that is not on the shown layer SHALL be treated as absent wherever the
viewer acts on what it shows: it SHALL NOT be drawn, its markings SHALL NOT be
drawn, a press, a hover and the on-screen position of a path SHALL NOT reach
it, and framing SHALL NOT count it. Showing a layer SHALL draw the picture
once, and a page standing still afterwards SHALL draw nothing. A declared
control on such a part SHALL stay in the handle's listing of controls and
SHALL NOT be reachable on screen. No material or geometry SHALL change.

#### Scenario: A hidden part is not reached

- **WHEN** the electrical layer is shown and a maker presses where the case
  stands
- **THEN** the case answers nothing, its on-screen position is null, and a
  part on the layer behind it is what the press reaches

#### Scenario: Framing counts what is drawn

- **WHEN** the electrical layer is shown and the page frames the model
- **THEN** the view fits the parts on the layer and not the case around them

### Requirement: The shown layer composes with focus and hiding

The shown layer, the focused root and the explicitly hidden paths SHALL be
three independent states, and a part SHALL be drawn only when the focused root
includes it, no hidden path covers it and the shown layer, if any, holds it.
Showing a layer SHALL NOT change the focused root or the hidden paths;
focusing, hiding and showing a path SHALL NOT change the shown layer. The
navigation state SHALL report the shown layer beside the focused root and the
hidden paths.

#### Scenario: The navigator cannot reveal what the layer leaves out

- **WHEN** a maker has hidden the case in the navigator, the app shows the
  electrical layer, and the maker then shows the case again in the navigator
- **THEN** the case is still not drawn, the navigation state no longer lists
  it as hidden, and showing the whole machine then draws it

#### Scenario: The layer does not reveal what the maker hid

- **WHEN** a maker hides a key in the navigator and the app then shows the
  electrical layer, and then the whole machine
- **THEN** the key stays hidden throughout and stays listed as hidden

### Requirement: A republished document keeps the shown layer it still declares

When a republished document still declares the shown layer's key, the layer
SHALL stay shown, drawn over the new tree's membership; when it no longer
does, the whole machine SHALL be shown. The change SHALL be reported in the
update's one notification.

#### Scenario: A part joins the shown layer

- **WHEN** the electrical layer is shown and the model is republished with
  one more part declaring it
- **THEN** that part is drawn and the layer stays shown

#### Scenario: The shown layer is gone

- **WHEN** the model is republished without the shown layer
- **THEN** the whole machine is shown and the navigation state reports no
  layer

### Requirement: A model's app shows a layer and the viewer adds no control

The helper's hook that answers a clocked machine's bank SHALL also answer the
document's layers, re-rendering the app when they change; any app SHALL read
them, and show one, through the mount's handle. The viewer SHALL present no
control of its own that shows or switches a layer: not in its panels, the
inspector, the navigator or the export page. A model with no app SHALL get no
layer control from this capability.

#### Scenario: The Enigma's buttons

- **WHEN** the Enigma's app renders a button per layer from the hook and one
  for the whole machine
- **THEN** each button shows its layer, or the whole machine, with no other
  control of the viewer's appearing

#### Scenario: A model without an app

- **WHEN** a model declaring layers and no app is shown
- **THEN** the whole machine is drawn and no layer control is presented

### Requirement: The layers capability has an explicit reader capability

The viewer SHALL advertise viewer API 32 for reading a document's layers and
showing one through the mount's handle, and SHALL keep reading document
versions 1 to 14.

#### Scenario: A host requires the capability

- **WHEN** a host reads the mount handle's API version
- **THEN** it is 32, and the document versions reported are 1 to 14
