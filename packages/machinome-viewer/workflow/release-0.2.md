# Machinome Viewer 0.2.0 release preparation

Publication pending. This is the companion to Machinome 0.7.0; neither this
document nor the local release artifacts mean the package has been published.

The Python distribution and bundled widget are both version 0.2.0. The widget
reports API 22 and reads document schemas 1–9, including running `Play`
contact laws. It retains legacy solid-node document reading and uses the
Machinome command, entry point, browser global and asset names.

Validation on Linux / Python 3.12 / Node 24:

- TypeScript typecheck and 1,243 widget tests passed.
- Python/browser suite: 181 tests and 18 subtests passed; two optional Curta
  project measurements skipped because their external fixture was unavailable.
- Wheel and source distribution build, strict metadata validation, and installed
  `describe` smoke are part of the matching framework release record at
  `workflow/archive/release-0.7-2026-09-20/README.md`.

Release order: publish this package before the framework's viewer extra is
advertised as installable. The framework is 0.7.0 and mechanics is 0.1.0;
these products retain independent version numbers. The widget npm package is
private and ships inside the Python package; no npm publication is planned.

To reproduce packaging: `python -m build`, then
`python -m twine check --strict dist/*`. Install the wheel in a fresh environment
outside the repository and run `machinome-viewer describe`; expect API 22,
version 0.2.0 and document versions 1 through 9. The sdist carries the bundle
and source; verify it independently as well.

Pushing, tagging and uploading remain the maintainer's separate release action.
