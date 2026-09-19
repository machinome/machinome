# Tasks — import the artifact by path

Red first: every test in section 1 must fail against the current code, for
the stated reason, before anything in section 2 is written.

## 1. Prove the failure

- [x] 1.1 Add the cross-package fixture `tests/cross_package_project/`:
  `parts.py` declaring a rigid `Solid2Node`, an exact `CadQueryNode`, a
  `MolejoNode` with one translational port, a leaf whose `render()` imports a
  file of its own by a relative path, and an `optimize = False` leaf;
  `tools/bench.py` declaring an assembly that places the first three;
  `sub/deep/group.py` declaring an intermediate assembly over the rigid leaf
  and `tools/deep_bench.py` a root over it; `samebench.py` declaring the
  same-package control. Model the fixture on
  `openspec/changes/import-the-artifact-by-path/evidence/probe_cross_package.py`,
  which already builds it, and keep it small enough to build in a test
  (`path_samples=60`, `profile_samples=8` for the flexible leaf).
- [x] 1.2 Add `tests/test_scad_import_paths.py` with a helper that reads a
  generated `.scad`, extracts every `import(file = "…")`, and resolves each
  against the `.scad`'s own directory. Tests:
  - a cross-package parent's `.scad` resolves every import, for all three
    leaf kinds — RED today on the flexible leaf's bare basename;
  - the same after a second build of the same model, with every artifact
    current — RED for the same reason, and the assertion that the two builds
    agree;
  - an intermediate assembly's own `.scad` resolves its import — RED today,
    anchored on the root's build directory;
  - the root's `.scad` over that intermediate resolves its import — green
    today, and a guard against fixing one end by breaking the other;
  - a project's own `import_stl` path is reproduced verbatim — green today,
    and the guard on the re-anchoring pass;
  - the same-package control is byte-identical to today's bare basenames.
- [x] 1.3 Add to `tests/test_snapshot.py`: with a fake runner returning
  OpenSCAD's `WARNING: Can't open import file '…', import() at line N` on
  stdout and returncode 0, `solid snapshot --renderer openscad` exits
  non-zero, names the file and the `.scad`, and writes no image — RED today,
  it reports success. Beside it: a clean run still writes the image and
  succeeds, and an unrelated warning is logged without failing.
- [x] 1.4 Record the red run (the failing assertions and their messages) in
  `evidence.md` under "Red".

## 2. Make it pass

- [x] 2.1 `solid_node/node/base.py`: add `_ArtifactImport(import_stl)`, the
  `artifact_import(path)` helper anchoring a path on `get_build_dir(self.src)`,
  and `_model_for_own_scad()` re-anchoring a deep copy onto `self.build_dir`
  (a no-op when the prefix is `.`). Use `artifact_import` at `base.py:821`
  and in `import_optimized()`, dropping its `relpath(self.basedir, self.root)`;
  render `_model_for_own_scad()` from `scad_code`. The re-anchored spelling is
  `os.path.relpath(os.path.join(<build dir>, <anchored path>), self.build_dir)`
  — normalised, so a root at the top of the source tree and a parent beside
  its parts reproduce today's text byte for byte (reviewer's note).
- [x] 2.2 Route the remaining emitters through `artifact_import`:
  `exact_leaf.py:99`, `flexible.py:324` (the per-binding snapshot),
  `adapters/jscad.py:94`, `adapters/stl.py:201`.
- [x] 2.3 `adapters/openscad.py`: its `scad_code` override renders the same
  re-anchored model, so an `OpenScadNode` is not a hole in the rule.
- [x] 2.4 Confirm `self.root` is no longer read for any path; leave the
  attribute and its propagation alone if anything else uses it, and say in
  the commit which.
- [x] 2.5 `solid_node/viewers/openscad.py`: log every warning, error or
  deprecation line of both captured streams at WARNING (progress output
  stays at DEBUG), and raise a named error when a line reports a
  file OpenSCAD could not open, carrying that file and `node.scad_file`.
  Record the matched text and the version measured (OpenSCAD 2021.01) beside
  the code.
- [x] 2.6 `solid_node/manager/snapshot.py`: catch that error, write the
  message to stderr, exit 1, and leave no image behind.
- [x] 2.7 Run the section 1 tests green; then
  `tests/test_scad_stl.py`, `tests/test_snapshot.py`, `tests/test_stl_node.py`,
  `tests/test_sheet_leaf.py`, `tests/test_build123d_adapter.py`,
  `tests/test_backend_neutral_materialization.py`, `tests/test_flexible*.py`,
  `tests/test_files.py`, `tests/test_running_document.py` — the SCAD- and
  artifact-path-sensitive files — and record the results.
- [x] 2.8 Re-run `evidence/probe_cross_package.py` against the fixed tree and
  append its output to `evidence.md` under "Green", showing every import
  resolving in every generated `.scad`.
- [x] 2.9 Measure `_model_for_own_scad` on the largest assembly fixture the
  suite builds (wall time per `.scad` write, and the copied tree's object
  count) and record it in `evidence.md`. The copy is taken for every node
  whose build directory is not the anchor — every node of a project whose
  models live under `simulation/`, i.e. every real project — so the cost is
  paid, not avoided (reviewer's note).

## 3. Record it

- [x] 3.1 `docs/adrs/BUILD/ADR-116-an-artifact-import-is-anchored-on-the-build-directory.md`
  — the decision as design.md states it, its relation to ADR-073 and
  ADR-086, and the rejected alternatives. Add it to `docs/adrs/README.md`
  in the BUILD section, preserving the table's order.
- [x] 3.2 Update `docs/architecture.md` where it describes the build
  artifact layout, so the anchoring rule is part of the described system.
- [x] 3.3 Documentation: wherever the docs explain a project's package
  layout or the generated SCAD, state that an assembly may live in any
  package relative to the parts it places.
- [x] 3.4 `workflow/warts.md`: mark the Thor bullet "A leaf's artifact is
  imported into its parent's `.scad` by bare filename…" FIXED, naming this
  change and ADR-116, and note that the intermediate-assembly half was
  found and fixed with it.
- [x] 3.5 Full suite: `python -m pytest tests -q`, recorded in `evidence.md`
  with the count and any pre-existing failures identified as pre-existing.

## 4. Close the cycle (reviewer)

- [x] 4.1 `openspec validate import-the-artifact-by-path --strict`, sync the
  baseline specs, archive the change, and commit the implementation record.
