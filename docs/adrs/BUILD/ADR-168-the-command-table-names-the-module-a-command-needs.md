# ADR-168: The Command Table Names the Module a Command Needs

**Status:** Accepted, third column names a node type since 2026-10-04, by [ADR-179](ADR-179-the-core-reaches-a-node-packages-renderer-and-command-through-the-table-of-supported-node-types.md)
**Date:** 2026-10-03
**Change:** [`lean-install`](../../../openspec/changes/archive/2026-10-03-lean-install/)
**Amends:**
- [ADR-024: Command-First CLI Grammar and Duck-Typed Command Registry](./ADR-024-command-first-cli-grammar-and-duck-typed-command-registry.md) — the registry gains a third column
- [ADR-059: Import at the Point of Use](./ADR-059-import-at-the-point-of-use.md) — dispatching a command imports the module it needs before the command, and answers an absent extra by name

**Related to:**
- [NODE/ADR-167: A kernel is an extra, and its module refuses its absence at import](../NODE/ADR-167-a-kernel-is-an-extra-and-its-module-refuses-its-absence-at-import.md) — the refusal this table answers by
- [NODE/ADR-162: A resolved provider declares the contract version it implements](../NODE/ADR-162-a-resolved-provider-declares-the-contract-version-it-implements.md) — the pattern `import-step` follows when its implementation moves

## Context and Problem Statement

`machinome import-step` reads a STEP document with `StepAssembly`, which
lives in `machinome.node.step` and needs the `step` extra once the kernels
are extras (ADR-167). Its implementation reached the reader through a lazy
import whose `ImportError` handler printed `install it with 'pip install
cadquery'`, an install line that no longer provides the reader. The plan's
D3 settled that a command whose implementation moves with a package is
resolved by a command table naming the module and the extra, with no
entry-point group; in this layer the implementation stays in
`machinome.manager`.

## Decision Drivers

- The command stays registered and listed with or without its extra, and is
  never reported as an unknown command.
- Without the extra the CLI answers with the line that installs it, writes
  nothing, prints no traceback, and exits 1, for the command and for its
  `-h` alike.
- `machinome -h` costs what it costs now: it imports no STEP reader.
- The extra is stated once, by the module that needs it.
- A broken install still reports its own import error.

## Considered Options

1. **A third column naming the module; the extra from its refusal** (chosen)
2. Import `machinome.node.step` at the top of `manager/import_step.py` and
   catch the refusal from `resolve_command`
3. A column naming the extra
4. An entry-point group

## Decision Outcome

`COMMANDS` values are `(module, class_name, needs)`; `needs` is
`'machinome.node.step'` for `import-step` and `None` for every other
command. Once `manage()` knows the selected command, and before it resolves
the command's class, it imports `needs`; on `ExtraUnavailable` it writes

```
Error: machinome import-step needs the step extra: machinome.node.step (StepNode, StepAssembly) needs cadquery, which is not installed; install it with 'pip install "machinome[step]"'
```

and exits 1. Any other import error propagates, as `resolve_command`
requires of a broken install. The help path resolves classes as before and
imports no `needs` module. `manager/import_step.py` imports `StepAssembly`
inside `handle()`; its own kernel refusal is removed.

### Why not option 2

The help path would import CadQuery and OCP (about 1.5 s) and need its own
refusal handling to list the command.

### Why not options 3 and 4

A column naming the extra is a second copy of what the module declares; an
entry-point group was rejected by D2.

## Consequences

- `machinome -h` lists `import-step` where it cannot run; invoking it
  answers with the install line.
- Every reader of `COMMANDS` unpacks three columns.
- No contract version for this seam yet: the CLI resolves no implementation
  from `machinome.node.step`, only its presence. When the command's
  implementation moves into the satellite, the entry becomes that module
  and ADR-162's pattern applies.

## References

- `machinome/cli.py` (`COMMANDS`, `require_needed_module`, `manage`),
  `machinome/manager/import_step.py`
- `tests/test_cli_lazy_imports.py`, `tests/test_import_step.py`
- `openspec/specs/cli/spec.md` ("Import-step command", "A command that needs
  an extra is answered by the extra")
