## MODIFIED Requirements

### Requirement: The tracked source set is unchanged

The system SHALL produce, for every node in a loaded tree, exactly the source
closure that `build-pipeline`'s Mtime-equality caching defines: the same set
of project-local files, the same `mtime_ns` derived from them, and therefore
the same artifact paths and the same up-to-date decisions.

Changing how the package of a file is looked up SHALL NOT change which files a
node tracks, in either direction. A file that contributes today SHALL still
contribute; a file that does not SHALL still not.

#### Scenario: A real tree is byte-for-byte the same

- **WHEN** a project of several hundred nodes is loaded and assembled under the
  indexed lookup and under a linear rescan of `sys.modules`
- **THEN** every node in both trees carries the same source closure, the same
  `mtime_ns`, and the same artifact path

#### Scenario: Relative imports still resolve

- **WHEN** a node's module reaches a sibling module through a relative import
- **THEN** that sibling is in the node's tracked source set, as it is today

#### Scenario: A file outside the project is still excluded

- **WHEN** a node's module imports a module that is not project-local
- **THEN** that module's file is absent from the node's tracked source set
