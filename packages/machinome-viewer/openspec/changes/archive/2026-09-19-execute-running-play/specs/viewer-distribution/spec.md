## ADDED Requirements

### Requirement: A play-capable distribution advertises its capability

The package's single declarations SHALL set viewer API 22 and document versions 1 through 9. The built bundle, Python entry point, and `machinome-viewer describe` command SHALL report those same values, and stale-bundle currency handling SHALL rebuild before reporting them.

API 22 SHALL supersede the earlier numeric declaration under "The viewer
declares its API version", retaining that requirement's single-declaration
and capability-reporting contract.

#### Scenario: A framework asks for viewer capabilities
- **WHEN** it resolves the entry point or invokes `describe` from this source or an installed distribution
- **THEN** it receives API 22 and document versions `[1,2,3,4,5,6,7,8,9]`, matching the bundle's loader

#### Scenario: Older documents remain supported
- **WHEN** the bundle mounts any valid document version 1 through 8
- **THEN** it retains the behavior and public handle contract of API 21 for that document
