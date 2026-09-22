## ADDED Requirements

### Requirement: Installed viewer support identifies source-timed running

After source-timed execution is implemented and verified, the package's single
capability declarations SHALL report viewer API 24 and document versions 1–11.
The built bundle, entry point, command report, browser global and handles SHALL
agree, preserving existing bundle-currency checks. These capability numbers
supersede API 23 and the v1–10 list in "Installed viewer support includes
retained time drives"; they do not authorize a package release or rewrite
historical release claims.

#### Scenario: A producer discovers the corrected consumer

- **WHEN** a producer or host reads the installed viewer's capability report
- **THEN** it receives API 24 and supported versions 1 through 11, matching
  the actual built bundle and its source-timed execution tests

#### Scenario: Unbuilt source cannot advertise an old bundle as corrected

- **WHEN** capability metadata has changed but a source checkout's bundle is stale
- **THEN** the existing currency mechanism rebuilds it or refuses by name
  rather than reporting API 24 for a bundle that still executes endpoint chords
