## 1. Startup prerequisite

- [ ] 1.1 Add a failing test that starting the shop with `openspec` unresolvable fails before binding a listener, naming the missing prerequisite
- [ ] 1.2 Add a failing test that startup proceeds when `openspec` runs
- [ ] 1.3 Implement the fail-closed preflight in the orchestrator's startup path and turn 1.1-1.2 green

## 2. Profile capability

- [ ] 2.1 Add a failing test that a profile declaring `OpenSpec` resolves the floor's OpenSpec tools, and that an unknown capability name still fails validation
- [ ] 2.2 Add a failing test that no Fordesmac role session reaches an OpenSpec tool, including a role declaring every other capability
- [ ] 2.3 Add `OpenSpec` to the closed capability vocabulary in `floor/profiles.py` and map it in `PROFILE_TOOL_MAP`
- [ ] 2.4 Declare `OpenSpec` in `profiles/builder/profile.toml` and confirm `profiles/fordesmac/` is untouched

## 3. Project record preparation

- [ ] 3.1 Add a failing test that `openspec_setup` in a project with no record initializes it, seeds house rules, and commits, all inside the project
- [ ] 3.2 Add a failing test that a second `openspec_setup` reports the existing record, creates no commit, and leaves house rules byte-identical
- [ ] 3.3 Implement `openspec_setup` and turn 3.1-3.2 green

## 4. Root containment

- [ ] 4.1 Add a failing test that `openspec_run` in an unprepared project nested under a repository that has a record fails naming the ancestor root, and that the ancestor is unmodified
- [ ] 4.2 Add a failing test that `openspec_run` proceeds when the resolved root is the active project
- [ ] 4.3 Implement the pre-invocation root verification and turn 4.1-4.2 green

## 5. OpenSpec passthrough

- [ ] 5.1 Add a failing test that `openspec_run` creates a change in a prepared project and returns the CLI's status and output
- [ ] 5.2 Add a failing test that store, global configuration, and telemetry subcommands, and a `--store` argument, are rejected without starting a process
- [ ] 5.3 Implement `openspec_run` with its subcommand rejection and turn 5.1-5.2 green

## 6. Archive gate

- [ ] 6.1 Add a failing test that archiving a change with unchecked tasks is refused, names the incomplete tasks, and leaves the change unarchived
- [ ] 6.2 Add a failing test that archiving a fully complete change syncs its specs and archives it
- [ ] 6.3 Implement the gate against the CLI's JSON status, with no override argument, and turn 6.1-6.2 green

## 7. Spec-only commits

- [ ] 7.1 Add a failing test that a floor-mediated commit staging only spec-record files performs no render, leaves the screenshot unstaged and unchanged, and succeeds
- [ ] 7.2 Add a failing test that a commit staging model source alongside spec-record files still refreshes and stages the screenshot
- [ ] 7.3 Implement the staged-path inspection in `git_commit` and turn 7.1-7.2 green

## 8. Builder discipline

- [ ] 8.1 Write the two-commit cycle into `profiles/builder/builder.md` beside the red-first loop: prepare the record, propose and commit the plan, build red-first, sync, archive, commit
- [ ] 8.2 State in the prompt that a change alters an interface between parts, that at most one change is open, and that a committed plan is never rewritten
- [ ] 8.3 State that the Maker never ratifies and never handles a spec artifact
- [ ] 8.4 Verify the prompt still passes profile validation and the declared skills are unchanged

## 9. Seeded house rules

- [ ] 9.1 Write the seed content: a capability is an interface between parts, a requirement is a measurable guarantee, a scenario is one fit or assembly test
- [ ] 9.2 Add the `MODIFIED` whole-block rule and the `Purpose` rule to the seed's per-artifact rules
- [ ] 9.3 Add a test proving the seeded rules reach the agent through the CLI's own instructions output

## 10. Documentation and decisions

- [ ] 10.1 Record Node and `@fission-ai/openspec` as prerequisites in `README.md` and `scripts/setup`
- [ ] 10.2 Promote ADR 0027 to Accepted with its acceptance date and update `docs/adrs/README.md`
- [ ] 10.3 Update `docs/architecture-overview.md` for the OpenSpec tool surface, the new capability, and the external-CLI boundary

## 11. Close the cycle

- [ ] 11.1 Run the full test suite and record the result
- [ ] 11.2 Exercise the cycle end to end against a scratch project: prepare, propose, build, archive
- [ ] 11.3 Sync baseline specs, archive the change, and commit the implementation record
