## MODIFIED Requirements

### Requirement: A controls table the viewer cannot resolve is refused by name

A document whose controls table the viewer cannot resolve SHALL be refused
when it is loaded, naming the document, the control and what is wrong,
before anything is rendered — the surface an undeclared driver id, an
unreadable bindings table and an inexecutable program already stand on. A
document is refused when:

- the table, or an entry in it, is not of the published shape, or an
  entry's kind is neither a press nor a turn;
- an entry's part or joint does not name exactly one node of that
  document's own tree, or the joint is not that part or one of its
  ancestors;
- an entry names an instruction its document's instruction table does not
  declare, an input its drivers table does not declare, or a coordinate its
  program does not publish — each refusal naming what the document does
  declare;
- a turn's published ratio is missing, not a finite number, or zero, which
  would make the gesture's quantum meaningless;
- an entry's axis or origin is not three finite numbers, or its axis has no
  direction;
- the joint the entry names is not posed by the coordinate the entry names
  as the LEADING run of its own operations — zero or more translations and
  then exactly one rotation over that coordinate, which are the two shapes
  the producer's joint placement publishes: the rotation alone, or a
  translation, the rotation and the translation back for a joint placed off
  its node's origin — the reading the gesture's geometry depends on;
- two controls of the same kind name the same part and do not have distinct
  selected turn joints, so a gesture without a named handle would have two
  meanings and the viewer would have to choose; in particular two turns on
  the same part selecting the same joint SHALL be refused even if their
  names, inputs or coordinates differ;
- the document carries a controls table and no program, which every
  document below the running version is, since a control has nothing to
  submit a request to.

Two valid turns naming one visible part but distinct selected joint paths
SHALL both load. Their separate named handles SHALL each submit only their
own declared input and measure about their own declared joint. A drag on
the shared body without selecting a handle SHALL submit neither turn.
This allowance SHALL NOT weaken any path, operation-span, coordinate,
domain or instruction validation above.

A document that carries no controls table SHALL load, pose, run and drive
exactly as it did before the viewer could read one.

#### Scenario: A part that does not resolve is named

- **WHEN** a document's control names a part its own tree does not contain
- **THEN** mounting fails naming the document, the control and the path,
  and nothing is rendered

#### Scenario: An instruction the document does not declare is named

- **WHEN** a document's press control names an instruction absent from its
  instruction table
- **THEN** mounting fails naming the control, the instruction and the
  instructions the document does declare

#### Scenario: A ratio of zero is refused

- **WHEN** a document's turn control publishes a ratio of zero
- **THEN** mounting fails saying the gesture has no quantum, rather than
  presenting a part that cannot be turned

#### Scenario: A joint that does not pose the coordinate is refused

- **WHEN** a document's control names a joint whose own operations do not
  begin with that coordinate's rotation, or with translations and then
  that rotation
- **THEN** mounting fails naming the control, the joint and what the joint
  is posed by, rather than turning the part about a line derived from it

#### Scenario: A joint placed off its node's origin is accepted

- **WHEN** a document's control names a joint whose operations are a
  translation, the rotation over the coordinate, and the translation back,
  and whose entry publishes the point it turns about as `origin`
- **THEN** mounting succeeds, and a drag on the part is measured about the
  line through the world image of `origin` along the world image of `axis`
  — the same line the joint's own placement turns the part about

#### Scenario: Distinct selected turn joints have distinct handles

- **WHEN** two valid turn controls name one part and select different joint
  paths, one of them an ancestor of the other
- **THEN** mounting succeeds and both named handles are reachable; a drag
  on either handle requests only its declared input about its own selected
  joint, while a drag on the undecided body requests neither

#### Scenario: Crossing the selected handle does not choose the part behind it

- **WHEN** a maker moves the pointer from a two-turn part onto either of
  its named handles while another controlled part lies behind the handle
- **THEN** that handle remains present and selected through pointerdown,
  and its gesture requests only its declared input; moving back to the
  canvas restores ordinary nearest-visible-part hover

#### Scenario: Same selected turn joint remains ambiguous

- **WHEN** two turn controls name one part and select the same joint, even
  with different display names, inputs, coordinates or operation spans
- **THEN** mounting fails naming both declarations and their shared part
  and joint; it does not silently choose one

#### Scenario: A control without a run is refused

- **WHEN** a document below the running version, or one carrying no
  program, carries a controls table
- **THEN** mounting fails naming the table, rather than presenting an
  affordance with nothing to ask

#### Scenario: A document with no controls is untouched

- **WHEN** a document carrying no controls table is mounted
- **THEN** it loads, poses, runs and is driven exactly as it was before
  this capability existed, and its parts move the camera
