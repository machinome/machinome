## ADDED Requirements

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
