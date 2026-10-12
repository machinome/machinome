# Running time-drive implementation evidence

20 September 2026. Viewer-owned implementation under the pilot's explicit
“Implement viewer support next” instruction. Planning commit `5dcbf4d` records
the scope; this does not claim a separate pilot review of the generated plan.
Consumes framework content `0ce71cd` and Astrarium project content `d736826`.
No framework code, shop code, historical CAD, publication or remote was changed.

## Red before green

- New producer-corpus replay and malformed-document tests initially reported
  **19 failures / 3 passes**: the previous loader rejected the explicit clock
  source and did not validate the new mapping contract.
- After mapping validation, execution still failed until each relation received
  an independent admitted clock path. No producer expectations were rewritten.
  Two replay-harness errors were corrected: a sequence step includes its instant
  commands' crossings as well as its advance, and reset/restore clear rings.
- Actual Astrarium browser mounting failed in both transports at the version-10
  gate with the old bundle. After execution support, browser stop/wind acceptance
  exposed a second real defect: instant winding committed in the engine but the
  paused browser still read drop 2 rather than 0.
- A worker regression first observed `issued, outcome` where the committed-bank
  notification was missing. The fix emits `issued, frame, outcome` for an instant
  move; browser readouts and pose then observe winding without another tick.
- Initial full-suite runs also identified stale API/version expectations in old
  tests. Only capability numbers changed there; old mechanical fixtures and their
  expected states remained untouched.

## Final validation

| Check | Result |
| --- | --- |
| Widget `npm test` | **1,382 passed**, 48 files |
| `npm run typecheck` | Pass |
| `npm run build` / distribution rebuild | Pass; one 800 kB bundle |
| Python `pytest -q -rs --disable-warnings` | **190 passed, 20 subtests passed, 2 skipped** |
| Sphinx `-n -W --keep-going -b html` | Pass, no warnings |
| Change and both affected baseline specs, strict validation | Pass |
| sdist and wheel build into a fresh temporary directory | Pass |
| Wheel installed in a fresh environment outside the repository | API 23, documents 1–10, existing bundle/pages and AGPL/source banner; no framework installed |
| Workspace `machinome-viewer describe` | API 23, documents 1–10, package 0.2.0 |
| Originating project's finite `machinome build` | Pass; no unsupported-document warning |
| `git diff --check` | Pass |

The two Python skips require the Curta's optional external build directory;
they are not Astrarium tests. All committed-fixture browser tests ran. Existing
dependency deprecations remain (51 warnings). Packaging also reports setuptools
data-directory warnings and npm's three moderate dependency advisories; no
dependency update or vulnerability remediation is included in this change.
The existing repository `dist/` was preserved; the dry run uploaded nothing.

## Parity and coverage

The producer's `tests/time-drive-corpus.json` is copied byte-for-byte into
`machinome_viewer/widget/src/time-drive-corpus.json`, verified with `cmp`:

`4da97d071f3d7b4764575ab1024ccfc0d1f54efe57f5821e66dd6b430a9747ed` (SHA-256).

Every recorded sequence step of all seven machines is replayed: TimeAffine,
TimeEnabled, AstrariumClock, IndependentTimeDrives, TimeRelease, MixedTimeDrive
and CurvedTimeStop, **54 steps** in total. Bank, clock, crossings, stops and
command results use the fixture's own float window and exact discrete ordering.
Restore/reset behavior is included. Existing running and clocked corpora remain
unchanged and green.

Additional cases cover malformed mappings, reserved state IDs, zero-duration
operations, nonlinear global-time retry without backlog, grouped targets,
selector-block contraction retaining original drive IDs, coherent nonlinear
downstream stops at three step sizes, and atomic refusal including history.
The unchanged operation-count checks still report Train 31.0, Clearing 471.1
and Curta carriage 5913.2 evaluations/tick.

## Actual Astrarium browser evidence

`tests/fixtures/astrarium/` contains the unmodified project document and both
referenced STL assets, not a browser-authored substitute. The document matches
the originating build by `cmp`; its SHA-256 is
`1dc6ba3f6910cae7e45a58f8b6e017aeb4b3e892e4a373da15238fcd1458f13e`.

At `dt=0.02`, in Chromium with a worker and with worker construction deliberately
refused, `tests/test_time_drive_document.py` proves:

- Mounting is paused at tick 0; only `enabled` and `wind` are inputs.
- Two seconds with no command produce shaft 2 and drop 2.
- Disable, wait and wind by 2 hold shaft 2 and restore drop 0.
- Resume reaches (3, 1), exhaustion (12, 10), then rewind/restart (13, 6).
- Restore/replay reaches (3, 3); reset returns (0, 0) and time 0.
- No browser page error occurs and canvas pixels change with retained motion.

Inspected rest/running screenshots in `tests/_shots/astrarium-*.png` show two
separate diagnostic cubes, the descending weight and consistent worker/fallback
poses. The harness widens its camera to cover the known 10 mm weight path; the
default rest fit clipped the moving weight. Generated screenshots stay ignored.
This is a nonhistorical capability fixture, not Dondi's reconstructed clock.

## Durable result

ADR-068 records the execution extension and transport correction. The public
manual documents read-only time, independent stops, retry semantics, instant
winding and stop provenance. Both affected baseline specs are synchronized;
all implementation tasks are complete. The change remains active for separate
archival. Package 0.2.0 remains unreleased; nothing was pushed or published.
