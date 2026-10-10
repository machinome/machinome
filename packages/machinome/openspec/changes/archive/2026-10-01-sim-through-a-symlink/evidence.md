# Evidence: sim-through-a-symlink

Run on the cycle worktree `machinome/WTs/sim-through-a-symlink`, branch
`sim-through-a-symlink`, cut from the bench `curta-findings` at 4d1440a
(itself `main` 8a8a267 plus the campaign plan), planning commit 707a8c8,
1 October 2026, with the workspace venv
(`/home/asa/devel/machinome/.venv/bin/python`, Python 3.12.3) and the
worktree first on `PYTHONPATH`.

## The cause, confirmed

The arithmetic of `AbstractBaseNode.__init__` on the Curta's two paths, with
the source as imported through the symlinked `PYTHONPATH` and the root as
discovery resolves it:

    src  = /home/asa/devel/machinome/projects/Calculators/Curta-Type-I-3x/simulation/clocked.py
    root = /mnt/data/machinome-projects/Calculators/Curta-Type-I-3x
    normpath(join(root/_build, relpath(dirname(src), root)))
      -> /mnt/home/asa/devel/machinome/projects/Calculators/Curta-Type-I-3x/simulation

`root` is resolved in `machinome/manifest.py` `_find_manifest`
(`os.path.realpath(origin)`); `src` was `inspect.getfile(cls)`, the module's
`__file__` as imported. Every other path of the build was already resolved
(see design.md, Context).

## Red first

`tests/test_project_through_a_symlink.py` on the unchanged tree (only the
test file added), `pytest -q tests/test_project_through_a_symlink.py`:

    E           AssertionError: '/tmp/machinome-symlinked-yhqf9443/real/link/symlinked_fixture_0' != '/tmp/machinome-symlinked-yhqf9443/real/_build/symlinked_fixture_0'
    E   AssertionError: '/tmp/machinome-symlinked-g1psfn9j/real' != '/tmp/machinome-symlinked-g1psfn9j/real/_build'
    E    : Machine builds in /tmp/machinome-symlinked-g1psfn9j/real/link/symlinked_fixture_1, outside the project build root /tmp/machinome-symlinked-g1psfn9j/real/_build
    FAILED tests/test_project_through_a_symlink.py::ProjectThroughASymlinkTest::test_both_spellings_share_one_build_directory
    FAILED tests/test_project_through_a_symlink.py::ProjectThroughASymlinkTest::test_sim_through_the_link_builds_under_the_build_root
    2 failed in 1.10s

With the link beside the project the climb lands inside the project
(`real/link/…`), which is writable, so the defect shows as a build
directory outside the build root rather than a `PermissionError`; on the
workspace's layout the same climb reaches `/mnt/home` and raises. (A first
red run also failed on an assertion of the test's own, `sim.state` listing
`arbor.turn`; a stepped `Sim`'s state is its drivers only, and the
assertion was corrected to `['crank']` before the run quoted above.)

## Green

After `self.src = os.path.realpath(self.get_source_file())` in
`machinome/node/base.py`:

    pytest -q tests/test_project_through_a_symlink.py
    2 passed in 1.11s

    pytest -q tests/test_named_models.py tests/test_source_set.py tests/test_external_wrapper_identity.py tests/test_running_simulation.py tests/test_missing_source_file.py tests/test_source_generation.py
    187 passed, 37 subtests passed in 24.19s

The whole suite, once, on the final content (code, tests and docs; before
the archive moved the change record):

    env -C <worktree> PYTHONPATH=<worktree> .venv/bin/python -m pytest -q
    4178 passed, 4 skipped, 53 warnings, 3076 subtests passed in 807.37s (0:13:27)

The suite keeps its persistent verdict store off (ADR-156's session pin),
so none of these passes was served from a memo of an earlier run.

`openspec validate --specs --strict` after the archive:
`Totals: 37 passed, 0 failed (37 items)`.

## The caller

The Curta (`projects/Calculators/Curta-Type-I-3x`, `main` 23c9e6f), run from
the symlinked path with the project on `PYTHONPATH` by that path. `-P`
keeps Python from putting the working directory (which `os.getcwd()`
reports resolved) at the front of `sys.path`, so the project is imported
through `PYTHONPATH` as the spike's `scenario.py` imported it; without
`-P`, a `python -c` caller imports the project through the resolved
working directory and never meets the defect. `PYTHONDONTWRITEBYTECODE=1`
keeps the run from writing bytecode into the project.

On the bench head (4d1440a, unchanged framework), `PYTHONPATH=<bench>:<Curta>`:

    env -C /home/asa/devel/machinome/projects/Calculators/Curta-Type-I-3x PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/asa/devel/machinome/machinome/WTs/curta-findings:/home/asa/devel/machinome/projects/Calculators/Curta-Type-I-3x /home/asa/devel/machinome/.venv/bin/python -P -c "
    import machinome; print(machinome.__file__)
    from simulation.clocked import ClockedCurta
    from machinome.simulation import Sim
    sim = Sim(ClockedCurta())
    print(sim.node.build_dir)
    "
      File "<frozen os>", line 225, in makedirs
    PermissionError: [Errno 13] Permission denied: '/mnt/home'

On this worktree, `PYTHONPATH=<worktree>:<Curta>`:

    env -C /home/asa/devel/machinome/projects/Calculators/Curta-Type-I-3x PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/asa/devel/machinome/machinome/WTs/sim-through-a-symlink:/home/asa/devel/machinome/projects/Calculators/Curta-Type-I-3x /home/asa/devel/machinome/.venv/bin/python -P -c "
    import machinome, simulation.clocked as m; print(machinome.__file__); print(m.__file__)
    from simulation.clocked import ClockedCurta
    from machinome.simulation import Sim
    sim = Sim(ClockedCurta())
    print(type(sim).__name__, sim.clocked, sim.node.build_dir)
    "
    /home/asa/devel/machinome/machinome/WTs/sim-through-a-symlink/machinome/__init__.py
    /home/asa/devel/machinome/projects/Calculators/Curta-Type-I-3x/simulation/clocked.py
    Sim True /mnt/data/machinome-projects/Calculators/Curta-Type-I-3x/_build/simulation

The module was imported through the symlinked spelling; the build
directory is the one a run from the real path uses (a `python -c` run from
the same directory on the bench, importing through the resolved working
directory, printed the same
`/mnt/data/machinome-projects/Calculators/Curta-Type-I-3x/_build/simulation`).
That directory already existed, so nothing was created. A marker file
touched in the session scratchpad before these runs, then
`find /mnt/data/machinome-projects/Calculators/Curta-Type-I-3x -newer <marker>`
after them, listed nothing; `/mnt/home` does not exist.

## The CLI

`machinome build`, `test`, `export` and `develop` construct nodes through the
same `AbstractBaseNode.__init__`, so the same line covers them. They were not
seen failing (the spike ran `machinome export` from the symlinked path)
because `loader._seed_project_path` inserts the resolved project root at the
front of `sys.path` before importing, so their modules carry resolved
`__file__` paths. The build directory no longer depends on that ordering. No
CLI code changed.

## ADR disposition

None, and ADR-159 is left unused. The change restores what build-pipeline
already promised ("the same artifact paths from any directory", anchored on
the discovered root) using the anchor every other path of the build already
uses; design.md records why the resolved path, not the written one, is that
anchor.

## Findings

- **The finding needs an import through the link, not only a working
  directory on it.** `os.getcwd()` is resolved by the kernel, so a module
  imported through `''` or a relative entry is resolved too. The trigger is
  a `sys.path` entry spelled through the link: a symlinked `PYTHONPATH`, or
  a script whose own directory is reached through a link. Videomaker's
  spike met it through `PYTHONPATH`.
- **On a writable layout the defect is silent.** Where the climb lands
  somewhere writable the node builds outside its project instead of
  raising (the test's fixture shows it landing in `real/link/…`). Any
  project caller that used a symlinked `PYTHONPATH` before this change may
  have left such stray directories; none were looked for.
- **`node.src` now reads resolved.** Nothing in the framework or its suite
  compared it with an unresolved spelling.
- The archive's sync added one trailing blank line at the end of
  `openspec/specs/build-pipeline/spec.md`; it is the CLI's output and was
  left as written.

## What was not done, and why

- **No change to build directory names, the build root's location, or an
  absolute `SOLID_BUILD_DIR`.** Out of the brief; a project reached by its
  real path builds exactly where it did.
- **No search for stray build directories** left by earlier symlinked runs
  in any project: writing or deleting in projects is outside this cycle.
- **No change to the viewer, Videomaker or the Curta.** Videomaker's
  evaluation may now run from the symlinked path; that is its own cycle.
- **`HISTORY.rst` was not edited.** The brief names it, but it has no
  `Unreleased` section; the framework's changelog with the `Unreleased`
  section is `docs/project/changelog.rst`, where `persistent-verdict-memo`
  recorded its bullet, and the bullet is there.
- **The studio's `shop-skills/machinome-api/SKILL.md`** is the
  orchestrator's, after the merge: its sentence "so every command behaves
  identically from any directory" wants "and through any symbolic link to
  the project", as `docs/concepts/node-tree.rst` now says.
