## ADDED Requirements

### Requirement: A source-bound leaf names its missing file

A leaf adapter whose part comes from a file outside Python — `StlNode`
(`stl_source`), `StepNode` (`step_source`), `JScadNode` (`jscad_source`) and
`OpenScadNode` (`scad_source`) — SHALL refuse to construct when the file it
declares is not there, and the refusal SHALL name the declaring class, the
attribute and the value declared on it, and the absolute path the framework
resolved that value to.

The refusal SHALL happen when the node is CONSTRUCTED: the same moment at
which a subclass declaring no source file at all is already refused, and the
moment at which the declaration can first be judged. A class body that writes
a child declaration constructs nothing, so declaring such a leaf inside
another node's body SHALL NOT itself fail; the failure arrives when the
parent is instantiated and realizes that child, before any geometry is read
and before any artifact is written.

A resolved path that exists but is not a regular file SHALL be refused in the
same way and SHALL say that it is not a file, rather than being handed to the
mesh or document reader.

This governs a declaration that was already wrong when the model was loaded.
It SHALL NOT change what happens to a source file that disappears after its
node was constructed: that remains a build failure raised when the node's
sources are read for freshness.

#### Scenario: A declared file that is not there

- **WHEN** a node whose adapter binds it to an external file is constructed,
  and the file that adapter's source attribute names does not exist
- **THEN** construction fails with an error naming the class, the source
  attribute and its declared value, and the absolute path resolved from it,
  and no artifact is written

#### Scenario: The failure arrives when the parent realizes the child

- **WHEN** an assembly's class body declares such a leaf as a child and the
  leaf's file is absent
- **THEN** importing the module holding that class body succeeds, and
  instantiating the assembly fails with that same error

#### Scenario: A declared source that is a directory

- **WHEN** the path a source attribute resolves to exists but is a directory
- **THEN** construction fails saying the path is not a file, naming the class
  and the attribute, rather than the mesh or document reader failing on it
  later

#### Scenario: A source removed after the node was constructed

- **WHEN** a node is constructed with its source file present and the file is
  removed before the build reads its sources for freshness
- **THEN** the build still fails on the missing source exactly as it does
  today; the construction-time check does not apply retroactively
