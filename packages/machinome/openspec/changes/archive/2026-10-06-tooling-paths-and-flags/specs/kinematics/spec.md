## ADDED Requirements

### Requirement: The parity fixture is regenerated from any checkout of the framework

The generator of the cross-runtime parity fixture,
`tools/generate_parity_fixture.py`, SHALL write the fixture to the path given
as its first argument. Given none, it SHALL write the fixture the viewer
repository commits, `machinome_viewer/widget/src/parity-fixture.json` in the
`machinome-viewer` checkout beside the framework's primary checkout, and SHALL
find that primary checkout through Git's common directory, so that the
primary checkout and every worktree of it resolve to the same file. When no
such checkout can be found — the framework checkout is not a Git checkout, or
no `machinome-viewer` checkout with that directory stands beside the primary
one — the generator SHALL refuse before building the fixture, naming the
directory it looked for and saying that the output path may be given as the
argument, and SHALL write nothing.

#### Scenario: Regenerating from a worktree

- **WHEN** a contributor runs the generator with no argument from a worktree
  of the framework under its primary checkout's `WTs/`
- **THEN** it writes `machinome_viewer/widget/src/parity-fixture.json` in the
  `machinome-viewer` checkout beside the primary checkout, not a path beside
  the worktree

#### Scenario: Regenerating from the primary checkout

- **WHEN** the generator is run with no argument from the primary checkout
- **THEN** it writes the same file a worktree of that checkout writes

#### Scenario: No viewer checkout beside the framework

- **WHEN** the generator is run with no argument and no `machinome-viewer`
  checkout stands beside the primary checkout, or the framework is not a Git
  checkout
- **THEN** it exits non-zero before building the fixture, naming the
  directory it looked for and the output argument, and writes nothing

#### Scenario: An explicit output path

- **WHEN** the generator is given an output path
- **THEN** it writes the fixture there, wherever the checkout stands
