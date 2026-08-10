## Why

Project cards reserve a model-preview area but currently show only a placeholder,
so the maker cannot visually distinguish projects from the hub. The shop already
owns project builds and bounded screenshot rendering, and its scoped Git commit
tool is the reliable place to carry a changed preview into project history.

## What Changes

- After every successful project build the shop makes a best-effort model
  screenshot at the project-root path `screenshot.png`, replacing it only after
  a complete image has been rendered.
- A screenshot failure never fails a model build or prevents a Git commit; the
  prior screenshot remains untouched, or the project remains without one.
- The scoped `git_commit` operation best-effort stages `screenshot.png` when it
  exists and has changed, then performs the requested commit regardless of
  screenshot generation or staging failure.
- New projects attempt their first screenshot during preparation so a successful
  initial render can be recorded in the initial repository state.
- Project cards display `screenshot.png` when available and retain the existing
  placeholder when it is absent or cannot be read.
- Hub state identifies the current screenshot revision and updates connected hub
  browsers when an open project's screenshot changes, without carrying project
  conversation or agent work into the hub stream.
- Rendering uses one fixed, shop-owned thumbnail recipe rather than adding
  project configuration in this change; its edge-connected pale canvas is
  converted to transparent alpha after rendering.

## Capabilities

### New Capabilities
- `project-model-screenshot`: Own the best-effort generation, atomic project-root
  publication, and lifecycle of the canonical `screenshot.png` model preview.

### Modified Capabilities
- `functional-model-inspection`: A successful shop build also requests a model
  screenshot without changing build success or failure semantics.
- `scoped-agent-tools`: `git_commit` best-effort stages the canonical screenshot
  before committing and never rejects the commit because screenshot work failed.
- `named-project-bootstrap`: Project preparation attempts a first screenshot in
  time for a successfully rendered image to join the initial commit.
- `shop-project-hub`: Project cards render the project screenshot with a safe
  placeholder fallback.
- `shop-live-state-stream`: Hub snapshots and live changes carry screenshot
  revision state so an already-open hub refreshes changed previews.

## Impact

- Project repositories gain one shop-managed, tracked convention at
  `<project>/screenshot.png`.
- Project preparation, source-triggered builds, externally observed successful
  publications, the scoped solid build and Git commit tools, and their tests are
  affected.
- The hub inventory/API gains screenshot availability or revision metadata and a
  narrowly scoped image route that also works for closed projects.
- The React hub replaces its placeholder with an accessible, cache-busted image
  while preserving the existing card dimensions and fallback.
- Runtime role instructions must recognize `screenshot.png` as shop-managed
  commit evidence rather than agent-created snapshot scratch.
- The committed-preview and best-effort commit-injection boundary should be
  recorded in an ADR and reflected in the architecture overview and ADR index.
