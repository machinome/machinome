## 1. Baseline and red tests

- [ ] 1.1 Record the baseline: time the three subprocesses `prepare_project`
      runs for an already-built project, and the wall time from open request to
      session registered.
- [ ] 1.2 Red: opening several projects in one shop invokes `solid viewer` once.
- [ ] 1.3 Red: opening a project whose build publishes nothing runs no
      `solid snapshot` subprocess, and leaves the existing screenshot untouched.
- [ ] 1.4 Red: opening a project whose build publishes nothing and which has no
      valid screenshot does render one.
- [ ] 1.5 Red: opening a project with a complete valid publication registers the
      session and starts its agents without awaiting the build.
- [ ] 1.6 Red: opening a project with no publication, and creating a new
      project, still wait for the build.
- [ ] 1.7 Red: a build that fails behind an already-open session reports
      `model_build_unavailable` and leaves the previous publication available.

## 2. Shop-scoped viewer bundle

- [ ] 2.1 Resolve the viewer bundle once for the running shop and reuse it for
      every session; keep the required-API-version check and the
      no-usable-bundle failure exactly as they are.
- [ ] 2.2 Pass it into project preparation instead of calling `solid viewer`
      per open.

## 3. Split preparation from building

- [ ] 3.1 Separate the repository work (resolve, boundary-verify, scaffold,
      `git init`, profile declaration, initial commit) from the build,
      snapshot validation, and screenshot.
- [ ] 3.2 Keep both callers building through
      `PreparedProject.build_invocation()` so open and watcher cannot drift.
- [ ] 3.3 Capture a digest of `_build/viewer.json` before and after the build
      and report whether the open published anything.
- [ ] 3.4 Render the screenshot only when the publication changed or
      `screenshot_revision()` reports none.

## 4. Open on an existing publication

- [ ] 4.1 In `_open`, when `_build/viewer.json` exists and passes
      `_validate_snapshot`, register the session, start the orchestrator and
      the watchers, then run the build as a task tracked on the session.
- [ ] 4.2 Start the watchers before the build so the publication cannot be
      missed.
- [ ] 4.3 Publish the "model being brought up to date" state on the hub and in
      the session snapshot, and clear it when the build settles — including the
      no-op success, which moves no artifact and would otherwise signal
      nothing. Show it on both the hub card and the workspace, since opening a
      project navigates away from the hub.
- [ ] 4.4 Report a background build failure on the session broker and leave the
      previous publication available.
- [ ] 4.5 Cancel and await the build task in `Session.close()` alongside the
      existing tasks.
- [ ] 4.6 Keep the blocking path for a project with no valid publication and
      for creation.

## 5. Verification

- [ ] 5.1 Turn every red test from group 1 green; run the floor suite.
- [ ] 5.2 Confirm the repository boundary is still verified before any agent
      starts on both paths.
- [ ] 5.3 Open the shop for real against a projects catalogue and measure a
      warm reopen of a large already-built project, before and after.
- [ ] 5.4 Confirm in the browser that the model appears from the existing
      publication, that the up-to-date state clears, and that a rebuild
      triggered by a source edit still reaches the viewer.
- [ ] 5.5 Confirm a newly created project still opens correctly and gains a
      screenshot.
