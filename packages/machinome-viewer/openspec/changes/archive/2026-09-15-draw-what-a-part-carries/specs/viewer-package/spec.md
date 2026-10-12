## MODIFIED Requirements

### Requirement: Geometry is refetched only when its identity changes

The viewer SHALL treat geometry as current only while both its model path and
`mtime` match the values it loaded, and SHALL refetch when either differs. A
node whose geometry `artifactChanged()` has just fetched SHALL count as current
for the `manifestChanged()` that immediately follows, even though the document
it fetches names a new `mtime` for that node, because the two calls loaded the
same bytes moments apart.

#### Scenario: A parameter change moves the model path

- **WHEN** a node's model path changes with an unchanged `mtime`
- **THEN** its geometry is refetched

#### Scenario: A source edit moves the mtime

- **WHEN** a node's `mtime` changes with an unchanged model path
- **THEN** its geometry is refetched

#### Scenario: A manifest update follows the artifact update it describes

- **WHEN** `manifestChanged()` names a new `mtime` for a node whose geometry
  `artifactChanged()` already replaced
- **THEN** `manifestChanged()` does not refetch that node's geometry


#### Scenario: A marking's artwork is edited

- **WHEN** a document update names a new `mtime` for one of a node's markings
  while the node's own model path and `mtime` are unchanged
- **THEN** that marking's geometry is refetched and the node's own geometry is
  not

#### Scenario: A part is rebuilt and its markings are not

- **WHEN** a document update names a new model path for a node while every one
  of its markings keeps the model path and `mtime` it was loaded with
- **THEN** the node's geometry is refetched and no marking's geometry is

#### Scenario: A marking is removed from a part

- **WHEN** a document update no longer lists a marking a node was carrying
- **THEN** that marking is no longer drawn, the node's remaining markings and
  its own geometry are undisturbed, and no geometry is refetched for them

#### Scenario: A marking artifact is updated on its own

- **WHEN** a host reports that a marking's artifact changed, naming that
  artifact's path
- **THEN** that marking's geometry is refetched and redrawn, no other geometry
  is refetched, and the document update that follows — naming the new `mtime`
  for bytes already on screen — does not refetch it again

### Requirement: Colour is inherited and falls back to a normal material

The viewer SHALL use a node colour or its nearest ancestor colour, and SHALL
use the framework's normal-based material when no colour is available.

#### Scenario: A part inherits its assembly's colour

- **WHEN** a node has no colour and an ancestor does
- **THEN** the part renders in the ancestor's colour

#### Scenario: A colourless assembly

- **WHEN** no node declares a colour
- **THEN** every model renders with the normal-based material


#### Scenario: A marking keeps its own colour on a colourless part

- **WHEN** a node that inherits no colour carries a marking that declares one
- **THEN** the part renders with the normal-based material and the marking
  renders in its own declared colour, and no colour of the part's is applied
  to it

### Requirement: The viewer declares its API version

The package SHALL declare one API version, expose it on every mount handle and
the browser global, and make it readable without executing the bundle. It SHALL
be raised whenever the mount interface or handle changes incompatibly, and when
a capability a host may require is added. The declared version SHALL be 14,
reflecting the drawing of the markings a document's parts carry — each in its
own declared colour, over the surface it lies on — on top of part controls, the
inspector layout, the mountable assembly navigator, the published
assembly-navigation state and its change subscription.

The package SHALL also declare, in the same one place, the document schema
versions this build reads, and SHALL report them beside the API version
wherever the API version is reported. A consumer asking which documents a
viewer reads SHALL be answered with that list rather than having to infer
it from the API version, and a consumer that receives no such list SHALL be
entitled to assume the versions every released viewer reads. Reading a
document's controls table or a node's markings list SHALL NOT change that list:
both are additive within the document versions that carry them, and the API
version is the only capability gate either moves.

#### Scenario: A host checks compatibility before mounting

- **WHEN** a host reads the installed viewer API version
- **THEN** it obtains the package's single declared version without running a
  browser bundle

#### Scenario: A mounted viewer reports its version

- **WHEN** a host inspects a mount handle or the browser global
- **THEN** both report the same declared API version

#### Scenario: A host requires targeted updates

- **WHEN** a host needs `artifactChanged()` and `manifestChanged()`
- **THEN** the declared API version tells it whether they are available

#### Scenario: A host requires camera orientation control

- **WHEN** a host needs to supply an up direction and field of view
- **THEN** the declared API version tells it whether they are available

#### Scenario: A host requires flexible geometry

- **WHEN** a host needs `version: 3` documents rendered
- **THEN** the declared API version tells it whether the capability is
  available

#### Scenario: A host requires documents carrying a bindings table

- **WHEN** a host needs `version: 4` documents rendered
- **THEN** the declared API version tells it whether the capability is
  available

#### Scenario: A host requires the published navigation state

- **WHEN** a host needs to read the focused root and the hidden paths, and
  to be told when they change
- **THEN** the declared API version tells it whether the capability is
  available, before it mounts a bundle it cannot build a navigator on

#### Scenario: A host requires the mountable navigator

- **WHEN** a host means to present the package's own assembly navigator
  rather than build one
- **THEN** the declared API version tells it whether the bundle carries
  one, before it mounts a bundle that publishes the navigation state but
  no navigator

#### Scenario: A host requires the inspector layout

- **WHEN** a host means to mount the package's composed inspector —
  sidebar, navigator and viewer in one element — rather than lay those
  parts out itself
- **THEN** the declared API version tells it whether the bundle carries
  one, before it mounts a bundle that carries a navigator and no layout to
  put it in

#### Scenario: A host requires part controls

- **WHEN** a host means to present a machine a maker drives by touching it,
  rather than only from a panel
- **THEN** the declared API version tells it whether this bundle reads a
  document's controls table and binds a pick to it, before it mounts a
  bundle that would show the same document with no affordance at all

#### Scenario: A producer asks which documents this viewer reads

- **WHEN** a producer asks the installed viewer what it reads, before
  publishing a document
- **THEN** it receives the list of document schema versions this build
  renders, including the running version, from the same declaration the
  bundle refuses by

#### Scenario: A host requires the markings drawn

- **WHEN** a host means to present a machine whose answer is printed on its
  parts — a calculator's digits, a dial's graduations — rather than a blank
  drum
- **THEN** the declared API version tells it whether this bundle draws a
  document's markings, before it mounts a bundle that would show the same
  document with nothing readable on it

## ADDED Requirements

### Requirement: The viewer draws the markings a part carries

The viewer SHALL draw every marking a rigid node of the published document
carries, one per entry of that node's markings list, each from the artifact the
entry names and in the colour the entry declares. A marking SHALL be drawn in
its part's own place, moving with the part under every pose, animation instant
and committed mechanical state the part moves under, with no placement supplied
by the viewer: the artifact holds the artwork's surface in the part's own frame,
and the part's own operations place it.

A marking SHALL be drawn OVER the surface it lies on, from every viewing
distance and angle at which the part itself is drawn, and SHALL NOT be broken
up by the surface it marks. The bias that achieves this is the viewer's own
rendering constant and SHALL NOT be presented as, or derived from, anything the
document states about where the part's surface is. A marking whose artwork is
open on both sides SHALL be drawn from either side.

A node that carries no markings SHALL be drawn exactly as it is drawn by a
viewer that has never read a marking: the same geometry, the same material and
the same scene contents. A document whose nodes carry no markings SHALL be
rendered, read back and photographed identically to the same document published
before markings existed.

The viewer SHALL draw markings on a document of any schema version it renders:
the markings list is additive to the document and is gated on no version.

#### Scenario: A part's markings are drawn in their own colours

- **WHEN** a document is mounted whose part carries two markings declaring
  different colours
- **THEN** both are drawn on that part, each in the colour its own entry
  declares, and the part is drawn in the colour it declares

#### Scenario: A marking goes where its part goes

- **WHEN** a driver, an animation instant or a mechanical command moves a part
  that carries a marking
- **THEN** the marking moves with it, arriving in the same place on the part's
  surface it started on, without the viewer computing any placement for it

#### Scenario: A marking is visible over the surface it marks

- **WHEN** a marked part is photographed from a viewpoint that sees the marked
  surface
- **THEN** the marking's colour is what is seen where the marking is, and the
  part's is what is seen where it is not

#### Scenario: A marking on a colourless part

- **WHEN** a document is mounted whose marked part inherits no colour
- **THEN** the part renders with the normal-based material and its marking
  renders in its own declared colour

#### Scenario: A marked document below the running version

- **WHEN** a document that declares an early schema version carries markings on
  its parts
- **THEN** its markings are drawn, exactly as a later version's are

#### Scenario: An unmarked document is untouched

- **WHEN** a document whose parts carry no markings is mounted
- **THEN** it renders exactly the picture it rendered before this viewer could
  draw a marking, and its scene contains nothing a marking would have added

### Requirement: A markings list the viewer cannot read is refused by name

The viewer SHALL refuse a document whose markings it cannot read, before
anything is rendered, naming the document, the node and the marking at fault and
what is wrong with it — the same refusal surface an unresolvable bindings table,
an inexecutable program and an unresolvable controls table already stand on. It
SHALL refuse a markings value that is not a list; an entry that is not an
object, or whose name or artifact reference is not a non-empty string, or whose
colour is not a six-digit hexadecimal colour; two markings of one node declaring
the same name; and a markings list on a node that is not rigid.

The viewer SHALL NOT draw a document's markings in part: a marking it cannot
read is a fault in the document that produced it, and rendering the rest would
present an incomplete marking as the machine's own answer.

A node carrying no markings key SHALL reach exactly the validation it reached
before this viewer could read one.

#### Scenario: A marking without a colour

- **WHEN** a document carries a marking whose entry declares no colour, or one
  that is not a six-digit hexadecimal colour
- **THEN** the document is refused naming it, before anything is rendered

#### Scenario: A marking without an artifact

- **WHEN** a document carries a marking whose entry names no artifact
- **THEN** the document is refused naming the node and the marking, and no
  geometry is fetched

#### Scenario: Two markings of one part share a name

- **WHEN** a node's markings list declares the same name twice
- **THEN** the document is refused naming the node and the repeated name

#### Scenario: A marking on a node that is not rigid

- **WHEN** a markings list appears on a node that carries children or a
  flexible spec
- **THEN** the document is refused naming that node

#### Scenario: A document with no markings is validated as before

- **WHEN** a document whose nodes carry no markings key is mounted
- **THEN** it is accepted or refused exactly as it was before this viewer could
  read a markings list
