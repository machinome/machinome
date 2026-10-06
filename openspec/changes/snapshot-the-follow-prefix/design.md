## Context

### The prefix and its cache

A running Bound that reads other coordinates is searched inside the
stretch: `_searched_constraint` (`machinome/simulation/run.py:928-1060`)
samples its level at `_SUBDIVISIONS` fractions, at both sides of every
Follow cut, and at the bisection points. When the tick's own propagation
does not trace every read, each sample calls `_constraint_level`
(`:1062-1114`). That method walks the Bound's compiled sub-program, its
`constraint.edges`, at the fraction `t`, on a fresh propagation from
`self._deltas(...)` (`Program.deltas_of`,
`machinome/simulation/program.py:3006-3013`), and then evaluates the
Bound's graph from the walked displacements and landings.

The Curta's retained radial ball has two such Bounds, a low one reading the
tens bell and a high one reading the carriage lift. Both have the same
sub-program: deterministic laws ending in the ball's `Follow` edge.
`cache-follow-prefix-probes`
(`openspec/changes/archive/2026-09-23-cache-follow-prefix-probes/`) made
the second Bound reuse the first one's walk at the same fraction. `_reached`
allocates `prefix_cache = {}` for one stretch (`:851`) and passes it down.
`_constraint_level` stores a successful eligible walk under
`(tuple(constraint.edges), struct.pack('!d', t))` (`:1075-1096`):

```python
if saved is None:
    deltas = self._deltas({input_id: delta * t
                           for input_id, delta in admissions.items()})
    landings = {}
    for edge in constraint.edges:
        for key, increment in edge.increments(values, deltas,
                                               landings=landings):
            deltas[key] = increment
    if eligible:
        saved = (MappingProxyType(dict(deltas)),
                 MappingProxyType(dict(landings)))
        prefix_cache[cache_key] = saved
else:
    deltas, landings = saved
```

After this branch (`:1099-1114`) the method reads `deltas[read_key]`,
`deltas[own_key]` and `landings[...]` only. A miss reads the walked
`Propagation` and a dict. A hit reads two `mappingproxy` objects.

### What a walk produces

`Propagation` (`machinome/simulation/trajectory.py:61-76`) is a `dict` of
displacements with six attributes, set in `__init__`:

| Attribute | Type | Written by |
|---|---|---|
| `motions` | `dict` key → `Motion` | law paths (`trajectory.py:322`, `:543-645`), terminal moves (`run.py:781`) |
| `demanded` | `frozenset` | `__init__` only |
| `untraced` | `set` | Follow, Play and their downstream edges (`trajectory.py:472-495`) |
| `follow_cuts` | `dict` key → `tuple` of floats | `follow_increments` (`trajectory.py:463-465`) |
| `follow_closures` | `dict` key → `tuple` of tuples | `follow_increments` (`trajectory.py:466`) |
| `terminal_keys` | `set` | Follow, Play and law edges after a terminal move |

A walk of the Curta's prefix carries 301 displacement keys, 216 demanded
keys and, at the first stored fraction of a crank tick, two motions and one
untraced key. The `MappingProxyType(dict(deltas))` snapshot keeps the 301
displacements and drops all six attributes.

### Reproduction at `1591276`

`<scratch>/repro.py` (its source goes into evidence.md) builds
`Sim(TwoSurfaces(), dt=1.0)` from `tests/test_running_follow.py`, takes the
low Bound, wraps `Run._deltas` to capture the walk's propagation, and calls
`_constraint_level` twice with one cache at `t = 0.5`. The output is in
proposal.md: one walk, one cache entry, equal levels, a miss propagation
carrying `follow_cuts`, `follow_closures` and `untraced`, and a hit object
of type `mappingproxy` on which each of the six attributes raises
`AttributeError`.

### Cost, measured at `1591276`

All runs are one process at a time, pinned with `taskset -c 14`, with the
project on `PYTHONPATH` after the bench, `PYTHONDONTWRITEBYTECODE=1` and
`SOLID_BUILD_DIR` set to a scratchpad directory, so nothing is written in
the project.

- `<scratch>/curta_measure.py VARIANT`: forty 0.1-second crank ticks of
  `MechanisticCurta`. Twenty subtract one with the crank raised, borrowing
  through both registers, and twenty add it back, as
  `test_mechanistic.py`'s
  `test_subtraction_borrows_through_both_registers_and_addition_undoes_it`
  does. It hashes every committed bank's keys and float bits.

  | Variant | Wall (s) | CPU (s) | Walks / stores / hits | Snapshots (s) |
  |---|---|---|---|---|
  | `bench` | 178.676 | 178.651 | — | — |
  | `proxy` (exact copy, counted) | 186.824 | 186.796 | 2856 / 2856 / 2856 | 0.009885 |
  | `frozen` (candidate, explicit form) | 187.164 | 187.139 | 2856 / 2856 / 2856 | 0.017893 |
  | `nocache` | 239.428 | 239.399 | — | — |

  Bank SHA-256 for all four:
  `167ea1cd4849c606a22e9457081c329495cd747f149ab19dbefa2288b18b1fcf`.
  Every stored prefix is read back exactly once, by the paired Bound. The
  cache saves 60.8 s of 239.4 s. The `bench` and `proxy` runs execute the
  same arithmetic and differ by 8.1 s, which is the run-to-run spread on this
  host. The `proxy` and `frozen` runs share their instrumentation and differ
  by 0.34 s, of which the snapshots account for 8 ms.
- `<scratch>/snapshot_microbench.py`, on the first prefix propagation a
  Curta crank tick stores (301 keys), per snapshot pair: today's proxy
  1.25 µs, an explicit frozen copy 2.08 µs, the generic frozen copy of
  Decision 1 2.46 µs. Over 2,856 stores the generic form adds about 3.5 ms.
- `simulation/test_radial_positioning_ball.py` (four tests), bench: 4
  passed in 260.98 s (wall 262.41 s); candidate, explicit form, by
  monkeypatch (`<scratch>/pytest_candidate.py`): 4 passed in 262.65 s (wall 264.08 s).
  Per test, bench / candidate: 87.08 / 87.06, 64.05 / 63.66, 45.97 / 47.11,
  42.57 / 43.98 s.
- `simulation/test_mechanistic.py::MechanisticCurtaTest::test_subtraction_borrows_through_both_registers_and_addition_undoes_it`,
  bench: 1 passed in 212.17 s (call 191.39 s, wall 213.54 s).
- Framework: `tests/test_follow_prefix_cache.py`,
  `tests/test_running_follow.py`, `tests/test_running_corpus.py` and
  `tests/test_following_contact_repro.py` on the bench: 43 passed, 84
  subtests passed in 2.86 s.

## Goals / Non-Goals

**Goals:** the code after the prefix branch of `_constraint_level` reads
one kind of object whether the prefix was walked or reused: a read-only
`Propagation` carrying the walk's displacements and every path attribute.
The cache keeps its scope, key, eligibility and immutability, and every
value it produces is unchanged.

**Non-Goals:** no change to what is cached, when, or for how long; no
change to the tick's own propagation or to the `getattr(deltas, ...)`
reads in `_reached`, `_constraint_reached` and `_searched_constraint`; no
deep freeze of `Motion` objects; no new reader of a path attribute after
the branch. No change in any project.

## Decisions

### 1. Store a frozen propagation

Add to `machinome/simulation/trajectory.py`, after `Propagation`, with
`from types import MappingProxyType` among the module's imports:

```python
class FrozenPropagation(Propagation):
    """A finished propagation that several readers share: its
    displacements and the paths that determined them, none of them
    changeable."""

    def __init__(self, propagation):
        dict.__init__(self, propagation)
        state = self.__dict__
        for name, value in vars(propagation).items():
            state[name] = (MappingProxyType(dict(value))
                           if isinstance(value, dict)
                           else frozenset(value)
                           if isinstance(value, (set, frozenset))
                           else value)

    def _refuse(self, *args, **kwargs):
        raise TypeError(f'{type(self).__name__} is read-only')

    __setitem__ = __delitem__ = __ior__ = _refuse
    clear = pop = popitem = setdefault = update = _refuse
    __setattr__ = __delattr__ = _refuse
```

The attributes are copied from `vars(propagation)`, not listed by name, so
an attribute a later change adds to `Propagation` is carried and frozen
without another edit here. The test (Decision 3) compares the attribute
names of the two objects, so an attribute that is not carried is a red
test. `Motion` values inside `motions` are shared, not copied: a `Motion`
is immutable apart from the memo of its own evaluations, exactly as it is
inside the walked `Propagation`. The tuples in `follow_cuts` and
`follow_closures` are immutable already. `Propagation.motion(key, values)`
works unchanged on the frozen object.

**Alternatives.**

- *Assert the shape at the hit* (the wart's second remedy). Nothing after
  the branch reads an attribute, so there is nothing a run-time assertion
  could check. It would be a comment, and the second shape would stay. It
  is cheaper by about 1.2 µs per store, which nobody can measure.
- *Store the walked `Propagation` itself.* It is the identical type, with
  no copy at all, but one mutable object would be read by two Bounds. The
  cache's own design (archived, Decision 2) requires immutable snapshots;
  dropping that is a change to the cache's contract, not to its shape.
- *List the six attributes by name* (the form `<scratch>/candidate.py`
  measured on the Curta). It is 0.4 µs cheaper per store, and silently
  drops an attribute added to `Propagation` later, which is the defect
  this change removes.
- *A deep-frozen `Motion`.* Not needed: nothing mutates a stored motion,
  and its memo is shared in the walked `Propagation` today.

### 2. The walk that publishes the prefix continues with it

In `Run._constraint_level` (`machinome/simulation/run.py:1093-1096`),
with `from .trajectory import FrozenPropagation` among the module's
relative imports (`trajectory` imports `program`, not `run`, so there is
no cycle):

```python
if eligible:
    saved = (FrozenPropagation(deltas),
             MappingProxyType(dict(landings)))
    prefix_cache[cache_key] = saved
    # The walk that publishes the prefix reads it as every later Bound
    # will, so the lines after this branch see one shape.
    deltas, landings = saved
```

The `else: deltas, landings = saved` branch is unchanged. On an eligible
prefix, a miss and every hit now hand the rest of the method the same
pair, a `FrozenPropagation` and a read-only mapping of landings. The
values read are the same float objects the walk produced, so every level
is bit-identical. A walk that is not eligible (no cache, an edge that is
not a law before the Follow, a non-finite fraction) keeps its mutable
`Propagation` and its `dict` of landings. Both are a `Propagation` and a
mapping, with the same attributes and keys.

### 3. Tests

Add to `FollowPrefixCacheTest` in `tests/test_follow_prefix_cache.py`,
after `test_exact_fraction_bits_and_distinct_edges_miss`, importing
`Propagation` from `machinome.simulation.trajectory`:

```python
def test_a_reused_prefix_is_the_propagation_its_walk_produced(self):
    sim = Sim(TwoSurfaces(), dt=1.0)
    run, low, high, values, admissions = self._probe_inputs(sim)
    walked = []
    original = Run._deltas

    def captured(run, admissions):
        deltas = original(run, admissions)
        walked.append(deltas)
        return deltas

    cache = {}
    with patch.object(Run, '_deltas', captured):
        self._level(run, low, values, admissions, 0.5, cache)
    (reused, landings), = cache.values()
    produced, = walked
    self.assertIsInstance(reused, Propagation)
    self.assertEqual(dict(reused), dict(produced))
    self.assertTrue(produced.follow_cuts)
    self.assertEqual(sorted(vars(reused)), sorted(vars(produced)))
    for name, value in vars(produced).items():
        with self.subTest(attribute=name):
            self.assertEqual(getattr(reused, name), value)
    key = next(iter(produced.follow_cuts))
    with self.assertRaises(TypeError):
        reused[key] = 1.0
    with self.assertRaises(TypeError):
        reused.follow_cuts[key] = ()
    with self.assertRaises(TypeError):
        reused.untraced = set()
    with self.assertRaises(TypeError):
        landings[key] = 1.0
    expected = self._level(run, high, values, admissions, 0.5, None)
    with patch.object(Run, '_deltas', captured):
        actual = self._level(run, high, values, admissions, 0.5, cache)
    self.assertEqual(len(walked), 1)
    self.assertEqual(float(actual).hex(), float(expected).hex())
```

Red today at the first assertion: `mappingproxy({...}) is not an instance
of <class 'machinome.simulation.trajectory.Propagation'>`. Stage P ran this
test from the scratchpad (`<scratch>/test_red_probe.py`, the same body in
a `TestCase` borrowing `_probe_inputs` and `_level`): red on the bench with
that message (1 failed in 1.02 s). With the candidate patched in, in the
explicit form and in the generic form of Decision 1, it passed together
with `tests/test_follow_prefix_cache.py`, `tests/test_running_follow.py`,
`tests/test_following_contact_repro.py` and `tests/test_running_corpus.py`:
44 passed, 90 subtests passed, in 2.93 s and 2.97 s.

A mappingproxy compares equal to a `dict` with the same items, and a
`frozenset` to a `set`, so the attribute comparison holds for the frozen
forms. `walked` stays at one entry because the hit does not walk and the
uncached reference runs outside the patch.

### 4. Proof plan

1. Red: the test of Decision 3, on the unmodified tree.
2. Green: the same test, then `tests/test_follow_prefix_cache.py`,
   `tests/test_running_follow.py`, `tests/test_following_contact_repro.py`,
   `tests/test_running_corpus.py`, `tests/test_clocked_corpus.py` and
   `tests/test_time_drive_corpus.py`. The corpora are replayed, never
   written; `git status --short tests/` lists only
   `tests/test_follow_prefix_cache.py`.
3. The Curta, before and after, against the bench (project on
   `PYTHONPATH`, nothing written there):
   - `simulation/test_radial_positioning_ball.py`, counts and wall time;
   - `test_mechanistic.py::MechanisticCurtaTest::test_subtraction_borrows_through_both_registers_and_addition_undoes_it`,
     counts and wall time;
   - `<scratch>/curta_measure.py bench`: the bank SHA-256 is
     `167ea1cd…8b18b1fcf` before and after, and the wall time is within
     the host's spread of 178.7 s.
4. The full suite once, alone.

## Risks / Trade-offs

- **A reader mutates the stored prefix** → every mutator of `dict` and
  every attribute assignment raises `TypeError`; the test checks item,
  nested-mapping and attribute assignment. `dict.__setitem__(frozen, ...)`
  called explicitly would bypass it, as it would bypass any `dict`
  subclass; nothing in the framework does that.
- **An attribute added to `Propagation` later is a mutable `list` or
  another type** → it is carried as it is, not frozen. The test's
  `vars` comparison still passes, so this is the one case the guard does
  not see; it is a two-line addition to the `isinstance` chain when it
  happens.
- **Cost** → measured at about 2.5 µs per store against 1.25 µs today, on
  2,856 stores in forty Curta ticks of about 180 s.

## Open Questions

1. **`test_mechanistic.py` as a whole is not the before-and-after run.**
   Who answers: the orchestrator. Its subtraction test alone takes 191 s
   of call time on the bench. The four other crank tests of its
   `MechanisticCurtaTest` run about 205 more ticks, some 16 minutes at
   that test's 4.8 s per tick, and its `MechanisticCurtaIntegrityTest` needs every
   mesh of the Curta, built cold into a scratch `SOLID_BUILD_DIR` because
   the project's own `_build` may not be written. The module is therefore
   well over the brief's fifteen minutes. **Recommendation:** run the
   radial-ball module, which is the smallest module whose subject is the
   Follow law, including its stops and bisection, plus the one
   `test_mechanistic.py` test above and the forty-tick bank digest. The
   integrity tests do not reach the running code this change touches.
   Answered at review (6 October 2026): that set is the validation.
