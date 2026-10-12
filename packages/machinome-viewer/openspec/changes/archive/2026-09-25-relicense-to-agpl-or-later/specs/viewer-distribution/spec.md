## MODIFIED Requirements

### Requirement: The package is licensed and versioned as one

The distribution SHALL declare `AGPL-3.0-or-later`, and the bundle it carries
SHALL open with a banner naming that licence, the package version, the
declared viewer API version and the source repository, and retaining the
notices of the libraries it bundles. The Python package, the widget's
`package.json` and the changelog SHALL declare one version.

#### Scenario: A conveyed bundle names its source

- **WHEN** a maker publishes an export directory or a host serves the bundle
- **THEN** the bundle's first lines name AGPL-3.0-or-later, the version, the API
  version and the repository the source can be obtained from
