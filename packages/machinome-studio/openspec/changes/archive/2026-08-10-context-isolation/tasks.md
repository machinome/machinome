## 1. MCP tool server

- [x] 1.1 Scaffold a floor-owned MCP server module implementing project-root
      path sandboxing shared by every tool
- [x] 1.2 Implement filesystem read tools: `list_dir`, `find_files`,
      `search_content`, `read_file` (with raster-image passthrough, SVG kept
      as text), `stat`
- [x] 1.3 Implement filesystem write tools: `write_file`, `edit_file`,
      `apply_patch`, `delete_file`, `move_file`, `make_dir`
- [x] 1.4 Implement git tools: `git_status`, `git_diff`, `git_log`,
      `git_show`, `git_rev_parse_toplevel`, `git_merge_base_is_ancestor`,
      `git_head`, `git_add`, `git_commit`
- [x] 1.5 Implement `solid_build` and `solid_test`, matching CLI argument and
      exit-status semantics
- [x] 1.6 Implement `solid_snapshot`: render to a temp path outside the
      project tree, return image content, delete the temp file
- [x] 1.7 Unit-test project-root sandboxing (escape attempts rejected) across
      every tool
- [x] 1.8 Implement bounded shop-broker lifecycle tools: `floor_assign`,
      `floor_direction`, `floor_acknowledge`, `floor_report`, `floor_complete`
      using only the backend-injected floor URL and active session
- [x] 1.9 Unit-test broker request mapping and confirm no generic network tool
      or caller-selectable URL/route is exposed

## 2. `claude` backend wiring

- [x] 2.1 Stop unconditionally passing `--safe-mode` in
      `floor/backends/claude.py` for roles configured with scoped tools
- [x] 2.2 Generate `--mcp-config`/`--strict-mcp-config` pointing at the floor
      tool server and pass `--tools mcp__<server>__<tool>` for the resolved
      tool list
- [x] 2.3 Verify MCP server connection status while accepting the first
      broker delivery, using a bounded readiness deadline

## 3. `opencode` backend wiring

- [x] 3.1 Generate `mcp` config entry pointing at the floor tool server in
      `floor/backends/opencode.py`
- [x] 3.2 Generate `tools: {...: false}` disabling every native tool, using
      the default `build` agent (no custom agent/permission block)
- [x] 3.3 Use a unique working directory per role launch to avoid session
      state bleed across `opencode serve` process launches

## 4. Documentation and cleanup

- [x] 4.1 Update `floor/profiles.py` comments/validation to reflect real
      enforcement for `claude`/`opencode` tool declarations, and unchanged
      non-enforcement for `codex`
- [x] 4.2 Document the librarian's tool surface as provisionally
      non-functional under this change
- [x] 4.3 Update Fordesmac role instructions to use the floor MCP lifecycle
      tools instead of `python -m floor.agent` shell commands
- [x] 4.4 Run combined validation (per AGENTS.md sprint/change discipline) and
      confirm existing roles unaffected by this change still work unchanged

## 5. Runtime provenance and isolated OpenCode events

- [x] 5.1 Add red entry-point tests proving both floor launchers start outside
      Git with an arbitrary required `--projects-dir` and never resolve a
      primary checkout
- [x] 5.2 Replace primary-checkout runtime discovery with loaded-package
      resource provenance for profiles, prompts, skills, assets, backend
      imports, and child MCP processes
- [x] 5.3 Add red OpenCode coverage proving a completed response from a unique
      role working directory crosses the adapter boundary, while unrelated
      directory/session events are ignored
- [x] 5.4 Consume OpenCode's cross-directory event stream and reconcile idle
      and failure events for registered role sessions
- [x] 5.5 Update launcher/operator and reference architecture documentation to
      make `--projects-dir` authoritative and remove runtime Git-checkout and
      checkout-relative project assumptions
- [x] 5.6 Run focused tests, the full suite, OpenSpec validation, and a live
      `delme-opencode` regression from this worktree
- [x] 5.7 Bind the default solid-node command to the shop's Python environment
      and cover an unrelated or broken ambient `solid` executable
- [x] 5.8 Add red regressions and implement immediate deduplicated OpenCode
      text-part delivery plus non-overlapping transcript/composer grid tracks
- [x] 5.9 Add red Claude startup regressions and separate immediate process
      exit detection from bounded MCP readiness that waits through `pending`
- [x] 5.10 Reproduce input-triggered Claude init, manifest the process without
      a warm-up turn, and gate the first real broker delivery on MCP readiness
