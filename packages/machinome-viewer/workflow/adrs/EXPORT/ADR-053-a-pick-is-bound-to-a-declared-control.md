# ADR-053: A pick is bound to a declared control, and the part follows commits

**Status:** Accepted

**Date:** 2026-09-14

**Change:** `drive-the-run-by-touch`

**Extends:**
- [ADR-048: Running controls submit requests; nothing binds back](ADR-048-running-controls-submit-requests.md)

**Consumes:**
- solid-node ADR-112: A control is a declaration on the model, and the
  gesture's geometry comes from the tree

## Context

ADR-048 gave a running document a panel and closed with a promise in its
own Consequences: *"Constrained dragging of a part is deliberately out:
the next viewer cycle binds a pick to a declared input through this same
command interface, with the same blocked-travel reporting."* This is that
cycle. The pilot's ask has been the same since 2026-09-12 — click the
dial, and the dial advances — and the panel only ever answered half of
it: a maker drove the Pascaline module by reading its inputs' qualified
ids off a list, not by touching the machine in front of them.

The other half became possible because the framework built it. The viewer
cannot infer which part a hand may turn, or what turning it means. The
module's own document is the proof: `program.sources['tens.input.turn']`
is `['tens_entry', 'units_entry']`, because the carry from the column
below moves the tens dial too, and nothing in the document says which of
the two a hand on that dial means; and `units.drum.turn` is in the bank
and the number drum turns with it, but a hand does not turn the drum —
it sits under the lid, and the ratchet is on the input arbor. A viewer
that made every posed part draggable would let a maker do what the
machine forbids.

So the binding is a **declaration**. solid-node's ADR-112 publishes it: a
version 5 document whose tree declares `Button(part, instruction)` or
`Turn(part, input)` carries a top-level `controls` table beside
`instructions`, additively, with the gesture's geometry read off the tree
(`joint`, `coordinate`, `axis`, `origin`) and the ratio (`per_unit`)
measured off the compiled program at the rest bank. What a viewer does
with that table is this ADR.

## Decision

**A part becomes touchable only because the document says so; a press is
the declared instruction and a drag is a sequence of relative moves on
the declared input, issued through the same `run()` handle and reported
the same way; and nothing in either gesture writes a coordinate.**

1. **The table is read on the refusal surface, before anything
   renders.** `assertRenderable` already refuses a document version this
   build cannot read, a flexible technology it cannot evaluate, a
   bindings table it cannot resolve, a program it cannot execute and an
   expression naming an undeclared driver. The `controls` table joins it,
   after the program its entries reference and before the tree walk.
   Every refusal names the document, the control's key and the offending
   value. A table read lazily, skipping entries that do not resolve,
   would put a viewer on screen missing exactly the control the author
   cared about, with no message. A document with no key gets `[]` and
   reaches exactly the code it reached before.

2. **The gesture's world line comes from ONE node's world matrix.** With
   `W` the joint node's `matrixWorld`, the line is `W · origin` along
   `W`'s rotation of `axis` — ADR-112 §3's consumer rule, with no case
   analysis. It is exact *while the joint turns*: the joint's own
   rotation fixes that own-frame line, so the plane a drag is measured in
   does not move under the drag that is moving the part.

   That is exact on one condition — `axis` and `origin` are published in
   the node's OWN frame, so the joint's placement must be the **leading
   run** of its node's operations: zero or more translations and then the
   rotation naming the entry's coordinate. Both shapes the producer
   publishes satisfy it (`r` alone, and `t(−a), r, t(a)` for a
   `Revolute(at=a)`, whose entry publishes `origin = a`). A document that
   fails the check is refused by name rather than turned about a wrong
   line.

3. **A pick is the nearest VISIBLE hit, and it must belong to a
   control.** three.js's `Raycaster` in this version does not consult
   `Object3D.visible` at all, so visibility is filtered here; having paid
   for that filter, the cast goes against the whole tree and takes the
   nearest hit, which buys the rule a maker expects — a part in front of
   a control is in front of it, and a dial under a closed lid is not
   pressed through the lid. A mesh finds its control through a map
   rebuilt at the three places a mesh can be replaced, not through a
   back-reference stamped on the mesh, which would survive a targeted
   artifact update only if every construction site remembered it.

4. **A press is a pointerup inside a four-pixel threshold**, and issues
   the declared instruction through the same `request(...)` the panel's
   button goes through — so it is indistinguishable to the run, to its
   listeners and to a readback. A press on a part carrying only a turn
   does nothing and reports nothing: there is no instruction to submit,
   and inventing one would move the machine in a way nobody declared.

5. **A quantum is committed, not accumulated, and only one is ever
   outstanding.** The quantum is the input's current nudge amount times
   the published ratio — 36° of sweep per digit on a Pascaline dial. Each
   time the unwrapped sweep crosses one, exactly one
   `move(input, {by, duration})` is issued, its sign taken through the
   ratio (a sweep of −36° on `per_unit = −36` asks for `+1`). At most one
   is in flight, because `Run.claim` gives an input one owner at a time
   and a second `move` would be refused rather than executed. What the
   gesture owes is **recomputed** from where the pointer stands rather
   than queued, so a sweep forward and back nets out instead of being
   paid for twice.

6. **A request that does not complete does not advance the origin**, and
   latches that direction until the maker backs off or reverses. This is
   ADR-048's "a blocked request accumulates no hidden movement" applied
   to a gesture: a drag into the ratchet reports blocked, leaves nothing
   to be executed later, and does not fire one blocked request every
   retire while it is held there.

7. **The part follows commits, never the pointer.** Nothing in the
   gesture writes a coordinate, sets a matrix or poses anything; the only
   effect a drag has on the scene is through the run's committed frames,
   which reach the tree exactly as they do for a panel nudge. The pointer
   may run ahead, and a machine that refuses to move does not move.

8. **The outcome is reported twice through one path.** `request` gains an
   optional client point and, when given, also writes a transient
   `role="status"` label there with `formatOutcome`'s own words. One code
   path, two places: a press that is blocked says exactly what a nudge
   that is blocked says.

9. **The gesture ends on the same five sides a jog does** — `pointerup`,
   `pointercancel`, `lostpointercapture`, the window's `blur`, and a
   `visibilitychange` to hidden — and each restores the camera, releases
   the capture and clears the affordance. A `move` already in flight is
   left to retire and report: it is a movement the machine agreed to
   make, and cancelling it would be the viewer inventing a stop the maker
   did not ask for.

10. **`partControls` is its own switch, and `controls()` is not gated by
    it.** The part affordance and the driver panel gate different pixels
    and are chosen independently, because a host that builds its own
    instrument panel still wants the dial pressable — the shop floor is
    exactly that host. What either switch gates is the pixels and the
    pointer, never an interface: `controls()` answers and the run API is
    whole either way. The declared API version rises to 12, because a
    host that means to present a machine a maker can touch has no other
    number to check.

Every decision above is pure data or pure vector math in
`partControls.ts`, tested in plain node; the DOM and the three.js are in
`viewer.ts` and decide nothing — the same split ADR-048 made for the
panel.

## Consequences

- A maker meets a machine and touches it. Pressing the Pascaline
  module's units dial enters one digit and turns the drum; dragging that
  dial the way the ratchet forbids reports blocked and moves nothing, on
  the real document, with the real mouse.
- What is touchable is auditable: it is a table in the document, refused
  by name when it does not resolve, and a part nothing declares still
  orbits the camera exactly as before.
- A drag is looser than the pointer and never wrong. Because a partially
  admitted quantum does not advance the origin, the pointer can lead the
  part by the unadmitted remainder — the same trade the framework already
  states about `per_unit` being a reading at rest.
- Below about 8.6° between the ray and the joint's plane the sweep is
  measured on screen instead, and exactly edge-on its sign is a stated
  convention rather than geometry. A maker who finds the dial turning the
  wrong way orbits a few degrees and gets the in-plane mode back.
- A hovered part whose node declares no colour gets the cursor and the
  title and no highlight: it renders through `MeshNormalMaterial`, which
  has no `emissive`.
- This viewer refuses one document shape the framework permits — two
  controls of the same kind on one part — because a press would have two
  meanings and the viewer would have to choose. A matching compile-time
  refusal is a framework follow-up.
- Not in this: no `Slide` (a prismatic drag), because the framework
  proposes none; no dialling by position, which is the historical
  Pascaline's gesture and belongs to the model; no keyboard gesture; and
  no stream of the crossings and stops a drag passes through, which is a
  different feature from the report a gesture needs.

## Alternatives considered

**Infer the binding in the viewer** from the reaching table and the posed
tree. Rejected by ADR-112 for the framework and rejected here for the
same reason: it is ambiguous exactly where it matters, and it makes
untouchable parts touchable.

**Cast against control meshes only.** Cheaper, and wrong: the filter for
`visible` has to exist anyway, and without the nearest-hit rule a dial
under a closed lid is pressed through the lid.

**Give each mesh a back-reference to its control at load.** It goes stale
silently the first time a construction site forgets to set it; a map
rebuilt at the three points the tree changes cannot go stale without one
of those three failing loudly.

**Let the part follow the pointer and reconcile afterwards.** That is a
two-way binding by another name, and the same bug ADR-048 refused for the
slider: it would show a machine in a position the run never committed.

**Advance the origin by the travel a partially blocked request actually
admitted.** It keeps pointer and part in register through a partial
block, and it adds a second rule where one is provably enough for the
acceptance machine, whose ratchet admits exactly zero. Recorded, not
taken.

**Outline a hovered part with a `Box3Helper`.** Material-independent and
easy to assert, and it draws a box around a dial, which is worse to look
at than no highlight at all.
