# product-identity Specification

## Purpose

Define the canonical customer-facing and machine-readable identities for
Machinome Studio while preserving mechanical shop vocabulary as a separate
domain language.
## Requirements
### Requirement: The product exposes one canonical identity
The system SHALL identify the customer-facing product as `Machinome Studio` and
SHALL use `machinome-studio` wherever distribution, service, agent,
project-configuration, configuration-directory or temporary-resource syntax
requires a machine-readable identifier. Its Python package SHALL be
`machinome.studio` and its command `machinome studio`, a command of
`machinome`. Current material SHALL describe *machinome* as the
source code of one machine and, collectively, the body of source code for
machines, and SHALL identify the Machinome organization as the home for machine
source repositories, resources, and the framework.

Historical records that described LibreSolid Studio or solid-node when those
were their names SHALL retain that wording. Current indexes and synthesis SHALL
make the transition legible without rewriting those records.

#### Scenario: A customer views product identity
- **WHEN** a customer opens the browser workspace or reads current product
  metadata and documentation
- **THEN** the product name is presented as `Machinome Studio`

#### Scenario: An integration addresses the product
- **WHEN** an integration reads package metadata, project configuration, or a
  product-derived runtime identifier
- **THEN** the identifier is `machinome-studio` or is prefixed by
  `machinome-studio-`, the package imports as `machinome.studio`, and the
  command is `machinome studio`

#### Scenario: A reader follows the rename history
- **WHEN** a reader opens a past ADR, archived change, or release record that
  predates the rename
- **THEN** the record retains the name used at that time and current guidance
  explains that Machinome Studio is its continuation

### Requirement: Mechanical shop vocabulary remains distinct from the product name
The system SHALL retain shop-floor, shop-root, shop-worktree, and related shop
terms when they describe the mechanical workflow rather than the product
identity.

#### Scenario: Current guidance describes a workflow concept
- **WHEN** current product guidance refers to the floor, repository lane, role
  workflow, or worktree by its shop-domain name
- **THEN** that domain term remains accurate without presenting `shop` as the
  product's customer-facing name

### Requirement: The browser surface wears the Machinome identity
The browser surface SHALL carry the Machinome visual identity as the
identity's application guide prescribes for a product. The title bar of
the hub and of every project workspace SHALL show the identity's outlined
wordmark with a plain-text `Studio` qualifier beside it in the same
colour, and that lockup SHALL name the product `Machinome Studio` to
assistive technology. The interface SHALL be set in Space Grotesk and its
code, paths, values and annotations in IBM Plex Mono, both bundled with
the studio beside their licence notices. The identity's logo-only font
SHALL NOT be used for text. The identity release SHALL be carried intact
as one versioned directory that this repository does not edit. The tab
SHALL carry the studio's own favicon: the identity's white symbol, its
geometry unchanged, on a black plate, distinct from the identity's orange
favicon.

The identity's orange is not an interface colour: interface accents remain
the reference design's.

#### Scenario: A maker opens the hub
- **WHEN** the maker opens the hub or a project workspace
- **THEN** the title bar shows the wordmark with its `Studio` qualifier, the product is named `Machinome Studio` to assistive technology, the page is set in Space Grotesk with technical text in IBM Plex Mono, and the tab shows the white symbol on a black plate

#### Scenario: The identity release is revised
- **WHEN** a revised identity is adopted
- **THEN** it arrives as a new versioned directory beside the current one, and no file of the current release is changed in this repository

