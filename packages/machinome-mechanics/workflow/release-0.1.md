# Machinome Mechanics 0.1.0 release preparation

Publication pending. This is the first release of the independent formula
package, paired with Machinome 0.7.0 and Viewer 0.2.0.

The twelve gear, screw, crank, delta and linkage helpers are imported from
`machinome_mechanics`, replacing the unreleased framework-owned
`machinome.mechanisms` package. Their equations and signatures are preserved.
The dependency is `machinome>=0.7.0`; solid-node 0.6 is historical formula
provenance, not an installable substitute for this dependency.

Validation on Linux / Python 3.12: 30 tests and 24 subtests pass, including
numeric/symbolic agreement and declarative/motion integration. Distribution
builds, strict metadata checks and isolated installation are recorded with the
matching framework under `workflow/archive/release-0.7-2026-09-20/README.md`.

Publish after Machinome 0.7.0, then verify a fresh
`pip install 'machinome[viewer,mechanics]==0.7.0'` resolves the whole set.
The framework's default installation remains independent of this package.

To reproduce local checks: `python -m pytest`, `python scripts/check-dist`.
To retain release artifacts: `python -m build` followed by
`python -m twine check --strict dist/*`. Install and smoke both wheel and
sdist outside the checkout, checking numeric and symbolic formulas.

No push, tag, index upload or remote release is performed by these checks.
