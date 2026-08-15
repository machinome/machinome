repo: LibreSolid/libresolid-studio
branch: main
path: floor/frontend/src

## Last sync

date: 2026-08-13T08:30:39Z

### Updated in this project

- Recreated the project floor page (rail, Model, Code, Agents areas, chat column) from `floor/frontend/src/main.tsx` and `styles.css`.
- Added a new **Build** rail section replacing the disabled **Sheets** item: plate grid of published STL pieces, per-piece analysis drawer, printer profile and package download.

## Screen map

| Project screen | Repo files |
| --- | --- |
| Project Floor.dc.html — workspace shell, rail, chat | floor/frontend/src/main.tsx (`Workspace`, `railItems`), floor/frontend/src/styles.css |
| Project Floor.dc.html — Model area | floor/frontend/src/main.tsx (`AssemblyPanel`, `AgentPanel`, `FunctionalModel`) |
| Project Floor.dc.html — Code area | floor/frontend/src/main.tsx (`CodeWorkspace`, `SourceIcon`) |
| Project Floor.dc.html — Agents area | floor/frontend/src/main.tsx (`AgentsWorkspace`) |
| Project Floor.dc.html — Build area (new) | new design; vocabulary from shop-skills/solid-node/SKILL.md, README.md |
