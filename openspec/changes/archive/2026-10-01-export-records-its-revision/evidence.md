# Evidence: export-records-its-revision

Framework finding 3 of "Three findings from filming the clocked Curta
(1 October 2026)" (`workflow/warts.md`), under the pilot's ruling of
1 October 2026 recorded in `workflow/ongoing/curta-film-findings/plan.md`.

- Worktree: `machinome/WTs/export-records-its-revision`, branch
  `export-records-its-revision`.
- Base: 4d1440a (`workflow: plan for the three findings from filming the
  clocked Curta`), the head of bench `curta-findings` when this worktree was
  cut. The bench has since gained `sim-through-a-symlink` (707a8c8, 6d49854,
  744e17d); this branch was not rebased onto it.
- Planning commit: 02ebc26.
- Python: the workspace venv, `PYTHONPATH=<worktree>`.

## The pinned manifest (task 1.1)

At 4d1440a, with no implementation, the fixture project of
`tests/test_export_source.py` (`[tool.machinome] model = "design.part:Part"`,
`design/part.py` a `Solid2Node` returning `cube(1)`, the `machinome new`
`.gitignore`, every file's mtime 1700000000 s, no Git) was exported with
`machinome export --no-widget` from two locations under the worktree's
ignored `build/`:

    $ cmp base-export-1/manifest.json base-export-2/manifest.json && echo IDENTICAL
    IDENTICAL
    cd58b466dd60cef718f21e0d57fb895632df508f5a8eef30282158292ec86aa1  base-export-1/manifest.json

That manifest is `tests/fixtures/export_outside_a_repository.json`
(version 2, model `models/design/part-Part-8570a2e1669f.stl`, piece
`bf92c475bae3`, no trailing newline).

## Red first (task 2.2)

`tests/test_export_source.py` on the unchanged `machinome/core/export.py`:

    FAILED tests/test_export_source.py::ExportSourceRecordTest::test_a_committed_project_records_its_revision
    FAILED tests/test_export_source.py::ExportSourceRecordTest::test_a_modified_tracked_file_marks_the_record_dirty
    FAILED tests/test_export_source.py::ExportSourceRecordTest::test_an_ignored_file_leaves_the_record_clean
    FAILED tests/test_export_source.py::ExportSourceRecordTest::test_an_untracked_file_marks_the_record_dirty
    FAILED tests/test_export_source.py::ExportSourceRecordTest::test_no_git_records_nothing_and_says_nothing
    FAILED tests/test_export_source.py::ExportSourceRecordTest::test_the_record_writes_nothing_in_the_repository
    6 failed, 2 passed in 12.83s

The committed-project case, through the real `machinome export`:

    E       AssertionError: None != {'revision': 'dfae50247e71836ba842863a17cdfab228c50045', 'dirty': False}

The dirty cases:

    E   AssertionError: 'source' not found in {'format': 'machinome-export', 'version': 2, 'animation': {'fps': 30, 'frames': 360}, 'drivers': {}, 'instructions': {}, 'root': {'name': 'Part', 'type': 'LeafNode', 'color': None, 'mtime': 1700000000.0, 'operations': [], 'model': 'models/design/part-Part-8570a2e1669f.stl', 'piece': 'bf92c475bae3'}, 'pieces': [{'id': 'bf92c475bae3', 'name': 'Part', 'sources': ['design/part.py'], 'models': ['models/design/part-Part-8570a2e1669f.stl'], 'count': 1, 'size': [1.0, 1.0, 1.0], 'volume': 1.0, 'watertight': True}]}

The two in-process cases:

    E       ImportError: cannot import name '_source_record' from 'machinome.core.export'

The two that passed are the non-repository and no-commit byte-identity
cases: on the base code they pass by construction, which is what proves the
pin is the base's bytes; after the change they are the guard that the record
never leaks into a document outside a repository.

The index guard discriminates. In a scratch repository with one committed
file then `touch`ed (stat-dirty, content-clean), the index's mtime:

    before=1790843935.2026-10-01 08:38:55.098840573 +0000
    optional-locks-0=1790843935.2026-10-01 08:38:55.098840573 +0000
    plain=1790843935.2026-10-01 08:38:55.151842268 +0000

Plain `git status` rewrote the index; `GIT_OPTIONAL_LOCKS=0 git status` did
not.

## Green

    $ pytest -q tests/test_export_source.py
    8 passed in 11.65s

    $ pytest -q tests/test_export.py tests/test_pieces.py tests/test_markings.py tests/test_cli_lazy_imports.py
    160 passed, 5 warnings, 81 subtests passed in 31.22s

    $ pytest -q tests/test_docs_structure.py tests/test_release_records.py tests/test_docs_exports.py tests/test_viewer_documentation_links.py
    34 passed, 181 subtests passed in 0.94s

The whole suite, first run, on the implementation before the fixture fix
below:

    FAILED tests/test_build_lock.py::LockParticipantsTest::test_export_releases_the_lock_after_building
    1 failed, 4183 passed, 4 skipped, 53 warnings, 3076 subtests passed in 662.80s (0:11:02)

    machinome/core/export.py:129: in export_node
        source = _source_record(project_root(node.src))
    E   TypeError: expected str, bytes or os.PathLike object, not Mock

That test exports a bare `Mock` to observe the build lock. A node always
has a source inside a project (its constructor resolves `project_root`), so
the fixture now gives the mock a `src` in a temporary project with a
`pyproject.toml`; the test's assertions are unchanged. The fixed module and
the new one:

    $ pytest -q tests/test_build_lock.py tests/test_export_source.py
    24 passed in 23.27s

The whole suite, once, on the final content:

    $ pytest -q
    4184 passed, 4 skipped, 53 warnings, 3076 subtests passed in 550.21s (0:09:10)

## The caller: the clocked Curta (task 5.2)

From the real path, worktree first on `PYTHONPATH`, the build directory and
the output under the worktree's ignored `build/`, no bytecode written:

    $ env -C /mnt/data/machinome-projects/Calculators/Curta-Type-I-3x \
        PYTHONPATH=<worktree> PYTHONDONTWRITEBYTECODE=1 \
        SOLID_BUILD_DIR=<worktree>/build/curta-build \
        machinome export clocked_curta --no-widget -o <worktree>/build/curta-export
    Exported to <worktree>/build/curta-export
    wall=80.61 s, maxrss=1240596 KB

The manifest:

    source:  {"revision": "23c9e6f48697d6bf9a0ed07c64355dd8ffc40540", "dirty": true}
    version 8 keys ['format', 'version', 'animation', 'drivers', 'states', 'instructions', 'bindings', 'clocked', 'root', 'pieces', 'source']

Beside it:

    $ git -C <project> rev-parse HEAD
    23c9e6f48697d6bf9a0ed07c64355dd8ffc40540
    $ git -C <project> status --porcelain | wc -l
    5

The five entries are untracked: the assembly video, `CREDITS`,
`curta-2x-files/`, `export/` (which holds the hand-written
`source-revision.txt`), `screenshots/reverser_inspection.png`. Nothing in the
project is newer than the run's start (`find -newermt` outside `.git`
printed nothing), `.git/index` kept its mtime (04:31:01, before the run), the
porcelain count was 5 before and after, and the log has no warning. The
document is version 8 as before; `source` is its last key.

## Manual build

`python -m sphinx -E -b html -n -W --keep-going docs docs/_build/html`
exits 1 on five nitpick warnings, none on a page this change touches, all
in files it does not change:

    docs/reference/api.rst:23: WARNING: py:meth reference target not found: AssemblyNode.simulate [ref.meth]
    docs/reference/api.rst:35: WARNING: py:attr reference target not found: AssemblyNode.time [ref.attr]
    docs/reference/api.rst:76: WARNING: py:class reference target not found: name keyword [ref.class]
    machinome/simulation/sim.py:docstring of machinome.simulation.Sim.initial:3: WARNING: py:class reference target not found: The snapshot taken at construction [ref.class]
    machinome/simulation/sim.py:docstring of machinome.simulation.Sim.state:12: WARNING: py:class reference target not found: The current snapshot by qualified id [ref.class]

The changed pages (`concepts/publishing`, `reference/cli`,
`project/changelog`) build without a warning, the `An export`_ section link
resolves, and the JSON example lexes.

## Findings

1. **An export written inside the project dirties the next one.** The
   ruling counts every untracked, non-ignored entry, so a project that keeps
   its exports in its own tree without ignoring them (the Curta's `export/`
   is untracked today) records `dirty: true` on every export after the
   first. The record is right by the rule; whether the Curta (and Leonardo)
   should ignore their export directories, or the marker should exclude the
   export's own output directory, is the pilot's. Not changed here.
2. **The Curta's caller record is dirty** for untracked files that are not
   model sources (a video, `CREDITS`, `curta-2x-files/`, a screenshot,
   `export/`). A consumer that refuses dirty exports would refuse this one;
   committing or ignoring them is project work.
3. **The build's `viewer.json` and the browser-snapshot document** do not
   carry `source` (decision 1). No consumer has asked for it there: the
   floor and `machinome develop` read the live document of the working
   tree, where a revision says nothing the working tree does not. A
   question, not a change.
4. **The framework's committed tutorial exports** (`docs/_exports/`), when
   next regenerated from inside the framework repository, will carry the
   framework's revision and, mid-cycle, `dirty: true`. Nothing compares
   them byte for byte; regenerating them is not part of this change.
5. **`exclude_build_from_git` does nothing in a worktree** (`.git` is a
   file), so a project worked from a Git worktree whose `.gitignore` lacks
   `_build*` sees its build directory untracked, and its exports after the
   first are dirty. Recording before the build keeps the first one clean.
   Pre-existing behaviour, recorded only.
6. **Strict manual build:** the five nitpick warnings above make
   `sphinx -n -W` exit 1 in this venv at this base, independent of this
   change.

## What was not done, and why

- No `source-revision.txt`: Videomaker and the gallery script stop reading
  and writing it in their own repositories, after this lands in `main`.
- No viewer change and no document version: the record is additive.
- No exclusion of the output or build directory from `dirty`: the ruling
  defines the marker as everything `git status --porcelain` lists (finding
  1).
- No `source` in `viewer.json` or the browser snapshot (finding 3).
- No author, date, branch, remote or path list.
- Not rebased onto the bench's newer head (744e17d); the merge is the
  orchestrator's.
- The studio's `shop-skills/machinome-api/SKILL.md` is not edited here; the
  orchestrator updates it in that repository.
