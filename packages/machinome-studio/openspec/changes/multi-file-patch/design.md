# Design: multi-file patch

## Context

`apply_patch` is one of the scoped tools in `floor/mcp_server.py`. It parses a
unified diff itself rather than shelling out to `git apply` or `patch`, because
every scoped tool must resolve its targets through the shared active-project
containment gate before touching the filesystem. That constraint stays.

Today the parser locates the single `--- ` header, requires exactly one, and
walks the hunks that follow, writing the rebuilt file at the end.

## Decisions

### Two phases, one write

Parse the whole diff into per-file plans, verify each plan against the current
file content, and only then write. The current implementation already defers
its single write to the end of the walk, so the file is untouched on failure;
extending that property across several files is the reason multi-file patching
is safer than several calls rather than merely faster. A partly applied slice
is worse than a rejected one, because the agent cannot tell from the error
which files it now has to undo.

### The diff names its own targets

A unified diff already carries each file's path in its `+++ ` header, so
requiring the caller to repeat it in `path` is redundant and cannot be
satisfied at all for more than one file. `path` becomes optional.

When `path` is supplied it must name the only file in the diff. This keeps
every existing call correct, and keeps the redundant argument meaningful rather
than silently ignored: a `path` that disagrees with the diff is a mistake worth
reporting, not something to resolve by preferring one over the other.

Paths come from the `+++ ` header with a leading `a/` or `b/` prefix stripped,
falling back to the `--- ` header when the target side is `/dev/null`. Each
resolved path goes through the same `_path` containment gate as any other tool
argument, so a diff cannot reach outside the project.

### Creation and deletion

`--- /dev/null` creates a file; `+++ /dev/null` deletes one. This is what `git
diff` already emits for added and removed files, so an agent that produces a
real diff of its intended change gets the right behavior without knowing a
shop-specific convention.

Creation still requires the diff to be internally consistent: a created file
must have no context or removed lines. `write_file` remains the simpler way to
create a file, and its description says so; this exists so that one coherent
multi-file edit does not have to be split across two tools.

### The Codex envelope stays rejected

`*** Begin Patch` is not a wrapper around a unified diff. Its hunks use `@@`
context markers without line numbers and `*** Update File:` headers, so
accepting it means implementing and maintaining a second patch dialect with its
own fuzzy-context matching. The cost is not justified when the failure it
causes is a single rejected call whose error now names the expected format.

## Risks

- A malformed multi-file diff fails as a whole where several single-file calls
  would have landed the good ones. This is intended, but it means the error
  must identify the failing file precisely enough to rebuild the diff.
- Two hunks in one diff touching the same file are applied in order against one
  in-memory copy, so their line numbers must both refer to the original file,
  as unified diff already requires.
