## MODIFIED Requirements

### Requirement: The browser viewer is documented in the manual

The framework manual SHALL document the browser viewer, the package of the
distribution machinome-viewer installed by the `viewer` extra: three how-to
guides listed in the how-to part of the navigation, `howto/browser-viewer`
(inspect and operate a posed, running or clocked machine), `howto/share-an-export`
(publish an export, link a presentation, take a still) and
`howto/embed-the-viewer` (a working host page, its source included, and the
layouts); and a reference section, `reference/viewer/`, listed in the
reference part of the navigation, whose index names the distribution, its
install line, the viewer API through `|viewer_api|` and the document versions
through `|document_versions|`, followed by the mount, the viewer handle, the
layouts, running and clocked machines, the viewer command `machinome viewer`,
compatibility and troubleshooting. Every public mount, option and handle
member of the widget SHALL have its entry in that section. The command line
reference SHALL hold a section `machinome viewer` stating its report, its
verbs `describe`, `serve` and `capture` and every option of the command,
linking the viewer command's page; no current page SHALL spell the former
command `machinome-viewer` with a verb. The framework's viewer, embedding,
sharing and installation pages and the sibling-manuals page SHALL link those
pages inside the manual, and no page SHALL link a separate viewer manual.

#### Scenario: A maker needs to operate the viewer
- **WHEN** a maker reads the framework's viewer page
- **THEN** they can follow a link inside the manual to the guide to operating
  a machine in the viewer

#### Scenario: A host needs a browser API detail
- **WHEN** a host reads the framework's embedding page
- **THEN** they can follow a link inside the manual to the viewer's complete
  API reference and the working embedding example

#### Scenario: The viewer's reference is complete

- **WHEN** the widget's tests run from the repository
- **THEN** each public member of the viewer's handles and options and each
  mount of `MachinomeViewer` has its entry in the pages under
  `reference/viewer/`, and the viewer's tests find the `describe` example's
  version, API and document versions equal to the package's

#### Scenario: No page sends a reader to the separate viewer manual

- **WHEN** the manual's pages and the framework's README are read
- **THEN** none links `machinome-viewer.readthedocs.io`, and the release
  facts' viewer API and document versions equal the widget's declaration

#### Scenario: The viewer command is in the command line reference

- **WHEN** the command line reference is read
- **THEN** its section `machinome viewer` names the report, the three verbs
  and every option the command's parser declares, and links the viewer
  command's page, and the framework's tests fail naming any option missing

#### Scenario: No page spells the former command

- **WHEN** the manual's current pages are read, the changelog and the
  upgrading page excepted
- **THEN** none spells `machinome-viewer describe`, `machinome-viewer serve`
  or `machinome-viewer capture`
