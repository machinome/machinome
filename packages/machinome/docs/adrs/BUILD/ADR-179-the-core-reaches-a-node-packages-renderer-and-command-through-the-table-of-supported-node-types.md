# ADR-179: The Core Reaches a Node Package's Renderer and Command Through the Table of Supported Node Types

**Status:** Accepted (provisional: its renderer column is removed by the viewer cycle); the `classes` column's readers amended 2026-10-05 by [NODE/ADR-181](../NODE/ADR-181-the-node-packages-root-exports-nothing.md)
**Date:** 2026-10-04
**Change:** [`openscad-out`](../../../openspec/changes/archive/2026-10-04-openscad-out/)
**Amends:**
- [ADR-168: The command table names the module a command needs](ADR-168-the-command-table-names-the-module-a-command-needs.md) — the third column names a node type, loaded through the table
- [NODE/ADR-167: A kernel is an extra, and its module refuses its absence at import](../NODE/ADR-167-a-kernel-is-an-extra-and-its-module-refuses-its-absence-at-import.md) — the one table of node types its "no table maps a module to its extra" admits, by ruling
**Related to:**
- [NODE/ADR-177: The OpenSCAD family is a node package, and the core names no technology](../NODE/ADR-177-the-openscad-family-is-a-node-package-and-the-core-names-no-technology.md)
- [ADR-103: The browser is the only interactive development viewer](ADR-103-the-browser-is-the-only-interactive-development-viewer.md)

## Context and Problem Statement

With the OpenSCAD family a node package (ADR-177), three readers in the core
still had to reach a node type by name: the node root's export table, the
`import-step` command (`machinome.node.step`) and the snapshot command's
OpenSCAD renderer. The pilot's ruling of 4 October 2026 allows the core to
mention a technology "nowhere but in a table of supported node types", and
reserves the renderer architecture — a contract, discovery — for a later
revisit; later the same day the pilot decided that viewers become providers
behind a seam `machinome.viewer` in the phase's last cycle.

## Considered Options

1. **A second table, `machinome.node.supported`, read by the node root, the
   CLI, the snapshot command and `machinome new`** (chosen)
2. Extend `cli.COMMANDS` (ADR-168) with renderers
3. Discover renderers and commands from installed portions through entry points

## Decision Outcome

`machinome/node/supported.py` holds only `NodeType(classes, renderers=(),
commands=())`, `NODE_TYPES` (eight rows: `cadquery`, `build123d`, `step`,
`molejo`, `solid2`, `openscad`, `jscad`, `stl`), `DEFAULT_RENDERER =
'openscad'` and three readers. A node type's address and extra are its key
(`machinome.node.<key>`, `machinome[<key>]`). `load(key)` imports the module,
passing its own `ExtraUnavailable` unmodified and refusing a module that
cannot be found the same way (`the <key> node type (<classes>) needs
machinome.node.<key> ...`); `renderer(name)` loads the contributing node type
and instantiates the renderer of the provisional column; `needed_by(command)`
names the node type a command needs. Importing the module imports no node
type.

- The node root's export table takes each node type's class names from
  `NODE_TYPES`: the same names resolve to the same objects.
- `COMMANDS['import-step'][2]` is `'step'`; `require_needed_module` loads it
  through the table, its message unchanged; `import_step` takes
  `StepAssembly` from `supported.load('step')`.
- `machinome snapshot --renderer` offers `web` and the table's renderer
  names, defaults to `DEFAULT_RENDERER`, resolves a table renderer before
  loading the node and answers an absent one with "machinome snapshot
  --renderer <name> needs the <extra> extra: ...; or use --renderer web", exit
  1. The renderer's `present(node)` runs in the build lock (it assembles and
  writes the root's presentation) and `render(node, args, output, runner)`
  after it, reporting its own failures. The web renderer composes no
  presentation.
- `machinome new` scaffolds the first of `solid2`, `cadquery` the table loads,
  and refuses naming both extras with neither.

What the renderers' lack of a contract looks like, recorded for the pilot's
revisit: the OpenSCAD renderer answers `present` and `render` (`withdraw` and
`draw` are its own); the web renderer answers `render` and `capture`; the
snapshot command still compares the string `'web'`, owns options only the
OpenSCAD renderer reads, and imports `BrowserRenderer` by name. No version is
checked on a renderer, no entry point or portion is discovered, no protocol
class exists.

## Rejected Options

- **2:** `COMMANDS` is keyed by command and read by the CLI only; a renderer
  is chosen after dispatch, and the whole CLI would become a module naming the
  technology.
- **3:** the pilot's later decision, with the renderer contract.

## Consequences

- A ninth node type is a row; a renderer or command a package contributes is
  a row. The table is a closed list in the core — the bend of Open/closed the
  pilot's ruling accepts, provisional until the renderer revisit.
- The viewer cycle replaces the renderer column with the seam
  `machinome.viewer` and moves `machinome/viewers/openscad.py` behind it.

## References

- [`openscad-out` change](../../../openspec/changes/archive/2026-10-04-openscad-out/): design Decision 6, the `cli` and `kernel-extras` deltas

## Amendment (2026-10-05)

[NODE/ADR-181](../NODE/ADR-181-the-node-packages-root-exports-nothing.md) leaves the node root no export
table. The `classes` column names the classes each node type's module defines
for a project to import; its readers are the root's refusal, which refuses
each of them naming `machinome.node.<key>`, and `load`'s message for a node
type that is not installed. The table's other readers are unchanged, and
`machinome import-step` reads it to load the `step` node type.
