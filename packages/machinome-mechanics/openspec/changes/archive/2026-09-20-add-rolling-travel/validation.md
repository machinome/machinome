# rolling_travel validation

## Package evidence

Environment: workspace `.venv/bin/python`, explicit PYTHONPATH to this mechanics
worktree. Framework content `9fb5127fad62e6c66067b34e7d02dd389471fa2d`;
viewer content `c6df93ddd1723f1b9be0fb7e73f19d6f6c2daffa`.

- Red: `python -m pytest -q tests/test_rolling.py` failed collection because
  `rolling_travel` was absent from this worktree's flat API.
- Green: `python -m pytest -q`: 38 passed, 24 subtests passed.
- Independent expectations: circumference fractions at signed/multi-turn angles,
  Thor's 117-tooth/2 mm belt advancing one tooth per 360/117 degrees, degenerate
  radius arithmetic and deferred angle/radius evaluation.
- `python -m sphinx -q -b doctest -W --keep-going docs docs/_build/doctest`
  passed after correcting a documentation-only signed-zero expectation.
- `python -m sphinx -q -b html -n -W --keep-going docs docs/_build/html` passed.
- `python scripts/check-dist` passed wheel and sdist metadata and external
  installation smokes, including the new exported numeric/symbolic helper.
  Nothing uploaded. The checker now compares the actual declared export list,
  replacing the foundation's fixed count of twelve.
- An independent Sol review found no formula, unit, symbolic, export or smoke
  defect. Its remaining documentation gate is integration of the named Dragon
  R1 and Thor consumers before treating this cycle as complete.

## Consumer evidence

Helper file SHA-256:
`0c111fceb475523329a2a90b55b8f2d55936fbe68201108208b80685e495b5d2`.

### Dragon R1

- Original main: `b6e1e32`; migration branch `mechanics-rolling-travel`,
  commit `644c70317def9b55da7750924383977fc43b5185`.
- The Sol agent migrated rack calculations, relation coefficients and integrated
  suspension steering without changing geometry, dimensions, phase or bounds.
- Independent five-pose sweep (-15, -7.5, 0, 7.5, 15 degrees): max travel error
  0 mm; endpoint magnitudes 2.356194490192345 mm; kingpin outputs unchanged.
- Steering faceted 14/14 and suspension faceted 14/14 (existing faceted run uses
  `--volume-epsilon 0.001`); steering exact without that option 14/14; pytest 8/8.
- Symbolic rack expression preserved. Two OpenSCAD endpoint snapshots inspected
  by both agent and parent; rack/sector stays visibly engaged.
- Full commands/evidence in project `docs/measurements.md`. Source geometry and
  user files unchanged. Parent reviewed the commit; no unresolved helper
  regression.

### Open Robot Actuator

- Original master: `52945759b57ec7ba40b3630ac9d861914906f2c0`.
- Migration commit: `4b2c01d3d37b46ab44e67c30ba0046137779e7fd`.
- Sol replaced its pitch-circle travel coefficient and declared its new package
  dependency; tensioner inverse conversion is deliberately unchanged.
- Before/after angles -360, -45, 0, 90, 810 degrees retain travel -30, -3.75,
  0, 7.5, 67.5 mm. Symbolic input accepted, finite build passed.
- Faceted and exact actuator suites each 14/14; rest and 810-degree snapshots
  inspected by agent, moved snapshot also inspected by parent. The two belt
  stages retain their routing. No helper regression.
- Reproduction commands and limitations: project `docs/rolling-travel.md`.

### Thor

- Original main: `c40e031f36b486c6ffa39117ba59904b70a008a6`.
- Migration commit: `c3c543d7d73d84f5ff47da326ebc436660cae6cb`.
- Sol replaced elbow and wrist belt laws without changing pitch radii, signs,
  zeroes or ratios. Signed/multi-turn sweep max error 5.7e-14 mm; SymPy
  old-minus-new simplifies to zero. Root build and symbolic document pass.
- Exact root suite 31/33, including both affected belt checks. A temporary
  detached worktree at the original commit reproduces 31/33, the same two
  overlap-inventory failures (260 of 272 unexpected pairs), and the same first
  pair/volume. No geometry or placement changed in this migration.
- Standalone Art2's unbound-coordinate refusal also reproduces at baseline.
  Both unrelated limitations remain in project evidence, not silently fixed.
- Home/driven images inspected by agent and parent: outer arm poses remain
  coherent, with existing detached wrist fasteners visible. Enclosed belts are
  occluded; these images are not belt-contact evidence. Numeric, symbolic and
  posed-port contracts establish preserved travel.
- Full baseline/current commands: project `docs/mechanics-rolling-travel.md`.
  Temporary baseline worktree removed cleanly; no unresolved helper regression.

### Hangprinter

- Original version_4: `a342b94c229cce8e5334687b9f37313b6d30356e`.
- Migration commit: `d0c32e07b77a1c59bc9bab220043938b4c0d2008`.
- Sol replaced the spool pitch-circle coefficient, preserving shaft signs and
  ratios. Old/new 1.4166666666666665 mm/degree agrees across signed/multi-turn
  samples; symbolic input accepted; finite build passed.
- Faceted and exact winch suites each 5/5; root suites each 19/19. Rest and
  z=300 snapshots inspected by agent; moved snapshot also inspected by parent.
- A first import from the shop root exposed a source-only molejo namespace;
  the documented project-root invocation passed. Not a product regression.
- Commands, paths and visual limits: project `docs/rolling-travel.md`.

### InMoov

- Original declarative-api: `6de118aac8963329867e4384ce243d0b3b00094a`.
- Migration commit: `dbbb3be94d6e8326cd05b24fffb280ea3536ddb1`.
- Sol replaced five constant-moment-arm tendon terms. Finger and thumb budgets
  remain exactly 14.189526818713901 and 7.66112275162911 mm; their inverse
  closure angles remain unchanged and belong to the next helper.
- Faceted and exact hand suites each 22/22; build passed. Open/fist snapshots
  inspected by agent; fist also inspected by parent. Fixed joint-distribution
  assumptions retained; no tendon-contact or force-model claim.
- Commands and paths: project `docs/rolling-travel.md`.

### Leonardo

- Original main: `b361190ad76763a3d703a85c6583e23e95ee8096`.
- Migration commit: `87b76494fe9509b82b72468e9448a2949c908d42`.
Leonardo's rack passes 11/11 exact checks at both default module 3 and module
2.5 after using the supported `.value` escape in its declared relation.
Its loom's direct six-pose check of all eight cloth picks passes against the
independent old formula, with -2.1485917317405896 degrees giving
-0.5550000000000007 mm and -8.594366926962351 degrees giving
-2.2200000000000006 mm. The parent inspected rack and loom images.

The loom's full exact attempt spent over 22 minutes in its 289-sample
assembly-integrity test without a completed verdict. Its own
`models/automatic_weaving_loom/docs/verification.md` explicitly leaves exact
root certification outstanding at baseline, while recording complete faceted
root checks. The exact attempt is therefore not counted as passing or as a
regression. This cycle uses that established faceted root gate, including the
new direct cloth-feed test, and does not advance the gallery's broader
certification queue. The full faceted root suite passed 27/27 at zero volume
epsilon in 295.25 seconds. Project evidence: `docs/rolling-travel.md`.

### Deepseek hydraulic sawmill

- Original main: `885086c15307ddf878c719ff3f36472f35ddcddd`.
- Migration commit: `6ae7aa8429a60a11ce86f45794fa2d93688af55d`.
- Carriage drum law preserves its negative frame sign and existing ratchet
  angle. One 7.5-degree tooth at 75 mm gives 9.817477042468104 mm before sign.
- Full exact suite 10/10, including measured carriage advance/return and
  cutting-stroke interference. Mid-cycle image inspected by Sol agent.
- Existing README directory-style test invocation is rejected by the CLI;
  manifest-root invocation passes. Exact commands: `docs/rolling-travel.md`.

### Vault combination lock

- Original main: `161b9eb890629150ec6ee085abf203c6a38e9c24`.
- Migration commit: `d4019018d81209f35495e83091ce16dc21bb2507`.
- Forward pinion/rack coefficient uses the helper; start-angle/stroke inverses
  still divide by the same coefficient. Source dimensions and seats unchanged.
- Exact bolt-train suite 5/5: independently measured one-tooth travel, seats,
  stops, tooth engagement and whole-door inventory through retract/return.
- Sol inspected the partial-door/one-bolt diagnostic image; no claim to finish
  the full vault. Exact commands: `docs/rolling-travel.md`.

### Review scope

All eight consumer diffs and records were reviewed. The consumer inventory was a targeted
source search, not proof of an exhaustive catalogue: aliases such as RADIAN
required a second pass. Angle-from-travel uses belong to the next helper, pure
degree-to-radian conversions are excluded, and winding laws with varying fleet
angle must preserve their geometric correction rather than be flattened.

### Audited exclusions

A second Sol source audit found no useful `rolling_travel` replacement in
3DPrintedClocks or astrarium. Clock `simulation/shared/movement.py`,
`simulation/shared/laws.py`, and wall_clock_02/wall_clock_50 payout laws receive
authoritative chain/outer-cord-layer circumferences, sometimes divided by 720
for 2:1 reeving. Inventing radius by dividing circumference by 2*pi merely to
multiply it back obscures that contract. Astrarium's `cord_motion` is an
explicitly artificial capability fixture with no physical contact radius.
These projects are intentionally unchanged. Their other radian conversions
describe coordinates or trigonometry, not tangent travel.

## Completion

No unresolved helper regression remains. Thor's reproduced baseline failures,
the loom's pre-existing exact-certification gap, and the rejected historical
CLI invocations are explicitly retained above. Main specs now include rolling
travel and require the installed distribution's complete declared public API.
The cycle is archived for local fast-forward integration; the next helper must
not begin until the package and these eight consumer commits are verified on
their original integration branches. No push or publication is authorized.
