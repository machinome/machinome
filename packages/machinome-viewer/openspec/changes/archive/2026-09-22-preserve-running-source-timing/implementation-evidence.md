# Source-timing implementation evidence

Worktree-only, unintegrated and unreleased. Pilot authority: autonomous
evidence-led fixes, 2026-09-22. Framework planning amendment is now `95478bb`
(superseding `aa0a86c` and `5f90739`); viewer planning remains `46fea1d`.

## Red-first and corrections

- Initial eight producer fixtures: 15/16 assertions failed before executor
  changes. Failures included carry errors of 1.5, nonuniform error 1.75,
  curved error about 1.292893 and missing inherited-boundary crossing records.
- Source paths, retained-walk pieces, active-branch DAG classification, block
  propagation, shared contact probes and range location brought those cases
  to parity. Stop-record comparison normalizes only Python's always-present
  empty `time_drives` tuple versus the viewer's documented optional key.
- The unchanged time-drive suite caught a missing clock-to-admission alias
  inside contracted blocks. Fixed in source lookup; all 32 cases pass.
- New inherited-kink crossing-budget test failed in both runtimes: three
  surfaces across separate source pieces escaped a maximum of two. Both now
  count the law's whole propagated path and refuse transactionally, including
  record-disabled probes. No tolerance or physical expected value changed.
- V11 tests first failed at the old public version gate and time-drive loader.
  The corrected loader accepts driver-only/Play/time-drive programs, refuses
  missing clock mappings and malformed explicit maps, and keeps v10 rules.

## Classified old assertions, not regenerated physics goldens

`RangedBlock`, simultaneous spin +2 and shift +1 over dt=.05: the corrected
producer independently reports stop t=.3, carry/lower/spin=.6 and spin admitted
.6, blocked. The old browser test required the searched approximation
.29999999999972715 and .5999999999994543. The assertion now pins the producer's
exact solved path; static block affinity remains false.

The cost-only assertion for the existing Curta carriage changes from 5913.2
to 6277.4 expression evaluations/tick (+6.16%) because determined path pieces
need endpoints. Clearing (471.1) and Train (31.0) remain exact controls. This
is a measured cost change, not altered physics or a real-time claim.

Existing running, clocked and time-drive corpus JSON bytes are untouched.
Metadata tests move their unsupported-version example from 11 to 12 and assert
API 24/v1–11. Package version/release history is unchanged.

## Completed algorithm and compatibility validation

- Full TypeScript suite: **1456 passed in 55 files**, 78.49 s, including all
  four Curta exports; typecheck passes. Historical corpus JSON is untouched.
- All four unchanged Curta producer exports pass bulk and twelve-portion
  restored replay. Full banks, statuses, admitted travel, crossings and stops
  match. Producer totals: 30.247/35.306/50.954/62.235 s for 6/7/11/constrained11.
  The browser suite's bulk/full-replay times were 3.136/14.708,
  4.236/15.527, 6.265/22.341 and 6.258/22.160 s. Concurrent runs mean these
  are observations, not controlled performance or real-time claims.
- Real Chromium worker and forced fallback pass the full constrained request
  and restoration. Dedicated browser plus carriage suite: **8 passed and 2
  subtests**, 31.22 s. Both source-timing screenshots were inspected: crank
  180, ones 724, tens 704, first lever 0. Their heading explicitly says no CAD
  geometry; existing stand-in carriage captures were also inspected. Neither
  is acceptance of Curta's full native assembly.
- Actual API-23 bundle SHA-256
  `20880099c6490adca932f7152c987751a645dddd1bf089ff197342db3c81727c`
  refuses a producer v11 export before operation in Chromium. The framework's
  entry-point gate separately refuses a report supporting only 1–10.
- Distribution dry-run passed twice; the final wheel installs in a throwaway
  environment outside the checkout and reports API 24 and v1–11. No upload.
- Framework's final running/document/clocked-document/corpus/viewer-gate run:
  **581 passed, 696 subtests**, 52.26 s; additional contact/constraint/docs
  checks: **67 passed, 91 subtests**, 2.56 s. Two existing framework warnings.
- Strict OpenSpec validation passes across both repositories. ADR-071/072
  record motion-path composition and the semantic capability gate. Baseline
  specs are synchronized; unrelated active viewer changes are left untouched.

Exact producer/consumer/fixture hashes and full-bank summaries are in
[paired-source-timing.json](paired-source-timing.json). Each committed fixture
also includes matching producer hashes; the project checkpoint is 8852677.
The generator lives only in the framework; viewer tests import neither it
nor the project. No endpoint-era physics goldens were regenerated.

## Validation corrections and environmental interruptions

- One Vitest Curta run completed its assertions but reported an RPC timeout
  while its synchronous CPU work starved the test worker. The async test now
  yields between complete requests only; execution is not subdivided. A
  clean four-case run passed in 62.536 s, then the complete suite passed.
- Running distribution packaging concurrently with Vitest followed the bench's
  shared node_modules symlink and emptied primary's dependencies. The original
  primary dependencies were restored with its unchanged lockfile; its source
  worktree is clean. The bench now has private dependencies. A red-first test
  proves packaging refuses a symlink before invoking npm, preserving its
  target. The normal private-directory build still installs and builds.
- Earlier Python full runs found stale API/version assertions and then a
  changelog test assuming the first section must always be the prior release.
  The tests now retain the historical release entry while permitting the
  explicitly Unreleased correction. No release date/version was changed.
- npm reported three moderate dependency advisories during the locked install;
  no forced or unrelated dependency upgrade was performed in this carry fix.

Final complete Python/browser suite: **196 passed, 22 subtests passed**,
248.52 s; 51 existing dependency deprecation warnings. No skips or failures.
No push, publication, primary merge, worktree cleanup or Curta default adoption
is performed. Both repository completion records are prepared; their tested
content hashes are fixed in the paired record, with commits verified at handoff.
