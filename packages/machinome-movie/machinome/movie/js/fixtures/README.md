# Shared fixtures

Fixtures both the Python suite and the JavaScript suite run, so the two
sides of the movie document cannot drift from each other. A fixture is added
once and paid for twice: a document one side does not handle fails that
side's suite.

- `documents/<name>.json` — valid `machinome-movie/0.1` documents. The Python
  suite asserts that evaluating the fixture movie of the same name (declared
  under that name in the fixture project's `[tool.machinome.movies]`, at
  `python/tests/fixtures/project/videos/<name>/movie.py`) yields exactly this
  document, written for this file (`root` points back at the movie). The Node
  suite asserts that it loads, validates against the schema, and resolves.
- `takes/<name>/<chapter-id>.json` — the speech double: an alignment record
  per chapter, in the shape the speech cache stores, so anchors resolve in
  tests without a provider. The Node suite installs them as the cached takes.
- `resolved/<name>.json` — the numeric episode the Node resolver produces
  from `documents/<name>.json` with `takes/<name>/`. Pinned by the Node
  suite; the Python suite does not read it.
- `invalid/<name>.json` — `{"name", "document", "must_mention": [...]}`: a
  document that must be refused, with the substrings the refusal names.
  Both suites iterate every file here. The substrings are locations,
  vocabulary and field names, chosen to be stable across languages, never a
  runtime's type names or number formatting.

`manifest.json` indexes the valid documents, `{"documents": [<name>, ...]}`,
so a new fixture is registered once and missed by neither side.

## The fixture project

`python/tests/fixtures/project/` is a tiny machinome project: a seesaw model
(`models/seesaw.py`), a hand-written posed export (`export/seesaw/`), a still
(`media/plate.png`), the take every fixture movie films (`videos/takes.py`)
and the movies. Its `export/seesaw/source-revision.txt` is the commit of the
project made this way, so that source pinned to it can be checked:

1. copy every file of the project except `export/`, `_build/` and
   `__pycache__/` into an empty directory;
2. `git init`, `git add -A`, and `git commit -m "Fixture project"` with
   author and committer `Videomaker fixture <fixture@videomaker.invalid>`,
   both dated `2026-09-30T00:00:00+00:00`, and no global or system Git
   configuration.

The Python suite makes that commit and asserts its hash. Changing any file
of the project changes the hash; re-pin the revision and re-evaluate the
documents together.
