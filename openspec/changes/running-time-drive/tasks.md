Ratified implementation checklist (2026-09-20). **Do not begin** before explicit pilot
ratification, successful OpenSpec validation, a planning-only commit, a clean
worktree and verified one-commit ancestry from the recorded base. Artifact
readiness is not permission to implement.

## 1. Reproduce and admit the declared source

- [ ] 1.1 Add a minimal Astrarium-derived time-to-joint regression and prove the proposed declaration fails on the recorded baseline; retain the existing direct-pose and commanded-rate controls. Record exact test commands and red evidence.
- [ ] 1.2 Test and implement running-root clock source resolution for affine and grouped laws, owner identity and source order. Keep elapsed/looping source refusals, all clock target refusals and exclusive run-owned joint binding.
- [ ] 1.3 Test and implement compilation of an explicit read-only time source, including known path values, rest at zero and moving-name tracking; reject free undeclared symbolic time with the repair diagnostic. Preserve existing unsupported-law boundaries.

## 2. Advance retained motion

- [ ] 2.1 Prove no-command stepping red, then admit each tick's elapsed interval and propagate the existing incremental laws; verify no fabricated driver, command, bank clock or extra tick on construction/inspection.
- [ ] 2.2 Prove nonzero-time enable, instantaneous inputs and Astrarium-equivalent stop/wind/resume sequences red, then verify jump subtraction and supported self-read gates preserve history and add no catch-up travel. Include the nonlinear global-time example.
- [ ] 2.3 Test snapshot/restore/reset, second-run ownership, post-commit actions and failure rollback with autonomous motion; verify time and bank never partially advance on refusal.

## 3. Keep mechanical stops local

- [ ] 3.1 Prove independent time-drive and shared downstream-train stop cases red, then integrate per-relation admission identities into source-sensitive stop grouping and the finite segmented-tick procedure.
- [ ] 3.2 Test grouped targets, mixed operator/time paths, constraint-relieving inputs, exhaustion, next-tick retry, no same-tick reopening and no backlog. Preserve blocked-command retirement and incompatible-writer refusals.
- [ ] 3.3 Add and test separate time-drive stop provenance with default-empty `Stop.time_drives`, unchanged actual `inputs`, bounded recording and unchanged serialization for command-only records.

## 4. Publish the executable contract

- [ ] 4.1 Prove time-drive publication red, then publish deterministic `program.time_drives`, source candidates and program identity, using document version 10 only when required. Preserve existing document bytes and version selection for all no-time-drive fixtures.
- [ ] 4.2 Generate producer-owned corpus scenarios for no-command motion, gates, winding/exhaustion, independent and connected stops, mixed commanded sources and replay/reset. Test real publication against the committed corpus and verify malformed/incomplete time-drive metadata is not emitted.
- [ ] 4.3 Verify live-run publication preserves bank, clock and ownership; exercise an older consumer's version refusal without changing viewer files. Record the fixture location and exact contract for the separately authorized viewer cycle; do not claim consumer parity.

## 5. Validate and complete the framework record

- [ ] 5.1 Run affected coupling, running simulation, jumps, reads, paths, selection, stops, Play, document and corpus suites plus clocked-time regressions. Compare no-time-drive execution counts/performance and run the broader framework suite in proportion to the changed paths; report environmental failures separately.
- [ ] 5.2 Re-run the originating project's acceptance sequence through the framework-owned two-cube fixture using the accepted spelling, with no startup rate. Record the parked project's original six-test status separately; do not edit the project or label its historical reconstruction complete.
- [ ] 5.3 Update public authoring documentation with affine and gated examples, retained-versus-absolute motion, stop/retry behavior and the lack of a force solver. Record measured evidence and the outstanding independent viewer/project follow-up in the finding.
- [ ] 5.4 Once implementation confirms the design, extract the consequential ADR, update its index and architecture synthesis, synchronize the delta specs, archive through OpenSpec and validate. Create the completed implementation commit only under the two-commit framework cycle; integration remains separately authorized.
