## Context

The viewer's records were written while the package was unreleased and the
framework was 0.7.0 in preparation. Framework and viewer now release
together; the pilot chose one number for both. The viewer already declares
API 23 and reads document versions 1 to 10, and the framework manual at
main `c5ca365` already names that API. What is out of date is the version
narrative, three cross-manual links, and two reference paragraphs.

## Goals / Non-Goals

**Goals:**

- Every reader-facing statement of the version says 0.7.0, released with
  Machinome 0.7.0, and nothing says "unreleased".
- The manual reads as a developer's manual: no decision records, no
  project code-names, no release-note prose inside reference entries.
- The changelog's release section is a user's summary; the detailed
  development narrative is kept, byte for byte, where maintainers look.

**Non-Goals:**

- No runtime, API or document-version change; no bundle behaviour change
  beyond its version banner.
- No publication: PyPI upload, tag and push stay with the pilot.
- No edit to archived OpenSpec records or accepted ADRs that mention 0.2.0
  as the then-current unreleased version; they are history.

## Decisions

- **One version number with the framework.** The viewer's `version` is a
  package identity, not a capability declaration; capability is carried by
  `apiVersion` and `documentVersions`, which do not move. Jumping from
  0.2.0 to 0.7.0 costs nothing a host can observe and makes the pair
  legible: "viewer 0.7 for machinome 0.7". Alternative: keep 0.2.0 and
  document the pairing in prose; rejected by the pilot.
- **Version strings stay single-sourced.** `pyproject.toml`, `__init__.py`
  and `package.json` each carry the number the tests already cross-check
  against the CLI reference example; the bundle banner comes from
  `package.json` at build. The bundle is rebuilt so the banner and the
  currency check agree.
- **Changelog shape follows the framework's.** A `0.7.0 — 21 September
  2026` section summarises what the released viewer does, grouped by what
  a reader can do, in the changelog's own voice. The 0.2.0 and 0.1.0
  development sections move verbatim to
  `workflow/archive/changelog-before-0.7.md`, referenced from the changelog
  and `workflow/README.md`. Alternative: keep a thousand lines of
  development narrative under the release heading; rejected because a
  changelog reader wants the release, not the campaign.
- **Cross-links name the framework manual's 0.7 pages** (`start/install`,
  `tutorial/10-share`, `reference/cli`, `project/upgrading`).
- **Reference prose stays reference.** The running page's two release
  paragraphs become a "Stops and time drives" section after "Request
  motion", stated as behaviour a host relies on, with the project name
  removed.
- **Tests turn red first.** `tests/test_documentation.py` expects
  `workflow/release-0.7.md`, refuses the word "unreleased" in the manual,
  README and current changelog section, and expects the changelog's first
  section to name 0.7.0 and the release date.

## Risks / Trade-offs

- [The bundle is rebuilt in a worktree with a linked `node_modules`] → run
  only `npm run build`; never `npm ci` or `npm install` through the link.
- [The manual states a release before the upload happens] → the pilot
  asked for the release narrative; the record names the upload as the
  pilot's separate action and the framework's status page carries the same
  fact.
- [Archived records keep saying 0.2.0] → they are dated history; the
  changelog archive note explains the renumbering.

## Migration Plan

Fast-forward viewer main; the framework manual's `viewer_version`
substitution becomes 0.7.0 in the framework repository. A host pinning
`machinome-viewer==0.2.0` never obtained a release, so nothing installed
changes meaning.
