# ADR-008: The real viewer is proved through a bundle selected by path, never assumed

Status: Accepted (OpenSpec change `viewer-integration-layer`, 30 September
2026). Extends [ADR-003](ADR-003-one-runner-and-a-content-keyed-test-memo.md).

## Context

Every browser and pipeline test draws its views with the viewer double, a
flat canvas with a pinhole camera, and the fixture export was written by hand
with the part names and no meshes. The testing policy names a sixth layer,
"Viewer integration (Playwright, the real bundle) ... Gated on a selected
bundle, and it asserts the API it needs rather than assuming it", and until
this change it had no test. *Cut and Advance* (version 2, 30 September 2026)
met on its first render two failures of the stage's contract with the real
viewer that no test could see (wart 1 of "Cut and Advance, version 2"): the
real viewer sizes its canvas on its own animation frame and shrinks a
detached host's canvas to nothing. The memory a film's viewer instances cost
was a guess (wart 5 of "The React stage").

The viewer is a separate product (AGPL, its own repository). Videomaker
reaches it only through the bundle a caller selects by path and the API that
bundle declares; the repository names no neighbouring checkout.

## Decision

1. **Layer 6 is its own project.** `vitest.config.mjs` has a project
   `viewer`, the files under `test/viewer/`, run after the slow project, one
   file at a time, with the slow project's global setup and setup file. The
   run's one Chromium serves both projects: the global setup keeps it on the
   main process's `globalThis`, made by the first setup of the run and closed
   by the last teardown. vitest runs a project's tests in a worker of its
   own, so the viewer project has its own asset server, made once for all its
   tests.
2. **The gate is `VIDEOMAKER_VIEWER_BUNDLE`.** Its value is the bundle's path,
   an argument in the environment that appears nowhere in the repository.
   Unset or empty, every test of the layer is skipped with the note "no
   viewer bundle selected", before the memo is consulted, and the memo's
   report lists it under that note, never as passed or run. A path with no
   file, or a file that does not define `MachinomeViewer` when loaded into a
   blank page, fails every test naming the path. A layer 6 test is declared
   with `viewerTest` (`test/support/viewer-bundle.mjs`).
3. **The API is asserted.** The layer mounts the bundle on the fixture
   export and compares the `apiVersion` the instance declares with what the
   fixture movie requires (`stageConfig(film).viewer.required.api`); a lower
   one fails naming the path and both numbers.
4. **The selected bundle is keyed by its bytes, under its variable.** A
   layer 6 test's verdict key covers the bundle's SHA-256 named
   `VIDEOMAKER_VIEWER_BUNDLE` (`SELECTED` in `test/support/reach.mjs`), never
   its path: the same bytes elsewhere are the same input, other bytes miss.
5. **The fixture export is real.** The fixture project's export is what the
   framework's `machinome export` writes for its seesaw (a declared 20 s loop,
   a beam that tips through it, a colour on its blocks), committed without the
   viewer (`--no-widget`). The layer proves, over it and the fixture tour:
   the API; that a canvas is its box's size on a fresh mount, after a change
   of set and when a view returns; A, B, A across a camera move, a ghosted
   highlight, a hidden layer and a leased instance; marks through the real
   `partOnScreen` and `project`; `check`, `preview` and `render` from the
   command line; and it records, without a threshold, the page heap and the
   resident memory of Chromium's process tree with one and two instances.

## Alternatives considered

- **The layer's tests in the slow project.** One worker and one asset server,
  but the layer could not be run or skipped as a project, and the gate would
  sit among tests that need no bundle.
- **A bundle found by a relative path to the viewer's checkout, or through
  the framework's report.** Rejected by the repository boundaries: a path is
  an argument, never an assumption about a neighbouring workspace, and the
  framework is reached only through its documents and, for a movie, its
  command.
- **Key the bundle by its path.** A path relative to the repository carries
  the neighbouring layout into the key and differs between two worktrees of
  one content; an absolute path differs between machines.
- **A threshold on memory.** The numbers depend on the machine, the GPU
  Chromium has and what else runs; they are recorded as evidence.
- **Keep the hand-written export beside the real one.** The real export
  matches the manifest every fixture document was written against; two
  exports would be two fixtures for one take.

## Consequences

- `npm test` without the variable reports the layer skipped by name; with
  it, the layer runs after the slow tests on the same Chromium. A new bundle
  reruns the layer.
- The fixture project's export has meshes and a posed loop; its revision and
  every document pinned to it were re-pinned together. The browser and
  pipeline tests with the double are unaffected but key the new export.
- A running or clocked fixture, a scenario take, and the bank checks the
  policy's layer 6 names are not built; they wait for a film that needs them.
