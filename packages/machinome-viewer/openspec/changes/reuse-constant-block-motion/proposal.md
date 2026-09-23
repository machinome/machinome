## Why

The current Curta Type I asymmetric-reverser export repeats an unchanged 31-law cyclic block on nearly every tick of an ordinary reversing-lever gesture. On the pinned viewer main and document, this block consumed about 7.4 CPU seconds across the 90° preparation and a 0.6-second, 144-tick gesture; a process-local *experimental* successful-result reuse reduced each 48-tick gesture from roughly 3.2–3.5 to 1.0–1.5 CPU seconds while preserving all 214 bank bits, admissions, status and final stop. The experiment is not safe product code, but it establishes a current-project need for bounded, exact reuse.

## What Changes

- Reuse at most one previously successful, certified constant-source result per compiled cyclic block within one running engine, only when every actual numeric dependency and held output matches bit-for-bit and the prior evaluation produced no crossing or landing side effect. Keep the ordinary eager execution for every uncertain or ineligible case.
- Reconstruct fresh constant output motion paths from complete scalar descriptors, preserving exact endpoints and any terminal-path metadata. Do not share mutable `Motion` instances between propagations.
- Clear the private reuse state on reset/restore and keep it out of documents, snapshots and global scope. Preserve first errors, selector/cut order, search points, banks, statuses, records and replay.
- Add red-first adversarial tests and exact Curta default-timestep paired measurements, then validate the combined state after the concurrent viewer terminal-target cycle lands.

## Capabilities

### New Capabilities

- `constant-block-motion-reuse`: bounded, exact reuse of a cyclic block's previously successful constant-source motion result within a running engine.

### Modified Capabilities

None.

## Impact

Private running evaluator and tests only, likely `widget/src/run/trajectory.ts` and `run.ts`; no new document field, framework change, public API, declared timestep or sampling change. The proposal starts from viewer `b976a172a7964b269183eaee289c8cf26668cd58` and must reconcile the concurrent terminal-target change to `Motion` before implementation/integration. The originating project is `projects/Calculators/Curta-Type-I-3x`, pinned asymmetric v13 export identity `200219dcb6356bb3d27324e22f8dce01fdc5779fdb0ba2b06a9c56c28be3c8e8`; its measurements, temporary diagnostic hashes and prototype limits are recorded in [evidence.md](evidence.md). This is an internal performance-equivalence change, not a new capability hosts must detect, so API 26 and document version 13 remain unchanged.
