## 1. Red

- [ ] 1.1 `tests/test_brep_common_guard.py`: a reversed unit box touching a
      normal one with `_boolean` patched empty is refused with
      `BrepCommonVerificationError` naming the reversed operand and its
      volume, not `BrepCommonInconsistency`; `mutually_outside` on a
      reversed box far from a normal one answers `False` both ways while
      a recorder for `BRepClass3d_SolidClassifier` sees no construction.
      Run; both red.

## 2. Green

- [ ] 2.1 `_inside_out(shape)` in `machinome/engine/brep.py`; the test in
      `intersect_shapes` before the witness and in `mutually_outside`
      before the classifiers. Run the guard, witness and geometry tests.
- [ ] 2.2 Read-only evidence on Thor's published `step/Art4BodyBot.step`
      through the framework's STEP reader: negative signed volume, and
      `intersect_shapes` against a box touching it refuses by name.

## 3. Records

- [ ] 3.1 ADR-142 amendment; `docs/project/changelog.rst` bullet under
      Unreleased.
- [ ] 3.2 Sync the `brep-engine` delta, archive, rerun the engine test
      modules, commit 2.
