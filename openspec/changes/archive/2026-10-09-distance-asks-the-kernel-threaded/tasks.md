## 1. Red

- [x] 1.1 `tests/test_brep_geometry.py`: a test with a recorder for
      `machinome.engine.brep.BRepExtrema_DistShapeShape` asserting that
      `SetMultiThread(True)` is called before `Perform()`, and a test that
      `_distance` on two placed solids equals CadQuery's `Shape.distance`.
      Run; the first is red.

## 2. Green

- [x] 2.1 `_distance`: empty constructor, `LoadS1`/`LoadS2`,
      `SetFlag(Extrema_ExtFlag_MIN)`, `SetMultiThread(True)`, `Perform()`,
      `Value()`. Run the two tests, then `tests/test_brep_geometry.py`,
      `tests/test_brep_common_guard.py`, `tests/test_witness_neighbourhood.py`
      and `tests/test_resolved_brep_witness.py`.

## 3. Records

- [x] 3.1 `docs/project/changelog.rst`: one bullet under Unreleased.
- [x] 3.2 Sync the `brep-engine` delta, archive, rerun the four test
      modules, commit 2.
