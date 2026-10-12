## Context

Prusa3-vanilla `simulation/belts.py` and Kossel `simulation/belt.py` convert
anchor distance to idler degrees and subtract the corresponding pitch-circle
rotation from a separate pulley phase. InMoov and Open Robot Actuator have
the same inverse calculation at a drum or tensioner contact radius.

## Goals / Non-Goals

Provide the shared inverse of rolling travel, without wrapping, clamping or
new phase semantics. Preserve each consumer's radius and motion conventions.
Belt tangent geometry, fitted pulley radii and phase anchoring are not part of
this helper. No declared dimensional-token face or new dependency is added.

## Decisions

Use `rolling_angle(travel, radius)` in the existing rolling family. Its single
formula is `travel / radius * (180 / pi)`, yielding unwrapped signed degrees.
Use the same positive surface-tangent convention as rolling_travel. Do not
add sign/offset arguments: callers already own them and compose arithmetic.

Physical radius is positive; negative radius retains ordinary arithmetic.
Zero radius is undefined and plain Python numeric division raises
ZeroDivisionError. Do not introduce a numeric-only guard that behaves
differently when a radius is symbolic; deferred division retains the expression
runtime's own singular behavior. This matches the existing screw inverse.

## Risks / Trade-offs

- Floating regrouping changes final bits: compare physical values within the
  established project tolerances and retain independent reference values.
- Pulley phases are often radians: keep their explicit radians-to-degrees
  conversion separate from this travel conversion. Do not mistake radians
  arithmetic for a rolling helper candidate.
- Contact, tooth-tip and pitch radii differ: supply exactly the existing radius.
- Use project-root commands with explicit source-worktree PYTHONPATH; never
  repoint the shared editable installation. Use independent build directories
  for simultaneous model variants to avoid artifact races.

## Migration Plan

After package red/green tests, Sol agents migrate consumers on focused project
branches. Capture before/after values and symbolic builds, run affected motion
contracts using each project's established validation kernel, and inspect
representative snapshots. Record baseline failures separately from regressions.
Review, sync, archive and locally fast-forward only validated content. A focused
revert restores a project law without changing geometry. Skip a blocked helper
with evidence; never archive it as completed.
