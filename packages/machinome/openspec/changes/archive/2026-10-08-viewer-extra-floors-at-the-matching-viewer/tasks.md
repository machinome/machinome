## 1. Prove the floor is missing

- [x] 1.1 Add `test_the_viewer_extras_floor_at_the_matching_viewer` to
      `tests/test_release_records.py`: for `viewer` and `web-snapshot`,
      parse the `machinome-viewer` requirement and assert its specifier is
      exactly `>=` `conf_value('viewer_version')`. Run it red against the
      unversioned extras.

## 2. Floor the extras

- [x] 2.1 `pyproject.toml`: `viewer = ["machinome-viewer>=0.8.0"]` and
      `web-snapshot = ["machinome-viewer[snapshot]>=0.8.0"]`, with the
      comment above them saying the floor is the matching viewer and the
      test that holds it. Run the new test green, then
      `tests/test_release_records.py` and `tests/test_kernel_extras.py`.

## 3. Records

- [x] 3.1 `docs/project/upgrading.rst`, "Install a matching viewer": one
      sentence that the `viewer` and `web-snapshot` extras require the
      matching viewer or newer, so upgrading through the extra upgrades the
      pair; keep "a 0.7 viewer reads a 0.8 export".
- [x] 3.2 `docs/project/changelog.rst`: one bullet under Unreleased naming
      the change.
- [x] 3.3 Build the manual strictly (`python -m sphinx -n -W --keep-going
      -b html docs <out>`) and run `tests/test_docs_structure.py`.

## 4. Complete

- [x] 4.1 Sync the `framework-identity` delta into the baseline spec,
      archive the change, run `tests/test_release_records.py`,
      `tests/test_kernel_extras.py`, `tests/test_docs_structure.py` and the
      strict manual build once more, and make commit 2.
