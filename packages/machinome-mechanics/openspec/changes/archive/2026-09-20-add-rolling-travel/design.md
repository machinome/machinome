## Context

Dragon R1 computes `pi * pitch_radius / 180` for rack travel per degree.
Thor's art2/art4 belt laws compute the same circumference fraction. Both have
existing measured motion contracts and preserve direction in their own frames.

## Goals / Non-Goals

Provide one pure arithmetic conversion, documented and empirically substituted
in both consumers. Do not introduce motion objects, geometry, clamping, contact
simulation, radius fitting or an inverse helper in this cycle.

## Decisions

Use `rolling_travel(angle, radius)` in `rolling.py`, re-exported flat. Compute
`angle * radius * (pi / 180)`; pi is a numeric constant, so ordinary arithmetic
retains deferred expression support. Return signed displacement from angle zero,
unwrapped. Positive travel follows the positively rotating surface's tangent;
the caller maps this direction to its axis. Radius is the pitch/contact radius.
Document physical positive radii but preserve arithmetic for zero/negative
values, consistent with screw_travel. No dimensional class-body promise.

Distribution review found the initial installation contract and smoke checker
fixed the export count at twelve. Preserve every original export and check the
installed API against the source's declared export list so this helper and
subsequent additions are included. This changes no package dependency.

## Risks / Trade-offs

- Direction conventions differ: retain each existing project sign and datum.
- Rounding order can change final bits: compare geometric values with existing
  tolerances, never bitwise geometry hashes as a substitute for motion evidence.
- Consumer environment must import this worktree, not the unmerged primary:
  use a per-command PYTHONPATH; do not change shared editable installations.

## Migration Plan

After package tests pass, Sol agents work on focused project branches, record
before/after sweeps, run relevant project contracts and inspect snapshots, then
commit their changes locally. Independent project repos own their migration
records; this OpenSpec change records their exact commits and issues. The parent
reviews evidence and integrates only validated commits. Reversion is a focused
Git revert; original source geometry remains untouched.
