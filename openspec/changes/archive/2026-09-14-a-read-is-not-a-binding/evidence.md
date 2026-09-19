# Evidence: a read is not a binding

Everything below was measured on this worktree
(`solid-node/WTs/fix-warts`, branch `fix-warts` at `a84030d`, the head
after cycles 1 to 3 of the wart plan). The probes are in `evidence/`; the
captured run of the first is `evidence/probe_publication.txt`.

    PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python \
        openspec/changes/a-read-is-not-a-binding/evidence/probe_publication.py
    PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python \
        openspec/changes/a-read-is-not-a-binding/evidence/probe_sim.py
    PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python \
        openspec/changes/a-read-is-not-a-binding/evidence/probe_candidates.py
    PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python \
        openspec/changes/a-read-is-not-a-binding/evidence/probe_lock.py <copy> [candidate-a]

## 1. The fixture, and the reproduction

`evidence/fixture.py` is the lock's shape with two joints and two
relations:

    class Plug(AssemblyNode):
        key = Key()                                  # leaf, joint `insert`
        p1 = Pin()                                   # leaf, joint `lift`
        key.insert.drives(p1.lift, ratio=0.5)        # CHILD-declared

    class LockBody(AssemblyNode):
        push = Driver(default=0.0, unit='mm')
        plug = Plug()
        d1 = Pin()
        push.drives(plug.key.insert)
        plug.p1.lift.drives(d1.lift, ratio=-1)       # ROOT-declared, READS p1.lift

    class Lock(LockBody):
        time = Time.running()

`LockBody` is the untimed twin: the same declarations, no time base.

Measured (`probe_sim.py`):

| what | result |
| --- | --- |
| `Lock()` posed with `set_state(push=1.0)` | poses: `key.insert=1.0`, `p1.lift=0.5`, `d1.lift=-0.5` |
| `Lock()` published FRESH (never posed) | PUBLISHED |
| `Lock()` POSED, then published | **REFUSED `DoublyBound`**, the wart's message verbatim |
| `LockBody()` posed, then published | PUBLISHED |
| `Sim(Lock(), 0.05)`, `move('push', to=2.0, duration=0.2)`, `run(0.4)` | runs: `key.insert=2.0`, `p1.lift=1.0`, `d1.lift=-1.0` |
| publication while that LIVE run owns the tree | PUBLISHED, and the run goes on: the next tick holds the same bank |

The refusal is therefore not the declarations. It needs a running root
whose coordinates were last bound by an ENUMERATION rather than by a run —
which is exactly what `solid build` hands the producer, because the
builder poses and renders the tree before it writes the viewer snapshot.

The refusing message, verbatim:

    DoublyBound: plug.p1.lift would be bound by the relation key.insert
    drives p1.lift and by the relation plug.p1.lift drives d1.lift. A
    coordinate has exactly one binder in one enumeration of the tree, and
    the framework does not compare two values to decide whether two
    statements agree: they are ordinarily symbolic expressions. Drop one
    of them.

## 2. Where it is raised, and why — the measured cause

The traceback is NOT the publication walk. It is the epilogue:

    core/serializer.py:249   drive_tree(node, lambda …: target._states[name])
                             ← the RE-RENDER in symbolic_document's finally,
                               after delivery.restore()
    node/qualified.py:311    root.render()
    node/assembly.py:103     solve_relations(assembly, enumeration)
    motion/couplings.py:2157 _refuse_double(…)

(The wart cites the chain `serializer.py:240` → `qualified.py:311` →
`couplings.py:1898`. The last two match the branch base `bd74132`
exactly — `root.render()` and the `_step_relation` call in
`solve_relations` — but at that base line 240 is a comment, while the
walk's own `drive_tree` is line 227 and the re-render's is line 249,
unmoved since. Both calls reach `qualified.py:311`, so the wart's chain
does not by itself say which; the trace above, and the `solid build`
traceback of §5, say it is the re-render.)

`probe_publication.py` traces every `clear_solved` and every
`_step_relation` across the three enumerations. The sequence, slot by
slot and binder by binder (`_bound_by` is what
`ResolvedEnd.bound()`'s freshness rule reads; `enum` is
`_enum_marker`):

**Enumeration 1 — the numeric pose (`set_state(push=1.0)`).** Tree order
runs the root's whole phase before the child's, so:

1. `Lock`'s phase: `push drives plug.key.insert` solves FORWARD →
   `key.insert = 1.0`, binder = that record, `_bound_by = Lock`.
   `plug.p1.lift drives d1.lift` finds neither end bound → DEFERRED.
2. `Plug`'s phase: `key.insert drives p1.lift` solves FORWARD →
   `p1.lift = 0.5`, binder = that record, **`_bound_by = Plug`**.
3. The enumeration's own fixpoint (`run_deferred`, which runs with NO
   phase current): `plug.p1.lift drives d1.lift` solves FORWARD →
   `d1.lift = -0.5`, binder = that record, **`_bound_by = None`** —
   `phase.note_bound` stamps `_bound_by` only while a SIMULATE phase is
   current, and the fixpoint runs outside every phase.

State handed to the producer: `key.insert=1.0 (_bound_by=Lock)`,
`p1.lift=0.5 (_bound_by=Plug)`, `d1.lift=-0.5 (_bound_by=None)`, all
three marked with enumeration 1.

**Enumeration 2 — the publication walk.** `_coordinate_publication`
installs a `RunBinder`, and `drive_tree`'s `collect` binds EVERY joint
coordinate of the tree to a symbolic token before anything renders. So
when the relations are attempted:

    attempt push drives plug.key.insert
        driven plug.key.insert … binder=<the running simulation> run_owned=True bound=True
        -> direction='run'
    attempt plug.p1.lift drives d1.lift
        driver plug.p1.lift  … run_owned=True bound=True
        driven d1.lift       … run_owned=True bound=True
        -> direction='run'
    attempt key.insert drives p1.lift
        driven plug.p1.lift  … run_owned=True bound=True
        -> direction='run'

Every relation is recorded as solved BY THE RUN, in neither direction —
which is the contract, and is why the publication walk itself is
innocent. Two consequences, both measured:

- `clear_solved` in this enumeration is handed the PREVIOUS
  enumeration's record — for `Lock`: `[key.insert, key.insert, d1.lift]`,
  for `Plug`: `[p1.lift, p1.lift]` — and correctly skips every one of
  them under the run-owned exemption.
- `_run_phase` then OVERWRITES `_solver_bound` with this phase's own
  bound list, which for both assemblies is **empty**: nothing in this
  enumeration bound a joint coordinate, because the delivery bound them
  all outside it. (In the real lock the list is not empty — it holds the
  five spring `height` PLAIN ports the publication did compute — but it
  holds none of the joint coordinates.)

The record of what enumeration 1 bound is now gone.

**`delivery.restore()`** then puts back each coordinate's value, binder,
`_enum_marker` and `_bound_by` exactly as saved — the export spec's "the
tree is left as it was found". It restores nothing at the assembly level.

**Enumeration 3 — the re-render, in the same `finally`.**

    clear_solved(Lock) _solver_bound=[]     ← nothing to drop
    attempt push drives plug.key.insert
        driven plug.key.insert value=1.0 enum=<enum 1> _bound_by=Lock bound=False
        -> forward                                   (correct: rebound fresh)
    attempt plug.p1.lift drives d1.lift
        driver plug.p1.lift value=0.5  enum=<enum 1> _bound_by=Plug bound=False
        driven d1.lift       value=-0.5 enum=<enum 1> _bound_by=None bound=True
        -> direction='backward'                      ← THE DEFECT
        after  d1.lift … binder=<relation plug.p1.lift drives d1.lift solved backward>
    clear_solved(Plug) _solver_bound=[]     ← nothing to drop
    attempt key.insert drives p1.lift
        driver plug.key.insert value=1.0 bound=True
        driven plug.p1.lift    value=0.5 binder=<relation plug.p1.lift drives d1.lift
                                                 solved backward> bound=True
        -> RAISED DoublyBound

The asymmetry is the whole defect, and it is `_bound_by`:

- `p1.lift` was bound in `Plug`'s phase, so `_bound_by = Plug`. While
  `Lock`'s own attempt runs, `Plug` is a DESCENDANT of the attempting
  assembly, so `ResolvedEnd.bound()` answers UNBOUND — "that assembly
  will rebind it later in this pass". Correct, by
  `deferred-read-is-current`.
- `d1.lift` was bound by the enumeration's fixpoint, outside every
  phase, so `_bound_by = None`. `bound()` answers BOUND — "a value
  bound outside any enumeration; nothing left to run will reclaim it;
  trust it". Also correct, by the same rule, for the state it is shown.

One end unbound, the other bound, and a law that inverts (`ratio=-1`):
the relation is read BACKWARD into `plug.p1.lift`. `Plug`'s own relation,
picked up next, finds its driven coordinate already bound by the root's
record and raises `_refuse_double` — naming, as the wart reports, the
root's relation as a binder of a coordinate it only reads.

Neither `bound()` nor `_step_relation` behaves wrongly. What is wrong is
the STATE they are given: a tree holding enumeration 1's values while
nothing holds enumeration 1's record of having bound them, so the clear
that would have dropped them drops nothing.

**Why the untimed twin escapes.** Under `LockBody` the publication walk
has no delivery, so its own enumeration BINDS both coordinates through
the relations (symbolically). `_solver_bound` is repopulated with them,
and the re-render's `clear_solved` drops both — `probe_publication.txt`,
the untimed half: `clear_solved(LockBody) _solver_bound=[key.insert,
key.insert, d1.lift]`, then `clear_solved(Plug) _solver_bound=[p1.lift,
p1.lift]`, then every relation solves FORWARD. This is the behaviour the
running path has to be brought back to.

**Why a live run escapes.** When a `Sim` owns the tree the coordinates
are run-owned before the publication and run-owned after the restore, so
the re-render's `clear_solved` skips them under the same exemption and
every end reads run-bound — the `direction='run'` short circuit answers
every relation. Measured in §1, row 6.

## 3. What a live `Sim` does with the same shape

`Sim(Lock(), 0.05)` accepts the declarations, `move('push', to=2.0,
duration=0.2)` + `run(0.4)` poses `key.insert=2.0`, `p1.lift=1.0`,
`d1.lift=-1.0`, and the tree publishes while that run owns it. So does
every untimed pose, and so does `set_state` under the running root — the
pose in §1 is the running root's own. `sim.run` does NOT refuse: only the
document producer does, and only over a tree an enumeration last bound.

## 4. Two candidate fixes, measured

`probe_candidates.py` applies each as a monkey patch and publishes the
posed fixture.

The fixture has a second pair, `OpaqueBody`/`OpaqueLock`: the same two
relations with a root law that does NOT invert (`squared`). It refuses
too, and differently —

    baseline, law that does not invert: REFUSED DoublyBound: d1.lift
    would be bound by the relation plug.p1.lift drives d1.lift and by the
    relation plug.p1.lift drives d1.lift.

— because the root's relation then DEFERS instead of inverting, and the
enumeration's fixpoint (no phase current, so the stale `d1.lift` reads
trustworthy again) finds both ends bound and refuses the relation against
its own previous binding. The backward step of §2 is one of two ways the
stale value surfaces; the stale value is the single cause.

**A — the producer puts back what its walk replaced.** The publication
saves each assembly's `_solver_bound` before the walk and restores it
beside the coordinates.

    baseline:    REFUSED DoublyBound: plug.p1.lift would be bound by …
    candidate A: PUBLISHED
    after:       plug.key.insert=1.0, plug.p1.lift=0.5, d1.lift=-0.5
    candidate A, law that does not invert: PUBLISHED

The pose is reproduced exactly: the re-render clears `key.insert` and
`d1.lift` at `Lock`'s phase and `p1.lift` at `Plug`'s, then solves
FORWARD throughout, which is what enumeration 1 did.

**C — the enumeration's fixpoint stamps `_bound_by`.** `run_deferred`
marks each slot it binds with the assembly whose relation it solved, so
`d1.lift` would carry `_bound_by = Lock` instead of `None`.

    candidate C: REFUSED DoublyBound: d1.lift would be bound by the
    relation plug.p1.lift drives d1.lift and by the relation plug.p1.lift
    drives d1.lift.

It only MOVES the refusal. With the stamp, `Lock`'s own attempt defers
(`_bound_by = Lock` is the attempting assembly), `Plug`'s phase rebinds
`p1.lift` fresh — and then the fixpoint, which runs with no phase
current, reads the stale `d1.lift` as trustworthy again and refuses the
relation against its own previous binding. The stale value is the
problem; marking it differently does not remove it.

## 5. The originating project

`evidence/probe_lock.py` runs a COPY of
`projects/Locks/Pin_tumbler_lock` (copied out with `tar`; the project is
never written to) with its five lift relations moved back from the root
into `Plug`'s body — the shape its `design.md` §5 says it wanted — posed
with `set_state(insertion=-30.0, rotation=0.0)` and then published:

    posed
      declarations: ['insertion', 'rotation']
    REFUSED DoublyBound: plug.p1.lift would be bound by the relation
    key.insert drives p1.lift and by the relation plug.p1.lift drives
    d1.lift. …

    (candidate-a)
    posed
      declarations: ['insertion', 'rotation']
    PUBLISHED (candidate A)

`solid build` on that same copy — the command the wart reports — refuses
in the same place, which is what fixes the frame beyond doubt:

    File "solid_node/core/builder.py", line 474, in _start
      self._write_viewer_snapshot()
    File "solid_node/core/builder.py", line 650, in
      _write_viewer_snapshot_with_inventory
      with symbolic_document(self.node) as (declarations, instructions):
    File "contextlib.py", line 144, in __exit__
      next(self.gen)
    File "solid_node/core/serializer.py", line 249, in symbolic_document
      drive_tree(node, lambda target, path, name, declaration:
    File "solid_node/node/qualified.py", line 311, in drive_tree
      root.render()
    …
    File "solid_node/motion/couplings.py", line 2157, in _step_relation
      _refuse_double(
    DoublyBound: plug.p1.lift would be bound by the relation key.insert
    drives p1.lift and by the relation plug.p1.lift drives d1.lift. …

The geometry had already been built at that point: the builder poses and
renders the tree, writes its artifacts, and only then publishes the
snapshot the viewer reads.

The same copy with the project's own workaround in place (all five
relations in the root) publishes on both. The project's five springs,
its `Bound` ranges reading five other coordinates, its `piecewise` laws
and its named driver pins are all present in both runs, and none of them
is the cause: the minimal fixture of §1, with one child relation, one
root relation and an affine law, reproduces the refusal on its own.

## 6. Open questions

1. `_ran_in_enumeration` is the other assembly-level mark the
   publication's phases overwrite. Nothing measured here depends on it
   (the re-render opens a new enumeration, against which the stale mark
   compares unequal either way), so this cycle does not restore it.
   Whether it should be restored for the same reason is unsettled.
2. The asymmetry `_bound_by = None` creates is not confined to
   publication: any value a `run_deferred` binding leaves behind reads as
   trustworthy in a LATER enumeration where the same value bound in a
   phase would defer. It is harmless today because `clear_solved` drops
   those values at the owning assembly's next phase — the record the
   publication is the only thing known to destroy. No second way to
   destroy it was found, and none was searched for exhaustively.
3. The defect needs the root's relation to have been DEFERRED in the
   pose — which happens exactly when its source is bound later in that
   pass than the root's own phase, i.e. by a descendant. A child's
   `simulate()` cannot be that descendant under a running root (binding
   a run-owned coordinate imperatively is refused on its own, correctly),
   so a child-declared RELATION is the shape, as the lock states it.
   Whether some other route to a deferred root relation exists was not
   searched exhaustively.

---

# Implementation record

Measured on this worktree, branch `fix-warts` at the planning commit
`3519c61`, with

    PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest …

## 7. Baseline (task 1.1)

At `3519c61`, before any edit:

| file | result |
| --- | --- |
| `tests/test_running_document.py` | 71 passed, 83 subtests passed |
| `tests/test_running_simulation.py` | 73 passed, 19 subtests passed |
| `tests/test_couplings.py` | 177 passed, 170 subtests passed |
| `tests/test_running_corpus.py` | 8 passed, 42 subtests passed |
| the four together | `329 passed, 2 warnings, 314 subtests passed in 23.47s` |

## 8. The fixtures, and the RED they produce (tasks 1.2 to 1.4)

`tests/running_project/machine.py` gains `StatedPlug` (the CHILD
assembly stating `key.travel.drives(p1.lift, ratio=0.5)` over the
existing `Slide` and `Pin` leaves), `StatedBelowBody` (the root stating
`push.drives(plug.key.travel)` and `plug.p1.lift.drives(d1.lift,
ratio=-1)`), `StatedBelow` (the same, running) and `StatedBelowOpaque`
(the running root with `law=squared`, which does not invert). It is
`evidence/fixture.py`'s `Lock`/`OpaqueLock` in the running project's own
vocabulary; nothing is added to `tools/generate_running_corpus.py`'s
`CORPUS`.

Measured on the fixtures before any change to the framework, the wart
reproduces verbatim:

    posed running  plug.key.travel=1.0, plug.p1.lift=0.5, d1.lift=-0.5
    running posed  REFUSED DoublyBound plug.p1.lift would be bound by the
                   relation key.travel drives p1.lift and by the relation
                   plug.p1.lift drives d1.lift. …
    posed untimed  plug.key.travel=1.0, plug.p1.lift=0.5, d1.lift=-0.5
    untimed posed  PUBLISHED
    posed opaque   plug.key.travel=1.0, plug.p1.lift=0.5, d1.lift=0.25
    opaque posed   REFUSED DoublyBound d1.lift would be bound by the
                   relation plug.p1.lift drives d1.lift and by the
                   relation plug.p1.lift drives d1.lift. …
    running fresh  PUBLISHED

RED, `tests/test_running_document.py::StatedBelowTest`, at the planning
commit's framework code:

    $ … -m pytest tests/test_running_document.py -q -k StatedBelow
    FAILED …::StatedBelowTest::test_a_law_that_does_not_invert_publishes_too
    FAILED …::StatedBelowTest::test_a_posed_running_tree_of_that_shape_publishes
    FAILED …::StatedBelowTest::test_a_posed_tree_poses_again_after_publication
    FAILED …::StatedBelowTest::test_posed_or_not_publishes_the_same_document
    4 failed, 1 passed, 71 deselected in 1.47s

Each of the four fails with `DoublyBound` — the three affine ones naming
`plug.p1.lift` "bound by the relation key.travel drives p1.lift and by
the relation plug.p1.lift drives d1.lift", the opaque one naming
`d1.lift` bound twice by one relation. The fifth,
`test_the_untimed_twin_is_unchanged`, passes red and green: the untimed
path is the reference behaviour, not a new one.

`tests/test_running_simulation.py::StatedBelowRunTest` (task 1.4) is
GREEN at the planning commit too, and deliberately so: a live run always
accepted this shape (§1, §3). It is a guard that the completed restore
does not disturb one — `2 passed, 73 deselected`.

## 9. GREEN, and the mechanism (task 2)

`symbolic_document`'s `remember` now snapshots each visited node's
`_solver_bound` beside its driver states, and the `finally` puts it back
after `delivery.restore()` and before the re-render, only when
`delivery is not None`, restoring absence as absence (`clear_solved`
POPS the record).

    $ … -m pytest tests/test_running_document.py -q -k StatedBelow
    5 passed, 71 deselected in 1.11s

The mechanism, not just the colour: `evidence/probe_publication.py`
re-run against the changed worktree traces the fixture's RE-RENDER
(enumeration 3) consuming the restored record and solving every relation
FORWARD, where §2 measured it clearing nothing and stepping backward:

    [re-render (the finally block)] clear_solved(Lock) _solver_bound=[
        'key.insert(value=1.0, run_owned=False, enum=0x…c807c0)',
        'key.insert(value=1.0, run_owned=False, enum=0x…c807c0)',
        'd1.lift(value=-0.5, run_owned=False, enum=0x…c807c0)']
    attempt push drives plug.key.insert
        driven plug.key.insert value=None binder=None … bound=False
        -> changed=True direction='forward'
    attempt plug.p1.lift drives d1.lift
        driver plug.p1.lift value=0.5 … _bound_by=Plug bound=False
        driven d1.lift       value=None binder=None … bound=False
        -> changed=False direction=None          (deferred, as in the pose)
    [re-render (the finally block)] clear_solved(Plug) _solver_bound=[
        'p1.lift(value=0.5, run_owned=False, enum=0x…c807c0)',
        'p1.lift(value=0.5, run_owned=False, enum=0x…c807c0)']
    attempt key.insert drives p1.lift
        driven plug.p1.lift value=None binder=None … bound=False
        -> changed=True direction='forward'
    attempt plug.p1.lift drives d1.lift
        driver plug.p1.lift value=0.5 … bound=True
        driven d1.lift      value=None … bound=False
        -> changed=True direction='forward'
    -- after publication
       plug.key.insert=1.0  <relation push drives plug.key.insert solved forward>
       plug.p1.lift=0.5     <relation key.insert drives p1.lift solved forward>
       d1.lift=-0.5         <relation plug.p1.lift drives d1.lift solved forward>
    running root: PUBLISHED

Both records are the ones ENUMERATION 1 wrote — the slots still carry
enumeration 1's marker (`enum=0x…c807c0`) and its values — so
`clear_solved` drops all three coordinates (`value=None`, `binder=None`
at each attempt), and the pass that follows is the pose's own pass, in
the pose's own direction. The asymmetric read of §2 cannot arise,
because neither end carries a stale value to read.

Task 2.4: `solid_node/motion/couplings.py`, `solid_node/motion/ports.py`,
`solid_node/node/phase.py` and `solid_node/node/assembly.py` are
unchanged — read, and confirmed by `git diff --stat`, whose only source
file is `solid_node/core/serializer.py`.

## 10. The recorded documents (task 3)

- `ByteIdentityTest`: `1 passed, 7 subtests passed`, and
  `git status tests/base_documents/` is empty — no captured document
  moved a byte.
- `python tools/generate_running_corpus.py` rewrote
  `tests/running-corpus.json` (14 scenarios over 12 machines, 276 ticks,
  185444 bytes) and `git diff` on it is empty.

## 11. Proof (task 4)

4.1, after the change:

| file | result |
| --- | --- |
| `tests/test_running_document.py` + `test_running_simulation.py` + `test_couplings.py` + `test_running_corpus.py` + `test_running_stops.py` + `test_running_jumps.py` | `434 passed, 2 warnings, 653 subtests passed in 30.68s` |
| the whole suite (`pytest tests/ -q`) | `2669 passed, 4 skipped, 50 warnings, 1493 subtests passed in 328.54s` |

The four baseline files of §7 went from `329 passed, 314 subtests` to
`336 passed, 314 subtests` — the seven tests this cycle adds (five in
`test_running_document.py`, two in `test_running_simulation.py`) and
nothing else. No test was edited to make it pass.

4.2, the probes re-run against the changed worktree (before/after):

| probe | before | after |
| --- | --- | --- |
| `probe_publication.py`, running root | `REFUSED DoublyBound: plug.p1.lift …` | `PUBLISHED`, with the trace of §9 |
| `probe_publication.py`, untimed twin | `PUBLISHED` | `PUBLISHED`, trace unchanged |
| `probe_sim.py` | live run, fresh publication and hand pose: `PUBLISHED`; publication after an enumeration pose refused | all four `PUBLISHED`, bank unchanged after the publication and after one more tick |
| `probe_candidates.py`, baseline (no patch) | `REFUSED` on both laws | `PUBLISHED` on both laws |
| `probe_candidates.py`, candidate A | `PUBLISHED` | `PUBLISHED` — the patch is now a NO-OP, it restores what the producer already restores |
| `probe_candidates.py`, candidate C | `REFUSED DoublyBound: d1.lift …` | `PUBLISHED` — the stale value it could not remove is gone, so its stamp no longer has one to misread |

4.3, the originating project. A copy of
`projects/Locks/Pin_tumbler_lock` was made with `tar` into the session's
scratchpad (the project itself was never written to; `git status` there
is clean), and its five lift relations moved back from
`PinTumblerLock`'s body into `Plug`'s, after the `key = Key(…)`
declaration the bound reads:

    key.insert.drives(p1.lift, law=key_lift(0))
    …
    key.insert.drives(p5.lift, law=key_lift(4))

With NO patch, against this worktree:

    $ … evidence/probe_lock.py <copy>
    posed
      declarations: ['insertion', 'rotation']
    PUBLISHED

against `REFUSED DoublyBound: plug.p1.lift …` at the planning commit
(§5). The lock publishes in the shape its `design.md` §5 says it wanted.
Making that edit in the project itself stays the pilot's call.

## 12. The record (task 5)

- `docs/architecture.md`: the running-publication section now says what
  the producer puts back beside the coordinates, and why the untimed path
  needs none of it.
- `docs/changelog.rst`: one Unreleased entry.
- `workflow/warts.md`: the finding marked **FIXED (cycle
  `a-read-is-not-a-binding`)**, its stale `serializer.py:240` line
  reference corrected to the re-render's `:249` (`:240` is a comment at
  this base; the walk's own call is `:227`), and the two corrections the
  cycle's evidence makes to the filing recorded under it. The two
  out-of-scope findings of §6 are filed, untriaged, in their own section.
- No ADR (task 5.4, design.md decision 4).
