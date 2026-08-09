## 1. Broker failure state

- [x] 1.1 Add red broker tests for snapshot-persistent role failure/recovery events and assignment-state preservation
- [x] 1.2 Implement optional per-agent failure state and broker failure/recovery operations

## 2. Orchestrator recovery

- [x] 2.1 Replace the fail-closed role-event test with red tests for retained-session recovery, dead-session replacement, exhausted retry handling, and unchanged backend-wide failure behavior
- [x] 2.2 Implement serialized role failure handling and next-envelope recovery without ending either routing loop

## 3. Browser notice

- [x] 3.1 Add red browser acceptance coverage for a live and snapshot-restored failure notice that clears after recovery
- [x] 3.2 Render accessible profile-labelled recovery notices from agent run state and style them in the conversation area
- [x] 3.3 Rebuild the checked-in frontend artifacts

## 4. Records and validation

- [x] 4.1 Update the architecture overview to describe recoverable role failures and runtime-ending backend failures
- [x] 4.2 Run focused broker, orchestrator, API, frontend build, and browser acceptance tests
- [x] 4.3 Validate the OpenSpec change and run the complete shop test suite
