## MODIFIED Requirements

### Requirement: Test runner lifecycle

The system SHALL build each node under test before testing it (load,
`set_keyframe(0)`, render, assemble, `build_stls`), then run all
`test_`-prefixed methods found on the node and on every companion test case
bound to it. The build SHALL hold the project build lock and SHALL release it
before the first test method runs, so a test sweep never blocks another build of
the same project.

When the reference names a single node, the run covers that node and the test
cases bound to it. When the reference names a file, the run covers the node
classes defined in that file that its companion test cases declare, each once
and in the file's definition order, and every test case in the companion; a
node class no test case declares SHALL NOT be built. When the companion
declares no node — there is no companion, or the file defines one node class
and its cases leave `node` implicit — the run covers every node class defined
in the file. A test case beside a file defining several node classes that
does not declare its node SHALL fail the run, naming the case and the
candidate classes, before any node is built. No test case in a companion
file SHALL be excluded from a run that covers its node.

Each method runs once per declared testing instant (default `[0]`), with the
keyframe set per instant, a colored pass/fail dot printed per instant, and each
child's operations checkpoint restored between instants and between tests. A
restored child SHALL be left standing at the coordinates it holds: after the
child's operation list is restored, every joint that child declares is placed
again from that child's own coordinate values, and a joint whose coordinates
are not all bound is cleared. So a test never measures a child whose placement
and whose coordinates disagree — including a child a previous test posed
through a running simulation, which owns the coordinates the runner's snapshot
does not. This applies to the CHILDREN of the node under test and to them
alone: the node under test is not checkpointed and a joint it declares itself
is neither restored nor re-placed. A child that declares no joint is restored
exactly as before, and an operation a test leaked — appended or inserted
anywhere in the list — is reverted as before. A re-placement the restore makes
SHALL NOT outlive the coordinate value that states it: if the next instant's
enumeration leaves that coordinate unbound, the child stands at rest.
The run SHALL print `Ran N tests in X seconds: P passed, F
failed` and exit 1 if any failed; `--failfast` stops at the first failure.
Under the faceted comparison kernel that summary line SHALL continue with
` (faceted kernel, volume epsilon E mm³)`, and the run SHALL announce the
kernel and epsilon on a line of its own before the first node is built; under
the exact kernel the run's output is unchanged.

#### Scenario: Failing contract fails the run

- **WHEN** any assertion raises across any instant
- **THEN** the summary counts the failure and the process exits 1

#### Scenario: A test sweep does not block a rebuild

- **WHEN** a test run has finished building the node and is running test methods
- **THEN** another process can acquire the project build lock and rebuild the
  same project

#### Scenario: A file reference runs every node in the file

- **WHEN** a user runs `solid test windmill/model.py` on a file defining two
  node classes, each with a companion test case declaring it
- **THEN** both nodes are built and the test methods of both test cases are
  counted in the summary

#### Scenario: A sub-assembly no test declares is not built

- **WHEN** a user runs `solid test boat/robot.py` on a file defining a machine
  and a sub-assembly that cannot be built on its own, and the companion's
  test cases declare only the machine
- **THEN** the machine is built and tested, the sub-assembly is never built,
  and the run passes

#### Scenario: A file with no companion builds every node

- **WHEN** a user runs `solid test boat/hull.py` on a file defining two node
  classes and no companion test file
- **THEN** both nodes are built and the run reports zero tests

#### Scenario: A faceted run is labelled as one

- **WHEN** `solid test --faceted --volume-epsilon 0.5` runs a project
- **THEN** a line before the first build names the faceted kernel and the
  epsilon, and the summary line ends with `(faceted kernel, volume epsilon
  0.5 mm³)`

#### Scenario: An exact run reads as it always did

- **WHEN** `solid test` runs without a kernel selection and without
  `SOLID_TEST_KERNEL` in the environment
- **THEN** no kernel line is printed and the summary line is exactly
  `Ran N tests in X seconds: P passed, F failed`

#### Scenario: A test after a scenario measures the machine the scenario left

- **WHEN** a scenario test steps a running simulation over the node the runner
  built, and a later test of the same run reads a root-level leaf that owns a
  joint
- **THEN** that leaf carries exactly one placement from its joint, stating the
  coordinate the leaf holds

#### Scenario: A checkpoint taken while a run's placement stands

- **WHEN** the node is posed by a running simulation before a test's
  checkpoint is taken, and a later test poses it again
- **THEN** the leaf carries one placement, not two, and does not stand at
  twice its coordinate's travel

#### Scenario: A leaked operation is still reverted

- **WHEN** a test inserts an operation anywhere in a child's operation list
- **THEN** the next instant and the next test see that operation gone, exactly
  as they did before the restore re-placed anything

#### Scenario: An untimed project's tests are unchanged

- **WHEN** a project whose root declares no time base is run, its joints bound
  by relations as the enumeration solves them
- **THEN** every test sees the placement it saw before this change, and the
  run's output is unchanged

#### Scenario: A guarded binding leaves the body at rest on the instant it skips

- **WHEN** an untimed project's root binds a root-level leaf's joint only
  under a guard, and a test method runs over two instants, the first of which
  binds it and the second of which does not
- **THEN** the second instant measures the leaf at rest, carrying no operation
  from that joint, exactly as it did before the restore re-placed anything

#### Scenario: A joint on the node under test is left alone

- **WHEN** the node under test declares a joint of its own and a test poses it
- **THEN** the restore neither reverts nor re-places that joint's operations,
  because the node under test is not among the children the runner
  checkpoints
