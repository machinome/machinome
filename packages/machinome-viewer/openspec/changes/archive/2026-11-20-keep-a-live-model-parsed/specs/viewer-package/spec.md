## MODIFIED Requirements

### Requirement: Expression cache pressure does not change a machine

A supported document SHALL load, pose and execute with the same results
regardless of expression-cache reclamation or prior supported documents
loaded on the page. A document whose live expression working set exceeds
the cache's reclamation threshold SHALL NOT fail or evaluate differently
solely because it crosses that threshold. Existing malformed-document
refusals and document-local binding meanings SHALL remain unchanged.

This promise SHALL include a large posed portable export whose operations
and flexible parameters read a shared ordered binding table. The complete
valid export SHALL mount with its published rigid and flexible geometry,
driver defaults and declared instruction targets; loading SHALL not stall
indefinitely before geometry is requested solely because its valid binding
table exceeds expression-cache headroom. Invalid content in such a document
SHALL still be refused before rendering it, preserving any last good model.

A loaded document's prepared expression graph SHALL be reused across
consecutive operations on the loaded documents — poses, drawn frames,
clocked requests and run ticks — whatever the size of that graph. Operating
loaded documents SHALL NOT by itself reclaim and reprepare their graphs;
obsolete expression state SHALL be reclaimed where it is created: when a
document is loaded, when a replacement is installed, when a document is
refused, whether at validation or after it, and when any viewer is
disposed, whether or not it is the last. Repeating operations on a loaded
document SHALL NOT add expression state. This reuse SHALL NOT change the
machine's admitted travel, coordinate bank, event records, snapshot/replay
behavior, numerical semantics or refusal behavior.

Whenever no document is being loaded, expression retention SHALL be bounded
by the expression graphs of the currently loaded documents and finite cache
headroom, not by accumulated publication history, refused documents or
disposed viewers. Disposing of the last viewer SHALL release retained
expression state.

#### Scenario: A large operating machine opens

- **WHEN** a supported operating machine's expression working set crosses
  the cache reclamation threshold while its document is loaded
- **THEN** mounting completes and its initial pose and subsequent request
  results match the same machine without cache pressure

#### Scenario: A complete binding-rich posed printer opens

- **WHEN** the complete supported Voron-2 portable export is opened with
  its ordered bindings, rigid model assets and flexible parts intact
- **THEN** the viewer mounts the full assembly, renders its default pose
  and permits its declared Home, Center and Present targets with the same
  placements and flexible shapes the published expressions describe

#### Scenario: Large invalid content is refused before replacement

- **WHEN** a large posed document carries an invalid binding or unsupported
  expression, including one reached through an operation or flexible parameter
- **THEN** loading refuses that content by the existing named error, no
  tree is rendered from it, and a last good model remains standing

#### Scenario: Consecutive operations reuse a loaded graph of any size

- **WHEN** a loaded document's prepared expression graph is larger than the
  cache's reclamation threshold and it is posed, drawn, requested or ticked
  several times in succession
- **THEN** those operations reuse the prepared graph without a cache
  generation change or a repeated binding-table preparation between them,
  and produce the same values, banks and event records as evaluation under
  forced reclamation

#### Scenario: Consecutive ticks reuse a fitting graph

- **WHEN** a supported running document has a prepared graph within the
  finite cache capacity and advances several consecutive ticks
- **THEN** those ticks reuse the prepared graph without a cache generation
  change between ticks and produce the same complete bank and event records
  as evaluation under forced reclamation

#### Scenario: A large document is installed without being prepared again

- **WHEN** a document whose expression graph is larger than the
  reclamation threshold finishes loading and its viewer installs it
- **THEN** its first and later operations reuse the graph its load
  prepared, without preparing its expressions or its binding table again

#### Scenario: Documents of very different size are operated alternately

- **WHEN** two loaded documents, one with a graph larger than the
  reclamation threshold and one small, use the same binding names for
  different expressions and are operated alternately after both have loaded
- **THEN** neither graph is reclaimed between those operations, and each
  document poses and operates according to its own bindings

#### Scenario: Repeated operation adds no expression state

- **WHEN** a loaded document's requests, ticks or poses are repeated after
  they have run once
- **THEN** the repetition prepares no expression state that the first run
  did not

#### Scenario: A viewer that is not the last is disposed

- **WHEN** two viewers are mounted on one page, one of them showing a
  document whose expression graph is larger than the reclamation threshold,
  and that viewer is disposed while the other stays mounted
- **THEN** the disposed document's expression state is not retained beyond
  finite cache headroom, and the remaining viewer continues to pose and
  operate according to its own document

#### Scenario: A refused replacement leaves no partial graph behind

- **WHEN** a viewer refuses a replacement document after preparing a large
  part of its expressions, whether the refusal comes from validating its
  expressions or from a later step such as a required asset that fails to
  load, and the last good model is then operated
- **THEN** the refused document's expression state is not retained beyond
  finite cache headroom, and the last good model poses and operates as it
  did before the refusal

#### Scenario: Reclamation happens between operations

- **WHEN** the expression cache is reclaimed after a machine has loaded
  and before it is posed or stepped again
- **THEN** it produces the same values, stops and request outcomes as it
  would without that reclamation, never values from another expression

#### Scenario: Documents keep their own binding meanings under pressure

- **WHEN** two mounted documents use the same binding names for different
  expressions and loading or operating either creates cache pressure
- **THEN** each continues to pose and operate according to its own bindings

#### Scenario: Reload history is not retained indefinitely

- **WHEN** a host repeatedly replaces a document with supported documents
  of a bounded working-set size, including a failed replacement
- **THEN** obsolete expression state is reclaimed, the last good model
  continues to operate correctly, and retained expression state does not
  grow with the number of past replacements

#### Scenario: The final viewer is disposed

- **WHEN** the last viewer is disposed after operation under cache pressure
- **THEN** no expression state remains retained by the viewer
