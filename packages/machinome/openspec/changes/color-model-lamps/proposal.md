## Why

Enigma's existing 26 lamp glasses need the electrical observation to select their unpowered/powered colors in the ordinary model document and Studio controls. The recorded actual-glass probe produces `#e5dfce → #ffd978 → #e5dfce` numerically but fails ordinary symbolic publication; current public alternatives provide static colors or host overlays, not a model-state color law.

## What Changes

- Add the proposed public helper `machinome.color.color_when(condition, *, on, off)` for selecting between two fixed six-digit hex colors. Numeric calls return the selected hex; symbolic calls retain a scalar predicate and both colors for ordinary publication.
- Extend the existing node `color` value with that one conditional form; preserve existing hex/None declarations, inheritance and fixed markings. Geometry, part/model identity and physical calculations are unchanged.
- Publish a conditional `color` as `{when: <scalar expression>, on: '#RRGGBB', off: '#RRGGBB'}`; choice-bearing documents require **version 14**, while documents without a symbolic choice retain their current format and bytes.
- Coordinate the viewer-owned companion `read-model-color-choice`: normal controls pose color from the same admitted scope as placement, including native/posed, clocked and running reset/restore/replay. No host script, model postprocessing or duplicate bodies.
- Document the helper and its compatibility gate, with the matching API shop-skill contract update.

## Capabilities

### New Capabilities

- `state-color`: numeric/symbolic selection of one existing body's color from model state.

### Modified Capabilities

- `node-model`: admit the single conditional-color value in addition to existing static hex/None.
- `export`: version-gated, shared-expression publication of conditional colors across ordinary producers.
- `user-documentation`: document the helper, lifecycle semantics and explicit consumer requirement.

## Impact

Core targets: proposed `packages/machinome/machinome/color.py`, node colorization/presentation, `core/serializer.py`, existing expression-sharing and state publication paths, tests and the existing public manual/reference. Viewer source and its own specs belong to companion `packages/machinome-viewer/openspec/changes/read-model-color-choice/`, not this package's allowed implementation root. The API shop skill is owned by Studio at `packages/machinome-studio/machinome/studio/shop-skills/machinome-api/SKILL.md` (ADR-193); its synchronized contract update is a named completion dependency under that product's process, not authority to change Studio UI or orchestration. No separate installed repository or copied contract is edited by this proposal.

No emission, physical brightness, bloom, lighting simulation, textures, continuous RGB platform, solver or new electrical behavior. The lit color is the source-backed positive control under the viewer's existing lighting. One helper is recommended over a new appearance declaration/method family; its spelling and wire shape are approved within the pilot’s advance implementation authorization and the coordinating agent’s review.

Standalone coordinated cycle, base clean `main` at `6f07b083d3e9a4194d5f982ce200ae9dc6ffe4b9`; managed branch/worktree `illuminate-model-lamps`, slot 14. The pilot’s active goal authorizes completion and local integration, subject to coordinating-agent review and the immediate capture predecessor. Record its completed integration HEAD before the planning commit and implementation. No installed-environment change, push or publication is authorized. Accepted ADR-188/194/196 establish the current monorepo viewer target; the workspace's older separate-viewer description and core OpenSpec's stale monolithic/symlink context are recorded discrepancies, not instructions adopted or repaired here.
