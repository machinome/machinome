# Closed belt path metrics validation

## Package

Planning commit `7c5193aa2446b36549804c847d24d3995ccbfa7b`.
Initial uncommitted `machinome_mechanics/belts.py` SHA-256:
`8e7dc4203f44a62569f2de3062bdc89e6e93d2c206c50b6249ac659cd72e372f`.
Final corrected source SHA-256:
`09388c2cb4a3839f8c542c04cebfd5f29344dbee240023ccef7382171aa1a9dd`.
From this worktree, `PYTHONPATH="$PWD"` and workspace `.venv/bin/python`:

- Red: `python -m pytest tests/test_belt_paths.py -q` failed collection on
  the missing `belt_path_metrics` import before implementation.
- Initial green: `python -m pytest tests/test_belt_paths.py tests/test_belt_tangents.py
  -q`: 38 passed. Initial full suite: 95 passed, 24 subtests passed.
- Final corrected full suite: 97 passed, 24 subtests passed. Doctest, strict
  HTML and wheel/sdist checks below were repeated successfully after correction.
- Nineteen new tests cover independent angular references, unequal three-circle
  indexing, reversal, a separate exact unequal-two-pulley length formula,
  collinear zero wrap, zero radii, limiting zero spans, malformed topology,
  unreachable geometry, deferred Solid2 geometry at five samples, the reviewed
  floating seam regression and a genuine near-seam wrap without clamping.
- `python -m sphinx -b doctest -W --keep-going docs
  /tmp/mechanics-path-metrics-doctest`: 109 passed, no failures.
- `python -m sphinx -b html -n -W --keep-going docs
  /tmp/mechanics-path-metrics-html`: passed.
- `python scripts/check-dist`: wheel and sdist built, strict metadata and
  installed numeric/symbolic smoke passed outside checkout; nothing uploaded.
- `git diff --check`: passed.

Framework and viewer observed clean at respectively
`0ce71cdea6cc4a2e7fd7e85dc68847daef3d34cc` and
`4355da1a7f64dacd7d86eb27dbdfdf7ced94598f`. Consumer records sample their
own before/after dependency state; these are not frozen checkout claims.

Later, during corrected consumer checks, the independently managed framework
advanced cleanly to `8d2bd71171be81f13ba5dd492851ed8b3a9ababb` (ancestor
joint constraints). Its diff does not touch machinome.math. Viewer stayed at
4355da1. Consumer records distinguish observations around their runs; package
tests were repeated against the advanced framework as well.

Independent Sol review found a substantive seam issue missed by the simple
horizontal zero-wrap example: on a large oblique collinear route, tiny negative
angular roundoff made `a - 360*floor(a/360)` round to exactly 360. Added the
reviewer's deterministic case first: it failed `assert 360.0 == 0` (18 other
path tests passed). Reapplying the same periodic reduction maps that rounded
endpoint to zero, without an epsilon band or numeric-only branch. The regression
also checks deferred expressions; a separate genuine near-360 wrap stays nonzero.
Consumers repeat their probes and affected gates against the corrected hash;
their original images retain their original hash provenance.

## Consumer review

All five consumers reviewed on focused project-owned branches. Local integration
follows this completed-cycle commit; no integration claim is made here yet.

Thor convention audit found an existing exact-zero wrap quirk: equal-radius-2
circles at (0,0), (10,0), (20,0) report wraps (180,360,180) and length
65.13274122871834, while canonical zero-wrap measurement gives (180,0,180)
and 52.56637061435917. This cycle keeps the helper's zero-wrap contract and
requires a Thor compatibility adapter, not a silent project bug fix. Real
elbow/wrist routes are nondegenerate. Printer after-span arcs map to the
helper's circle-indexed arc tuple rotated by one entry.

### Prusa3-vanilla and Kossel

- Prusa original master `46c9e5741dde0ef07eefb89a4975749f95d52872`;
  migration `95f575c45c8fa5dc1f8c63bd1df3a1b1ef54103e`.
- Kossel original master `159ad7eb228d83819f4e91c82cd58f33a5a1f0f7`;
  migration `5c720a6a2ece81ec3f9b8a96fe67c8953a3f5125`.
- Public wrappers remain lists/scalar; arcs rotate once from circle indexing
  to after-span indexing. Local duplicated normal/tangent/path math removed.
  Pitch fits, marker meanings, mounting/phase and Kossel's known axis bug stay.
- Parent reviewed both source diffs, runnable scripts/check-belt-tangent-points
  and complete records; reran probes successfully. Six/five routes compare
  independent legacy spans, every station and total length within absolute
  1e-12: actual X/Y or tower, back-idler, one/both zero radii, limiting span.
- Prusa X and Y each faceted/exact 6/6; Kossel Tower faceted 9/9 and root
  faceted 15/15. Both builds passed. Unrelated Kossel exact Effector failure
  is outside this gate, not claimed fixed or rerun.
- Both Sol and parent inspected fresh belt-path-metrics-nonzero.png overviews
  in each _build directory: Prusa x120/y80/z60 and Kossel x50/y-30/z110 show
  coherent visible routes and assembly poses. Image resolution/occlusion does
  not establish tooth contact or correct physical travel in the known bug.
- Each docs/mechanics-belt-path-metrics.md records exact test/capture commands,
  mechanics source identity and dependency drift from 0ce71cd to 8d2bd71,
  with viewer stable at 4355da1. All listed probes, CAD suites and builds passed
  again against the final corrected helper and advanced framework. Actual route
  metrics did not change; images retain their initial helper hash provenance.
- Sol's independent correction review passed 40 focused tests and the reported
  seam reproducer now returns (180,0,180). Both final consumer amendments are
  evidence-only; source did not change after their CAD checks.

### Hangprinter

- Original version_4 `12f74a6f00f0275cd2f289c703b0d122cc1875a9`;
  migration `28ffcd1de97f5880a9b96147c64940707a09c3d8`.
- Same list/scalar adapters and one-position arc rotation; obsolete private
  tangent/normal implementations removed. Prior durable probe now derives
  measured normals from span directions instead of removed private helpers.
- Parent reviewed complete source/evidence and executed the asserting probe
  embedded in docs/belt-path-metrics.md. It checks flattened cardinalities
  and absolute 1e-12 across actual winch, back-idler, zero radii and limiting
  span routes. Actual span/arc/station errors <=2.13e-14/5.68e-14/2.84e-14 mm,
  length about 605.3484495084118 mm, agreeing with the retained independent
  calculation (the immediate-base record rounds its last digit to 7).
  Limit route remains all zero.
- Faceted/exact winch 5/5 each, root 19/19 each; build passed. Sol inspected
  focused and z300 images; parent inspected /tmp/hangprinter-belt-path-metrics-
  winch.png, showing coherent spool/idler/motor routing. Images cannot certify
  force, tension or physical contact. Full commands and stable clean dependency
  heads are in the project record. All probes, listed suites and build passed
  again with the corrected helper at stable clean 8d2bd71/4355da1; initial
  images retain their earlier helper hash and 0ce71cd dependency provenance.

### Metamaquina2

- Original main `42013334c43b036bacbf68b881f01704bae20ba6`;
  migration `bd56d5211311ef4449f94c975a45190688ee430b`.
- Same public wrapper forms, marker mapping and arc rotation. Removed unused
  _normals/_touch; the retained old reference probe now owns its old touch math
  and derives observed normals from spans instead of dead private production.
- Parent reviewed source, complete docs/belt-path-metrics-verification.md and
  runnable docs/probes/belt_tangent_points.py, and reran the latter against
  the final helper. Actual X/Y, back-idler, collinear-equal, limiting inner,
  first-zero and both-zero routes agree within absolute 1e-12. X/Y lengths
  remain 803.8854513557229 and 1036.4343190090678 mm; all stations agree.
- Exact root passed 67/67 before correction in 421.84s and again with final
  helper in 203.04s. Explicit build passed. Existing jhead.scad line107 parser
  diagnostic on cold build remains documented, not presented as fixed.
- Sol and parent inspected fresh _build/belt-path-metrics-driven-web.png,
  x90/y-80/z140, rendered with corrected helper. Coherent exterior pose; contact
  details too small to certify visually. The corrected exact run began before
  framework drift was observed, so its framework content is not pinned. Final
  build/capture followed the clean 8d2bd71 observation; viewer stayed at 4355da1.

### Thor

- Original main `81ab279310e45b8cbc610ab52b8e29968e0e0ec8`;
  migration `a071b1863299af98cf7431b8971e9df9cb645637`.
- Numeric adapter retains tangent preflight contacts and exact diagnostic,
  truthy marker mapping, zero-radius wrap 0, exact-zero CW wrap 360 on a nonzero
  outgoing span, and the base raw angular direction at zero outgoing spans.
  Only degenerate legacy policy uses those contacts; ordinary path metrics
  delegate to the helper. Tangent remains needed by idler_clearance.
- Parent found a missed mixed limiting case during review: circles (0,0)r2
  CW, (5,0)r3 CCW, (8,10)r2 CW. Initial adapter returned first wrap321.340...
  instead of baseline38.6598... because zero span erased old handedness.
  Final adapter preserves the immediate-base raw angle using preflight contacts.
- Parent reviewed source, full docs/mechanics-belt-path-metrics.md and asserting
  docs/verify_belt_path_metrics.py, and reran final probe successfully. Elbow
  and wrist lengths unchanged at 462.9770193306483/223.52395515247483 mm;
  back-idler length error 1.137e-13 mm; ordinary wrap errors <6e-14 degrees.
  Collinear legacy wraps 180/360/180 remain exact; two-circle limiting route
  stays zero; mixed limiting route exactly 41.41812403389678 mm with baseline
  wraps; zero-radius old wrap and total preserved. Ordinary routes also pass
  an independent angular-tangent reference, separately from the base adapter.
- Final corrected-hash compile/build pass. Exact root 31/33, all belt checks
  pass; only known whole-machine overlap failures remain (260/272 unexpected
  pairs, first base.arduino_mega/base.base_box_body 2093.029 mm3). No change to
  tests or allowed overlaps. Stable final dependency heads 8d2bd71/4355da1.
- Sol inspected fresh home/driven OpenSCAD images; parent inspected driven.
  Exterior pose is coherent, contacts enclosed. Images were rendered with
  initial helper hash; final probe/build/exact rerun proves actual routes
  unchanged. This is not a claim to certify a previously failing whole robot.

## Completion

The independent review's only helper defect was reproduced red and fixed; a
separate Thor adapter mismatch was caught and preserved against the actual
pre-cycle baseline. All five final diffs, durable probes and representative
images were reviewed. Corrected helper tests, docs, distribution smokes and
consumer gates pass within the explicit existing limits above. The full added
requirement is synced and compared before archive. Local fast-forward merges
and post-merge verification follow the completed-cycle commit and are recorded
in the next cycle's campaign ledger.
