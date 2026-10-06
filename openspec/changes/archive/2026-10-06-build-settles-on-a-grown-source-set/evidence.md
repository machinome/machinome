# Evidence — `build-settles-on-a-grown-source-set`

Cycle 2 of the fix-warts-3 campaign (`workflow/ongoing/fix-warts-3.md`).
Bench `machinome/WTs/fix-warts-3`, branch `fix-warts-3`, planning commit
`f9d4c381c39654219103a939a1da394ef04faa26` (`git -C <bench> rev-parse
HEAD`). Every framework command ran as `env -C <bench> PYTHONPATH=<bench>
/home/asa/devel/machinome/.venv/bin/<tool> ...` (Python 3.12.3);
`python -c 'import machinome; print(machinome.__file__)'` printed
`<bench>/machinome/__init__.py`. `<scratch>` is the campaign scratchpad's
`cycle2/` directory; every `SOLID_BUILD_DIR` named below is a fresh
directory under it. `<hexapod>` is
`projects/Robots/hexapod_spiderbot_model` (a link to
`/mnt/data/machinome-projects/Robots/hexapod_spiderbot_model`). One test
run or build of ours at a time throughout. A `START` count is
`grep -c START` over the command's combined output; a wall time is
`date +%s.%N` around the command.

## 1. Baseline on the unmodified tree (f9d4c38)

### 1.2 The fixture's timestamps

`stat -c '%y %n' <bench>/tests/scad_where_read_project/*`, as the bench's
checkout wrote them; no step of this cycle touched them:

```
2026-10-06 14:10:31.477951865 +0000 __init__.py
2026-10-06 14:10:31.478951896 +0000 bracket.stl
2026-10-06 14:10:31.478951896 +0000 legacy.py
2026-10-06 14:10:31.479951928 +0000 machine.py
2026-10-06 14:10:31.479951928 +0000 native.py
2026-10-06 14:10:31.480951959 +0000 tab.stl
```

(`__pycache__/`, written by the earlier test runs, is the only other
entry.)

### 1.3 The bounded builds

`env -C <bench> PYTHONPATH=<bench> SOLID_BUILD_DIR=<scratch>/a-before-<root>
timeout 30 .venv/bin/machinome build tests/scad_where_read_project/<module>:<root>`:

| reference | exit | `START` lines | wall |
|---|---|---|---|
| `native.py:StlBench` | 124 | 9 | 30.0 s |
| `machine.py:Machine` | 124 | 8 | 30.0 s |

Every line of the `StlBench` output is ` INFO -    core.builder - START`;
`Machine`'s adds the first generation's `.scad generated with ...` lines and
the fixture's deliberate `FutureWarning` about binding a port in `render()`.

### 1.4 One generation, traced

`env -C <bench> PYTHONPATH=<bench> SOLID_BUILD_DIR=<scratch>/a-trace-before
.venv/bin/python <scratch>/trace_one_generation.py
tests/scad_where_read_project/native.py:StlBench` (exit 0), its lines other
than the log's `INFO`:

```
after load: 1 files, max mtime_ns 1791295831479951928 (tests/scad_where_read_project/native.py)
after _prepare: 3 files, max mtime_ns 1791295831480951959 (tests/scad_where_read_project/tab.stl)
  joined during _prepare: tests/scad_where_read_project/bracket.stl mtime_ns 1791295831478951896
  joined during _prepare: tests/scad_where_read_project/tab.stl mtime_ns 1791295831480951959
  assembly census holds 4 paths; assembled files not in it: []
outcome BuildOutcome.SOURCE_CHANGED
_start returned BuildOutcome.SOURCE_CHANGED at builder.py:361; last lines executed [381, 379, 391, 392, 393, 361]
_start returned BuildOutcome.SOURCE_CHANGED at builder.py:314; last lines executed [314, 315, 316, 317, 319, 314]
```

The inner `_start` (the generation's) executed 391-393, the post-assembly
comparison, and returned through the `with project_build_lock(...)` line
(361); the outer `_start` returned the same value from its recursive call
(314). The assembly census holds every assembled file.

`<scratch>/trace_one_generation.py`:

```python
"""Run one builder generation in-process and trace where `_start` returns.

Usage (bench as cwd, PYTHONPATH=<bench>, SOLID_BUILD_DIR=<scratch>):
    python trace_one_generation.py tests/scad_where_read_project/native.py:StlBench

Read-only with respect to the bench: it patches nothing in the source, it
only observes `Builder._start` with sys.settrace and wraps `_prepare` on the
loaded node instance to print the source set and its maximum before and
after preparation.
"""

import asyncio
import os
import sys

from machinome.core import builder as builder_module
from machinome.core.builder import Builder

reference = sys.argv[1]
BUILDER_FILE = builder_module.__file__
last_line = {}
returns = []


def tracer(frame, event, arg):
    code = frame.f_code
    if code.co_filename != BUILDER_FILE or code.co_name != '_start':
        return None
    if event == 'line':
        last_line.setdefault(id(frame), []).append(frame.f_lineno)
    elif event == 'return' and arg is not None:
        returns.append((frame.f_lineno, arg, last_line[id(frame)][-6:]))
    return tracer


def describe(node, label):
    files = sorted(node.files)
    stats = {path: os.stat(path).st_mtime_ns for path in files}
    newest = max(stats, key=stats.get)
    print(f'{label}: {len(files)} files, max mtime_ns {stats[newest]} '
          f'({os.path.relpath(newest)})')
    return set(files)


original_load = builder_module.load_node


def load_and_wrap(*args, **kwargs):
    node = original_load(*args, **kwargs)
    before = describe(node, 'after load')
    prepare = node._prepare

    def wrapped(*a, **k):
        result = prepare(*a, **k)
        after = describe(node, 'after _prepare')
        for path in sorted(after - before):
            print(f'  joined during _prepare: {os.path.relpath(path)} '
                  f'mtime_ns {os.stat(path).st_mtime_ns}')
        from machinome.source_generation import current_census
        census = current_census()
        if census is None:
            print('  no census active around _prepare')
        else:
            untracked = {os.path.realpath(p) for p in after} - census.paths
            print(f'  assembly census holds {len(census.paths)} paths; '
                  f'assembled files not in it: {sorted(untracked)}')
        return result

    node._prepare = wrapped
    return node


builder_module.load_node = load_and_wrap
builder = Builder(reference, watch=False, lifecycle=True)
sys.settrace(tracer)
try:
    outcome = asyncio.run(builder._start())
finally:
    sys.settrace(None)
print('outcome', outcome)
for line, value, lines in returns:
    print(f'_start returned {value} at builder.py:{line}; '
          f'last lines executed {lines}')
```

`<scratch>/grown_set_probe.py`:

```python
"""Prototype of the red test: a project whose STL is dated `offset_ns`
newer than its module, every file an hour older than the build, built by a
real `machinome build` subprocess bounded by subprocess.run's own timeout.

Usage: python grown_set_probe.py <machinome package parent> <scratch dir>
"""

import os
import shutil
import subprocess
import sys
import time

import trimesh

package_parent, scratch = sys.argv[1], sys.argv[2]
HOUR = 3600 * 10 ** 9

for label, offset_ns in (('1 ms', 10 ** 6), ('1 s', 10 ** 9)):
    root = os.path.join(scratch, f'grown-{offset_ns}')
    shutil.rmtree(root, ignore_errors=True)
    os.makedirs(os.path.join(root, 'design'))
    with open(os.path.join(root, 'pyproject.toml'), 'w') as manifest:
        manifest.write('[tool.machinome]\nmodel = "design.bench:Bench"\n')
    with open(os.path.join(root, 'design', '__init__.py'), 'w'):
        pass
    with open(os.path.join(root, 'design', 'bench.py'), 'w') as module:
        module.write(
            'from machinome.node.assembly import AssemblyNode\n'
            'from machinome.node.stl import StlNode\n\n\n'
            'class Tab(StlNode):\n'
            '    stl_source = "tab.stl"\n\n\n'
            'class Bench(AssemblyNode):\n'
            '    def render(self):\n'
            '        return [Tab()]\n')
    trimesh.creation.box().export(os.path.join(root, 'design', 'tab.stl'),
                                  file_type='stl')
    module_ns = time.time_ns() - HOUR
    for path, stamp in ((os.path.join(root, 'pyproject.toml'), module_ns),
                        (os.path.join(root, 'design', '__init__.py'),
                         module_ns),
                        (os.path.join(root, 'design', 'bench.py'), module_ns),
                        (os.path.join(root, 'design', 'tab.stl'),
                         module_ns + offset_ns)):
        os.utime(path, ns=(stamp, stamp))

    environment = dict(os.environ, PYTHONPATH=package_parent,
                       PYTHONDONTWRITEBYTECODE='1')
    environment.pop('SOLID_BUILD_DIR', None)
    started = time.monotonic()
    try:
        completed = subprocess.run(
            [sys.executable, '-c',
             'import sys; sys.path.insert(0, %r); '
             'from machinome.cli import manage; manage()' % package_parent,
             'build'],
            cwd=root, env=environment, capture_output=True, text=True,
            timeout=45)
        output = completed.stdout + completed.stderr
        outcome = f'exit {completed.returncode}'
    except subprocess.TimeoutExpired as expired:
        output = ((expired.stdout or b'').decode() +
                  (expired.stderr or b'').decode())
        outcome = 'timed out after 45 s'
    print(f'STL {label} newer than its module: {outcome}, '
          f'{output.count("START")} START lines, '
          f'{time.monotonic() - started:.1f} s, viewer.json '
          f'{os.path.exists(os.path.join(root, "_build", "viewer.json"))}')
```

### 1.5 The scratch project

`env -C <scratch> .venv/bin/python <scratch>/grown_set_probe.py <bench>
<scratch>/probe-before`:

```
STL 1 ms newer than its module: timed out after 45 s, 36 START lines, 45.0 s, viewer.json False
STL 1 s newer than its module: timed out after 45 s, 37 START lines, 45.0 s, viewer.json False
```

No builder process survived the timeouts (`ps -eo pid,ppid,etime,args`
filtered for `machinome`, `grown` and `builder`: nothing).

### 1.6 The focused builder set

`pytest -q -p no:cacheprovider tests/test_retained_builder_generation.py
tests/test_builder_lifecycle.py tests/test_source_generation.py
tests/test_builder_reload_resilience.py tests/test_build_lock.py`:

```
85 passed, 7 subtests passed in 57.63s   (wall 58.8 s)
```

### 1.7 Robots/hexapod_spiderbot_model in a fresh worktree

Before: `git -C <hexapod> status --short` printed nothing; `git -C
<hexapod> worktree list`:

```
/mnt/data/machinome-projects/Robots/hexapod_spiderbot_model                                      7ef1e36 [main]
/mnt/data/machinome-projects/Robots/hexapod_spiderbot_model/.git/licensing-worktrees/adequation  28dc6b3 [license-adequation-20260921]
```

`<hexapod>/WTs` did not exist. `git -C <hexapod> worktree add --detach
<hexapod>/WTs/build-settles` printed `Preparing worktree (detached HEAD
7ef1e36)` / `HEAD is now at 7ef1e36 machinome 0.8: imports and flags on the
campaign's names`; no branch was created. `git -C
<hexapod>/WTs/build-settles rev-parse --show-toplevel` printed
`/mnt/data/machinome-projects/Robots/hexapod_spiderbot_model/WTs/build-settles`
and `rev-parse HEAD` `7ef1e36e745ea6da062cb40102eb8628f12c42fa`. With the
worktree in place the main checkout's `git status --short` printed `?? WTs/`
(the project's `.gitignore` does not name it).

The checkout's timestamps (`stat -c '%y %n'`):

```
2026-10-06 16:22:47.830229918 +0000 pyproject.toml
2026-10-06 16:22:47.837230140 +0000 simulation/printed.py
2026-10-06 16:22:47.839230203 +0000 simulation/spiderbot.py
2026-10-06 16:22:47.878231442 +0000 stl/Frame.stl
2026-10-06 16:22:47.898232077 +0000 stl/Tip.stl
```

`env -C <hexapod>/WTs/build-settles PYTHONPATH=<bench>
SOLID_BUILD_DIR=<scratch>/a-hexapod-before timeout 120
.venv/bin/machinome build`: exit 124, 33 `START` lines, wall 120.0 s. No
process of it survived (`ps` filtered for `build-settles` showed only the
invoking shell).

## 2. Red tests, on the unmodified source (f9d4c38)

Added to `tests/test_retained_builder_generation.py`:

- `_GrowingNode`, a node double whose `mtime_ns` is the largest `os.stat`
  mtime over its current `files` on every read, as
  `AbstractBaseNode.mtime_ns` is over the node's current set.
- `JoinedContributorTest` (in-process, `_InProcessBuilderTest`): a real
  project directory (`pyproject.toml` declaring `model.py`), `model.py`
  dated an hour back, a joiner `part.stl`; the real
  `project_source_generation`; `load_node` patched to return a
  `_GrowingNode` whose `files` are `{model.py}` and whose `_prepare` calls
  `machinome.source_generation.track_sources([part.stl])` and adds the
  joiner to `files`; `_published_model_is_current` a `Mock` returning
  `False`, `generate_stl` an `AsyncMock` returning `CURRENT`,
  `_write_viewer_snapshot` a `Mock` returning `True`.
  - `test_a_newer_contributor_joining_during_assembly_builds`, subtests for
    the joiner dated 1 ms and 1 s after the module and an hour after the
    present: the grown maximum exceeds the module's, `_start()` returns
    `CURRENT`, `_prepare` is called once, `generate_stl` awaited once and
    `_write_viewer_snapshot` called once.
  - `test_a_contributor_replaced_after_joining_stands_down` (the guard):
    after joining, the joiner is replaced (`os.replace`) by a sibling with
    other bytes stamped with the joiner's own mtime; `_start()` returns
    `SOURCE_CHANGED`, `generate_stl` is not awaited and
    `_write_viewer_snapshot` not called.
- `FreshCheckoutBuildTest::test_a_mesh_newer_than_its_module_builds_in_one_generation`:
  for each subtest a project in its own temporary directory with its own
  package (`checkout_ms`, `checkout_s`), `parts.py` declaring
  `Tab(StlNode)` with `stl_source = 'tab.stl'` and `Bench(AssemblyNode)`
  rendering `[Tab()]`, `tab.stl` written with `trimesh.creation.box()`,
  `pyproject.toml` declaring `<package>.parts:Bench`; `pyproject.toml`,
  `__init__.py` and `parts.py` dated an hour back and `tab.stl` 1 ms or 1 s
  after them. `Build().build('<package>.parts:Bench')` runs in the project
  (`chdir`, `SOLID_BUILD_DIR=<project>/_build`,
  `PYTHONDONTWRITEBYTECODE=1`) with `machinome.manager.build.Process`
  wrapped to record each real child and to raise `AssertionError` naming
  the first child's exit code when a second is requested. Expected: status
  0, one child exiting 0, and `viewer.json` naming one child, `Tab`, whose
  `model` is a file under `<package>/tab-` in the build directory. The
  subtest's package leaves `sys.modules` at cleanup.

`pytest -q -p no:cacheprovider tests/test_retained_builder_generation.py
-k "JoinedContributorTest or FreshCheckoutBuildTest"` (exit 1, 3.9 s):

```
_ JoinedContributorTest.test_a_newer_contributor_joining_during_assembly_builds [1 ms after the module] _
E               AssertionError: <BuildOutcome.SOURCE_CHANGED: 11> != <BuildOutcome.CURRENT: 0>
_ JoinedContributorTest.test_a_newer_contributor_joining_during_assembly_builds [1 s after the module] _
E               AssertionError: <BuildOutcome.SOURCE_CHANGED: 11> != <BuildOutcome.CURRENT: 0>
_ JoinedContributorTest.test_a_newer_contributor_joining_during_assembly_builds [an hour after the present] _
E               AssertionError: <BuildOutcome.SOURCE_CHANGED: 11> != <BuildOutcome.CURRENT: 0>
_ FreshCheckoutBuildTest.test_a_mesh_newer_than_its_module_builds_in_one_generation [checkout_ms] _
E           AssertionError: a second builder was spawned; the first exited 11
_ FreshCheckoutBuildTest.test_a_mesh_newer_than_its_module_builds_in_one_generation [checkout_s] _
E           AssertionError: a second builder was spawned; the first exited 11
5 failed, 3 passed, 14 deselected in 3.92s
```

The five failures are the five red subtests, each for the reason the design
names; the guard, run alone, passed (`1 passed in 0.20s`). The red run
ended in under four seconds: the supervisor test's bound is its own refusal
of a second builder, not a timeout.

`FreshCheckoutBuildTest`'s viewer-document assertions were tightened after
the first green run showed the document's shape (one child `Tab`, `model`
`<package>/tab-<...>.stl`). The red was then repeated with the change of 3.1
removed from the file and restored afterwards: the same five failures with
the same five messages, `5 failed, 3 passed, 14 deselected in 3.72s`.

## 3. The change

`machinome/core/builder.py`, `Builder._start`, the post-assembly comparison
(`git diff`):

```diff
-            # Assembly discovers the complete source union. An edit during it
-            # invalidates the loaded classes before any later publication.
+            # Without a source generation -- reached only through a patched
+            # loader, since a reference outside a project does not load --
+            # the loaded maximum is this branch's only record of what was
+            # loaded. With one, the assembly phase's closing check has
+            # already compared every contributor with its own observation,
+            # those that joined during assembly included (ADR-084): a newer
+            # file joining moves the grown set's maximum without any source
+            # having changed, and must not stand the build down.
             if (assembly_failure is None and
+                    self._source_generation is None and
                     self.node.mtime_ns != loaded_source_mtime_ns):
                 return BuildOutcome.SOURCE_CHANGED
```

Nothing else in the file changed; the lock-wait comparison after
`checkpoint('after_lock')` is as it was.

### 3.2 Green

The new tests (`-k "JoinedContributorTest or FreshCheckoutBuildTest"`):
`3 passed, 14 deselected, 5 subtests passed in 3.67s`. The whole file:
`17 passed, 5 subtests passed in 43.24s`.

The focused builder set of 1.6, the existing tests unedited:

```
88 passed, 12 subtests passed in 61.27s (0:01:01)   (wall 62.4 s)
```

85 + the three new tests, 7 + the five new subtests.

### 3.3 Lint

`flake8 --max-line-length=89` (flake8 7.3.0) on the two touched Python
files, compared with the same command on their `HEAD` text (`git show
HEAD:<file> | flake8 -`): no new finding. `builder.py` has two, both at
`HEAD` (`F401 '.serializer.DOCUMENT_FORMAT' imported but unused`, `E303 too
many blank lines (2)` at its line 867); the test file has none, before or
after.

`black --check` (black 26.5.1) reports both files would be reformatted, and
so it does for each file's `HEAD` text (`git show HEAD:<file> | black
--check -q -`, exit 1): the repository is not black-formatted (the CI step
is `continue-on-error`). The new code follows the surrounding style.

## 4. Framework validation

### 4.1 The bounded builds

As 1.3, bound raised to 120 s, fresh `SOLID_BUILD_DIR`s:

| reference | exit | `START` lines | wall |
|---|---|---|---|
| `native.py:StlBench` | 0 | 1 | 6.5 s |
| `machine.py:Machine` | 0 | 1 | 6.7 s |

Each build directory holds `viewer.json` and the fixture's artifacts.

### 4.2 One generation, traced

As 1.4, for both roots (exit 0 each). `StlBench`:

```
after load: 1 files, max mtime_ns 1791295831479951928 (tests/scad_where_read_project/native.py)
after _prepare: 3 files, max mtime_ns 1791295831480951959 (tests/scad_where_read_project/tab.stl)
  joined during _prepare: tests/scad_where_read_project/bracket.stl mtime_ns 1791295831478951896
  joined during _prepare: tests/scad_where_read_project/tab.stl mtime_ns 1791295831480951959
  assembly census holds 4 paths; assembled files not in it: []
outcome BuildOutcome.CURRENT
_start returned BuildOutcome.CURRENT at builder.py:496; last lines executed [485, 489, 493, 494, 495, 496]
_start returned BuildOutcome.CURRENT at builder.py:314; last lines executed [314, 315, 316, 317, 319, 314]
```

`Machine`: after load 2 files; after `_prepare` 4 files, the largest
`tab.stl` `1791295831480951959`; `bracket.stl` and `tab.stl` joined; the
assembly census holds 5 paths, `assembled files not in it: []`;
`outcome BuildOutcome.CURRENT`, returned at the same lines.

The wrapper also printed its block again for each later call of the root's
`_prepare`, which `trigger_stl` makes in the artifact pass (a memoized
no-op there): twice in all for `StlBench`, three times for `Machine`, each
with the same set and `assembled files not in it: []` against that pass's
census.

### 4.3 The scratch project

`env -C <scratch> .venv/bin/python <scratch>/grown_set_probe.py <bench>
<scratch>/probe-after`:

```
STL 1 ms newer than its module: exit 0, 1 START lines, 2.3 s, viewer.json True
STL 1 s newer than its module: exit 0, 1 START lines, 2.3 s, viewer.json True
```

### 4.4 `tests/test_scad_presentation.py`

The fixture's timestamps, `stat` again just before: those of 1.2,
unchanged. `pytest -v -p no:cacheprovider tests/test_scad_presentation.py`,
alone (exit 0):

```
======== 22 passed, 2 warnings, 23 subtests passed in 106.40s (0:01:46) ========   (wall 107.5 s)
```

Among them, PASSED, the seven the cycle `snap-keeps-the-triad-unit` had to
deselect:

```
tests/test_scad_presentation.py::WithoutTheEngineTest::test_native_projects_build_without_each_module PASSED [ 22%]
tests/test_scad_presentation.py::WrittenOnlyWhereReadTest::test_a_build_writes_only_the_scad_authored_leafs_scad PASSED [ 54%]
tests/test_scad_presentation.py::SweepTest::test_presentation_scad_and_a_renamed_leafs_scad_are_swept PASSED [ 63%]
tests/test_scad_presentation.py::SnapshotOnDemandTest::test_a_build_removes_a_root_scad_a_killed_render_left PASSED [ 68%]
tests/test_scad_presentation.py::SnapshotOnDemandTest::test_the_openscad_renderer_draws_the_roots_scad_for_its_pose PASSED [ 77%]
tests/test_scad_presentation.py::SnapshotOnDemandTest::test_the_renderer_removes_the_roots_scad_after_drawing_it PASSED [ 81%]
tests/test_scad_presentation.py::SnapshotOnDemandTest::test_the_renderer_removes_the_roots_scad_when_drawing_fails PASSED [ 86%]
```

They were not run red: each would wait out its runner's 600 s timeout; 1.3
and cycle 1's evidence §4.3 stand for the red.

## 5. Validation in Robots/hexapod_spiderbot_model (read only)

### 5.1 The build after the change

In the worktree of 1.7, `env -C <hexapod>/WTs/build-settles
PYTHONPATH=<bench> SOLID_BUILD_DIR=<scratch>/a-hexapod-after timeout 900
.venv/bin/machinome build`: exit 0, 1 `START` line, wall 8.2 s. The build
directory holds `viewer.json`, whose tree has 172 nodes with a `model`, and
29 STL files.

### 5.2 One generation, traced

`env -C <hexapod>/WTs/build-settles PYTHONPATH=<bench>
SOLID_BUILD_DIR=<scratch>/a-hexapod-trace .venv/bin/python
<scratch>/trace_one_generation.py simulation/spiderbot.py:Spiderbot` (exit
0), its lines other than the log's `INFO` and the 23 `joined during
_prepare` lines of each block:

```
after load: 7 files, max mtime_ns 1791303767839230203 (simulation/sourced.py)
after _prepare: 30 files, max mtime_ns 1791303767898232077 (stl/Tip.stl)
  assembly census holds 31 paths; assembled files not in it: []
after _prepare: 30 files, max mtime_ns 1791303767898232077 (stl/Tip.stl)
  assembly census holds 31 paths; assembled files not in it: []
outcome BuildOutcome.CURRENT
_start returned BuildOutcome.CURRENT at builder.py:496; last lines executed [485, 489, 493, 494, 495, 496]
_start returned BuildOutcome.CURRENT at builder.py:314; last lines executed [314, 315, 316, 317, 319, 314]
```

(`simulation/sourced.py` shares `simulation/spiderbot.py`'s nanosecond, the
loaded closure's largest.) Every one of the 23 meshes that joined is in the
census.

### 5.3 The worktree removed

`git -C <hexapod>/WTs/build-settles status --short`: nothing. `git -C
<hexapod> worktree remove <hexapod>/WTs/build-settles` (exit 0); `rmdir
<hexapod>/WTs` (exit 0). `git -C <hexapod> worktree list` prints the two
lines of 1.7 and `git -C <hexapod> status --short` prints nothing, as
before; the worktree was detached, so no branch was created.

## 6. Words

### 6.1 Changelog

`docs/project/changelog.rst`, under the existing `Unreleased`, after the
cycle-1 bullet: design.md Decision 5's bullet, "**A build of a fresh
checkout finishes.**" `pytest -q -p no:cacheprovider
tests/test_release_records.py`: `9 passed, 58 subtests passed in 0.14s`.

### 6.2 The manual

`grep -rn -i "stand down\|stands down\|SOURCE_CHANGED\|maximum mtime\|aggregate"
docs/ --include=*.rst --include=*.md`, outside `docs/adrs/`: three lines of
`docs/architecture.md` (2115, 2176, 2206), the source-generation paragraph
and the development-reload paragraphs, which describe the per-contributor
census and a reload's repair, not the removed comparison; they stay as they
are. The only other hit is the new changelog bullet.

## 7. Findings record

`workflow/warts.md`, "Findings from the framework cycle `lean-install`
(3 October 2026)": the `mesh-engine` addendum moved verbatim to
`workflow/archive/fix-warts-3-2026-10-06/resolved.md` under
`## build-settles-on-a-grown-source-set`, with the entry's first line
quoted for context and a "What shipped" paragraph; in its place a
"**Remaining (2026-10-06)**" note: the restart loop closed by this change,
the three-hour hang not claimed (design.md, Open Question 1).
`workflow/ongoing/fix-warts-3.md`, "Progress": one line for this cycle.

## 8. Sync, archive, full suite

### 8.1-8.2 Sync and archive

`openspec validate build-settles-on-a-grown-source-set`: `Change
'build-settles-on-a-grown-source-set' is valid`, with the non-blocking
warning `Why section should not exceed 1000 characters`, as planned.
`openspec archive build-settles-on-a-grown-source-set --yes` (task status
25/29, section 8's four boxes open at that moment):

```
Specs to update:
  build-pipeline: update
  one-shot-build-and-notification: update
Applying changes to openspec/specs/build-pipeline/spec.md:
  ~ 1 modified
Applying changes to openspec/specs/one-shot-build-and-notification/spec.md:
  ~ 1 modified
Totals: + 0, ~ 2, - 0, → 0
Specs updated successfully.
Change 'build-settles-on-a-grown-source-set' archived as '2026-10-06-build-settles-on-a-grown-source-set'.
```

The archive left one blank line more at the end of
`openspec/specs/one-shot-build-and-notification/spec.md`; it was removed,
so the baseline diff is the requirement's added sentence and scenario only.
Every scenario of the two modified requirements is present once
(`grep -c "Scenario: <title>$"`, 1 each): in `build-pipeline`, "The newest
source wins", "A contributor changes beneath the same maximum", "A
contributor newer than the loaded sources joins during assembly", "A
contributor edited after it joined stands the build down", "A redundant
build publishes nothing", "A watching builder finds nothing to do", "An
ordinary change still builds"; in `one-shot-build-and-notification`, "Build
the project model", "Build publishes beside a running watch loop", "The
source moves while the build waits", "A freshly checked-out project builds
once". `openspec validate --specs`: `Totals: 45 passed, 0 failed (45
items)`.

### 8.3 The focused builder set

As 1.6, after the archive:

```
88 passed, 12 subtests passed in 61.23s (0:01:01)   (wall 62.4 s)
```

### 8.4 Full suite

`env -C <bench> PYTHONPATH=<bench> timeout 2400 .venv/bin/pytest -q -p
no:cacheprovider`, alone, nothing deselected (exit 0):

```
4614 passed, 4 skipped, 55 warnings, 6582 subtests passed in 664.28s (0:11:04)   (wall 666.7 s)
```

Cycle 1's run, with the seven `test_scad_presentation.py` tests
deselected, was `4604 passed, 4 skipped, 7 deselected`; this one has those
seven and the three new tests. The fixture's timestamps after the run are
those of 1.2.
