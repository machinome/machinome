# Machinome Viewer 0.7.0 release preparation

Companion to Machinome 0.7.0, released 21 September 2026. The pilot decided
the viewer releases as 0.7.0, the framework's number, replacing the unreleased
0.2.0 development state (OpenSpec change `release-the-viewer-as-0-7`). This
document records the prepared state; uploading to PyPI, tagging and pushing are
the maintainer's separate actions.

The Python distribution and bundled widget are both version 0.7.0. The widget
reports API 23 and reads document schemas 1–10, including running `Play`
contact laws and explicit time drives. It retains legacy solid-node document
reading and uses the Machinome command, entry point, browser global and asset
names.

Release set: machinome 0.7.0 (Apache-2.0), machinome-viewer 0.7.0
(AGPL-3.0-only), machinome-mechanics 0.1.0 (Apache-2.0). The framework and
mechanics keep their own numbers; the viewer's now follows the framework's.
The widget npm package is private and ships inside the Python package; no npm
publication is planned.

Release order: publish this package before the framework's `viewer` extra is
advertised as installable, since that extra is unpinned and resolves to the
index.

To reproduce packaging: `python -m build`, then
`python -m twine check --strict dist/*`. Install the wheel in a fresh environment
outside the repository and run `machinome-viewer describe`; expect API 23,
version 0.7.0 and document versions 1 through 10. The sdist carries the bundle
and source; verify it independently as well. Never run `scripts/check-dist`,
`npm ci` or `npm install` in a worktree whose `node_modules` is a link to the
primary checkout.

Validation evidence for this state is in
`openspec/changes/archive/2026-09-21-release-the-viewer-as-0-7/evidence.md`.
