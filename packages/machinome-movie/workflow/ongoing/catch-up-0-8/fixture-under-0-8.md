# fixture-under-0-8: the fixture project on machinome 0.8

Status: done on branch `fixture-under-0-8` (from `catch-up-0-8` e9b08f9),
6 October 2026; a narrow adjustment under `AGENTS.md` (maintenance
preserving ratified behaviour), no OpenSpec change. Not integrated.

## The red

From the worktree, against the workspace venv (machinome 0.8.0):

```
$ PYTHONPATH=<worktree>/python .venv/bin/python -m pytest python/tests -q
...
python/tests/test_declarations.py:16: in <module>
    from models.seesaw import Seesaw
python/tests/fixtures/project/models/seesaw.py:3: in <module>
    from machinome.node import AssemblyNode, CadQueryNode
../../../machinome/machinome/node/__init__.py:192: in __getattr__
    raise ImportError(
E   ImportError: module 'machinome.node' has no attribute 'AssemblyNode': the root of machinome.node exports nothing, and 'AssemblyNode' is imported from its module, 'machinome.node.assembly'. Write `from machinome.node.assembly import AssemblyNode`.
=========================== short test summary info ============================
ERROR python/tests/test_declarations.py
ERROR python/tests/test_evaluation.py
ERROR python/tests/test_take.py
!!!!!!!!!!!!!!!!!!! Interrupted: 3 errors during collection !!!!!!!!!!!!!!!!!!!!
3 errors in 1.89s
```

The framework's refusal for the other name reads the same way:
`'CadQueryNode' is imported from its module, 'machinome.node.cadquery'`.

## What changed and why

- `models/seesaw.py` and `models/counter.py` import `AssemblyNode` from
  `machinome.node.assembly` and `CadQueryNode` from
  `machinome.node.cadquery`, the modules the refusal names and the
  framework's own tutorial (`docs/tutorial/counter/`) now spells.
- Each model also lost one blank line above its first class (seesaw:
  between the docstring and the imports; counter: between
  `import cadquery as cq` and the `machinome` imports), so that the second
  import line does not move the code below it. The fixture movies excerpt
  both models by line (`Source("../models/seesaw.py", lines=(22, 24))`,
  `Source("../models/counter.py", lines=(150, 153))`, with `through_line`
  and `line=` on the same numbers), and those numbers are pinned in the
  tests, the invalid fixtures' refusal words and the manual
  (`docs/declaring-a-movie.md`). A first re-pin with the extra line kept
  was refused at `tour`: `Balance.source: cues[3]: emphasize: the token
  'beam' is absent from the excerpt declaration (../models/seesaw.py, lines
  22 to 24)`. Lines 22 to 24 of the seesaw and 150 to 153 of the counter
  read exactly as before. The excerpts' line numbers are part of the fixture
  documents, so keeping them reading as before is the smaller and truer
  change than moving every number by one (approved by the orchestrator).
- Every other framework import of the fixture project and of
  `python/machinome_movie/` (`machinome.simulation`, `machinome.math`,
  `machinome.parameters`, `machinome.node.markings`,
  `machinome.node.declarative`, `machinome.motion.*`) was checked by import
  under 0.8.0 and resolves; none changed.

## The re-pin

`node scripts/pin-fixture-project.mjs --python .venv/bin/python --machinome .venv/bin/machinome`:

```
Export counter: made from 20bb29a7783c3840bae32d3f7ae10a26acb22eab, manifest changed, written to python/tests/fixtures/project/export/counter.
Export seesaw: made from 20bb29a7783c3840bae32d3f7ae10a26acb22eab, manifest changed, written to python/tests/fixtures/project/export/seesaw.
Revision: 20bb29a7783c3840bae32d3f7ae10a26acb22eab, recorded by every export's source.
Document minimal: changed, written to fixtures/documents/minimal.json.
Document tour: changed, written to fixtures/documents/tour.json.
Document count: changed, written to fixtures/documents/count.json.
Now run node scripts/pin-resolved.mjs minimal tour count and review the pins before committing.
```

then `node scripts/pin-resolved.mjs minimal tour count`. The fixture files
changed, each reviewed by hand:

| file | what changed |
|---|---|
| `python/tests/fixtures/project/export/seesaw/manifest.json` | `source.revision` 10b189d… → 20bb29a…; every node's `mtime` (the export was made again, as `fixtures/README.md` says it always differs) |
| `python/tests/fixtures/project/export/counter/manifest.json` | the same two |
| `fixtures/documents/{minimal,tour,count}.json` | `model.sourceRevision` only |
| `fixtures/resolved/{minimal,tour,count}.json` | `model.sourceRevision` only |

No STL under either export changed by a byte, no manifest field was added or
removed, and no number but the `mtime`s moved: the 0.8 framework exports
these two models as 0.7 did.

Left as they were: `fixtures/invalid/take-initial-incomplete.json` still
names 10b189d… and the other invalid fixtures older revisions (warts.md,
Fix-warts 11: no refusal depends on it); `test_evaluation.py` writes
10b189d… into a sidecar the evaluation is asserted not to read.

## The suites

- Python, `PYTHONPATH=<worktree>/python .venv/bin/python -m pytest python/tests -q`:
  298 passed, 0 skipped, 0 failed, 26.9 s (28.1 s wall).
- Node, `VIDEOMAKER_VIEWER_BUNDLE=<machinome-viewer>/machinome_viewer/widget/dist/machinome-viewer.js npm test -- --cold`
  (viewer API 29): 52 files, 501 tests passed, 0 skipped, 0 failed,
  "Test memo: 0 passed from the memo, 501 run", 933 s (934 s wall). Layer
  6 ran: `real-viewer` (7), `take` (6), `player` (1), `transport` (2).
  `node_modules` in the worktree is a link to the primary checkout's, as in
  the other worktrees; its lockfile is the branch's.

No EMFILE was met.

## Changelog and manual

Nothing reader-facing changed: no page, README or package metadata names the
framework's version or the old spelling (`python/pyproject.toml` depends on
`machinome` unpinned), so no changelog bullet.

## Findings

- The fixture movies excerpt the models by line number, and those numbers
  are pinned across the tests, the manual and the invalid fixtures, so any
  change to a model's line count above an excerpt is a change to all of
  them. Worked around here by keeping the line count.
- `scripts/pin-fixture-project.mjs` writes as it goes: the refused first
  run had already replaced both exports and `documents/minimal.json` when
  `tour` was refused, leaving the tree half re-pinned. Its comments do not
  say otherwise, but neither do they say so; the second, accepted run
  rewrote everything. Recorded as `warts.md`, Catch-up 2.
- Not in this cycle's scope: `README.md` and `AGENTS.md` say no published
  viewer release declares API 28 or 29; machinome-viewer 0.8.0 is on PyPI
  (checked 6 October 2026), which the workspace records as declaring API 29.

## test-cli-in-the-worktree

Status: done on the same branch, its own commit, 6 October 2026; a narrow
adjustment (test hygiene) for `warts.md`, The player 11.

`python/tests/test_cli.py`'s `run()` gave its child an environment of `PATH`
alone, so from a worktree `python -m machinome_movie` resolved to the venv's
editable install, the primary checkout's package. It now passes the
checkout's `python/` on the child's `PYTHONPATH`, as `test_watch.py`'s
`environment()` does, with the same comment.

The red, by a mutation: `main()` of this worktree's
`python/machinome_movie/__main__.py` was made to print `MUTATION: the
worktree package ran` and exit 97 (`python -m machinome_movie list x` with
the worktree's `PYTHONPATH` exits 97). Before the fix, with the mutation in
place, `python -m pytest python/tests/test_cli.py -q` gave `5 passed in
4.91s`: the children ran the primary's package. After the fix, with the
mutation still in place, `5 failed in 0.79s`, each child exiting 97 with the
mutation's message. With the mutation removed, `5 passed in 4.96s`, and the
whole Python suite 298 passed in 28.0 s.

## status-claims

Status: done on the same branch, its own commit, 6 October 2026; a narrow
adjustment (status honesty) for `warts.md`, Catch-up 3.

machinome-viewer 0.8.0 is on PyPI (0.7.0, 0.7.1 and 0.8.0 listed), tagged
`v0.8.0` in its repository, and its `CHANGELOG.md` says it "declares viewer
API 29". Three pages said API 28 and 29 were in the source checkout only:

- `README.md`: the API 28 sentence loses its release clause, and the API 29
  sentence ends "machinome-viewer 0.8.0 declares it", the release stated
  once (API 29 carries 28). The README is 97 bytes and one line shorter.
- `AGENTS.md`, "Current status": API 28 and API 29 are each "which
  machinome-viewer 0.8.0 declares".
- `docs/FORMAT.md`, "Format 0.3": the parenthesis keeps what API 28 adds and
  drops the release clause, the README being where the release is stated.

README line 139 ("For a 0.3 episode that needs Viewer API 28 it also reads
the selected bundle's `viewer API` banner") states no release and is
unchanged. No pin asserted the old wording. A pin in
`test/repository.test.mjs` (`status-claims`) now refuses the old phrases in
the three pages and asks the README for the release; it failed on the old
text ("README.md: the viewer's release") and passes on the new. Node `pure`
project 252 passed (25 files, 4.3 s); Python suite 298 passed (27.5 s).
