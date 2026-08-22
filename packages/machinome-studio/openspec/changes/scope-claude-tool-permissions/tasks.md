## 1. Claude adapter argv

- [ ] 1.1 Add a failing test that a scoped role's argv carries no
      `--permission-mode` at all
- [ ] 1.2 Add a failing test that the argv grants exactly the role's resolved
      floor tools through `--allowedTools`
- [ ] 1.3 Add a failing test that the argv denies exactly the floor tools the
      role did not resolve through `--disallowedTools`, using the librarian
      (which declares no `Edit`) so the subset case is covered
- [ ] 1.4 Add a failing test that the argv disables every built-in tool
- [ ] 1.5 Implement the allowlist, denylist, and empty built-in set in
      `_role_command`; delete the `--permission-mode` branch
- [ ] 1.6 Delete the unscoped `--safe-mode` branch and make a Claude runtime
      without a concrete tool list a startup error

## 2. Profile declaration

- [ ] 2.1 Add a failing test that a Claude runtime table declaring `permission`
      is rejected, and that a table declaring `tools = "inherit"` is rejected
- [ ] 2.2 Remove `permission` from `BackendRuntime`, `_CLAUDE_RUNTIME`, and
      `_runtime` validation; require a concrete Claude tool list
- [ ] 2.3 Drop the `permission` line from all five Claude runtime tables in
      `profiles/fordesmac/profile.toml` and `profiles/builder/profile.toml`
- [ ] 2.4 Update the profile, project-runtime-selection, and role-contract
      tests that assert on the retired field

## 3. Live verification

- [ ] 3.1 Re-run the design spike's argv shape against the real `claude` CLI and
      the real `floor.mcp_server` at the librarian's exact scope, confirming
      `permissionMode: default`, exactly the declared tools advertised, an
      allowlisted write executing with empty `permission_denials`, and a
      denied tool absent
- [ ] 3.2 Update `tests/fixtures/fake_claude_cli.py` so its init frame reports
      the default permission mode and the tools the argv actually grants,
      rather than a fixed bypass
- [ ] 3.3 Run the full test suite and confirm no unrelated regression

## 4. Records

- [ ] 4.1 Write an ADR superseding ADR 0015, recording deny-by-default Claude
      permissions with the declared tool list as the whole authority; set
      ADR 0015 to `Superseded by NNNN` and update `docs/adrs/README.md`
- [ ] 4.2 Update `docs/architecture-overview.md` where it describes Claude
      permission handling or profile runtime declarations
- [ ] 4.3 Sync baseline specs and archive the change
