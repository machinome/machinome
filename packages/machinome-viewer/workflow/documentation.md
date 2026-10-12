# Building and checking the viewer's pages of the manual

The viewer's user pages are part of the Machinome manual (change
`join-viewer`, 12 October 2026): the how-to guides
`howto/browser-viewer.rst`, `howto/share-an-export.rst` and
`howto/embed-the-viewer.rst`, with the embedding example beside the last, and
the reference section `reference/viewer/`, all under
`packages/machinome/docs/`. They are built with the manual, by its
`docs/conf.py`, from its `docs/requirements.txt`. Workflow records belong
here, not in the user navigation.

## Local build

From `packages/machinome/` of the repository, with Python 3.12+:

```sh
python -m venv .venv-docs
.venv-docs/bin/python -m pip install -r docs/requirements.txt
.venv-docs/bin/python -m sphinx -n -W --keep-going -b html docs docs/_build/html
python -m http.server 8022 --bind 127.0.0.1 --directory docs/_build/html
```

Open <http://localhost:8022/howto/browser-viewer.html>. The build imports no
CAD backend and needs no Node: `docs/requirements.txt` installs the published
viewer, whose bundle the build copies beside the embedding guide with the
committed spinner export under `docs/_exports/spinner/`. The manual's source
path leaves this package out, so a source copy without a built bundle does
not shadow the installed viewer.

Check reference coverage with `npm test --workspaces` from the repository's
root (the widget's `documentation.test.ts` reads `reference/viewer/`), and
the pages and facts with `python -m pytest tests/test_documentation.py` from
`packages/machinome-viewer/`. Browser review evidence belongs in
`documentation-review.md`.

After building HTML, run `python scripts/check-docs-browser.py` from
`packages/machinome-viewer/` in an environment with Playwright and Chromium,
naming the built HTML directory if it is not `docs/_build/html` of the
manual. It checks the viewer's pages' local links, desktop and mobile layout,
search, the live spinner and the exact running and clocked reference
snippets, and writes screenshots and a report to this package's
`_build/docs-review/`.
