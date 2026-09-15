"""Mechanism probes against solid_node.manager.test.Test, without a build.

    PYTHONPATH="$PWD" .venv/bin/python openspec/changes/honour-skip-and-xfail/evidence/probe_runner_mechanism.py
"""
import io
import unittest
from contextlib import redirect_stdout

from solid_node.manager.test import Test as Runner, StopTestRun


def with_instants(*values):
    def decorator(method):
        method.testing_instants = list(values)
        return method
    return decorator


class FakeNode:
    children = ()

    def set_keyframe(self, instant):
        self.last_instant = instant


class TwoDifferentFailures(FakeNode):
    @with_instants(0, 1, 2)
    def test_sweep(self):
        if self.last_instant == 0:
            raise AssertionError('FIRST failure, at instant 0')
        if self.last_instant == 2:
            raise AssertionError('LAST failure, at instant 2')


class SkipThenFail(FakeNode):
    @with_instants(0, 1)
    def test_sweep(self):
        if self.last_instant == 0:
            raise unittest.SkipTest('skipped at instant 0')
        raise AssertionError('real failure at instant 1')


class OnlyASkip(FakeNode):
    @with_instants(0, 1, 2, 3)
    def test_sweep(self):
        if self.last_instant == 1:
            raise unittest.SkipTest('skipped at instant 1')


def run(node, failfast=False):
    runner = Runner()
    runner.failfast = failfast
    runner.test_case = None
    runner.node = node
    out = io.StringIO()
    with redirect_stdout(out):
        try:
            runner.run_tests()
        except StopTestRun:
            pass
    return runner, out.getvalue()


print('=== A. Two failing instants in one method: which traceback survives')
runner, out = run(TwoDifferentFailures())
print(out)
print(f'num_tests={runner.num_tests} num_passed={runner.num_passed} '
      f'num_failed={runner.num_failed}')
print(f'FIRST failure in output: {"FIRST failure" in out}')
print(f'LAST failure in output:  {"LAST failure" in out}')

print('\n=== B. A skip at instant 0 and a real failure at instant 1')
runner, out = run(SkipThenFail())
print(f'num_tests={runner.num_tests} num_passed={runner.num_passed} '
      f'num_failed={runner.num_failed}')
print(f'SkipTest reported: {"skipped at instant 0" in out}')
print(f'real failure reported: {"real failure at instant 1" in out}')

print('\n=== C. A method whose only exception is a skip, over four instants')
runner, out = run(OnlyASkip())
print(out)
print(f'num_tests={runner.num_tests} num_passed={runner.num_passed} '
      f'num_failed={runner.num_failed}')

print('\n=== D. The same, with --failfast')
runner, out = run(OnlyASkip(), failfast=True)
print(out)
print(f'num_tests={runner.num_tests} num_passed={runner.num_passed} '
      f'num_failed={runner.num_failed}')

print('\n=== E. skipTest and expectedFailure reach a node through TestCaseMixin')
from solid_node.test import TestCase, TestCaseMixin
print(f'solid_node.test.TestCase mro includes unittest.TestCase: '
      f'{unittest.TestCase in TestCase.__mro__}')
print(f'TestCaseMixin has skipTest: {hasattr(TestCaseMixin, "skipTest")}')
print(f'unittest.SkipTest is an Exception subclass: '
      f'{issubclass(unittest.SkipTest, Exception)}')


class FailThenSkip(FakeNode):
    @with_instants(0, 1, 2)
    def test_sweep(self):
        if self.last_instant == 0:
            raise AssertionError('REAL failure, at instant 0')
        if self.last_instant == 2:
            raise unittest.SkipTest('skipped at instant 2')


print('\n=== F. A real failure at instant 0 and a skip at instant 2')
runner, out = run(FailThenSkip())
print(out)
print(f'num_failed={runner.num_failed}; '
      f'REAL failure in output: {"REAL failure" in out}')


print('\n=== G. unittest.skip forms: what reaches the runner')
import functools


@unittest.skip('method-level @skip')
def decorated_method(self):
    raise AssertionError('body should never run')


print(f'@unittest.skip wraps the function: '
      f'{decorated_method.__name__ == "decorated_method"}, '
      f'__unittest_skip__={getattr(decorated_method, "__unittest_skip__", None)}')
try:
    decorated_method(None)
except unittest.SkipTest as e:
    print(f'calling it raises SkipTest({e!r}) -- so a method-level @skip '
          f'reaches the runner as the same exception skipTest() raises')


@unittest.skip('class-level @skip')
class SkippedWholeCase(FakeNode):
    def test_a(self):
        print('    [body of test_a RAN]')

    def test_b(self):
        print('    [body of test_b RAN]')


print(f'class carries __unittest_skip__={getattr(SkippedWholeCase, "__unittest_skip__", None)}')
runner, out = run(SkippedWholeCase())
print(out)
print(f'num_tests={runner.num_tests} num_passed={runner.num_passed} '
      f'num_failed={runner.num_failed}')

print('\n=== H. testing_instants survives @unittest.skip over @testing_steps')
from solid_node.test import testing_steps


@unittest.skip('why')
@testing_steps(3)
def swept(self):
    pass


print(f'testing_instants={getattr(swept, "testing_instants", None)}')
