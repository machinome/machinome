## Context

`LoopOperatingTrial(OperatingCurta)` replaces `carriage` with `LoopRunningCarriage`, a subclass of the former carriage class, and explicitly copies the 25 inherited controls before adding one loop Turn. The inherited `shift carriage` control still holds a `PathRef.root` pointing to the ancestor's `carriage` declaration. `NodeMeta` compares that object with `declared_children(LoopOperatingTrial)['carriage']` and refuses the class. A subclass-only `controls` mapping is not a solution: explicit tables replace inherited tables, as current tests promise.

The baseline already resolves an explicitly selected joint to the effective named joint on the realized node, including supported joint overrides. Part paths also walk the realized instance by name. The missing piece is authorization of an ancestor-owned control reference across a compatible child replacement, without admitting a foreign reference merely because its first segment has the same spelling.

## Goals / Non-Goals

**Goals:** Admit explicitly preserved inherited controls on a subclass's compatible same-path replacement; keep existing effective-path validation and published control semantics; make the Curta trial's class, simulation and control document work without reauthoring its controls.

**Non-Goals:** Automatic merging of `controls` mappings, name-only acceptance of foreign references, new control syntax, new document fields, or weakening of run-owned coordinate, domain, ancestry or input-reachability checks. No viewer runtime change unless a paired document reveals an actual consumer defect.

## Decisions

1. Keep an explicit `controls` mapping as the complete effective table. A subclass that writes only its new control intentionally has only that control; `{}` still clears all. The Curta's explicit copy-plus-add table remains the author declaration.
2. At class validation, the ordinary exact-declaration check remains first. For a mismatch, admit only an unchanged control object found under that same entry name in an ancestor's validated control table, whose original first child was declared on that ancestor, and whose effective first child at that name is a subclass-compatible replacement. Reject a merely same-named reference from an unrelated class, a different control object, an incompatible child, or a missing first child. This is provenance-based permission, not generic string rebinding.
3. Apply the same provenance rule to the control's explicit coordinate path. The driver remains subject to its existing owner-identity check. During compilation, resolve the part and coordinate through the realized effective tree; keep the existing selected-joint remapping, ancestry, bank ownership, coordinate-domain, and driver-reachability checks. A missing or incompatible nested path refuses with the named control rather than publishing a stale target.
4. Preserve the existing serialized controls schema and program identity behavior. Verify the actual Curta document with the current viewer rather than changing the viewer spec by symmetry.

## Risks / Trade-offs

- An ancestor table can be copied under a new class, but provenance must not become name-only authorization. Red tests use unrelated classes with identical child names and explicit coordinates.
- A compatible replacement might remove or change a nested path or joint. Class validation and compilation must fail closed at their respective existing boundaries, with a named control; no stale ancestor declaration can be published.
- The Curta owns many controls; inspect every compiled entry and a representative gesture, and compare old unchanged entries where meaningful. Do not claim byte-identical whole documents after the model itself adds a driver/control.

## Migration Plan

No declaration migration. Existing tables and documents remain valid. The new Curta subclass can compile its already-written copy-plus-add table. Revert the narrow validation change to restore old behavior if its negative controls fail.

## Open Questions

None requiring a new author choice; implementation tests will confirm whether an additional compilation-time nested-path check is needed beyond the current effective-tree walk.
