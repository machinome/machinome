## Context

The extracted code arrives with the framework's assumptions: the server read
the build directory through `solid_node.core.builder`, the capture staged the
node itself by serializing it, and every consumer imported paths from
`solid_node.viewers.bundle`. The licensing goal rules those imports out in
both directions.

## Goals / Non-Goals

**Goals:** a package that installs beside solid-node with no dependency
either way beyond an entry point and a console script; unchanged browser
behaviour; unchanged published names; the bundle carrying its own source
offer.

**Non-Goals:** replacing Create React App, changing the viewer API, or
publishing to PyPI — publishing is the maintainer's explicit decision.

## Decisions

- **A process boundary, not imports.** The framework spawns `serve` and
  `capture`; it resolves the bundle through an entry point that imports only
  the standard library. An Apache program that optionally launches an AGPL
  program through a documented interface is not a combined work; an Apache
  program importing AGPL classes arguably is. The alternative — keeping
  `WebViewer` and `BrowserRenderer` importable from here — was less
  refactoring and was rejected for that reason.
- **The server knows a directory, not a project.** `serve --build-dir` replaces
  `get_build_dir()`; `errors.json` is found beside the document. Ports keep
  their environment defaults so `.env` files written by the shop's bench
  script keep working.
- **The capture photographs a staging directory.** The framework keeps the
  half of the old renderer that knows nodes — building artifacts, serializing
  the document, hard-linking models into a staging directory — and hands the
  directory over. The capture adds the bundle and mount page, serves, shoots.
  Camera arrives as eye, target, up and field of view: the framework parses
  OpenSCAD camera syntax, the viewer does not learn it.
- **Fixtures are committed exports.** The old tests exported a node with the
  framework at test time. A `--no-widget` export of the spinner project is
  committed instead; the suite completes it with the installed widget files.
- **The parity fixture generator stays with the producer.** Its numbers are the
  framework's render results; the JSON it writes is committed here.
- **Versions.** Package 0.1.0; viewer API stays 5. A test pins the Python
  version, `package.json` and the changelog to one number.

## Risks / Trade-offs

- A framework release that renames the entry point or the commands strands
  installed viewers; both are named in `viewer-distribution` and covered by
  tests on both sides.
- Two processes where there was one means `solid develop` restarts the server
  as a subprocess instead of a `multiprocessing` child; the reload contract is
  unchanged because the server never held state.
