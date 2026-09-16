# Evidence: keep-the-bundle-current

Worktree `solid-node-viewer/WTs/keep-the-bundle-current`, branch
`keep-the-bundle-current`, planning commit `45a0219` over `main` `98d0347`.
Widget `node_modules` is a symlink to the primary checkout's; nothing here
ever ran `npm ci`.

## The failure, as the maker met it

The studio refused a correct document:

> `/api/sessions/.../artifacts/viewer.json` declares document version 7,
> which this viewer does not render; it renders versions 1, 2, 3, 4, 5, 6.

Measured in the live workspace before anything was changed: the editable
install's bundle, built `Sep 15 17:42`, 719,398 bytes, carried
`viewer API 15` and `[1,2,3,4,5,6]`, while `package.json` at `main`
declared `solidNodeViewerApi: 16` and `[1,2,3,4,5,6,7]` and `describe()`
reported those. Both cycles that read version 7 — `execute-the-selection`
(`5a3e1d7`) and `mirror-the-gate-guard` (`98d0347`) — were integrated. The
document was correct; the renderer was old; the message blamed the
document.

## Base measurements (task 0)

| | base |
| --- | --- |
| Python suite | **129 passed, 12 subtests, 116.58 s** |
| widget suite | **36 files, 924 tests, 55.88 s**; `npm run typecheck` clean |
| build | `dist/solid-widget.js` 723.9 kb (741,244 bytes) |
| build inputs | **77** files |
| newest-mtime scan | **median 2.88 ms**, max 3.97 ms over 20 runs |
| `npm run build` | **0.33-0.41 s** wall clock over 3 runs |

The cost numbers are what justify checking on every answer and per
development-server request: the check is milliseconds, the repair is a
third of a second and only when something changed.

### The deterministic reproduction (task 0.3)

No file is edited: build the bundle from the sources at `fff31e4`
(API 15, versions 1-6), restore `main`'s sources, ask.

```
describe()          -> apiVersion: 16, documentVersions: [1,2,3,4,5,6,7]
the bundle it names -> viewer API 15, refuses by [1,2,3,4,5,6]
newest input: src/viewer.ts  1789545088253318639 ns
bundle:                      1789545079380059872 ns   STALE
```

## Red first

| test | red, against the unchanged code |
| --- | --- |
| all of `tests/test_currency.py` (2.1, 2.4-2.6) | `ImportError: cannot import name 'currency' from 'solid_node_viewer'` |
| `ThisInstallationTest::test_the_bundle_named_carries_the_api_version_reported` (2.2) | `AssertionError: 15 != 16` |
| `ThisInstallationTest::test_the_bundle_named_refuses_by_the_versions_reported` (2.2) | `describe() reports documentVersions [1,2,3,4,5,6,7], but the bundle at .../solid-widget.js does not carry that list` |
| `test_cli.py::…::test_a_stale_bundle_exits_nonzero_with_the_reason_and_no_stdout` (2.3) | `BundleStale` propagates out of `run_describe` uncaught |
| `test_server.py` ×2 (2.8) | `AttributeError: <module 'solid_node_viewer.server'> does not have the attribute 'ensure_current'` |
| `test_capture.py` ×2 (2.9) | `AttributeError: <module 'solid_node_viewer.capture'> does not have the attribute 'ensure_current'` |
| `test_packaging.py` ×5 (2.7) | `AttributeError: 'Frontend' object has no attribute 'output_is_stale'` |

The two `ThisInstallationTest` reds are the cycle's whole point: they are
the maker's failure, stated as an assertion. They were measured with the
real bundle made stale by the reproduction above and `describe()` **not
yet** wired to `currency`.

The server and capture tests were written after their wiring and then
proved red by restoring the unwired module from `main` and re-running
them — recorded here rather than claimed as written-first.

**One guard is honestly not red**: task 2.10, that a rebuilding `describe`
writes nothing to standard output. There is no rebuild in the base code to
pollute stdout, so it was written green against the new path. It is
asserted at the unit level (`test_the_build_writes_nothing_to_standard_output`,
which pins `capture_output`) and end-to-end below.

## After

| | after |
| --- | --- |
| Python suite | **156 passed, 16 subtests, 121.72 s** (+27 tests) |
| widget suite | **36 files, 924 tests**, `npm run typecheck` clean — unchanged |
| `git status` over `solid_node_viewer/widget` and `docs/adrs` | **0 files** |

No TypeScript file, no `package.json` number and no ADR beyond the new 059
changed: the claim "this cycle changes when the bundle is built, never
what it contains" is a measurement, not an assertion.

### End to end (task 5.4)

The reproduction re-run, then the command asked:

```
stale bundle on disk:  viewer API 15
$ python -m solid_node_viewer describe
{ "apiVersion": 16, "documentVersions": [1,…,7], … }   (stdout: one object)
stderr: empty
the bundle now:        viewer API 16, [1,2,3,4,5,6,7]
```

The command repaired the installation it was asked about and answered for
the bundle it actually handed the path of.

## Deviations from the design

- **A missing bundle is left to `BundleMissing`.** `ensure_current()`
  repairs a bundle that is STALE, not one that is ABSENT. The existing
  requirement "An installation without a built bundle → the entry point
  raises and the command exits non-zero, both naming where a built bundle
  comes from" is preserved unchanged, and a fresh clone still runs
  `npm ci && npm run build` once — which it must, since a rebuild never
  installs. Deliberate, and the reason the scenario survives untouched.
- **`bundle.py` now owns one import more.** `WIDGET_DIR`, `PACKAGE_DIR` and
  `BUNDLE_NAME` moved to `currency.py` and are re-exported, so the widget
  directory is still declared once. `test_the_lookup_imports_only_the_standard_library`
  was widened by exactly `solid_node_viewer.currency`, and
  `test_currency.py` asserts that module is stdlib-only in turn, so the
  promise the test exists for is intact.
- **The rebuild is silent unless logging is configured.** `logger.info`
  names the stale bundle and the input that outdates it, but a bare
  `describe` configures no handler, so a 0.35 s pause is unexplained on a
  terminal. Library convention, and stdout must stay clean; `solid develop`
  configures logging and does report it.

## Not run, and why

- **`scripts/check-dist`.** It runs `npm ci` in the widget directory, and
  this worktree's `node_modules` is a symlink to the primary checkout's —
  running it here would empty the primary's dependencies. The wheel path is
  covered by `tests/test_packaging.py` instead. If the reviewer wants
  check-dist exercised, it belongs in the primary checkout after
  integration.
- **The shop end to end.** The workspace's editable install resolves to the
  PRIMARY checkout, so `solid viewer` here would exercise the old code.
  Proving the studio serves a rebuilt bundle belongs to integration, not to
  this worktree.

## Follow-ups for the pilot

1. **A shop already running does not re-ask.** `libresolid-studio`
   resolves the bundle once through `solid viewer` and holds it for the
   life of the shop (`floor/sessions.py:521-531`). After this change a shop
   *started* after a viewer change rebuilds before it serves; a shop
   already running keeps the path it resolved, whose file is rebuilt by the
   next process that asks, and its route re-reads the file per request — so
   a page reload is correct, but nothing makes it re-ask on its own.
   Whether the shop should re-resolve per session open is a shop-repository
   decision and was deliberately not taken here.
2. **`check-dist` could verify currency** rather than only building and
   smoking, now that staleness is a question the package can answer.
3. **ADR-059 is `Proposed`.** It needs the reviewer's acceptance, and the
   index row updated with it.

## A base that moved under the cycle

While this cycle was being implemented, viewer `main` advanced from
`98d0347` to `814ff26` (`Merge branch 'slide-and-turn-parts' into main`).
The deterministic reproduction restores sources with
`git checkout main -- solid_node_viewer/widget`, and its final run
therefore pulled eight of that cycle's TypeScript files into this
worktree — a partial slice of another cycle, without its tests, fixtures,
OpenSpec record or ADR. They reached the first implementation commit and
were removed by restoring `solid_node_viewer/widget/src` to `98d0347` and
amending; the commit now touches no file under `solid_node_viewer/widget`
at all, and the suite was re-run green at the amended state
(**156 passed, 16 subtests, 117.04 s**).

Two consequences worth carrying forward:

1. **Integration is not a fast-forward.** This branch is based on
   `98d0347`; `main` is `814ff26`. The cycles are disjoint — this one
   touches no TypeScript and that one touches no Python outside its own
   fixtures and `tests/test_direct_motion.py` — so the merge should be
   clean, but it is a merge and belongs to the pilot.
2. **The reproduction should name its base commit, not a branch.** Using
   `main` in a restore makes an experiment depend on what someone else
   integrated meanwhile. Recorded so the next cycle writes `98d0347`.
