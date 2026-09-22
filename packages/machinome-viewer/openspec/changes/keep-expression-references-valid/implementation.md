# Implementation evidence — 22 September 2026

Pilot ratification is recorded in planning commit `85a9599`. This repair
belongs to the viewer repository. The framework and Curta mechanism are
not changed by it; Curta seat integration is the independent project
checkpoint `1fc3e00`, not part of this viewer change.

## Reference audit

| Holder / boundary | Lifetime after repair |
| --- | --- |
| Shared intern store, memo, free-name cache | Reset together, before outer synchronous work or after final disposal |
| `BindingTable.roots()` | Whole map prepared in one scope, generation-qualified between uses |
| Running/clocked `nodeOf` | Shared source-to-root cache, no second stale map |
| Program load, classification and block folding | Root/table acquisition and traversal in one load scope; later active-read folds scope themselves |
| Stored kink levels | Original source, postorder index and generation; refreshed inside `kinkLevel` before both operands are consumed |
| `LevelPaths` and retained-path readers | `ExpressionPath` reconstructs raw `PathValue` from source and original standing values; tick scopes prevent repeated rebuilding within a tick |
| Running integration and clocked requests | One synchronous scope per complete operation, released on errors |
| Pose scopes, tree update, operations matrices | Document-local lazy roots, acquired in a coherent evaluation/update scope |
| Reconciliation | Compare old/new document maps in one scope after asynchronous asset preparation; never hold a scope over `await` |
| Shapes, binding closure, free-name sets | No node IDs; safe across generations |

`prepare` and last-mount `releaseExpressions` are the reset entry points.
The former nests within the complete caller operation; the latter defers
disposal until the outer operation ends if necessary. The trigger stays
50,000. No retry-until-fit loop, per-document store, session pin or numerical
algorithm change is introduced. Low-level raw-node walkers remain internal
operation-local helpers, not a host API.

## Red-first evidence

`npm test -- --reporter=dot src/expression-lifetime.test.ts` before the fix:

- Multi-entry map, threshold 5: **21 received, 11 expected**, proving an
  existing integer silently referred to the wrong node, not only a missing ID.
- Root-before-binding classification: `Cannot read properties of undefined
  (reading 'kind')` in `shapeOf`, reproducing the Curta load failure.
- Retained kink after index reuse: the same missing-node error in `kinkLevel`.

After fixing those, two additional regressions were added before their
repairs: retained pose scope failed in expression evaluation, and held path
failed in `PathValue.at`. Both now pass. The path test changes a standing
input at a later point, proving rebuilding binds the original piece rather
than silently choosing the new point's standing values.

The ten new tests also cover nested scopes, exception cleanup, deferred
final disposal, two live documents with identical binding names, 60 bounded
replacements interspersed with malformed replacements, running replay,
all 30 clocked corpus machines under pressure (including kinked cases), and
tree reconciliation with changed binding dependencies. No existing numeric
expected value or malformed-document refusal was altered.

The bounded replacement test retained at most **32 nodes** after each
iteration (threshold 5), with zero after final disposal; it uses both live
documents again after each failed replacement, so reclamation is not bought
by abandoning the last good model.

## Validation

Initial complete widget run: 51 files / 1,418 tests pass, before the final
five added coverage cases. Initial Python/browser run: 191 passed, 2 skipped,
20 subtests passed, 51 existing deprecation warnings (202.43 seconds).
The skips are optional Curta drawing exports absent from that test's default
path, not successful coverage. The final Python run supplies their actual
workspace path to exercise them as well.

An overlapping rerun is **not green**: the widget suite had 1,422 passes,
one wall-clock cost failure (529 versus the existing >900 ticks/s requirement)
and a Vitest worker RPC timeout. The concurrent Python suite had 190 passes,
one browser timing failure (a fourth animation frame already reached the
end of a 0.2-second gesture), two skips and 20 passing subtests. Two large
Curta acceptance browsers were active during this run. No expectation was
changed; uncontended reruns are the completion gate, and the failed logs
remain `/tmp/viewer-lifetime-suite-final.log` and
`/tmp/viewer-lifetime-python-final.log`.

After both large-browser probes ended, the unchanged complete widget suite
was rerun with `--maxWorkers=1`: **51 files, 1,423 tests pass**, 61.73 seconds.
Typecheck and the uninstrumented bundle build pass. The new focused suite is
10/10. The unchanged Curta performance assertion passes at **1,101 ticks/s**.

The first serial Python run exercised both optional Curta drawing tests and
passed all runtime/browser checks: 192 passed, one documentation failure.
That failure caught this change's unnecessary new `Unreleased` changelog
section conflicting with the release-record test. The published changelog
was restored unchanged; this OpenSpec record and the ADR amendments describe
the unreleased repair. All seven documentation tests then passed, with no
test expectation changed.

Final full serial Python/browser run: **193 passed, zero skipped, 20 passing
subtests**, 270.46 seconds, 51 existing deprecation warnings. Command:

```sh
MACHINOME_CURTA_BUILDS=/home/asa/devel/machinome-studio/projects/Calculators/Curta-Type-I-3x/_build /home/asa/devel/machinome-studio/.venv/bin/python -m pytest -q -rs
```

Logs: `/tmp/viewer-lifetime-suite-serial.log`,
`/tmp/viewer-lifetime-typecheck.log`, `/tmp/viewer-lifetime-build.log`,
`/tmp/viewer-lifetime-python-complete.log`. No Python performance change,
version bump, release, push or publication occurred. The spec sync/archive
confirmation was asked while validation ran; pending the pilot's answer,
the fully tested implementation is checkpointed with this change still active.

Initial full Curta run: **passed**, all four cases, no page errors, full
eighth-station stopped/relieved banks equal Python exactly (4 × 213 values).
The initial/idle banks are equal. Bundle SHA-256
`cb3e343ba9a74b107ca16c1014adb97860f376a90074b7c312e6959a1712c3eb`;
mount 16.633 s, first idle step 0.514 s, first move 1,267.2 ms. The mounted
calculator screenshot was inspected.

### Final public-bundle Curta acceptance

**Passed** for bundle SHA-256
`20880099c6490adca932f7152c987751a645dddd1bf089ff197342db3c81727c`.
The document/program identities remain unchanged. Mount 28.334 s, first
idle step .737 s, first move 1,666.9 ms; its initial portion overlapped the
other validation workloads, so these are observations, not performance
targets. Initial/idle banks are identical and all four cases below passed
blocked motion, exact snapshot replay, admitted .05° relief and blocked retry:

| Station | Target | Crank stop |
| --- | ---: | ---: |
| Hundreds | 190° | 165.22323837279146° |
| Hundreds | 880° | 165.22323837227304° |
| Eighth | 290° | 265.22323837279146° |
| Eighth | 980° | 265.22323837227304° |

No page errors. Both eighth stopped/relieved pairs equal Python exactly,
four complete states of 213 coordinates each. Both station screenshots
were inspected (assembled geometry, markings, crank pose and displayed
request state); pixels do not substitute for the numeric comparison.

Project command:

```sh
python -m simulation.tools.result_bank_operating_browser --build _build_result_bank_repaired_2026_09_22 --python-report simulation/docs/evidence/result-bank-eighth-python-acceptance-2026-09-21.json
```

The complete numeric evidence stays in its originating project at
`simulation/docs/evidence/result-bank-browser-acceptance-2026-09-22.json`,
SHA-256 `ca8a84e07b330cf70964d8126b8804709d1f922fbf0893f297c68508ef646b39`.
The report validator also rejects partial initial/idle banks (red first,
5/5 green), and revalidates this saved report against the Python oracle.
No Curta source geometry or export asset is copied into the viewer package.

The original Curta export hash and program identity remain those in
`evidence.md`. Public-bundle acceptance uses the project-owned
`simulation.tools.result_bank_operating_browser`, extended only to record
mount/first-step timings and compare initial/idle banks. It still exercises
hundreds/eighth short/long stops, exact replay, relief and retry and exact
213-coordinate bank comparison wherever Python evidence exists. Python
full-bank evidence is available for the eighth station only; hundreds has
recorded stop angles and project geometry tests, not a captured full-bank
Python oracle.

Separate source-only census (NOT a replacement for public-bundle acceptance):

```sh
cd machinome_viewer/widget
./node_modules/.bin/esbuild tools/expression-pressure.ts --bundle --platform=node --format=esm --outfile=/tmp/viewer-expression-pressure.mjs
node /tmp/viewer-expression-pressure.mjs /home/asa/devel/machinome-studio/projects/Calculators/Curta-Type-I-3x/_build_result_bank_trial/manifest.json
```

Program-load peak **94,854 nodes**; retained after idle **62,610**; after
posing **59,110** (2,713 expressions); after final disposal **0**. The peak
counter is numeric test-only telemetry, not retained nodes or a host option.
Measured source program-load time was about 1.05 seconds, excluding assets,
DOM and WebGL. Browser mount timings measure a different operation. No
Python performance or arbitrary-size-memory guarantee is claimed.
