## Context

`symbolic_document` (`solid_node/core/serializer.py`) is the document
producer's one walk over the tree. Under a running root it does three
things in order:

1. installs a `RunBinder` and binds EVERY joint coordinate of the linked
   tree to a symbolic token of its own qualified id, through
   `CoordinateDelivery` — the path `set_state` takes — before anything
   renders (`drive_tree`'s `visit`/`collect`, all of it ahead of
   `root.render()`);
2. yields, while the caller serializes the tree it has just rendered
   symbolically;
3. in its `finally`: puts back every node's driver snapshot, calls
   `delivery.restore()` — every coordinate's value, binder, `_enum_marker`
   and `_bound_by` — and then RE-RENDERS the tree under the restored
   numeric snapshot, because the operations still hold token values and
   nothing else would put numbers back in them.

Step 3's re-render opens a NEW enumeration over the tree. An enumeration
begins each assembly's phase by clearing what that assembly's own
PREVIOUS phase bound, and that record is `_solver_bound`, written on the
assembly at the end of every phase (`solid_node/node/assembly.py`,
`_run_phase`). The publication's own phases overwrite it — and under a
running root they bind no joint coordinate at all, because the delivery
bound them outside the enumeration and every relation into one is
therefore recorded as solved BY THE RUN. So the re-render inherits the
pose's values with nothing left that knows to clear them, and
`ResolvedEnd.bound()`'s freshness rule — correct on the state it is
shown — then reads two ends of one relation asymmetrically: a coordinate
a child's phase bound reads UNBOUND (that child will attempt again this
pass), while one the enumeration's own fixpoint bound reads BOUND (it
carries `_bound_by = None`, the mark of a value nothing left in the pass
will reclaim). The root's relation is solved from the wrong end, and the
child's relation is refused against it.

The whole measurement, binder by binder, is `evidence.md` §2; the
reproduction is a framework fixture, and the originating project is the
pin tumbler lock.

## Goals / Non-Goals

**Goals:**

- A running root posed by an enumeration publishes without refusal, and
  publishes the same document a never-posed tree of the same class does.
- After the publication the tree poses again exactly as if nothing had
  been published: same values, same binders, no false double binding.
- A child-declared relation read by a root-declared one is pinned as a
  legal shape, with a law that inverts and one that does not.

**Non-Goals:**

- Changing `_step_relation`, `ResolvedEnd.bound()`, `clear_solved`,
  `run_deferred` or anything else in `solid_node/motion/couplings.py`.
  All of them are correct on the state they are handed; measured
  alternatives that change them are rejected below.
- Changing the untimed or looping publication path in any byte. Those
  documents are pinned against captured base documents
  (`tests/test_running_document.py::ByteIdentityTest`) and this change
  must not move them.
- Changing what a document CONTAINS. Only the producer's restore changes.
- Making the lock's own edit. Moving the five lift relations back into
  `Plug` is the project's change and the pilot's call.

## Decisions

### 1. The producer restores the enumeration's record beside the coordinates

The export capability already requires that the producer "restore every
coordinate it bound — its value, its binder and its freshness marks" and
that "the tree is left as it was found". The defect is that the restore
is incomplete: the walk also replaces per-ASSEMBLY state, and puts none
of it back. The fix completes the restore rather than adding a new rule:
`symbolic_document` snapshots each assembly's `_solver_bound` where it
already snapshots that node's driver states (`remember`), and puts it
back in the same `finally`, BEFORE the re-render.

Measured as candidate A in `evidence.md` §4: the fixture publishes, the
non-invertible twin publishes, the pose is reproduced value for value,
and the originating project publishes in the shape it wanted (§5).

Why `symbolic_document` and not `CoordinateDelivery`: the delivery is
also `set_state`'s own path, where `restore()` is the rollback of a
REFUSED binding and no re-render follows. Teaching it about the
enumeration's bookkeeping would change `set_state`'s rollback for a
problem only the producer has.

Why only under a running root (`delivery is not None`): the untimed
publication binds the same coordinates THROUGH the relations, inside its
own enumeration, so its `_solver_bound` is repopulated and its re-render
already clears correctly — measured, `evidence.md` §2, "Why the untimed
twin escapes". Restoring the pre-publication record there would change
which slots the untimed re-render clears, for no defect, against
byte-identity tests.

### 2. The solver is not touched

Three alternatives were considered and rejected:

- **Stamp `_bound_by` in `run_deferred`** so a coordinate the
  enumeration's fixpoint binds is marked with the assembly whose relation
  it solved. Measured (candidate C, `evidence.md` §4): it only MOVES the
  refusal — the fixpoint runs with no phase current, reads the same
  stale value as trustworthy on the next pass and refuses the relation
  against its own previous binding. The stale value is the cause;
  marking it differently does not remove it.
- **Weaken `ResolvedEnd.bound()`** so a value from an earlier
  enumeration never reads as bound. This is exactly the naive fix
  `deferred-read-is-current` rejected with its own reproduction: it
  defers forever a value bound outside any enumeration — a hand
  assignment, or a node the serializer re-renders alone after its owning
  enumeration closed — and `UnreachedCoordinate` fires where nothing is
  wrong.
- **Have `_step_relation` prefer the forward direction when the driven
  end's value is stale.** This asks the solver to compare two answers
  and pick one, which the couplings capability refuses on purpose: "the
  framework does not compare two values to decide whether two statements
  agree".

### 3. The re-render stays

Not re-rendering under a running root would leave every operation holding
a token value after publication, which is what the re-render exists to
undo and what "rendering it again reproduces the same pose" pins.
Clearing the whole tree's coordinates after the restore instead of
restoring the record would destroy a LIVE run's bank — publication over a
tree a live `Sim` owns works today (`evidence.md` §1) and must go on
working.

### 4. The spec delta is one requirement in one capability

`export`'s "A committed bank poses the geometry" already owns the
producer's restore and the "left as it was found" scenario. The change
extends that requirement with the re-POSE half of the promise and with
the shape the lock states, and adds two scenarios beside the five it
already carries. Nothing in `couplings` changes: the shape is legal there
today, and every pose and every `Sim` already accepts it.

No ADR is proposed. This restores a stated contract and introduces no new
boundary; cycles 1 and 2 of this plan (`cancel-stops-the-command`,
`publish-only-what-runs`) set the same precedent.

## Risks / Trade-offs

- [The restore reaches only the assemblies the walk remembered.] → Under
  a running root `collect` calls `remember` for every assembly with a
  driver snapshot, which is every assembly the walk visits and therefore
  every assembly whose `_solver_bound` the walk's own phases overwrite.
  A subtree the walk never visits keeps its own record untouched, as
  today. A test poses a two-level tree, publishes, and poses again.
- [A live run's restored record names run-owned slots.] → `clear_solved`
  already exempts a run-owned slot, so the restored record changes
  nothing there; the existing scenario "publication runs over a tree a
  live run owns" must stay green, and a test re-measures the bank after
  the publication and one further tick.
- [`deferred-read-is-current`'s freshness rule.] → Untouched. The fix
  changes the STATE the rule reads, not the rule, and it changes it back
  to what the rule was designed for: a value whose owning assembly's
  record still exists, cleared at that assembly's next phase.
  `tests/test_couplings.py`'s deferred-read scenarios are the guard.
- [ADR-099's whole-tree fixpoint.] → Untouched. `run_deferred` goes on
  binding outside every phase and goes on leaving `_bound_by = None`;
  candidate C measured that changing this is both insufficient and a
  widening of the fixpoint's contract.
- [Untimed byte identity.] → The restore is conditional on the running
  delivery, so no untimed or looping document moves.
  `ByteIdentityTest` is the guard and runs unchanged.
- [`_ran_in_enumeration` is the other assembly-level mark the walk
  overwrites.] → Not restored by this change; nothing measured depends
  on it, because the re-render opens a new enumeration against which the
  stale mark compares unequal either way. Recorded as an open question
  in `evidence.md` §6 rather than fixed blind.

## Open Questions

1. Should `_ran_in_enumeration` be restored for the same reason? No
   failure was produced from it; left alone deliberately.
2. `run_deferred` leaving `_bound_by = None` is a real asymmetry that
   this change does not remove — it only stops the producer from
   creating the state in which the asymmetry can be read. Whether the
   fixpoint should bind under the stating assembly's phase at all is a
   couplings question, and a bigger one than this defect.
