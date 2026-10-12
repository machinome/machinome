## MODIFIED Requirements

### Requirement: A framework finds the installed viewer through one entry point

The distribution SHALL register the `solid_node.viewer` entry point group
with one entry, `bundle`, resolving to a function that returns the absolute
`path` of the installed bundle, the absolute `index` of the standalone
export page, the integer `apiVersion` the widget declares, the list of
document schema versions the widget renders as `documentVersions`, and the
package `version`. Resolving it SHALL import only the standard library — no
browser bundle, no web framework — and SHALL raise, with the remedy, when
the installation carries no built bundle, so a caller never receives a path
that does not exist. `solid-node-viewer describe` SHALL print the same
mapping as one JSON object on standard output, or print nothing there,
report the remedy on standard error and exit non-zero when there is no
bundle.

`apiVersion` and `documentVersions` SHALL come from the widget package's
own single declaration of each, the same declaration the bundle is built
from, so the answer a framework reads and the versions the bundle actually
refuses can never disagree.

#### Scenario: A framework resolves the viewer without importing it

- **WHEN** solid-node loads the `solid_node.viewer` entry point and calls it
- **THEN** it obtains an existing absolute bundle path, the export page and
  the declared API version, having imported nothing of the viewer's
  rendering, serving or capturing code

#### Scenario: A program asks the command line

- **WHEN** a program runs `solid-node-viewer describe` against an
  installation with a built bundle
- **THEN** it parses one JSON object carrying the path, index, API version
  and version, and the process exits zero

#### Scenario: An installation without a built bundle

- **WHEN** the entry point or the command is asked in a source checkout that
  has not built the widget
- **THEN** the entry point raises and the command exits non-zero, both naming
  where a built bundle comes from, and standard output carries no result

#### Scenario: A producer asks which documents this installation reads

- **WHEN** a framework resolves the entry point, or runs
  `solid-node-viewer describe`, before publishing a document
- **THEN** the answer carries the list of document schema versions this
  build renders, and that list is the same one the bundle refuses an
  unlisted version by
