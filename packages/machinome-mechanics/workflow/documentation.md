# Maintaining the user manual

`docs/` contains user-facing RST sources and assets. Use the framework's
`sphinx_rtd_theme` and its normal navigation conventions. Keep provenance,
checklists, release procedures and validation logs in `workflow/`.

## Build and preview HTML

From the repository root, using Python 3.12 as on Read the Docs:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r docs/requirements.txt
.venv/bin/python -m sphinx -b html -n -W --keep-going docs docs/_build/html
.venv/bin/python -m http.server 8020 --bind 127.0.0.1 --directory docs/_build/html
```

Open <http://localhost:8020/>. Stop the preview with Ctrl-C. `make -C docs html`
is equivalent when `sphinx-build` from that environment is on PATH.

The HTML build imports no runtime package and needs no CAD tools, external
machine exports, unpublished wheels or sibling checkouts. The explicit Sphinx
function directives are checked against the real public API during testing.
Version text is read from `pyproject.toml`, including in a source distribution.

## Check examples and the reference

Use an environment with the actual framework and mechanics installed. Before
publication, supply both local repositories so pip can resolve the dependency:

```sh
python -m pip install -e /path/to/machinome -e '.[dev,docs]'
python -m pytest
python -m sphinx -b doctest -W --keep-going docs docs/_build/doctest
python scripts/check-dist
```

Doctests exercise the real formulas, symbolic expressions and motion-law
example. No mocked framework is used. The reference test compares every
`__all__` entry and its signature with the manual. When adding a helper, add
its Python-domain directive, parameters, result, conventions, domain and an
executable example, then link it from the reference index. Keep build dependency
pins in `docs/requirements.txt` and the `docs` extra aligned.

## Read the Docs setup

The intended project slug is `machinome-mechanics`, with the manual at
<https://machinome-mechanics.readthedocs.io/en/latest/>. The repository contains
the version-2 `.readthedocs.yaml` configuration: Ubuntu 24.04, Python 3.12,
`docs/requirements.txt`, `docs/conf.py`, warnings treated as errors.

After the approved change is integrated and pushed, import
`https://github.com/machinome/machinome-mechanics` into Read the Docs if it is
not already connected. Select the `machinome-mechanics` slug and `main` as the
default branch, then verify the GitHub integration/webhook and trigger the
first build. Later pushes to an enabled branch trigger builds through that
integration. Enable release tags as documentation versions when published.

A successful local build does not create an RTD project or prove a hosted
deployment. If a different slug is necessary, update the package Documentation
URL, README, `html_baseurl` and the companion framework links together.

The framework links here from its guides and reference; this manual links back
for installation, model authoring and motion semantics. Do not duplicate the
helper reference into the framework or require a live inventory fetch to
render either manual.
