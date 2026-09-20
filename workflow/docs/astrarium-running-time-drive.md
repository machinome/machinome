# Astrarium: elapsed time as a retained-motion source

Status: **empirical finding and ratified framework plan**, 2026-09-20. The
pilot approved implementation with “ratify, go on”. No implemented fix,
browser support or completed historical reconstruction is claimed. No external
issue was requested or opened.

## Originating evidence

Project: `projects/astrarium` in the shop's explicit catalogue, an independent
repository whose canonical root is `/mnt/data/machinome-projects/astrarium`.
Examined checkpoint: `67090d2829a4f5431e58ab7c11328ac3583774d8`.
Read `HANDOFF.md`, `docs/running-capability.md`,
`model/capability_fixture.py`, `simulation/mechanistic.py`,
`simulation/rate_probe.py` and the diagnostic tests.

The requested machine is Giovanni de' Dondi's Astrarium, with a reusable
physical model and an initial mechanistic `Time.running()` simulation. The
project is parked by explicit pilot direction. It currently contains only
planning, historical research and two nonhistorical diagnostic cubes; no
historical gears, frame or escapement have been built. Its documented six-test
baseline is three failed captured-time acceptance tests and three passed
commanded-rate comparisons. All three failures stop at the initial no-motion
assertion; they do not separately demonstrate winding or stop bugs.

The precise finding is:

| Pattern | Recorded result |
| --- | --- |
| Plain-part `rotate(self.time, axis)` | Absolute pose expression works; not retained joint motion |
| Assign `self.time` to a running joint | `DoublyBound`, consistent with exclusive run ownership |
| Imperatively time-fed `SignalPort` driving a joint | `UnsupportedLaw`, not an admitted source |
| Clock captured in the diagnostic law factory | Fixture constructs but does not advance the joint |
| Explicit `time.drives(shaft.turn)` | Intentional `TypeError` refusal |
| Declared dummy driver advanced with `Sim.rate` | Comparison retains angle through stopping/winding and replays |

These observations do not establish that all autonomous mechanisms are
impossible, that `self.time` is unreadable, or that a running simulation is
a force/inertia/contact solver. The direct pose probes establish Python-side
expression behavior, not inspected browser output.

## Framework cycle identity

- Lane: standalone framework proposal; not sprint-scoped.
- Shop root: `/home/asa/devel/machinome-studio`.
- Primary framework: `/home/asa/devel/machinome-studio/machinome`, branch
  `main`, clean when the bench was opened.
- Base: `9fb5127fad62e6c66067b34e7d02dd389471fa2d`.
- Opened through the shop's `scripts/dev-env running-time-drive setup`.
- Branch: `running-time-drive`.
- Worktree: `/home/asa/devel/machinome-studio/machinome/WTs/running-time-drive`.
- Intended integration target: framework `main`, only with explicit authority
  and reverified base. No integration, push or publication is authorized now.
- Change: [running-time-drive](../../openspec/changes/running-time-drive/proposal.md).
- Current state at the planning commit: ratified planning files only;
  implementation follows the clean planning/ancestry gate.

Existing unrelated worktrees, including stale registry paths outside this
workspace, were preserved. Neither the framework primary checkout nor the
Astrarium or viewer repository was edited for this proposal.

## Source investigation at the recorded base

This is new framework-side evidence, not an internal explanation retroactively
claimed by the project's earlier handoff:

- `machinome/motion/ports.py`, `Time`: reading time already follows the bound
  root time; its declaration has relation/group entry points.
- `machinome/motion/couplings.py`, `ClockRef.check`: unconditionally refuses
  the clock at either end of `drives`. Ownership validation is currently
  written for elapsed-clock committing relations.
- `machinome/simulation/run.py`, `Run.integrate`: admissions come only from
  active commands on declared drivers. The bank carries inputs and joints;
  elapsed time is bound after tick commit, not admitted as a source path.
- `machinome/simulation/program.py`, `_relation_edge` and `_law_graphs`:
  running expressions are compiled over declared relation sources. A free
  captured time is not a declared moving input. A source fix therefore has
  to address compilation and path evaluation, not only syntax.
- Stop grouping currently traces actual input IDs and retires their commands.
  A global stoppable pseudo-input called `time` would couple unrelated trains
  and would confuse simulation time with physical travel.

Relevant contracts inspected: framework architecture (relations, time bases,
running simulation, publication and invariants); coupling, simulation and
export baseline requirements; ADRs 104–108, 110–111, 124, 127 and the current
Play boundary. Context7 had no Machinome entry; the checked-out source and
accepted local records are the evidence, not guessed public API documentation.

## Reproduction performed while proposing

From the framework bench, with `PYTHONPATH=.` and the workspace Python,
imported `AssemblyNode`, `CadQueryNode`, `Revolute` and `Time`; declared a
shaft leaf with `turn = Revolute(axis=(0, 0, 1))`; then defined a root with:

```python
time = Time.running()
shaft = Shaft()
time.drives(shaft.turn, ratio=6)
```

Class definition raised `TypeError`: “the clock 'time' cannot be the driver
end of a relation”, followed by guidance to use an elapsed-clock commitment
or a `self.time` pose. The imported `machinome.__file__` was confirmed inside
this bench, not the primary checkout. This was a diagnostic command, not an
implementation test or a passing acceptance result. No code files were added.
The project's reported six-test result is prior project evidence, not a new
suite run in this proposal-only cycle.

## Recommendation and limits

Admit the running root's time as an explicit read-only `.drives` source;
integrate existing law changes along each elapsed interval; retain joints in
the existing bank. A relation is a persistent drive but not a command:
mechanical stopping discards unadmitted motion and retries only a new tick's
interval. Distinguish independent time-source relations for physical stops;
never halt the global clock. Leave absolute `self.time` posing and exclusive
joint binding unchanged.

The [design](../../openspec/changes/running-time-drive/design.md) records
alternatives, compatibility changes, proposed publication fields and risks;
the delta specs and tasks hold the testable proposal. No ADR is accepted
before implementation confirms the ratified choice.

The independent viewer's current README/CHANGELOG advertise unreleased source
API 22 reading document versions 1–9. This proposal requires version 10 for
actual time-driven programs, plus framework-generated conformance fixtures.
The consumer needs a separate authorized viewer cycle, and Astrarium needs a
later explicit resumption and project acceptance. Neither is silently included
in framework producer completion. Cadence, dimensions and historical accuracy
remain unresolved project responsibilities.

## Planning validation

`openspec status --change running-time-drive` reports all four planning
artifacts present. `openspec validate running-time-drive --strict` passes.
This is proposal-shape validation, not implementation completion or simulation
proof. The pilot separately ratified the plan with “ratify, go on”. Every
implementation task remains unchecked at the planning commit.
