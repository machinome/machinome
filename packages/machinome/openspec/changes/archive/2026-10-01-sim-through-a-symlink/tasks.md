## 1. Red first

- [x] 1.1 Add `tests/test_project_through_a_symlink.py`: a temporary
  project (resolved temporary directory, `pyproject.toml` with
  `[tool.machinome]`, a package holding a plate part and an assembly
  root with one driver) and a symbolic link to it beside it.
  `SOLID_BUILD_DIR` unset and the build anchor cleared, so the build root
  is the project's own `_build`. Import the node class through the
  link's path on `sys.path`, with the working directory on the link,
  construct the node and `Sim(node, 0.1)`; assert the node's build
  directory is under `<resolved root>/_build` and that nothing was
  created in the project outside `_build`. Import the same class through
  the resolved path and assert the two build directories are equal.
- [x] 1.2 Run it on the unchanged tree and record the failing assertion
  verbatim in `evidence.md` (the build directory outside the build root).

## 2. The fix

- [x] 2.1 `machinome/node/base.py`, `AbstractBaseNode.__init__`: take
  `self.src` as `os.path.realpath(self.get_source_file())`, with a
  comment saying why the anchor is the resolved path.
- [x] 2.2 Run the focused test green, then the neighbouring suites that
  read build directories and source sets (`tests/test_named_models.py`,
  `tests/test_source_set.py`, `tests/test_external_wrapper_identity.py`,
  `tests/test_running_simulation.py`).

## 3. Records

- [x] 3.1 `docs/project/changelog.rst`, `Unreleased`: one bullet.
- [x] 3.2 `docs/concepts/node-tree.rst`: "every command behaves the same
  from any directory" gains "and through any symbolic link to the
  project".
- [x] 3.3 `docs/architecture.md`, build pipeline: the resolved anchor in
  one sentence.
- [x] 3.4 No ADR (decision recorded in design.md: the change restores the
  contract with the anchor the build already uses).

## 4. Proof and completion

- [x] 4.1 The whole framework suite once on the final content; summary
  line verbatim in `evidence.md`.
- [x] 4.2 The caller: from
  `/home/asa/devel/machinome/projects/Calculators/Curta-Type-I-3x` (the
  symlinked path), with the worktree first on `PYTHONPATH` followed by the
  symlinked project path, construct `Sim(ClockedCurta())` and print its
  node's build directory; quote the command and its last lines. Write
  nothing in the project beyond its own ignored `_build`.
- [x] 4.3 Sync the delta into `openspec/specs/build-pipeline/spec.md` and
  archive the change with the OpenSpec CLI; write `evidence.md` in the
  archived change; `openspec validate --strict` on the specs.
