# framework-identity Specification

## Purpose
TBD - created by archiving change rename-framework-to-machinome. Update Purpose after archive.
## Requirements
### Requirement: The framework has one Machinome identity

The framework distribution SHALL be named `machinome`, its import package
SHALL be `machinome`, its executable SHALL be `machinome`, and its source
repository SHALL be `machinome/machinome`. Current product metadata,
documentation, diagnostics, templates and integration contracts SHALL use
those names.

#### Scenario: A user installs and imports the framework

- **WHEN** a user installs `machinome`
- **THEN** the framework is importable as `machinome`
- **AND** its command is available as `machinome`

#### Scenario: A reader follows the source link

- **WHEN** current package metadata or documentation names the source
  repository
- **THEN** it points to `github.com/machinome/machinome`

### Requirement: Version 0.7 records the rename lineage

The first Machinome release SHALL be version 0.7.0 and SHALL state that it is
the direct continuation of solid-node 0.6.0 with the repository's complete Git
history. Its changelog, release note and migration guidance SHALL explain the
reason for the name change and map old distribution, import, command,
configuration, viewer and mechanics names to their Machinome replacements.
A later 0.7.x release SHALL keep that material and add its own changelog
entry, `HISTORY.rst` entry and release-note section above it.

Historical ADRs, archived changes and release records SHALL retain the names
that were true when they were written. Current synthesis and indexes SHALL
make the transition discoverable.

#### Scenario: A 0.6 user reads the 0.7 release material

- **WHEN** the user looks for the next release after solid-node 0.6.0
- **THEN** the material identifies Machinome 0.7.0 as that release and gives
  the complete migration map

#### Scenario: A 0.7.0 user reads the 0.7.1 release material

- **WHEN** the user looks for what changed after Machinome 0.7.0
- **THEN** the changelog's 0.7.1 entry sits above the 0.7.0 entry, and the
  rename and migration material of 0.7.0 is unchanged beneath it

#### Scenario: A reader opens a historical decision

- **WHEN** an ADR predating 0.7 discusses solid-node
- **THEN** its historical wording remains intact and current architecture
  material identifies it as a decision inherited by Machinome

### Requirement: The renamed runtime is a clean break

Machinome 0.7 SHALL NOT install a `solid_node` import package or a `solid`
console alias. It SHALL read project configuration from `[tool.machinome]` and
runtime settings from `MACHINOME_*` names. When it can identify a former
`[tool.solid-node]` table or former environment name, it SHALL fail with a
migration message rather than silently ignoring configuration or running with
different defaults.

#### Scenario: A project uses current configuration

- **WHEN** a project declares models under `[tool.machinome]`
- **THEN** `machinome models`, `machinome build --all`, and `machinome test
  --all` resolve those models

#### Scenario: A project retains the former table

- **WHEN** a project contains `[tool.solid-node]` and no `[tool.machinome]`
- **THEN** the command fails naming the table and its `[tool.machinome]`
  replacement

#### Scenario: A caller imports the former package

- **WHEN** only Machinome 0.7 is installed and a caller imports `solid_node`
- **THEN** no compatibility package supplied by Machinome satisfies that import

### Requirement: Extras select independent Machinome products

The distribution SHALL expose `viewer`, `mechanics`, and `studio` extras that
select `machinome-viewer`, `machinome-mechanics`, and `machinome-studio`
respectively. The default framework installation SHALL depend on none of them.
Current release material SHALL state that the experimental studio remains
unpublished and that the `studio` extra cannot resolve from a package index
until that publication occurs.

The `viewer` extra and the `web-snapshot` extra SHALL require the matching
viewer release or newer: the two packages are numbered together, and the
floor each extra states SHALL be the one matching viewer version the manual
declares in its release facts, so a release that moves the matching version
moves both floors with it or fails naming the extra left behind. The floor
states what the extra installs, not what a document needs: the framework
SHALL keep reading the installed viewer's own report for what it renders,
and current upgrade material SHALL keep stating which older viewers read the
documents the release exports.

#### Scenario: A user installs the viewer extra

- **WHEN** `pip install "machinome[viewer]"` resolves from published packages
- **THEN** the independent AGPL `machinome-viewer` distribution is installed
  beside the framework

#### Scenario: A user upgrades the framework with the viewer extra

- **WHEN** an installation holding an older viewer runs
  `pip install -U "machinome[viewer]"` against published packages
- **THEN** the viewer is upgraded to the matching release or newer beside the
  framework

#### Scenario: The floor and the declared matching viewer agree

- **WHEN** the release facts declare the matching viewer version
- **THEN** the `viewer` and `web-snapshot` extras each floor at exactly that
  version, and a test fails naming the extra whose floor differs

#### Scenario: A user installs the mechanics extra

- **WHEN** `pip install "machinome[mechanics]"` resolves from published
  packages
- **THEN** the independent `machinome-mechanics` distribution is
  installed without the framework importing or re-exporting its helpers

#### Scenario: A reader asks for the studio extra before publication

- **WHEN** current 0.7 guidance shows `pip install "machinome[studio]"`
- **THEN** it also states that the installation cannot resolve from an index
  until Machinome Studio is published

