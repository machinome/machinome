# Machinome Viewer 0.8.0 release preparation

Companion to Machinome 0.8.0, released 5 October 2026. The pilot decided on
5 October that the viewer releases as 0.8.0, the framework's number, as it
did for 0.7.0 and 0.7.1 (OpenSpec change `release-0-8-0`). This document
records the prepared state; uploading to PyPI, tagging and pushing are the
maintainer's separate actions.

The Python distribution and bundled widget are both version 0.8.0, and the
bundle banner reads `machinome-viewer 0.8.0 - viewer API 29`. The widget
reports API 29 and reads document schemas 1–13. 0.8.0 is the source on
`main` after 0.7.1: API 28 (`track-a-part-on-screen`, `highlight-a-part`,
`move-up-and-field-of-view`, 29 September) adds `partOnScreen`, `project`,
`highlight` and an up direction and field of view per `setView`; the
fresh rigid-asset draw order became independent of fetch completion
(`deterministic-asset-load-order`, 29 September, no API change); API 29
(`on-demand-clocked`, 1 October) mounts a clocked machine with
`renderMode: 'on-demand'`. The document format does not move: Machinome
0.8.0's exports declare versions 1 to 13, as 0.7's do, so a 0.7 viewer
reads them, and this viewer reads every 0.7 export.

Release set: machinome 0.8.0 and machinome-viewer 0.8.0, each under the
licence its own manual states (this package is AGPL-3.0-or-later);
machinome-mechanics 0.1.0 is unchanged and not re-released. The viewer's
number follows the framework's. The widget npm package is private and ships
inside the Python package; no npm publication is planned.

Release order: publish this package before the framework's `viewer` extra is
advertised as installable, since that extra is unpinned and resolves to the
index.

To reproduce packaging: `scripts/check-dist` in the primary checkout after
integration builds the wheel and sdist, installs the wheel outside the
repository and runs `machinome-viewer describe`; expect version 0.8.0, API
29 and document versions 1 through 13. It uploads nothing. Never run
`scripts/check-dist`, `npm ci` or `npm install` in a worktree whose
`node_modules` is a link to the primary checkout.

After the change is archived, it is integrated into `main` by fast-forward
and `scripts/check-dist` runs from the primary checkout. Remaining for the
pilot: the `v0.8.0` tag, the push, the PyPI upload, the Read the Docs build
of the released version, and the Context7 refresh.

Validation evidence for this state is in the archived `release-0-8-0`
change's `evidence.md`.
