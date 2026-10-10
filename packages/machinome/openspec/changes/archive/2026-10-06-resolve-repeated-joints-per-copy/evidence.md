# Evidence — `resolve-repeated-joints-per-copy`

Cycle 4 of the fix-warts-3 campaign (`workflow/ongoing/fix-warts-3.md`).
Bench `machinome/WTs/fix-warts-3`, branch `fix-warts-3`, planning commit
`e41e759e7dbefdd64da125771f76b42f2be378ca` (`git -C <bench> rev-parse
HEAD`). Every framework command ran as `env -C <bench> PYTHONPATH=<bench>
/home/asa/devel/machinome/.venv/bin/<tool> ...` (Python 3.12.3);
`python -c 'import machinome; print(machinome.__file__)'` printed
`<bench>/machinome/__init__.py`, and so did every probe (each prints
`machinome.__file__` first) and, from inside the project with the same
`PYTHONPATH`, the project's interpreter. The project command ran as
`env -C <Prusa> PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/machinome
test --mesh simulation/prusa_i3.py`, with `<Prusa>` =
`projects/3D-Printers/Prusa3-vanilla` (branch `master`, `77bf9d8`, clean
tree). `<scratch>` is the campaign scratchpad's `cycle4/` directory; this
stage's outputs are in its `apply-baseline/` and `apply-after/`
subdirectories, and Stage P's are at its top level, left in place. Tools:
`flake8` 7.3.0 (the pyenv shim; the venv has none), `black` 26.5.1,
`openspec` 1.6.0. One test run of ours at a time throughout; before each
heavy run the process table was checked for another `pytest` or
`machinome test|snapshot|build` of the campaign, and none was running.

## 1. Baseline on the unmodified tree (e41e759)

### 1.2 The reproduction

`env -C <bench> PYTHONPATH=<bench> .venv/bin/python
<scratch>/repro_repeat_index.py` (exit 0; the script catches and prints):

```
machinome from /home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py
[axis/at/range of a repeated class] RED: ParameterError: Guide.turn: axis -- the callable raised AttributeError: 'Guide' object has no attribute 'index'
[each copy bound to 30] RED: ParameterError: Guide.turn: axis -- the callable raised AttributeError: 'Guide' object has no attribute 'index'
[carries of a repeated class] RED: ParameterError: Roller.spin: carries -- the callable raised AttributeError: 'Roller' object has no attribute 'index'
[frame at of a repeated class] RED: ParameterError: Seated.seat: frame argument at -- the callable raised AttributeError: 'Seated' object has no attribute 'index'
[check() reads index] RED: AttributeError: 'Checked' object has no attribute 'index'
[a callable failing for another reason] RED: ParameterError: Wrong.turn: axis -- the callable raised AttributeError: 'Wrong' object has no attribute 'no_such_thing'
```

The same with `PROBE_SEED=1` (exit 0):

```
machinome from /home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py
PROBE: index seeded before __init__
[axis/at/range of a repeated class] ok: [((0, 0, 1), (0.0, 0.0, 0.0), (0, 90)), ((0, 0, -1), (10.0, 0.0, 0.0), (0, 91))]
[each copy bound to 30] ok: [('guides-0', 0, [['r', '30', [0, 0, 1]]]), ('guides-1', 1, [['t', ['-10.0', '-0.0', '-0.0']], ['r', '30', [0, 0, -1]], ['t', ['10.0', '0.0', '0.0']]])]
[carries of a repeated class] ok: [(5.0, 0.0, 0.0), (6.0, 0.0, 0.0)]
[frame at of a repeated class] ok: [<frame at=(0.0, 0.0, 0.0) x=(1, 0, 0) y=(0, 1, 0) z=(0, 0, 1)>, <frame at=(0.0, 0.0, 3.0) x=(1, 0, 0) y=(0, 1, 0) z=(0, 0, 1)>]
[check() reads index] ok: [0, 1]
[a callable failing for another reason] RED: ParameterError: Wrong.turn: axis -- the callable raised AttributeError: 'Wrong' object has no attribute 'no_such_thing'
```

Both outputs are byte-identical (`diff`) to Stage P's
`<scratch>/repro-unmodified.txt` and `<scratch>/repro-probe-seed.txt`, and
match design.md's Context table row for row.

The two probe scripts, as they stand in the scratchpad (which is not
durable). `<scratch>/pyproject.toml`, beside them, gives the fixtures a
project root:

```toml
# Throwaway manifest so the reproduction script is a project's source.

[tool.machinome]
model = "repro_repeat_index:Pair"
```

`<scratch>/repro_repeat_index.py`:

```python
"""Reproduce: a `.repeat()` copy's `index` is not readable by a callable
CLASS-declared joint argument (axis, at, carries, range) of the repeated
class, nor by a frame argument or `check()`, because the copy is stamped
after its construction returns.

Run: env -C <bench> PYTHONPATH=<bench> .venv/bin/python <this file>
"""

import os
import sys
import traceback

os.environ.setdefault(
    'SOLID_BUILD_DIR',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '_build'))

from solid2 import cube

import machinome
from machinome.motion.joints import Orbit, Revolute, declared_joints
from machinome.node.assembly import AssemblyNode
from machinome.node.solid2 import Solid2Node

print('machinome from', machinome.__file__)

if os.environ.get('PROBE_SEED'):
    # Probe of the proposed shape, patched in at run time only: the copy
    # is allocated, its index seeded into its own instance dict, and only
    # then initialized; the post-construction stamp is kept.
    from machinome.node import declarative
    from machinome.parameters import ParameterError
    from machinome.node.declarative import evaluate

    def construct(self, values, owner, index=None):
        called = ()
        if self.wiring:
            from machinome.motion.mates import call_freedom_functions
            called = call_freedom_functions(self, owner)
        args = [evaluate(arg, values) for arg in self.args]
        kwargs = {key: evaluate(arg, values)
                  for key, arg in self.kwargs.items()}
        cls = self.node_class
        child = cls.__new__(cls, *args, **kwargs)
        if isinstance(child, cls):
            if index is not None:
                child.__dict__['index'] = index
            child.__init__(*args, **kwargs)
        if called:
            from machinome.motion.mates import resolve_freedom_functions
            resolve_freedom_functions(child, called)
        if self.wiring:
            self._record_wiring(child, owner)
        if self.site_joints:
            self._resolve_site_joints(child, owner)
        return child

    def realize(self, values, owner):
        count = evaluate(self.count, values)
        if isinstance(count, float) and count.is_integer():
            count = int(count)
        copies = []
        for index in range(count):
            child = self.declaration.realize(values, owner, index=index)
            child.__dict__['index'] = index
            copies.append(child)
        return copies

    declarative.ChildDeclaration.realize = construct
    declarative.RepeatDeclaration.realize = realize
    print('PROBE: index seeded before __init__')


def run(label, build):
    try:
        result = build()
    except Exception as failure:
        print(f'[{label}] RED: {type(failure).__name__}: {failure}')
        return None
    print(f'[{label}] ok: {result}')
    return result


class Guide(Solid2Node):
    turn = Revolute(axis=lambda node: (0, 0, 1 if node.index == 0 else -1),
                    at=lambda node: (10.0 * node.index, 0, 0),
                    range=lambda node: (0, 90 + node.index),
                    unit='deg')

    def render(self):
        return cube(1, center=True)


class Pair(AssemblyNode):
    guides = Guide().repeat(2)


def axes():
    pair = Pair()
    return [declared_joints(type(guide))['turn'].arguments(guide)
            for guide in pair.guides]


run('axis/at/range of a repeated class', axes)


def bound():
    pair = Pair()
    placed = []
    for guide in pair.guides:
        guide.turn = 30
        run = guide.__dict__['_joint_motion']['turn']
        placed.append((guide.name, guide.index,
                       [operation.serialized for operation in run]))
    return placed


run('each copy bound to 30', bound)


class Roller(Solid2Node):
    spin = Orbit(axis=(0, 0, 1), at=(0, 0, 0),
                 carries=lambda node: (5.0 + node.index, 0, 0), unit='deg')

    def render(self):
        return cube(1, center=True)


class Rollers(AssemblyNode):
    rollers = Roller().repeat(2)


def carried():
    rollers = Rollers()
    return [declared_joints(type(roller))['spin'].arguments(roller)[3]
            for roller in rollers.rollers]


run('carries of a repeated class', carried)


from machinome.node.frames import Frame, resolved_frames
from machinome.parameters import Length


class Seated(Solid2Node):
    seat = Frame(at=lambda node: (0, 0, 3.0 * node.index))

    def render(self):
        return cube(1, center=True)


class Seats(AssemblyNode):
    seats = Seated().repeat(2)


run('frame at of a repeated class',
    lambda: [resolved_frames(s)['seat'] for s in Seats().seats])


class Checked(Solid2Node):
    size = Length(1.0, min=0)

    def check(self):
        self.seen = self.index

    def render(self):
        return cube(1, center=True)


class CheckedPair(AssemblyNode):
    items = Checked().repeat(2)


run('check() reads index', lambda: [c.seen for c in CheckedPair().items])


def other_failure():
    class Wrong(Solid2Node):
        turn = Revolute(axis=lambda node: node.no_such_thing, unit='deg')

        def render(self):
            return cube(1, center=True)

    class Wrongs(AssemblyNode):
        items = Wrong().repeat(2)

    Wrongs()


run('a callable failing for another reason', other_failure)
```

`<scratch>/seed_probe.py` (Stage P's suite probe, design.md "Suite under
the probe"):

```python
"""Install the proposed seeding from outside the bench, as a pytest plugin
(`-p seed_probe`) or by import: a `.repeat()` copy is allocated, its
`index` seeded into its own instance dict, and only then initialized; the
stamp after construction is kept. The non-repeated path is untouched
(`index=None` constructs exactly as before)."""

import os

from machinome.node import declarative
from machinome.node.declarative import evaluate

_LOG = os.environ.get('SEED_PROBE_LOG')
_original_child_realize = declarative.ChildDeclaration.realize
_original_repeat_realize = declarative.RepeatDeclaration.realize


def _construct(self, values, owner, index=None):
    if index is None:
        return _original_child_realize(self, values, owner)
    called = ()
    if self.wiring:
        from machinome.motion.mates import call_freedom_functions

        called = call_freedom_functions(self, owner)
    args = [evaluate(arg, values) for arg in self.args]
    kwargs = {key: evaluate(arg, values) for key, arg in self.kwargs.items()}
    node_class = self.node_class
    child = node_class.__new__(node_class, *args, **kwargs)
    if isinstance(child, node_class):
        child.__dict__['index'] = index
        type(child).__init__(child, *args, **kwargs)
    if called:
        from machinome.motion.mates import resolve_freedom_functions

        resolve_freedom_functions(child, called)
    if self.wiring:
        self._record_wiring(child, owner)
    if self.site_joints:
        self._resolve_site_joints(child, owner)
    if _LOG:
        with open(_LOG, 'a') as log:
            log.write(f'{node_class.__qualname__} {index}\n')
    return child


def _realize(self, values, owner):
    count = evaluate(self.count, values)
    if isinstance(count, float) and count.is_integer():
        count = int(count)
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        return _original_repeat_realize(self, values, owner)
    copies = []
    for index in range(count):
        child = self.declaration.realize(values, owner, index=index)
        child.__dict__['index'] = index
        copies.append(child)
    return copies


declarative.ChildDeclaration.realize = _construct
declarative.RepeatDeclaration.realize = _realize
```

### 1.3 Focused tests

`pytest -q -p no:cacheprovider tests/test_declarative_nodes.py
tests/test_joints.py tests/test_frames.py` (exit 0):

```
313 passed, 5 warnings, 409 subtests passed in 5.94s   (wall 7.07 s)
```

### 1.4 The originating project, unmodified bench

`git -C <Prusa> status --short`: empty. The documented run (exit 1, wall
41.14 s; `<scratch>/apply-baseline/prusa.log`):

```
Ran 19 tests in 37.75 seconds: 17 passed, 2 failed (mesh engine, volume epsilon 0 mm³)
```

The two failures:

- `PrusaI3Test.test_the_gear_pair_drives_at_every_feed`: `AssertionError:
  big_gear should be blocked at 1.5deg against small_gear (no
  intersection)`;
- `PrusaI3Test.test_x_home_meets_the_switch`: `AssertionError: bearings-0
  should be blocked displaced 1.0mm along [-1, 0, 0] against switch (no
  intersection)`.

These are design.md's two pre-existing failures. The wall time is a
quarter of Stage P's 169 s; the count and the failures are the same.
`git -C <Prusa> status --short` after the run: empty.

## 2. Red tests, on the unmodified source (e41e759)

New class `RepeatIndexDuringConstructionTest` in
`tests/test_declarative_nodes.py`, after `RepeatIndexTest`. The fixtures
that realize (`Guide`/`GuidePair`, `Roller`/`Rollers`, `Seated`/`Seats`,
`Checked`/`CheckedPair`, `Stubborn`/`Stubborns`, `Guards`) are at module
level beside `Bead`/`Ranked`/`Half`. The two fixtures that exist only to
be refused (`Wrong`/`Wrongs`, and `Single` holding one plain `Guide`) are
defined inside their tests, as the module's other refusal tests define
theirs, so no module-level class of the test module fails to realize.
Task 2.1's three assertions are three tests (arguments, placement,
identity). `pytest -q -p no:cacheprovider -rA tests/test_declarative_nodes.py
-k RepeatIndexDuringConstructionTest` (exit 1;
`<scratch>/apply-baseline/section2.log`):

```
6 failed, 4 passed, 82 deselected, 9 subtests passed in 0.75s   (wall 1.07 s)
```

| Test | Task | Before the change |
|---|---|---|
| `test_each_copy_resolves_its_own_joint_arguments` | 2.1 | RED: `ParameterError: Guide.turn: axis -- the callable raised AttributeError: 'Guide' object has no attribute 'index'` |
| `test_each_copy_is_placed_by_its_own_joint` | 2.1 | RED: the same |
| `test_the_copies_keep_one_identity` | 2.1 | RED: the same |
| `test_an_orbits_carried_point_reads_the_copys_position` | 2.2 | RED: `ParameterError: Roller.spin: carries -- the callable raised AttributeError: 'Roller' object has no attribute 'index'` |
| `test_a_frame_argument_reads_the_copys_position` | 2.3 | RED: `ParameterError: Seated.seat: frame argument at -- the callable raised AttributeError: 'Seated' object has no attribute 'index'` |
| `test_a_check_reads_the_copys_position` | 2.3 | RED: `AttributeError: 'Checked' object has no attribute 'index'` |
| `test_a_callable_failing_for_another_reason_is_refused` | 2.4 (a) | green |
| `test_a_single_child_still_has_no_index` | 2.4 (b) | green |
| `test_a_copy_ends_with_its_position_over_its_own` | 2.5 (a) | green |
| `test_a_legacy_repeat_realizes_with_names_and_positions` | 2.5 (b) | green |

The existing guards, `RepeatIndexTest`,
`SiteJointCallableTest.test_a_copys_index_is_not_reachable_from_a_site_callable`
and `tests/test_joints.py`'s `ArgumentResolutionTest`, are green in 1.3's
run.

## 3. The change

`machinome/node/declarative.py`, design.md Decision 2 as written:

- `ChildDeclaration.realize(self, values, owner, index=None)`; its
  docstring gains a paragraph saying what `index` is and that only
  `RepeatDeclaration.realize` passes it;
- `ChildDeclaration._construct(self, args, kwargs, index)` replaces the
  plain `self.node_class(*args, **kwargs)`: with no `index` it is that
  plain call; with one it calls `node_class.__new__`, and when the result
  is an instance of `node_class` writes `child.__dict__['index'] = index`
  and calls `type(child).__init__(child, *args, **kwargs)`;
- `RepeatDeclaration.realize` passes `index=index` and keeps its stamp
  after construction; the comment that gave the old timing ("AFTER
  construction ... No sighting needs `index` during construction") is
  replaced by Decision 2's three lines.

`tests/test_declarative_nodes.py`: the docstring of
`SiteJointCallableTest.test_a_copys_index_is_not_reachable_from_a_site_callable`
now gives as its reason that a site callable is handed the declaring
parent, with no copy in scope; the sentence "stamped ... AFTER the copy's
construction" is gone. Its code and assertions are unchanged.

### 3.3 Green

`pytest -q -p no:cacheprovider -rA tests/test_declarative_nodes.py -k
RepeatIndexDuringConstructionTest` (exit 0;
`<scratch>/apply-after/section2.log`): all ten tests `PASSED`.

```
10 passed, 82 deselected, 9 subtests passed in 1.00s   (wall 1.47 s)
```

1.3's files (exit 0): 1.3's count plus the ten new tests and their nine
subtests.

```
323 passed, 5 warnings, 418 subtests passed in 6.10s   (wall 7.27 s)
```

`env -C <bench> PYTHONPATH=<bench> .venv/bin/python
<scratch>/repro_repeat_index.py`, without `PROBE_SEED` (exit 0):

```
machinome from /home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py
[axis/at/range of a repeated class] ok: [((0, 0, 1), (0.0, 0.0, 0.0), (0, 90)), ((0, 0, -1), (10.0, 0.0, 0.0), (0, 91))]
[each copy bound to 30] ok: [('guides-0', 0, [['r', '30', [0, 0, 1]]]), ('guides-1', 1, [['t', ['-10.0', '-0.0', '-0.0']], ['r', '30', [0, 0, -1]], ['t', ['10.0', '0.0', '0.0']]])]
[carries of a repeated class] ok: [(5.0, 0.0, 0.0), (6.0, 0.0, 0.0)]
[frame at of a repeated class] ok: [<frame at=(0.0, 0.0, 0.0) x=(1, 0, 0) y=(0, 1, 0) z=(0, 0, 1)>, <frame at=(0.0, 0.0, 3.0) x=(1, 0, 0) y=(0, 1, 0) z=(0, 0, 1)>]
[check() reads index] ok: [0, 1]
[a callable failing for another reason] RED: ParameterError: Wrong.turn: axis -- the callable raised AttributeError: 'Wrong' object has no attribute 'no_such_thing'
```

Identical (`diff`) to Stage P's probe run `<scratch>/repro-probe-seed.txt`
with its `PROBE:` line removed: the probe column of design.md's table.

## 4. The originating project, after the change

`git -C <Prusa> status --short`: empty. The documented run (exit 1, wall
58.48 s; `<scratch>/apply-after/prusa.log`):

```
Ran 19 tests in 55.18 seconds: 17 passed, 2 failed (mesh engine, volume epsilon 0 mm³)
```

The same two failures, with the same messages:
`PrusaI3Test.test_the_gear_pair_drives_at_every_feed` (`big_gear should be
blocked at 1.5deg against small_gear (no intersection)`) and
`PrusaI3Test.test_x_home_meets_the_switch` (`bearings-0 should be blocked
displaced 1.0mm along [-1, 0, 0] against switch (no intersection)`). With
every duration masked (`sed -E 's/[0-9]+\.[0-9]+ ?s(econds)?//g;
s/[0-9]+(\.[0-9]+)?s\b//g'`), the 1408-line logs before and after are
identical (`diff`: no line differs). `git -C <Prusa> status --short` after
the run: empty.

## 5. Manual, ADR and changelog

- `docs/concepts/joints.rst`, "Arguments": the sentence "A ``repeat()``
  copy's ``index`` does not exist yet when its joint arguments resolve,
  so derive a per-copy joint argument from the parent's placement, or
  drive the per-copy difference through a broadcast relation's ``law=``."
  is replaced in place by design.md Decision 6's sentence, which is
  shorter.
- `docs/architecture.md`: "(not yet assigned when a site's arguments
  resolve)" becomes "(it is handed the parent, not the copy)"; "a plain
  0-based instance attribute `RepeatDeclaration.realize` stamps AFTER
  construction" becomes "... attribute that `RepeatDeclaration.realize`
  writes before the copy's construction runs".
- `docs/adrs/NODE/ADR-096-a-relation-broadcasts-over-a-repeated-child.md`:
  a final section "Amendment (2026-10-06, change
  `resolve-repeated-joints-per-copy`)" saying Decision 4's three things
  (written before the constructor and again after; `check()`, joint and
  frame arguments read it, resolving where they always did; identity,
  naming and refusal unchanged). The decision text above it is not
  edited. `docs/adrs/README.md`: ADR-096's line ends "**Accepted**,
  extends 089, depends on 061/063/093, amended 2026-10-06".
- `docs/project/changelog.rst`: one bullet, "A repeated copy reads its
  index while it is constructed", under the existing `Unreleased`
  section, after the children-refuse-early-reads bullet, naming the
  change.

5.5, the grep of the manual for the old timing, `docs/` without `adrs/`
and `releases/`:

```
grep -rn -i "index" <bench>/docs --include=*.rst --include=*.md --include=*.txt \
  | grep -v "/adrs/\|/releases/" \
  | grep -i "not yet\|does not exist\|after construction\|AFTER construction\|doesn't exist\|not exist"
grep -rn -A2 -B2 "\`\`index\`\`\|\`index\`\|node\.index" <bench>/docs --include=*.rst --include=*.md \
  | grep -v "/adrs/\|/releases/" | grep -i "yet\|exist\|after\|stamp"
grep -rn -i "stamp" <bench>/docs --include=*.rst --include=*.md | grep -v "/adrs/\|/releases/" | grep -i index
```

No output from any of the three. The same first pattern over
`machinome/`, `openspec/specs/` and `README.md`: no output. The remaining
mentions of a copy's `index` outside the ADRs are the two edited
`architecture.md` sentences, the new changelog bullet and
`docs/concepts/relations.rst:78` ("a resolved parameter, a copy's
``index``", a list of what a law may read, still true).
`docs/howto/repeat-and-vary.rst` is not edited (design.md Decision 6).

## 6. Checks

The checks ran after sections 7 and 8, so that the full suite covers the
synced spec, the archived change and the moved wart as well as the code.

### 6.1 Lint, against HEAD

`flake8 --max-line-length=89 machinome/node/declarative.py
tests/test_declarative_nodes.py` on the tree, and the same on the two
files as they stand at HEAD (`git show HEAD:<file>` into
`<scratch>/head/`):

```
now:  declarative.py:42 E127, :474 E127;
      test_declarative_nodes.py:24 E127, :33 E127, :1107 E128, :1119 F841,
      :1313 F401 (node_classes_in), :1318 E128
HEAD: declarative.py:42 E127, :474 E127;
      test_declarative_nodes.py:23 F401 ('machinome.motion.joints.Orbit'
      imported but unused), :24 E127, :32 E127, :925 E128, :937 F841,
      :1131 F401 (node_classes_in), :1136 E128
```

Every finding on the tree is one that HEAD has, at a line moved by the
insertion; none is in a changed line. One fewer than HEAD: `Orbit`, an
unused import at HEAD, is now used by `Roller`. `black --check` (26.5.1,
the venv's) on the same two files: "2 files would be reformatted", now and
at HEAD alike; the repository is not black-formatted and the CI step is
`continue-on-error`, and the new code follows the surrounding style.

### 6.2 Full suite

`pytest -q -p no:cacheprovider` at the bench root, alone, after the
archive (exit 0; `<scratch>/apply-after/suite.log`; no `Too many open
files` in the log):

```
4644 passed, 4 skipped, 55 warnings, 6642 subtests passed in 669.68s (0:11:09)   (wall 672.12 s)
```

The unmodified bench reads `4634 passed, 4 skipped, 6619 subtests`, and so
did Stage P's run with the change installed from outside; the ten new
tests account for the passed count. Of the 23 further subtests, the new
tests account for nine. The other fourteen were not traced to a test:
every test file that scans the tree, its modules or its records
(`test_docs_structure`, `test_release_records`, `test_docs_exports`,
`test_core_names_no_split_words`, `test_core_names_no_scad`,
`test_core_kernel_free`, `test_leaf_capability_set`,
`test_node_root_exports_nothing`, `test_named_models`,
`test_verdict_store`, `test_expression_type`, `test_meta`,
`test_machinome_identity`, `test_content_verified_currency`,
`test_flexible_document`) counts the same subtests on the tree as on a
copy of HEAD (`git archive HEAD` into `<scratch>/headtree/`, each file run
in both). The previous cycle recorded eight such untraced subtests on
the same suite. Every subtest passed; no test failed or was skipped
beyond the four the unmodified bench skips.

## 7. Warts

- 7.1: the second entry of "joint-frame-follows-declarer (2026-09-10)"
  moved verbatim (checked by string containment against `git show
  HEAD:workflow/warts.md`) to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md`, under
  `` ## `resolve-repeated-joints-per-copy` ``, preceded by the line naming
  its section, as the file's other entries are, and followed by a "What
  shipped" paragraph (the copy seeded before construction; joint
  arguments, frame arguments and `check()` reading it; resolution not
  moved; the ADR-096 amendment; the projects keeping their workarounds;
  Prusa3-vanilla's run unchanged). Deleted from `workflow/warts.md`; the
  section keeps its first entry, and its opening sentence, "Two things it
  raised remain.", now reads "One thing it raised remains." The standing
  triage's "Planned, never done" bullet "**A `.repeat()` copy's joint
  arguments resolve before `index` exists**" is deleted.
- `workflow/ongoing/fix-warts-3.md`: a Progress line for this cycle, after
  cycle 3's.

## 8. Sync and archive

- 8.1: the delta's one ADDED requirement, "A repeated copy carries its
  position throughout its own construction", with its five scenarios,
  copied into `openspec/specs/declarative-nodes/spec.md` after
  "Class-body child declarations" (the delta's body is contained verbatim
  in the spec); no existing requirement edited. `openspec validate
  declarative-nodes`: "Specification 'declarative-nodes' is valid".
- `openspec validate resolve-repeated-joints-per-copy` before archiving:
  "Change 'resolve-repeated-joints-per-copy' is valid".
- `openspec archive resolve-repeated-joints-per-copy --yes --skip-specs`
  (the spec was synced by hand in 8.1, so the CLI's own sync, which would
  add the requirement a second time, was skipped): "Change
  'resolve-repeated-joints-per-copy' archived as
  '2026-10-06-resolve-repeated-joints-per-copy'". Its warnings: the Why
  section's length, and 21 of 25 tasks complete (6.1, 6.2, 8.2 and 8.3,
  done after it and ticked in the archived copy).
- `openspec validate --specs`: `Totals: 45 passed, 0 failed (45 items)`.
- 8.3: 1.3's files, which hold section 2's tests, once more after the
  archive (exit 0): `323 passed, 5 warnings, 418 subtests passed in
  7.62s` (wall 8.97 s), as in 3.3.
- Nothing committed on the bench, and nothing in Prusa3-vanilla edited.

## Records that differ from the letter of the plan

- Task 2.1's three assertions are three tests, and the two refusal
  fixtures of 2.4 are defined inside their tests (section 2).
- The checks of section 6 ran after sections 7 and 8 (section 6).
- The warts section's opening sentence was changed to count the one entry
  it keeps, and a Progress line was added to the campaign plan (section 7).

The code is design.md Decision 2 as written, and the manual, ADR and
changelog edits are Decisions 4 and 6 as written; design.md and tasks.md
needed no revision.
