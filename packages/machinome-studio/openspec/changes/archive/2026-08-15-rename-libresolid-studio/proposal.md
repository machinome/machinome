## Why

The repository has been renamed from `solid-node-studio` to `libresolid-studio`
and the product from “SolidNode Studio” to “LibreSolid Studio”. The ratified
`product-identity` capability named the former identities, so every specification
that quoted them — package and plugin metadata, the browser brand, the project
runtime-configuration key, and the cross-repository protocols — became
inaccurate at the moment of the rename. The baseline must state the identities
the product actually exposes.

## Record of how this change was made

This cycle was written **after** implementation, at the pilot's explicit
direction, and does not follow the normal propose-ratify-implement order.

- The rename was implemented and committed directly on the shop primary branch
  as `ea1fff6` (“feat: rename product to LibreSolid Studio”), including the
  edits to the baseline specifications this change now records.
- No proposal existed at the time of that commit, so the baseline briefly stated
  an identity that no ratified change backed.
- The pilot then directed that the specs be synced and that the irregular
  order be left visible in the record rather than reconstructed as a normal
  two-commit cycle.

The delta specifications here were extracted verbatim from the baseline as
committed in `ea1fff6`, so the change and the baseline agree by construction.
The preceding rename to SolidNode Studio (`2026-08-08-rename-solid-node-studio`)
did run the normal cycle and remains the reference for that order.

## What Changes

- **BREAKING**: Rename the Python distribution and plugin identifier to
  `libresolid-studio`.
- **BREAKING**: Rename the project runtime-configuration table a project
  declares in its `pyproject.toml` from `[tool.solid-node-studio]` to
  `[tool.libresolid-studio]`, with no compatibility fallback. Existing projects
  must migrate.
- Replace runtime service, agent, session, and temporary-resource identifiers
  derived from the former product name.
- Present the customer-facing product name as “LibreSolid Studio” in the
  browser workspace, documentation, and descriptive metadata.
- Name `libresolid-studio` as the shop repository in the framework-change and
  sprint-coordination protocols.
- Preserve the `solid-node` framework name, its `SolidNodeWidget` browser
  global, and mechanical shop-domain vocabulary.
- Preserve archived changes and sprint records unchanged as historical evidence
  of decisions taken under the former name.

## Capabilities

### Modified Capabilities

- `product-identity`: The canonical customer-facing and machine-readable
  identities become `LibreSolid Studio` and `libresolid-studio`.
- `project-runtime-selection`: The project-owned runtime-configuration table is
  `[tool.libresolid-studio]`.
- `shop-browser-workspace`: The browser workspace presents `LibreSolid Studio`.
- `framework-change-protocol`: Framework orchestration is owned by
  `libresolid-studio`.
- `sprint-coordination`: Sprint scope names `libresolid-studio` as the shop
  repository.

## Impact

This affects package and plugin metadata including repository URLs, floor
runtime identifiers, browser branding, the project runtime-configuration
contract, the operating contract, README, architecture overview, ADRs, design
material, skills, tests, and baseline specifications.

Every existing project that declares `[tool.solid-node-studio]` stops being
readable until it migrates. The 18 projects in this workspace's `projects/`
catalogue were migrated in place as part of the implementation; each of those
edits remains uncommitted in its own project repository, because those repos
carry unrelated in-progress work that is not this change's to commit.
