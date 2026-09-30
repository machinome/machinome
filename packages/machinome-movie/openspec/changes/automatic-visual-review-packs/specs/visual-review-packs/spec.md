## Purpose

Give Leonardo's finished local films bounded, traceable encoded-MP4 images
for a person to review, without treating image generation as approval.

## ADDED Requirements

### Requirement: Render records resolved review events

Videomaker SHALL record a versioned review-sample plan in the published film
manifest from the same global output-frame requests used for rendering. The
plan SHALL identify exact zero-based adjacent frame pairs for shot joins,
resolved active word-reveal changes, source-emphasis changes/clearing, shot
ends and film end, comparing state by shot and authored cue identity across a
shot's active-to-outgoing role transfer and retaining incoming/outgoing side
as context. A role transfer alone SHALL NOT create a word or emphasis onset;
all labels SHALL remain when events share a pair. The plan SHALL also identify actual resolved
midpoint and last-active output frames of each transition for interior
inspection. It SHALL not add an episode authoring field.

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

#### Scenario: End without a predecessor
- **WHEN** a film or shot has only one output frame
- **THEN** the plan uses a single-frame end sample and invents no prior frame

### Requirement: Review uses only the attested encoded film

Before generating or reusing a pack, Videomaker MUST verify the published
MP4's bytes against the manifest's output SHA-256, keep stable attested
manifest/MP4 input during decoding, and recheck the live inputs before
publishing or reusing a pack. A detected change during the attempt MUST
prevent a new complete index or successful reuse. Videomaker SHALL validate
the recorded sample plan against decoded film count and dimensions. Every pack image SHALL
come from the decoded MP4 in display order and identify its exact zero-based
frame index and actual presentation timestamp. Standalone review SHALL NOT
recompute events from the current episode or timeline implementation.

#### Scenario: Good published film
- **WHEN** a compatible manifest and its matching MP4 are reviewed
- **THEN** each selected image corresponds to the decoded MP4 frame at the
  index in the plan and its label reports decoder-observed PTS

#### Scenario: Changed film or inconsistent decode
- **WHEN** the MP4 hash differs, or its decoded count, dimensions, or PTS
  disagree with the manifest and plan
- **THEN** review refuses the pack without presenting stale images as current

#### Scenario: Output replaced during review
- **WHEN** the published MP4 or manifest changes after the initial hash check
  but before decode/reuse completes
- **THEN** review detects the changed live input, refuses success and publishes
  no new complete pack index, even if an old pack or a stable snapshot exists

#### Scenario: Manifest predates review plans
- **WHEN** standalone review receives a legacy manifest with no compatible
  recorded review plan
- **THEN** it refuses automatic event review with a rerender instruction,
  leaves the original film untouched, and does not run a newer timeline on it

### Requirement: Pack is bounded and honest

Videomaker SHALL automatically attempt, after a successful film publication,
an overview of at most 96 deterministic frames including the first and last,
plus deduplicated join, word, emphasis and end event pairs and transition
interior samples. Overview and event sheets SHALL contain at most 24 cells;
event pairs SHALL remain adjacent, with at most 12 pairs per page, and
pagination SHALL retain every selected event/sample. Visible cell labels
SHALL be length-bounded while the index retains complete cue descriptions
and all shared labels. The pack SHALL distinguish padding from film frames
and SHALL state that it was generated for human review, not reviewed or
approved.

#### Scenario: Leonardo's full feature demonstration
- **WHEN** the 1,380-frame, 30-fps `demo-all-features` MP4 is reviewed
- **THEN** the overview includes the historical half-second indices and the
  last frame on bounded pages, and event pages include its joins, word and
  source-emphasis changes, and end without silent truncation

#### Scenario: Multiple labels and page boundary
- **WHEN** two events share a pair and event count spans multiple sheets
- **THEN** the pair is shown together once with both labels and pagination
  keeps every pair adjacent within a sheet

#### Scenario: Long cue descriptions
- **WHEN** a cue has a long text label and many events share its frame pair
- **THEN** every full label remains in the index, sheet text stays within its
  cell, and no event is omitted or clipped merely to fit the sheet

### Requirement: Review publication is independent of film publication

Videomaker SHALL publish each complete review-pack index atomically last in
an immutable, provenance-bound generation under the project's ignored build
directory. Old complete packs SHALL remain available. A failed automatic
pack attempt SHALL be visibly reported separately and SHALL NOT roll back or
falsely mark the successfully published MP4/manifest as failed; standalone
review failure SHALL have a failing command status.

#### Scenario: Interrupted or failed pack
- **WHEN** image decoding, generation, or index publication fails after the
  film is published
- **THEN** the MP4 and manifest remain valid, no incomplete generation has
  a usable complete index, and the render reports a pack-specific retry path

#### Scenario: Retry after another complete pack
- **WHEN** standalone review is retried for a matching manifest and MP4
- **THEN** it either verifies/reuses a complete pack or publishes another
  complete generation without overwriting the earlier one
