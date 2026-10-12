# Internal mesh validation

## Package

Planning commit `832252a98c6f44776ccef8817cf8034ba95dd392`.
Tested uncommitted `machinome_mechanics/gears.py` SHA-256
`d7433e1d8f7f9742ca5bd5da9118712d49365422dfda9d5d62a0a0798af3390b`.
Commands ran from the cycle worktree with workspace Python, PYTHONPATH=$PWD,
and OPENBLAS_NUM_THREADS=1 / OMP_NUM_THREADS=1.

- Red: focused test collection failed because internal_mesh_angle did not exist.
- Green: full `python -m pytest -q` passed 184 tests and 24 subtests in
  1.71 seconds, under 768 MiB address-space, 45 CPU/60 wall-second limits.
  Thirteen new tests cover Thor's signed unwrapped coefficient, OpenTorque's
  independent external-mesh oracle, relative-mesh identity, common-frame motion,
  count scaling, unvalidated counts and zero divisor, plus actual Solid2
  all-operand and fixed-ring child-local expressions.
- `python -m sphinx -b doctest -W --keep-going docs
  /tmp/mechanics-internal-doctest`: 150 examples passed in 1.80 seconds,
  maximum RSS 141,408 KiB, under a 768 MiB process-tree cgroup with zero swap
  and 60-second runtime. First run caught an RST heading underline warning;
  it was corrected, and the final strict run passed without warnings.
- `python -m sphinx -q -b html -n -W --keep-going docs
  /tmp/mechanics-internal-html`: passed under 768 MiB address-space and
  45 CPU/60 wall-second limits.
- `python scripts/check-dist`: wheel/sdist builds, strict metadata and installed
  numeric/deferred smokes passed outside the checkout, under 768 MiB
  address-space, 90 CPU/120 wall-second limits. No uploads or shared repointing.
- Strict OpenSpec validation: four items passed; git diff --check passed.

Framework and viewer remained clean at
`8d2bd71171be81f13ba5dd492851ed8b3a9ababb` and
`4355da1a7f64dacd7d86eb27dbdfdf7ced94598f`.

Independent Sol review found no defect in formula, frames, domains, tests or
documentation. Thirteen focused tests repeated under a 768 MiB address-space
and 60 CPU-second cap with threads1: 0.14 seconds test time, 0.48 seconds wall,
50,960 KiB maximum RSS. Review explicitly confirmed OpenTorque's common-frame
-input/6 and local -7*input/24 identities and Thor's retained mounting signs.

## Consumers

All CAD-backed imports, probes, tests, builds and captures below were serialized
in systemd process-tree cgroups capped at 768 MiB, zero swap, threads1 and
at most 300 wall seconds (parent probes: 60). No cap was raised. RSS below
is measured by /usr/bin/time, not systemd's charged-memory summary.

### OpenTorque

Original master base `59c51fda7f183b98682a65227b3d288e13941ad7`;
Sol consumer commit `98208070b4c623d647e75b18dfd4fd2e6fb763f8` on
mechanics-internal-mesh-angle. Three real orbit-to-planet laws now use
internal_mesh_angle(0,126,54,carrier)-carrier. Sun-to-orbit 1/8, phases,
axes, hierarchy and source transforms are unchanged. The old external-mesh
law remains an independent test oracle. Dependency/Python metadata and README
document the founded, unpublished source package.

- `scripts/check-internal-mesh-angle`: eight repeated/signed states, all three
  local/common-frame planet angles, and eighteen actual deferred-law samples
  passed (3.48 s, 475128 KiB RSS).
- Native reducer faceted 8/8 (7.72 s, 591060 KiB) and exact 8/8 (3.42 s,
  541444 KiB); supporting output-stack 6/6 and actuator 6/6 faceted passed
  (combined 16.96 s, 572220 KiB).
- Root build and fresh axial ReducerPosePreview image passed (11.11 s,
  525024 KiB). Parent inspected `_build/internal-mesh-angle-axial.png`:
  coherent three-planet arrangement and bearings. The fixed ring is absent
  from this preview, so it is not visual proof of ring contact.
- Parent read all changed source, metadata, tests/probe and
  `docs/internal-mesh-angle.md`, checked raw gate summaries and independently
  reran the native probe: pass, 3.62 s, 523160 KiB RSS.
- Raw logs retained outside build: /tmp/opentorque-internal-mesh-probe.log,
  /tmp/opentorque-internal-mesh-reducer-faceted.log,
  /tmp/opentorque-internal-mesh-reducer-exact.log,
  /tmp/opentorque-internal-mesh-supporting-faceted.log and
  /tmp/opentorque-internal-mesh-build-image.log.

### Thor

Original main base `c229b25322e3b899aa70349355dccd262fb8748b`;
Sol consumer commit `097ffd94e6f42f1a30528b2137f46a336e855650` on
mechanics-internal-mesh-angle. The positive-six coefficient is now obtained
from internal_mesh_angle(1,60,10). All four separate negative mounting signs,
bound motor/pinion ports and PHASES remain unchanged.

- Retained `docs/verify_internal_mesh_angle.py`: eight numeric angles, four
  actual native relations at +/-20 degrees and twenty actual deferred values
  pass. Parent independently repeated it: 3.99 s, 521216 KiB RSS.
- New complete-model regression checks all four actual spin/turn ports at
  shoulder +/-20 against independent 60/10 and placement signs. First draft
  incorrectly inspected assembly motion operations; corrected to actual ports.
  Parent rejected a helper-as-oracle draft before final validation.
- Broad exact attempt failed that initial draft and then hit 768 MiB in the
  assembly inventory. It is NOT a full suite pass; neither the broad suite nor
  historical exact mesh contracts were recertified. Historical 31/33 result
  has two failures each reporting 260 of 272 unexpected pairs.
- A focused loader retained initially under docs failed discovery (expected
  path, got None; 4.59 s, 433560 KiB), executing no mechanical test. Moving
  the alias/companion to simulation made the retained command reproducible:
  `machinome test --exact simulation/internal_mesh_focus.py` passed 1/1.
  Parent independently repeated this exact retained command: 1.65 s test,
  6.21 s wall, 498760 KiB RSS, unit internal-parent-thor-retained.
- Root build passed (11.8 s); home and art2=20 snapshots passed (8.2/9.1 s).
  Parent inspected both /tmp/thor-internal-mesh-angle-{home,driven}.png:
  coherent external assembly, visibly driven upper arm. Enclosed gearing
  means these images prove external poses, not tooth contact.
- An earlier virtual-address-capped preflight could not map OCP/VTK; no CAD
  result is claimed from it. Final gates used physical-memory cgroups.
  No raw log files were retained; project record names transient journal units.
  Parent reviewed all changes and the corrected evidence record
  `docs/mechanics-internal-mesh-angle.md`.

Both final consumer trees are clean before integration. Framework/viewer heads
remain the package-header identities. The complete new requirement was synced
and compared byte-for-byte with its delta; four strict OpenSpec items and
git diff --check passed. Archive and local guarded integration follow; the
next ledger update records exact merged commits and post-merge checks.
