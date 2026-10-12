# Machinome Viewer 0.7.0 release preparation

Companion to Machinome 0.7.0, released 23 September 2026. The pilot decided
the viewer releases as 0.7.0, the framework's number, replacing the unreleased
0.2.0 development state (OpenSpec change `release-the-viewer-as-0-7`). This
document records the prepared state; uploading to PyPI, tagging and pushing are
the maintainer's separate actions.

The Python distribution and bundled widget are both version 0.7.0. The widget
reports API 27 and reads document schemas 1–13, including running `Play`
contact laws, explicit time drives, source-timed motion, the two-surface
`Follow` (ADR-075) and finite convex-profile contact inside a numeric running
bound, both folded into the release on 23 September after the 22 September
fold. API 27, folded the same day, adds separately named handles for two
`Turn` controls on one part selecting different joints, with no document
change; bounded exact reuse of a constant cyclic block's motion was folded
with it as an internal performance change. It retains legacy solid-node document
reading and uses the Machinome command, entry point, browser global and asset
names.

Release set: machinome 0.7.0 (Apache-2.0), machinome-viewer 0.7.0
(AGPL-3.0-or-later), machinome-mechanics 0.1.0 (Apache-2.0). The framework and
mechanics keep their own numbers; the viewer's now follows the framework's.
The widget npm package is private and ships inside the Python package; no npm
publication is planned.

Release order: publish this package before the framework's `viewer` extra is
advertised as installable, since that extra is unpinned and resolves to the
index.

To reproduce packaging: `python -m build`, then
`python -m twine check --strict dist/*`. Install the wheel in a fresh environment
outside the repository and run `machinome-viewer describe`; expect API 27,
version 0.7.0 and document versions 1 through 13. The sdist carries the bundle
and source; verify it independently as well. Never run `scripts/check-dist`,
`npm ci` or `npm install` in a worktree whose `node_modules` is a link to the
primary checkout.

Validation evidence for this state is in
`openspec/changes/archive/2026-09-21-release-the-viewer-as-0-7/evidence.md`.

25 September 2026, before publication: the grant is AGPL-3.0-or-later,
version 3 or any later version rather than version 3 only, in every header,
both manifests, the bundle banner and the manual (change
`relicense-to-agpl-or-later`); the `v0.7.0` tag is re-cut on the integrated
head.

25 September 2026, CI red at 0761145 (run 36125015897) for two test
reasons, both fixed before the tag is re-cut: the new licence test scanned
its own source, and the marked pixel bench photographed the corner
full-screen button, whose inline `display` beat the manual's own hide rule
`.machinome-fullscreen { display: none }`. The button now sets no inline
`display` (the icon is a block filling its padding box), a unit test holds
that, and the bench proves the documented rule in a real browser. The
"pre-existing environmental flake" the `go-fullscreen` record describes was
this button: its hide rule never applied.

27 September 2026: released as **0.7.1** with Machinome 0.7.1 (change
`release-0-7-1`). The 0.7.0 distributions were uploaded to PyPI on
26 September from the files built at `1e67c83` (the sha256 digests in
`dist/0.7.0-2026-09-25/` match the index); the GitHub `v0.7.0` tag still
points at `0761145`, two commits short of what was published. 0.7.1
renumbers that same source: the package, the widget and the banner say
0.7.1, API 27 and document versions 1–13 do not move, and the changelog
says so. The framework's 0.7.1 changes the document not at all, so the
pairing is by number only. Distributions are built from the primary
checkout with `scripts/check-dist` after integration; tagging, pushing
and uploading remain the maintainer's.
