## Context

The Curta Type I project at `48d71c91bfb0b37c831cb8cd0ecc098dbc86d844` compares a turned reverser tooth with two exact drum prints. That committed baseline's `simulation/tools/reverser_tooth_envelope.py` (SHA-256 `10a913c45758bb24e88a7ab6e2fe9c433f4657cdf9876f5b71db77d52a11c19c`) posed native drums afresh. An uncommitted, subsequently withdrawn trial cached one native drum during station-1, crank-173°, height-minus-3 mm midpoint refinement. Its transient source file was not hashed before replacement; the reproducible test supplies equivalent reader-local reuse from the committed fresh-native reader in the test process, with no project source edit. After 39 successful native queries, the 40th at shaft `207.5123519897461` returned an invalid two-solid common whose reported volume was 1241.46 mm³. A fresh pose of the same valid inputs returned a valid common of `2.8890132738894073e-12` mm³. The cached drum's 325-vertex tolerance tuple changed during destructive OCCT comparisons; the original source and freshly posed drum did not. An initial protected-mode implementation completed all 200 original calls without mutating inputs, but returned an invalid two-solid common at a different **fresh-input** pose (crank 169°, shaft `150.7459411621095`°, height -3 mm, lift zero); default mode returned a valid two-solid common of `4.241072983936974e-09` mm³ whether parallelism was on or off. Deep-copying both operands then calling default Common gave that valid 169° result and completed the original 200-call sequence with no caller-input mutation and bit-identical boundary records to the fresh-native default control. The project's fresh-native control at `0cb681a01202184ee3f146027a9881bc657ecf50` completed all ten boundaries at both surveyed heights but loses reusable native placement work; the four cached partial rows are not safe resume evidence.

The framework's exact layer already caches native shapes and 512 placed shapes, then sends them repeatedly to Common and Fuse. Its false-empty guard also runs a Section over the caller's shapes. OCCT's default mode permits needed tolerance updates to propagate to input subshapes. `CadQuery Shape.copy(mesh=False)` uses `BRepBuilderAPI_Copy(shape.wrapped, copyGeom=True, copyMesh=False)` and returns a private exact B-rep operand. The existing default OCCT Boolean can amend that copy without changing the caller's retained input.

## Goals / Non-Goals

**Goals:** Preserve caller-owned native input subshape tolerances and topology through framework Common, Fuse and false-empty Section operations; prevent order-dependent invalid results from repeated native comparisons; retain exact output and fail-closed verification rules.

**Non-Goals:** Repair an already-invalid input, classify a numerically invalid result as valid, change contact thresholds, use meshes, add fuzzy Boolean tolerances, change part geometry, expose a mode knob, or claim every OCCT defect is solved.

## Decisions

- Deep-copy both operands at each framework-owned Common/Fuse operation in the shared `_boolean` path, and both operands at the Section in `_false_empty_witness`, before passing those private copies to OCCT. Preserve original argument order, parallel-mode choice, default kernel mode, exact result, named-pair error wording and guard policy. A copy failure refuses within the same pair-named error path; it never falls back to shared inputs or a mesh. The copies are call-local, not retained in the framework's shape caches. Copying potentially large solids costs memory and CPU, but avoids the measured protected-mode invalid result and retains bit-identical origin boundary records. Removing the project cache alone avoids one witnessed pattern but leaves framework-owned retained placements vulnerable.
- Reject `SetNonDestructive(True)` for this cycle. It isolates inputs but changes OCCT output validity at the measured 169° pose. Do not conditionally retry it, accept an invalid result, or add a mesh/fuzzy/tolerance fallback. Copied default operands are the single selected kernel path.
- Do not alter existing `IsDone`, `Solids`, volume, witness, or assertion verdict logic. The originating project already checks and rejects its invalid common. This change makes the operation preserve inputs; it is not an error waiver or a replacement-volume algorithm.
- Prove the public behavior with focused real OCCT tests of reused inputs (including a spy that fails red when any of the three operations receives the caller-owned shapes rather than private copies), ordinary disjoint/tangent/positive and copy-failure controls, and a process-local repetition of the original Curta drum sequence over the committed fresh-native reader. Compare all endpoint records with the fresh-native default control; pin project and framework source. Record both the formerly invalid 173° reused-input pose and the protected-mode-only invalid 169° fresh-input pose. Run the framework suite and project caller tests before integrating.

## Risks / Trade-offs

- **Copies cost memory and CPU per Boolean** → measure the repeated Curta query sequence and report cost honestly; copies are call-local and do not enlarge the framework's retained shape cache.
- **A private copy may change a near-degenerate result** → preserve default OCCT mode and test both the 169° valid fresh-input common and the 173° ten-boundary bit-identical endpoint records; retain exact positive and invalid-result checks without an epsilon.
- **Section might mutate a shape during failed-empty verification** → pass private copies and test that its construction preserves both original inputs; do not skip the existing independent witness search.

## Migration Plan

No project or document migration. A previous process that has already mutated a cached native shape must be restarted; copying protects newly run operations, not historical in-memory mutation. Reverting the private copying restores prior behavior. No viewer change is required because its faceted browser kernel does not call these native OCCT operations.

## Open Questions

None before revised implementation. The initial protected-mode idea is rejected by the measured 169° fresh-input invalid result; real Curta and framework regressions decide whether private copies are sufficient.
