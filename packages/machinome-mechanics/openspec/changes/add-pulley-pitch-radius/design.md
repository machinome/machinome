## Context

Thor simulation/flexibles.py derives GT2 radius; its hardware.GT2Pulley
also derives a tooth-tip surface by subtracting an offset. Actuator
simulation/layout.py derives the 10/30-tooth AT3 radii. Printer timing
modules derive a pitch radius using the fitted loop period before subtracting
their PITCH_LINE allowance. These are existing consumers, not hypothetical ones.

## Goals / Non-Goals

Provide the circumference identity once. Do not fit belts, generate teeth,
choose a nominal pitch, round tooth counts, alter contact surfaces or repair
unrelated project errors (including Kossel's anchor-axis projection).

## Decisions

`pulley_pitch_radius(teeth, pitch)` returns `teeth * pitch / (2*pi)` in a
new belts family, also flat-exported. A length independent of coordinate frame
has no angle zero or rotational sign. Its physical inputs are positive pitch
and positive integral tooth count. It does not enforce that domain: zero,
negative and fractional inputs preserve ordinary arithmetic and symbolic
expressions use the same definition. A validation guard would break the
existing compositional contract without a project need.

Pitch means linear distance along the pitch line, not angular pitch or
tooth-tip circumference. Caller-owned offsets remain outside this helper.
Thor's declared Count usage must be inspected separately: use a resolved
value if needed, and preserve parameter dependence, not only the default.
No new dimensional-token guarantee is made.

## Risks / Trade-offs

- Surface versus pitch radius confusion → compare both radii and keep offsets.
- Reordered arithmetic → independent circumference and old-value tolerances.
- CAD checks can be expensive or have known failures → run established
  affected contracts, baseline any new failure, inspect representative pixels
  and disclose structural limits without treating a green suite as certification.

## Migration Plan

Prove tests red, implement, then Sol agents migrate Thor and Actuator plus
other natural belt consumers on project-owned focused branches. Record helper
source hash, exact consumer commits and dependency drift. Review evidence, sync
and archive before local fast-forward integration; only then open the next
helper. A focused project revert restores old arithmetic. Skip unresolved
helper blockers without archiving incomplete work; no push or publication.
