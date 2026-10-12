# Mixed-contact acceptance — 2026-09-21

## Scope and authority

Base `e82b5214e4460e606cb86608f042e7a6fcefa49d`; planning-only commit
`f77dab4`. The pilot approved the explained direction correction, its
following-contact precision extension, validation and local integration.
The framework owns its separate cycle, base `e63700e`, planning `5673d1f`.
No API/version, tolerance, geometry, package boundary, push or release change.

## Red proof and implementation

The actual full Curta export on unmodified main fails the input-9/single-360°
request in the worker with `LandingInvariantError`, atomically retaining
its snapshot. Export SHA-256:
`92719ac99b1188cc50cdc100683946c0235c5a3116be7a2993dff1f15d75c7db`.
Original bundle:
`8acaf5989e5fa99bb5f3314c2080016603893ca8e665569a4d707ff24f8de751`.

Before runtime edits, the five added producer scenarios yield four real
failures (both overtaking directions, restraint observation, following-contact
chatter) and one passing stationary control. A fifth test failure was the
fixture census still expecting 23 scenarios; the generator now emits 28.

The running walk now establishes the local near-to-far orientation for a
moving threshold, preserving its ordinal landing and named refusal. The
separate `contact-proof.ts` certifies exact constant relative level with
BigInt rationals over binary inputs and the existing shared expression DAG.
Continuous selection crossings partition into individually proved affine
pieces. Unsupported operations, exhausted proof work and every nonzero
slope fall back. No bank arithmetic is replaced.

Five unit tests cover offset cancellation, both subnormal slope directions,
selection kinks, curved/division fallback, finite proof work, shared bindings
and nonfinite input. Existing genuine-refusal and transactional tests pass.
The complete 28-scenario corpus passes, including actual restore/replay and
subsequent moves. Its extra guard fails when a case or exact replay is lost.
All 23 old producer scenarios are value-identical. Copied corpus SHA-256:
`d5ed2bed27caefd5d667445b3572b1368644a69cce746f07c1f34e889d5ad4df`.

## Validation checkpoint

- Typecheck and bundle build pass.
- Python/browser end-to-end suite: **192 passed, 20 subtests, 436.98 s**;
  51 pre-existing deprecation warnings.
- `scripts/check-dist` builds source and wheel, installs the wheel in a fresh
  temporary environment and reports API 23 / document versions 1–10 /
  version 0.2.0. No upload. npm reports three moderate dependency advisories;
  no dependency or lockfile change is included here.
- Widget suite with two workers: **1412 passed, one speed-floor failure**.
  All functional tests pass. The fixed 900 ticks/s floor also fails on
  unchanged main on this host (378 ticks/s). Candidate observed 628 ticks/s
  under concurrent CAD/browser load; no floor is weakened. An earlier
  unlimited-worker run also timed out an RPC under load; that disappears
  with two workers. Final performance retry remains pending.
- Real full-tree Curta worker: the single input-9/360° carry completes;
  no page errors; the screenshot was inspected at crank 360°. Raised
  withdrawal stops at **145.22323837279146°**, with exact snapshot replay.
  Carried withdrawal and full Python bank comparison are still running.

ADR-070 records the confirmed branch-decision design. This repository has no
separate architecture synthesis; its decision index is updated. This is not
production Curta adoption, acceptance of T07 print fitting, or completion of
the whole operating-roadmap change.

## Final browser and widget results

The complete widget suite now passes **1413/1413, 62.64 s**, with one worker
after the heavy browser suites complete. The unchanged cost suite separately
passes **14/14, 35.44 s**, including **1051 ticks/s** against the original
900 floor. The earlier failures were load-sensitive; no floor or functional
expectation was relaxed. A separate functional run passes **1399/1399**.

The full Curta worker acceptance now completes carry and exact carry replay,
both short and two-revolution withdrawal requests, exact stop replay, reverse
relief and idle retention. Raised stop: **145.22323837279146°**; carried
stop: **504.9514572141925°**; both retain the tens shaft at **169.6°**.
No page errors. All 213 bank values are captured for Python comparison.
Bundle SHA-256:
`1098d52b62445f2a8ef6fece5ce38b4d9723ae1f8a6c74d21729668d4bb6d1aa`.
The original export hash above is unchanged. Both the complete-assembly
carry screenshot and final relieved pose were inspected; the latter reads
crank **504.9015°**, correctly reflecting −.05° relief.

Producer full suite: **3499 passed / 2033 subtests, 4 skipped, 729.80 s**.
Real native/mesh stop and overtravel checks plus neighbouring motion controls:
**6/6, 88.940 s**. The final Python whole-assembly carried case and direct bank
comparison remain pending at this checkpoint; no integration is claimed yet.

## Acceptance complete

Final full Python Curta: **2/2, 1145.059 s**. Comparing the complete Python and
browser banks at both stops and both relieved/idle states gives **213 values
per state, maximum difference exactly 0.0**. Reports:

- Python SHA-256: `75c294c40f3c124a0461fbe76f56c45b91cb737a251d9aab2fd03ade7d3aa931`.
- Browser SHA-256: `f5e736d94e5cdf777817ea94a23cdf11a9ec03657f05face7f850b2255d370b4`.

The baseline delta is synchronized and strict OpenSpec validation passes.
All runtime/geometry acceptance is complete. Integration remains the
authorized post-archive operation: require clean main unchanged at `e82b521`,
fast-forward only, verify both commits and remove only this clean worktree.
The project handoff records the actual integrated pair afterwards, rather
than this archive pretending that its own future commit already exists.
