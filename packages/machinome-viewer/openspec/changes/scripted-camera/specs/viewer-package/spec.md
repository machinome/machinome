## ADDED Requirements

### Requirement: Scripted viewpoints preserve the machine

A host SHALL be able to change the camera of a loaded viewer without reloading
geometry or changing machine time, driver values or assembly visibility.

#### Scenario: Follow the sawmill power train

- **WHEN** a host supplies a finite camera position and distinct target
- **THEN** the viewer adopts and renders that view before returning
- **AND** it retains the mounted machine and its state.

#### Scenario: Refuse an invalid view without partial mutation

- **WHEN** either vector is invalid or camera and target coincide
- **THEN** the operation fails and leaves the previous view intact.

### Requirement: Offline posed capture can avoid idle rendering

A filming host SHALL be able to request rendering only when it changes a posed
model's presentation, without a background render loop.

#### Scenario: Capture a frame and inspect it

- **WHEN** an externally controlled, paused, noninteractive posed viewer is
  mounted in on-demand mode and the host changes time or viewpoint
- **THEN** the requested state is rendered synchronously
- **AND** no continuous frame loop runs between host requests.

#### Scenario: Refuse a machine that needs a cadence

- **WHEN** on-demand capture is asked to load a running/clocked document or
  a document with declared instructions
- **THEN** loading fails rather than presenting controls that cannot advance.
