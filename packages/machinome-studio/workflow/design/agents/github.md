repo: LibreSolid/solid-node-studio
branch: main
path: floor/

## Last sync

date: 2026-08-11T20:45:36Z

### Updated in this project

- Recreated the workspace shell (titlebar, activity rail, context column, chat, status bar) from `floor/frontend/src/styles.css`.
- Designed the Agents section: agent roster with per-agent runtime, live activity feed with tool calls and unified diffs.
- Added a per-agent control panel for backend, model, and reasoning with apply-now / next-assignment and pyproject.toml options.

## Screen map

| Screen | Repo files |
| --- | --- |
| Agents.dc.html | floor/frontend/src/main.tsx (Workspace, AgentPanel, ProfileConversation, railItems), floor/frontend/src/styles.css, profiles/fordesmac/profile.toml, profiles/builder/profile.toml, floor/mcp_server.py (TOOL_NAMES, PROFILE_TOOL_MAP), floor/app.py (broker event kinds), README.md (per-agent backend/model/reasoning selection) |

## Notes

Tool calls, tool results, and file diffs are not present in the broker event
stream today (`floor/app.py` publishes `agent_*`, `work_*`, `direct_work_*`,
`conversation_entry`, `model_artifact_changed`, `source_file_changed`). The
activity feed in this design implies new per-agent event kinds. Tool names,
roles, models, and effort values in the mock data come from
`floor/mcp_server.py` and the profile TOMLs.
