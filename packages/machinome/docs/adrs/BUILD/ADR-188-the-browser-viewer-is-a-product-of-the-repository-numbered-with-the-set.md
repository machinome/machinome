# ADR-188: The Browser Viewer Is a Product of the Repository, Numbered with the Set

**Status:** Accepted; the npm workspace's second member, with a lock of its own, amended 2026-10-12 by [ADR-191](ADR-191-the-videomaker-is-a-product-of-the-set-its-node-side-installed-by-its-command.md); the studio's frontend beside the widget, amended 2026-10-12 by [ADR-193](ADR-193-the-studio-is-a-product-of-the-set-reached-by-machinome-studio.md); "The seam is unchanged" and its sentence on `machinome vet` superseded 2026-10-12 by [ADR-194](ADR-194-viewers-are-providers-behind-one-seam-chosen-by-name.md) (note below)
**Date:** 2026-10-12
**Change:** [`join-viewer`](../../../openspec/changes/archive/2026-10-12-join-viewer/)
**Supersedes:**
- [EXPORT/ADR-068: Optional viewer package behind a process boundary](../EXPORT/ADR-068-optional-viewer-package-behind-a-process-boundary.md), in the viewer's repository and licence; its lookup through the `machinome.viewer` entry point, its process boundary and the framework's completeness without the viewer stand
**Amends:**
- [ADR-182: The repository is a monorepo of distributions, each named by its directory](ADR-182-the-repository-is-a-monorepo-of-distributions-named-by-directory.md): the root holds an npm workspace, a private `package.json` and its one `package-lock.json`, beside the uv workspace
- [ADR-183: An extension package is a namespace portion in its own distribution](ADR-183-an-extension-package-is-a-namespace-portion-in-its-own-distribution.md): a product numbered with the set, its manifest, pin, `__init__.py` and widget `package.json` in `.bumpversion.cfg`, `~=` both ways
- [ADR-187: The mechanics helpers are a portion of the repository at their own version](ADR-187-the-mechanics-helpers-are-a-portion-of-the-repository-at-their-own-version.md): a second product keeping its record in its directory, this one numbered with the set
**Related to:**
- [ADR-103: The browser is the only interactive development viewer](ADR-103-the-browser-is-the-only-interactive-development-viewer.md): the viewer `machinome develop` opens, unchanged
- [ADR-179: The core reaches a node package's renderer and command through the table of supported node types](ADR-179-the-core-reaches-a-node-packages-renderer-and-command-through-the-table-of-supported-node-types.md): the provisional renderer column, which the `viewer-seam` cycle removes

## Context and Problem Statement

The plan for the joins of Machinome 0.9 (`workflow/ongoing/joins-0.9.md` at
the repository root, set by the pilot on 11 October 2026) brings
machinome-viewer into the repository as its third join. The browser viewer
was split from this repository on 5 September 2026 (ADR-068) and published
from a repository of its own as 0.7.0, 0.7.1 and 0.8.0, numbered with the
framework, 0.8.1 held at released state: the embeddable three.js widget,
the development server, the headless capture and the bundle the framework
copies into every export, imported as `machinome_viewer`.

On 12 October 2026 the pilot settled how it joins: whole, into
`packages/machinome-viewer/`, with its record and its whole history, its
four tags prefixed `viewer-`; its manual folded into the one manual; one
licence and one version, the set's, `~=` both ways; pip-only distribution,
its widget the first member of a root npm workspace; the seam unchanged, the
framework finding the viewer through its entry point and running it as a
separate process. The same day the pilot gave its Python package the
address `machinome.viewer.web`, the address the `viewer-seam` outline of 4
October 2026 gives the web provider.

At its new place the product does not work as it is (design.md of the
change, probes 4 to 8 and 13): its widget's tests read the fixtures and the
manual by relative paths, its currency check refuses to rebuild a stale
bundle when npm installs the dependencies at the workspace root, its
packaging guard watches only the widget's own `node_modules`, its manual's
pages fail the framework's build, and the lock's Playwright needs a Chromium
the machine lacked. The address resolves editable and from the wheels
(probe 19), hides behind a regular `machinome/viewer/__init__.py` in an
editable workspace unless that file extends its path with portions (probe
20), and passes `machinome vet` unless the contract denies it (probe 21).

## Considered Options

1. **A product of the repository at `machinome.viewer.web`, numbered with
   the set, its process seam kept** (chosen by the pilot)
2. The same at `machinome.viewer`; refused by the pilot: the seam's own
   address, which the `viewer-seam` cycle would take back with a second
   rename
3. The same with `machinome_viewer` kept; declined by the pilot: outside
   the set's dotted names
4. The viewer as an extension package whose record folds into the
   framework's; refused by the plan, under which a product keeps its record
5. The seam of viewers in this cycle, the viewer one of its providers;
   refused by the pilot: the seam is unchanged and `viewer-seam` is a later
   cycle
6. The widget's own lockfile kept beside the workspace's; refused by probe
   5: npm reads only the root's inside a workspace

## Decision Outcome

**The package is `machinome.viewer.web`.** The distribution
`machinome-viewer`, at `packages/machinome-viewer/`, ships the package
directory `machinome/viewer/web/` with its own `__init__.py`, the eight
modules and the widget, and none at `machinome/` nor at `machinome/viewer/`;
the core's path extension admits the portion, and `machinome.viewer` is a
namespace level with no module of its own until the seam. Its console script
`machinome-viewer` and its entry point `bundle =
machinome.viewer.web.bundle:describe` in the group `machinome.viewer` keep
their names. No module of the former name is provided.

**The seam is unchanged.** The framework loads only the entry point and runs
the viewer as `python -m machinome.viewer.web describe|serve|capture` in its
own interpreter; it imports no viewer code, and the viewer imports nothing of
the framework. `machinome vet` denies `machinome.viewer.web` as a framework
internal: it serves, captures and builds in processes of its own.

**Its record is in its directory.** Beside the package the directory holds
its manifest, README, `CHANGELOG.md`, `MANIFEST.in`, `.gitignore`, the links
`LICENSE` and `LICENSES`, `scripts/`, its `tests/`, its `openspec/` and its
`workflow/` with its own decision log, `workflow/adrs/`. Its Python tests run
from that directory and its widget's from the root, in CI's test job; the
core's suite does not collect them. Its manual is three how-to guides and the
reference section `reference/viewer/` of the framework's manual, whose
embedding example the build copies with the installed viewer's bundle.

**It carries the set's version and licence.** Its manifest, its pin
`machinome~=`, its `__init__.py` and its widget's `package.json` are tables
of `.bumpversion.cfg`; the core's `viewer` and `web-snapshot` extras pin it
`~=`; npm brings the root lock's member entry to the version. Its manifests,
every source header and the bundle's banner state the set's expression, and
the bundled libraries' notices are kept, their provenance in `CREDITS.md`.

**The root holds an npm workspace.** A private `package.json` whose one
member is the widget, with no version and no package of its own, and one
`package-lock.json` seeded from the widget's, every resolution kept;
`node_modules/` at the root, ignored. The currency check accepts the build
program wherever Node resolves it, and packaging refuses a symbolic
`node_modules` anywhere from the widget up.

**It is smoked from its wheel.** `scripts/check-dist` requires npm, builds
the viewer (its sdist builds the bundle), installs its wheel by path and
checks its eight modules and bundle owned by its distribution, no widget
source, its version and pin, the core's extras pinning it, the entry point's
report, the banner and the licence texts, then runs `machinome-viewer
describe` and `machinome viewer`.

### Consequences

- Good: one licence, one version, one manual and one CI for the set.
- Good: the viewer sits where the seam of viewers will find its web
  provider, so the `viewer-seam` cycle renames nothing of it.
- Good: the framework reaches the viewer as before; the studio, the site
  and the exports read the same report and the same bundle.
- Neutral: Node enters CI's test, browser-snapshot and dist jobs; the docs
  job keeps the published viewer and needs no Node.
- Bad: the 79 commits from before the split read twice in a global log, the
  framework's originals and their rewritten copies, told apart by their
  paths.
- Bad: the core's suite and the viewer's tests need a built bundle and
  Chromium for the installed Playwright.
- Bad: every viewer process imports the core's `__init__` (probe 10), about
  10 ms within the run-to-run spread of a process start.
- Bad: until the seam, `machinome.viewer` is a namespace level with no
  module of its own beside the core's `machinome.viewers`; the seam's
  `machinome/viewer/__init__.py` must extend its `__path__` with
  `_namespace_portions`, or it hides the viewer in every editable workspace
  while every wheel installation still works (probe 20).
- Bad: project tools that run `python -m machinome_viewer` move to the new
  address or to `machinome viewer`, in their own repositories.
- Neutral (2026-10-12, `join-movie`): the movie's JavaScript directory is
  the workspace's second member and keeps a lock of its own for an installed
  copy (ADR-191).
- Neutral (2026-10-12, `join-studio`): the studio's frontend is the
  workspace's third member, built from the root beside the widget, and the
  studio, a product numbered with the set, photographs projects through the
  viewer's capture it requires (ADR-193).

## Note (2026-10-12)

[ADR-194](ADR-194-viewers-are-providers-behind-one-seam-chosen-by-name.md)
supersedes "The seam is unchanged" (OpenSpec change `viewer-seam`): the
package `machinome.viewer.web` is the web provider of the framework's seam of
viewers, `machinome.viewer`, which imports it at its address; the entry
point `machinome.viewer` is removed, and the framework serves and captures
through the provider in its own process and runs no program of the viewer's.
`machinome-viewer describe|serve|capture` and `python -m machinome.viewer.web`
keep working. `machinome vet` denies the seam whole, `machinome.viewer`, in
place of `machinome.viewer.web`. The rest of this record stands.
