## Why

The Curta `LoopOperatingTrial` replaces its inherited `carriage` with a specialized subclass and copies `OperatingCurta.controls` while adding one loop control. Class construction rejects the copied `shift carriage` control because its declaration still points at the ancestor's carriage object, even though the effective child is at the same path. The project cannot retain its existing hand controls and add the new one through the current declaration contract without restating every control.

## What Changes

- Admit an inherited control copied into a subclass table when its part and explicit coordinate still resolve through a compatible, same-path replaced child. Bind their effective declarations from the subclass tree, preserving all existing ownership, ancestry, coordinate, domain, driver and input-reachability checks.
- Keep an explicit subclass `controls` table a complete replacement, not an automatic merge. Reject a foreign same-name control reference and an incompatible replacement; do not relax ordinary newly authored controls.
- Prove the Curta trial's class definition and public control enumeration, compilation, and document against the existing viewer contract. No new author API or document field is proposed.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `simulation`: Inherited controls remain valid when their declaring assembly's child is compatibly replaced at the same path in a subclass that explicitly preserves those controls.

## Impact

`machinome/simulation/control.py`, narrowly relevant class validation and compilation, baseline simulation spec, focused tests, and the originating Curta `LoopOperatingTrial` caller. The serialized controls table and viewer API remain unchanged.
