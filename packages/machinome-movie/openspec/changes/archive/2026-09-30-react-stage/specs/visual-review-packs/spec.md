## MODIFIED Requirements

### Requirement: Render records resolved review events

Videomaker SHALL record a versioned review-sample plan in the published film
manifest from the same global output-frame requests used for rendering. The
plan SHALL identify exact zero-based adjacent frame pairs for shot joins,
resolved active word-reveal changes, source-emphasis changes/clearing, shot
ends and film end, reading word reveals from the titles' revealed words and
emphasis from the source panels' lit tokens in the element states of those
requests, and comparing state by shot, element and authored cue identity
across a shot's active-to-outgoing role transfer, retaining incoming/outgoing
side as context. Authored cue identity SHALL distinguish duplicate identical
descriptions without adding fields to existing frame requests. Event
candidates SHALL follow the picture side selected for composition: a fade
uses only its resolved outgoing or incoming side, while a dissolve, wipe or
slide may include both. A role transfer alone SHALL NOT create a word or emphasis onset;
all labels SHALL remain when events share a pair. The plan SHALL also identify actual resolved
midpoint and last-active output frames of each transition for interior
inspection. Labels SHALL identify resolved request/candidate picture state,
not assert perceptual visibility through a full plate, opacity, wipe edge or
other occlusion. It SHALL not add an episode or document authoring field.

#### Scenario: Fractional events and a transition
- **WHEN** a shot boundary, spoken-word onset, or source-emphasis change falls
  between output-frame instants, including a join with outgoing content
- **THEN** the manifest's event pair uses the preceding and first changed
  **rendered global frame requests**, not rounded nominal shot-local time

#### Scenario: Cache hit and shared pair
- **WHEN** all output frames are reused from the shot cache and a word and
  emphasis event resolve to the same adjacent pair
- **THEN** the manifest still contains the pair once with both event labels

#### Scenario: A join has an interior
- **WHEN** an incoming transition spans multiple global output frames and
  outgoing and incoming shots have distinct cues at the same list position
- **THEN** the plan retains their distinct shot/cue identities and side context and
  samples the actual transition midpoint and last active frame in addition to
  the join pair

#### Scenario: A cue moves from active to outgoing
- **WHEN** a cue has the same resolved word count or emphasis state on the
  frame before a join and on the next frame as outgoing content
- **THEN** the join pair retains both role contexts but the role change alone
  adds no word or emphasis onset label

#### Scenario: Identical descriptions have distinct authored cues
- **WHEN** two simultaneous even-reveal overlays in one shot have identical
  text and timing but different authored list indices
- **THEN** their resolved counts and review labels retain both authored
  identities without changing the old frame request or merging them by text

#### Scenario: Fade selects one picture side
- **WHEN** an incoming cue advances during a fade's outgoing-only half, then
  the fade switches to the incoming picture
- **THEN** the off-picture advance is not labelled as a visible word onset;
  the newly selected picture may record that cue's then-resolved count as
  entry state, and the join's midpoint/last-active samples remain present

#### Scenario: End without a predecessor
- **WHEN** a film or shot has only one output frame
- **THEN** the plan uses a single-frame end sample and invents no prior frame

#### Scenario: Lit tokens of a movie's source panel
- **WHEN** *Cut and Advance* lights `waterwheel`, `drives` and `crankshaft` on
  its source panel as they are spoken, then clears them
- **THEN** the plan holds a pair at each token's first lit frame and one at
  the clearing, each labelled with the shot, the source element and the cue
