# Main integration validation

The pilot explicitly requested merging the completed Codex change on
26 September 2026. Integration joins main `0c137cf` (including the new manual
and public-repository status) with implementation `d4f0277`, preserving its
planning and spike commits.

Conflicts in README and AGENTS were reconciled by preserving main's manual
structure and public status while retaining Codex support. Under the
write-the-manual skill, the Codex guidance now lives in the subject-owning
installation, configuration, agent, troubleshooting, CLI and status pages.
Codex version/model/effort substitutions derive from source without importing
the runtime. The hub's ordinary executable summary still lists Claude and
OpenCode; the manual accurately distinguishes Codex's qualification on project
opening or runtime-catalogue requests.

Two added documentation tests failed before reconciliation (missing derived
Codex facts/login guidance and obsolete retirement text), then passed. No
runtime behavior was altered while resolving the merge. Compared with
`d4f0277`, the only floor-source differences are main's pre-existing module
docstring edits in `floor/__init__.py` and `floor/mcp_server.py`.

Combined-content validation:

- Full Python discovery: 437 tests in 157.091 seconds, successful with one
  optional development-workspace machinome-installation acceptance skip.
  The previously observed ignored asyncio subprocess-destructor warning
  remains after shutdown.
- Documentation suite: 21 tests passed, including the two red-first additions.
- Frontend TypeScript checks and production build passed; the existing
  large-chunk warning remains.
- Strict nitpicky Sphinx HTML build passed. Changed pages were opened in
  Chromium, derived facts checked in rendered text, and the Codex installation
  screenshot inspected.
- OpenSpec strict validation: all 28 active changes/specifications passed.
- Wheel and sdist built with `python -m build --no-isolation`; the built wheel
  imported the Codex backend and pinned-version declaration outside the checkout.
  No distribution-check script exists in this repository; this is a packaging
  build/import smoke, not an installed-project runtime acceptance test.
- Whitespace and unresolved-conflict checks passed.

The original authenticated and forced-call evidence remains applicable because
the runtime implementation is unchanged. No additional model calls, login
mutation, push, publication, branch deletion or worktree cleanup was performed
for integration. Generated HTML, browser assets and distributions are not staged.
