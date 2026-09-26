# Curta periodic lockout: first contact loses its pushing input

Status: implemented, validated and archived on 2026-09-20; not integrated.
Date: 2026-09-20.

Origin: `Calculators/Curta-Type-I-3x`, branch `direct-operation`, checkpoint
`c76f230836ce3a91cc960564a1e1f0b3a7e9232b`. The project-owned record is
`simulation/docs/periodic-lockout-stop-2026-09-20.md`; executable reproductions
are `simulation/periodic_lockout.py` and `simulation/test_periodic_lockout.py`.
Upstream CAD is unchanged. The separately verified ones-lockout fit and
experimental measured contact profile are not the cause of this run failure.

Framework examined: clean main
`8d2bd71171be81f13ba5dd492851ed8b3a9ababb`. Standalone investigation worktree:
`machinome/WTs/periodic-lockout-first-contact`, branch of the same name.

## Observation

On the complete source-backed bell and result stack, prepare digit 3, height
0, crank 120°, then withdraw digit to zero. The retained ones shaft stands at
189.60000000000002°. The diagnostic lower bound on `bell.turn` reads the
actual co-rotating drum and, in that certified shaft neighbourhood, evaluates
`-360*floor((-drum-10.8)/360)-125.22`.

The project measured 3/4 cases passing: fixed local stop with immediate target
840°, periodic stop with immediate target 150°, and periodic stop with timed
target 840°. Immediate periodic target 840° raises `StopInvariantError`.

A read-only process-local wrapper around `Run._constraint_group` reproduced
the error on the cycle base, without changing the method's result or any
source file. For the sole moving candidate `crank_angle`, admission 720°,
constraint levels at fractions of the request were:

| Fraction | Level (positive means outside) |
| --- | --- |
| 0 | -5.219999999999999 |
| .005 | -1.6200000000000045 |
| .01 | 1.980000000000004 |
| 1 | -5.220000000000027 |

The selected group was `[]`. `_searched_constraint` finds the interior
crossing; `_constraint_group` compares only the candidate's levels at 0 and
1. Their net difference is nonpositive, so the only pushing input disappears.
The invariant correctly refuses the entire tick rather than committing it.

## Proposed direction and boundary

Preserve the contact's inside/outside localization bracket and identify
pushing candidates there using the same sub-program arithmetic. Do not turn
off the invariant, cap user travel, secretly split requests, or special-case
the Curta. Own-coordinate freezing and existing bounded-search limitations
remain. ADR-113 explicitly chose a net whole-stretch pushing test: changing
that choice requires ratification, an implementation-proven decision record
and cross-runtime conformance evidence, not a silent repair.

The proposal is `periodic-lockout-first-contact`. This note is evidence and
intent, not authority to implement, integrate, or modify the independent
viewer. Compound effects requiring several inputs together, arbitrary narrow
unsampled contacts, and broader running-performance work remain outside scope.

## Resolution

The pilot ratified the complete plan before planning commit `c2023b1`.
The implemented private contact bracket preserves the inside commit fraction
and compares each admission alone across the inside/outside sides. No model
API, geometry, document version or tolerance changed. ADR-135 amends ADR-113's
old endpoint-only attribution choice.

Validation: 3,488 framework tests and 2,011 subtests pass (4 skips); an expanded
233-test focused matrix also passes. The actual Curta reproduction passes all
four cases, and its broader measured-lockout suite passes all six tests,
including five flats, later revolutions, withdrawal phases, replay, relief,
retry and legal 1080° travel. Seven actual long-request stop poses have zero
complete-part overlap in both kernels, and .2° posed overtravel produces
positive overlap in every case. Snapshots were rendered and inspected.

The [archived evidence](../../openspec/changes/archive/2026-09-20-periodic-lockout-first-contact/evidence.md)
records commands, content identities, red-first and mutation checks, complete
geometry results, and the separate viewer handoff. Main remains at the cycle
base pending explicit integration authority. The production Curta restraint
and upstream CAD are unchanged; operating Curta is not declared complete.
