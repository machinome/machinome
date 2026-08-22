## 1. Profile-resolved skill metadata

- [ ] 1.1 Add a failing test that a resolved profile agent carries each
      allowlisted skill's name, description, and directory
- [ ] 1.2 Add failing tests that profile validation rejects a `SKILL.md` with
      missing frontmatter, a mismatched `name`, and an empty or absent
      `description`
- [ ] 1.3 Add `ProfileSkill(name, description, path)` and replace
      `ProfileAgent.skill_paths` with `ProfileAgent.skills`, parsing and
      validating `SKILL.md` frontmatter in `_skill_path`
- [ ] 1.4 Update existing profile and role-contract tests to the new field

## 2. The `load_skill` tool

- [ ] 2.1 Add failing tests: loading an announced skill returns its
      instructions and lists its bundled resources; an unregistered name fails
      naming what is available; a bundled `resource` is returned; a `resource`
      escaping the skill directory fails; a session with no registered skill
      does not advertise the tool
- [ ] 2.2 Add a failing test that a path inside a registered skill directory is
      still rejected by the path-taking tools
- [ ] 2.3 Implement `ProjectTools.load_skill`, its schema, and the
      `--skills-json` registry parameter on `mcp_command` and the server CLI
- [ ] 2.4 Advertise `load_skill` in `tools/list` only when the session has a
      registered skill

## 3. Claude backend

- [ ] 3.1 Add failing tests that a scoped role with skills gets
      `mcp__floor__load_skill` in `--tools` and in its readiness expectation,
      that its MCP config registers exactly that agent's skills, and that a
      role with no skill gets neither
- [ ] 3.2 Add a failing test that the session contract lists each skill's name
      and description, names the loading tool, and contains no `SKILL.md` path
- [ ] 3.3 Implement the registry in `_mcp_config`, the tool in `_role_command`
      and `_expected_tools`, and the catalogue in `_role_contract`

## 4. OpenCode backend

- [ ] 4.1 Add failing tests that the system contract carries the catalogue and
      no skill instructions, and that `floor_load_skill` is enabled in the
      prompt payload for a role with skills and absent for one without
- [ ] 4.2 Add a failing test that the server config registers the profile's
      skills
- [ ] 4.3 Implement the `skills` constructor parameter, its registration in
      `start()`, per-session skill tracking in `open_role`, the tool flag in
      `_prompt`, and the catalogue in `_system_contract`

## 5. Wiring

- [ ] 5.1 Thread the profile's skills through `create_backend` and
      `SessionRegistry`'s backend construction, with a test that the union of
      the profile's skills reaches the OpenCode backend
- [ ] 5.2 Run the full test suite and confirm no unrelated regression

## 6. Records

- [ ] 6.1 Update `docs/architecture-overview.md` where it describes how skills
      reach a runtime session
- [ ] 6.2 Update `AGENTS.md` if its description of skill exposure to runtime
      agents no longer matches
- [ ] 6.3 Sync baseline specs and archive the change
