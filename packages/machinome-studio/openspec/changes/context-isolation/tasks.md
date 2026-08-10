## 1. MCP tool server

- [ ] 1.1 Scaffold a floor-owned MCP server module implementing project-root
      path sandboxing shared by every tool
- [ ] 1.2 Implement filesystem read tools: `list_dir`, `find_files`,
      `search_content`, `read_file` (with raster-image passthrough, SVG kept
      as text), `stat`
- [ ] 1.3 Implement filesystem write tools: `write_file`, `edit_file`,
      `apply_patch`, `delete_file`, `move_file`, `make_dir`
- [ ] 1.4 Implement git tools: `git_status`, `git_diff`, `git_log`,
      `git_show`, `git_rev_parse_toplevel`, `git_merge_base_is_ancestor`,
      `git_head`, `git_add`, `git_commit`
- [ ] 1.5 Implement `solid_build` and `solid_test`, matching CLI argument and
      exit-status semantics
- [ ] 1.6 Implement `solid_snapshot`: render to a temp path outside the
      project tree, return image content, delete the temp file
- [ ] 1.7 Unit-test project-root sandboxing (escape attempts rejected) across
      every tool

## 2. `claude` backend wiring

- [ ] 2.1 Stop unconditionally passing `--safe-mode` in
      `floor/backends/claude.py` for roles configured with scoped tools
- [ ] 2.2 Generate `--mcp-config`/`--strict-mcp-config` pointing at the floor
      tool server and pass `--tools mcp__<server>__<tool>` for the resolved
      tool list
- [ ] 2.3 Verify MCP server connection status before first turn (respect
      existing `startup_grace`) to avoid the race observed in the spike

## 3. `opencode` backend wiring

- [ ] 3.1 Generate `mcp` config entry pointing at the floor tool server in
      `floor/backends/opencode.py`
- [ ] 3.2 Generate `tools: {...: false}` disabling every native tool, using
      the default `build` agent (no custom agent/permission block)
- [ ] 3.3 Use a unique working directory per role launch to avoid session
      state bleed across `opencode serve` process launches

## 4. Documentation and cleanup

- [ ] 4.1 Update `floor/profiles.py` comments/validation to reflect real
      enforcement for `claude`/`opencode` tool declarations, and unchanged
      non-enforcement for `codex`
- [ ] 4.2 Document the librarian's tool surface as provisionally
      non-functional under this change
- [ ] 4.3 Run combined validation (per AGENTS.md sprint/change discipline) and
      confirm existing roles unaffected by this change still work unchanged
