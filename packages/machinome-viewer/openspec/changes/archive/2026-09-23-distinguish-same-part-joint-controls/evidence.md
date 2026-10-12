# Evidence: distinct selected-joint controls on one visible part

This is a viewer capability correction for the Curta operating-loop trial,
not a change to the machine's mechanical validity or to the v13 document
format. Project source was not edited in this viewer cycle.

## Red and compatibility boundary

- Viewer base `2274dd2afa4b6d75793d304da922b5944a8fcbe5`, API 26, refused
  the actual 26-control v13 export at load. The immutable hosted failure
  report `operating-loop-trial-pointers-01.json` has SHA-256
  `e2228ef9848f7dd3dc9813b920154961911813c500c27a58f48ec68eef5f2355`;
  its bundle SHA is `0e73249a4047844a6d3b95df8e3b0898014fb3dc8097fab0db5e63ad8c86c77d`.
  The error names `deploy loop (simulation-only mounting)` and `clear registers`
  on the shared visible part. There was no pointer attempt because mount failed.
- The two actual declarations select different joints: `clear registers`
  selects ancestor `carriage.registers.clearing_ring.turn` via
  `clearing_rotation`; `deploy loop (simulation-only mounting)` selects leaf
  `carriage.registers.clearing_ring.clearing_ring.swivel` via
  `loop_deployment`. The latter is an independent mounting freedom in this
  trial, not a second name for the first joint.
- The synthetic same-part/different-joint loader test failed under the old
  `(kind,part)` claim. The existing named-handle geometry test passed before
  the loader correction, distinguishing the parser limit from handle
  geometry. After loading was enabled, the first real Chromium pointer run
  failed with zero outcomes because pending hover recast replaced the clearing
  handles with the crank handles behind them. The failed report remains at
  `operating-loop-api27-two-turn-pointers-01.json`. A focused hover-crossing
  unit test was red before the owned-handle hover guard.

## Green source and browser gates

- API 27 retains document versions 1–13 and the unchanged v13 control wire.
  The claim is `(kind,part,joint)` only for Turns; same-joint duplicate Turns
  still refuse even with different names/inputs, and Button/Slide duplicates
  are unchanged. Focused fixtures also preserve a one-control declaration,
  Button+Turn, and Turn+Slide on one part.
- Candidate bundle SHA-256 is
  `4e4580332e33c75042c2e188f80fbd3b8712280dabc1e56a895310651160339c`.
  Fresh ordinary export-02 `manifest.json` SHA-256 is
  `46f7d5245d260423046d295a7866b08b6f95f410941c3892b5ba855356fcc029`;
  it carries 216 coordinates and 26 controls.
- Actual hosted pointer report `operating-loop-api27-two-turn-pointers-02.json`
  SHA-256 `eeebe9139cb60acbbe3ef9e8e63c466e923c201b4c0dedcaa88bbbd4239ac1c5`
  passed. The `clear registers` handle submitted only
  `clearing_rotation` (+1); the `deploy loop` handle submitted only
  `loop_deployment` (+4). Both used real pointerdown/move/up on the visible
  named handles, retired their commands and had no page errors/refusals.
  The corresponding screenshot SHA-256 is
  `d322c2b3723261340349fa589ff36af2f85913143dae818e84d27613de5b6b42`
  and was inspected.
- Separate public hosted declaration/body report in this viewer worktree,
  `_build/verify_26_body_03.json`, SHA-256
  `cdca9381d9d30746f4d5534ee9f3043834a868461f11cbe48fbcf890805ff063`,
  found all 26 controls and both gesture points. A real drag on the shared
  visible body, not on either handle, produced no outcome, no pending command
  and an unchanged full bank. No page error. The first two attempts at this
  diagnostic used a relative asset root and returned a harness-only 404;
  they remain under `_build/verify_26_body{,_02}.json` and were not counted
  as product failures.
- The unmodified standalone export-02 page was separately exercised by the
  parent project gate. Its visible `deploy loop` handle completed +4. Its
  `clear registers` handle admitted 1.4372 degrees in total and then blocked
  at the seated mechanical stop; it did not complete. Only the selected
  input changed, no page errors occurred, and the captured pixels were
  inspected. This is standalone gesture evidence, not a hidden host remount.
- The later default production export-01 was mounted through the public
  hosted API for end-pose pixels, not as a pointer test. Its manifest SHA-256
  is `68f16a67d7823d259e7e170cb92d349caaa37e6e69a597fa664f9dd9f0840ec9`.
  `_build/capture_loop_ends_02.json` SHA-256
  `90fb75ea21bcdf8e6ff7b0d0638fa0fcdc6e8032942f880f677565ef5d1b6d38`
  records API 27, 26 controls, stowed `loop_deployment=0`, and a completed
  awaited public `run.move(to:90)` with terminal bank 90, no pending command
  or page error. The stowed/deployed PNG SHA-256 values are
  `dd818b5f2d56a1c3aebb3fd324fe3fdc7169188f4e130eb7a677e740c35c73b6`
  and `19fb7f1e6778c1db9e5f0b78ad28989e2c88bdb24fb41dd62373e17821022787`.
  Both were visually inspected: the loop is tucked above the clearing ring
  at 0 and swings outward at 90, with the rest of the Curta visible. The
  first diagnostic attempt did not await public `move()` and misread its
  Promise as a synchronous status; its report is retained but is not a
  product failure.

## Package and documentation gates

- Full widget suite after the final Turn+Slide compatibility fixture:
  1,583 passed, 2 skipped, 60 files. Its focused file passed 52/52.
  TypeScript typecheck passed. The bundle built and was frozen at the hash
  above; the final test and manual edits do not change runtime bundle bytes.
  `python -m machinome_viewer describe` from this worktree reports that
  exact bundle path, API 27, document versions 1–13 and package version
  0.7.0.
- Strict Sphinx build passed 14 pages. Documentation/browser check passed
  14 pages, 2 viewports and 204 links, including mobile, search, interactive
  and reference examples, without browser errors. The rendered compatibility
  page was inspected; its historical 0.7.0/API-26 substitutions and current
  API-27 sentence render as values rather than literal placeholders. The manual distinguishes
  current-source API 27 from the recorded 0.7.0/API-26 release; no push,
  publication or package-version change is claimed.
- During spec sync, the older user-documentation baseline requirement was
  found to call the recorded 0.7.0 release API 25/document 1–12, contrary
  to the unchanged 0.7.0 changelog/manual API 26/document 1–13 facts. The
  change's explicit MODIFIED delta reconciles only that release-fact wording
  and scenario while retaining the pointwise profile-contact contract.
- The first broad Python gate after declaring API 27 had 15 failures, all
  stale test expectations of API 26, versus 185 passed and 8 subtests. Those
  version pins were updated to 27, preserving the historical release-page
  assertions. The final broad rerun passed 198 tests and 22 subtests in
  462.34 s; 50 warnings were dependency/Pillow deprecations, not failures.
