# Application evidence — 2026-09-21

## Authority and state

The pilot approved the explained direction correction, matching viewer work,
and local integration after validation: “yes, do that and merge to main when
you're finished.” Base `e63700e4fdb90e066d47f358e9de0ea935ac1be9`; planning-only
commit `5673d1f` (amended for the explicitly approved precision extension).
Strict OpenSpec validation passed, the worktree was clean,
and one-commit ancestry was verified before implementation.

Implementation remains uncommitted and unintegrated. The viewer has its own
`mixed-threshold-landing` worktree based on `e82b521`, planning commit `f77dab4`.
Its matching implementation is under acceptance. No production
Curta adoption, API/format/version change, tolerance change, push or release.

## Original fault, red then green

`OvertakenFollower` starts at q=2. Before x=1 its rate is 1 and its gate is
q>2x+1; the threshold overtakes it at (x,q)=(1,3). Thereafter its rate is .5,
giving q=3.5 at x=2 and q=4 at x=3. The reflected fixture tests negative motion;
an observed fixture adds a free downstream bound; a stationary fixture tests
source-only crossing without invented movement. Expected values are derived
independently, not sampled from a corrected run.

Before implementation, all three moving/observed subcases raise the same
landing invariant; the stationary control passes. The candidate brackets the
incoming/non-incoming branches locally with sources fixed at the crossing,
then uses the existing ordinal landing walk. Only a jump whose level reads
another moving source needs this orientation check. The unchanged stationary
path retains its exact expression-evaluation count (986 in the pinned fixture).

Focused tests: **59 passed, 77 subtests passed, 8.84 s**. Expanded existing
running-read/jump/corpus/periodic-stop and clocked-corpus regression, with the
new direction tests: **163 passed, 653 subtests passed, 33.71 s**. This is a
selected regression suite, not the whole repository suite or final acceptance.

## Real-machine gate

Curta's faithful source-law reduction passes without the observer. With the
candidate correction it gets beyond `LandingInvariantError` but now raises
`UnsupportedLaw` in `_decide`: **one pass, one error, 24.042 s**. Evidence:
`_build_checks/mixed-threshold-reduced-first-fix.log` in the project. Thus the
direction correction alone does not meet the ratified real-Curta acceptance.

The complete source-backed `HigherOperatingTrial` confirms the same second
refusal: **one test, one error, 259.694 s**, on the ordinary carry preparation,
before the later withdrawal test can run. Evidence:
`_build_checks/mixed-threshold-full-carry-first-fix.log`. This is not merely
an artifact of the CAD-free reduction.

The original full-tree browser refusal is already reproduced on viewer
`e82b521`, bundle SHA-256
`8acaf5989e5fa99bb5f3314c2080016603893ca8e665569a4d707ff24f8de751`, export
`92719ac99b1188cc50cdc100683946c0235c5a3116be7a2993dff1f15d75c7db`.
The input-9 request completes, the 360-degree crank request refuses, the worker
snapshot is unchanged, no page error occurs, and the screenshot is inspected.

## Further finding: following contact mistaken for chatter

At crank 343°, the lever's pin-following branch should leave
`own - rest - approach` constant. After the corrected landing, its retained
value is −3.0518676393442563 and the evaluated level is exactly zero. Probes
of the inactive-reset branch read +2.220446049250313e−16 at fractions 1/64 and
2/64, zero at 4/64 and 8/64, −2.220446049250313e−16 at 16/64, then zero at
32/64 and 1. The first tiny positive value flips the reset on. That branch's
first probe reads −0.00017185156250021372, flipping it off; the engine calls
the repeated flip a sliding mode. It commits nothing.

An independent affine diagnostic `FollowingContact` uses
`32 + (1+x/7) - .1*x*(q+4.2-(1+x/7)>0)`, initially q=−3.2.
The gate-off solution follows q=−3.2+x/7, keeping contact level zero; gate-on
would pull below the pin. Its constant 32 contributes no motion but exposes
round-off in the current difference-of-evaluations/probe calculation. The
completion test is honestly red with the same `UnsupportedLaw`. Earlier
attempts without this arithmetic offset passed and were not reproductions.
It also fails on unmodified main `e63700e` (2.43 s, imported framework path
verified explicitly), proving the precision fault was not introduced by the
direction correction. The current candidate reproduces it in 2.58 s.

This is a separate precision/branch-decision finding, not proof of physical
interference and not authorization to suppress genuine chatter, skip the
request, change the carry law or loosen tolerances. The pilot explicitly
approved the extension: “Yes—extend the fix and finish validation.”

## Precision implementation and interim acceptance

`contact_proof.py` composes the skeleton increment into its contact level
using exact rational representations of the finite binary constants. It
certifies only zero slope. Unsupported operations and any nonzero slope,
including ±5e−324, fall back to the existing executor. Bank evaluations,
branch operators, tolerance constants and clocked code are unchanged.

An affine-only first attempt passed the small diagnostic but still failed
the faithful Curta reduction (one pass / one error, 30.755 s): a prefix can
cross several continuous profile knots. The final proof partitions at exact
`min`/`max`/`abs` selection crossings, then applies the same affine certificate
to every piece. It does not extrapolate one branch across a kink. Unknown
kinks/curves remain unproved; a 1024-piece proof-work bound returns to the
existing algorithm, never accepts motion. This is the design's per-affine-piece
certificate applied across a piecewise-affine profile, not extra sampling.

Faithful Curta reduction: **2/2 pass, 54.046 s**, including the unchanged
observer-free source laws and their downstream restraint observer. Focused
orientation/proof tests: **7 passed / 7 subtests, 1.62 s** before adding a
further bounded-work/nonfinite negative test. Producer corpus/proof suite:
**20 passed / 88 subtests, 3.11 s** before the extra width guard.

The corpus now has 28 scenarios, 25 machines and 401 recorded steps. Its 23
previous scenarios are value-identical, including all old documents, banks,
crossings and commands. SHA-256:
`d5ed2bed27caefd5d667445b3572b1368644a69cce746f07c1f34e889d5ad4df`.
The viewer copy is byte-identical. Both width guards require the five new
cases, real replay and subsequent completed motion.

The matched browser build completes the actual input-9/360° request in its
worker, with no page error; the screenshot shows the complete original
assembly tree posed at crank 360°. Full obstruction/relief/replay, Python full
assembly and final regressions remain in progress at this checkpoint.

An early full framework run straddled the fixture edits and retained an old
module in memory: missing new fixture lookup and two stale width-guard
exclusions failed. Fresh focused replay passes; a clean final full run is
required. The first browser full run had a stale corpus census (corrected),
one worker timeout under host load, and a speed floor failure. Repeating with
two workers removes the timeout and leaves only the speed floor; unchanged
viewer main also fails that same floor (378 ticks/s versus required 900).
No threshold is relaxed; final performance validation is still pending.

## Final repository and browser results

- Full framework: **3499 passed, 4 skipped, 2033 subtests, 729.80 s**.
  Source path is this isolated worktree. All previous genuine-refusal,
  transactional, running, clocked, play and expression-cost assertions pass.
- Viewer complete widget suite: **1413/1413 pass, 62.64 s**, with one worker
  after heavier browser tests finish. The unchanged speed floor passes;
  the isolated cost suite also passes 14/14 (1051 ticks/s on the formerly
  failing 900-floor test). No test expectation or tolerance was weakened.
- Viewer Python/browser suite: **192 passed / 20 subtests, 436.98 s**.
  Typecheck, bundle and fresh-wheel installation smoke pass.
- Real full-tree browser: ordinary carry, exact carry replay, raised and
  carried withdrawal, short/long requests, stop replay and relieving/idle
  motion pass with no page errors. Stops are **145.22323837279146°** and
  **504.9514572141925°**; both retain tens shaft **169.6°**. The resulting
  213-value banks are retained for direct Python comparison. Browser bundle
  SHA-256 is `1098d52b62445f2a8ef6fece5ce38b4d9723ae1f8a6c74d21729668d4bb6d1aa`;
  export SHA-256 is unchanged from the red reproduction.
- The carry and final relieved-state screenshots were inspected. The final
  crank readout is **504.9015°**, following the requested −.05° relief.
- Curta geometry/neighbour checks: **6/6 pass, 88.940 s**. Both exact solids
  and complete published meshes are clear at the admitted raised/lowered
  stop, and both collide at .2° overtravel. Eight ordinary three-turn source
  tooth counts and four pin/pawl/reset-law controls also pass.

The earlier full-Python run loaded the superseded affine-only proof: its
raised case passed, then it was deliberately terminated during its carried
case rather than accepted as current evidence. A fresh whole-assembly run
against the final piecewise certificate passes raised withdrawal; the
carried case and full-bank comparison remain pending at this checkpoint.

The CLI's old framework-local web-app build note does not apply to the
independently owned viewer, and its one-commit convention does not override
the shop's two-commit cycle. No shared/main viewer source was built or edited.

## Acceptance complete

Final complete `HigherOperatingTrial`: **2/2 pass, 1145.059 s**, including
unchanged source carry preparation, raised/carried withdrawal, exact replay,
two-revolution requests and reverse relief with idle retention. Direct
comparison of Python and browser stopped/idle banks covers **213 coordinates
in each of four states; maximum difference is exactly 0.0**. Both stops
and the source geometry remain as recorded above.

Raw report SHA-256 values:

- Python: `75c294c40f3c124a0461fbe76f56c45b91cb737a251d9aab2fd03ade7d3aa931`.
- Browser: `f5e736d94e5cdf777817ea94a23cdf11a9ec03657f05face7f850b2255d370b4`.

Additional project support-curve/law regression: **5/5, 105.705 s**, including
79,310 ordinary trajectory samples. Final focused framework/docs/corpus
check: **39 passed / 131 subtests, 3.27 s**. Both baseline deltas are fully
synchronized, with all prior requirements preserved. ADR-136 and the
architecture synthesis record the confirmed decision.

Integration is the authorized **post-archive** operation, not a claim made
by this implementation commit: require clean main still at `e63700e`,
fast-forward only, verify two-commit ancestry and then remove this registered
clean worktree. The independent viewer follows the same sequence from
`e82b521`. The originating project's final handoff records the resulting
content IDs after those operations; no third framework evidence commit is
needed. No production Curta adoption, push or publication is included.
