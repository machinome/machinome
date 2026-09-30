# Shared fixtures

Fixtures both the Python suite and the JavaScript suite run, so the two
sides of the movie document cannot drift from each other. A fixture is added
once and paid for twice: a document one side does not handle fails that
side's suite.

- `documents/<name>.json` — valid `machinome-movie/0.1` documents. The Python
  suite asserts that evaluating the fixture movie of the same name
  (`python/tests/movies/<name>.py`) yields exactly this document. The Node
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

`manifest.json` indexes the valid documents so a new fixture is registered
once and missed by neither side.
