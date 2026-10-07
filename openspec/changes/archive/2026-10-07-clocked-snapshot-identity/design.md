## Context

### What a clocked snapshot holds today

`Clocked.__init__` (`machinome/simulation/clocked.py:1712-1777`) compiles
the machine, builds the bank and then computes two names for what it
compiled:

- `self.identity` (`:1756-1757`): the SHA-256 of `described()`
  (`:1899-1927`). The listing names the root class by
  `module.qualname`, each input and each state with its `dtype` and
  `scale`, the clock where the root declares `Time.elapsed()`, each
  committing relation's source and target ids, primitive, level and laws,
  and each compiled bound's coordinate, side and level. It is taken before
  `state=` is applied and never recomputed, so it names the machine and
  not the bank. Every document producer publishes it as `clocked.identity`
  (`published()`, `:1952-1953`), and `Sim.identity` returns it.
- `self.model` (`:1758-1759`): the root class's bare `__name__` followed by
  the sorted bank ids, for example `Counter(crank,tens,units)`.

`ClockedSnapshot` (`:1691-1702`) has `__slots__ = ('model', 'values')`.
`self.initial` (`:1775`) and `snapshot()` (`:2069-2070`) build one from
`self.model` and the bank. `restore()` (`:2072-2083`) refuses a value that
is not a `ClockedSnapshot`, then refuses one whose `model` differs, then
poses the snapshot's values through `_posed`, which leaves the previous
bank and pose standing if the tree refuses the new pose.

A machine whose joint range, bound or commit law changed keeps the same
class name and the same bank ids, so it has the same `model`, and
`restore` accepts a snapshot from the old machine. So does a same-named
class from another module. The identity of each of these machines is
different, and nothing compares it.

### The running counterpart

`RunSnapshot` (`machinome/simulation/run.py:255-273`) is a dataclass whose
first field, `program`, is the compiled program's identity. `Run.restore`
(`:1575-1592`) refuses a snapshot whose `program` differs:

```
that snapshot was taken over the program <a>, and this simulation runs
<b>. A snapshot restores into the machine it was taken from: its
coordinates, its inputs and its relations are what its bank means.
```

The baseline spec states it for a running root
(`openspec/specs/simulation/spec.md`, "Snapshot, restore and reset act on
the run's bank"): "`sim.restore(snapshot)` SHALL compare the program
identity". The viewer's clocked machine
(`machinome-viewer/machinome_viewer/widget/src/clocked/machine.ts:94-97`,
`:409-424`) carries `{identity, bank}` and refuses with `that snapshot was
taken over the machine <a> and this one is <b>`.

### What the identity covers, measured

The scratch script `<scratch>/repro_bench.py` restores a snapshot of the
register counter into same-named variants built by one factory:

```
units State range (0, 9) -> (0, 19):
  identity 07f7121997107d68 -> 07f7121997107d68  (equal: True)
  ACCEPTED bank now {'crank': 1080.0, 'tens': 0, 'units': 3}
crank Driver range none -> (0, 7200):
  identity 07f7121997107d68 -> 07f7121997107d68  (equal: True)
  ACCEPTED bank now {'crank': 1080.0, 'tens': 0, 'units': 3}
commit law advance -> by_two:
  identity 07f7121997107d68 -> 905b2345a1b08c0a  (equal: False)
  ACCEPTED bank now {'crank': 1080.0, 'tens': 0, 'units': 3}
```

A declared `Driver` or `State` `range` is not in the identity. The ranges
the identity covers are JOINT ranges, compiled by `compile_bounds`
(`:1379-1411`) from `_compiled_spans`. A clocked request is clipped by
exactly those. `<scratch>/probe_tests.py` shows that a joint range on the
units dial, `(0, 324)` against `(0, 360)`, does change the identity, as
the commit law does. The red tests use these two changes.

### Who reads a clocked snapshot

- **The framework.** `Sim.snapshot`, `Sim.restore`, `Sim.initial` and
  `Sim.reset` (`machinome/simulation/sim.py:387-410`) delegate to the
  executor. Nothing else in `machinome/` builds or reads a
  `ClockedSnapshot`.
- **The clocked corpus.** `tools/generate_clocked_corpus.py:446-449` and
  `tests/test_clocked_corpus.py:138-141` keep snapshots in a dictionary
  keyed by the script's label and restore them into the same `Sim`. The
  corpus records banks only. Restoring into the same simulation always
  matches, so the corpus is byte-identical.
- **The viewer** builds its own snapshot from the document's
  `clocked.identity` and never receives the framework's object.
- **Videomaker** (`python/machinome_movie/evaluate.py:383`) reads
  `sim.snapshot().values`. Its scratch spike reads the same. Neither
  constructs a `ClockedSnapshot` or reads `model`.
- **Projects.** No `*.py` under `projects/` names `ClockedSnapshot`. The
  Curta's `simulation/test_event_driven.py` restores snapshots into the
  simulation they were taken from.
- **Tests.** `tests/test_clocked_sim.py:369-380` builds a
  `ClockedSnapshot(model, values)` by hand to restore a bank the tree
  refuses.

## Goals / Non-Goals

**Goals:**

- A clocked snapshot carries the identity of the machine it was taken
  over.
- `restore` refuses a snapshot taken over any other machine, as the
  identity defines one, before touching anything, and names both.
- A snapshot still restores into the machine it was taken from, in a new
  simulation as in the same one.

**Non-Goals:**

- Changing what the identity covers (Open Questions 1 and 2).
- Changing any document, corpus, the viewer or Videomaker.
- Snapshot equality, a new `repr`, serialization of a snapshot.

## Decisions

### 1. The snapshot carries `identity`; the constructor takes it third

```python
class ClockedSnapshot:
    """A clocked simulation's whole state as a value object: the model
    it was taken over, the bank, and the identity of the machine, which
    `restore` compares."""

    __slots__ = ('model', 'values', 'identity')

    def __init__(self, model, values, identity):
        self.model = model
        self.values = dict(values)
        self.identity = identity
```

`Clocked.__init__` builds `self.initial = ClockedSnapshot(self.model,
self.bank, self.identity)`. The identity is computed at `:1756`, before
`:1775`. `Clocked.snapshot()` returns `ClockedSnapshot(self.model,
self.bank, self.identity)`. `__repr__` is unchanged.

**Alternatives.**

- *Make `identity` optional, defaulting to `None`.* A snapshot built
  without it would then be refused by `restore` anyway, so the default
  would only move the failure from the constructor to the restore, where
  it is harder to read. The one hand-built snapshot in the suite is
  updated instead.
- *Put `identity` first, as `RunSnapshot` puts `program`.* That reorders
  the two existing arguments for no gain, and a caller passing
  `(model, values)` positionally would then pass a bank as an identity.
  Adding the argument last fails loudly on the old two-argument call.
- *Replace `model` by `identity`.* `model` is what makes the refusal
  readable, since the identity is a digest. The brief allows it to stay.

### 2. `restore` compares the identity, and only the identity

```python
    def restore(self, snapshot):
        if not isinstance(snapshot, ClockedSnapshot):
            raise TypeError(...)            # unchanged
        if snapshot.identity != self.identity:
            raise ValueError(
                f'that snapshot was taken over {snapshot.model}, the '
                f'machine {snapshot.identity}, and this simulation runs '
                f'{self.model}, the machine {self.identity}. A snapshot '
                f'restores into the machine it was taken from: its '
                f'drivers, its states and its relations are what its '
                f'bank means.')
        self._posed(dict(snapshot.values))
```

The check comes before `_posed`, so a refused snapshot changes nothing.
The `model` comparison is removed. Two snapshots with different `model`
strings always have different identities, because the identity's listing
contains the root's `module.qualname`, whose last part is the class name
in `model`, and every bank id `model` lists: each input and state, and
the clock as `clock time`. The existing test
`test_restore_refuses_a_snapshot_from_another_model` (`Counter` against
`Scaled`) stays green under the identity check.

The message keeps the running refusal's shape and closing sentence and
names both models and both identities. Where the models match, the reader
sees one name with two identities, which says the machine changed under
the name.

Revised at the orchestrator's review of the implementation (7 October
2026): the model string lists every bank id (41 on the Curta, so the
message as written above ran to about 1,400 characters), and when the
two models are equal it is printed once, followed by "and this
simulation runs the same model with another identity"; both identities
still follow. The tests assert the refusal and the identities, not the
sentence.

**Alternatives.**

- *Keep the `model` check first, for a separate message.* It adds a branch
  whose every case the identity check already refuses, and a reader would
  have two messages for one rule.
- *Say what differs* (a range, a law, a module). Only the digests are
  available at `restore`. Keeping the listing on the snapshot to compare
  it line by line is more than the finding asks for, and the running
  refusal does not do it either.

### 3. The tests

In `tests/test_clocked_identity.py`, at module level:

```python
def skipping(sources, targets):
    """The counter's commit law advancing the units by two."""
    return lambda crank, units, tens: ((units + 2) % 10,
                                       (tens + (units >= 8)) % 10)


def restated(stop=324.0, law=advance):
    """The register counter, built here so that every variant has this
    module, one qualified name and one bank: only the units dial's stop
    or the commit law differs."""

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
```

`advance`, `strokes` and `DIGIT` come from `tests/clocked_project/counter.py`,
and `Revolute` from `machinome.motion.joints`. A new class
`SnapshotIdentityTest(BaseNodeTest)` holds:

1. `test_a_snapshot_carries_the_machines_identity` (RED: `AttributeError`,
   `'ClockedSnapshot' object has no attribute 'identity'`). Over
   `Counter()` after one request: `sim.snapshot().identity` and
   `sim.initial.identity` both equal `sim.identity`.
2. `test_a_snapshot_restores_into_the_same_machine` (guard, green before
   and after). A snapshot taken over `restated()()` after
   `move('crank', by=1080.0)` restores into a new `Sim(restated()())`. The
   bank equals the snapshot's values, `units` is `3`, and the units dial
   stands at `108.0`.
3. `test_a_machine_whose_range_changed_refuses_the_snapshot` (RED: the
   restore is accepted, `ValueError not raised`). Same snapshot, restored
   into `Sim(restated(stop=360.0)())`. The test first asserts what makes
   it a test of the identity: the two `model` strings are equal and the two
   `sim.identity` values differ. Then `restore` raises `ValueError` whose
   message contains both identities and `Counter(crank,tens,units)`, and
   the target's `sim.state` and `units_dial.turn.value` are what they were
   before the call.
4. `test_a_machine_whose_commit_law_changed_refuses_the_snapshot` (RED,
   same failure). As 3, into `Sim(restated(law=skipping)())`.

The two preconditions in 3 and 4 hold on the unmodified bench
(`<scratch>/probe_tests.py`), so their red is the restore being accepted
and nothing else.

`tests/test_clocked_sim.py::test_a_restore_whose_pose_is_refused_changes_nothing`
builds its snapshot as `ClockedSnapshot(saved.model, {'crank': 0.0,
'value': 3}, saved.identity)` from `saved = sim.snapshot()`, so it still
reaches the tree's refusal of the pose. Under the new constructor the
two-argument call raises `TypeError`, so this edit is made with the
change, in the same task.

No test pins the same-named class from another module. That refusal
follows from the identity's definition, which Open Question 2 leaves
open, and the Curta script shows it.

### 4. Records

- `ClockedSnapshot`'s docstring, as in Decision 1.
- `docs/architecture.md`, the clocked bank paragraph (`:1815-1820`): after
  "so it names the machine and not the bank," add "a clocked snapshot
  carries it, and `restore` refuses a snapshot whose identity differs
  before touching anything,". The rest of the sentence is unchanged.
- `docs/project/changelog.rst`, appended to the one `Unreleased` section:

  ```rst
  * **A clocked snapshot restores only into the machine it was taken
    from.** ``sim.snapshot()`` under a clocked root carries the machine's
    identity, the string ``sim.identity`` returns and an export publishes
    as ``clocked.identity``, and ``sim.restore()`` refuses a snapshot whose
    identity differs, naming both, before touching anything. It used to
    compare the class name and the bank's ids only, so a snapshot restored
    into a same-named machine whose joint range or commit law had changed,
    or into a same-named class from another module. ``ClockedSnapshot``
    takes the identity as its third argument (clocked-snapshot-identity).
  ```

- `docs/reference/api.rst` needs no edit: its autoclass renders the new
  docstring, and "``initial`` is a ``ClockedSnapshot`` of the initial
  bank" stays true. `docs/concepts/clocked.rst` does not describe what
  `restore` compares. `docs/concepts/joints.rst:645-648` becomes true
  under a clocked root.

## Proof plan

- **Red first.** Tests 1, 3 and 4 fail on the unmodified tree for the
  reasons named. Test 2 passes before and after.
- **Focused suite.** `tests/test_clocked_sim.py tests/test_clocked_identity.py
  tests/test_clocked_time.py tests/test_clocked_corpus.py`: at Stage P,
  `145 passed, 195 subtests passed in 6.11s`. After the change, the same
  plus four tests.
- **Corpus.** `git -C <bench> status --short tests/` lists no corpus file.
- **Originating project.** On the Curta, before and after:
  - `<scratch>/curta_restore.py`: before, all three restores are
    accepted. After, the fresh instance is accepted with result digits
    `[4, 1, 0, 0]`, and the changed range and the other module are
    refused with the new message.
  - `pytest -p no:cacheprovider -q --durations=5
    <project>/simulation/test_event_driven.py::EventDrivenOperationsTest`:
    at Stage P `11 passed, 57 subtests passed in 36.50s`. The same counts
    after. Two of these tests snapshot and restore the Curta.
  - `EventDrivenGeometryTest` in the same module is not run. It builds the
    Curta's meshes in a scratch build directory, which is the cost of a
    full build, and it neither snapshots nor restores.
- **Full suite** once, alone, on the final tree.

## Risks / Trade-offs

- **A hand-built `ClockedSnapshot` with two arguments now raises
  `TypeError`.** The class is listed in the API reference, so this is a
  change to a documented constructor. No project or sibling repository
  builds one, and the changelog says it.
- **The identity includes the import module.** A snapshot taken over a
  model imported as `models.counter` is refused by the same file imported
  under another module name. In one process these are two different
  classes, so refusing is consistent with the identity as defined.
  Whether the definition should anchor on the manifest's module is Open
  Question 2.

## Open Questions

1. **Should a declared `Driver` or `State` `range` be part of the clocked
   identity?** Today it is not. The clocked executor never reads it: a
   request is clipped only by compiled joint bounds, and `state=` accepts
   a value outside a state's declared range. A snapshot from a machine
   whose driver range changed is therefore still accepted after this
   change. Adding the ranges would change every published
   `clocked.identity`, the export spec's definition and ADR-128.
   **Recommendation:** out of this change. Stage A files it in
   `warts.md` as an untriaged finding, with the scratch run's output.
   Who answers: the pilot, if a project needs the declared ranges to
   bind. Answered at review (7 October 2026): out of this change, filed.
2. **Should the identity's root be the manifest's module rather than the
   import module?** This is the open warts entry "A machine's identity
   depends on the module its model is imported from". This change uses
   the identity as defined, so its refusals follow whatever that entry
   decides. **Recommendation:** leave it to that entry. No test here pins
   the module case. Who answers: the pilot, through that entry's triage.
   Answered at review (7 October 2026): left to that entry.
