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
failed`, continued by `, S skipped`, `, X expected failures` and
`, U unexpected successes` for each of those counts that is not zero, and
SHALL exit 1 when any test failed or any test succeeded unexpectedly, and 0
otherwise; `--failfast` stops at the first test that fails the run. A run in
which nothing was skipped, expected to fail, or unexpectedly successful
SHALL print that line with none of those continuations. Under the faceted
comparison kernel that summary line SHALL continue with
` (faceted kernel, volume epsilon E mm³)`, and the run SHALL announce the
kernel and epsilon on a line of its own before the first node is built; under
the exact kernel the run's output is unchanged.

#### Scenario: Failing contract fails the run

- **WHEN** any assertion raises across any instant
- **THEN** the summary counts the failure and the process exits 1

#### Scenario: A run whose only unusual results are skips exits 0

- **WHEN** a run's tests all pass except one that skipped itself
- **THEN** the summary reads one skipped test, counts it as neither passed
  nor failed, and the process exits 0

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
- **THEN** no kernel line is printed and, when no test was skipped,
  expected to fail, or unexpectedly successful, the summary line is exactly
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


## ADDED Requirements

### Requirement: A skipped test is not a failure

A test that declares itself inapplicable — by calling `skipTest(reason)` in
the test method or in its `setUp`, by raising the skip exception any other
way, or by carrying `unittest`'s skip decoration on the test method or on the
whole test class — SHALL be reported
as SKIPPED: neither passed nor failed, named with its reason, counted in the
summary's own skipped count, and unable on its own to make the run exit 1.

A skipped test SHALL be distinguishable from a passing and from a failing one
by the words the runner writes, not by colour alone, so a run captured to a
log or a pipe still says which tests were skipped.

The unit of a skip is the INSTANT at which it was declared. Under an
animation-instant decorator, a method runs once per declared instant, and an
instant that declares itself skipped SHALL be skipped alone: the remaining
instants still run, and the method's verdict follows them. A method whose
every instant skipped SHALL be reported as one skipped test; a method some of
whose instants skipped and whose remaining instants all passed SHALL be
reported as passed, saying how many instants it skipped.

When a test class is decorated as skipped, no test method of that class SHALL
run, and the class's own set-up SHALL NOT run either; each of its test methods
is counted once as skipped.

A skip SHALL NOT replace the report of a real failure: when one instant of a
method fails and another skips, the run reports the failure, with the failing
instant's traceback.

`--failfast` SHALL NOT stop on a skip, at either the instant or the test
level, because a skip is not a failure.

#### Scenario: A test that skips itself

- **WHEN** a test method calls `skipTest('no exact kernel here')` and every
  other test passes
- **THEN** the run names that test as skipped with its reason, counts it as
  neither passed nor failed, reports one skipped test in the summary, and
  exits 0

#### Scenario: A skip at one instant of a sweep

- **WHEN** a method decorated to run at several instants skips itself at one
  of them and passes at the others
- **THEN** the remaining instants still run, the method is reported as passed
  saying one instant was skipped, and the run exits 0

#### Scenario: Every instant of a sweep skips

- **WHEN** a method decorated to run at several instants skips itself at
  every instant
- **THEN** the method is reported as one skipped test, not as several

#### Scenario: A skip does not hide a failure in the same method

- **WHEN** a method fails at one instant and skips at a later one
- **THEN** the method is reported as failed, with the traceback of the
  failing instant and not of the skip, and the run exits 1

#### Scenario: A whole test class declared skipped

- **WHEN** a companion test class carries `unittest`'s skip decoration
- **THEN** none of its test method bodies runs, its class set-up does not
  run, each of its test methods is counted once as skipped, and the run
  exits 0

#### Scenario: A skip declared in set-up

- **WHEN** a test case's `setUp` calls `skipTest(reason)` before a test method
  runs
- **THEN** that method is reported as skipped with the reason, counted once,
  no instant of it runs, and the run continues with the next test and exits 0

#### Scenario: A skipped test in a log without colour

- **WHEN** a run whose output is captured to a file skips a test
- **THEN** the captured text says that test was skipped and gives its reason,
  without depending on colour

### Requirement: An expected failure is honoured and an unexpected success fails the run

A test method marked as expected to fail — `unittest`'s expected-failure
decoration — SHALL be reported as an EXPECTED FAILURE when it raises: neither
passed nor failed, counted in the summary's own expected-failure count,
unable on its own to make the run exit 1, and printed without the traceback a
real failure prints, because that failure is the declared outcome.

A test method marked as expected to fail that does NOT raise SHALL be
reported as an UNEXPECTED SUCCESS, counted in the summary's own
unexpected-success count, and SHALL make the run exit 1 — the marking is now
wrong, and a run must not stay green over a statement about the machine that
is no longer true.

Expectation is a property of the METHOD, not of an instant. A method marked
as expected to fail that is also decorated to run at several instants is an
expected failure when at least one of its instants raises, and an unexpected
success when none does; the run over the remaining instants is not abandoned
by the first raise.

A skip SHALL take precedence over the expectation: a method marked as
expected to fail whose every instant skipped is reported as skipped, not as
an expected failure and not as an unexpected success, which is what
`unittest` itself reports.

`--failfast` SHALL NOT stop on an expected failure, and SHALL stop on an
unexpected success, which is a failure of the run.

#### Scenario: A test expected to fail, that fails

- **WHEN** a test method marked as expected to fail raises an assertion error
- **THEN** the run names it an expected failure, prints no traceback for it,
  counts it as neither passed nor failed, reports one expected failure in the
  summary, and exits 0

#### Scenario: A test expected to fail, that passes

- **WHEN** a test method marked as expected to fail completes without raising
- **THEN** the run names it an unexpected success, reports one unexpected
  success in the summary, and exits 1

#### Scenario: A sweep expected to fail that raises at one instant

- **WHEN** a method marked as expected to fail is decorated to run at several
  instants and raises at one of them
- **THEN** every instant runs, the method is reported as one expected
  failure, and the run exits 0

#### Scenario: A sweep expected to fail that passes at every instant

- **WHEN** a method marked as expected to fail is decorated to run at several
  instants and raises at none of them
- **THEN** the method is reported as one unexpected success and the run
  exits 1

#### Scenario: A test expected to fail that skips instead

- **WHEN** a test method marked as expected to fail skips itself at every
  instant
- **THEN** it is reported as skipped, not as an expected failure and not as
  an unexpected success, and the run exits 0

#### Scenario: Failfast and an unexpected success

- **WHEN** `--failfast` is given and a test marked as expected to fail passes
- **THEN** the run stops there and exits 1
