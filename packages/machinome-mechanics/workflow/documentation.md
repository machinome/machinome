# Maintaining the user manual

The helpers' user pages are part of the Machinome manual, under
`packages/machinome/docs/`: the reference section `reference/mechanics/` (its
index, the conventions page and one page per formula family) and the how-to
`howto/mechanism-formulas.rst`, whose example project sits beside it in
`howto/mechanism-formulas/`. They are built with that manual and follow its
conventions. Keep provenance, checklists, release procedures and validation
logs in this package's `workflow/`.

## Build and preview HTML

The pages build with the Machinome manual, from the framework's directory
`packages/machinome/`, in an environment holding its `docs/requirements.txt`:

```sh
python -m sphinx -b html -n -W --keep-going docs docs/_build/html
```

The HTML build imports no runtime package and needs no CAD tools. The
manual's `mechanics_version` states this package's version, and the
framework's `tests/test_release_records.py` holds it to `pyproject.toml`.

## Check examples and the reference

From this package's directory, `packages/machinome-mechanics/`, on the
repository's synced workspace:

```sh
python -m pytest
```

`tests/test_documentation.py` runs every `>>>` example of the section's pages
and of the how-to with the standard library's `doctest`, under the flags
Sphinx's doctest builder uses, with the how-to's example project on the path;
it compares every `__all__` entry and its signature with the reference, and
keeps the pages' links inside the manual. No mocked framework is used. When
adding a helper, add its Python-domain directive, parameters, result,
conventions, domain and an executable example to its family page, then add it
to the section index's tables. `python -m sphinx -b doctest docs
docs/_build/doctest` from the framework's directory, with the example
directory on `PYTHONPATH`, runs the same examples through Sphinx.
