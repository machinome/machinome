## Purpose

Show export-pinned project Python beside Leonardo's model with deterministic
typing, reviewable narration, and optional external subtitles, without
presenting fabricated source or silently changing a mastered film.

Administrative note (29 September 2026): This Purpose was added for baseline
sync after the source-scenes change was planned and implemented. It does not
change the original requirements, scenarios, or evidence, and does not
backdate proposal or ratification.

## ADDED Requirements

### Requirement: Source on screen is authentic

The author SHALL select real Python line ranges from the consuming project at
the model's pinned revision. Production MUST refuse changed bytes, missing files,
out-of-repository paths and invalid line ranges before rendering. Build records
SHALL identify the file, lines, revision and content hashes.

#### Scenario: Show the wheel connection
- **WHEN** a scene selects the sawmill's wheel-to-crankshaft declaration
- **THEN** the audience sees that source with Python highlighting beside the model.

#### Scenario: Refuse a fabricated or stale excerpt
- **WHEN** selected source differs from the pinned model revision
- **THEN** production refuses it rather than presenting it as that model's code.

### Requirement: Typing is reproducible and timed

The author SHALL time source reveals in shot-local seconds, including pauses.
Typing and highlighting MUST be derived from video time, preserve source text,
escape embedded markup and restore exactly after seeking. Invalid or incomplete
typing schedules MUST be refused. The whole excerpt SHALL remain legible.

#### Scenario: Follow measured narration
- **WHEN** the narration reaches the wheel connection's authored cue
- **THEN** its actual line types into view while the model follows its own authored clock.

#### Scenario: Revisit an earlier instant
- **WHEN** capture seeks forward and returns
- **THEN** source, cursor, visibility and model pixels match the original instant.

### Requirement: Subtitles are optional player assets

Narrated renders SHALL produce synchronized UTF-8 SRT beside the MP4 with the
same basename. Narration subtitles MUST NOT be burned into frames or embedded in
the MP4. Explanatory labels and source code remain allowed.

#### Scenario: Watch without captions
- **WHEN** a viewer plays the MP4 without enabling subtitles
- **THEN** the picture contains no narration transcript.

#### Scenario: Enable subtitles separately
- **WHEN** the author uploads the SRT to YouTube or loads it in a media player
- **THEN** its cues follow measured speech and retain written pronunciation aliases.

### Requirement: Narration beginnings are preserved and reviewable

The author SHALL select an expressive model and feminine voice, acquire lossless
speech, and reuse verified cached audio. Production MUST preserve entire clips
at the authored offset without gating or onset fades, reject overflow rather than
truncate, and keep credentials outside artifacts. Evidence MUST distinguish
sample preservation from subjective listening approval.

#### Scenario: Expressive short scene
- **WHEN** the author selects Eleven v3 and PCM output
- **THEN** the scene uses that model and lossless input without unsupported legacy
  context fields or a silent model fallback.

#### Scenario: Preserve a first phoneme
- **WHEN** a cached clip contains sound at its first sample
- **THEN** the mix retains that onset after the authored preroll and subtitles use
  the same offset.

### Requirement: A short scene is a complete review artifact

Preview and rendering SHALL work for episodes shorter than the old rehearsal,
with in-range replay checks and thumbnails, encoded-media verification and
source/audio provenance. Building MUST NOT publish anything.

#### Scenario: Review the code study
- **WHEN** a short Leonardo scene is built
- **THEN** it yields an inspected animation-and-code MP4, SRT, preview and manifest.
