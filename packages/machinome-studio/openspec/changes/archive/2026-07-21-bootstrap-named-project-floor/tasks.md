## 1. Pin and prove the solid-node publication boundary

- [x] 1.1 Add a focused executable acceptance check that proves the selected solid-node CLI can perform one finite build of `root`, exit nonzero on an invalid initial project, and publish the complete viewer snapshot consumed by Floor.
- [x] 1.2 Make command discovery select this workspace's `./solid-node` installation or an explicitly configured equivalent, never an unrelated sibling checkout found incidentally on `PATH`.
- [x] 1.3 Run the acceptance check and record the existing supported command, artifact contract, and framework revision exercised by the shop tests.

## 2. Prove named-project preparation red

- [x] 2.1 Add table-driven tests that reject an omitted name, uppercase or whitespace variants, separators, dot components, absolute paths, and resolved symlink escapes while accepting lowercase kebab-case names.
- [x] 2.2 Add tests that a missing project invokes the configured solid executable as `new <name>` from the workspace `projects/` directory, creates only the standard scaffold, and establishes that exact directory as an independent Git repository with one initial scaffold commit.
- [x] 2.3 Add tests that an existing exact project repository is reused without running `solid new` or mutating Git state, while a plain directory, nested repository, file, and escaped path each fail preparation.
- [x] 2.4 Add tests that scaffold, Git initialization, initial commit, build-command, malformed viewer snapshot, missing referenced artifact, and stale-artifact failures each preserve useful evidence and return a stage-specific error.

## 3. Gate the complete runtime red

- [x] 3.1 Extend launcher tests to fail until the project name is required and arbitrary maker-facing project paths can no longer bypass workspace resolution.
- [x] 3.2 Add ordering tests that no port bind, FastAPI server task, Codex app-server, or role thread starts before project preparation and complete snapshot validation succeed.
- [x] 3.3 Add failure-path tests proving every preparation error prints no browser URL and creates zero floor or agent runtime resources.
- [x] 3.4 Add orchestration tests proving foreman, designer, and machinist all receive the same verified project repository as their working directory while their role adapters continue to load from the shop checkout.
- [x] 3.5 Add browser/artifact acceptance coverage proving the first model request after a reported open returns the preflighted viewer snapshot and referenced files rather than the no-build 404 response.

## 4. Implement project preparation and fail-closed opening

- [x] 4.1 Implement a typed preparation result and strict project-name/project-home resolver with containment and symlink checks.
- [x] 4.2 Implement missing-project creation through the configured `solid new` command, exact-root Git initialization, scaffold-only initial commit, and non-destructive failure reporting.
- [x] 4.3 Implement existing-project exact Git-root validation without source, index, commit, or scaffold mutation.
- [x] 4.4 Implement the supported one-shot `root` build and validate readable viewer metadata plus every contained referenced model artifact before accepting the project.
- [x] 4.5 Reorder the persistent Codex launcher so preparation completes before server construction, require the project name in its public command contract, and pass the verified project root to Floor and all three role threads.
- [x] 4.6 Remove or align the legacy optional-project entry point so every supported way to open a project shop uses the same preparation gate and cannot expose an unbuilt Floor.

## 5. Verify and record the convention

- [x] 5.1 Make the focused preparation, launcher, orchestration, artifact-route, broker, and browser tests green, then run the complete Python and frontend suites.
- [x] 5.2 Manually open a previously absent kebab-case project, verify its initial Git commit and visible default model, close it cleanly, and reopen the existing project without recreation.
- [x] 5.3 Manually force an initial-build failure and verify no listener, broker task, app-server process, role thread, or browser URL survives or is reported while the project evidence remains available.
- [x] 5.4 Update README, Codex startup guidance, and current shop operating knowledge to require a project name, describe `projects/<name>` creation/reuse, and state the build-before-open guarantee.
- [x] 5.5 Sync the accepted delta specs to baseline, archive the completed OpenSpec change, and commit the implementation record only after all gates and manual checks pass.

## Validation evidence

- Workspace CLI acceptance: `solid build root` published `_build/viewer.json`
  and every referenced model artifact; `solid build absent` exited nonzero.
- Framework checkout exercised: `ae525ae19e12ec979353e99a7fbeafb76e962e27`.
- Python regression: 47 tests passed, including 6 Playwright browser checks.
- Frontend: `npm test` and `npm run build` passed.
- Manual checks created and reopened `manual-check` with one clean scaffold
  commit, served its initial model, and closed both runs cleanly. Forced build
  failure for `manual-failure` exited 1, printed no browser URL, left no
  listener on port 9128, and preserved the one-commit project evidence.
