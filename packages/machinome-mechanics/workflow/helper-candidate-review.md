# Remaining candidate review, 2026-09-20

This is empirical pre-proposal evidence, not a baseline specification. The
pilot authorized skipping blocked helpers; a shortlist is not evidence by itself.
Sol inventory inspected runtime Python throughout projects (excluding tests,
docs/OpenSpec, scripts, build trees, vendored code and virtual environments),
and the parent inspected the named production seams below. No CAD was run for
this inventory, no project was changed, and no public helper was added here.

## differential_angles: skip before proposal

Thor is a genuine consumer: `simulation/art4.py:150-154` computes the common
frame pair wrist +/- CROWN_RATIO*tool, used by motor and belt bindings at
161-176. Its crown/pinion ratio is 30/15 (`art56.py:36-42`).

The proposed second consumer, Dragon R1, does not repeat this computational
law. `simulation/drivetrain.py:175-205` places side gears inside a parent
carrier rotating about -X; both side gears receive the same local `difference`
coordinate. The left gear is physically mirrored by a 180-degree X transform.
At 212-233, carrier and difference remain separate coordinates at separate
hierarchy levels. `simulation/test_drivetrain.py:142-157` independently expects
the same local value on both sides, with opposite physical motion supplied by
the mirrored frames. The parent inspected these source and test sections.

Calling a common-frame sum/difference helper there would require adding the
carrier, then subtracting it again for the child-local coordinate and undoing
the mirrored sign, returning the same current difference. This adds work
without abstracting production mechanics. Flattening those transforms instead
changes hierarchy, axes and serialization, beyond an equivalent refactor.

A broader runtime search for paired sums/differences and differential/carrier/
average terms found no useful second independent consumer; other hits were
ordinary vectors, phase arithmetic or single-axis gearing. Therefore this
helper is struck before proposal for this campaign. No unfinished cycle is
archived, and Thor/Dragon remain unchanged for this candidate. Revisit only
when a second project needs the common-frame pair directly.

## indexed_advance: qualified after a broader review

The first pair-only inventory judged plain floor*increment+partial too thin.
Broader source evidence found the same mechanical accumulation in four real
repositories:

- Pascaline-module `simulation/carry.py:12-23`: origin-shifted turns, continuous
  segmented cam stroke and accumulated carry. The origin is 325 degrees;
  the current throw is 36 degrees (`layout.py:113-125`).
- Deepseek Leonardo-hydraulic-sawmill `simulation/kinematics.py:25-28,87-97`:
  completed turns plus a geometry-derived partial stroke; the four-revolution
  reset remains outside the accumulated result.
- 3DPrintedClocks `simulation/shared/geneva.py:30-44`: shifted turn count and
  clamped half-cosine partial motion, accumulated by the slot pitch.
- Curta-Type-I-3x `simulation/clocked_laws.py:108-111`: completed-turn rack
  increments plus a limited within-turn reach.

Parent inspected all four. A second independent Sol review evaluated a narrow
higher-order candidate against the real Pascaline and sawmill laws:
`n=floor((angle-origin)/360); phase=angle-360*n;
result=n*increment+stroke(phase)`. Existing numeric results matched exactly
at signed turns, seams, partial strokes and reset-region inputs; an actual
Solid2 argument and the sawmill callback produced a deferred graph.

The useful shared boundary is the completed-turn/phase accounting, not a
generic ratchet, window, cam, or reset model. A pure caller-authored stroke
can retain each project's irreducibly different within-turn geometry, while
the helper owns that repeated accounting. The phase supplied to the callback
must be explicitly documented as [origin,origin+360), not phase since origin.
Seam continuity is caller-owned and requires the upper left limit to equal
increment plus the lower value. A constant-zero callback with nonzero increment
is a valid discontinuous counterexample; continuity cannot be promised.

This finding supports a later single-helper cycle, not implementation authority
independent of its proposal and empirical consumer gates. No arbitrary period,
reset flags, callback branching support or stateful callbacks are needed.
