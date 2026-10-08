## MODIFIED Requirements

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
