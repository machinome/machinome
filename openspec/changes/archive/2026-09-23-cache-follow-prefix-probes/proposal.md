## Why

The Curta Type I production `OperatingCurta` gained a certified two-surface retained positioning ball. Its paired dynamic Bounds replay the same three-edge prefix at the same fractions, including the expensive Follow envelope partition, independently. On framework `f4c48f6`, five ordinary 0.1-second crank ticks take 37.18 CPU seconds without meshes, versus 4.55 with the static ball; a profile records 768 prefix replays in the five ticks. The unchanged mechanical program is correct, but this repeated work makes ordinary operation markedly slower.

## What Changes

- Reuse a successful Follow-containing subprogram's prefix propagation at the same exact search fraction within one running stretch, when another Bound requires that identical subprogram and starting state.
- Keep every Bound's own level evaluation, sample sequence, crossing/bisection, errors, cut-side evidence, landing, and stop attribution unchanged. Uncertain/nonmatching cases use the existing replay.
- Add red-first parity and reuse tests plus a measured production Curta before/after benchmark. No author API, document field, timestep, tolerance, or sample-count change.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `simulation`: Equivalent running constraints may share a proven successful Follow prefix propagation within a single stretch, without changing observable simulation behavior.

## Impact

Internal `machinome/simulation/run.py` constraint search and focused framework tests; no dependency or wire-format change. The originating caller is `/mnt/data/machinome-projects/Calculators/Curta-Type-I-3x` at project commit `a139fe0`, with the production radial-ball source hashes recorded in the design. This standalone cycle is in clean worktree `machinome/WTs/cache-follow-prefix-probes` on branch of the same name, from framework main `83aad09`, targeting framework `main`. The pilot previously authorized a clean-worktree exception preserving primary untracked `docs/examples/v8-engine/`; this cycle uses that exception without moving or editing those files. Authority is the pilot's standing autonomous framework-fix instruction, not a separate ratification of this specific cache design.
