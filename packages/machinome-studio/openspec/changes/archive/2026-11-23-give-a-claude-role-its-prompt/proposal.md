## Why

A Claude role works without its profile prompt. On 23 November 2026 the
pilot opened the project SO-ARM100 under `openspec-builder`, asked the
agent what the project was, and the agent answered first: "The profile file
is outside the project, so I can't read it with these tools. I'll go on
with the project files."

The Claude backend's session instructions carry the prompt's path and tell
the session to read it. Since the change `scope-claude-tool-permissions`
(22 August 2026, ADR 0026) a Claude role has no built-in tool, and the
floor's file tools refuse every path outside the active project, where the
profile prompts live. So the instruction cannot be followed, and every
Claude role of both shipped profiles runs on the session instructions
alone: its role name, its skill catalogue and the trust framing, with none
of the conduct its prompt states. The baseline already requires the
backend to "deliver the resolved profile prompt" as session-level
instructions; the Codex and OpenCode backends deliver its text.

## What Changes

- The Claude backend puts the text of the agent's profile prompt in the
  session-level instructions, in place of the path and the instruction to
  read it. The instructions no longer name the prompt's path.
- The baseline says what "deliver" means: the prompt's text, never a path
  in its place, and no file read is needed for a role to learn its role.
- Nothing else changes: the tool surface, the project boundary of the file
  tools, the skill catalogue and on-demand skill loading, the profiles and
  their prompts.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `shop-agent-backend`: the requirement "The Claude backend operates Claude
  Code CLI sessions" states that the session-level instructions carry the
  profile prompt's text and that a role is never sent to read a file for
  it, with one scenario added.

## Impact

Studio only (`packages/machinome-studio`). Code: `_role_contract` in
`machinome/studio/backends/claude.py`. Tests: `tests/test_orchestrator.py`
(the role-contract test, which today asserts the path, and a new test over
every agent of both shipped profiles). Records: `CHANGELOG.md`. The
session instructions of a Claude role grow by the prompt's size, at most
14 kB today, passed as one command-line argument. No framework, viewer or
shop-skill change; no profile or prompt is edited.

## Authorization

The pilot was shown the diagnosis and this fix on 23 November 2026 and
answered "go", which authorizes the proposal and its implementation. The
plan was written and reviewed by the repository agent; no person and no
second agent reviewed the finished text. Integration and push remain the
pilot's.
