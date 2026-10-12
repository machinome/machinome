## ADDED Requirements

### Requirement: The contributor guide says how the movie package's tests run

`CONTRIBUTING.rst` SHALL install `packages/machinome-movie` editable in its
pip command, and SHALL say that the movie package keeps its tests in its own
directory: its Python tests run with `python -m pytest` from
`packages/machinome-movie`, and its Node suite with `npm test --workspace
packages/machinome-movie/machinome/movie/js` from the repository's root after
`npm ci` there, its browser and pipeline tests needing Chromium and FFmpeg. It
SHALL say that the root's `npm ci` installs each member's dependencies beside
it, and that `machinome movie setup` is for an installed copy, not for the
checkout.

#### Scenario: A contributor runs the movie's tests

- **WHEN** a contributor follows the guide on a fresh clone
- **THEN** `uv sync`, `npm ci` at the root, then `python -m pytest` from
  `packages/machinome-movie` and `npm test --workspace
  packages/machinome-movie/machinome/movie/js` from the root run the
  package's two suites, and the layout test fails if the guide omits either
