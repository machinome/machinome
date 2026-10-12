## 1. Workspace

- [x] 1.1 `.gitignore`: ignore `/solid-node-viewer` with a comment naming it an independent repository.
- [x] 1.2 `scripts/setup`: tier 1 installs `"solid-node[viewer]"`; tier 2 clones `SOLID_NODE_VIEWER_REPO` to `./solid-node-viewer`, installs it editable, builds widget and app there; remove the npm steps inside `solid-node/`; update the header comment.
- [x] 1.3 `scripts/dev-env`: remove the frontend-link step, `VIEWERS_DIR` and the comments describing it; keep ports. `tests/dev-env-test.sh`: drop the two frontend-link tests and the viewer fixture directories; keep the port assertions.

## 2. Contract and documentation

- [x] 2.1 `AGENTS.md`: current-status bullet for the viewer; a "solid-node-viewer work" lane after molejo's; workspace layout and entry points; the framework lane notes the viewer is not framework source and that `solid develop` opens OpenSCAD without the extra.
- [x] 2.2 `README.md`: workspace mechanics for both tiers and the layout.
- [x] 2.3 `docs/architecture-overview.md`: workspace layout and the floor-preparation paragraph name the viewer package and the framework's report of it.

## 3. Agent knowledge

- [x] 3.1 `shop-skills/solid-node-api/SKILL.md`: `solid viewer` fields and failure; `solid develop` default by installation; `--renderer web` requires the viewer extras; exports ship the installed viewer's files.
- [x] 3.2 `shop-skills/solid-node/SKILL.md` and `skills/running-the-shop/SKILL.md`: the develop note and the open-failure guidance name the extra.

## 4. Floor evidence

- [x] 4.1 `tests/fixtures/fake_solid.py`: the missing-viewer message names `pip install "solid-node[viewer]"`; add `index` and `version` to the fake report so it matches the real one.
- [x] 4.2 Run the shop suite (`pytest`, `tests/dev-env-test.sh`) and confirm the project-open failure test still reads the remedy through.
