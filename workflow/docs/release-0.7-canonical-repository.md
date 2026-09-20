# Machinome 0.7 canonical-repository release handoff

2026-09-20. Publication pending. This supersedes the artifact selection in
`workflow/archive/release-0.7-2026-09-20/README.md`; that earlier evidence is
preserved unchanged. Canonical source: https://github.com/machinome/machinome.
The pilot ratified `use-machinome-repository-name` and authorized local integration.

## Release artifacts

Use only `dist/release-0.7-canonical-2026-09-20/` in each owning repository.
The framework checkout becomes `machinome/`; companion checkout names stay
`machinome-viewer/` and `machinome-mechanics/`. Versions remain framework 0.7.0,
viewer 0.2.0 and mechanics 0.1.0. Exact hashes are in
`release-0.7-canonical-artifacts.sha256`, relative to the shop workspace.

Viewer source: `e24b014`; mechanics source: `7b8d5bb`.
Framework source is the implementation commit archiving
`use-machinome-repository-name`, based on `44edea8` with planning commit `e8c073b`.
Its later spec/evidence completion does not change the packaged runtime or metadata.

## Verification

- Homepage assertion failed against old metadata, then passed after correction.
- Framework identity/docs/extraction checks: 17 passed, 40 subtests (Python 3.12).
- All 34 framework baseline specs and the change pass strict OpenSpec validation.
- All three wheel/sdist pairs build and pass `twine check --strict`.
- Wheel runtime payloads are byte-identical to the prior release set, excluding
  distribution metadata and the viewer's transient `.build.lock`.
- All three wheel metadata/README payloads are free of `machinome-framework`.
- Fresh combined wheel installation on Linux/Python 3.11.14 resolves 119 packages
  without broken dependencies. The retained release smoke passes: installed
  origins, both exact CAD backends' 24 mm3 box, numeric/symbolic formulas,
  extraction boundary and viewer API 22/document schemas 1–9.
- Reinstallation from all three new sdists passes the same smoke and dependency check.
- Strict Sphinx manual rebuild passes without warnings, retained at
  `dist/docs-0.7-canonical-2026-09-20/`. Current landing/quickstart/contributing/
  upgrading links contain no old repository name. The three external CAD exports
  are reused from the prior release's verified artifacts; geometry was not
  regenerated or visually revalidated for this URL-only change.
- The canonical GitHub SSH remote responds to a read-only HEAD lookup.

The full suites and browser/CAD visual evidence remain those recorded in the
previous release report; they are not claimed as rerun here. No new architecture
ADR is needed: the naming refinement leaves ADR-130's runtime boundary intact.

## Publication steps remaining

Push the prepared framework, viewer and mechanics commits and ensure the pinned
example commits are remotely available before a documentation build. Publish
viewer 0.2.0, framework 0.7.0, then mechanics 0.1.0 from the exact new artifact
directories. Tag/create releases and verify an index-only combined installation
when the pilot authorizes those actions. Studio remains unpublished and outside
this release. No push, tag or upload was performed here.
