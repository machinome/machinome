## ADDED Requirements

### Requirement: The state color helper has one public contract

The public API reference SHALL document `machinome.color.color_when(condition, *, on, off)`, its finite zero/nonzero semantics, two fixed hex colors, same-body effect, symbolic publication and reset/restore/replay behavior. The compatibility reference SHALL state its format/consumer requirement and distinguish two-color visual selection from emitted light. Work after a released version SHALL be recorded as unreleased without restating the release as having this new capability. The Studio-owned API shop skill SHALL be synchronized with this public spelling and semantics before the coordinated feature is called complete.

#### Scenario: A maker finds a supported model spelling

- **WHEN** a maker looks up how to color a body from a state observation
- **THEN** the reference shows the public helper in `simulate()` and ordinary publication, with no host script or duplicate-body workaround

#### Scenario: Existing installed versions remain described honestly

- **WHEN** the new source capability has not been released
- **THEN** the changelog/status records it as unreleased with its required viewer capability, while released static-color behavior remains accurately described
