# Evidence — `clocked-snapshot-identity`

Cycle 9 of the fix-warts-3 campaign (`workflow/ongoing/fix-warts-3.md`).
Bench `machinome/WTs/fix-warts-3`, branch `fix-warts-3`, planning commit
bdf0bcf (`git -C <bench> rev-parse HEAD` printed
`bdf0bcfce42676492cf9e1ca57a09fc9a1e7f2ab`). Every framework command below
ran as
`env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1 /home/asa/devel/machinome/.venv/bin/<tool> ...`,
one process at a time, never in parallel (`ps -eo pid,args | grep
'[p]ytest\|[m]achinome test\|[m]achinome snapshot\|[m]achinome build'`
printed nothing before the first run). The interpreter check,
`python -c 'import machinome; print(machinome.__file__)'`, printed
`/home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py`.

`<project>` is `/home/asa/devel/machinome/projects/Calculators/Curta-Type-I-3x`,
branch `main`, head `1f3dc22` (`git -C <project> rev-parse --short HEAD`).
It was read and run, never written. Every Curta command ran as
`env -C <scratch> PYTHONPATH=<bench>:<project> PYTHONDONTWRITEBYTECODE=1 SOLID_BUILD_DIR=<scratch>/build /home/asa/devel/machinome/.venv/bin/<tool> ...`,
with `-p no:cacheprovider` for pytest. `git -C <project> status --short`
listed the same four untracked entries before and after every Curta run
(`"3D Printed Curta Calculator Assembly_720p.mp4"`, `CREDITS`,
`curta-2x-files/`, `screenshots/reverser_inspection.png`).

`<scratch>` is the campaign scratchpad's `cycle9/` directory
(`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle9/`).
It is not durable; the scripts this record depends on are copied below.
`<focused>` is `tests/test_clocked_sim.py tests/test_clocked_identity.py
tests/test_clocked_time.py tests/test_clocked_corpus.py`.

## 1. Baseline on the unmodified tree (bdf0bcf)

### 1.1 The scripts

`<scratch>/probe_tests.py`, run from the bench root (`<scratch>` holds a
`pyproject.toml` declaring `[tool.machinome] model = "repro_bench:Counter"`,
so the script's classes have a project root):

```python
"""Probe the red tests' fixture shape: one factory, same module, same
qualname, same bank; a changed joint range or commit law changes the
identity, and the unmodified bench restores across both."""

from machinome.motion.joints import Revolute
from machinome.node.assembly import AssemblyNode
from machinome.simulation import Driver, Sim, State

from tests.clocked_project.counter import DIGIT, advance, strokes
from tests.clocked_project.parts import Dial


def skipping(sources, targets):
    """The counter's law advancing the units by two."""
    return lambda crank, units, tens: ((units + 2) % 10,
                                       (tens + (units >= 8)) % 10)


def counter(stop=324.0, law=advance):
    class Counter(AssemblyNode):
        crank = Driver(default=0, unit='deg')
        units = State(default=0, range=(0, 9), dtype=int)
        tens = State(default=0, range=(0, 9), dtype=int)

        units_dial = Dial(turn=Revolute(axis=(0, 0, 1), unit='deg',
                                        range=(0, stop)))
        tens_dial = Dial()

        (crank & units & tens).commits((units, tens), at=strokes, law=law)

        units.drives(units_dial.turn, ratio=DIGIT)
        tens.drives(tens_dial.turn, ratio=DIGIT)

    return Counter


def taken():
    sim = Sim(counter()())
    sim.move('crank', by=1080.0)
    return sim.snapshot()


for label, other in (('same', counter()),
                     ('range 324 -> 360', counter(stop=360.0)),
                     ('law advance -> skipping', counter(law=skipping))):
    saved = taken()
    sim = Sim(other())
    before = dict(sim.state)
    print(label, other.__module__, other.__qualname__,
          'model equal', saved.model == sim._clocked.model,
          'identity equal', Sim(counter()())._clocked.identity
          == sim._clocked.identity)
    try:
        sim.restore(saved)
    except Exception as failure:
        print('  refused', type(failure).__name__, failure)
        print('  unchanged', sim.state == before)
    else:
        print('  accepted', sim.state,
              'units dial', sim.node.units_dial.turn.value)
```

`<scratch>/curta_restore.py`, run with the project on `sys.path`:

```python
"""The originating project's reproduction: a snapshot of the clocked Curta
restored into the same machine (accepted before and after the change), into
a same-named machine whose one range changed (accepted today, refused after),
and into an unchanged same-named class from another module.

Run with the project on sys.path and a scratch SOLID_BUILD_DIR; nothing is
written into the project.
"""

import time

from machinome.motion.joints import Bound, Prismatic
from machinome.simulation import Sim
from simulation.clocked import ClockedCurta
from simulation.clocked_laws import at_rest
from simulation.clocked_parts import Operation


class TighterOperation(Operation):
    """`Operation` with the crank's lift stopping at 8 mm, not 9."""

    crank_lift = Prismatic(axis=(0, 0, 1), range=(
        Bound(lambda own, crank: own * (1 - at_rest(crank)),
              reads=(Operation.crank,)),
        Bound(lambda own, crank: own + (8 - own) * at_rest(crank),
              reads=(Operation.crank,))))


class EventDrivenCurta(ClockedCurta):
    """The Curta, one range changed, under the original's module and name."""

    __module__ = 'simulation.event_driven'
    __qualname__ = 'EventDrivenCurta'

    operation = TighterOperation()


Changed = EventDrivenCurta


class EventDrivenCurta(ClockedCurta):  # noqa: F811
    """The Curta unchanged, a same-named class in another module."""


Elsewhere = EventDrivenCurta


def attempt(label, saved, target):
    started = time.perf_counter()
    other = Sim(target())
    built = time.perf_counter() - started
    print(f'{label}:')
    print(f'  class    {target.__module__}.{target.__qualname__}')
    print(f'  model    equal: {saved.model == other._clocked.model}')
    print(f'  identity {other._clocked.identity[:16]}  (built {built:.2f} s)')
    try:
        other.restore(saved)
    except Exception as failure:
        print(f'  REFUSED  {type(failure).__name__}: {failure}')
    else:
        print(f'  ACCEPTED result digits '
              f'{[other.state[f"result_{i}.value"] for i in range(4)]}')


started = time.perf_counter()
sim = Sim(ClockedCurta())
print(f'ClockedCurta constructed in {time.perf_counter() - started:.2f} s')
print(f'  identity {sim._clocked.identity[:16]}')
sim.move('digit_1', to=7)
sim.trigger('Turn crank')
sim.trigger('Turn crank')
saved = sim.snapshot()
print(f'  snapshot after 7 x 2: result digits '
      f'{[saved.values[f"result_{i}.value"] for i in range(4)]}')

attempt('same machine, fresh instance', saved, ClockedCurta)
attempt('one range changed (crank_lift high 9 -> 8 mm)', saved, Changed)
attempt('unchanged, same-named class in another module', saved, Elsewhere)
```

### 1.2 The bench probe

`python <scratch>/probe_tests.py`, output identical to Stage P's
`probe_tests.before.out` (`diff`, no output):

```
same __main__ counter.<locals>.Counter model equal True identity equal True
  accepted {'crank': 1080.0, 'tens': 0, 'units': 3} units dial 108.0
range 324 -> 360 __main__ counter.<locals>.Counter model equal True identity equal False
  accepted {'crank': 1080.0, 'tens': 0, 'units': 3} units dial 108.0
law advance -> skipping __main__ counter.<locals>.Counter model equal True identity equal False
  accepted {'crank': 1080.0, 'tens': 0, 'units': 3} units dial 108.0
```

### 1.3 The Curta's restores

`/usr/bin/time -f 'wall %e s' python <scratch>/curta_restore.py`:

```
ClockedCurta constructed in 1.91 s
  identity c7286b3be65803cc
  snapshot after 7 x 2: result digits [4, 1, 0, 0]
same machine, fresh instance:
  class    simulation.event_driven.EventDrivenCurta
  model    equal: True
  identity c7286b3be65803cc  (built 1.63 s)
  ACCEPTED result digits [4, 1, 0, 0]
one range changed (crank_lift high 9 -> 8 mm):
  class    simulation.event_driven.EventDrivenCurta
  model    equal: True
  identity 73974bcd5dfebaf1  (built 1.66 s)
  ACCEPTED result digits [4, 1, 0, 0]
unchanged, same-named class in another module:
  class    __main__.EventDrivenCurta
  model    equal: True
  identity cc13707b2bc0f349  (built 1.53 s)
  ACCEPTED result digits [4, 1, 0, 0]
wall 10.30 s
```

All three accepted; the second and third run machines whose identities
differ from the first's.

### 1.4 The Curta's operation tests

`/usr/bin/time -f 'wall %e s' pytest -p no:cacheprovider -q --durations=5
<project>/simulation/test_event_driven.py::EventDrivenOperationsTest`:

```
6.65s call  ...::test_ratchet_stop_survives_repeated_reverse_requests
4.90s call  ...::test_full_register_carry_and_all_clearing_stations
4.09s call  ...::test_recorded_running_oracle
3.52s call  ...::test_separate_register_clearing_in_both_directions
2.32s call  ...::test_borrow_undo_shift_and_restore
11 passed, 57 subtests passed in 35.33s
wall 36.34 s
```

### 1.5 The focused tests

`/usr/bin/time -f 'wall %e s' pytest -p no:cacheprovider -q <focused>`:
`145 passed, 195 subtests passed in 6.05s` (wall 7.09 s).

## 2. Red tests, on the unmodified source

`tests/test_clocked_identity.py` gains the imports of tasks.md 2.1, the
module-level `skipping` and `restated` of design.md Decision 3, and the
class `SnapshotIdentityTest` with the four tests of Decision 3. Tests 3 and
4 share a helper, `assertRefused(model)`, which takes the snapshot over
`restated()()` after `move('crank', by=1080.0)`, asserts the two
preconditions (the target's `snapshot().model` equals the snapshot's
`model`; the target's `sim.identity` differs from the source simulation's
`sim.identity`), then asserts the refusal: `ValueError`, a message holding
the source's identity, the target's identity and
`Counter(crank,tens,units)`, and the target's `sim.state` and
`units_dial.turn.value` as they stood before the call. The preconditions
read the source simulation's `sim.identity` and not the snapshot's, so on
the unmodified tree they run and pass, and the red is the restore being
accepted and nothing else.

`pytest -p no:cacheprovider -q tests/test_clocked_identity.py::SnapshotIdentityTest`:

```
tests/test_clocked_identity.py:142: in assertRefused
    with self.assertRaises(ValueError) as caught:
E   AssertionError: ValueError not raised
tests/test_clocked_identity.py:142: in assertRefused
    with self.assertRaises(ValueError) as caught:
E   AssertionError: ValueError not raised
E       AttributeError: 'ClockedSnapshot' object has no attribute 'identity'
tests/test_clocked_identity.py:154: AttributeError
FAILED tests/test_clocked_identity.py::SnapshotIdentityTest::test_a_machine_whose_commit_law_changed_refuses_the_snapshot
FAILED tests/test_clocked_identity.py::SnapshotIdentityTest::test_a_machine_whose_range_changed_refuses_the_snapshot
FAILED tests/test_clocked_identity.py::SnapshotIdentityTest::test_a_snapshot_carries_the_machines_identity
3 failed, 1 passed in 1.19s
```

| test | before |
|---|---|
| `test_a_snapshot_carries_the_machines_identity` | RED: `AttributeError: 'ClockedSnapshot' object has no attribute 'identity'` |
| `test_a_snapshot_restores_into_the_same_machine` | green (guard) |
| `test_a_machine_whose_range_changed_refuses_the_snapshot` | RED: `AssertionError: ValueError not raised`, preconditions passing |
| `test_a_machine_whose_commit_law_changed_refuses_the_snapshot` | RED: `AssertionError: ValueError not raised`, preconditions passing |

## 3. The change

- `machinome/simulation/clocked.py`, `ClockedSnapshot`: `__slots__ =
  ('model', 'values', 'identity')`, `__init__(self, model, values,
  identity)`, and the docstring of design.md Decision 1. `__repr__`
  unchanged.
- `Clocked.__init__`: `self.initial = ClockedSnapshot(self.model,
  self.bank, self.identity)`. `Clocked.snapshot()`: the same.
- `Clocked.restore`: the `model` comparison is replaced by
  `snapshot.identity != self.identity`, raising the `ValueError` of
  Decision 2 (`that snapshot was taken over <model>, the machine
  <identity>, and this simulation runs <model>, the machine <identity>. A
  snapshot restores into the machine it was taken from: its drivers, its
  states and its relations are what its bank means.`). The `isinstance`
  check and `self._posed(dict(snapshot.values))` are unchanged.
- `tests/test_clocked_sim.py::BoundTest::test_a_restore_whose_pose_is_refused_changes_nothing`
  takes `saved = sim.snapshot()` and builds
  `ClockedSnapshot(saved.model, {'crank': 0.0, 'value': 3}, saved.identity)`.
  Assertions unchanged.

A search of the bench for `ClockedSnapshot` (`grep -rn` over `*.py`,
`*.rst`, `*.md`) finds no other constructor call; `tests/test_snapshot.py`'s
`ClockedSnapshotTest` is a test of `machinome snapshot` on a clocked model
and does not touch the class.

### 3.5 Green

- `pytest -p no:cacheprovider -q tests/test_clocked_identity.py::SnapshotIdentityTest`:
  `4 passed in 1.01s`.
- `pytest -p no:cacheprovider -q <focused>`: `149 passed, 195 subtests
  passed in 6.35s` (wall 7.35 s): 1.5's counts plus the four tests.

### 3.6 Files under `tests/`

`git -C <bench> status --short` lists ` M machinome/simulation/clocked.py`,
` M tests/test_clocked_identity.py`, ` M tests/test_clocked_sim.py`, and no
corpus file: `tests/clocked-corpus.json` is byte-identical.

## 4. The originating project after the change

### 4.1 The Curta's restores

`/usr/bin/time -f 'wall %e s' python <scratch>/curta_restore.py` (the two
refusal messages each list the Curta's 41 bank ids twice; shortened here
to `EventDrivenCurta(carriage_elevation,…,turns_5.value)`, the full text is
in the run's output):

```
ClockedCurta constructed in 1.83 s
  identity c7286b3be65803cc
  snapshot after 7 x 2: result digits [4, 1, 0, 0]
same machine, fresh instance:
  class    simulation.event_driven.EventDrivenCurta
  model    equal: True
  identity c7286b3be65803cc  (built 1.59 s)
  ACCEPTED result digits [4, 1, 0, 0]
one range changed (crank_lift high 9 -> 8 mm):
  class    simulation.event_driven.EventDrivenCurta
  model    equal: True
  identity 73974bcd5dfebaf1  (built 1.66 s)
  REFUSED  ValueError: that snapshot was taken over EventDrivenCurta(carriage_elevation,…,turns_5.value), the machine c7286b3be65803cc279920722cb59c440e7616d93d74dbfac5eb1b232dbcb6be, and this simulation runs EventDrivenCurta(carriage_elevation,…,turns_5.value), the machine 73974bcd5dfebaf1fc406c57c8cc650760412da47e2035394a361fc18f9f9c98. A snapshot restores into the machine it was taken from: its drivers, its states and its relations are what its bank means.
unchanged, same-named class in another module:
  class    __main__.EventDrivenCurta
  model    equal: True
  identity cc13707b2bc0f349  (built 1.47 s)
  REFUSED  ValueError: that snapshot was taken over EventDrivenCurta(carriage_elevation,…,turns_5.value), the machine c7286b3be65803cc279920722cb59c440e7616d93d74dbfac5eb1b232dbcb6be, and this simulation runs EventDrivenCurta(carriage_elevation,…,turns_5.value), the machine cc13707b2bc0f349c37d87140b74c4e6e444f905e9fbc5ca60544dca32cc8692. A snapshot restores into the machine it was taken from: its drivers, its states and its relations are what its bank means.
wall 10.15 s
```

Accepted, refused, refused, as expected.

### 4.2 The Curta's operation tests

The command of 1.4:

```
6.52s call  ...::test_ratchet_stop_survives_repeated_reverse_requests
4.98s call  ...::test_full_register_carry_and_all_clearing_stations
3.95s call  ...::test_recorded_running_oracle
3.71s call  ...::test_separate_register_clearing_in_both_directions
2.40s call  ...::test_borrow_undo_shift_and_restore
11 passed, 57 subtests passed in 35.70s
wall 36.72 s
```

| run | counts | pytest | wall |
|---|---|---|---|
| before (1.4) | 11 passed, 57 subtests passed | 35.33 s | 36.34 s |
| after (4.2) | 11 passed, 57 subtests passed | 35.70 s | 36.72 s |

### 4.3 The bench probe

`python <scratch>/probe_tests.py`:

```
same __main__ counter.<locals>.Counter model equal True identity equal True
  accepted {'crank': 1080.0, 'tens': 0, 'units': 3} units dial 108.0
range 324 -> 360 __main__ counter.<locals>.Counter model equal True identity equal False
  refused ValueError that snapshot was taken over Counter(crank,tens,units), the machine f542620c34bd4f2764c12359f2ce5befdd5ea70455ae4a3a2f7ac623d1f48acd, and this simulation runs Counter(crank,tens,units), the machine 39b454776557a5259ba05c112e12522f58a6c615b248922e3cf9bcde423aeb85. A snapshot restores into the machine it was taken from: its drivers, its states and its relations are what its bank means.
  unchanged True
law advance -> skipping __main__ counter.<locals>.Counter model equal True identity equal False
  refused ValueError that snapshot was taken over Counter(crank,tens,units), the machine f542620c34bd4f2764c12359f2ce5befdd5ea70455ae4a3a2f7ac623d1f48acd, and this simulation runs Counter(crank,tens,units), the machine ee06820e7e5ec8caadfafaa0f515e3f310360deac34712ef63aa608387a5bc16. A snapshot restores into the machine it was taken from: its drivers, its states and its relations are what its bank means.
  unchanged True
```

### 4.4 The declared ranges, after the change (for the filed finding)

Stage P's `<scratch>/repro_bench.py` (design.md, "What the identity covers,
measured"), run again from the bench root after the change: the units
state's range `(0, 9)` widened to `(0, 19)` and the crank driver's
`range=(0, 7200)` each keep identity `07f7121997107d68` and the restore is
ACCEPTED; the commit law `advance -> by_two` changes it to
`905b2345a1b08c0a` and the restore is now REFUSED. `python -c` building
`Sim(Counter(), state={'units': 15})` over `tests/clocked_project/counter.py`
prints `{'crank': 0, 'tens': 0, 'units': 15}`: accepted.

## 5. Records

- 5.1 `docs/architecture.md`, the clocked bank paragraph: after "so it
  names the machine and not the bank," the clause "a clocked snapshot
  carries it, and `restore` refuses a snapshot whose identity differs
  before touching anything,".
- 5.2 `docs/project/changelog.rst`: design.md Decision 4's bullet,
  appended to the one `Unreleased` section after
  `snapshot-the-follow-prefix`'s bullet.
- 5.3 `grep -rn -i 'ClockedSnapshot\|restore\|snapshot' docs` (`*.rst`,
  `*.md`, excluding `adrs/` and `releases/`), filtered for `clocked` or
  `identity`: `docs/reference/api.rst:822` ("``initial`` is a
  ``ClockedSnapshot`` of the initial bank") and `:831` (the autoclass,
  which renders the new docstring) stay true; `docs/concepts/clocked.rst`
  lines 29, 193 and 215 say a state is set through `restore`, a restored
  pose is judged by the enumeration and the clock is a banked value in
  snapshots, none of which says what `restore` compares, and line 253
  ("an ``identity`` digest so a bank saved against one machine is refused
  against another") now holds of the framework's own `restore` as well as
  the viewer's; `docs/concepts/joints.rst:645-648`
  ("changing them changes the program's identity, so a snapshot taken
  under the old limits does not restore under the new ones") now reads
  true under a clocked root too, as 4.3 shows for a joint range; the other
  hits are running-root passages (`docs/concepts/running.rst`,
  `docs/project/upgrading.rst`, `docs/architecture.md` 1627, 1739) and are
  untouched. No page needed another edit.

## 6. Warts

- 6.1 Item 4 of "# Three findings from filming the clocked Curta (1
  October 2026, found by Videomaker's curta-video campaign)" moved
  verbatim to `workflow/archive/fix-warts-3-2026-10-06/resolved.md` under
  `` ## `clocked-snapshot-identity` ``, after `snapshot-the-follow-prefix`,
  with the "From ..." line and a "What shipped" paragraph; deleted from
  `workflow/warts.md`, the section's items 5, 6, 8, 9 and 10 kept. One
  edit beyond tasks.md: the section's opening sentence, which accounts for
  each finding by number, now says "finding 4 is fixed by
  `clocked-snapshot-identity` (`archive/fix-warts-3-2026-10-06/resolved.md`)",
  so a reader of a list beginning at 5 is told where 4 went.
- 6.2 New section "## Findings from the framework cycle
  `clocked-snapshot-identity` (2026-10-07)" after the
  `keep-the-corpus-cursor-honest` findings, one bullet: **A declared
  driver or state range is neither enforced on a clocked bank nor part of
  the clocked identity**, with 4.4's measurements, the export spec's and
  ADR-128's definition, and **Untriaged.** (the review answered design.md
  Open Question 1 as "out of this change, filed").

## 7. Sync and archive

- 7.1 By hand. In `openspec/specs/simulation/spec.md`: "A clocked
  simulation solves a request path event by event" takes the delta's
  `restore` clause; "A clocked simulation publishes its machine's
  identity" takes the delta's last paragraph in place of "The clocked
  snapshot's shape, `restore`'s comparison and every published document
  SHALL be unchanged by this member." and the three added scenarios after
  "A simulation that is not clocked refuses the identity by name". Before
  the edit, `python <scratch>/diff_delta.py <bench>` showed for the first
  requirement only the one-line clause (`-...over a different model before
  touching` / `+...over a different machine — one whose` and two added
  lines), and for the second only the replaced paragraph and the three
  added scenarios. After it, the same script prints both requirement
  headers and no diff lines. `git diff --stat -- openspec/specs`:
  `openspec/specs/simulation/spec.md | 38 +++++++++++++++++++++++++++++++++++---`
  (35 insertions, 3 deletions). `openspec validate
  clocked-snapshot-identity`: "Change 'clocked-snapshot-identity' is
  valid". `openspec validate simulation`: "Specification 'simulation' is
  valid".
- 7.2 `openspec archive clocked-snapshot-identity --yes --skip-specs` (the
  spec was synced by hand in 7.1, so the CLI's own sync was skipped):
  "Change 'clocked-snapshot-identity' archived as
  '2026-10-07-clocked-snapshot-identity'". Its warnings: the Why section's
  length, and 26 of 29 tasks complete (7.2 to 7.4, done after it and
  ticked in the archived copy). `openspec validate --specs`: `Totals: 45
  passed, 0 failed (45 items)`.
- 7.3 On `machinome/simulation/clocked.py`, `tests/test_clocked_identity.py`
  and `tests/test_clocked_sim.py`, on the working tree and on the three
  files as they are at HEAD (extracted with `git show HEAD:<file>` into
  `<scratch>/head/`):
  - `flake8 --max-line-length=89` (pyenv shim, flake8 7.3.0): 2 findings
    after, 2 at HEAD, both in `clocked.py` and in lines this change did
    not touch: `677:58: F541 f-string is missing placeholders` and
    `F811 redefinition of unused 'visit'` (at 1844 referring to 1840
    after, two lines lower than at HEAD because the snapshot class grew
    by two lines). With line numbers stripped the two lists differ only in
    that referenced line number. The test files are clean at HEAD and
    after. No new finding.
  - `black --check` (26.5.1): all three files "would reformat" at HEAD and
    after; the repository is not black-formatted. Lines `black -t py311
    --diff` changes: `clocked.py` 2354 at HEAD, 2359 after;
    `test_clocked_identity.py` 72 and 158 (the new code in the file's
    single-quote style); `test_clocked_sim.py` 835 and 839.
- 7.4 `<focused>`: `149 passed, 195 subtests passed in 6.09s` (wall
  7.02 s). The full suite, on the final tree, alone (`ps` showed no run
  of ours), `pytest -q -p no:cacheprovider` at the bench root: exit 0,
  wall 639.73 s, `4672 passed, 4 skipped, 55 warnings, 6662 subtests
  passed in 637.35s (0:10:37)`. No failure, no `Too many open files`.

Nothing is committed. `git -C <bench> status --short` lists the changed
`docs/architecture.md`, `docs/project/changelog.rst`,
`machinome/simulation/clocked.py`, `openspec/specs/simulation/spec.md`,
`tests/test_clocked_identity.py`, `tests/test_clocked_sim.py`,
`workflow/warts.md`, `workflow/archive/fix-warts-3-2026-10-06/resolved.md`
and `workflow/ongoing/fix-warts-3.md`, the change's directory moved to
`openspec/changes/archive/2026-10-07-clocked-snapshot-identity/`.
