# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

import io
import os
import tempfile
import unittest
from argparse import Namespace
from contextlib import redirect_stdout, redirect_stderr
from unittest import TestCase
from unittest.mock import patch
from trimesh.creation import box
from machinome.manager.test import Test as Runner, StopTestRun
from machinome import test as framework
from machinome.motion.ports import get_coordinate
from machinome.node.base import AbstractBaseNode
from machinome.node.operations import Translation
from machinome.simulation import Sim
from machinome.simulation.enumeration import bind_declared_defaults

from .running_project.machine import Conditional, Floating, Train, TrainBody


def with_instants(*values):
    """Stand-in for machinome.test.testing_steps/testing_instant: tags
    a plain function with the instants Test.run_test iterates over."""
    def decorator(method):
        method.testing_instants = list(values)
        return method
    return decorator


class FakeNode:
    """A minimal stand-in for a real Node instance, providing only what
    Test.run_class_tests/run_test touch: `children` (iterated by
    save/restore_children_checkpoints), `set_keyframe`, and plain
    `test_*` methods discovered through dir()/getattr.
    """
    children = ()

    def __init__(self):
        self.calls = []
        self.last_instant = None

    def set_keyframe(self, instant):
        self.last_instant = instant


class AlwaysPassesNode(FakeNode):
    @with_instants(0, 1, 2)
    def test_multi_instant(self):
        self.calls.append(self.last_instant)


class FirstInstantFailsNode(FakeNode):
    @with_instants(0, 1, 2)
    def test_multi_instant(self):
        self.calls.append(self.last_instant)
        if self.last_instant == 0:
            raise AssertionError("boom")


class FirstTestFailsNode(FakeNode):
    # dir() visits these in alphabetical order, so test_a_fails always
    # runs before test_b_should_not_run.
    def test_a_fails(self):
        self.calls.append('a')
        raise AssertionError("boom")

    def test_b_should_not_run(self):
        self.calls.append('b')


def run_class_tests_capturing_stdout(runner, node):
    # Only run_tests() catches StopTestRun (the signal a failfast failure
    # raises to abort the remaining run); direct run_class_tests() callers,
    # like these instants-loop-focused tests, must do so themselves.
    with redirect_stdout(io.StringIO()):
        try:
            runner.run_class_tests(node, node)
        except StopTestRun:
            pass


def run_class_tests_capturing_output(runner, klass, node):
    """Like run_class_tests_capturing_stdout, but returns the captured
    text and accepts `klass` and `node` separately -- needed when the
    methods under test live on a companion test case bound to a
    different node object (the setUp-skip scenarios)."""
    out = io.StringIO()
    with redirect_stdout(out):
        try:
            runner.run_class_tests(klass, node)
        except StopTestRun:
            pass
    return out.getvalue()


class SkipTestMixin:
    """A tiny stand-in for unittest.TestCase.skipTest: raises the same
    exception the real method raises, without pulling in the rest of
    TestCase -- FakeNode deliberately isn't one."""

    def skipTest(self, reason=None):
        raise unittest.SkipTest(reason)


class SkipsOnlyInstantNode(SkipTestMixin, FakeNode):
    def test_skip(self):
        self.skipTest('the exact kernel is not available here')


class ExpectedFailureRaisesNode(FakeNode):
    @unittest.expectedFailure
    def test_expected_fail(self):
        raise AssertionError('the known kernel gap')


class ExpectedFailurePassesNode(FakeNode):
    @unittest.expectedFailure
    def test_expected_fail(self):
        pass


class SkipMiddleInstantNode(SkipTestMixin, FakeNode):
    @with_instants(0, 1, 2)
    def test_sweep(self):
        self.calls.append(self.last_instant)
        if self.last_instant == 1:
            self.skipTest('nothing to compare at mid-sweep')


class SkipEveryInstantNode(SkipTestMixin, FakeNode):
    @with_instants(0, 1, 2)
    def test_sweep(self):
        self.calls.append(self.last_instant)
        self.skipTest('never applicable')


class FailThenSkipNode(SkipTestMixin, FakeNode):
    @with_instants(0, 1, 2)
    def test_sweep(self):
        self.calls.append(self.last_instant)
        if self.last_instant == 0:
            raise AssertionError('a real regression')
        if self.last_instant == 2:
            self.skipTest('skipped at instant 2')


class ExpectedFailureSweepNode(FakeNode):
    @unittest.expectedFailure
    @with_instants(0, 1, 2)
    def test_sweep(self):
        self.calls.append(self.last_instant)
        if self.last_instant == 1:
            raise AssertionError('the known kernel gap')


class ExpectedFailureAllSkipNode(SkipTestMixin, FakeNode):
    @unittest.expectedFailure
    @with_instants(0, 1, 2)
    def test_sweep(self):
        self.calls.append(self.last_instant)
        self.skipTest('never applicable')


@unittest.skip('methods should not run')
class SkippedWholeClassNode(FakeNode):
    setup_called = False

    @classmethod
    def setUpClass(cls):
        cls.setup_called = True

    def test_a(self):
        self.calls.append('a')

    def test_b(self):
        self.calls.append('b')


class SetupSkipsCase(SkipTestMixin):
    """A companion test case whose setUp skips before any instant runs
    (reviewer's note 1): both test methods must be individually skipped,
    and the run continues from one to the next."""

    def __init__(self):
        self.calls = []

    def setUp(self):
        self.calls.append('setup')
        self.skipTest('the exact kernel is not available here')

    def tearDown(self):
        self.calls.append('teardown')

    def test_a(self):
        self.calls.append('a')

    def test_b(self):
        self.calls.append('b')


class SetupRaisesCase:
    """A companion whose setUp raises something other than SkipTest: the
    run aborts exactly as it does today (reviewer's note 1) -- a
    green-both-ways guard, not a RED case."""

    def setUp(self):
        raise RuntimeError('setup blew up')

    def test_a(self):
        pass


class FakeChild:
    """A minimal stand-in for a child node: `restore_children_checkpoints`
    only reads and reassigns `operations`, and `re_place_declared_joints`
    finds no joints declared on a plain class."""

    def __init__(self):
        self.operations = []


class ChildOperationsGrowThenSkipNode(SkipTestMixin, FakeNode):
    """A sweep whose instant 0 leaks an operation onto a child and whose
    instant 1 skips: instant 2 must still see a restored child
    (reviewer's note 3) -- restore_children_checkpoints already runs
    after every instant unconditionally, skipped ones included, so this
    is a guard rather than a RED case."""

    def __init__(self, child):
        super().__init__()
        self.child = child
        self.instant2_operations = None

    @property
    def children(self):
        return [self.child]

    @with_instants(0, 1, 2)
    def test_sweep(self):
        if self.last_instant == 0:
            self.child.operations.append('leaked')
        elif self.last_instant == 1:
            self.skipTest('mid-sweep')
        else:
            self.instant2_operations = list(self.child.operations)


class FailfastSkipSweepNode(SkipTestMixin, FakeNode):
    @with_instants(0, 1, 2)
    def test_sweep(self):
        self.calls.append(self.last_instant)
        if self.last_instant == 1:
            self.skipTest('mid-sweep')


class FailfastExpectedFailureSweepThenPassNode(FakeNode):
    # dir() visits these in alphabetical order, so test_a_expected_fail
    # always runs before test_b_passes.
    @unittest.expectedFailure
    @with_instants(0, 1, 2)
    def test_a_expected_fail(self):
        self.calls.append(('a', self.last_instant))
        if self.last_instant == 1:
            raise AssertionError('the known kernel gap')

    def test_b_passes(self):
        self.calls.append('b')


class FailfastUnexpectedSuccessNode(FakeNode):
    @unittest.expectedFailure
    def test_a_unexpectedly_passes(self):
        self.calls.append('a')

    def test_b_should_not_run(self):
        self.calls.append('b')


class FailfastInstantsLoopTest(TestCase):
    """Regression tests for B6: `if self.failfast: break` sat outside the
    `except` block, breaking the instants loop unconditionally -- even
    when the instant just passed."""

    def test_all_passing_instants_run_even_with_failfast(self):
        node = AlwaysPassesNode()
        runner = Runner()
        runner.failfast = True
        runner.test_case = None

        run_class_tests_capturing_stdout(runner, node)

        self.assertEqual(node.calls, [0, 1, 2])
        self.assertEqual(runner.num_passed, 1)
        self.assertEqual(runner.num_failed, 0)

    def test_failfast_stops_instants_loop_after_first_failure(self):
        node = FirstInstantFailsNode()
        runner = Runner()
        runner.failfast = True
        runner.test_case = None

        run_class_tests_capturing_stdout(runner, node)

        self.assertEqual(node.calls, [0])
        self.assertEqual(runner.num_failed, 1)

    def test_without_failfast_all_instants_run_despite_failure(self):
        node = FirstInstantFailsNode()
        runner = Runner()
        runner.failfast = False
        runner.test_case = None

        run_class_tests_capturing_stdout(runner, node)

        self.assertEqual(node.calls, [0, 1, 2])
        self.assertEqual(runner.num_failed, 1)


class FailfastAbortsRunTest(TestCase):
    """Regression tests for B6: --failfast's help text promises to "stop
    the test run on the first error", but the old `break` only escaped
    the instants loop, so the run continued into the next test_* method.
    """

    def test_failfast_skips_remaining_tests_after_a_failure(self):
        node = FirstTestFailsNode()
        runner = Runner()
        runner.failfast = True
        runner.test_case = None
        runner.node = node

        out = io.StringIO()
        with redirect_stdout(out):
            runner.run_tests()

        self.assertEqual(node.calls, ['a'])
        self.assertEqual(runner.num_failed, 1)
        self.assertEqual(runner.num_passed, 0)
        # The summary line must still print after an aborted run.
        self.assertIn("Ran 1 tests", out.getvalue())
        self.assertIn("1 failed", out.getvalue())

    def test_without_failfast_all_tests_run(self):
        node = FirstTestFailsNode()
        runner = Runner()
        runner.failfast = False
        runner.test_case = None
        runner.node = node

        out = io.StringIO()
        with redirect_stdout(out):
            runner.run_tests()

        self.assertEqual(node.calls, ['a', 'b'])
        self.assertEqual(runner.num_failed, 1)
        self.assertEqual(runner.num_passed, 1)
        self.assertIn("Ran 2 tests", out.getvalue())


class SkipAndExpectedFailureTest(TestCase):
    """workflow/warts.md, Internal-Cycloidal-Actuator finding: the
    instants loop and run_class_tests have no skip and no
    expected-failure concept -- `unittest.SkipTest` is caught by the
    bare `except Exception` and counted as a failure, and
    `@unittest.expectedFailure` is read nowhere. Each method here is
    RED against the unchanged runner for the reason recorded in
    tasks.md 1.1/1.2; evidence.md's probes are the end-to-end
    reproduction this file exercises unit by unit."""

    def test_a_skip_is_reported_skipped_not_failed(self):
        node = SkipsOnlyInstantNode()
        runner = Runner()
        runner.test_case = None

        text = run_class_tests_capturing_output(runner, node, node)

        self.assertEqual(runner.num_failed, 0)
        self.assertEqual(getattr(runner, 'num_skipped', 0), 1)
        self.assertIn(' skipped', text)
        self.assertIn('the exact kernel is not available here', text)

    def test_an_expected_failure_that_raises_is_not_a_failure(self):
        node = ExpectedFailureRaisesNode()
        runner = Runner()
        runner.test_case = None

        text = run_class_tests_capturing_output(runner, node, node)

        self.assertEqual(runner.num_failed, 0)
        self.assertEqual(getattr(runner, 'num_expected_failures', 0), 1)
        self.assertNotIn('Traceback', text)
        self.assertNotIn('the known kernel gap', text)

    def test_an_expected_failure_that_passes_is_an_unexpected_success(self):
        node = ExpectedFailurePassesNode()
        runner = Runner()
        runner.test_case = None

        text = run_class_tests_capturing_output(runner, node, node)

        self.assertEqual(runner.num_passed, 0)
        self.assertEqual(getattr(runner, 'num_unexpected_successes', 0), 1)
        self.assertIn('UNEXPECTED SUCCESS', text)

    def test_a_skip_at_one_instant_does_not_fail_the_sweep(self):
        node = SkipMiddleInstantNode()
        runner = Runner()
        runner.test_case = None

        text = run_class_tests_capturing_output(runner, node, node)

        self.assertEqual(node.calls, [0, 1, 2])
        self.assertEqual(runner.num_passed, 1)
        self.assertEqual(runner.num_failed, 0)
        self.assertIn('1 of 3 instants skipped', text)

    def test_a_sweep_that_skips_at_every_instant_is_one_skipped_test(self):
        node = SkipEveryInstantNode()
        runner = Runner()
        runner.test_case = None

        run_class_tests_capturing_output(runner, node, node)

        self.assertEqual(getattr(runner, 'num_skipped', 0), 1)
        self.assertEqual(runner.num_passed, 0)
        self.assertEqual(runner.num_failed, 0)

    def test_a_skip_does_not_overwrite_a_real_failures_traceback(self):
        node = FailThenSkipNode()
        runner = Runner()
        runner.test_case = None

        text = run_class_tests_capturing_output(runner, node, node)

        self.assertEqual(runner.num_failed, 1)
        self.assertIn('a real regression', text)
        self.assertNotIn('SkipTest', text)

    def test_a_marked_methods_sweep_runs_every_instant(self):
        node = ExpectedFailureSweepNode()
        runner = Runner()
        runner.test_case = None

        run_class_tests_capturing_output(runner, node, node)

        self.assertEqual(node.calls, [0, 1, 2])
        self.assertEqual(getattr(runner, 'num_expected_failures', 0), 1)
        self.assertEqual(runner.num_failed, 0)

    def test_a_skip_wins_over_the_expectation(self):
        node = ExpectedFailureAllSkipNode()
        runner = Runner()
        runner.test_case = None

        run_class_tests_capturing_output(runner, node, node)

        self.assertEqual(getattr(runner, 'num_skipped', 0), 1)
        self.assertEqual(getattr(runner, 'num_expected_failures', 0), 0)
        self.assertEqual(getattr(runner, 'num_unexpected_successes', 0), 0)

    def test_a_class_level_skip_runs_no_body_and_no_setup(self):
        node = SkippedWholeClassNode()
        runner = Runner()
        runner.test_case = None

        run_class_tests_capturing_output(runner, node, node)

        self.assertEqual(node.calls, [])
        self.assertFalse(SkippedWholeClassNode.setup_called)
        self.assertEqual(getattr(runner, 'num_skipped', 0), 2)

    def test_a_skip_declared_in_setup_skips_the_method_and_continues(self):
        case = SetupSkipsCase()
        node = FakeNode()
        runner = Runner()
        runner.test_case = case
        runner.node = node

        try:
            text = run_class_tests_capturing_output(runner, case, node)
        except unittest.SkipTest:
            self.fail(
                'a SkipTest raised from setUp escaped run_class_tests '
                "instead of being reported as a skipped test "
                "(reviewer's note 1)")

        self.assertEqual(
            case.calls, ['setup', 'teardown', 'setup', 'teardown'])
        self.assertEqual(getattr(runner, 'num_skipped', 0), 2)
        self.assertEqual(runner.num_failed, 0)
        self.assertIn('the exact kernel is not available here', text)

    def test_a_non_skip_setup_error_still_propagates(self):
        case = SetupRaisesCase()
        node = FakeNode()
        runner = Runner()
        runner.test_case = case
        runner.node = node

        with self.assertRaises(RuntimeError):
            runner.run_class_tests(case, node)

    def test_a_skip_between_instants_still_restores_the_children(self):
        # reviewer's note 3: a skip at instant 1 after an operation was
        # added at instant 0 must not leak into instant 2.
        child = FakeChild()
        node = ChildOperationsGrowThenSkipNode(child)
        runner = Runner()
        runner.test_case = None

        run_class_tests_capturing_output(runner, node, node)

        self.assertEqual(node.instant2_operations, [])

    def test_failfast_does_not_break_the_sweep_on_a_skip(self):
        node = FailfastSkipSweepNode()
        runner = Runner()
        runner.test_case = None
        runner.node = node
        runner.failfast = True

        with redirect_stdout(io.StringIO()):
            runner.run_tests()

        self.assertEqual(node.calls, [0, 1, 2])
        self.assertEqual(runner.num_passed, 1)
        self.assertEqual(runner.num_failed, 0)

    def test_failfast_does_not_break_on_a_marked_methods_raise(self):
        node = FailfastExpectedFailureSweepThenPassNode()
        runner = Runner()
        runner.test_case = None
        runner.node = node
        runner.failfast = True

        with redirect_stdout(io.StringIO()):
            runner.run_tests()

        self.assertEqual(
            node.calls, [('a', 0), ('a', 1), ('a', 2), 'b'])
        self.assertEqual(getattr(runner, 'num_expected_failures', 0), 1)
        self.assertEqual(runner.num_failed, 0)

    def test_failfast_stops_on_an_unexpected_success(self):
        node = FailfastUnexpectedSuccessNode()
        runner = Runner()
        runner.test_case = None
        runner.node = node
        runner.failfast = True

        with redirect_stdout(io.StringIO()):
            runner.run_tests()

        self.assertEqual(node.calls, ['a'])
        self.assertEqual(getattr(runner, 'num_unexpected_successes', 0), 1)


class ReportSummaryLineTest(TestCase):
    """report()'s summary line: unchanged when nothing unusual happened
    -- the ADR-090 discipline for this output -- and, when something
    did, the three new counts appended before the kernel/quantum
    note."""

    def test_default_run_reports_todays_line_unchanged(self):
        runner = Runner()
        runner.num_tests = 3
        runner.num_passed = 3
        runner.num_failed = 0

        out = io.StringIO()
        with redirect_stdout(out):
            runner.report(1.23)

        self.assertIn(
            'Ran 3 tests in 1.23 seconds: 3 passed, 0 failed\n',
            out.getvalue())

    def test_nonzero_counts_are_appended_before_the_kernel_note(self):
        runner = Runner()
        runner.num_tests = 8
        runner.num_passed = 4
        runner.num_failed = 0
        runner.num_skipped = 1
        runner.num_expected_failures = 2
        runner.num_unexpected_successes = 1
        runner.policy = framework.ComparisonPolicy('faceted', 0.0)

        out = io.StringIO()
        with redirect_stdout(out):
            runner.report(1.0)

        self.assertIn(
            'Ran 8 tests in 1.00 seconds: 4 passed, 0 failed, '
            '1 skipped, 2 expected failures, 1 unexpected success '
            '(faceted kernel, volume epsilon 0 mm³)',
            out.getvalue())


class InstrumentedChild:
    """A minimal stand-in for a Node instance for restore_children_checkpoints:
    reuses the *real* AbstractBaseNode.save_checkpoint/restore_checkpoint and
    the real `mesh` property getter (instrumented only to count accesses),
    so the test exercises the actual checkpoint/mesh semantics rather than a
    reimplementation of them.
    """

    def __init__(self, stl_file):
        self.stl_file = stl_file
        self.operations = []
        self.checkpoint = None
        self.mesh_access_count = 0

    save_checkpoint = AbstractBaseNode.save_checkpoint
    restore_checkpoint = AbstractBaseNode.restore_checkpoint
    base_mesh = AbstractBaseNode.base_mesh

    @property
    def mesh(self):
        self.mesh_access_count += 1
        return AbstractBaseNode.mesh.fget(self)


class FakeParent:
    def __init__(self, children):
        self.children = children


class RestoreChildrenCheckpointsTest(TestCase):
    """The runner holds its own snapshot of each child's operations
    (a test calling save_checkpoint() on a node cannot clobber the
    restore point — B9), restores by content rather than truncation,
    and never touches `mesh` while restoring (B8: mutating the fresh
    trimesh that `mesh` builds from disk was a discarded no-op).
    """

    def setUp(self):
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        self.stl_path = os.path.join(tmpdir.name, 'child.stl')
        box((1, 1, 1)).export(self.stl_path)

    def test_restore_reverts_operations_and_mesh_reflects_restored_state(self):
        child = InstrumentedChild(self.stl_path)
        runner = Runner()
        runner.save_children_checkpoints(FakeParent(children=[child]))
        child.operations.append(Translation([5, 0, 0], node=None))

        # Sanity check: the added operation actually moved the mesh.
        translated_center = list(child.mesh.center_mass)
        self.assertNotAlmostEqual(translated_center[0], 0.0)

        runner.restore_children_checkpoints(FakeParent(children=[child]))

        self.assertEqual(child.operations, [])
        restored_center = list(child.mesh.center_mass)
        for actual in restored_center:
            self.assertAlmostEqual(actual, 0.0)

    def test_clobbered_node_checkpoint_cannot_move_the_restore_point(self):
        child = InstrumentedChild(self.stl_path)
        runner = Runner()
        runner.save_children_checkpoints(FakeParent(children=[child]))

        # A test leaks an operation and THEN calls save_checkpoint():
        # a runner trusting the node's own checkpoint index would now
        # restore to a state that includes the leak.
        child.operations.append(Translation([5, 0, 0], node=None))
        child.save_checkpoint()

        runner.restore_children_checkpoints(FakeParent(children=[child]))

        self.assertEqual(child.operations, [])

    def test_restore_reverts_inserted_operations_too(self):
        child = InstrumentedChild(self.stl_path)
        placement = Translation([1, 0, 0], node=None)
        child.operations.append(placement)
        runner = Runner()
        runner.save_children_checkpoints(FakeParent(children=[child]))

        # Perturbations are INSERTED before a placement, not appended;
        # truncating to a saved length would discard the wrong one.
        child.operations.insert(0, Translation([5, 0, 0], node=None))

        runner.restore_children_checkpoints(FakeParent(children=[child]))

        self.assertEqual(child.operations, [placement])

    def test_restore_does_not_access_mesh_property(self):
        # The B8 implementation called operation.mesh(child.mesh) once
        # per discarded operation -- an extra STL load + transform whose
        # result was thrown away immediately. Restoring should never
        # need to touch `mesh` at all.
        child = InstrumentedChild(self.stl_path)
        runner = Runner()
        runner.save_children_checkpoints(FakeParent(children=[child]))
        child.operations.append(Translation([5, 0, 0], node=None))

        runner.restore_children_checkpoints(FakeParent(children=[child]))

        self.assertEqual(child.mesh_access_count, 0)


def built(klass):
    """The rest-render build sequence `evidence/probe_checkpoint.py` and
    `evidence/probe_conditional.py` use, off the public API: bind every
    declared default, render at instant 0, and prepare the tree the way
    the build/test loader does before handing it to the runner."""
    node = klass()
    bind_declared_defaults(node)
    node.set_keyframe(0)
    node._prepare()
    return node


def motion_count(node):
    return len([operation for operation in node.operations
               if getattr(operation, '_motion', False)])


def travel_of(node):
    """The travel every motion operation on `node` states, added up --
    `evidence/bench/test_machine.py`'s `placement()`."""
    total = 0.0
    for operation in node.operations:
        if getattr(operation, '_motion', False):
            total += float(operation.serialized[1][0])
    return total


class RestoreChildrenCheckpointsJointTest(TestCase):
    """`evidence.md`'s reproduction, driven through the runner's own
    `save_children_checkpoints`/`restore_children_checkpoints`, off a
    real running root: a checkpoint saved and restored around a joint's
    placement must leave a CHILD standing at the coordinates it holds,
    never twice its travel and never at rest while its coordinate reads
    otherwise."""

    def test_a_running_roots_checkpoint_restore_does_not_double_the_slide(self):
        # evidence.md §1: doubled, 12.0 and 0.0, for a coordinate
        # reading 0.0.
        root = built(Train)
        runner = Runner()

        sim = Sim(root, 0.1)
        sim.move('lever', to=120.0, duration=0.2)
        sim.run(0.2)                                # a Sim poses the tree

        runner.save_children_checkpoints(root)        # the checkpoint is taken

        Sim(root, 0.1)                                # a second Sim poses it

        runner.restore_children_checkpoints(root)      # the checkpoint is restored

        Sim(root, 0.1)                                # a third Sim poses it

        self.assertEqual(motion_count(root.slide), 1)
        self.assertAlmostEqual(
            travel_of(root.slide),
            get_coordinate(root.slide, 'travel')._value)

    def test_a_running_roots_geometry_is_not_lost_after_the_next_keyframe(self):
        # evidence.md §7 (`BenchGeometry`): the checkpoint held the
        # build's TAGGED operation; `set_keyframe`'s sweep removes it,
        # and nothing re-places it because a running root's own
        # coordinate is not re-solved by the enumeration.
        root = built(Train)
        runner = Runner()

        runner.save_children_checkpoints(root)   # what the runner saves
                                                  # before every test

        sim = Sim(root, 0.1)
        sim.move('lever', to=120.0, duration=0.2)
        sim.run(0.2)                             # a Sim poses the tree

        runner.restore_children_checkpoints(root)  # the checkpoint is restored
        root.set_keyframe(0)                       # and set_keyframe(0) runs

        self.assertEqual(motion_count(root.slide), 1)
        self.assertAlmostEqual(
            travel_of(root.slide),
            get_coordinate(root.slide, 'travel')._value)

    def test_a_frees_whole_run_is_not_doubled_by_the_restore(self):
        # evidence.md §3: a `Free`'s one binding places FOUR operations;
        # the restore must not leave two runs of four standing.
        root = built(Floating)
        runner = Runner()

        sim = Sim(root, 0.1)
        sim.move('rise', to=6.0, duration=0.2)
        sim.run(0.2)

        runner.save_children_checkpoints(root)
        Sim(root, 0.1)
        runner.restore_children_checkpoints(root)
        Sim(root, 0.1)

        self.assertEqual(motion_count(root.floater), 4)

    def test_a_guarded_bindings_re_place_does_not_outlive_its_value(self):
        # revision 1's Finding A (evidence.md §A1/§A2/§A4): GREEN on the
        # unchanged framework, RED once the restore re-places from the
        # coordinate (task 3.1) and before `clear_solved` drops the
        # motion with the value (task 4.0).
        root = built(Conditional)
        runner = Runner()

        runner.save_children_checkpoints(root)

        root.set_keyframe(0)                     # instant 0: the guard binds
        runner.restore_children_checkpoints(root)  # cleanup between instants

        root.set_keyframe(1)                     # instant 1: the guard does
                                                  # not bind -- the test
                                                  # method's own assertion
                                                  # runs here, before this
                                                  # instant's own restore

        self.assertEqual(motion_count(root.gate), 0)
        self.assertIsNone(get_coordinate(root.gate, 'travel')._value)


class RestoreChildrenCheckpointsControlTest(TestCase):
    """The green-before-and-after controls: what the restore must go on
    doing exactly as it did (`evidence.md` §4 and the existing insertion
    coverage, extended to a child that also owns a joint)."""

    def test_an_untimed_root_reports_the_same_placement_throughout(self):
        # evidence.md §4: untouched under a keyframe-only test, because
        # every placement is TAGGED and a wholesale restore cannot
        # strand one the next render does not already drop.
        node = built(TrainBody)
        runner = Runner()
        before = travel_of(node.slide)

        for _ in range(3):
            runner.save_children_checkpoints(node)
            node.set_keyframe(0)
            self.assertEqual(motion_count(node.slide), 1)
            self.assertAlmostEqual(travel_of(node.slide), before)
            runner.restore_children_checkpoints(node)
            self.assertEqual(motion_count(node.slide), 1)
            self.assertAlmostEqual(travel_of(node.slide), before)

    def test_a_leaked_operation_is_reverted_on_a_child_that_also_owns_a_joint(self):
        node = built(TrainBody)
        runner = Runner()
        runner.save_children_checkpoints(node)

        leaked = Translation([5, 0, 0], node=None)
        node.slide.operations.insert(0, leaked)

        runner.restore_children_checkpoints(node)

        self.assertNotIn(leaked, node.slide.operations)
        self.assertEqual(motion_count(node.slide), 1)
        self.assertAlmostEqual(
            travel_of(node.slide),
            get_coordinate(node.slide, 'travel')._value)

    def test_a_child_declaring_no_joint_is_restored_unchanged(self):
        node = built(TrainBody)
        runner = Runner()
        runner.save_children_checkpoints(node)
        before = list(node.wheel.operations)

        node.wheel.operations.append(Translation([1, 0, 0], node=None))
        runner.restore_children_checkpoints(node)

        self.assertEqual(node.wheel.operations, before)

    def test_a_joint_on_the_node_under_test_itself_is_left_alone(self):
        # The runner checkpoints `node.children`, never the node under
        # test -- a joint the root declares on itself is neither
        # reverted nor re-placed.
        node = built(TrainBody)
        runner = Runner()
        node.spindle = 30.0
        runner.save_children_checkpoints(node)

        node.spindle = 60.0
        runner.restore_children_checkpoints(node)

        self.assertEqual(get_coordinate(node, 'spindle')._value, 60.0)


class ResolvePathMappingTest(TestCase):
    """`machinome test` is routinely handed the TEST file instead of the
    node file it exercises: `root/test_gear.py` instead of `root/gear.py`,
    or `root/test.py` instead of `root/__init__.py`. resolve_path() maps
    it back to the node file (the mirror image of loader.load_test's
    node->test mapping), so the runner proceeds exactly as if the node
    file had been given (skill-repo improvements.md #5)."""

    def setUp(self):
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        self.dir = tmpdir.name

    def touch(self, name):
        path = os.path.join(self.dir, name)
        open(path, 'w').close()
        return path

    def test_maps_test_prefixed_file_to_its_node_file(self):
        self.touch('gear.py')
        test_path = self.touch('test_gear.py')
        runner = Runner()

        self.assertEqual(
            runner.resolve_path(test_path),
            os.path.join(self.dir, 'gear.py'),
        )

    def test_maps_bare_test_file_to_init_file(self):
        self.touch('__init__.py')
        test_path = self.touch('test.py')
        runner = Runner()

        self.assertEqual(
            runner.resolve_path(test_path),
            os.path.join(self.dir, '__init__.py'),
        )

    def test_ordinary_node_path_passes_through_unchanged(self):
        node_path = self.touch('gear.py')
        runner = Runner()

        self.assertEqual(runner.resolve_path(node_path), node_path)

    def test_missing_mapped_node_file_exits_with_clear_error(self):
        # test_gear.py exists, but its sibling gear.py does not.
        test_path = self.touch('test_gear.py')
        expected_node_path = os.path.join(self.dir, 'gear.py')
        runner = Runner()

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as ctx:
                runner.resolve_path(test_path)

        self.assertEqual(ctx.exception.code, 1)
        message = stderr.getvalue()
        self.assertIn(expected_node_path, message)
        # A single clear line, never a bare TypeError traceback.
        self.assertNotIn('Traceback', message)

    def test_missing_mapped_init_file_exits_with_clear_error(self):
        test_path = self.touch('test.py')
        expected_node_path = os.path.join(self.dir, '__init__.py')
        runner = Runner()

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as ctx:
                runner.resolve_path(test_path)

        self.assertEqual(ctx.exception.code, 1)
        self.assertIn(expected_node_path, stderr.getvalue())


class NoNodeClassInModuleTest(TestCase):
    """A module with no AbstractBaseNode subclass defined in it -- the
    case when a stray file, or (before this fix) a TEST file, is handed
    to `machinome test` -- must fail with a clear one-line error instead of
    the opaque `TypeError: 'NoneType' object is not callable` that
    calling the loader's None straight away used to produce."""

    def setUp(self):
        fixture_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'meta_project')
        fd, self.path = tempfile.mkstemp(
            suffix='.py', prefix='no_node_class_', dir=fixture_dir)
        os.close(fd)
        with open(self.path, 'w') as f:
            f.write("# fixture: deliberately defines no node class\n"
                     "VALUE = 1\n")
        self.addCleanup(os.remove, self.path)
        self.relative_path = os.path.relpath(self.path)

    def test_build_node_fails_clearly_instead_of_crashing(self):
        runner = Runner()

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as ctx:
                runner.build_node(self.relative_path)

        self.assertEqual(ctx.exception.code, 1)
        message = stderr.getvalue()
        self.assertIn(self.relative_path, message)
        self.assertNotIn('Traceback', message)


class MultiTestCaseFixture(TestCase):
    """Shared scratch-project setup for the companion TestCase binding
    tests below (tasks 4.1-4.3): a real, tiny, temp-dir project with its
    own manifest, built and rendered through openscad exactly as `solid
    test` runs a maker's project -- not stubbed, because binding is
    decided by real class identity (`declared is klass`) and a mock node
    cannot stand in for that."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = self.tmp.name
        os.mkdir(os.path.join(self.root, 'boat'))
        open(os.path.join(self.root, 'boat', '__init__.py'), 'w').close()
        with open(os.path.join(self.root, 'pyproject.toml'), 'w') as stream:
            stream.write(
                '[tool.machinome]\nmodel = "boat.windmill:Windmill"\n')
        # Other test modules in this suite set SOLID_BUILD_DIR at import
        # time (some to an absolute path elsewhere in the repo); a build
        # driven from this scratch project must publish into ITS OWN
        # _build, not one left behind by an unrelated module.
        environment = patch.dict(os.environ)
        environment.start()
        self.addCleanup(environment.stop)
        os.environ.pop('SOLID_BUILD_DIR', None)

    def write(self, relative, content):
        path = os.path.join(self.root, relative)
        with open(path, 'w') as stream:
            stream.write(content)
        return path

    def run_solid_test(self, path, failfast=False):
        """Drive Runner().handle() exactly as the CLI does, capturing
        stdout/stderr and turning a raised SystemExit into (code, out,
        err) instead of letting it propagate -- a passing run never
        calls sys.exit, so code is 0 in that case."""
        stdout, stderr = io.StringIO(), io.StringIO()
        args = Namespace(path=path, failfast=failfast)
        code = 0
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                Runner().handle(args)
            except SystemExit as exc:
                code = exc.code
        return code, stdout.getvalue(), stderr.getvalue()


SKIP_ONLY_SOURCE = '''from machinome.node import Solid2Node
from solid2 import cube


class Widget(Solid2Node):
    def render(self):
        return cube(1, center=True)
'''

SKIP_ONLY_TEST_SOURCE = '''from machinome.test import TestCase
from .widget import Widget


class WidgetTest(TestCase):
    node = Widget

    def test_builds(self):
        self.assertIsNotNone(self.node.mesh)

    def test_skips(self):
        self.skipTest('the exact kernel is not available here')
'''

UNEXPECTED_SUCCESS_SOURCE = '''from machinome.node import Solid2Node
from solid2 import cube


class Gadget(Solid2Node):
    def render(self):
        return cube(1, center=True)
'''

UNEXPECTED_SUCCESS_TEST_SOURCE = '''import unittest
from machinome.test import TestCase
from .gadget import Gadget


class GadgetTest(TestCase):
    node = Gadget

    @unittest.expectedFailure
    def test_marked_but_passes(self):
        self.assertIsNotNone(self.node.mesh)
'''


class UnusualResultExitCodeTest(MultiTestCaseFixture):
    """ADR-117: the exit-code contract moves in both directions -- a run
    whose only unusual result is a skip must not fail the run, and a run
    containing an unexpected success must (`manager/test.py:179-180`)."""

    def test_a_run_with_only_a_skip_exits_zero(self):
        node_path = self.write('boat/widget.py', SKIP_ONLY_SOURCE)
        self.write('boat/test_widget.py', SKIP_ONLY_TEST_SOURCE)

        code, stdout, stderr = self.run_solid_test(node_path)

        self.assertEqual(code, 0, stderr)
        self.assertIn('1 skipped', stdout)

    def test_a_run_with_an_unexpected_success_exits_one(self):
        node_path = self.write('boat/gadget.py', UNEXPECTED_SUCCESS_SOURCE)
        self.write('boat/test_gadget.py', UNEXPECTED_SUCCESS_TEST_SOURCE)

        code, stdout, stderr = self.run_solid_test(node_path)

        self.assertEqual(code, 1, stderr)
        self.assertIn('1 unexpected success', stdout)


WINDMILL_SOURCE = '''from machinome.node import Solid2Node
from solid2 import cube


class Windmill(Solid2Node):
    def render(self):
        return cube(1, center=True)


class Sail(Solid2Node):
    def render(self):
        return cube(1, center=True)
'''

WINDMILL_TEST_SOURCE = '''from machinome.test import TestCase
from .windmill import Windmill, Sail


class WindmillTest(TestCase):
    node = Windmill

    def test_windmill_builds(self):
        self.assertIsNotNone(self.node.mesh)


class SailTest(TestCase):
    node = Sail

    def test_sail_builds(self):
        self.assertIsNotNone(self.node.mesh)
'''


class CompanionMultipleTestCasesRunTest(MultiTestCaseFixture):
    """Task 4.1, and the spec's 'Several test cases in one companion
    file' scenario: before this cycle the loader returned only the
    first TestCase defined in a companion file (`candidates[0][1]`) --
    a second TestCase in the same file never ran, and the run still
    reported success. The proposal's own words: a silently unrun test
    is worse than a wrongly loaded node, because the wrong node is at
    least visible on screen and the missing test is visible nowhere.
    Each TestCase here declares the node it exercises, and both must
    run, each bound to the one it declared."""

    def test_both_test_cases_in_the_companion_file_run(self):
        node_path = self.write('boat/windmill.py', WINDMILL_SOURCE)
        self.write('boat/test_windmill.py', WINDMILL_TEST_SOURCE)

        code, stdout, stderr = self.run_solid_test(node_path)

        self.assertEqual(code, 0, stderr)
        self.assertIn('WindmillTest.test_windmill_builds', stdout)
        self.assertIn('SailTest.test_sail_builds', stdout)
        self.assertIn('Ran 2 tests', stdout)
        self.assertIn('2 passed, 0 failed', stdout)


HULL_SOURCE = '''from machinome.node import Solid2Node
from solid2 import cube


class Hull(Solid2Node):
    def render(self):
        return cube(1, center=True)


class Deck(Solid2Node):
    def render(self):
        return cube(1, center=True)
'''

HULL_TEST_UNDECLARED_SOURCE = '''from machinome.test import TestCase


class HullTest(TestCase):
    def test_never_runs(self):
        pass
'''


class UndeclaredTestCaseInMultiNodeModuleTest(MultiTestCaseFixture):
    """Task 4.2, failure branch: a TestCase with no `node = <Class>`
    declaration, next to a module defining several node classes, has no
    way to say which one it binds to. The run must fail loudly, naming
    the test case and every candidate node class -- never silently
    skip it and never silently guess one."""

    def test_undeclared_case_fails_the_run_naming_case_and_candidates(self):
        node_path = self.write('boat/hull.py', HULL_SOURCE)
        self.write('boat/test_hull.py', HULL_TEST_UNDECLARED_SOURCE)

        code, stdout, stderr = self.run_solid_test(node_path)

        self.assertEqual(code, 1)
        self.assertIn('HullTest', stderr)
        self.assertIn('Hull', stderr)
        self.assertIn('Deck', stderr)
        self.assertIn('must declare node', stderr)
        # Never silently skipped: the run must abort before any summary
        # -- in particular never a summary claiming everything passed.
        self.assertNotIn('passed', stdout)


MAST_SOURCE = '''from machinome.node import Solid2Node
from solid2 import cube


class Mast(Solid2Node):
    def render(self):
        return cube(1, center=True)
'''

MAST_TEST_SOURCE = '''from machinome.test import TestCase


class MastTest(TestCase):
    def test_mast_builds(self):
        self.assertIsNotNone(self.node.mesh)
        # The snake_case alias TestCase.set_node derives from the class
        # name is unaffected by whether `node` was declared or implied.
        self.assertIsNotNone(self.mast.mesh)
'''


class UndeclaredTestCaseBesideSingleNodeModuleTest(MultiTestCaseFixture):
    """Task 4.3: every project that predates this cycle has exactly one
    node class per test file and never declared `node = ...` -- that
    majority case must keep working unchanged. An undeclared TestCase
    beside a single-node module binds to that module's one node class
    implicitly, with no error and no behaviour change."""

    def test_undeclared_case_still_binds_and_runs(self):
        node_path = self.write('boat/mast.py', MAST_SOURCE)
        self.write('boat/test_mast.py', MAST_TEST_SOURCE)

        code, stdout, stderr = self.run_solid_test(node_path)

        self.assertEqual(code, 0, stderr)
        self.assertIn('MastTest.test_mast_builds', stdout)
        self.assertIn('Ran 1 tests', stdout)
        self.assertIn('1 passed, 0 failed', stdout)


class ComparisonKernelSelectionTest(TestCase):
    """The kernel a run compares on is a property of the run, resolved
    once from the flags, then the environment, then the exact default --
    and refused loudly when the pieces do not fit together."""

    def tearDown(self):
        framework.set_comparison_policy(None)

    def parser(self):
        import argparse
        parser = argparse.ArgumentParser()
        Runner().add_arguments(parser)
        return parser

    def test_exact_and_faceted_are_mutually_exclusive(self):
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                self.parser().parse_args(['--exact', '--faceted'])

    def test_flags_parse_into_a_kernel_and_an_epsilon(self):
        args = self.parser().parse_args(['--faceted', '--volume-epsilon', '0.5'])
        self.assertEqual((args.kernel, args.volume_epsilon), ('faceted', 0.5))
        args = self.parser().parse_args([])
        self.assertEqual((args.kernel, args.volume_epsilon), (None, None))

    def test_the_default_is_the_exact_kernel(self):
        policy = framework.resolve_comparison_policy(environ={})
        self.assertEqual(policy, ('exact', 0.0,
                                  framework.DEFAULT_PLACEMENT_QUANTUM))

    def test_faceted_without_an_epsilon_is_strict(self):
        policy = framework.resolve_comparison_policy('faceted', environ={})
        self.assertEqual(policy, ('faceted', 0.0,
                                  framework.DEFAULT_PLACEMENT_QUANTUM))

    def test_the_environment_selects_the_faceted_kernel(self):
        policy = framework.resolve_comparison_policy(
            environ={'SOLID_TEST_KERNEL': 'faceted',
                     'SOLID_TEST_VOLUME_EPSILON': '0.25'})
        self.assertEqual(policy, ('faceted', 0.25,
                                  framework.DEFAULT_PLACEMENT_QUANTUM))

    def test_a_flag_beats_the_environment(self):
        policy = framework.resolve_comparison_policy(
            'exact', environ={'SOLID_TEST_KERNEL': 'faceted',
                              'SOLID_TEST_VOLUME_EPSILON': '0.25'})
        self.assertEqual(policy, ('exact', 0.0,
                                  framework.DEFAULT_PLACEMENT_QUANTUM))

    def test_an_unknown_kernel_name_is_refused_naming_the_variable(self):
        with self.assertRaisesRegex(
                ValueError, r"SOLID_TEST_KERNEL.*'exact'.*'faceted'.*fast"):
            framework.resolve_comparison_policy(
                environ={'SOLID_TEST_KERNEL': 'fast'})

    def test_a_negative_epsilon_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'negative'):
            framework.resolve_comparison_policy(
                'faceted', -1.0, environ={})
        with self.assertRaisesRegex(ValueError, 'negative'):
            framework.resolve_comparison_policy(
                environ={'SOLID_TEST_KERNEL': 'faceted',
                         'SOLID_TEST_VOLUME_EPSILON': '-2'})

    def test_a_non_numeric_environment_epsilon_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'SOLID_TEST_VOLUME_EPSILON'):
            framework.resolve_comparison_policy(
                'faceted', environ={'SOLID_TEST_VOLUME_EPSILON': 'tiny'})

    def test_an_epsilon_offered_to_the_exact_kernel_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'nothing.*absorb'):
            framework.resolve_comparison_policy('exact', 0.5, environ={})
        with self.assertRaisesRegex(ValueError, 'nothing.*absorb'):
            framework.resolve_comparison_policy(None, 0.5, environ={})

    def test_the_environment_epsilon_is_not_read_by_the_exact_kernel(self):
        policy = framework.resolve_comparison_policy(
            environ={'SOLID_TEST_VOLUME_EPSILON': 'tiny'})
        self.assertEqual(policy, ('exact', 0.0,
                                  framework.DEFAULT_PLACEMENT_QUANTUM))

    def test_a_two_argument_construction_means_the_default_quantum(self):
        # The seven positional two-argument ComparisonPolicy(...) sites in
        # machinome/test.py, machinome/manager/test.py and this repo's
        # own tests are none of them edited to pass a quantum (design.md
        # §6); this is what makes that mean "at the default quantum".
        self.assertEqual(
            framework.ComparisonPolicy('exact', 0.0).placement_quantum,
            framework.DEFAULT_PLACEMENT_QUANTUM)

    def test_the_placement_quantum_flag_parses(self):
        args = self.parser().parse_args(['--placement-quantum', '1e-6'])
        self.assertEqual(args.placement_quantum, 1e-6)
        args = self.parser().parse_args([])
        self.assertIsNone(args.placement_quantum)

    def test_the_placement_quantum_is_not_in_the_kernel_group(self):
        args = self.parser().parse_args(
            ['--exact', '--placement-quantum', '1e-6'])
        self.assertEqual((args.kernel, args.placement_quantum),
                         ('exact', 1e-6))

    def test_the_default_placement_quantum(self):
        policy = framework.resolve_comparison_policy(environ={})
        self.assertEqual(policy.placement_quantum,
                         framework.DEFAULT_PLACEMENT_QUANTUM)

    def test_the_environment_selects_a_placement_quantum(self):
        policy = framework.resolve_comparison_policy(
            environ={'SOLID_TEST_PLACEMENT_QUANTUM': '1e-6'})
        self.assertEqual(policy.placement_quantum, 1e-6)

    def test_a_placement_quantum_flag_beats_the_environment(self):
        policy = framework.resolve_comparison_policy(
            placement_quantum=0,
            environ={'SOLID_TEST_PLACEMENT_QUANTUM': '1e-6'})
        self.assertEqual(policy.placement_quantum, 0.0)

    def test_a_zero_placement_quantum_is_the_exact_bytes_key(self):
        policy = framework.resolve_comparison_policy(
            placement_quantum=0, environ={})
        self.assertEqual(policy.placement_quantum, 0.0)

    def test_the_exact_kernel_accepts_a_placement_quantum(self):
        # Unlike --volume-epsilon, refused by the exact kernel.
        policy = framework.resolve_comparison_policy(
            'exact', placement_quantum=1e-6, environ={})
        self.assertEqual(policy, ('exact', 0.0, 1e-6))

    def test_the_environment_quantum_is_read_under_both_kernels(self):
        exact_policy = framework.resolve_comparison_policy(
            environ={'SOLID_TEST_PLACEMENT_QUANTUM': '1e-6'})
        faceted_policy = framework.resolve_comparison_policy(
            'faceted', environ={'SOLID_TEST_PLACEMENT_QUANTUM': '1e-6'})
        self.assertEqual(exact_policy.placement_quantum, 1e-6)
        self.assertEqual(faceted_policy.placement_quantum, 1e-6)

    def test_a_negative_placement_quantum_is_refused(self):
        # Unlike the epsilon's negative-value error, the spec requires
        # this one to name the flag or the variable that supplied the
        # value (design.md Sec 3 "Errors").
        with self.assertRaisesRegex(ValueError,
                                    r'--placement-quantum.*negative'):
            framework.resolve_comparison_policy(
                placement_quantum=-1.0, environ={})
        with self.assertRaisesRegex(
                ValueError, r'SOLID_TEST_PLACEMENT_QUANTUM.*negative'):
            framework.resolve_comparison_policy(
                environ={'SOLID_TEST_PLACEMENT_QUANTUM': '-1'})

    def test_a_non_finite_placement_quantum_is_refused(self):
        # inf collapses every relative matrix to the same all-zero cell
        # (one verdict served for every pair in the run); nan reaches
        # astype(np.int64) undefined. Both parse as valid floats, so
        # resolve_comparison_policy must check finiteness itself.
        with self.assertRaisesRegex(ValueError,
                                    r'--placement-quantum.*finite'):
            framework.resolve_comparison_policy(
                placement_quantum=float('inf'), environ={})
        with self.assertRaisesRegex(ValueError,
                                    r'--placement-quantum.*finite'):
            framework.resolve_comparison_policy(
                placement_quantum=float('nan'), environ={})
        with self.assertRaisesRegex(
                ValueError, r'SOLID_TEST_PLACEMENT_QUANTUM.*finite'):
            framework.resolve_comparison_policy(
                environ={'SOLID_TEST_PLACEMENT_QUANTUM': 'inf'})
        with self.assertRaisesRegex(
                ValueError, r'SOLID_TEST_PLACEMENT_QUANTUM.*finite'):
            framework.resolve_comparison_policy(
                environ={'SOLID_TEST_PLACEMENT_QUANTUM': 'nan'})

    def test_a_non_numeric_environment_quantum_is_refused(self):
        with self.assertRaisesRegex(
                ValueError, r'SOLID_TEST_PLACEMENT_QUANTUM.*length.*mm'):
            framework.resolve_comparison_policy(
                environ={'SOLID_TEST_PLACEMENT_QUANTUM': 'tight'})

    def test_an_empty_environment_quantum_means_unset(self):
        # Matches the kernel's and epsilon's siblings: environ.get(...)
        # or default, so a blank line in .env is unset, not an error.
        policy = framework.resolve_comparison_policy(
            environ={'SOLID_TEST_PLACEMENT_QUANTUM': ''})
        self.assertEqual(policy.placement_quantum,
                         framework.DEFAULT_PLACEMENT_QUANTUM)

    def test_the_runner_refuses_before_building_anything(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        args = Namespace(path='whatever.py', failfast=False,
                         kernel=None, volume_epsilon=0.5)
        with patch.object(Runner, 'build_node',
                          side_effect=AssertionError('must not build')):
            with redirect_stdout(stdout), redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as stop:
                    Runner().handle(args)
        self.assertEqual(stop.exception.code, 1)
        self.assertIn('nothing', stderr.getvalue())
        self.assertIn('absorb', stderr.getvalue())

    def test_the_framework_resolves_lazily_from_the_environment(self):
        framework.set_comparison_policy(None)
        with patch.dict(os.environ, {'SOLID_TEST_KERNEL': 'faceted',
                                     'SOLID_TEST_VOLUME_EPSILON': '0.5'}):
            self.assertEqual(framework.comparison_policy(),
                             ('faceted', 0.5,
                              framework.DEFAULT_PLACEMENT_QUANTUM))
        # Resolved once: the environment changing afterwards does not
        # move a run that has already chosen.
        with patch.dict(os.environ, {'SOLID_TEST_KERNEL': 'exact'}):
            self.assertEqual(framework.comparison_policy().kernel, 'faceted')

    def test_the_runner_sets_the_policy_it_resolved(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        args = Namespace(path='whatever.py', failfast=False,
                         kernel='faceted', volume_epsilon=0.5)
        seen = {}

        def record(path):
            seen['policy'] = framework.comparison_policy()
            raise SystemExit(0)

        # The reference is resolved before any build; stopping there is
        # enough to see the policy already in force and announced.
        with patch('machinome.manager.test.resolve_node', record):
            with redirect_stdout(stdout), redirect_stderr(stderr):
                with self.assertRaises(SystemExit):
                    Runner().handle(args)
        self.assertEqual(seen['policy'], ('faceted', 0.5,
                                          framework.DEFAULT_PLACEMENT_QUANTUM))
        self.assertIn('faceted kernel', stdout.getvalue())
        self.assertIn('0.5', stdout.getvalue())

    def test_an_exact_run_announces_nothing(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        args = Namespace(path='whatever.py', failfast=False,
                         kernel=None, volume_epsilon=None)
        with patch('machinome.manager.test.resolve_node',
                   side_effect=SystemExit(0)):
            with redirect_stdout(stdout), redirect_stderr(stderr):
                with self.assertRaises(SystemExit):
                    Runner().handle(args)
        self.assertEqual(stdout.getvalue(), '')

    def test_the_summary_line_names_a_faceted_run(self):
        runner = Runner()
        runner.policy = framework.ComparisonPolicy('faceted', 0.5)
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            runner.report(1.0)
        self.assertRegex(
            stdout.getvalue(),
            r'Ran 0 tests in 1\.00 seconds: 0 passed, 0 failed '
            r'\(faceted kernel, volume epsilon 0\.5 mm³\)')

    def test_the_summary_line_of_an_exact_run_is_unchanged(self):
        runner = Runner()
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            runner.report(1.0)
        self.assertEqual(
            stdout.getvalue(),
            '\nRan 0 tests in 1.00 seconds: 0 passed, 0 failed\n')

    def test_the_summary_line_is_unchanged_at_the_default_quantum(self):
        runner = Runner()
        runner.policy = framework.ComparisonPolicy('exact', 0.0)
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            runner.report(1.0)
        self.assertEqual(
            stdout.getvalue(),
            '\nRan 0 tests in 1.00 seconds: 0 passed, 0 failed\n')

    def test_the_summary_line_names_a_non_default_quantum(self):
        runner = Runner()
        runner.policy = framework.ComparisonPolicy('exact', 0.0, 1e-06)
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            runner.report(1.0)
        self.assertRegex(
            stdout.getvalue(),
            r'Ran 0 tests in 1\.00 seconds: 0 passed, 0 failed '
            r'\(placement quantum 1e-06 mm\)')

    def test_the_summary_line_names_the_quantum_beside_the_faceted_label(self):
        runner = Runner()
        runner.policy = framework.ComparisonPolicy('faceted', 0.5, 1e-06)
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            runner.report(1.0)
        self.assertRegex(
            stdout.getvalue(),
            r'Ran 0 tests in 1\.00 seconds: 0 passed, 0 failed '
            r'\(faceted kernel, volume epsilon 0\.5 mm³, '
            r'placement quantum 1e-06 mm\)')


ROBOT_SOURCE = '''from machinome.node import Solid2Node
from solid2 import cube


class Keel(Solid2Node):
    """A sub-assembly that only its parent can build."""

    def render(self):
        raise RuntimeError('keel needs its boat')


class Boat(Solid2Node):
    def render(self):
        return cube(1, center=True)
'''

ROBOT_TEST_SOURCE = '''from machinome.test import TestCase
from boat.robot import Boat


class BoatTest(TestCase):
    node = Boat

    def test_boat_builds(self):
        self.assertIsNotNone(self.node.mesh)
'''


class BareFileCoversDeclaredClassesTest(MultiTestCaseFixture):
    """A bare file reference covers the node classes its companion
    declares and no other: a sub-assembly nobody tests, that cannot be
    built alone, is never built. openvmp's robot.py is the origin --
    a machine and five sub-assemblies whose ports the machine binds."""

    def test_an_undeclared_sub_assembly_is_not_built(self):
        node_path = self.write('boat/robot.py', ROBOT_SOURCE)
        self.write('boat/test_robot.py', ROBOT_TEST_SOURCE)

        code, stdout, stderr = self.run_solid_test(node_path)

        self.assertEqual(code, 0, stderr)
        self.assertNotIn('keel needs its boat', stderr)
        self.assertIn('BoatTest.test_boat_builds', stdout)
        self.assertIn('Ran 1 tests', stdout)

    def test_a_file_with_no_companion_builds_every_class(self):
        node_path = self.write('boat/hull.py', HULL_SOURCE)

        code, stdout, stderr = self.run_solid_test(node_path)

        self.assertEqual(code, 0, stderr)
        self.assertIn('Ran 0 tests', stdout)
