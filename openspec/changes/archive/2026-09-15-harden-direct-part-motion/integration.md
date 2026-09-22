# Integration reconciliation — 2026-09-22

The completed correction on `harden-direct-part-motion` (`8a59ff0`,
`d1108a4`) was merged with preserved ancestry into framework main after
main had moved to `5d5ba18`. The merge kept the later running-motion
behavior and baseline requirements, and applied this correction under the
renamed `machinome` package. The historical planning and evidence files
retain their original `solid-node` paths because they record the work as
performed on 15 September.

The merge resolved the renamed `simulation/program.py` by carrying its
effective-joint and complete-placement checks into the current implementation.
The baseline simulation and export specs include both the current running
behavior and the archived control requirements. No viewer source changed.

Validation in `machinome/WTs/reconcile-direct-part-motion`:

- Focused controls, running-document, joints, couplings and adversarial
  review tests: 563 passed, 569 subtests passed.
- `openspec validate --all --strict --no-interactive`: 34 specs passed.
- Full framework suite before correcting two stale test expectations:
  3534 passed, 4 skipped, 2 failed, 2106 subtests passed. Both failures
  were `RunningSnapshotWarningTest` assertions expecting running document
  version 5; main's Curta source-timing correction already publishes version
  11. The expectations and mocked warning now use version 11.
- After that expectation correction, the build-publication file and all
  focused correction suites passed: 571 tests, 569 subtests.

The old `direct-part-motion` branch still contains only the superseded
adversarial planning draft (`67003f6`). The independent
`curta-running-performance-wart` commit (`f21c46e`) is patch-equivalent to
the `f310a3c` record already on main. Neither needs a second merge.
