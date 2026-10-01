## Why

A consumer recording a take of a clocked machine through `Sim` cannot ask
the simulation which machine it is running. The export's manifest carries
`clocked.identity`, and the viewer's `restore({identity, bank})` refuses
another machine's bank by that name, but the framework's `Sim` keeps the
same string only on the private `sim._clocked.identity`.

The finding comes from Videomaker's curta-video campaign, which filmed the
clocked Curta (`projects/Calculators/Curta-Type-I-3x`, `ClockedCurta`,
document version 8) by recording a take through the public `Sim` and posing
the viewer from the recorded banks. Videomaker's archived change
`2026-10-01-declare-a-take`, `evidence.md`, finding 2: with no public
identity, its take check compares the recorded bank's ids with the export's
drivers and states instead. A law changed under the same ids passes that
check, and is caught only later, where the viewer restores the bank with the
document's identity. Filed in `workflow/warts.md` as "Three findings from
filming the clocked Curta (1 October 2026)", finding 2. The plan that cuts
this change is `workflow/ongoing/curta-film-findings/plan.md`.

What the originating project does with the result: Videomaker reads
`Sim(model).identity` while it records a take and compares it with the
`clocked.identity` of the export the film poses. A take recorded over a
machine that differs from the export's is then refused when it is recorded,
not when the viewer restores it. That comparison is one line in Videomaker's
`_record`, made in a later Videomaker cycle.

## What Changes

- **`Sim.identity`, read-only.** Under a clocked root it is the compiled
  clocked machine's identity: the same string the export, the build and the
  web snapshot write as `clocked.identity` for the same model. Those
  producers obtain their machine by constructing a `Sim`, so the two values
  are equal by construction, not because two implementations agree.
  It is a property of the machine, not of the bank. A `Sim` opened with
  `state=`, moved by requests, or restored still reports the same identity.
- **Refused by name on a `Sim` that is not clocked.** Under an untimed or a
  running root, reading `sim.identity` raises `TypeError` naming
  `identity` and the model, in the shape `_running` already uses for the
  members a clocked or untimed `Sim` does not have. Under a running root the
  message points at `sim.program.identity`, the public member that already
  carries a running program's identity.
- **Nothing else moves.** The clocked snapshot keeps its shape, the document
  keeps its bytes and its version, the viewer is not touched, and nothing is
  added to the cadence surface.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `simulation`: one ADDED requirement, "A clocked simulation publishes its
  machine's identity", stating `Sim.identity`, its equality with the
  exported `clocked.identity`, its independence of the bank, and its refusal
  on a `Sim` that is not clocked.

## Impact

**Framework code.** `machinome/simulation/sim.py`: the `identity` property
and one private refusal helper beside `_not_clocked` and `_running`. No
other module changes.

**Tests.** A new `tests/test_clocked_identity.py`, built on the suite's
clocked fixture `tests/clocked_project/counter.py`. It checks that the
identity equals the exported manifest's, that it does not depend on the
bank, that it differs between machines, and that it is refused on an untimed
and on a running root, with each refusal's names asserted.

**Docs.** `docs/reference/api.rst`, which lists `Sim`'s members, gains
`identity` and one sentence in its "Clocked simulation" section. The
changelog entry goes under `Unreleased`. `docs/architecture.md` gains one
clause in the clocked mode's synthesis.

**Caller.** `Sim(ClockedCurta()).identity` is run from the Curta's real path
and compared with `export/clocked_curta/manifest.json`. Nothing is written
into the project.

**Downstream, not in this change.** The studio's
`shop-skills/machinome-api/SKILL.md` gains the member, as the orchestrator's
edit after the merge. Videomaker's use of it is a Videomaker cycle.
