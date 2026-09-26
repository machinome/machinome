# Evidence — write-the-studio-manual

Filled in as the increments land; the reviewer reads it instead of
re-running the cycle. A command without its output, a red step recorded only
as "failed", is not evidence.

## 0. Baseline

Worktree: `machinome-studio/WTs/write-the-manual`, branch `write-the-manual`,
starting head `979a0a6` ("Relicense Machinome Studio as AGPL-3.0-or-later").

Studio suite in the primary checkout before the change (workspace venv,
Python 3.12.3):

```
$ python -m unittest discover -s tests
Ran 341 tests in 151.164s
OK (skipped=1)
```

Sibling manuals built for link verification (both exit 0):

```
$ python -m sphinx -b html -q docs docs/_build/html      # in machinome/
$ python -m sphinx -b html -q docs docs/_build/html      # in machinome-viewer/
```

## 1. Red

(to be filled)

## 2. Green

(to be filled)

## 3. Read as the reader

(to be filled)

## 4. Out of scope, found while applying

(to be filled)
