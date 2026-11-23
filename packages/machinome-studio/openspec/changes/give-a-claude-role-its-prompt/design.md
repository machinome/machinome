## Context

`ClaudeBackend._role_contract` builds the text passed to
`claude --append-system-prompt`. One of its lines is "Before taking any
task action, read the following profile prompt in full and follow it as
authoritative: <path>". That line was written when a Claude role held the
built-in `Read` tool (ADR 0015 describes a Foreman reading its prompt with
it). ADR 0026 emptied the built-in tool set (`--tools ""`) and left the
floor's tools as the session's whole authority; those resolve every path
inside the active project and refuse the rest
(`path resolves outside active project`). The prompt files are in the
studio's package, outside every project. No test noticed: the role-contract
test asserts that the path is in the instructions.

The Codex backend builds its instructions with "The following profile
prompt is authoritative:" followed by `prompt_path.read_text()`; the
OpenCode backend embeds the same text in its system contract.

## Goals / Non-Goals

**Goals:**

- A Claude role holds its profile prompt from its first turn, with no tool
  call.

**Non-Goals:**

- Any change to the file tools' project boundary or to the tool surface.
- Any change to skill delivery, which stays a catalogue plus `load_skill`.
- The "Shop checkout:" line of the session instructions, which also names a
  path outside the project. Foreman's prompt refers to it; it is left as it
  is.
- Editing a prompt, or stripping its frontmatter before delivery.

## Decisions

**The prompt's text goes into the session instructions.** `_role_contract`
replaces the read instruction with the line the Codex backend uses, "The
following profile prompt is authoritative:", followed by the file's text
as it is, frontmatter included, as the other two backends deliver it. The
prompt's path is not named: a path the session cannot open is only an
invitation to try.

Alternatives considered:

- *Let the floor's `read_file` reach the profile directory.* It widens the
  one boundary the file tools have, for a single file per session, and the
  role still works without its prompt whenever the model does not make the
  call.
- *A floor tool that returns the session's prompt*, as `load_skill` returns
  a skill. Skills are loaded on demand because they are large and optional;
  the prompt is neither, and the same dependence on the model's first call
  remains.
- *`--append-system-prompt-file`.* The CLI has it, but the instructions are
  composed of several parts and would need a temporary file per role, for
  no gain: the largest prompt is 14 kB and Linux allows 128 kB for one
  argument.

## Risks / Trade-offs

- [A prompt above the single-argument limit would fail to start the
  session] → none is near it; the failure would be immediate and named by
  the operating system, not silent.
- [Roles change behaviour] → they begin to follow prompts they were always
  meant to follow. Sessions opened before the change keep their old
  instructions until they are reopened.
