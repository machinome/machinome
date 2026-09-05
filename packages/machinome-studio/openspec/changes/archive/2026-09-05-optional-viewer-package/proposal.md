## Why

The browser viewer has left solid-node and become `solid-node-viewer`, an
independent AGPL-3.0-only package installed through the framework's `viewer`
extra. The shop installs the framework, benches its worktrees, opens floors
on the viewer the framework reports, and documents all of that for its
agents; every one of those places still assumes the viewer is inside the
framework and is built with npm there.

## What Changes

- Add `solid-node-viewer/` to the workspace as a fourth kind of ignored,
  independent repository beside the framework, molejo and the browser
  prototypes; give it its own lane in the agent contract, like molejo's:
  work happens inside that repository under its own OpenSpec, never through
  the shop's worktree or sprint machinery, and its status claims stay honest
  (0.1.0 unreleased, on no index yet).
- `scripts/setup`: tier 1 installs `solid-node[viewer]`; tier 2 clones the
  viewer repository beside the framework, installs it editable and builds its
  two frontends there. Nothing is built inside `solid-node/` any more.
- `scripts/dev-env`: drop the frontend-link step and its tests; a framework
  worktree has no frontends to link.
- The floor keeps obtaining the viewer through `solid viewer`; the requirement
  is restated so that "no viewer" means the viewer package is not installed,
  and the remedy the maker sees is the extra.
- Agent-facing knowledge: the solid-node API skill's `solid viewer`, `solid
  develop` and `--renderer web` entries, the machining skill's develop note,
  and the running-the-shop skill's failure guidance.
- Reference documentation: README workspace mechanics, the architecture
  overview's workspace layout and floor-preparation paragraph, and the
  fake `solid` fixture's viewer messages.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `functional-model-inspection`: the viewer the floor requires comes from the
  installed viewer package, reported by the framework; "no viewer" is "the
  extra is not installed", and the remedy says so.

## Impact

`.gitignore`, `AGENTS.md`, `README.md`, `docs/architecture-overview.md`,
`scripts/setup`, `scripts/dev-env`, `tests/dev-env-test.sh`,
`tests/fixtures/fake_solid.py`, `shop-skills/solid-node-api/SKILL.md`,
`shop-skills/solid-node/SKILL.md`, `skills/running-the-shop/SKILL.md`,
`openspec/specs/functional-model-inspection/spec.md`. No floor Python
changes: `solid viewer` still answers with `path` and `apiVersion`, and the
floor already forwards the framework's stderr as the failure reason. Paired
with solid-node's `optional-viewer-package` change and solid-node-viewer
0.1.0.
