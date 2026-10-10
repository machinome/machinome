# Documentation review evidence — 2026-09-20

Base/main: `4d747191f8a94cb72fa3a4bef23a9742b91f0acf`.
Planning commit: `1fd0e22`. Pilot approved sync/archive on 2026-09-20.
Primary `main` remains at the base. No runtime or ADR changes.

Before implementation, `rg machinome-mechanics.readthedocs docs` returned no
matches. The guide navigation, API reference, driving-law guide and upgrading
guide now link to the independent mechanics manual. Its four destination URLs
were checked against the completed local mechanics build.

Validation from the framework cycle worktree:

```sh
PYTHONPATH=. /home/asa/devel/machinome-studio/.venv/bin/python -m sphinx \
  -b html -W --keep-going -w docs/_build/warnings.log docs docs/_build/html
openspec validate mechanics-documentation-links --strict
git diff --check
```

All thirty pages build successfully; warnings log is empty. The three external
example exports were reused read-only from the existing `docs-0-7` worktree
through local ignored `_exports` symlinks under this worktree's `docs/examples/`.
Specifically, V8, Metamaquina2 and Clock 01 came from that worktree's matching
`docs/examples/<project>/docs/_exports/` directories. No example was rebuilt,
no submodule source was changed and no validation of new CAD geometry is claimed.
The published build still uses the repository's existing RTD export process.

The companion mechanics browser review checked the new manual at desktop and
mobile sizes, followed its internal links, exercised search, and checked links
from these four framework pages. No browser errors occurred. Screenshots are
in the mechanics worktree's ignored `_build/review/` directory.

Review preview: <http://localhost:8021/api-reference.html#mechanics-helpers>.
Mechanics preview: <http://localhost:8020/>.

Following the requested site review, the pilot approved sync/archive. The
user-documentation baseline now includes the mechanics manual requirement,
and the completed implementation record is archived as
`2026-09-20-mechanics-documentation-links`. Integration remains separate.
No push, publication or hosted RTD build has been performed.
