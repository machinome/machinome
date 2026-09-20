## Context

Pilot ratified on 2026-09-20, not yet an accepted implementation ADR. The originating project is the
parked historical Astrarium, not a hypothetical motor API. See the proposal
and `workflow/docs/astrarium-running-time-drive.md` for evidence and exact
repository identities.

At the recorded framework base, `ClockRef.check()` rejects every `drives`
end. `Run.integrate()` admits motion only from active commands on declared
drivers. Time is bound into the pose after committing the bank, but is not
a moving source in the compiled relation graph. Removing the declaration
refusal alone would therefore not fix the runtime.

ADR-105 makes the run the sole joint binder; ADR-106 gives running laws an
incremental reading; ADR-108 stops connected motion rather than clamping a
part independently. ADR-127 explicitly prohibited clock-driven relations
while introducing elapsed-clock commitments. This proposal changes that
prohibition only for a running clock on the source side. The other decisions
remain constraints, not obstacles to bypass.

## Goals / Non-Goals

**Goals:**

- Start retained motion from declared model state, without a dummy driver,
  a startup `Sim.rate`, or author mutation in a tick callback.
- Use the existing relation vocabulary for enable, winding, finite travel,
  downstream gearing and retained-coordinate gates.
- Preserve deterministic stepping, replay, exclusive bank ownership,
  atomic failure and the existing numerical agreement rules.
- Publish enough information for an independent consumer to execute the
  same machine and supply producer-generated proof for that consumer.

**Non-Goals:**

- No automatic physical law: time supplies seconds, not gravity, torque,
  inertia, energy conservation, an escapement frequency or contact dynamics.
- No posed or event-driven Astrarium, historical CAD, or resumed project work.
- No new `Time` mode, public motor class, integrator callback, implicit
  dependency inference, clock commands, adjustable run clock, or new `State`
  support under `Time.running()`.
- No expansion of the supported `Play` topology, cyclic-law class or stop
  search guarantee just to make the API symmetrical. Existing refusals remain
  unless a time source itself requires the narrow change described here.
- No viewer implementation, package release, external issue or shop mutation.

## Decisions

### 1. Make time an explicit source, not another joint writer

Proposed class-body use (the joint-bearing `Shaft` already exists):

```python
def gated_rotation(owners, target):
    return lambda seconds, enabled: 6 * seconds * (enabled > 0.5)

class Machine(AssemblyNode):
    time = Time.running()
    enabled = Driver(default=1, range=(0, 1))
    shaft = Shaft()
    (time & enabled).drives(shaft.turn, law=gated_rotation)
```

`time.drives(shaft.turn, ratio=6)` is the affine case. Native seconds enter
the law; the result has the target coordinate's native units. The factory
still gets realized owners once and returns a callable over values in written
source order. No per-tick Python callback is introduced.

The time declaration must belong to the running root that owns the graph.
Foreign, descendant or mismatched clocks are refused with the relation's
identity. Time is never a writable target or an operator driver; it appears
in neither the input controls nor `sim.commands` nor the mechanical bank.
`sim.time == sim.tick * sim.dt` remains the clock authority.

Keep `simulate(): self.shaft.turn = self.time` refused when the run owns that
joint. Keep `self.part.rotate(self.time, axis)` valid as an ordinary absolute
pose expression. Their different meanings must be explicit in the docs.

**Alternatives rejected:** special-case imperative assignment would create a
second joint writer and make pose enumeration affect history; inventing a
`Motor` repeats existing law vocabulary; requiring an author-created driver
and startup rate preserves the very friction Astrarium reported.

### 2. Integrate the law along elapsed time, without assigning its absolute value

Construction evaluates the existing rest pose at time zero and seeds the
ordinary bank. No motion occurs merely because the tree is inspected,
rendered, serialized or constructed. For an advancing tick, a declared time
source traverses `[k*dt, (k+1)*dt]`. Commanded drivers traverse their admitted
paths simultaneously. A zero-duration input operation has a stationary
clock. Deferred actions keep their existing post-commit ordering.

The existing continuous-increment, jump-subtraction, self-read, selector and
conflict rules apply. For the example at a fixed enabled value, a tick adds
`6*dt` or zero. Crossing the enable threshold changes the branch; its jump
does not teleport the shaft by `6*time`. A smooth operating parameter in a
law still has the ordinary multivariate `f(end)-f(start)` semantics: this is
NOT a new rule saying that a law's value is angular velocity.

Elapsed time continues while a mechanism is disabled. When enabled again,
only the current interval contributes; missed travel is not stored. A
nonlinear time law uses the current global time on resumption, not an
invented mechanism-local age. Authors who need a phase retained while stopped
must declare that mechanical coordinate and use its retained state.

### 3. A mechanical stop blocks a drive path, never the clock

A single shared stoppable `time` input would wrongly connect every autonomous
mechanism. Give each resolved relation that explicitly names time a distinct
internal drive identity. All its targets share that identity; downstream
gearing driven by its first shaft shares its motion. Two separate time-source
relations do not become mechanically coupled just because both read seconds.

These identities are ephemeral admission sources, not public drivers or
extra persisted coordinates. Extend the existing candidate-source and
outward-motion tests to include them. If a ranged weight stops a train,
localize the boundary, commit the admitted prefix for the connected train,
and suppress the pushing time source for the remainder of that tick. An
unrelated time drive and inputs that relieve the constraint continue.
Existing conflicts still refuse a whole tick; no priority among two drives
prescribing incompatible movement is invented.

Within a segmented tick the stopped relation's clock contribution holds at
the stopping instant; the remaining sources follow their existing paths.
On the next tick its time source begins at that tick's GLOBAL start time,
with no increment assigned for rebasing after the stop. It attempts that
tick's new motion, so an unchanged bound admits zero again, and release or
winding permits motion on a subsequent tick without issuing a new rate
command. A source stopped earlier in a tick is not reopened later in that
same tick; this preserves the existing finite stop-segmentation rule.

That is intentionally different from an operator command: a blocked command
is retired; a declarative time drive is an ongoing model relationship with
no command to retire. No backlog or hidden restart latch is stored. Stop
diagnostics identify the stopped relation separately from actual driver IDs;
`Stop.inputs` remains the actual driver IDs and a default-empty
`Stop.time_drives` tuple identifies blocked time drives. Serialized records
omit that field when empty, so legacy command-only records retain their
current representation.

The stop-event bound counts moving command inputs plus moving time-drive
identities. Atomic staging includes all their admitted prefixes and records.
An error leaves tick, bank, tree and rings unchanged; no time drive advances
behind the failed tick. Snapshot/restore and reset need no extra physical
phase state: the tick, bank and existing command state suffice.

### 4. Make compilation and diagnostics tell the truth

Extend the existing `ClockRef` and relation resolution rather than classifying
time as an unowned plain port. The compiler gives the declared clock a
read-only source identity, a known start value and path, and keeps all
mechanical coordinates under the run's existing binder. Source/path tracking,
including ADR-124's moving-name optimization, must see its nonzero tick delta.

Validate free names in compiled laws. A free `$t` or `time` captured from
`owner.time` without naming the declared time source must fail before ticking,
naming the relation and showing `(time & other_sources).drives(...)` as the
repair. Do not silently infer an undeclared dependency. This check covers a
free symbolic clock, not arbitrary Python code that already evaluated a read
to a numeric constant; no static-analysis guarantee is claimed for that case.
Unknown non-source expression names remain unsupported too.

Keep the existing restrictions on discontinuous laws into nonbanked ports,
unsupported self-read arithmetic, unbreakable dependency cycles and `Play`
chains. A retained gate may still read its own driven coordinate in the
already-supported manner. Test those boundaries rather than implementing new
algebra to complete a table.

### 5. Publish a versioned program, with a separate viewer dependency

Time-driven programs require document version 10 (the next unused version
at the recorded base). Models without compiled time drives keep the exact
existing version-selection ladder and bytes; pose-only use of `self.time`
does not opt into version 10.

Keep `program.clock = "time"` and the existing clock expression name. Add
`program.time_drives`, only for the new capability: an ordered list mapping a
stable drive `id` to its compiled `edge` index. IDs use the internal reserved
namespace `@time:<edge-index>`, which cannot be a qualified driver
ID. Each listed edge names `time` in `needs` but never in `gives`;
`program.sources` includes those drive IDs alongside input IDs. Consumers
can then distinguish a global time read from the independent admission and
stop identity of the relation that uses it. All targets of one resolved edge
share its ID. The final schema and ordering are tested deterministically.

The list, its membership and the semantics version participate in program
identity. This preserves snapshot incompatibility checks. Time is not added
to `coordinates`, `drivers`, `intermediates` or operator controls. Existing
expressions and jump plans retain their expression language and binding
table; there is no second Python-only law interpretation.

Framework-generated conformance scenarios must carry per-tick expected bank,
time, crossings, stop provenance, command outcomes and replay/reset results.
Version 9 consumers must refuse version 10 rather than ignore the new table.
The current independent viewer advertises versions 1–9: browser support needs
its own repository-owned, pilot-authorized change consuming these fixtures.
Framework producer completion is not browser completion. Do not claim the
Astrarium unblocked end-to-end before that consumer is validated.

## Risks / Trade-offs

- **A read-only source touches several algorithms** → prove source resolution,
  rest, tick, path cuts, stops, replay and publication separately red-first;
  removing `ClockRef.check` alone is not acceptance.
- **Continuous parameter changes may surprise authors** → document incremental
  potential-law semantics and use a discrete enable in the introductory
  example. Do not advertise a general velocity solver.
- **Stop grouping could freeze unrelated mechanisms or allow inconsistent
  gearing** → test independent time relations, shared downstream trains,
  grouped targets, mixed operator/time motion and atomic conflicts.
- **Time/source handling could change ordinary runs or make idle models cost
  more** → retain a no-time-drive fast path and byte/version regression tests;
  compare representative existing commanded runs.
- **Viewer lag** → version gate, publish producer fixtures, record a separate
  consumer dependency, and withhold any browser-parity claim until replayed.
- **Historical fidelity overclaim** → the proof machine is two cubes, not an
  escapement; cadence, dimensions and source interpretation remain project work.

## Migration Plan

1. Pilot ratifies this design; validate and create the planning-only commit.
2. Implement and test in this isolated framework worktree, starting from the
   Astrarium-equivalent failure. Leave the parked project unchanged: reproduce
   its acceptance operations against a fixture using the proposed syntax.
3. Publish version-10 producer fixtures and document the viewer handoff. If
   implementation contradicts any ratified choice, return for a plan revision.
4. On proven implementation, extract the architectural decision, update the
   architecture and affected baseline specs, archive, and create commit two.
5. Integrate only on pilot authority. A separate viewer cycle and later pilot
   resumption of Astrarium are needed for project/browser validation. Rollback
   before integration means leaving this isolated branch unintegrated; no
   published package or stored project needs rewriting.

## Open Questions

The pilot ratified the choices above on 2026-09-20, including explicit
`time.drives`, per-relation stop isolation, and next-tick retry without
catch-up. Viewer implementation is a known separate dependency,
not permission granted by this framework proposal. Recheck that document
version 10 remains free before implementation/integration; a moved baseline
requires the normal reconciliation decision, not silent renumbering.
