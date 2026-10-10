## Why

One address per name is the split's readiness condition ("The next phase:
the architecture ready for the split", `workflow/ongoing/lean-core.md`): a
name a project imports must have exactly one import path, the module that
defines it, so that cutting a node package moves a module and never a
second spelling. The node package's root, `machinome/node/__init__.py`,
still resolves twenty-one names a second time, lazily, from the modules that
define them (`_EXPORTS`, and `StlRenderStart` eagerly); the plan's counts of
4 October 2026 put 1007 project files on that root spelling and 35 on the
module's. The pilot decided on 5 October 2026 ("Root cleanup decided; the
viewer deferred; 0.8 after the root is clean", same plan): **the node root
exports nothing**; every name is imported from its module and each of the
former root names refuses naming its module, as the moved port names do; the
manual's examples change with the code; the workspace's rewrite tool
rewrites every project repository in one pass before this change lands; and
0.8 is released once the root is clean. The same session's ruling "Every
node type is a package" (4 October 2026) adds `jscad` and `stl` as node
packages with their extras, for symmetry, deferred by `openscad-out` to this
cycle.

## What Changes

- **The node root exports nothing.** `machinome.node` keeps its docstring,
  its namespace-portion path extension, its refusals and its submodule access
  (`from machinome.node import supported`, `machinome.node.step`), and
  resolves no other name. Each of the twenty-one names it resolved at 815ceb9
  (`AssemblyNode`, `declared_children`, `FusionNode`, `CadQueryNode`,
  `Build123dNode`, `Build123dSheetNode`, `SheetLeafNode`, `FlexibleNode`,
  `MolejoNode`, `Solid2Node`, `OpenScadNode`, `JScadNode`, `StlNode`,
  `Marking`, `Wrapped`, `Flat`, `Svg`, `Frame`, `StepNode`,
  `property_as_number`, `StlRenderStart`) raises `ImportError` at
  `from machinome.node import <name>`, whose message names the module that
  defines it and the line to write (design.md, Decision 3, verbatim). The
  node types' names come from the table of supported node types
  (`machinome.node.supported`, its `classes` column); the core's own twelve
  from a table in the root (Decision 2). `__all__` is empty, and the root
  binds no public name but its submodules.
- **The gate, red first and permanent** (`tests/test_node_root_exports_nothing.py`):
  the root resolves none of the twenty-one and refuses each naming its
  module; no file under `machinome/` or `tests/`, and no page under `docs/`
  (decision records excepted) or `README.rst`, spells
  `from machinome.node import <one of them>` or `machinome.node.<one of
  them>`. Red on 815ceb9: 6 core files (8 offences), 291 test files (491),
  20 documentation files (58) (design.md, Context).
- **Every reader repointed:** the two project templates of `machinome new`,
  the source `machinome import-step` generates (composed from the classes'
  own modules), the docstrings that describe the root, the 291 test files (a script in this
  change, `repoint.py`, from this change's `moved-names.toml`) and the
  manual: every example, the API reference's directives (each node type
  documented under its module), the install page, the backends guide's
  node-type table, the upgrading page's mapping, the changelog.
- **`jscad` and `stl` are node packages:** each gains its extra in
  `pyproject.toml`, `machinome[jscad]` and `machinome[stl]`, both empty
  (`JScadNode` runs the `jscad` command, a Node program no pip extra
  installs; `StlNode` reads with trimesh, a required dependency), and `all`
  includes both. Neither module checks a kernel, so neither is refused at
  any door; their rows in the table already exist.
- **BREAKING (framework API):** `from machinome.node import <name>` and
  `machinome.node.<name>` fail for each of the twenty-one names; nothing
  aliases them (ADR-169). `from machinome.node import *` binds nothing. The
  moved-names table `moved-names.toml` lists the twenty-one with their
  modules.
- **BREAKING (generated source):** `machinome new` and `machinome import-step`
  write `from machinome.node.<module> import <name>` lines.
- **Install:** `machinome[jscad]` and `machinome[stl]` are new extras that
  install nothing beyond the package; a manifest naming them keeps working
  when the node packages are cut.

Not in this change: the projects (the workspace's `scripts/rewrite-projects`
rewrites every project repository in one pass, committed on each checked-out
branch, before this change is integrated; Voron-2's `shape()` call sites by
hand in the same pass), the viewer seam (deferred past 0.8; ADR-179's
provisional renderer column ships), any rename the pilot locked, the package
split, the licence, the release. Sibling repositories (the studio's two
skills, machinome-mechanics' tests and examples) are follow-ups recorded in
design.md, Migration Plan.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `node-model`: the node root exports nothing (new requirement: the
  refusals, their texts' form, the empty `__all__`, the submodule access);
  the table of supported node types no longer feeds an export table.
- `cli-startup-cost`: the requirement on the root's lazy exports becomes the
  root resolving no name and importing no backend; a broken or absent
  backend is reported through the module import.
- `kernel-extras`: the `jscad` and `stl` extras, `all`; the project
  templates may name their node type's module; the root reaches the table
  for its refusals.
- `openscad-node`: the node type at its address is the one path; the
  refusal's doors.
- `markings`, `mates`: `Marking`, `Wrapped`, `Flat`, `Svg` and `Frame` are
  imported from their modules only; the mates example imports from the
  modules.
- `ports`: the old-path scenario names only moved names; a node class is
  imported from its module.
- `vet`: the public contract is spelled by module; a former root name is not
  a vet finding.
- `cli`: generated project source imports each name from its module (new
  requirement).
- `user-documentation`: the manual imports every name from its module, the
  API reference documents each under its module, the upgrading page maps the
  twenty-one, the install page and the backends guide list every node type
  with its module and extra (new requirement); the values page's statement
  of where node classes come from.

## Impact

- **Code.** `machinome/node/__init__.py` (rewritten), `machinome/node/supported.py`
  (docstring; a reader of `classes` for the refusal), `pyproject.toml`
  (`jscad`, `stl`, `all`), `machinome/manager/import_step.py`, the two
  templates under `machinome/manager/templates/project/root/`, the
  docstrings of `parameters.py`, `node/adapters/__init__.py` and
  `node/build123d.py`. No core module imports a root
  name in code today (design.md, Context): the code's behaviour changes only
  at the root, the templates and the generator.
- **Tests.** 291 files repointed (101 test modules, 8 helpers, 182 fixture
  files); the tests whose subject is the root revised by hand; new: the
  gate; the leaf-contract golden gains an expected-difference table for the
  source digests its fixtures' repointed import lines move (Decision 9).
- **Projects.** Every project file on the root spelling fails to load until
  the workspace pass rewrites it; the pass runs before integration, so the
  sweep after this change expects no `expected` row. A rewritten part's
  source digest changes, so each rewritten part rebuilds once, to the same
  bytes.
- **Docs.** The 19 manual files with root imports, the API reference,
  `docs/architecture.md`, the changelog's Unreleased section, the campaign
  plan.

Originating evidence: `workflow/ongoing/lean-core.md`, "Root cleanup
decided; the viewer deferred; 0.8 after the root is clean (pilot, 5 October
2026)" (the decisions), "The next phase: the architecture ready for the
split" (this cycle's entry, item 3, and "one address per name", 1007 project
files), "Every node type is a package" and "Locked at the session's close"
(the norm `machinome.node.<x>` / `machinome[<x>]`, `jscad` and `stl` as
packages), and "State of the campaign" (the eighth and ninth cycles'
integration notes); ADR-169 ("It stays as long as `_MOVED` does; the root
cleanup decides both").
