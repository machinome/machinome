## Why

The historical Astrarium reconstruction can read `self.time` under
`Time.running()`, but cannot declare elapsed seconds as a source of retained
joint motion: direct assignment conflicts with the run's ownership, a
time-fed plain port is not an admitted input, and `time.drives(...)` is
explicitly refused. Its working comparison requires an artificial driver
and a `Sim.rate` command; the maker needs the clock to start from its model's
declared operating state without that extra command protocol.

## What Changes

- Admit the root's declared `time = Time.running()` as a read-only source
  of ordinary `.drives(...)`, alone or in a source group. Reuse the existing
  affine and law-factory syntax; introduce no motor class or setup callback.
- Supply elapsed seconds along each tick's path to those relations. Retain
  joints by integrating the existing law's continuous changes, not by
  assigning an absolute time-derived pose.
- Preserve held positions across disabling, physical stops and resumption;
  discard unadmitted motion rather than accumulating catch-up travel. Each
  time-source relation is an independent drive unless the declared mechanism
  connects it to another. Simulation time itself is never mechanically stopped.
- Keep `self.time` pose expressions, exclusive run ownership, commanded
  drivers, untimed inspection and the other time bases unchanged. Refuse
  undeclared free time in a running law with an actionable diagnostic instead
  of allowing an inert or partially compiled law.
- Extend the framework's published-program contract and producer conformance
  fixtures for time-driven motion. **Consumer compatibility boundary:** only
  documents using the new semantics require version 10; older consumers must
  refuse them. An independently authorized viewer change is required for
  browser execution; no viewer code belongs in this framework cycle.

## Capabilities

### New Capabilities

None; this extends the existing relation, running-simulation and export
capabilities.

### Modified Capabilities

- `couplings`: allow a running clock on the source side of `drives`, preserving
  elapsed-clock commitment rules and all prohibitions on writing the clock.
- `simulation`: advance declared time-driven relations without commands,
  preserve retained state and physical stops, and diagnose hidden time reads.
- `export`: publish time-drive identity and semantics, select the required
  document version, and provide framework-generated conformance evidence.

## Impact

Expected implementation surfaces: `machinome/motion/ports.py` and
`couplings.py`, `machinome/simulation/program.py` and `run.py`, document
publication, focused tests, producer corpus, and public documentation.
Accepted decisions 104–108, 110–111, 124 and 127 are relevant: this deliberately
relaxes ADR-127's refusal of a running clock as a drive source, but preserves
its elapsed-clock behavior and ADR-105's exclusive joint ownership. It is not
a gravity, inertia, escapement or contact solver and does not establish any
historical Astrarium cadence.

Originating evidence: `projects/astrarium` at `67090d2`, especially
`HANDOFF.md`, `docs/running-capability.md`, and its six diagnostic tests.
Framework investigation and repository identities are recorded in
`workflow/docs/astrarium-running-time-drive.md`. The project remains parked;
this proposal authorizes neither its reconstruction nor a viewer mutation.

Status: **pilot ratified**, 2026-09-20: “ratify, go on”. Implementation is
authorized after the validated planning commit and clean ancestry gate;
integration, viewer changes and project resumption remain separate.
