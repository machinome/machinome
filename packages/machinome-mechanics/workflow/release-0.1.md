# Machinome Mechanics 0.1.0 release

Version 0.1.0 is the first release of the independent formula package,
released on 23 September 2026 with Machinome 0.7.0. The release set is
Machinome 0.7.0 (Apache-2.0), Machinome Viewer 0.7.0 (AGPL-3.0-only) and
Machinome Mechanics 0.1.0 (Apache-2.0). The framework manual names this
version through its `mechanics_version` substitution.

The twelve foundational gear, screw, crank, delta and linkage helpers were
extracted from the framework's unreleased `machinome.mechanisms` package with
equations and signatures preserved; the [helper expansion](helper-expansion.md)
added twelve more before release, each validated in at least two projects.
The dependency is `machinome>=0.7.0`; solid-node 0.6 is historical formula
provenance, not an installable substitute.

## What the release was checked with

- `python -m pytest`: the formula suites, numeric/symbolic agreement,
  declarative and relation integration, and the documentation tests that
  keep the reference complete, the release stated, the framework links
  live and the reference free of project credits.
- `python -m sphinx -b html -n -W --keep-going docs docs/_build/html` and
  the `doctest` builder: strict manual and executable examples.
- `python scripts/check-dist`: wheel and sdist built, metadata checked,
  each installed and smoked outside the checkout. It uploads nothing.

Per-cycle evidence for each helper is in the archived OpenSpec changes and
in `helper-expansion.md`.

## Publishing

Publishing is the pilot's explicit decision. Upload after Machinome 0.7.0
is on the index, then verify in a fresh environment that
`pip install 'machinome[viewer,mechanics]'` resolves the whole set and that
`python -c "import machinome_mechanics"` succeeds. Push the repository and
tag `v0.1.0`; the Read the Docs project builds from the pushed `main`
([documentation maintenance](documentation.md)). The framework's default
installation remains independent of this package.
