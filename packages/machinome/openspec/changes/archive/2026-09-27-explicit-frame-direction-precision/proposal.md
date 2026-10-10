## Why

Curta Type I's exact source-derived zero-positioning-pin triad loses tiny
direction components during Frame normalization, making the independent
legacy/mated moving-pose comparison differ by `1.4452851360147179e-8` mm at
places 8. Geometric tests pass 6/6; no physical fit failure is claimed.

## What Changes

- Retain full normalized direction precision when BOTH `x` and `z` are
  explicitly supplied to `Frame`, including expressions and callables.
- Preserve snapped behavior when `x` is omitted or `z` defaults; explicitly
  writing the default z vector remains distinguishable from omitting it.
- Keep projection, orthogonality and refusal rules, and final mate
  rotation/axis snap `1e-9`, unchanged.
- Make `resolved_frames` expose the same precise basis the mate composes.
  Update framework public docstrings/manual and root-owned Studio companion
  API documentation, with no new arguments, strings or viewer/schema changes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `mates`: narrow frame resolution/readout snapping to declarations not
  explicitly supplying both direction vectors; pin actual mate composition.
- `user-documentation`: document the explicit-direction precision distinction
  in public docstrings/manual and record it only under Unreleased.

## Impact

`machinome/node/frames.py`, frame/mate tests, public Frame/ResolvedFrame
documentation and `docs/concepts/joints.rst`. Studio's API skill update is
separately owned by root in the Studio repository, never this framework tree.
Caller evidence remains project-owned: `_build/zero-mates-candidate.patch`,
`simulation/test_zero_mates.py` and
`simulation/docs/zero-mates-in-progress-2026-09-27.md` in Curta-Type-I-3x.

The pilot explicitly ratified this public numeric contract before proposal;
broader interface changes still require approval first. Standalone clean base
main `82a9774dfeaaf60b04f1e46b452198bab8611c4f`, branch/worktree
`explicit-frame-direction-precision` at
`machinome/WTs/explicit-frame-direction-precision`, integration target `main`.
This is planning only: root reviews/commits planning, another Sol applies;
review precedes sync/archive. ADR disposition follows verified implementation.
