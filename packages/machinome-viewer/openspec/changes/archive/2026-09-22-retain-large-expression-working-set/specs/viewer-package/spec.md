## MODIFIED Requirements

### Requirement: Expression cache pressure does not change a machine

A supported document SHALL load, pose and execute with the same results
regardless of expression-cache reclamation or prior supported documents
loaded on the page. A document whose live expression working set exceeds
the cache's reclamation threshold SHALL NOT fail or evaluate differently
solely because it crosses that threshold. Existing malformed-document
refusals and document-local binding meanings SHALL remain unchanged.

When a supported machine's prepared expression graph fits within the
viewer's finite cache capacity, consecutive ticks SHALL reuse that graph
without reclaiming and reparsing it between those ticks. This reuse SHALL
NOT change the machine's admitted travel, coordinate bank, event records,
snapshot/replay behavior, numerical semantics or refusal behavior.

Expression retention across repeated publications SHALL be bounded by
current live work and cache headroom, not accumulated publication history.
Disposing of the last viewer SHALL release retained expression state.

#### Scenario: A large operating machine opens

- **WHEN** a supported operating machine's expression working set crosses
  the cache reclamation threshold while its document is loaded
- **THEN** mounting completes and its initial pose and subsequent request
  results match the same machine without cache pressure

#### Scenario: Consecutive ticks reuse a fitting graph

- **WHEN** a supported running document has a prepared graph within the
  finite cache capacity and advances several consecutive ticks
- **THEN** those ticks reuse the prepared graph without a cache generation
  change between ticks and produce the same complete bank and event records
  as evaluation under forced reclamation

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
