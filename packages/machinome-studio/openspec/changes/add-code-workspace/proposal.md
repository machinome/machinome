## Why

The workspace exposes the live functional model and its agent conversation, but
the maker cannot inspect or edit the project source that produces that model.
Adding a Code workspace closes that loop while preserving the filesystem as the
single change boundary for maker and agent edits.

## What Changes

- Replace the deferred Files and Code rail items with one interactive Code area
  immediately after Model. Code owns a project-root navigator and Monaco editor
  while the existing conversation remains mounted at the right.
- Expose only the project's Git-visible working set: tracked files and untracked
  files not excluded by Git ignore rules. `.git`, ignored paths, build output,
  binary files, and unsafe paths are not editable source.
- Add project-scoped list, read, and revision-checked atomic-save operations.
  A stale save is rejected instead of overwriting a concurrent agent edit.
- Publish filesystem create, modify, move, and delete events so clean editor
  buffers refresh automatically, dirty buffers enter an explicit conflict
  state, and agent-created untracked files appear without tool instrumentation.
- Route every saved Python source through the existing source watcher rather
  than adding a browser-specific build path.
- Record maker saves as trusted `user_file_changed` system notices for the
  agents whose broker work state was active at save time. Notices neither enter
  conversation nor change assignments, never wake an idle agent, and survive a
  turn-completion race until each recipient's next ordinary turn.
- Preserve chat draft/scroll, Monaco models and dirty buffers, and functional
  model view state while the maker changes workspace areas.
- Amend the source boundary: the Floor may serve verified project source as
  inert text for editing, but still never imports, interprets, or executes it;
  the Model area continues to consume only published build artifacts.

## Capabilities

### New Capabilities
- `project-source-editing`: Git-visible source discovery, safe text reads,
  revision-checked saves, filesystem synchronization, conflicts, and retained
  maker-change notices.

### Modified Capabilities
- `shop-browser-workspace`: Make Code the second interactive workspace area,
  remove Files, preserve the conversation and per-area state, and render the
  project navigator and Monaco editor.
- `shop-agent-messaging`: Deliver trusted informational file-change notices to
  agents active at save time without waking idle agents or changing work state.
- `functional-model-inspection`: Treat maker saves like every other qualifying
  filesystem source change and build them through the existing watcher.

## Impact

- `floor/app.py`, `floor/sessions.py`, `floor/watcher.py`, and orchestration
  state gain safe source APIs, source events, and retained system delivery.
- `floor/frontend/` gains Monaco, file/navigation/editor state, conflict UI,
  and interactive Model/Code switching; the checked-in production bundle is
  rebuilt.
- Browser API and broker event contracts gain project-file operations and a
  trusted non-conversation notice kind.
- Focused backend, watcher, orchestrator, frontend, and browser acceptance
  coverage is required.
- A new ADR amends ADR 0004's no-source-serving clause; the ADR index,
  architecture overview, reference design, and baseline specs are updated.
