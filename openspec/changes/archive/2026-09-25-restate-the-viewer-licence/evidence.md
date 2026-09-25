# Evidence

## Red

`LicenceWordingTest` added to `tests/test_docs_structure.py` and run against
4195a53:

    9 failed, 1 passed, 37 subtests passed

The failures name `why.rst`, `start/install.rst`, `concepts/publishing.rst`,
`reference/manuals.rst`, `project/status.rst`, `project/changelog.rst`,
`project/upgrading.rst`, `releases/release-0.7.rst` and `README.rst`.

## Green

    tests/test_docs_structure.py tests/test_profile_documentation.py
    tests/test_viewer_documentation_links.py: 12 passed, 110 subtests passed

    python -m sphinx -b html -W --keep-going docs <out>: build succeeded.

No `AGPL-3.0-only` remains under `docs/` outside `docs/adrs/`, nor in
`README.rst` or `pyproject.toml`; `HISTORY.rst` keeps its 0.6 account.
