# Pulley pitch radius validation

## Package evidence

Planning base: `4870f32379fc9e0c966a0466a7a84f1ce4743ae5`.
Uncommitted tested `machinome_mechanics/belts.py` SHA-256:
`63f8d30a19d36b2cc4504919d6e3b989df1c0092348ad4c1930b31adb4ea482d`.
Commands run from this mechanics worktree with `PYTHONPATH="$PWD"` and
`/home/asa/devel/machinome-studio/.venv/bin/python`.

- Red: `python -m pytest -q tests/test_belts.py` failed collection because
  the public pulley_pitch_radius did not yet exist.
- Green: `python -m pytest -q`: 57 passed, 24 subtests.
- Independent circumference checks cover 117-tooth GT2, 10/30-tooth AT3 and
  fitted printer pitch, one-tooth rolling travel and angle identities, explicit
  pitch versus surface radius, zero/signed/fractional arithmetic, and raw
  symbolic count/pitch evaluated at five values.
- `python -m sphinx -q -b doctest -W --keep-going docs docs/_build/doctest`:
  96 examples, zero failures.
- `python -m sphinx -q -b html -n -W --keep-going docs docs/_build/html`: pass.
- `python scripts/check-dist`: wheel/sdist metadata, installed exports and
  numeric/symbolic smoke checks passed outside the checkout. No upload.

Observed dependency heads after package checks: framework
`0ce71cdea6cc4a2e7fd7e85dc68847daef3d34cc` (clean), viewer
`5dcbf4d476ff0d34bb42fe13f9b799ebd8ec5852` (concurrent dirty source).
These are observations, not a frozen dependency environment.

## Audit boundaries

A follow-symlinks source search identified six established consumers: Thor,
Actuator, Hangprinter, Prusa3-vanilla, Kossel and Metamaquina2. Independent
test arithmetic remains an oracle, not a migration target. Dutch-windmill-2's
legacy belt demonstrator is an additional validated consumer.
Vault's rack pinion and dutch-windmill-3's pin gears use the same circumference
identity but are not pulleys; this cycle does not rename their mechanics merely
to increase its consumer count. The search encountered two dangling links in
roboto_origin's vendored OS tree and is not claimed as exhaustive.

## Consumer validation

### Prusa3-vanilla

- Original master `119a29cd66e978dde77597f74f5a748898e235a4`.
- Migration `b8212ccfc613ac1cae4c11d344862b07aa6ab894`.
- Public flank radius and internal groove passage use the helper, preserving
  fitted period and PITCH_LINE subtraction. Independent arithmetic is unchanged.
- Five counts (1, 16, 18, 20, 117) and four pitches (1.9992, 2, 2.5001, 3)
  match old radii exactly, including flank offset. Raw deferred count/pitch
  expressions match at five samples.
- X/Y faceted suites 6/6 each, X/Y exact suites 6/6 each, root build passed.
  Sol inspected center and home-XY OpenSCAD images; parent inspected home-XY.
  Visible routing and poses are coherent; overview pixels alone do not certify
  all tooth contacts. Full commands: docs/mechanics-pulley-pitch-radius.md.

### Kossel

- Original master `b4fe950b16d7242cb0ca3bf9b044966ea42ddd33`.
- Migration `44d9349a64386c1099cbf5cd660770b7d86a3435`.
- Same two natural pitch-radius uses as Prusa; same independent parameter
  matrix and deferred comparisons pass with zero numeric error.
- Tower faceted 9/9, root faceted 15/15, root build passed. Sol inspected home
  and driven OpenSCAD images; parent inspected driven (x=60,y=-40,z=120).
  Existing anchor-axis projection error is unchanged and limits physical
  travel claims. Unrelated Effector ball-capture failure was not rerun.
- Commands and limits: docs/mechanics-pulley-pitch-radius.md.

Both above: framework stayed 0ce71cd. Viewer advanced from dirty 5dcbf4d
to clean 4355da1a7f64dacd7d86eb27dbdfdf7ced94598f; their geometry tests and
OpenSCAD images do not use that viewer. Parent reviewed both source diffs and
evidence records; no helper regression found.

### Open Robot Actuator

- Original master `0efefe824b9099b8d3485ea77baeea5d640d0fc6`.
- Migration `d099c03d772a2a6d944402a9b9e5ca28f7488b40`.
- Both AT3 pitch radii use the helper. Four independent count/pitch pairs
  match exactly, including nondefault sizes; raw deferred pitch is preserved.
- Faceted pre/post 14/14, exact 14/14, root build passes. Sol inspected rest
  and input_angle=810 snapshots; parent inspected the latter. Visible routes
  and stations remain coherent, with no force/contact certification implied.
- Full commands, source identity and dependency observations:
  docs/pulley-pitch-radius.md. Framework stable 0ce71cd; viewer changed
  independently 5dcbf4d -> 4355da1 (not used for these OpenSCAD images).

### Hangprinter

- Original version_4 `d0c32e07b77a1c59bc9bab220043938b4c0d2008`.
- Migration `2cc703793e9029e19313b22a00472be030173e69`.
- Flank radius and groove passage use helper; fitted period and 0.254 mm
  surface offset unchanged. Old/new comparisons match exactly for 20/255
  teeth at nominal 2 mm and actual fitted 1.9978496683445934 mm pitch, plus
  7 teeth at 2.5 mm. Raw deferred pitch retains the same law.
- Pre/post faceted and final exact suites: winch 5/5, root 19/19. Build passes.
  Sol inspected rest/z=300 images; parent inspected raised mover. Overview
  establishes visible whole-machine pose, not detailed groove contact or
  tension/elasticity. Full commands: docs/pulley-pitch-radius.md.
- Same observed framework/viewer heads as Actuator. Parent reviewed diff and
  evidence, including the clarified limit that kinematic/geometry contracts
  do not certify tension or elasticity.

### Thor

- Original main `c3c543d7d73d84f5ff47da326ebc436660cae6cb`.
- Migration `d57ae064b94a2f9bc580a7d66eb27af0e96b80f7`.
- Flexibles wrapper and PulleyGT2 derived radius use the helper. The latter
  passes teeth.value, retaining parameter dependence and 0.254 mm tip offset.
- Six tooth counts (8,20,40,60,117,121) preserve numeric radii exactly. Raw
  symbolic old-minus-new simplifies to zero. Actual nondefault pulley renders
  at 40/60/117/121 teeth have diameters 24.956790895, 37.689186342,
  73.976513367 and 76.522992456 mm; derived Count behavior is preserved.
- Compilation and full root build pass. Exact root suite 31/33, with all
  belt-specific checks passing; only the two established full-machine overlap
  failures persist (260/272 unexpected pairs, same first pair at 2093.029 mm3).
- Sol inspected home/driven OpenSCAD images, parent inspected driven. Belts
  are enclosed: only exterior pose coherence is visually established.
- Source/dependency identity and commands in docs/mechanics-pulley-pitch-radius.md.
  Framework stable 0ce71cd; concurrent viewer 5dcbf4d -> 4355da1 not used by
  these OpenSCAD images. The full documented nondefault geometry probe was
  rerun successfully after parent requested a runnable reproduction.

### Metamaquina2

- Original main `70ff30ed8af7617fa74a562de47234cdb7c35dea`.
- Migration `a652e8369551c540cd5dd71d82c34af28cf4080a`.
- Flank and groove-passage pitch radii use helper, retaining fitted period and
  surface offset; inverse count calculation remains independent.
- Twelve nondefault count/pitch pairs match old values exactly; raw symbolic
  arguments retain both symbols. Root exact 67/67 in 453.23s, including bought
  radius, X/Y mesh, tooth travel and groove tests. Existing jhead.scad parser
  diagnostic repeats without failing the established suite.
- Parent and Sol inspected driven web image (x=90,y=-80,z=140): coherent
  exterior. Contacts are too small to establish visually. Commands/limits:
  docs/pulley-pitch-radius-verification.md.

### Dutch Windmill 2

- Original main `784c79e1cee992cfd833d3733c4a5c581d628233`.
- Migration `45f3700584859ec419a79615a4cee18ddea43fd2`.
- Pulley constructor and BeltLoop driver/driven radii use helper. All offsets,
  tooth counts, centers and motion ratios remain unchanged.
- Exact baseline 15/15 in 24.15s; after migration 15/15 in 23.61s, including
  drive ratio, nonaccumulating pose, clearance and envelope contracts. Six
  legacy render-time FutureWarnings unchanged; no API modernization attempted.
- Twelve count/pitch pairs match exactly; symbolic count/pitch remain deferred.
  Parent and Sol inspected web t=.375 image: coherent exterior; guard hides
  belt/pulley contacts. Full commands: docs/pulley-pitch-radius-verification.md.
- Pre-existing untracked screenshot.png preserved and never staged.

The two web consumers report framework stable 0ce71cd, viewer changing from
dirty 5dcbf4d to 4355da1. Their images are observations, not a pinned renderer
reproduction. All seven final source diffs, evidence records and representative
images were reviewed. No helper regression remains; unrelated known failures
and legacy warnings are explicitly retained. Final package repeat passed
57 tests plus 24 subtests with framework HEAD bracketed unchanged at 0ce71cd.

The baseline contains the complete added requirement; strict OpenSpec and diff
hygiene checks passed before archival. Local fast-forward integration follows
the completed-cycle commit, with exact results entered in the campaign ledger
when the next cycle opens.
