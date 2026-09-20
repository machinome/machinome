## ADDED Requirements

### Requirement: Installed viewer support includes retained time drives

The shipped bundle and package description SHALL consistently report viewer API
23 and supported document versions 1 through 10 after retained time-drive
execution is implemented and verified. Package version 0.2.0 SHALL remain
identified as unreleased until the maintainer separately publishes it.

#### Scenario: A producer discovers matching browser support

- **WHEN** a producer asks the installed viewer for its supported versions
- **THEN** it receives API 23 and v1–10 support matching the actual bundle,
  and its version-10 Astrarium document can load and run
