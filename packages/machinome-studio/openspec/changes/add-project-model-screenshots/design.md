## Context

The hub already reserves a 158-pixel model-preview region on every project
card, but the production UI fills it with a striped placeholder. A project
session already invokes the selected solid-node CLI during preparation, after
source changes, and through the scoped `solid_build` tool. The same scoped MCP
surface exposes `solid_snapshot` only as temporary image output and exposes the
only Git commit operation available to scoped runtime agents.

The change crosses project preparation, build watching, the scoped MCP server,
project inventory, the hub stream, and the browser. It must preserve two
existing boundaries: Floor does not import project Python, and an image problem
must not turn a valid build or an important commit into a failure.

## Goals / Non-Goals

**Goals:**

- Maintain one canonical project-owned preview at `<project>/screenshot.png`.
- Refresh that preview best-effort after successful builds and immediately
  before floor-mediated commits.
- Include a changed preview in a floor-mediated commit without requiring an
  agent to stage it explicitly.
- Display the preview on hub cards for open and closed projects and refresh an
  already-connected hub when it changes.
- Preserve the current placeholder and all normal build and commit behavior
  when no usable screenshot exists.

**Non-Goals:**

- Rejecting or delaying a commit until screenshot freshness can be proven.
- Making screenshot success part of model-build success.
- Adding project-selectable camera, pose, image-size, or style settings.
- Replacing the richer snapshots machinists render and inspect as engineering
  evidence.
- Guaranteeing refreshes for terminal or CI builds performed while no shop
  session is observing the project.
- Rewriting existing project history or eagerly modifying closed projects.

## Decisions

### 1. `screenshot.png` is a project-root artifact with a fixed recipe

The canonical path is exactly `screenshot.png` beneath the verified project Git
root. The shop invokes the solid-node CLI as a subprocess and writes no project
Python. It renders a 640x360 PNG at time `0.1`, with orthographic projection,
autocenter and view-all enabled, and no diagnostic overlays. This is a stable
thumbnail recipe, not a design-evidence view and not a new project setting.

The shop selects the solid-node CLI's web renderer, which produces the
transparent canvas directly. It publishes the complete PNG bytes without
pixel post-processing, making the card background responsible for the preview
canvas without heuristic treatment of model geometry.

The renderer writes to a temporary file outside the project. The shop verifies
that a PNG was produced, compares its bytes with the existing regular
non-symlink `screenshot.png`, and atomically replaces the project file only when
the bytes differ. A failed subprocess, missing output, malformed output, unsafe
existing path, comparison failure, or replacement failure is a screenshot
failure only. The existing screenshot remains untouched whenever possible.

Writing directly to the final path was rejected because the hub could observe
a truncated image. Writing into `_build` was rejected because that directory is
framework-owned publication output and is intentionally the only functional
model boundary served by the workspace.

### 2. Every shop-owned success path requests the shared best-effort refresh

Project preparation requests a screenshot after its initial successful build.
The source watcher requests one after a build subprocess exits successfully.
The scoped `solid_build` tool requests one after a successful CLI result. When
the artifact watcher observes an externally published `viewer.json`, it also
requests a refresh, which covers a successful external build while the project
is open. A no-op external build that publishes nothing is unobservable and
cannot have changed the required screenshot.

These entry points call one shared helper with per-project serialization.
Repeated requests may coalesce, and only a completed render may replace the
file. Serialization prevents an older render from overwriting a newer request.
Screenshot errors are logged or returned as supplemental warning information;
they never replace a build result or publish a model-build failure.

Treating every artifact publication as a trigger was rejected because one
build publishes several files. `viewer.json` is the bounded success signal for
an externally owned publication; shop-owned subprocesses use their exit status.

### 3. The Git commit tool performs best-effort refresh and injection

Immediately before invoking `git commit`, the scoped `git_commit` tool requests
one screenshot refresh of the current project and then attempts
`git add -- screenshot.png` when the path is a regular non-symlink file. It
does not unstage, delete, or restore anything. It invokes the requested commit
even if rendering, comparison, replacement, or staging fails. Its response
preserves the Git result and may include a supplemental screenshot warning so
an agent can report degraded evidence without mistaking it for commit failure.

The initial project commit uses the same helper and best-effort staging after
the initial build, allowing a successfully rendered screenshot into the first
repository state. If the build or screenshot fails, preparation retains its
existing behavior and records the scaffold without the image.

A commit-freshness gate and staged-tree provenance check were rejected by the
pilot: commits are more important than previews. A Git hook was rejected
because it would alter commits made outside the floor, add repository setup,
and make failure behavior harder to keep subordinate. Prompt-only staging was
rejected because the requirement is shop machinery rather than agent conduct.

### 4. Inventory exposes availability and a content revision; one exact route serves it

Project inventory treats a screenshot as available only when
`<verified-root>/screenshot.png` is a regular non-symlink PNG. It derives a
content revision from its bytes and includes availability/revision in the hub
snapshot. The image route accepts only the project name and serves only that
exact file after repeating the existing direct-child and exact-repository-root
checks; it accepts no arbitrary project-relative path and works whether or not
the project has an open session.

The browser uses the content revision in the image URL so a changed screenshot
bypasses cache while identical content retains one URL. Missing, unreadable, or
failed images render the existing striped placeholder. The image has useful alt
text derived from the project name and uses contain-style sizing within the
existing 158-pixel preview region.

Serving the live `_build` viewer in miniature was rejected because it would
open a viewer per card and prevent closed projects from being cheap inventory.
Embedding image bytes in the hub snapshot was rejected because it would make
every state snapshot scale with all project images.

### 5. Screenshot changes are project metadata on the hub stream

An atomic replacement of `screenshot.png` while a session is open produces a
hub-scoped project update carrying the new content revision. It does not enter
the project conversation, broker event history, or another project's session
stream. A reconnect recomputes inventory and therefore recovers the latest
revision without event replay. The browser updates only the affected card's
image URL.

This is an intentional amendment to the current rule that hub live changes are
only lifecycle changes: the screenshot is durable project-card metadata, not
agent work or conversation.

### 6. The boundary is recorded durably

Implementation creates an ADR for the project-root screenshot convention, the
best-effort build/commit behavior, and the closed-project serving boundary. The
architecture overview and ADR index are updated when the ADR is accepted. The
runtime role contracts are revised so `screenshot.png` is recognized as a
shop-managed injected artifact, while arbitrary snapshots remain scratch that
agents do not commit.

## Risks / Trade-offs

- **A screenshot can be stale when rendering fails** → Preserve the last usable
  image and keep builds and commits honest about their own result; supplemental
  warnings expose the degraded preview when the caller can receive them.
- **A commit can contain no new screenshot after a model change** → This is the
  pilot's explicit best-effort trade-off; the next successful build or commit
  retries generation.
- **Rendering at both build and commit costs time** → Use a small fixed image,
  skip atomic replacement for byte-identical output, and serialize/coalesce
  build-driven requests. Commit-time rendering remains bounded and subordinate.
- **Renderer output may vary across machines or framework versions** → Fix all
  shop-controlled rendering inputs and compare final bytes. Framework rendering
  changes are legitimate preview changes rather than hidden compatibility work.
- **Web renderer output may differ from the prior OpenSCAD output** → The
  framework's web screenshot is the selected canonical preview renderer;
  engineering snapshots remain the evidence surface for close inspection.
- **An open hub could cache an old PNG** → Content-revision URLs change only
  when the bytes change, and live hub metadata updates target the affected card.
- **A malicious project may place a symlink at `screenshot.png`** → Never
  follow or replace it, do not stage it automatically, and serve the placeholder.

## Migration Plan

No eager migration runs. Existing projects without `screenshot.png` continue
to show the placeholder. Their next successful observed build or floor-mediated
commit attempts to create the image, after which a later commit can track it.
New projects attempt the image during initial preparation. Rolling back the shop
leaves an ordinary PNG in each project; older versions ignore it safely.

## Open Questions

None. The filename, repository location, best-effort failure behavior, and lack
of per-project rendering configuration are ratified inputs to this proposal.
