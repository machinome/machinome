## Why

The pin tumbler lock (`projects/Locks/Pin_tumbler_lock`, migrated to
`Time.running()` on 2026-09-14) states the sentence its mechanism makes —
"the key lifts the pins inside the plug" — in `Plug`'s own body, and the
root then reads those same lifts to place the five driver pins and the
five springs that ride on them. `solid build` refuses the document:

    DoublyBound: plug.p1.lift would be bound by the relation key.insert
    drives p1.lift and by the relation plug.p1.lift drives d1.lift. A
    coordinate has exactly one binder in one enumeration of the tree …

The second relation READS `plug.p1.lift`; the message names a relation's
SOURCE as a binder of it. Every untimed pose, every `Sim` and the whole
test suite accept exactly these declarations — measured, with a live run
that poses the shape correctly, in `evidence.md` §3. The project moved all
five lift relations into the ROOT's body as a workaround and recorded the
reason as the framework's rather than its own.

The refusal is not in the publication walk. It is in the epilogue
`symbolic_document` runs after that walk: the producer restores every
coordinate's value, binder and freshness marks — the contract the export
spec already states — and then re-renders the tree, but it does NOT
restore the ENUMERATION bookkeeping its own walk overwrote. Under a
running root the publication enumeration binds no JOINT COORDINATE (the
delivery bound them outside it, so every relation into one records as
solved by the run), so every assembly's record of what its previous phase
bound is replaced by one naming at most the plain ports the publication
computed; the re-render's clear then drops none of the coordinates, the pose's values survive into a new enumeration, and
the freshness rule reads the two ends of the root's relation
ASYMMETRICALLY — one stale, one trusted — so the relation is read
BACKWARD into the child's coordinate. The child's own relation then finds
its driven coordinate bound by the root's record and raises. Full
sequence, binder by binder, in `evidence.md` §2.

## What Changes

- The producer's restore is completed: publishing a document under a
  running root puts back, beside every coordinate's value, binder and
  freshness marks, each assembly's record of what its own previous
  simulate phase bound — so the re-render that follows clears and
  re-solves exactly as it would have if nothing had been published.
- A relation a CHILD declares into its own coordinate, read by a relation
  the ROOT declares, is pinned as a legal shape under a running root: it
  publishes, and the published document reproduces the pose the tree
  already held.
- No change to the couplings contract, to `_step_relation`, to the
  freshness rule of `deferred-read-is-current`, or to ADR-099's fixpoint:
  all three are correct on the state they are given, and the defect is
  the state the producer leaves them.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `export`: "A committed bank poses the geometry" — the producer's
  restore names the enumeration bookkeeping as well as the coordinates,
  and the shape the lock states is pinned by scenario.

## Impact

- `solid_node/core/serializer.py` (`symbolic_document`,
  `_coordinate_publication`) and possibly
  `solid_node/node/assembly.py` (`CoordinateDelivery`), depending on
  which of the two owns the restore — design.md decides.
- `tests/test_running_document.py`, `tests/running_project/machine.py`
  (one new fixture pair), `tests/test_couplings.py`.
- Every `solid build` / `solid export` / `solid snapshot` of a running
  root, which is the only path that publishes a POSED tree.
- The pin tumbler lock may move its five lift relations back into
  `Plug`'s body once the fix lands; the project change is the pilot's,
  not this cycle's.
