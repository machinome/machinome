## ADDED Requirements

### Requirement: The contributor guide says how the studio's tests run

`CONTRIBUTING.rst` SHALL install `packages/machinome-studio` editable in its
pip command, and SHALL say that the studio keeps its tests in its own
directory: they run with `make test PKG=machinome-studio`, or with `python -m
pytest` from `packages/machinome-studio` after `npm ci` at the repository's
root and the build of the studio's frontend from there, with the OpenSpec CLI
on the PATH; its browser tests run when `MACHINOME_STUDIO_E2E=1` is set, with
Chromium installed. It SHALL say how the studio's browser surface is built
from the root, and that the built surface is not tracked.

#### Scenario: A contributor runs the studio's tests

- **WHEN** a contributor follows the guide on a fresh clone with the OpenSpec
  CLI installed
- **THEN** `uv sync`, `npm ci` at the root and `make test PKG=machinome-studio`
  build the studio's frontend and run its tests, its browser tests skipping
  with a reason naming `MACHINOME_STUDIO_E2E`, and the layout test fails if
  the guide omits the studio's directory from its pip command
