## Why

A leaf whose declared source file is not there builds most of the way and then
fails with a `FileNotFoundError` that names a path and nothing else — not the
node, not the class, not the attribute that declared it.

`projects/Actuators/Internal-Cycloidal-Actuator` met it and paid for it
(`workflow/warts.md`, "# Internal-Cycloidal-Actuator (2026-09-06, STEP import
cycles)", second bullet):

> Finding, not filed as a cycle: a `StepNode` whose `step_source` is absent
> constructs fine and fails later inside `mtime_ns` with a bare
> `FileNotFoundError` naming only the path. The actuator project calls its
> own `source.require()` at import to keep the extract command in the
> failure. A leaf that validated its declared file at construction, naming
> the class and the path, would be the better failure; `StlNode` has the same
> gap.

That project's `simulation/actuator/parts.py` — a file `solid import-step`
generated — carries a hand-written preamble whose only job is to replace the
framework's failure with a usable one:

```python
# The leaf's own missing-file failure is a bare FileNotFoundError naming
# only the path; "the vendor STEP file is obtained, never faked" is
# unchanged by the move to generated source, so this generated module
# still calls source.require() at import to keep the failure naming the
# extract command.
require()
```

Reproduced on this worktree (`evidence.md`, every line from a probe that was
actually run):

- `MissingStl()`, `MissingStep()` and `MissingJscad()` all **construct
  successfully** with no file on disk; the failure arrives later, from
  `base.py:1039`'s `os.stat`, as
  `FileNotFoundError: [Errno 2] No such file or directory: '…/absent.stl'`.
- Through the CLI the message the maker sees is
  `parts:MissingStl: failed to inspect initial sources project: [Errno 2] No
  such file or directory: '…/absent.stl'` — it names the MODEL reference, not
  the node; and for a leaf placed inside an assembly,
  `assembly:Rig: failed to assemble project: [Errno 2] …` names only the root.
- `OpenScadNode` fails at construction already, but with the same bare
  `FileNotFoundError` from its `coherent_read`.
- A declared source that exists **but is a directory** is not caught at all:
  `mtime_ns` answers happily (`os.stat` succeeds on a directory), and the
  build dies deep inside a foreign library — trimesh's
  `string is not a file: …/a_directory` for STL, and for STEP an OCCT
  `Standard_Failure: input in flex scanner failed` dumped in red to the
  terminal before the framework's own reader-status message.

The framework already refuses a leaf that declares no source file at all,
at construction, naming the class (`stl.py:161-165`, `step.py:475-479`,
`jscad.py:28-30`). Declaring a file that is not there is the same kind of
mistake, made one step later, and it deserves the same kind of failure.

## What Changes

- A source-bound leaf — `StlNode`, `StepNode`, `JScadNode`, `OpenScadNode` —
  whose declared source file does not exist SHALL fail **when the node is
  constructed**, with an error naming the class, the declaring attribute and
  its declared value, and the absolute path the framework resolved it to.
- The same failure SHALL name the case where the resolved path exists but is
  not a regular file, saying so, instead of handing a directory to trimesh or
  to the STEP reader.
- Nothing else changes about when a leaf is checked. A source file removed
  *after* the node was constructed still raises `FileNotFoundError` out of
  `mtime_ns`, which is the ratified answer for a build whose sources move
  underneath it (`tests/test_content_verified_currency.py:431-447`); this
  change adds a check at construction, it does not move that one.
- Scaffolding is untouched: `solid new` writes a `Solid2Node`
  (`solid_node/manager/templates/project/root/__init__.py:1-4`) and
  `solid import-step` reads the document and writes source text without ever
  constructing a `StepNode` (`solid_node/manager/import_step.py`), so neither
  can trip the new check.
- **Out of scope**, recorded so it is not read into this change:
  - `OpenScadNode` has no "you declared no `scad_source`" failure at all —
    it raises `TypeError: join() argument must be str, bytes, or
    os.PathLike object, not 'NoneType'` (probed; `openscad.py:40`), where
    every other source-bound adapter raises a message naming the class. A
    separate correction.
  - The builder's wrapper text `failed to inspect initial sources project`
    (`builder.py:358`) reads as broken English and names the model where it
    could name the node. Untouched here.

## Impact

- Affected specs: `stl-import` (MODIFIED "STL source declaration and
  freshness"), `step-import` (MODIFIED "STEP source declaration and
  freshness"), `node-model` (ADDED "A source-bound leaf names its missing
  file").
- Affected code: `solid_node/node/sources.py` (one new helper),
  `solid_node/node/adapters/stl.py`, `.../step.py`, `.../jscad.py`,
  `.../openscad.py` (one call each), `docs/leaf-nodes.rst`.
- Affected projects: `Internal-Cycloidal-Actuator`'s `source.require()`
  preamble becomes optional — it still adds the extract command, which the
  framework cannot know, so this change does not delete it and nothing in
  that project must move.
- No ADR is proposed; see `design.md`, "Why this is not an ADR".
