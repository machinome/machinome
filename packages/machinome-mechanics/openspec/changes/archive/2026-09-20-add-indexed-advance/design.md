## Context

Pascaline's current corrected 40-tooth carry has one segment, 325..359 degrees,
with a 36-degree throw and zero lead; historical seven-segment/114.9-degree
variants are not its current source. Its carried-column and trailing-idler
laws need accumulated turns. The sawmill combines a 7.5-degree tooth step
with nonlinear hook contact; its smooth four-turn reset is a separate policy.
Both retain project-owned partial-stroke geometry. Clocks' Geneva and Curta's
clocked rack confirm the same repeated accounting, without expanding this
cycle's migration scope. Existing extraction decisions keep pure arithmetic
in this independent package and relation construction in projects.

## Goals / Non-Goals

Goals: remove repeated floor/phase/turn accumulation in two real consumers,
preserve signed turns and actual deferred motion, and document a narrow pure
callback contract. Non-goals: stroke synthesis, arbitrary periods, reset or
continuity enforcement, stateful iteration, geometry certification, registry,
or framework mutations.

## Decisions

- New indexing module with one function. Compute
  `n=floor((angle-phase_origin)/360); phase=angle-360*n;`
  `return n*increment+stroke(phase)` using machinome.math.floor.
  Fixed degree period matches all named uses; a general period adds no needed
  mechanical behavior.
- The callback gets absolute phase in [origin,origin+360), NOT displacement
  from origin. Pascaline can therefore keep its existing segment coordinates.
  A zero-based callback would force source coordinate rewrites.
- Invoke stroke once, without sampling/validation. It must be pure and use
  supported expression arithmetic for deferred inputs; arbitrary Python
  branches/math/state are not made symbolic by the helper. Callback exceptions
  propagate. No coercion or hidden numeric/symbolic dispatch.
- Increment and stroke share any caller displacement unit/sign/zero. Angle
  and origin are degrees. Continuity is conditional on
  stroke(origin+360 from below)=increment+stroke(origin); no continuity claim
  is made for arbitrary callbacks. Return values remain unwrapped.
- Keep Pascaline's wrapper and local segment sum. Keep sawmill's reset outside
  the helper and rev_phase for pawl lift. Do not alter geometry or source poses.

## Risks / Trade-offs

- Origin misunderstood as callback-relative phase → explicit examples and
  shifted-origin/negative-turn tests, current Pascaline poses as independent oracle.
- Generic callback overclaim → document pure supported arithmetic only and
  test actual Solid2 expressions at the changed relation boundary.
- Continuity asserted without proof → test both continuous mechanical ramps
  and a deliberately discontinuous zero-stroke/nonzero-step counterexample.
- CAD memory or inherited failures → serialize process-tree-capped 768 MiB,
  swap0, threads1 gates; never increase cap or call partial suites complete.
  Build and fresh inspected images complement independent law/pose probes.

## Migration Plan

Commit planning, observe missing-helper red, implement package with full unit,
documentation and distribution checks. Sol agents own distinct consumer
branches; parent reviews evidence and repeats actual native-law checks.
Sync/compare baseline, archive, commit and guarded-local-merge only after gates.
Separate consumers can be reverted independently; no push or publication.

## Open Questions

None blocking. If either named consumer cannot preserve mechanics, document
the finding and leave this cycle unfinished under the pilot's skip authority.
