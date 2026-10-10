# Curta clearing from the retained wheel angle

**Status:** pre-spec requirement and implementation handoff, requested by the
pilot on 2026-09-15. This records a project need and a reproduced limitation;
it does not ratify an API, authorize a solver redesign, or claim that the
tested expression is the only possible representation.

**Taken up** as OpenSpec change `read-the-driven-coordinate` (ADR-121) on
2026-09-15: the refused sentence below is a READ of the driven end, integrated
piece by piece from the retained value. The project-side migration (item 9)
and the viewer's execution of a version 6 document (item 8) remain open, each
in its own repository.

## Required outcome

A maker sweeps the Curta's clearing ring. Each number wheel turns only while
the passing rack engages its teeth, reaches its missing-tooth zero gap, then
holds while the ring continues. Its response must follow the wheel's retained
position. Releasing the ring preserves partial clearing; continuing the sweep
continues from there. Passing an already-zero wheel does not turn it again.

The maker handles the carriage and ring independently. Clearing does not lift
the carriage, finish a partial sweep, seat it, or reset an untouched register.
The two permitted sweep directions and the physical intervals that reach the
result and counter banks must be represented. Ordinary operation uses the
same run in Python and the browser; no page-owned register state or reset
callback supplies the answer.

## Originating project and evidence

The independent repository is
`projects/Calculators/Curta-Type-I-3x`, branch `direct-operation`, checkpoint
`b285393`. Paths below are relative to that repository:

- `simulation/docs/direct-operation-2026-09-15.md`: approved whole-machine
  interaction inventory and acceptance obligations.
- `openspec/changes/simulate-the-curta/specs/curta-operation/spec.md`:
  retained operation, selective clearing, partial release and replay outcomes.
- `simulation/tools/direct_operation_probe.py`: executable public-API
  diagnostic, with a working lift/turn control as a positive check.
- `simulation/docs/direct-operation-prerequisites-2026-09-15.md`: measured
  framework/viewer identities and the diagnostic result.
- `simulation/cycle.py:cleared_position`: the existing *pose* law, which
  receives a starting position and one normalized clearing sweep. It is
  reference geometry/timing, not an implementation of arbitrary repeated
  clearing under retained state.
- `simulation/clearing.py`, `simulation/test_clearing.py`,
  `simulation/clearing_contact.py`, `simulation/test_clearing_contact.py`,
  `simulation/docs/measurements.md`: source-backed racks, their fitted groove,
  missing-tooth zero and engagement evidence.

At diagnosis, framework main was
`8d29cf5e4b289da79e65bd09e3d0c13f5721f305`. From the project root:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH="$PWD" \
  ../../../.venv/bin/python -m simulation.tools.direct_operation_probe
```

The independent crank lift and turn complete at 9 mm and -360 degrees. The
clearing fixture fails during declaration:

```text
TypeError: wheel.rotation is named as both a source and a driven end of one relation:
a coordinate is a source or a driven end of one relation, not both.
```

The attempted relation is `(rack & wheel.rotation).drives(wheel.rotation,
law=missing_tooth)`. The diagnostic gate is intentionally schematic: it asks
whether engagement may depend on the retained output coordinate at all. It
does not establish actual Curta tooth geometry, engagement thresholds,
direction conventions, or a correct numerical integration rule. In particular,
simply deleting the declaration refusal is not an implementation.

## Architectural question to resolve

Find and document a supported representation of this state-dependent
disengagement. First establish whether the current public model can express
it without additional state disguised as a part, duplicated wheel coordinates,
or per-tick project mutation. If it can, prove that representation and return
the project-side example. If it cannot, propose the smallest coherent
framework change under the shop's normal workflow.

Relevant accepted boundaries are:

- ADR-105: the run owns driver and joint coordinates; plain ports are derived
  values, the author declares no independent memory, and inspecting a model
  advances nothing.
- ADR-106: a law is compiled in the direction solved at rest, and running
  motion integrates its continuous contribution.
- ADR-107: branch jumps themselves contribute no movement.
- ADR-108 and ADR-109/113: ranges stop pushing inputs; a bound can read state,
  but a stop and disengagement have different outcomes.
- ADR-110: Python and the viewer execute one published mechanical program.
- `docs/architecture.md`, sections Kinematics and Simulation, and baseline
  `openspec/specs/couplings/spec.md` and `simulation/spec.md`.

These remain authoritative. A range stopping the ring when one wheel reaches
zero fails this requirement: the gap frees the ring to continue. Recomputing
the wheel from total rack travel loses its independent history. Freezing an
engagement decision for a whole large tick can overshoot the gap. Any new
state-read semantics must say when the read is evaluated, how a within-tick
engagement change is located, and how initialization and ordinary posing work;
these are design questions for the proposal, not decisions made here.

## Acceptance evidence owed

Start with a small geometry-free fixture and independent expected travel,
then validate the source-backed Curta interface. At minimum:

1. From each digit 0–9, a sufficient rack sweep reaches the zero gap and the
   ring completes its remaining travel. Zero at the start stays zero.
2. Repeat the same physical clearing sweep after a completed clear. The
   already-zero wheel stays put; it does not repeat its former contribution.
3. Stop part way, inspect repeatedly, save/restore, and resume. The retained
   angle and admitted ring travel replay consistently without a new starting
   register supplied by the caller.
4. Exercise both mechanically permitted directions, changes of direction,
   entry/exit of contact and clearing followed by another crank operation.
   Expected direction and zero come from the real interface, not the rejected
   diagnostic's arbitrary 359-degree comparison.
5. Clear several wheels with different initial digits from one ring input.
   Each disengages independently; an untouched wheel and the unswept register
   remain unchanged. A real obstruction still blocks according to its own
   physical constraint.
6. Compare a coarse tick crossing disengagement with finer partitions and
   partial commands, within a stated accuracy contract. Prove that crossing
   the gap does not create a jump, extra wheel travel, or hidden command backlog.
7. Preserve single command ownership, transactional refusal, snapshot identity,
   reset semantics and bounded recording. Regression-test ordinary affine
   laws, externally gated clutches and range stops.
8. Export through the actual producer and replay that document through the
   independent viewer's running engine. Record exact tested content commits;
   if consumer changes are needed, they belong in a separate viewer change.
9. Return to the real project, verify clearing contact at sampled run states,
   and exercise actual controls. Retain its previously recorded whole-machine
   geometry failures; this feature does not waive them or finish its OpenSpec
   change.

Use the project's existing resource guard for heavy CAD runs: one job at a
time, one BLAS/OpenMP thread, and the 8 GiB address-space limit documented in
`simulation/docs/pause-report-2026-09-11.md`. The small declaration diagnostic
requires no CAD build.

## Handoff boundary

The pilot requested this document so another agent can take up the requirement;
the current project task proceeds with markings. There is no selected public
API spelling, ratified OpenSpec cycle, framework implementation, viewer change,
or permission to publish attached to this note. Return a supported example,
the accepted contract and regression evidence that unblock the project's
retained clearing implementation.
