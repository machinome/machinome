## MODIFIED Requirements

### Requirement: Materialized artifact

`StlNode.present()`, the leaf base's, SHALL always materialize the node's
own STL artifact from the source file when that artifact is not up to date —
selected body extracted, `adjust` applied, written in binary form, and
mtime-stamped to the node's source mtime — and SHALL return the same
presentation, an import of that artifact, whether or not it was rebuilt. There is no
import-in-place path: downstream consumers (fusion, piece identity,
export, the viewer) SHALL see only the node's own artifact. Producing
the artifact SHALL NOT require OpenSCAD or any external tool.

#### Scenario: A current artifact is not rewritten

- **WHEN** `present()` runs on an `StlNode` whose artifact is up to
  date
- **THEN** the source STL is not re-read for materialization, no
  artifact is written, and the returned presentation is unchanged

#### Scenario: The leaf builds without OpenSCAD

- **WHEN** a project whose leaves are all `StlNode`s is built with no
  `openscad` on the PATH and no fusion in the tree
- **THEN** every leaf's STL artifact is produced and the build succeeds
