# rolling_angle validation

## Package

Commands ran from this independent mechanics worktree with
`PYTHONPATH=/home/asa/devel/machinome-studio/WTs/mechanics-rolling-angle` and
the workspace `/home/asa/devel/machinome-studio/.venv/bin/python`.

Mechanics source SHA-256 (`rolling.py`):
`14a09ea6cee1c4af3aa2716242523253ad8b234154b4f68d6cac43868849664e`.
Dependency heads observed after package validation: framework
`0ce71cdea6cc4a2e7fd7e85dc68847daef3d34cc`, viewer
`c6df93ddd1723f1b9be0fb7e73f19d6f6c2daffa`. Record consumer dependency
heads separately if they change during the campaign.

- Red: `python -m pytest -q tests/test_rolling.py` failed collection with the
  absent `rolling_angle` export before implementation.
- Green: `python -m pytest -q`: 46 passed, 24 subtests passed. A repeat with
  framework HEAD sampled before/after passed with `0ce71cd` unchanged.
- Independent references cover signed circumference fractions, multiple turns,
  both inverse compositions, negative radius, zero-divisor refusal and
  simultaneous symbolic distance/radius evaluated against math.degrees.
- `python -m sphinx -q -b doctest -W --keep-going docs docs/_build/doctest`:
  89 examples, zero failures.
- `python -m sphinx -q -b html -n -W --keep-going docs docs/_build/html`: pass.
- `python scripts/check-dist`: wheel/sdist metadata and isolated installed
  numeric/symbolic smoke checks pass, including rolling_angle. No upload.

## Consumer evidence

### Prusa3-vanilla

- Original master `e0f0494`; migration `119a29cd66e978dde77597f74f5a748898e235a4`.
- Pulley phase stays explicitly radians-to-degrees; paid belt travel and plain
  idler travel use rolling_angle at unchanged fitted/contact radii.
- X/Y signed positions -100, -25, 0, 25, 100 mm preserve old/independent values
  within 2.274e-13 degrees. Actual deferred $t expressions agree over five
  samples within 9.095e-13 degrees. No dimensional declaration token is used.
- X and Y axis suites: 6/6 each faceted and 6/6 each exact. Root build passes.
  Sol inspected center and home-XY snapshots: routing and distinct poses remain
  coherent. Broader machine/extruder certification was not rerun; its archived
  record has three unrelated faceted displacement-check failures.
- Full commands/source identity/limits: project `docs/rolling-angle.md`.
  Framework stable at 0ce71cd. Viewer moved c6df93d -> 5dcbf4d, a planning-only
  commit; tests use exact/faceted kernels and snapshots OpenSCAD, not the viewer.

### Open Robot Actuator

- Original master `4b2c01d3d37b46ab44e67c30ba0046137779e7fd`.
- Migration `0efefe824b9099b8d3485ea77baeea5d640d0fc6`.
- Tensioner inverse coefficient is -rolling_angle(1, 5), preserving sign and
  roller datum. Old/new samples at -25, -1, 0, 1, 12.5 mm agree to floating
  precision; supported raw deferred travel expressions also agree.
- Faceted pre/post and exact final suites 14/14; build succeeds. Sol inspected
  rest/810-degree snapshots: belt routes and roller datums unchanged.
- Project `docs/rolling-angle.md` records commands, helper source hash and
  dependency heads. Final faceted check bracketed by unchanged framework
  0ce71cd and viewer c6df93d. No helper regression.

### InMoov

- Original declarative-api `dbbb3be94d6e8326cd05b24fffb280ea3536ddb1`.
- Migration `d2ad79a934eae91fd2f841016c8b4498f2d34eac`.
- Drum closure angles use rolling_angle on unchanged tendon budgets and 8.4 mm
  drum radius. Finger closure differs only in the final float bit
  (96.78571428571429 -> 96.7857142857143 degrees); thumb closure unchanged.
- Supported raw deferred travel expressions agree with independent old laws.
  Faceted pre/post and exact final hand suites 22/22; build succeeds. Sol
  inspected open/fist snapshots: hand datums and joint sharing unchanged.
- Project `docs/rolling-angle.md` records exact commands, source hash and
  bracketed final faceted check with stable framework 0ce71cd/viewer c6df93d.
  No new tendon force/contact claims. No helper regression.

### Kossel

- Original master `2ded276225b40ca8d5c6bb7969281e9b91514ba4`.
- Migration `b4fe950b16d7242cb0ca3bf9b044966ea42ddd33`.
- Loop pulley/idler conversions and actual runtime pulley_turn affine
  coefficients use rolling_angle. Pitch-line allowance, phase, sign, datum and
  inverse Affine relation remain unchanged. Ratio is bit-identical; offset
  differs by -5.82e-11 degrees. Six-height forward max difference 2.33e-10
  degrees, inverse round-trip max 7.11e-15 mm. Symbolic laws agree exactly.
- After final runtime-coefficient edits: Tower faceted 9/9, root faceted 15/15,
  root build passed. Sol inspected home/driven OpenSCAD images; they establish
  external routing/pose, not correct one-to-one belt travel (see finding below).
- Existing unrelated Effector ball-capture failure stays outside this refactor.
  Commands/dependency heads: project `docs/mechanics-rolling-angle.md`.

Parent review noticed implausibly large rotation rates and the Sol follow-up
confirmed a separate, pre-existing project bug. Kossel's carriage travels along
the belt plane's Y axis, but unchanged gt2.span_scale divides by the tangent's
X component. At a 600 mm tower the tangent is
(0.000643751945, 0.999999792792): existing scale 1553.39336496, whereas its Y
projection gives 1.0000002072. Default carriage height 340.655928 mm therefore
yields anchor 494214.93697 mm rather than the projected 318.15189283 mm.
Periodic belt geometry and wheel rotations hide this in the green tests.
The helper migration preserves old behavior; it does not certify physical
one-to-one travel. A separate red-first project change is needed to correct
anchor, wheel motion and affine relations. No silent behavior fix was made.

### Metamaquina2

- Original main `c916f9b5f09ba27faaab9225fff0cdf6342fc00c`.
- X/Y inverse laws preserve negative anchor / positive gone conventions,
  phases and fitted radii. Complementary PITCH_ARC coefficients use the already
  merged rolling_travel; these were missed consumers in the first audit.
- Independent numeric comparisons differ at most 4.55e-13 degrees. Raw symbolic
  position is retained; rolling_angle(PITCH_ARC, radius) returns one degree.
- Root exact suite 67/67 in 172.70s, including axis motion, pulley mesh, tooth
  travel and groove-per-tooth/inverse ratio checks.
- Parent and Sol inspected `_build/rolling-angle-driven-web.png` at x=90,
  y=-80, z=140. Exterior assembly and displaced axes are coherent; small or
  occluded belt contacts are established by tests, not this overview image.

### Fender Bender

- Original main `68c4c97bbe05c7532182e8ac89db07a0189291b5`.
- Wheel law is rolling_angle(-2*slack, radius), preserving both moving legs
  and rotation sign. Old truncated pi gives at most 9.095e-13 degrees difference.
  Raw symbolic slack/radius retains the expected -2*180/pi coefficient.
- Root exact suite 18/18 in 340.55s, including direct wheel/slack motion,
  solids, assembly and scenarios.
- Parent and Sol inspected `_build/rolling-angle-driven-web.png` at channel=2,
  slack=150: coherent visible exterior and channel alignment. The enclosure
  occludes much of the filament path; the image alone does not certify contact.

Both project `docs/rolling-angle-verification.md` files record commands and
source identity. Framework remained 0ce71cd. OpenSCAD snapshots failed to
render (Metamaquina also reported the existing jhead.scad parser diagnostic).
Web fallback succeeded, but the viewer was concurrently changing: HEAD moved
c6df93d -> 5dcbf4d and source was dirty. These images are visual observations,
not a claim of a pinned, reproducible viewer environment. No helper regression
was found. Final documentation-only consumer commits are recorded below.

- Metamaquina2: `70ff30ed8af7617fa74a562de47234cdb7c35dea`.
- Fender Bender: `bff1174b6c3dae0d9fc6fd00cb96c20fd9df61a0`.

All six consumer diffs and evidence records were reviewed. Baseline mechanisms
specification contains the complete added requirement. Strict validation and
diff hygiene passed before archival. Local fast-forward integration follows
the completed-cycle commit; its exact commit and verified branch results are
recorded in the next cycle's campaign ledger.
