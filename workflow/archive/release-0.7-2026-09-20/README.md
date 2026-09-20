# Machinome 0.7 release preparation

Date: 2026-09-20. Status: local release preparation; publication pending.
The pilot authorized direct release maintenance, commits and local integration,
and explicitly directed completion of the existing mechanics extraction.

## Release set

| Distribution | Version | Contract |
| --- | --- | --- |
| machinome | 0.7.0 | Apache-2.0; successor to solid-node 0.6.0 |
| machinome-viewer | 0.2.0 | AGPL-3.0-only; API 22, document schemas 1–9 |
| machinome-mechanics | 0.1.0 | Apache-2.0; twelve helpers; machinome >=0.7.0 |

Framework base: `6954e7cff5aa7a541efd68ece8d784e6831fc79b`.
Viewer source: `8efe10f` (runtime unchanged from `038f74d`).
Mechanics source: `8a05bd4` (runtime unchanged from `2605bcf`).
Framework changes were made on `prepare-0-7-release` in its isolated bench.

## Corrections and evidence

- Framework bump configuration and Sphinx version now agree with package 0.7.0.
  Current compatibility guidance names viewer API 22 and schemas 1–9.
- The original mechanics extraction (`b4eb460`, followed by the extra in
  `08ba6a9`) never reached main. The pilot directed its completion. The duplicate
  framework modules and their transferred formula tests are removed; boundary
  tests and the mechanics-distribution spec take their place. The former
  framework formula spec is preserved beside this report. ADR-132 records the
  resulting ownership without overwriting main's unrelated ADR-101.
- The extraction boundary test failed on the existing
  `machinome.mechanisms` package before removal and passes afterwards.
- A fresh installation selected ocp-gordon 0.3.1, which imports
  `OCP.collections`; the pinned OCP 7.8 does not have that module. The existing
  development environment concealed this because it had ocp-gordon 0.2.2.
  Bounding ocp-gordon to `>=0.2.2,<0.3` fixes the fresh install without
  changing the selected CAD backends. Both exact backends produce a 24 mm³
  2×3×4 box in the isolated environment.
- The documentation pinned pre-rename V8 and Metamaquina sources. Their
  existing migrated project commits are now pinned:
  V8 `fdf624b9d07831bda6baa690dfa7d6bf3aef400c`,
  Metamaquina `c916f9b5f09ba27faaab9225fff0cdf6342fc00c`.
  Clock 01 keeps `b089545bfcb8bbb507e480c6381010cd8281fb89`.
  No mechanical project source was edited. Documentation environments install
  this framework and the independent mechanics package before exporting V8.

## Validation

Linux, Python 3.12, Node 24.11.1. Checks below used the release worktree or
installed distributions outside the source trees, as stated.

- Framework final suite: **3,406 passed, 1,981 subtests passed, four skips**.
  The opt-in web snapshot test passed separately. Remaining skips: JSCAD CLI
  unavailable and two optional vendor-STEP fixture tests.
- Framework release/docs/boundary focused checks: **17 passed, 40 subtests**.
- Viewer Python/browser suite: **181 passed, 18 subtests, two skips** for
  external Curta measurements; all 1,243 widget tests and typecheck pass.
- Mechanics against the extracted framework: **30 passed, 24 subtests**.
- All **34 framework baseline specs** pass strict OpenSpec validation.
- All three wheel/sdist pairs build and pass `twine check --strict`.
- Fresh combined installation of
  `machinome[viewer,mechanics,web-snapshot]==0.7.0` using the local artifacts
  resolves with no broken requirements. `smoke.py` verifies installed import
  origins, CAD volumes, numeric/symbolic formulas, removal of the old helper
  package, and the framework's viewer report.
- The same smoke passes after reinstalling all three source distributions.
- Full manual: all three external examples exported successfully and Sphinx
  completed with `-W --keep-going` and no warnings. The rendered manual is
  retained at `dist/docs-0.7-2026-09-20/`.
- The fresh installed framework/viewer captured the V8 at 800×600 through
  Chromium. Visual inspection confirms the complete assembly and its colors
  render; `v8-release.png` records that smoke, not manufacturing validation.

OpenSpec 1.6.0 rejected a maintenance-only change with no spec delta and did
not implement the installed skill's skip-specs support. The pilot explicitly
approved the direct maintenance path. No fabricated validation or archived
OpenSpec cycle is claimed; the extraction's baseline spec is validated normally.

## Release handoff

Each repository retains its wheel and sdist in
`dist/release-0.7-2026-09-20/`. Artifact hashes are recorded separately beside
this report. Companion release instructions live in viewer
`docs/release-0.2.md` and mechanics `docs/release-0.1.md`.

The remaining external actions require the pilot's release instruction:

1. Push the three prepared repositories and the pinned example commits before
   triggering a remote documentation build. In particular Clock 01's commit was
   unavailable from its remote during validation and was fetched from the local
   project catalogue. Source installs for the companion packages also require
   their prepared commits to be available remotely.
2. Publish viewer 0.2.0, framework 0.7.0, then mechanics 0.1.0. Mechanics depends
   on framework >=0.7.0; its optional extra becomes index-resolvable once both
   are uploaded. Use the retained wheel/sdist pairs, not arbitrary older files
   in each repository's dist directory.
3. Tag and create the corresponding releases as directed, and verify a fresh
   combined install from the index.

No push, tag, upload or remote release was performed. The Studio extra is
experimental and unpublished, and is outside this release. No Python 3.11,
Windows or macOS run is claimed.
