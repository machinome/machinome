## Why

Enigma I's isolated rotor worktree (`/mnt/data/machinome-projects/enigma-i-worktrees/rotor`, evidence commit `c7f125b`) reproduces a browser violation of the existing clocked atomic-request contract: a final rendered rotation becomes undefined, yet public `MachineHandle.move` commits its bank and the actual source pawl disappears. Native public `Sim` refuses the same three requests and retains bank, joint and event record; normal Studio operating controls cannot safely rely on the browser's current admission behavior.

## What Changes

- Refuse a clocked final pose whose evaluated placement cannot produce finite local and composed rendered transforms, with a diagnostic naming the assembly path and offending operation or composition.
- Prepare the affected transforms before changing the live tree, retaining the bank, event outcome and every previously visible placement when preparation fails, including a failure after an earlier sibling was prepared.
- Exercise the real standard document, bundled widget and public machine handle using an authored minimal fixture, with native refusal as the reference and finite visible geometry as evidence.
- Preserve valid clocked requests, bindings, selective updates, exact event landings and document/API versions. Driver and State ranges remain presentation metadata.
- Pin recovery after candidate-expression caches were populated: an original-bank update and a move of an independent driver must read standing values, without a cache rollback mechanism unless the implementation evidence requires one.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: make final rendered-transform admission and whole-tree refusal explicit for the existing clocked atomic-request promise.

## Impact

The implementation target is the monorepo's `packages/machinome-viewer/machinome/viewer/web/widget/src/tree.ts` and its clocked pose hook in `viewer.ts`, with viewer-owned tests/fixtures. Core source at `packages/machinome/` is the native reference, not an implementation target. The product retains its own OpenSpec record here under accepted ADR-188; ADR-194 and ADR-196 describe its current import/command ownership (`machinome.viewer.web`, `machinome viewer`). The workspace contract and `scripts/dev-env` still describe the former separate viewer repository/process; this discrepancy is recorded, not repaired or silently adopted as a policy change by this proposal.

No solver, new declaration, range guard, physical stop, lamp/control feature, document field or public interface is proposed. Fixing browser refusal does not admit the partial Enigma flank law as a complete operating mechanism. No Enigma STL is copied into framework fixtures.

The pilot ratified the completed proposal and its cache-recovery review on 2026-11-07 with the explicit instruction **"Authorize implementation and local integration"**. This includes the monorepo viewer target, planning commit, implementation, completion and local fast-forward integration under the framework workflow; it authorizes neither push nor publication. Base: clean framework `main` at `c8e5e124f84a015f8da322c4ced0fd3ce52ef4f3`; managed branch/worktree `refuse-nonfinite-clocked-pose` at `machinome/WTs/refuse-nonfinite-clocked-pose`; integration target `main`. Coordinate with the parent repository agent before integration or any shared installed-runtime change, because its mechanical regression/build/snapshot work uses that runtime.
