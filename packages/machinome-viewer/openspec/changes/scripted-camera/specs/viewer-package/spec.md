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
