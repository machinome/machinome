## MODIFIED Requirements

### Requirement: A successful build sweeps unreferenced artifacts

After a successful publication the system SHALL remove files in the build
directory that the current viewer snapshot does not reference. It SHALL NOT
remove:

- the snapshot;
- the error file;
- `.scad` inputs;
- `.brep` exact geometry;
- live render lock files;
- temporaries belonging to a build in progress;
- the test framework's verdict store, the directory `.verdicts` at the top of
  the build directory, together with everything in it.

The sweep SHALL be confined to the build directory.

The verdict store is spared by location rather than by reference. It is test
state, not a build artifact, and no published document names it. It is
written by test runs that may be in progress while a build publishes.

`.brep` artifacts are spared by kind rather than by reference, because no
published document names them. As with `.scad` inputs, a superseded one is
therefore not removed by the sweep; mtime-equality caching means a superseded
artifact is never read.

A **marking** artifact under the `markings` capability is spared by
**reference**, not by kind, because the published snapshot names it beside the
part's model. A marking still declared is therefore kept, and a marking
artifact whose declaration was deleted or renamed is removed by the next
successful publication, exactly as a renamed node's artifact is.

#### Scenario: A renamed node leaves nothing behind

- **WHEN** a node is renamed and the project is rebuilt successfully
- **THEN** the artifact under the old name is gone from the build directory and
  the artifact under the new name is present and referenced

#### Scenario: A failed build sweeps nothing

- **WHEN** a build fails
- **THEN** no artifact is removed from the build directory

#### Scenario: Exact geometry survives the sweep

- **WHEN** a build of exact nodes publishes successfully and sweeps
- **THEN** every `.brep` written for a current node is still present, though
  the published snapshot names none of them

#### Scenario: The verdict store survives the sweep

- **WHEN** a project whose build directory holds a verdict store is rebuilt
  and publishes successfully
- **THEN** the `.verdicts` directory and every file in it are still present,
  and the next test run is served from them

#### Scenario: A declared marking survives the sweep

- **WHEN** a project whose parts declare markings publishes successfully and
  sweeps
- **THEN** every marking artifact the snapshot names is still present

#### Scenario: A dropped marking leaves nothing behind

- **WHEN** a marking declaration is deleted and the project is rebuilt
  successfully
- **THEN** that marking's artifact is gone from the build directory and the
  part's own artifacts are untouched
