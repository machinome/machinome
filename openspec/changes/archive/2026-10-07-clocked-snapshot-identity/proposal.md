## Why

A clocked simulation restores a snapshot into a machine that is not the one
the snapshot was taken over. `workflow/warts.md`, "Three findings from
filming the clocked Curta (1 October 2026, found by Videomaker's
curta-video campaign)", item 4:

> **The framework's clocked snapshot carries no identity, the viewer's
> does.** `ClockedSnapshot` holds `model` (the bare class name with the
> sorted bank ids) and `values`, and `Clocked.restore` compares `model`
> only, so the framework restores a snapshot from a machine whose law or
> range changed under the same ids, or from a same-named class in another
> module; the export spec says the identity exists precisely to refuse
> that, and a running `RunSnapshot` does carry and check
> `program.identity`. Found by `sim-identity` (its `evidence.md`, finding
> 1).

`ClockedSnapshot` (`machinome/simulation/clocked.py:1691-1702`) holds
`model`, which is `f'{type(node).__name__}({",".join(sorted(self.bank))})'`
(`:1758-1759`), and `values`. `Clocked.restore` (`:2072-2083`) refuses a
snapshot only when the two `model` strings differ. The executor already
computes `self.identity` at construction (`:1756-1757`): a SHA-256 over
`described()` (`:1899-1927`), which lists the root class by module and
qualified name, every input and state with its `dtype` and `scale`, the
clock, every committing relation's ends, primitive, level and laws, and
every compiled bound's coordinate, side and level. The export spec states
what that identity is for (`openspec/specs/export/spec.md`, the `clocked`
object): "so a bank taken against one machine is refused against another,
and so a changed range changes the identity". ADR-128 says the same. The
framework publishes the identity, as `clocked.identity` and as
`sim.identity`, but its own `restore` never reads it. A running snapshot
does: `RunSnapshot.program` (`machinome/simulation/run.py:255-273`) is
compared in `Run.restore` (`:1575-1586`). The viewer's clocked machine
also carries `identity` in its snapshot and refuses on a mismatch
(`machinome-viewer`, `widget/src/clocked/machine.ts:94-97`, `:409-424`).

The `sim.identity` requirement written by `sim-identity` left this open on
purpose: "The clocked snapshot's shape, `restore`'s comparison and every
published document SHALL be unchanged by this member."

**Reproduced on the bench `fix-warts-3` at `5955e88`**, with the
interpreter check printing
`/home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py`.

In the framework's own fixtures, a scratch script builds the register
counter of `tests/clocked_project/counter.py` from one factory. Every
variant therefore has the same module, the same qualified name and the
same bank. It takes a snapshot after three strokes and restores it into a
second simulation:

```
same __main__ counter.<locals>.Counter model equal True identity equal True
  accepted {'crank': 1080.0, 'tens': 0, 'units': 3} units dial 108.0
range 324 -> 360 __main__ counter.<locals>.Counter model equal True identity equal False
  accepted {'crank': 1080.0, 'tens': 0, 'units': 3} units dial 108.0
law advance -> skipping __main__ counter.<locals>.Counter model equal True identity equal False
  accepted {'crank': 1080.0, 'tens': 0, 'units': 3} units dial 108.0
```

The units dial's joint range and the commit law each change the identity,
and both restores are accepted.

In the originating project, `projects/Calculators/Curta-Type-I-3x` (branch
`main`, head `1f3dc22`), a scratch script imports the clocked model
`simulation.clocked.ClockedCurta` with the project on `sys.path` and a
scratch `SOLID_BUILD_DIR`, and writes nothing in the project. It sets
`digit_1` to 7, triggers `Turn crank` twice and takes a snapshot. It then
restores the snapshot into three simulations. The second is a subclass of
the Curta whose `operation.crank_lift` stops at 8 mm instead of 9, declared
under the original's module and name. The third is the unchanged Curta
under the same name in another module:

```
ClockedCurta constructed in 1.83 s
  identity c7286b3be65803cc
  snapshot after 7 x 2: result digits [4, 1, 0, 0]
same machine, fresh instance:
  class    simulation.event_driven.EventDrivenCurta
  model    equal: True
  identity c7286b3be65803cc  (built 1.57 s)
  ACCEPTED result digits [4, 1, 0, 0]
one range changed (crank_lift high 9 -> 8 mm):
  class    simulation.event_driven.EventDrivenCurta
  model    equal: True
  identity 73974bcd5dfebaf1  (built 1.59 s)
  ACCEPTED result digits [4, 1, 0, 0]
unchanged, same-named class in another module:
  class    __main__.EventDrivenCurta
  model    equal: True
  identity cc13707b2bc0f349  (built 1.50 s)
  ACCEPTED result digits [4, 1, 0, 0]
```

All three restores are accepted. The last two are restores into another
machine.

## What Changes

- **A clocked snapshot carries the machine's identity.** `ClockedSnapshot`
  gains a third slot, `identity`. `Clocked.snapshot()` and
  `Clocked.initial` fill it with the executor's `identity`, which is the
  same string as `sim.identity` and the export's `clocked.identity`. The
  constructor becomes `ClockedSnapshot(model, values, identity)`. `model`
  and `values` keep their names and meanings, so a reader of
  `sim.snapshot().values` (Videomaker's take recorder) is unaffected.
- **`restore` compares identities.** `Clocked.restore` refuses a snapshot
  whose `identity` differs from the simulation's, with a `ValueError`,
  before touching the bank, the tree or the record. The message has the
  running refusal's shape and names both models and both identities:
  `that snapshot was taken over Counter(crank,tens,units), the machine
  <identity>, and this simulation runs Counter(crank,tens,units), the
  machine <identity>. A snapshot restores into the machine it was taken
  from: its drivers, its states and its relations are what its bank
  means.` The comparison of `model` strings is removed, because a
  different `model` always means a different identity: the identity lists
  the root class and every bank id that `model` names.
- **Tests.** Three red tests and one guard, in `tests/test_clocked_identity.py`.
  A snapshot and `sim.initial` carry `sim.identity`. A snapshot is refused
  by a same-named machine whose one joint range changed, and by one whose
  commit law changed, leaving its bank and pose as they stood. A snapshot
  still restores into a fresh simulation over the same machine. The one
  existing test that builds a `ClockedSnapshot` by hand
  (`tests/test_clocked_sim.py:369-380`) passes the identity.
- **Records.** The `ClockedSnapshot` docstring names the identity.
  `docs/architecture.md` says, beside `sim.identity`, that a clocked
  snapshot carries it and `restore` refuses on a mismatch. A changelog
  bullet goes under `Unreleased`. The warts item moves to the campaign's
  `resolved.md`.

**Deliberately out**, with the reason:

- **The identity's definition is unchanged.** `described()`, the export's
  `clocked.identity` and every published document keep their bytes.
  `tests/clocked-corpus.json` is byte-identical: its scripts name
  snapshots by label and record only banks
  (`tools/generate_clocked_corpus.py:446-449`,
  `tests/test_clocked_corpus.py:138-141`).
- **A declared `Driver` or `State` `range` is not in the identity, and
  stays out.** The scratch run shows that changing a state's or a
  driver's declared range leaves the identity as it was, and the restore
  accepted. The identity lists compiled joint bounds, which are what a
  clocked request is clipped by. The clocked executor reads no declared
  driver or state range, and `Sim(Counter(), state={'units': 15})` is
  accepted on the bench. Widening the identity would change every
  published `clocked.identity` and the ratified definition in the export
  spec and ADR-128. design.md, Open Question 1, recommends recording it as
  a finding.
- **The import module stays in the identity.** The warts entry "A
  machine's identity depends on the module its model is imported from"
  asks whether to anchor the identity on the manifest's module name. That
  choice is open and is not made here. With this change, a snapshot taken
  over one module's class is refused by a same-named class from another
  module, which is what the finding asks for. design.md, Open Question 2.
- **The viewer and Videomaker are not touched.** The viewer builds its
  own clocked snapshot from the document's identity and never receives the
  framework's. Videomaker reads `sim.snapshot().values`, which does not
  change. Nothing is written in either repository.
- **No equality, no `repr` change.** `ClockedSnapshot` keeps its `__repr__`
  and gains no `__eq__`. The running snapshot's equality is a dataclass
  property no clocked requirement asks for.
- **No ADR.** ADR-128 already states that the identity refuses a bank
  taken against another machine. This change makes the framework's own
  `restore` do it.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `simulation`: two requirements are modified.
  - "A clocked simulation publishes its machine's identity": its last
    paragraph, which kept the snapshot's shape and `restore`'s comparison
    unchanged, is replaced. A clocked snapshot SHALL carry the identity,
    and `restore` SHALL refuse a snapshot whose identity differs, naming
    both, before touching anything. Every published document stays
    unchanged. Three scenarios are added: a snapshot carries the identity;
    a snapshot is refused by a same-named machine whose range or commit
    law changed; a snapshot restores into the same machine. Every existing
    scenario is carried unchanged.
  - "A clocked simulation solves a request path event by event": one
    clause changes. `restore` refuses a snapshot taken over a different
    MACHINE, as the identity requirement defines it, instead of a
    different "model". Every scenario is carried unchanged.

## Impact

- **Code:** `machinome/simulation/clocked.py`: `ClockedSnapshot`
  (`:1691-1702`) gains `identity` in `__slots__`, `__init__` and its
  docstring. `Clocked.__init__` (`:1775`) and `Clocked.snapshot`
  (`:2069-2070`) pass `self.identity`. `Clocked.restore` (`:2072-2083`)
  compares `snapshot.identity` instead of `snapshot.model`. No other
  function changes.
- **Tests:** `tests/test_clocked_identity.py` gains one class with four
  tests and a module-level fixture factory. `tests/test_clocked_sim.py`
  `test_a_restore_whose_pose_is_refused_changes_nothing` passes the
  identity to the constructor.
- **Public surface:** `ClockedSnapshot` is not exported by
  `machinome.simulation` or `machinome`. It is reached as
  `machinome.simulation.clocked.ClockedSnapshot` and listed in
  `docs/reference/api.rst` (`:831`), and its constructor takes a third
  argument. No project constructs one: a search of every `*.py` under
  `projects/` finds no `ClockedSnapshot`. Videomaker's
  `python/machinome_movie/evaluate.py` reads only `.values`.
- **Documents, corpora, identities:** unchanged.
- **Manual:** `docs/architecture.md`, the clocked bank paragraph
  (`:1813-1820`), gains one clause. `docs/concepts/clocked.rst` says
  nothing about what `restore` compares. `docs/concepts/joints.rst:645-648`
  says that changing limits changes the identity, "so a snapshot taken
  under the old limits does not restore under the new ones", and this
  change makes that true under a clocked root too. The changelog gets one
  bullet.
- **Projects:** the Curta's clocked tests restore snapshots into the
  machine they were taken over (`simulation/test_event_driven.py`,
  `test_split_requests_and_session_state` and
  `test_borrow_undo_shift_and_restore`), and must stay green. At Stage P
  `EventDrivenOperationsTest` passes 11 tests and 57 subtests in 36.50 s
  against the bench.

## Authorization

The pilot's mandate of 6 October 2026 for the fix-warts-3 campaign
(`workflow/ongoing/fix-warts-3.md`, "Mandate"): "work on the items you can
autonomously, orchestrating opus subagents and using empirical evidence
from projects to validate, other than your adversarial review. if
something needs my input, record and defer, you'll go unsupervised." This
change is the campaign table's cycle 9, `clocked-snapshot-identity`,
validated in Curta-Type-I-3x. design.md's two Open Questions each carry a
recommendation, and neither blocks the fix.
