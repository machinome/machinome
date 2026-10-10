## ADDED Requirements

### Requirement: Documentation embeds through the Machinome directive

The Sphinx extension SHALL register `.. machinome::`, copy its support files
under a Machinome-named output resource directory, and resolve the installed
bundle through `machinome-viewer`. Current documentation SHALL use only that
directive.

#### Scenario: A documentation author embeds an export

- **WHEN** a page uses `.. machinome:: <export-dir>`
- **THEN** the built page embeds the export with the installed Machinome viewer
