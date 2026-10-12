## Context

The shop runtime verifies and prepares one independent project repository before
it opens role sessions. `CodexAppServer.start_thread` already passes that
repository as the thread `cwd`, but it separately overrides the role sandbox
to `danger-full-access` and disables approval prompts. That grants each role
the host's unrestricted filesystem and network authority even though the run
has a narrower durable work boundary.

The app-server protocol accepts per-thread sandbox and approval settings. The
change must retain the single app-server owner, persistent role threads, broker
delivery semantics, and the ability for a role to read its shop role card and
skills outside the project repository.

## Goals / Non-Goals

**Goals:**

- Constrain model-generated role commands to the verified project workspace.
- Remove the application's hard-coded unrestricted sandbox and no-approval
  override.
- Make the chosen boundary observable in focused adapter tests.

**Non-Goals:**

- Changing the broker, role prompts, project preparation, or app-server
  ownership model.
- Adding project-specific permission exceptions, network access, or new
  writable roots.
- Changing the pilot's own Codex permissions outside live shop role threads.

## Decisions

### Use the prepared project root as each role's workspace-write root

Each `thread/start` request SHALL retain the verified project root as `cwd` and
set its sandbox to `workspace-write`. This aligns the runtime authority with
the project repository selected during preparation. It permits normal
mechanical-project edits and local commands while keeping writes and network
access bounded by Codex's workspace policy.

The alternative—using the shop checkout as the workspace—would let the roles
modify harness code and would not match the project ownership boundary. Adding
both directories as writable roots would likewise permit unintended shop
changes and is not needed for the role cards or skills, which only need to be
read.

### Do not override the approval policy

The adapter SHALL omit `approvalPolicy` from `thread/start`. The configured
Codex workspace policy therefore governs prompts for boundary crossings rather
than the shop silently forcing `never`.

The alternative of hard-coding `on-request` would be safer than `never` but
would still override an explicit pilot or managed-workspace policy. Keeping
the adapter neutral makes the project's configuration the source of the
approval behavior.

### Test the outgoing app-server request, not only role state

Extend the fake app-server fixture or adapter tests to retain the complete
`thread/start` parameters. Assert every created shop role uses
`workspace-write`, its `cwd` equals the prepared project root, and the request
does not contain `approvalPolicy` or `danger-full-access`. This regression
test is independent of live account availability and validates the security
boundary at the adapter seam.

## Risks / Trade-offs

- [A role needs a new operation outside the project boundary] → Codex presents
  the configured approval path; introduce a narrowly scoped, ratified
  exception only when a real workflow requires one.
- [A dependency installer or CAD tool expects network access] → keep the live
  role turn bounded by default and have the pilot approve the specific action;
  do not restore full access globally.
- [App-server sandbox fields change while experimental] → retain protocol
  adapter tests and validate against the installed app-server schema before
  upgrading the integration.
