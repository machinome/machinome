# Evidence

## The failure

Read the Docs, project `machinome`, build #34734207 of the pushed `v0.7.0`
tag (446da34), 24 September 2026, `length` 901 s, `success` false. Its
command log (API v2):

| Command | Time |
| --- | --- |
| `pip install -r docs/requirements.txt` | 13 s |
| `pip install -r requirements.txt` | 35 s |
| `pip install "machinome-viewer @ git+…"` | 8 s |
| Metamaquina 2 export (`--fps 30 --frames 360`) | 568 s |
| Pascaline download and export | 3 s + 146 s |
| Curta export | cut off, no exit code |

The `latest` build before it (#34718094, `main` at 6a0ae5f) stopped the
same way: 648 s in the Metamaquina 2 export, then cut off inside the
Pascaline's.

## Red

`tests/test_docs_exports.py` rewritten and `tests/test_docs_structure.py`
edited before any other file, run against the configuration at 5dcecb9:

    18 failed, 13 passed, 77 subtests passed in 0.39s

The failures: the three example directives name exports outside
`docs/_exports/`; `.gitmodules` and the three example pages exist;
`.readthedocs.yaml` has `jobs`, `apt_packages`, a `nodejs` tool,
`submodules` and four install steps; the docs job checks out submodules,
installs OpenSCAD and Node, installs from two repository URLs and runs
three exports; `docs/requirements.txt` does not name the viewer; the
examples page does not link to machinome.org.

## Green

Same tests plus the other documentation tests, after the change:

    tests/test_docs_exports.py tests/test_docs_structure.py
    tests/test_viewer_documentation_links.py tests/test_sphinx_ext.py
    tests/test_profile_documentation.py tests/test_tutorial_counter.py
    42 passed, 78 subtests passed in 54.54s

## The manual builds from the requirements alone

A fresh virtualenv (Python 3.11) holding only `sphinx`, `sphinx_rtd_theme`
and a `machinome-viewer` 0.7.0 wheel built from the viewer repository's
`v0.7.0` tag (standing in for the PyPI upload; `machinome-viewer describe`
in that venv reports API 27, versions 1–13):

    python -m sphinx -b html -W --keep-going docs <out>
    build succeeded.

Before the change the same environment produced the three example-export
errors and, without `OCP` mocked, seven autodoc import failures; with the
mock and the examples gone, nothing. The workspace venv build with `-W
--keep-going` is clean too. Every tutorial export under `_machinome/` in
the output carries `index.html` and `machinome-viewer.js` from the
installed viewer beside its committed `manifest.json` and `models/`.

The built `examples.html` was read: it links `https://machinome.org/` and
`https://machinome.org/foundry/`, names a posed, a running and a clocked
machine by kind, and embeds no model. No `example-*.html` is built.

## Left in the repository

No reference to `docs/examples`, an `example-*` page or
`--recurse-submodules` remains outside `HISTORY.rst`'s account of earlier
releases and the archived changes.
