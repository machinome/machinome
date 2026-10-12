## Purpose

Support project-authored, inspectable local narrated films of an existing
posed Machinome simulation, with reproducible presentation and production
evidence separate from publication.

Administrative note (29 September 2026): This Purpose was added for baseline
sync after the first rehearsal was implemented and adopted during
implementation. It does not change the original requirements, scenarios,
evidence, or adoption chronology, and does not claim prior ratification.

## ADDED Requirements

### Requirement: The author can inspect and edit one screenplay

An episode SHALL keep narration, visual intent and timed presentation cues in
human-readable project-owned source, with technical presets separately readable.
Reading an episode MUST NOT require executing program code.

#### Scenario: Revise a lesson

- **WHEN** the author opens the sawmill episode
- **THEN** each shot shows its narration beside its visual direction and cues
- **AND** those same sources are consumed by production without a second script.

#### Scenario: Refuse ambiguous source

- **WHEN** source contains duplicate keys, aliases or executable/custom types
- **THEN** production fails with a source error rather than guessing intent.

### Requirement: Invalid production inputs are refused before capture

Production SHALL check episode timing, model duration and pinned source revision,
named camera/layer references and evidence file existence before rendering.

#### Scenario: Detect a stale sawmill export

- **WHEN** the export duration or recorded model revision differs from production settings
- **THEN** production fails before rendering frames from that export.

#### Scenario: Detect incomplete direction

- **WHEN** shots overlap or leave a gap, or reference an unknown layer or camera
- **THEN** production identifies the invalid input rather than silently omitting it.

### Requirement: Presentation follows the authored model state

The film SHALL present the existing posed simulation at the authored times,
viewpoints and visibility states, independently of capture speed. The tool MUST
NOT create replacement mechanical behavior or imply support for stateful replay.

#### Scenario: Explain a stroke slowly

- **WHEN** a shot maps its video interval to a shorter model interval or explicit model-time keys
- **THEN** frames follow that mapping without advancing by wall-clock time.

#### Scenario: Restore the whole assembly

- **WHEN** a reveal shot is followed by a shot with no hidden layers
- **THEN** the previously hidden parts are visible again.

#### Scenario: Revisit a pose

- **WHEN** the tested renderer returns to an identical time and presentation after another shot
- **THEN** it restores identical pixels in that same rendering environment.

### Requirement: Narration is generated and reusable

The author SHALL be able to generate synthetic narration using the configured
ElevenLabs voice and reuse unchanged generated speech without another paid request.
Credentials MUST remain outside project sources, browser content and build records.

#### Scenario: Change camera timing only

- **WHEN** presentation is revised but cached speech inputs are unchanged
- **THEN** production reuses the verified cached segments and their alignment.

#### Scenario: A sentence is too long

- **WHEN** measured speech exceeds its available shot interval
- **THEN** production reports the required duration and retains the generated segment
- **AND** it does not truncate or silently stretch the narration.

### Requirement: Captions and teaching cues follow the lesson

The video SHALL combine explanatory labels and readable captions with the 3D
animation. Captions SHALL follow generated speech timing and retain the written
project name when a pronunciation alias is used.

#### Scenario: Explain cut and advance

- **WHEN** the sawmill episode marks cut/advance phases around measured spoken words
- **THEN** corresponding model poses and labels follow the authored phase mapping
- **AND** narration captions use the generated alignment rather than reading-speed estimates.

### Requirement: An author can inspect a local rehearsal

The workflow SHALL produce still previews and a narrated local MP4 with the
requested dimensions, duration and frame rate, plus reusable caption files.

#### Scenario: Render the first episode

- **WHEN** the valid sawmill screenplay and narration are rendered
- **THEN** the result contains 2,520 video frames at 1920×1080 and 30 fps over 84 seconds
- **AND** it includes narration, on-screen captions and the authored credits.

#### Scenario: Inspect before a full render

- **WHEN** the author requests a still preview or reduced silent render
- **THEN** the workflow produces review media without generating speech.

### Requirement: Credits and publication gaps are explicit

The episode SHALL credit the source project and state its license, and tell the
audience that the video description links to the interactive simulation. Missing
release URLs SHALL remain explicit and MUST NOT be replaced with invented links.
Building a video MUST NOT upload or publish it.

#### Scenario: Review a rehearsal before the simulation is public

- **WHEN** public simulation or source URLs are unresolved
- **THEN** a local rehearsal can be produced with credit and license text
- **AND** generated release copy marks missing links and the build is not release-ready.

### Requirement: Production leaves inspectable evidence

Generated media SHALL stay outside committed source in the consuming project's
build directory. Production SHALL record resolved source inputs, model/viewer and
audio identities, output checks and rendering environment for the rehearsal.

#### Scenario: Trace the first video

- **WHEN** an author inspects the completed build manifest
- **THEN** it identifies the screenplay, model revision, actual asset/audio hashes,
  rendering settings and encoded media properties used for that build.
