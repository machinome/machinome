## MODIFIED Requirements

### Requirement: The comparison kernels are documented

The how-to guide on running tests fast SHALL explain that a test run
compares on one of two kernels: the exact boundary-representation kernel,
the default and the one a release or CI run uses, and the faceted kernel,
which answers every geometric question on the parts' meshes at tessellation
precision and is the one a developer selects for a fast loop. It SHALL state
how the kernel is selected (`--exact` / `--faceted`, else
`SOLID_TEST_KERNEL`, else exact), that a checkout's ignored `.env` is where a
developer records the faceted choice so CI inherits nothing, what the volume
epsilon absorbs and that it exists only for the faceted kernel, and that a
faceted run labels itself.

The same guide SHALL also explain the run's placement quantum: that the
verdict memo asks whether two comparisons are the same question, that the
relative placement deciding that is quantised to a grid so the float noise of
composing one rigid motion by two routes does not split a question in two,
that the quantum is selected by `--placement-quantum`, else
`SOLID_TEST_PLACEMENT_QUANTUM`, else the documented default, that `0` restores
the exact-bytes key, that it applies under both kernels, and that it is a
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

The CLI page SHALL list the options under `machinome test` (`--exact`,
`--faceted`, `--volume-epsilon`, `--placement-quantum`, and `--verdict-store` /
`--no-verdict-store`) and the four environment variables. The changelog SHALL
record the capability.

#### Scenario: A developer learns how to run fast

- **WHEN** a reader whose suite is slow on exact solids reads the guide
- **THEN** they find the faceted kernel, the `.env` line that selects it for
  their checkout, and the statement that CI keeps the exact kernel

#### Scenario: A reader looks up the flags

- **WHEN** a reader looks up `machinome test` on the CLI page
- **THEN** they find `--exact`, `--faceted`, `--volume-epsilon`,
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
