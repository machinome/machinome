## ADDED Requirements

### Requirement: A failing method reports its first failing instant, by name

When a test method fails — at least one of its instants raises, and it is
not marked as expected to fail — the runner SHALL print the traceback of
the FIRST instant that raised, in the order the instants were declared,
and no other instant's. Every instant SHALL still run, as before, unless
`--failfast` stops the method at its first failing instant.

For a method that declares its instants with `@testing_instant` or
`@testing_steps`, the failure SHALL be reported on the method's line, in
words and not by colour alone, as `FAIL! at instant T`, where T is the
first failing instant written so that it can be given back to
`@testing_instant` to reproduce it exactly: an integer as written, any
other number in the shortest form that reads back as the same float. When
the method declares more than one instant, the line SHALL continue with
` (K of N instants failed)`, K the instants that raised and N the instants
declared, or, when `--failfast` stopped the method at its first failing
instant before its last, with ` (--failfast stopped the sweep at instant P
of N)`, P that instant's position among the N.

A method that declares no instant SHALL report its failure with `FAIL!`
alone, as before.

`FAIL!` SHALL remain the first word written after the instants' marks, so
a reader matching it on the method's line still finds it.

#### Scenario: A sweep that fails twice, differently

- **WHEN** a method decorated to run at instants `0`, `0.5` and `1` raises
  one assertion at `0` and a different exception at `1`
- **THEN** its line reads `FAIL! at instant 0 (2 of 3 instants failed)`,
  the traceback printed is the one raised at `0`, and the one raised at
  `1` is not printed

#### Scenario: One declared instant

- **WHEN** a method decorated `@testing_instant(0.5)` fails
- **THEN** its line reads `FAIL! at instant 0.5`, with no count

#### Scenario: An instant that is not a round number

- **WHEN** a method swept over `@testing_steps(49)` first fails at its
  second instant
- **THEN** the line names that instant as `0.020833333333333332`, the
  float the runner handed to the keyframe, not a rounded value

#### Scenario: Failfast stops a sweep

- **WHEN** `--failfast` is given and a method decorated to run at three
  instants fails at its first
- **THEN** no further instant runs and its line reads `FAIL! at instant 0
  (--failfast stopped the sweep at instant 1 of 3)`

#### Scenario: A method that declares no instant

- **WHEN** a method with no instant decorator fails
- **THEN** its line ends with `FAIL!`, exactly as before

### Requirement: An exception in set-up is an error, and the run goes on

An exception other than a skip raised by a test case's `setUp` SHALL be
reported as an ERROR of the method being set up: the method's line SHALL
say `ERROR! (setUp raised)`, the exception's traceback SHALL be printed,
no instant of the method SHALL run, and the case's `tearDown` SHALL NOT be
called for it. An exception other than a skip raised by a test case's
`setUpClass` SHALL be reported as an ERROR of each of that class's test
methods, each line saying `ERROR! (setUpClass raised)`, the traceback
printed once; none of the class's methods SHALL run, and its
`tearDownClass` SHALL NOT be called.

An ERROR is neither passed nor failed. Each errored method SHALL be
counted once as a test and once in the summary's own error count, and an
error SHALL make the run exit 1. After an error the run SHALL continue
with the next test, the next test case and the next node, and SHALL print
its summary line, unless `--failfast` stops it there.

An expected-failure marking SHALL NOT turn an error in set-up into an
expected failure: the marking is a statement about the method's own body,
which never ran.

A developer's quit from the debugger in set-up SHALL still end the run,
as it does from a test method.

#### Scenario: setUp raises

- **WHEN** a test case whose `setUp` raises a `RuntimeError` has two test
  methods, and a second test case bound to the same node has one passing
  method
- **THEN** both methods of the first case are reported `ERROR! (setUp
  raised)` with the traceback, neither runs, the second case's method runs
  and passes, the summary reads `3` tests, `1 passed, 0 failed, 2 errors`,
  and the run exits 1

#### Scenario: setUpClass raises

- **WHEN** a test case whose `setUpClass` raises has one test method, and
  a second test case has one passing method
- **THEN** the first method is reported `ERROR! (setUpClass raised)` and
  does not run, the second runs and passes, the summary reads `1 passed,
  0 failed, 1 error`, and the run exits 1

#### Scenario: A class whose set-up raises, with several methods

- **WHEN** a test case's `setUpClass` raises and the case has two test
  methods
- **THEN** each method is counted once as a test and once as an error,
  the traceback is printed once, and `tearDownClass` is not called

#### Scenario: Failfast and an error

- **WHEN** `--failfast` is given and a test case's `setUp` raises
- **THEN** the run stops after reporting the first method's error, prints
  its summary line, and exits 1

#### Scenario: A method expected to fail whose set-up raises

- **WHEN** a method marked as expected to fail belongs to a test case
  whose `setUp` raises
- **THEN** the method is reported as an error, not as an expected failure,
  and the run exits 1

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
failed`, continued by `, E errors` (`, 1 error` for one), `, S skipped`,
`, X expected failures` and `, U unexpected successes`, in that order, for
each of those counts that is not zero, and SHALL exit 1 when any test
failed, any test errored, or any test succeeded unexpectedly, and 0
otherwise; `--failfast` stops at the first test that fails the run, an
error included. A run in which nothing errored, was skipped, expected to
fail, or unexpectedly successful SHALL print that line with none of those
continuations. In a run on the
mesh engine that summary line SHALL continue with
` (mesh engine, volume epsilon E mm³)`, and the run SHALL announce the
engine and epsilon on a line of its own before the first node is built; on
the B-rep engine the run's output is unchanged.

#### Scenario: Failing contract fails the run

- **WHEN** any assertion raises across any instant
- **THEN** the summary counts the failure and the process exits 1

#### Scenario: A run whose only unusual results are skips exits 0

- **WHEN** a run's tests all pass except one that skipped itself
- **THEN** the summary reads one skipped test, counts it as neither passed
  nor failed, and the process exits 0

#### Scenario: An error is counted beside the failures

- **WHEN** a run has two passing tests, one failing test, one test whose
  set-up raised and one skipped test
- **THEN** the summary line reads `Ran 5 tests in X seconds: 2 passed, 1
  failed, 1 error, 1 skipped` and the process exits 1

#### Scenario: A test sweep does not block a rebuild

- **WHEN** a test run has finished building the node and is running test methods
- **THEN** another process can acquire the project build lock and rebuild the
  same project

#### Scenario: A file reference runs every node in the file

- **WHEN** a user runs `machinome test windmill/model.py` on a file defining two
  node classes, each with a companion test case declaring it
- **THEN** both nodes are built and the test methods of both test cases are
  counted in the summary

#### Scenario: A sub-assembly no test declares is not built

- **WHEN** a user runs `machinome test boat/robot.py` on a file defining a machine
  and a sub-assembly that cannot be built on its own, and the companion's
  test cases declare only the machine
- **THEN** the machine is built and tested, the sub-assembly is never built,
  and the run passes

#### Scenario: A file with no companion builds every node

- **WHEN** a user runs `machinome test boat/hull.py` on a file defining two node
  classes and no companion test file
- **THEN** both nodes are built and the run reports zero tests

#### Scenario: A mesh run is labelled as one

- **WHEN** `machinome test --mesh --volume-epsilon 0.5` runs a project
- **THEN** a line before the first build names the mesh engine and the
  epsilon, and the summary line ends with `(mesh engine, volume epsilon
  0.5 mm³)`

#### Scenario: A B-rep run reads as it always did

- **WHEN** `machinome test` runs without an engine selection and without
  `SOLID_TEST_ENGINE` in the environment
- **THEN** no engine line is printed and, when no test errored, was
  skipped, expected to fail, or unexpectedly successful, the summary line
  is exactly `Ran N tests in X seconds: P passed, F failed`

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

### Requirement: A skipped test is not a failure

A test that declares itself inapplicable — by calling `skipTest(reason)` in
the test method or in its `setUp`, by raising the skip exception from its
test case's `setUpClass` or any other way, or by carrying `unittest`'s skip
decoration on the test method or on the whole test class — SHALL be reported
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
is counted once as skipped. When a test class's `setUpClass` raises the skip
exception, no test method of that class SHALL run either, and each of its
test methods is counted once as skipped with the exception's reason, exactly
as for the decoration.

A skip SHALL NOT replace the report of a real failure: when one instant of a
method fails and another skips, the run reports the failure, with the failing
instant's traceback.

`--failfast` SHALL NOT stop on a skip, at either the instant or the test
level, because a skip is not a failure.

#### Scenario: A test that skips itself

- **WHEN** a test method calls `skipTest('no B-rep engine here')` and every
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

#### Scenario: A skip declared in class set-up

- **WHEN** a companion test class's `setUpClass` raises the skip exception
  with a reason, and it has two test methods
- **THEN** neither method body runs, each is counted once as skipped with
  that reason, the run continues with the next test case, and exits 0

#### Scenario: A skip declared in set-up

- **WHEN** a test case's `setUp` calls `skipTest(reason)` before a test method
  runs
- **THEN** that method is reported as skipped with the reason, counted once,
  no instant of it runs, and the run continues with the next test and exits 0

#### Scenario: A skipped test in a log without colour

- **WHEN** a run whose output is captured to a file skips a test
- **THEN** the captured text says that test was skipped and gives its reason,
  without depending on colour
