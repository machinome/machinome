## Context

The checkout directory and the GitHub remote had already moved to
`libresolid-studio` when this work began, while repository content still used
the former product name in 48 tracked files: public metadata, machine
identifiers, runtime session labels, the project runtime-configuration key,
operating instructions, current specifications, and design material.

Two neighbouring names had to survive untouched. `solid-node` is the framework,
a separate repository this rename does not touch, and `SolidNodeWidget` is the
framework's browser global. “Shop” likewise remains the domain word for the
floor, roles, worktrees, and lanes. A blind textual replacement would have
damaged all three.

## Goals / Non-Goals

**Goals:**

- Establish “LibreSolid Studio” as the only active customer-facing product name.
- Establish `libresolid-studio` as the canonical distribution, plugin, service,
  and repository identifier.
- Move the project runtime-configuration table to `[tool.libresolid-studio]`.
- Keep the baseline specifications accurate to the shipped product.

**Non-Goals:**

- Rename the `solid-node` framework or its `SolidNodeWidget` browser global.
- Rename domain concepts such as shop floor, shop worktree, shop root, roles,
  the `shop-skills/` directory, or the `shop-floor-frontend` package.
- Rewrite archived changes, archived sprint records, or captured spike evidence.
- Introduce compatibility aliases for the former package, plugin, or
  configuration identifier.

## Decisions

### Preserve the display/machine identity split

The split ratified by `2026-08-08-rename-solid-node-studio` is retained
unchanged in form: human-visible labels use the exact spelling “LibreSolid
Studio”, and values constrained to identifier syntax use `libresolid-studio` or
that value as a prefix. Only the two names change.

### Rename the project configuration key without a fallback

`[tool.solid-node-studio]` becomes `[tool.libresolid-studio]` with no
deprecated-key fallback, so exactly one spelling is ever read or written.

Alternative: read both keys and write only the new one. Rejected by the pilot,
who chose migration of existing projects over a compatibility period. The
trade-off is accepted deliberately: a project that is not migrated fails to
load its runtime selections rather than silently falling back to defaults.

Alternative: keep the old key and rename only the surface. Also rejected — a
configuration key contradicting the product name is a durable inconsistency.

### Leave historical records under their original name

Archived OpenSpec changes, archived sprint records, and spike evidence keep the
former name. Their accuracy as records of what was decided and captured at the
time outranks global textual consistency, and rewriting them would make the
`2026-08-08` rename record self-contradictory.

Alternative: rewrite archives too, as the `2026-08-08` cycle did. Rejected by
the pilot for this cycle.

### Record the irregular order rather than hide it

Implementation preceded this proposal. The proposal states that plainly and
names the implementing commit. Reconstructing a two-commit cycle after the fact
would have produced a tidier but false record of how the decision was made.

## Risks / Trade-offs

- [An unmigrated project silently loses its runtime selections] → The rename is
  breaking and documented as such; the workspace catalogue was migrated with the
  implementation.
- [External automation still addresses the former distribution or plugin
  identifier] → Treated as breaking, with the new value stated consistently.
- [The framework name or its widget global is over-renamed] → Replacement was
  restricted to the exact strings `solid-node-studio` and `SolidNode Studio`,
  which cannot match `solid-node` alone or `SolidNodeWidget`.
- [Baseline and change records drift] → The delta specs were extracted
  mechanically from the committed baseline rather than retyped.

## Migration Plan

The implementation order actually followed:

1. Rename public metadata, runtime identifiers, and the configuration key.
2. Migrate the operating contract, README, architecture overview, ADRs, design
   material, skills, and baseline specs.
3. Migrate the 18 projects in the workspace catalogue to the new key.
4. Rebuild the browser frontend so the served brand matches.
5. Run the test suite and OpenSpec validation.
6. Write and archive this record (this step, performed afterwards).

Rollback is a revert of `ea1fff6` plus this record; no persistent user data is
migrated.

## Open Questions

None. The pilot supplied both canonical names and chose migration over a
compatibility fallback.
