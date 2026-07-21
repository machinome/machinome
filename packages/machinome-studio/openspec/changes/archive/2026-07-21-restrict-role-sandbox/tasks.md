## 1. Restrict role execution

- [x] 1.1 Change app-server role-thread creation to use the prepared project as a `workspace-write` sandbox and omit the hard-coded approval override.
- [x] 1.2 Confirm that the app-server adapter retains the project root as every role's `cwd` without adding writable roots or network exceptions.

## 2. Prove and document the boundary

- [x] 2.1 Add a red-first adapter regression that inspects each role's outgoing `thread/start` request and proves it excludes unrestricted sandbox and no-approval settings.
- [x] 2.2 Run focused orchestration tests and the full shop test suite; report any workflow that now legitimately requires a separately approved exception.
- [x] 2.3 Update the relevant runtime documentation or ADR consequence if it still implies unrestricted role execution.
