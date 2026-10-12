# Driven four-bar pose validation

## Package

Planning commit `69b4907e4bec19f248b563c0bbbdb8b4ebbe7aa5`.
Tested uncommitted machinome_mechanics/linkages.py SHA-256:
`112ea044ff1ec430ab5b328eb9c2caa16680b91133c752ad27cdcc018efc6c33`.
Commands ran in this worktree with `PYTHONPATH="$PWD"` and workspace Python.

- Red: `python -m pytest tests/test_four_bar_pose.py -q` failed collection
  because four_bar_pose was missing, before implementation.
- Focused green: 15 passed. Full `python -m pytest -q`: 143 passed,
  24 subtests passed.
- After the resource incident, full package suite repeated under 768 MiB
  address-space / 45 CPU-second / 60 wall-second caps with OpenBLAS/OMP
  threads1: same 143+24 result, 2.29 seconds wall, peak RSS 121,424 KiB.
- Tests compare closure to an independent coordinate-circle construction and
  verify all three moving-link lengths, branch cross-product and reconstructed
  bearings. Both sides, three scales, shifted pivots and 73 angle samples
  from -360 to 720 degrees are checked. Constructed rocker angle >180 is pinned.
  Inner/outer tangency and unreachable/singular errors are covered. Actual
  Solid2 expressions simultaneously defer angle, both pivots and all lengths
  for five samples on both branches and recheck geometric closure.
- `python -m sphinx -q -b doctest -W --keep-going docs
  /tmp/mechanics-four-bar-doctest`: 131 examples passed.
- `python -m sphinx -q -b html -n -W --keep-going docs
  /tmp/mechanics-four-bar-html`: passed.
- `python scripts/check-dist`: built wheel/sdist strict metadata and installed
  numeric/symbolic smoke passed outside checkout; nothing uploaded.
- `git diff --check` and `openspec validate --all --strict`: passed.

Framework and viewer observed clean at package checks:
`8d2bd71171be81f13ba5dd492851ed8b3a9ababb` and
`4355da1a7f64dacd7d86eb27dbdfdf7ced94598f` respectively.

Independent Sol review reran all 15 tests and found no substantive issue.
An additional deterministic 1,802 valid random branch poses found no wrong
branch, maximum independent-point/reconstructed-bearing error 6.30e-14 and
link-length error 1.69e-14. Rocker outputs outside the principal interval
were retained; coupler bearings remained principal. Tangency conditioning and
atan2 seam jumps are documented limits, not promises of continuous tracking.

## Consumers

Both consumer reviews are complete. Local integration follows the completed
implementation commit; its outcome is recorded in the next campaign ledger.

### Dragon R1

- Original main `644c70317def9b55da7750924383977fc43b5185`;
  migration `107102444b2614f65e6beb9229657c5a160e3d9f`.
- The local inverse ride law, source-minus-target angles, reflected cases,
  Y offsets and SuspensionPose remain unchanged. The helper owns only the
  driven endpoint, closure and output bearings; no source pivot was moved.
- Parent reviewed full source diff, docs/mechanics-four-bar-pose.md and
  scripts/check-four-bar-pose, then reran the independent old-vs-actual probe.
  All three rotations and both XYZ points match within 1e-10 across 401 numeric
  rides for each of four handed variants and seven actual deferred samples
  per variant over [-4,+4] mm.
- Affected faceted 14/14 and root faceted 3/3 pass at volume epsilon 0.001 mm3;
  build passes. Affected exact suite is 9/14: the same five failures were
  reproduced on detached untouched base 644c703, with unchanged tests. Two
  rack/link intersections are 0.0002594828755637162 and
  0.0002026781564762112 mm3; three rim/yoke residues are
  2.4424906541753444e-15 mm3. This is no-regression evidence, not an exact-clean
  certification. The temporary baseline worktree was removed cleanly.
- Sol and parent inspected fresh exposed front-bump (+4) and rear-droop (-4)
  images _build/four-bar-front-bump.png and _build/four-bar-rear-droop.png.
  Both handed pairs remain coherently assembled. Whole-car body occlusion is
  not used as linkage proof. Installed-car travel remains +/-2 mm; standalone
  mechanism travel remains +/-4 mm. No dynamic/load certification is added.
- Framework/viewer stayed clean/stable at 8d2bd71/4355da1. No helper issue.

### Strandbeest

- Original main `1c81ca5381f953776e3ac8e190f990a09c7b8a0a`;
  migration `4ccaa591de164322a6e62318d1ddd0d6b6111987`.
- W and U preserve their +1/-1 branches, returned C is reused, and the scale
  guard, guarded local intersection and V/T/S triangles remain unchanged.
  First mechanics import has an explicit project dependency declaration.
- Parent reviewed production/test diffs, full docs/four-bar-pose-verification.md
  and independent docs/probes/four_bar_pose.py. Final parent rerun passed all
  eight numeric points at 1,083 distinct poses / 2,166 forward/reverse
  comparisons across three scales (2e-12), and six actual Solid2 C/W/U samples
  (1e-9): 0.23 seconds, peak RSS 36,420 KiB under the limits below.
- Parent reran all six kinematic tests and the relocated genuine wrong-W-side
  mutation: 7/7 pass, 0.89 seconds wall, 37,580 KiB peak RSS. The mutation's
  isolated child preserves the explicit helper source overlay. Legacy CAD
  mutations still expect an absent solid executable; that unrelated harness
  was not modernized. A broad attempt was terminated after 11:19, with 15
  passes observed then five legacy CAD harness failures/timeouts. Its partial
  result is not a suite pass. Parent also found and terminated its remaining
  orphaned rotor mutation child; no campaign process remained afterward.
- Final sequential cgroup gates used MemoryMax=768M, MemorySwapMax=0,
  RuntimeMaxSec=300 and BLAS/OMP threads1. Parent inspected retained logs:
  affected LegDemo faceted 4/4 (1.88 seconds, zero volume epsilon), exact 4/4
  (7.36 seconds), full WalkingDemo build exit0 and full driven web capture
  exit0 (14.23 seconds, independent process peak RSS 568,120 KiB).
- Parent inspected both fresh .cache/four-bar-leg-driven-web.png and
  .cache/four-bar-full-driven-web.png, phase137. The individual chain and
  repeated full-machine leg stations are coherently assembled; source axial
  layers remain visible. Fine pivot contact and the occluded bank are not
  pixel-certified. Exact affected contracts supply the sampled contact checks.
  No new stability, force, traction or whole-machine collision claim is made.
- Source hash matches the package identity above. Framework/viewer remained
  clean and unchanged at 8d2bd71/4355da1. No helper issue remains.

Resource incident: the first full-leg deferred probe recursively expanded all
eight point expressions, including nested unchanged triangle constructions.
Parent's duplicate diagnostic run (PID 3093102) reached about 2.8 GiB RSS and
was still running after 14 minutes. After the pilot reported killing a
high-memory process, parent explicitly terminated this remaining owned process
(exit 143). The exact process the pilot killed could not be identified. No
success is claimed for the original probe. Running duplicate unbounded probes
was a validation-process mistake, not evidence of a helper geometry failure.

The replacement retains all-point numeric legacy comparisons (1,083 distinct
poses, checked forward/reverse for 2,166 comparisons) and evaluates only changed
C/W/U closure expressions at six times, compiling each once. Parent reran it
successfully using workspace Python, explicit cycle PYTHONPATH, thread counts1,
`/usr/bin/time -v timeout 60s prlimit --as=805306368 --cpu=45 -- python -u
docs/probes/four_bar_pose.py`: 0.21 seconds, peak RSS 36,260 KiB. Subsequent
heavy checks are sequential and resource-bounded. Full-leg symbolic expansion
is not claimed; full-model numeric and CAD evidence remain separate gates.

Address-space caps of 1.75 then 2.0 GiB failed on CAD shared-library/thread-local
allocation at roughly 575--578 MiB RSS. The identical untouched-base affected
command failed at 574,092 KiB too; this was a cap incompatibility, not a new
helper failure. The final physical-memory cgroup gates above passed. Parent
verified the live snapshot unit's MemoryMax=805306368, MemorySwapMax=0 and
five-minute runtime limit. Its charged-memory peak reached that ceiling;
shared mapping accounting is not identical to process RSS. No cap was raised
after adopting this 768 MiB process-tree limit.

## Completion

One public helper, two independently migrated project repositories. Package
unit/deferred/docs/distribution gates and the affected consumer evidence above
support completion, with explicit pre-existing exact/harness and resource
limitations. Sync and strict validation precede archival; local fast-forward
integration and post-merge checks follow the implementation commit. No push,
publication, framework edit or shared installation change.
