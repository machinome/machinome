# Contact-referenced pulley angle validation

## Package

Planning commit `2e73354b5adb62bde3462302537edd0fca2e22ab`.
Tested uncommitted `machinome_mechanics/belts.py` SHA-256:
`c5f170dee942172dba37eb5b3d8d43f182f263e52c5c2c43331f8bb3427664ed`.
Commands ran from this worktree with `PYTHONPATH="$PWD"` and workspace Python.

- Red: `python -m pytest tests/test_belt_pulley_angle.py -q` failed collection
  specifically because the helper import did not exist, before implementation.
- Green focused suite: 12 passed. Full `python -m pytest -q`: 109 passed,
  24 subtests passed.
- Tests cover reference station, signed multiple turns, both senses, an
  independent no-slip arc identity, shifted path origins, negative/zero radius,
  defaults and simultaneously deferred position/radius/contact/station operands
  at five samples against independent math.degrees arithmetic.
- `python -m sphinx -q -b doctest -W --keep-going docs
  /tmp/mechanics-pulley-angle-doctest`: 116 examples, no failures.
- `python -m sphinx -q -b html -n -W --keep-going docs
  /tmp/mechanics-pulley-angle-html`: passed.
- `python scripts/check-dist`: wheel/sdist strict metadata and installed
  numeric/symbolic smoke passed outside checkout; nothing uploaded.
- `git diff --check` and `openspec validate --all --strict`: passed.

Dependencies observed clean after package checks: framework
`8d2bd71171be81f13ba5dd492851ed8b3a9ababb`, viewer
`4355da1a7f64dacd7d86eb27dbdfdf7ced94598f`.

Independent Sol review reran 12 focused tests and found no substantive issue.
It checked the contact/station zero, sense conventions, unwrapped behavior,
deferred arithmetic and the boundary leaving fitting/mounting/Affine to callers.
Thor is not migrated for this helper: its tooth-ratio coupling is not a
contact-station calculation, and no consumer is manufactured for coverage.

## Consumer review

Prusa3-vanilla, Kossel and Metamaquina2 migrations reviewed and validated.
Local integration follows the completed-cycle commit.

### Prusa3-vanilla

- Original master `95f575c45c8fa5dc1f8c63bd1df3a1b1ef54103e`;
  migration `45a371a398b53f8eda024fe061ba19ce8e7389c2`.
- Loop.pulley_angle delegates anchor, fitted pitch radius, measured degree
  phase and pulley station to the helper. Fitting, outer mounting transforms
  and plain-idler rolling remain unchanged.
- Parent reviewed source, complete docs/mechanics-belt-pulley-angle.md and
  runnable scripts/check-belt-pulley-angle, then reran it. The old independent
  phase-minus-arc law matches actual fitted X/Y loops at six signed/unwrapped
  positions and six actual Solid2 time samples within absolute 1e-10 degrees.
- Faceted and exact X/Y suites each pass 6/6; root build passes. Sol and parent
  inspected fresh _build/belt-pulley-angle-driven.png at x145/y65/z70. Visible
  routes and assembly remain coherent; the overview does not certify tooth
  contact. No new issue; dependencies clean/stable at 8d2bd71/4355da1.

### Kossel

- Original master `5c720a6a2ece81ec3f9b8a96fe67c8953a3f5125`;
  migration `bc255795777d67ba910c52d4666442d580a3f1e8`.
- Loop phase uses the helper; pulley_turn remains an invertible Affine with
  its old single rolling-angle slope and helper-derived constant offset.
  Radius fit, idler law, mounting and known axis-projection defect unchanged.
- Parent reviewed source, docs/mechanics-belt-pulley-angle.md and asserting
  scripts/check-belt-pulley-angle, and reran the probe. Tower heights 500/600/700
  retain direct angle values; affine forward discrepancy <=1.863e-9 degrees
  on multi-million-degree values, inverse roundtrip <=7.106e-15 mm. Actual
  deferred expressions match the old numeric law at five time samples.
- Tower/root faceted 9/9 and 15/15, build passes. The known exact Effector
  failure is outside this gate. Parent and Sol inspected the fresh x60/y-40/z120
  overview in _build/belt-pulley-angle-driven.png: coherent visible routes and
  pose, not proof of physical travel or tooth contact.
- Initial portable-shebang probe launch selected system Python and failed to
  import machinome; the explicit workspace-Python invocation passes. Stable
  clean dependency heads 8d2bd71/4355da1. No helper issue found.

### Metamaquina2

- Original main `bd56d5211311ef4449f94c975a45190688ee430b`;
  migration `69c4f5a4e811b6f33b6224d550de407e194d1d6c`.
- X supplies its anchor and phase; Y supplies the global clamp station,
  pulley contact station and counterclockwise sense. Fitted radii, positive
  numeric phase workaround, clamp mapping and mounting transforms remain.
- Parent reviewed source, complete docs/belt-pulley-angle-verification.md and
  docs/probes/belt_pulley_angle.py, then reran its independent legacy numeric
  and evaluated actual Solid2-expression comparisons. Five signed positions
  spanning multiple turns pass at 1e-12 numeric and 1e-10 deferred tolerance.
- Full exact suite 67/67 in 358.46 seconds; warm build passed in 17.65 seconds.
  Existing jhead line-107 diagnostics and FilamentSpoolHolder warning remain.
- Sol and parent inspected fresh _build/belt-pulley-angle-driven-web.png at
  x90/y-80/z140: coherent assembly and routes, not a tooth-contact certificate.
  Framework/viewer stayed clean at 8d2bd71/4355da1. No helper issue found.

## Completion

All three consumer commits are ready for local fast-forward integration.
The final package suite was repeated: 109 tests and 24 subtests passed.
Baseline synchronization, strict validation and archival are checked before
the implementation commit; local merges and post-merge checks are recorded
in the following campaign-ledger update. No push or publication is authorized.
