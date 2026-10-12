## 0. The base, measured before anything changes

- [x] 0.1 Base: worktree `solid-node-viewer/WTs/keep-the-bundle-current`,
      branch `keep-the-bundle-current` at `98d0347` (`main`), widget
      `node_modules` symlinked to the primary checkout's (never installed
      from here). Python suite: **129 passed, 12 subtests, 116.58 s**.
      `npm run build` → `dist/solid-widget.js` 723.9 kb (741,244 bytes).
- [x] 0.2 The failure as the maker met it, from the live workspace: the
      editable install's bundle, built `Sep 15 17:42` (719,398 bytes),
      carried `viewer API 15` and `[1,2,3,4,5,6]` while `package.json` at
      `main` declared `solidNodeViewerApi: 16` and `[1..7]`; the studio
      refused a version 7 document and blamed the document.
- [x] 0.3 Deterministic reproduction without editing a file: build from
      the sources at `fff31e4`, restore `main`'s sources, ask.
      `describe()` → `apiVersion: 16`, `documentVersions: [1..7]`; the
      bundle it names → `viewer API 15`, refuses by `[1,2,3,4,5,6]`.
      This is the reproduction the red tests of §2 encode.
- [x] 0.4 Cost, so the design can afford a check on every answer: **77**
      build inputs, newest-mtime scan **median 2.88 ms** (max 3.97 ms over
      20 runs); `npm run build` **0.33-0.41 s** wall clock over 3 runs.

## 1. Ratification

- [x] 1.1 `openspec validate keep-the-bundle-current --strict` green.
- [x] 1.2 ADR-059 drafted — the viewer keeps its own bundle current, builds
      but never installs, and refuses what it cannot repair. Numbered 059
      because 055 is held by the in-flight `slide-and-turn-parts` cycle.
      Proposed status until the reviewer accepts it.

## 2. Red first: the drift, proved against the current code

Each test in this section MUST be run against the unchanged code and MUST
fail for the stated reason before §3 begins. Record the failure text.

- [x] 2.1 `tests/test_currency.py`: a checkout whose newest widget source is
      newer than its bundle is STALE, and one with no source newer is
      CURRENT — over a temporary checkout-shaped tree, comparing
      `st_mtime_ns` integers, equal times counting as current.
      Red because there is nothing to import.
- [x] 2.2 The reproduction of 0.3 as a test: with a bundle built from an
      older declaration, `describe()`'s `apiVersion`/`documentVersions`
      DISAGREE with the ones the bundle at its own `path` carries.
      Red because today they disagree and nothing objects; green when the
      answer is given only after the rebuild.
- [x] 2.3 A stale bundle that cannot be rebuilt: dependencies absent →
      the entry point raises `BundleStale` naming the bundle, the newer
      input, the reason and the remedy; `describe` exits non-zero with
      empty stdout. Red: today it answers zero and prints a wrong answer.
- [x] 2.4 The never-install guarantee: a rebuild driven with a recording
      stub for the build program runs the BUILD argv only — no `ci`, no
      `install` — and the widget's dependency directory is untouched.
      Red because there is no rebuild path at all.
- [x] 2.5 Concurrency: two threads finding the same bundle stale produce
      exactly ONE build invocation, both observe a current bundle, and no
      caller reads a partially written file. Red for the same reason.
- [x] 2.6 An installed distribution: a tree with the bundle and
      `package.json` but no `src/` and no `build.mjs` is current without
      scanning, never rebuilds, and never looks for npm. Red because
      there is no such classification.
- [x] 2.7 `tests/test_packaging.py`: a checkout whose bundle is STALE gets
      it rebuilt before a wheel is assembled. Red because
      `build_missing_frontends` builds only what is absent.
- [x] 2.8 `tests/test_server.py`: a bundle request after a source changes
      under a running server serves the rebuilt bundle; a stale bundle
      that cannot be rebuilt answers unavailable with its reason on both
      `/_viewer/bundle.js` and `/_viewer`. Red on both counts today.
- [x] 2.9 `tests/test_capture.py`: a capture whose bundle is stale copies
      the rebuilt bundle into staging, and one that cannot be rebuilt
      fails writing no image. Red today.
- [x] 2.10 stdout hygiene: `describe` that rebuilds prints exactly one JSON
      object and nothing the build wrote. Red is not available honestly
      here (no rebuild exists to pollute it); record it as a guard written
      green against the new path, and say so rather than claiming a red.

## 3. The currency module

- [x] 3.1 `solid_node_viewer/currency.py`, standard library only, importable
      without cost: `is_source_checkout()`, `build_inputs()`,
      `newest_input_ns()`, `is_stale()`, `ensure_current()`, and
      `BundleStale`. Inputs per design D2; `node_modules` excluded.
- [x] 3.2 `ensure_current()`: return immediately when not a source checkout
      or not stale; otherwise take the `dist/.build.lock` exclusive lock,
      RE-CHECK staleness, run the build with output captured, and raise
      `BundleStale` with the tail of that output when it fails (D5-D7).
      Unlocked fallback where `fcntl` is unavailable, logged.
- [x] 3.3 The build invocation is `npm run build` in the widget directory
      and nothing else — the never-install rule of D4 stated in the code
      and in a comment that says why, with the emptied-`node_modules`
      incident named so a later change does not "helpfully" add `npm ci`.
- [x] 3.4 `BundleStale` message: the bundle path, the newest input and its
      time, the reason the rebuild did not happen, and the remedy.

## 4. The four exits

- [x] 4.1 `bundle.describe()` calls `ensure_current()` before it reads the
      declaration. `bundle_path()` and `has_bundle()` stay pure (D3).
- [x] 4.2 `cli.run_describe` reports `BundleStale` on stderr and exits
      non-zero, as it already does for `BundleMissing`, keeping stdout empty.
- [x] 4.3 `server.py`: the `/_viewer/bundle.js` route and the `/_viewer`
      status route make the bundle current per request and report a stale
      unbuildable bundle the way they report an absent one.
- [x] 4.4 `capture.py`: make the bundle current before copying it into
      staging; a `BundleStale` becomes a `CaptureError` that writes no image.
- [x] 4.5 `packaging.py`: `build_missing_frontends` → `build_stale_frontends`,
      using `currency`'s comparison; the sdist path still builds
      unconditionally.

## 5. The suite, the types and the build

- [x] 5.1 Python suite green against the 0.1 baseline, with the new totals
      recorded. Expect the count to rise by §2's tests only.
- [x] 5.2 The widget suite and typecheck are NOT expected to change — no
      `src/` file is touched — but run `npm run typecheck` and `npm test`
      once and record the numbers, because the claim "the bundle's content
      is untouched" is worth one measurement rather than an assertion.
- [x] 5.3 Confirm by diff that no file under `solid_node_viewer/widget/src/`,
      no number in `package.json`, and no ADR other than the new 059 changed.
- [x] 5.4 End-to-end, in this worktree: reproduce 0.3 again, then ask
      `describe` and record that it now answers `apiVersion: 16` with a
      bundle at its `path` that carries `viewer API 16` and `[1..7]`.
- [x] 5.5 `scripts/check-dist` is NOT run: it runs `npm ci` in the widget,
      and this worktree's `node_modules` is a symlink to the primary's, so
      running it here would empty the primary's dependencies. Record that
      the wheel path is covered by 2.7 instead, and leave check-dist to the
      primary checkout if the reviewer wants it.

## 6. The record

- [x] 6.1 `CHANGELOG.md` under `0.2.0 — unreleased`: the bundle is kept
      current with its sources in a source checkout, a stale bundle that
      cannot be rebuilt is refused rather than served, and a wheel is no
      longer cut from a stale bundle.
- [x] 6.2 `README.md` "Working on the viewer": the manual
      `npm run build` step is no longer the thing standing between an edit
      and a correct answer — say what is automatic and what still is not
      (dependency installs).
- [x] 6.3 `evidence.md`: §0's measurements with their after numbers, each
      red test's failure text, and the follow-ups — the shop's cached
      bundle path (non-goal here), and whether `check-dist` should verify
      currency in the primary checkout.
- [x] 6.4 `openspec validate --strict` green; archive left for the reviewer,
      as the previous cycles left it.
