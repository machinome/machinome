# ADR-133: Running Time Drives Retained Motion with Independent Admissions

**Status:** Accepted
**Date:** 2026-09-20
**Amends:** ADR-127's blanket refusal of clock sources in `drives`, for running clocks only
**Depends on:** ADR-105, ADR-106, ADR-107, ADR-108, ADR-110, ADR-111, ADR-121
**OpenSpec change:** `running-time-drive`
([archived record](../../../openspec/changes/archive/2026-09-20-running-time-drive/))

## Context

The parked Astrarium reconstruction at `67090d2` needs retained shaft motion
with enable, winding and finite reserve. Its two-cube diagnostic can pose a
part from `self.time`, but cannot name time as a retained-motion source.
Assigning a running joint violates exclusive run ownership; introducing an
artificial driver and a startup rate works but makes the scenario supply a
relationship that belongs in the model. These are framework findings, not
historical escapement evidence.

## Decision

The root's `time = Time.running()` is an explicit read-only `drives` source,
alone or in a source group. Factories still receive realized owners once;
returned laws receive source values in written order. The run contributes
existing continuous increments and subtracts discontinuities. It does not
reinterpret position laws as velocity callbacks. Joint ownership and ordinary
absolute `self.time` transforms are unchanged. Undeclared free symbolic time
is refused; arbitrary Python reads already reduced to constants are not
claimed detectable.

Each resolved time-source relation has its own admission identity. Grouped
targets share it; downstream gearing inherits its retained motion. A stop
clips that admission for the tick's remainder without stopping global elapsed
time or unrelated time drives. The next tick tries its own global interval,
without catch-up, local age or a restart latch. A stopped admission never
reopens in the same tick. Actual blocked commands still retire.

These admissions are not inputs or persisted coordinates: `tick * dt` is
still the clock, and existing snapshots carry all replay state. Stop records
keep real drivers in `inputs` and time-drive IDs in default-empty
`time_drives`. Time-driven downstream stop localization evaluates the original
source path through its full determining prefix; interpolating an upstream
curved law's net travel would leave coupled coordinates inconsistent.
The existing bounded search tolerance and limitations remain.

Version 10 publishes `program.time_drives`, ordered mappings from
`@time:<edge-index>` to the flattened published edge index. Those edges read
`time`; their IDs participate in source candidates and program identity, but
never in bank, driver or control tables. Documents without time drives keep
their previous versions and bytes. A separate producer corpus records actual
documents and run results; the independent viewer must consume it before
claiming support. A version-9 viewer refuses version 10.

## Consequences

The model now states autonomous retained motion without a synthetic command.
Operating history matters, while atomic ticks, snapshots and existing law
semantics remain shared. Independent admissions add source bookkeeping, and
curved upstream stop paths require prefix evaluation. Global time in a
nonlinear law continues while disabled: authors needing retained phase must
model that phase mechanically. Time provides no gravity, inertia, contact
dynamics or historical cadence.

The Python producer is implementable and testable independently, but browser
execution remains a separate repository change. Astrarium stays parked until
the pilot resumes it; this decision does not complete its reconstruction.

## Rejected alternatives

- Imperative joint assignments or tick callbacks would create a second writer
  and make pose evaluation mutate mechanical history.
- An author-created driver plus startup `Sim.rate` preserves the reported
  friction; a new `Motor` declaration repeats the existing law vocabulary.
- One globally stoppable clock would mechanically couple unrelated trains.
- Treating law values as velocities or inferring captured clock dependencies
  would change existing semantics instead of admitting an explicit source.
- Persisted local ages or catch-up travel would invent phase state the model
  never declared.
