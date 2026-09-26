# Building and hosting the user manual

The manual is `docs/`, built with Sphinx and `sphinx-rtd-theme` like the
framework, viewer and mechanics manuals. Release facts are read once in
`docs/conf.py`: the version from `pyproject.toml`; the required viewer API,
the Claude model and reasoning sets and the Build volume from the floor's
source, read as text; and the framework version the studio runs against,
the one hand-maintained value. Pages use the substitutions and never the
numbers.

## Local build

From the repository root, with Python 3.11 or later:

```sh
python -m venv .venv-docs
.venv-docs/bin/python -m pip install -r docs/requirements.txt
.venv-docs/bin/python -m sphinx -b html -n -W --keep-going docs docs/_build/html
python -m http.server 8023 --bind 127.0.0.1 --directory docs/_build/html
```

Open <http://localhost:8023/>. The build imports nothing of the floor, the
framework or the viewer, and needs no CAD tool or backend. The studio's
own `.venv/` carries the same two pins through the `docs` extra
(`pip install -e '.[docs]'`), which `tests/test_documentation.py` keeps
identical to `docs/requirements.txt`.

That test holds the manual's shape: the pages, the derived facts, no
caveat outside the status page, no project name or checkout path, every
launcher option documented, sibling links from an allowlist, and the
records kept out of `docs/`. Run it with the rest of the suite. Before
adding a link to the framework's or the viewer's manual, open the target
in that manual's built HTML and add it to the test's allowlist.

Sphinx renders `.rst` only; `docs/adrs/`, `docs/design/` and
`docs/product/` are excluded by name in `conf.py` and stay where
`AGENTS.md` names them.

## Read the Docs

Nothing is hosted. The intended project slug is `machinome-studio`, which
would serve <https://machinome-studio.readthedocs.io/>; `.readthedocs.yaml`
is ready for it, installing `docs/requirements.txt` alone and failing on
warnings. Importing the repository into Read the Docs is the pilot's
decision; the repository is public. When a slug is chosen, add a `Documentation` URL to
`pyproject.toml`, and list the studio's manual in the framework's
`reference/manuals.rst` through a framework change.

## A release

A release turns the `Unreleased` section of `CHANGELOG.md` into the
version's section, edits the status page, and moves `machinome_version` in
`conf.py` when the framework moved; the studio's own version comes from
`pyproject.toml`. The three sibling manuals state the framework's release
date; the studio states none until it releases.
