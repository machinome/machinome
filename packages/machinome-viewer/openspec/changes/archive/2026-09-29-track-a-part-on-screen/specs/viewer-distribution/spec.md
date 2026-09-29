## ADDED Requirements

### Requirement: Installed viewer support identifies film annotations

The package's single capability declaration SHALL report viewer API 28 once
the viewer tracks parts and world points on screen, highlights parts with
the others kept, dimmed or ghosted, and adopts an up direction and a field
of view per view change. Document versions SHALL remain 1 through 13: none
of these capabilities reads a new document field. The built bundle, the
Python entry point, `machinome-viewer describe` and every mount handle SHALL
report the same API, and the existing bundle-currency checks SHALL remain
effective. This declaration SHALL NOT imply a package release or revise the
recorded 0.7.1 release, which declares API 27.

#### Scenario: A film host checks before mounting

- **WHEN** a host reads the installed viewer's API before relying on part
  tracking, highlighting or per-view up and field of view
- **THEN** it receives 28 from the package, the bundle and the mount handle
  alike, with document versions 1 through 13

#### Scenario: An older bundle is told apart

- **WHEN** a host finds API 27
- **THEN** it knows none of the three capabilities is present, without
  calling a member to find out
