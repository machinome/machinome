## Why

The guitar project's machinist recorded repeated patching failures in
`docs/warts.md`. Most were missing documentation and have been corrected
directly, but one is a real limitation of the tool: `apply_patch` rejects a
diff containing more than one file header, so it changes exactly one file per
call.

A released increment is normally implemented across an implementation file and
its tests together. Splitting that into one call per file makes each later call
patch a tree that earlier calls already moved, and the machinist reported
exactly that failure mode: patches whose context no longer matched. It also
leaves a partly applied slice on disk whenever a later file fails, with no
single operation that either lands the whole coherent edit or lands none of it.

## What Changes

- `apply_patch` accepts a unified diff describing one or more files and applies
  the whole diff as a single operation.
- The diff itself names each file it changes, so `path` becomes optional. When
  `path` is supplied the diff must describe that one file, which keeps every
  existing single-file call working unchanged.
- Every file in the diff is verified against its current content before
  anything is written. If any file fails to verify, no file is modified and the
  error names the file, hunk, and line that did not match.
- A diff may create a file (`--- /dev/null`) or delete one (`+++ /dev/null`),
  so one coherent edit can add, change, and remove files together.
- The result reports each file the call changed, created, or deleted.
- The Codex `*** Begin Patch` envelope remains unsupported. Its hunk body is a
  different format rather than a wrapper around a unified diff, so accepting it
  would mean maintaining a second patch dialect. `apply_patch` continues to
  reject it with an error naming the format it does expect.

## Capabilities

### Modified Capabilities
- `scoped-agent-tools`: `apply_patch` applies a multi-file unified diff
  atomically, derives its targets from the diff, and supports file creation and
  deletion within one patch.

## Impact

- `floor/mcp_server.py` gains a two-phase patch implementation: parse and
  verify every file, then write.
- The `apply_patch` tool description and parameter schema change, which is what
  runtime agents actually read; `path` moves out of the required list.
- Existing single-file callers and the current tool tests are unaffected in
  behavior.
- No architecture boundary changes: the tool keeps the same project containment
  gate and remains the only patch surface exposed to runtime agents. No ADR is
  required.
