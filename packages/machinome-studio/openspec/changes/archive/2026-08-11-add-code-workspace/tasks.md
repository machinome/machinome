## 1. Safe project source service

- [x] 1.1 Add failing unit/API tests for Git-visible tracked and untracked discovery, ignored/build/control-path exclusion, symlink and traversal rejection, binary/size bounds, and project-session isolation
- [x] 1.2 Implement a project-rooted source service that enumerates through Git, synthesizes directory entries, reads bounded UTF-8 text, and returns SHA-256 revisions
- [x] 1.3 Add failing API tests for accepted atomic saves, mode preservation, stale revision conflicts, disappeared/ignored targets, and no maker-side create operation
- [x] 1.4 Implement session-scoped list/read/save routes with revision comparison, a save lock, same-directory atomic replacement, and precise HTTP errors
- [x] 1.5 Add failing watcher/API tests for project-scoped create/modify/move/delete invalidations, ignored/build event containment, and reconnect reconciliation inputs
- [x] 1.6 Publish source invalidation events from the existing session observer without changing the model watcher's Python-only build and debounce path

## 2. Retained active-agent notices

- [x] 2.1 Add failing broker/orchestrator tests for active-recipient capture, per-path coalescing, continuing-turn injection, completion-race retention, next-ordinary-turn delivery, waiting-agent exclusion, and unchanged conversation/work state
- [x] 2.2 Add retained trusted notice state and event framing separate from user direction, assignments, reports, and conversation
- [x] 2.3 Extend the portable backend protocol with steer-only notice delivery and add failing/green Codex, Claude, and OpenCode adapter coverage proving it never starts a turn
- [x] 2.4 Wire an accepted maker save through its session to snapshot broker-active roles, attempt notice injection, and retain any unaccepted notice until ordinary delivery

## 3. Monaco Code workspace

- [x] 3.1 Add locally bundled `monaco-editor` and `@monaco-editor/react` dependencies and configure Vite workers without a CDN
- [x] 3.2 Replace the Files/Code deferred rail entries with interactive Model and Code areas while keeping Agents and Sheets deferred and the conversation mounted outside the area switch
- [x] 3.3 Implement the Git-visible navigator, per-path Monaco models/tabs, language selection, dirty state, Ctrl/Cmd+S, revision-checked saves, and accessible loading/error states
- [x] 3.4 Implement source-event and reconnect reconciliation: clean external replacement, own-save suppression, dirty conflict preservation, explicit reload, tree refresh for agent-created/moved/deleted files, and no actor attribution
- [x] 3.5 Preserve chat draft/scroll, Monaco tabs/models/view/undo state, and functional-model camera/timeline state across Model/Code switches
- [x] 3.6 Add browser acceptance coverage for browse/open/edit/save/build, external clean refresh, dirty conflict and stale-save protection, untracked file appearance, ignored file exclusion, persistent chat, and persistent model/editor state

## 4. Architecture and durable contracts

- [x] 4.1 Add and accept an ADR amending ADR 0004 so Floor may serve verified project source as inert text while `_build` remains the Model input, then update the ADR index
- [x] 4.2 Rewrite the architecture overview for the source service, source invalidations, Monaco workspace, revision conflicts, and retained steer-only notices
- [x] 4.3 Update the reference design to remove Files, make Code second, remove unsupported agent attribution, and document the accepted navigator/editor/conflict behavior
- [x] 4.4 Sync the project-source-editing, shop-browser-workspace, shop-agent-messaging, and functional-model-inspection delta requirements into baseline specs

## 5. Validation and completion

- [x] 5.1 Run focused source service, watcher, broker, orchestrator, backend, API, and browser acceptance tests red-first and then green
- [x] 5.2 Run frontend type-check/build and rebuild the checked-in `floor/static/` production assets
- [x] 5.3 Run the full Python test suite and OpenSpec strict validation, recording any environmental limitation honestly
- [x] 5.4 Archive the completed OpenSpec change and verify the archived record, baseline specs, ADR, architecture, source bundle, and tests are all present in the implementation commit
