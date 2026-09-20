## ADDED Requirements

### Requirement: Indexed advance from a within-turn stroke

`indexed_advance(angle, increment, stroke, phase_origin=0)` SHALL return
`n*increment + stroke(angle-360*n)`, where
`n=floor((angle-phase_origin)/360)`. The helper SHALL be exported flat and
from indexing. Angle and origin SHALL be degrees; finite signed input SHALL
retain completed negative/positive turns without wrapping the output.
Increment and stroke output SHALL share the caller's displacement unit and
positive direction. Mounting signs and output reference SHALL remain caller-owned.

The pure caller-authored stroke SHALL be invoked exactly once with the
absolute within-turn phase in [phase_origin,phase_origin+360), not phase
measured from origin. Numeric and supported deferred operands SHALL use the
same arithmetic; for deferred use the callback SHALL itself support expression
arithmetic. No general Python branching, stateful callback evaluation,
stroke fitting, arbitrary period, reset policy or geometry certification
SHALL be provided. Callback errors SHALL propagate.

The helper SHALL NOT enforce or promise continuity. A continuous seam SHALL
require the caller's upper one-sided stroke limit to equal increment plus
the stroke at phase_origin. Zero/negative increments and arbitrary stroke
offsets SHALL retain arithmetic behavior without automatic normalization.

#### Scenario: One tooth accumulates per input turn

- **WHEN** increment=7.5, origin=0 and stroke(p)=7.5*p/360
- **THEN** inputs -720,-90,0,180,360,810 give -15,-1.875,0,3.75,7.5,16.875
  within floating tolerance

#### Scenario: Pascaline preserves its shifted carry window

- **WHEN** origin=325, increment=36 and stroke(p)=36*clamp01((p-325)/34)
- **THEN** inputs 0,324,325,342,359,360,685,719 give 0,0,0,18,36,36,36,72
- **AND** the callback's phase remains in [325,685), preserving segment coordinates

#### Scenario: A stroke is invoked once without hidden continuity correction

- **WHEN** a constant-zero stroke and increment=10 are used at default origin
- **THEN** inputs 359 and 360 return 0 and 10 respectively
- **AND** each call invokes the stroke exactly once

#### Scenario: Project reset remains separate

- **WHEN** the sawmill supplies its existing hook-derived partial stroke
- **THEN** completed tooth steps and partial motion preserve its prior law
- **AND** its four-turn smooth reset remains an external multiplication

#### Scenario: Deferred inputs preserve turn accounting

- **WHEN** supported deferred angle, increment or origin and a compatible pure
  callback are evaluated at representative signed turns and seam neighborhoods
- **THEN** results agree with independent numeric turn/stroke accounting

#### Scenario: Callback failure is not hidden

- **WHEN** the caller's stroke raises an exception
- **THEN** that exception propagates rather than substituting zero advance
