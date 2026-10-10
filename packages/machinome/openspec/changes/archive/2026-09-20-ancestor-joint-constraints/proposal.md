## Why

Curta's closing locking disc must stop the crank against a retained result
shaft, but the two existing joints belong to different nested assemblies.
The current bound declaration cannot express that relationship without
restructuring the Studio tree or substituting a fake state coordinate.

## What Changes

- Let an assembly state an additional range constraint on an existing
  descendant's scalar joint coordinate, naming the target and reads through
  checked declaration paths.
- Preserve that joint's owner, frame, motion order, qualified identity and
  original range. Additional constraints intersect with existing limits;
  none can relax or replace another.
- Resolve each constraint's reads in the assembly that declares it, without
  banking plain ports, duplicating retained state or adding a new motion law.
- Use the existing untimed, running and clocked bound semantics and existing
  published expression vocabulary. No new solver, contact engine, tolerance,
  document version or viewer implementation is intended.
- Validate the real Curta wrong-order crank request against source geometry
  and preserve its assembly/control paths. This cycle does not certify all
  Curta interlocks or complete the operating machine.

## Capabilities

### New Capabilities

None: this extends the existing joint and simulation capabilities.

### Modified Capabilities

- `joints`: an assembly can add a scoped constraint to an existing descendant
  joint without redeclaring or moving that joint; independent limits compose
  by intersection and retain their own declaration scopes.
- `simulation`: ancestor constraints participate in existing physical stops,
  transactional command outcomes, identity, snapshot replay and compiled
  publication, preserving the behavior of models without them.

## Impact

Expected surfaces: declaration recording and checked coordinate paths,
joint-range resolution and enumeration checks, shared bound compilation,
focused tests and producer evidence, public API documentation. Reuse the
existing compiled spans and constraint sub-programs; the run executor and
viewer should need no new semantics. If either assumption fails, return the
design choice to the pilot rather than broadening the cycle silently.

This deliberately revisits ADR-113's rejected separately declared bound:
Curta demonstrates why joint placement ownership and an installed obstacle's
scope cannot always be the same. Explicit additive intersection resolves its
concern about two competing places defining allowed travel. ADR-097/098's
joint frames and replacement rules remain unchanged. ADR-133's newly merged
running-time admissions are regression obligations, not an alternative to
the missing declaration.

Origin: Curta-Type-I-3x `0db199f`; the reproduction still fails on framework
`0ce71cdea6cc4a2e7fd7e85dc68847daef3d34cc`. Repository identities, measured
contact and the supported-route comparison are in
`workflow/docs/curta-ancestor-joint-constraints.md`.

Status: pilot ratified, 2026-09-20: “Ratify—implement, validate and archive
the cycle.” This covers the complete planning artifacts and requires the
planning-only commit before implementation. Integration remains separate.
