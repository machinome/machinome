## 1. Red

- [ ] 1.1 Run `test_distribution_import_command_and_extras_share_the_name`
      on the unmodified bench and record it red for the stated reason:
      `['machinome-viewer>=0.8.0'] != ['machinome-viewer']`.

## 2. Green

- [ ] 2.1 `tests/test_machinome_identity.py`: for `viewer`, `mechanics` and
      `studio`, unpack the extra's one requirement, parse it with
      `packaging.requirements.Requirement` and assert its `.name`. Run the
      test green, then `tests/test_machinome_identity.py`,
      `tests/test_release_records.py` and `tests/test_kernel_extras.py`.

## 3. Records

- [ ] 3.1 Write `evidence.md` in the change directory with the commands and
      outputs, sync the `framework-identity` delta, archive the change, run
      `openspec validate --all` and the three test modules once more.
