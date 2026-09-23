## ADDED Requirements

### Requirement: Installed viewer support identifies two-envelope Follow

After version-12 Follow execution passes producer/consumer parity and browser validation, the package's single capability declarations SHALL report viewer API 25 and document versions 1–12. The built bundle, Python entry point, command report and browser global SHALL agree; stale-bundle currency checks SHALL remain effective. This capability declaration SHALL NOT imply a new package release or revise historical release claims.

#### Scenario: Producer discovers Follow support
- **WHEN** a producer or host reads the installed viewer capability report
- **THEN** it receives API 25 and supported document versions 1 through 12 matching the actual built bundle and its Follow tests

#### Scenario: An older consumer sees the new export
- **WHEN** a version-12 Follow document is offered to a viewer whose supported versions end at 11
- **THEN** that viewer refuses the document rather than silently executing its old law or Play algorithm

#### Scenario: Source bundle is stale
- **WHEN** capability metadata has changed but a source checkout's bundle is older
- **THEN** the existing currency mechanism rebuilds it or refuses by name rather than advertising Follow for an old bundle
