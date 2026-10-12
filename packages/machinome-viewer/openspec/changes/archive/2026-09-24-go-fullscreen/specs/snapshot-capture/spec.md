## ADDED Requirements

### Requirement: A photograph carries no full-screen control

A capture SHALL NOT photograph the viewer's full-screen control, whatever
the staged document and whether or not the headless browser permits full
screen. The pixels the transparent background promises SHALL stay
transparent where the control would otherwise stand.

#### Scenario: A model without a timeline is photographed

- **WHEN** a staged posed document that does not read `$t` is captured
- **THEN** the capture's page shows no full-screen control and the
  photograph's bottom-right corner is transparent
