# Adversarial review — 2026-09-15

## Authority and identity

The pilot requested review, corrections and then Curta work. After merging
the prerequisite, the pilot directed corrections to branch from main.
Base: clean main `1aac0ffa8c430b68e97dc1acec04a2d0cd21b140`.
Branch/worktree: `harden-direct-part-motion`, slot 17 under `solid-node/WTs/`.
Planning-only commit: `8a59ff0`, exactly one commit above base.
Integration target: main, not integrated or authorized to push.
The old `direct-part-motion` worktree and its early review edits/commit
`67003f6` remain untouched; it is not the continuing bench.

## Findings

1. Valid subclass/site joint replacements broke inherited explicit controls:
   the compiler compared stale declaration identity against effective joints.
   Validated own/path references now resolve the realized body's named joint,
   preserving foreign-reference, ancestry, reachability and Free refusals.
2. Fixing selection exposed stale bank metadata: inherited relation ends
   created slots through the original joint while binding already addressed
   the replacement by name. A Revolute replacing a Prismatic thus published
   mm/translational and incorrectly admitted Slide. Resolved joint relation
   ends now use the effective declaration before creating the slot. A separate
   no-control test proves actual slot and program metadata, not a UI workaround.
3. Contiguity accepted incomplete, reordered and duplicated pivot blocks.
   Private operation index/length marks beside the existing joint slot now
   prove the complete ordered placement. Nothing new is serialized; no stale
   side list, expression parsing or regenerated placement is used.
4. The producer did not implement browser sliding; its archived evidence
   honestly left paired acceptance open. Viewer `slide-and-turn-parts` and
   Curta are separate consumer/project work, not claimed complete here.

These repair existing effective-joint and ADR-117 contracts. No new public
interface, run semantics or architectural decision: no successor ADR needed.

## Reproduction and proof

Commands used workspace Python with `PYTHONPATH="$PWD"` inside the new bench.

- Before production edits, review regression: **12 failed, 3 passed**,
  including three missing-pivot-operation subtests. Overrides failed by
  identity; the no-control bank had `('mm', 'translational')` instead of
  `('deg', 'rotational')`; damaged spans were not refused.
- Review, controls, running-document, joints and couplings suites:
  **542 passed, 561 subtests, 3 expected deprecation warnings**.
- Full `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 pytest -q --tb=short`:
  **2766 passed, 4 skipped, 1524 subtests, 53 warnings**, 328.58 seconds.
  Warnings concern existing deprecated fixtures/library APIs and process forks.
- Regenerated running corpus compared with `cmp`: byte-identical,
  **185444 bytes, 14 scenarios, 12 machines, 276 ticks**.
- Control fixture generator exported columns/selector/crank/tilted/register
  into the viewer's `tests/fixtures/direct-motion/`, respectively 4/2/3/2/2
  controls and 0/2/3/2/2 selected spans. They are actual producer exports.
  The consumer records the eventual exact tested content pair.
- Existing no-control and inferred-rotation byte-identity tests pass unchanged.

An overlapping diagnostic invocation in the old bench raced its shared
`tests/_build` and produced FileNotFoundError. That was an invalid parallel
test run, not a product finding. Reported new-bench regressions were sequential;
fixture generation waited for the full suite to finish.

## Limits

Declaration and placement proof is not force/contact simulation, Curta
arithmetic or pointer reachability. Browser pixels and originating-project
mechanical sequences remain separate acceptance work. No merge or push.
