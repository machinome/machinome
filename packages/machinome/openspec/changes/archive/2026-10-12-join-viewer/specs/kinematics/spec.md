## MODIFIED Requirements

### Requirement: The parity fixture is regenerated from any checkout of the framework

The generator of the cross-runtime parity fixture,
`tools/generate_parity_fixture.py`, SHALL write the fixture to the path given
as its first argument. Given none, it SHALL write the fixture the browser
viewer's widget commits in the same checkout of the repository,
`packages/machinome-viewer/machinome/viewer/web/widget/src/parity-fixture.json`,
found from the framework's directory without Git, so that a worktree writes
its own viewer's fixture and the primary checkout its own (change
`join-viewer`). When the checkout holds no such directory, the generator
SHALL refuse before building the fixture, naming the directory it looked for
and saying that the output path may be given as the argument, and SHALL write
nothing.

#### Scenario: Regenerating from a worktree

- **WHEN** a contributor runs the generator with no argument from a worktree
  of the repository
- **THEN** it writes the viewer package's
  `machinome/viewer/web/widget/src/parity-fixture.json` in that worktree, not a
  file of another checkout

#### Scenario: Regenerating from the primary checkout

- **WHEN** the generator is run with no argument from the primary checkout
- **THEN** it writes the primary checkout's own viewer fixture, at the same
  path relative to the repository's root as a worktree's

#### Scenario: No viewer checkout beside the framework

- **WHEN** the generator is run with no argument from a framework directory
  with no `packages/machinome-viewer/` beside it
- **THEN** it exits non-zero before building the fixture, naming the
  directory it looked for and the output argument, and writes nothing

#### Scenario: An explicit output path

- **WHEN** the generator is given an output path
- **THEN** it writes the fixture there, wherever the checkout stands
