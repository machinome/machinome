## RENAMED Requirements

- FROM: `### Requirement: The comparison kernels are documented`
- TO: `### Requirement: The comparison engines are documented`

## MODIFIED Requirements

### Requirement: Installation and dependency claims match released packaging

Requirement and installation statements in the documentation SHALL match the
released packaging: dependencies that are conditional in the release (such
as the OpenSCAD binary and the mesh engine on the mesh path) SHALL be
described as conditional with the condition named, hard dependencies (such
as molejo) SHALL NOT be described as optional or unpublished, and an upgrade
that requires reinstalling the environment SHALL be called out where an
existing user would look for it.

#### Scenario: An all-exact project

- **WHEN** a reader whose parts are all OCCT-backed reads the quickstart
- **THEN** they learn the OpenSCAD binary is needed only for the
  OpenSCAD-family and mesh paths, not for installing or using the
  framework

#### Scenario: Upgrading an existing environment

- **WHEN** a 0.5.x user consults the documentation before upgrading
- **THEN** they find the instruction to reinstall the environment and the
  reason the in-place upgrade fails

### Requirement: The comparison engines are documented

The how-to guide on running tests fast SHALL explain that a test run
compares on one of two engines: the B-rep engine,
the default and the one a release or CI run uses, and the mesh engine,
which answers every geometric question on the parts' meshes at tessellation
precision and is the one a developer selects for a fast loop. It SHALL state
how the engine is selected (`--brep` / `--mesh`, else
`SOLID_TEST_ENGINE`, else `brep`), that
 a checkout's ignored `.env` is where a
developer records the mesh choice so CI inherits nothing, what the volume
epsilon absorbs and that it exists only for the mesh engine, and that a
mesh run labels itself.

The same guide SHALL also explain the run's placement quantum: that the
verdict memo asks whether two comparisons are the same question, that the
relative placement deciding that is quantised to a grid so the float noise of
composing one rigid motion by two routes does not split a question in two,
that the quantum is selected by `--placement-quantum`, else
`SOLID_TEST_PLACEMENT_QUANTUM`, else the documented default, that `0` restores
the exact-bytes key, that it applies under both engines, and that it is a
statement about arithmetic noise and must stay far below the smallest
clearance the suite judges. It SHALL state that a run at a non-default quantum
says so on its summary line.

The same guide SHALL also explain the verdict store. It SHALL say:

- that every verdict a run decides is kept under the project's build
  directory, and served to a later run that asks the same question of the
  same state;
- that the state is the content of the compared parts' artifacts, a flexible
  part's bound values and specification, and the pair's quantised relative
  placement, so a rebuild reproducing the same artifacts or a moved project
  still reuses it;
- that a change to the framework or to an installed geometry kernel starts
  it afresh on its own;
- that it never changes a verdict;
- that `--no-verdict-store` or `SOLID_TEST_VERDICT_STORE=off` runs without
  it, and that such a run says so;
- that deleting the `.verdicts` directory is always safe.

The CLI page SHALL list the options under `machinome test` (`--brep`,
`--mesh`, `--volume-epsilon`, `--placement-quantum`, and `--verdict-store` /
`--no-verdict-store`) and the four environment variables. The changelog SHALL
record the capability.

#### Scenario: A developer learns how to run fast

- **WHEN** a reader whose suite is slow on B-rep solids reads the guide
- **THEN** they find the mesh engine, the `.env` line that selects it for
  their checkout, and the statement that CI keeps the B-rep engine

#### Scenario: A reader looks up the flags

- **WHEN** a reader looks up `machinome test` on the CLI page
- **THEN** they find `--brep`, `--mesh`, `--volume-epsilon`,
  `--placement-quantum`, `--verdict-store` / `--no-verdict-store`, and the four
  environment variables with their precedence

#### Scenario: A reader learns what the placement quantum decides

- **WHEN** a reader whose sweep re-runs booleans on parts that move together
  reads the guide
- **THEN** they find what the quantum merges, its default, that `0` restores
  the exact key, and that it is not a tolerance on any assertion

#### Scenario: A reader learns why a second run is fast

- **WHEN** a reader whose second test run finished in seconds, where the first
  took minutes, reads the guide
- **THEN** they find that verdicts are kept between runs and keyed on the
  state of their parts, that no verdict changes because of it, how to run
  without the store, and that the `.verdicts` directory may be deleted at any
  time
