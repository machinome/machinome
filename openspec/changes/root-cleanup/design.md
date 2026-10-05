## Context

The tenth cycle of the lean-core campaign's layer 1 and the last before 0.8
(`workflow/ongoing/lean-core.md`, "The next phase: the architecture ready for
the split", item 3, and "Root cleanup decided; the viewer deferred; 0.8 after
the root is clean (pilot, 5 October 2026)"), cut from the line `v0.8-split` at
815ceb9 ("Merge branch 'v0.8-split-brep-mesh' into v0.8-split") on the bench
`machinome/WTs/v0.8-split-root-cleanup`. The pilot's three decisions of
5 October bind it: the node root exports nothing and each former root name
refuses with its module's address, as the moved port names do, the manual's
examples changing with the code; the workspace's rewrite tool rewrites every
project repository in one pass (Voron-2's `shape()` call sites by hand inside
it); and each repository is rewritten and committed on its checked-out branch.
The viewer cycle is deferred past 0.8, so ADR-179's provisional renderer column
ships. The ruling "Every node type is a package" (4 October 2026) adds `jscad`
and `stl` as node packages with their extras; `openscad-out` deferred them to
this cycle ("jscad and stl as packages go with the root cleanup").

Precedents, all under `openspec/changes/archive/`: `2026-10-03-lean-install`
(ADR-167: an extra is named by the last component of the module that needs it,
three doors; ADR-168: the command table; ADR-169: a leaf type is one module
under `machinome.node`, the adapters package kept only to refuse, "it stays as
long as `_MOVED` does; the root cleanup decides both"), `2026-10-03-backend-switch`
(ADR-166: no class-name recognition), `2026-10-04-openscad-out` (ADR-177, 179:
the table `machinome.node.supported`, whose `classes` column the root's
`_EXPORTS` reads today; the token gate that admits the word `scad` only in the
family's modules and the table) and `2026-10-05-brep-mesh` (ADR-180: the names
this cycle's docs and tests use; the moved-names format; the scenario-title
table). ADR-087 moved the ports out of the node package and is why `_MOVED`
exists.

Facts below were read on the bench at 815ceb9 unless marked *inferred*. The
scans are this change's `gate-prototype.py` (the gate's text rule) and
`repoint.py` (the repointing, dry run), both run with the workspace venv's
Python 3.12.3; nothing of the framework was imported by them, and no `pytest`
or `machinome` command ran.

### What the root does today

`machinome/node/__init__.py` (198 lines):

| line | what |
|---|---|
| 62 | `__path__ = _namespace_portions(__path__, __name__)`: node packages cut later resolve as portions (ADR-169) |
| 64 | `from .base import StlRenderStart`: eager, importing `base` and through it `declarative`, `frames`, `markings`, `phase`, `presentation`, `sources` |
| 65 | `from .supported import NODE_TYPES`: binds `NODE_TYPES` in the root, so `from machinome.node import NODE_TYPES` works |
| 73-87 | `_EXPORTS`: eleven core names (`AssemblyNode`, `declared_children`, `FusionNode`, `SheetLeafNode`, `FlexibleNode`, `Marking`, `Wrapped`, `Flat`, `Svg`, `Frame`, `property_as_number`) and the nine class names of the table's `classes` column, resolved lazily |
| 94-103 | `_MOVED`: the six port and time-base names and the two removed submodules, refused with `ImportError` naming `machinome.motion.ports` |
| 105 | `__all__ = ['StlRenderStart', *_EXPORTS]`: 21 names |
| 108-153 | `_load` (re-raises `ExtraUnavailable` unmodified, splices "raised resolving ..." into any other `ImportError`) and `_submodule` (attribute access to a submodule) |
| 156-194 | `__getattr__`: `_MOVED`, then `_EXPORTS`, then a submodule, else `AttributeError` |

Probe (`import machinome.node` in a fresh interpreter): the public names of its
namespace are `ExtraUnavailable`, `NODE_TYPES`, `StlRenderStart`, `find_spec`,
`import_module` and the submodules `base`, `declarative`, `frames`, `markings`,
`phase`, `presentation`, `sources`, `supported`; so the root answers five names
that are not submodules besides its 21 exports, `from machinome.node import
import_module` included.

### Who reads the root

- **No core module imports a root name in code.** `grep -rn "from
  machinome.node import" machinome/` finds module imports only (`supported` in
  `cli.py:107`, `manager/new.py:13`, `manager/snapshot.py:12`,
  `manager/import_step.py:430`; `phase` in `model.py:355` and
  `motion/joints.py:638`), which stay. The other hits are text: the docstrings
  of `parameters.py:15` (an example import block), `node/adapters/__init__.py:18`
  ("the root spellings ... are unchanged") and the root's own (`:122`); the two
  lines `machinome import-step` writes into a project (`manager/import_step.py:175`,
  `:365`); and the two templates `machinome new` copies
  (`manager/templates/project/root/cadquery.py:3`, `solid2.py:1`). No module
  under `machinome/` reads `machinome.node.__all__` or a root attribute by name.
  The code's behaviour therefore changes only at the root, the templates and the
  generator.
- **The tests**: 291 files spell a root name (101 test modules, 8 helpers such
  as `brep_engine_golden.py`, 182 files of fixture projects such as
  `tests/meta_project/`, 53 files, and `tests/vet_projects/`, 41); 410 of their
  491 offences are import statements, 81 are fixture sources inside strings or a
  dotted address (`tests/test_node_lazy_exports.py`'s `'machinome.node.StepNode'`).
  The tests whose subject is the root itself are listed in Decision 8.
- **The manual**: 19 files import a root name (13 pages and the tutorial's
  seven modules), and `docs/reference/api.rst` documents twelve classes by their
  root address (`.. autoclass:: machinome.node.Solid2Node`, lines 404-581),
  which Sphinx imports and which the CI docs job builds with warnings as errors.
  Four prose sentences say where node classes come from (`api.rst:174`, `:652`,
  `concepts/values.rst:54`, `tutorial/03-dimensions.rst:24`). Two decision
  records (ADR-167, ADR-169) spell the root and keep it (historical entries
  retain the names they used).
- **Sibling repositories** (read, not edited): machinome-studio's
  `shop-skills/machinome-api/SKILL.md` (six lines) and `shop-skills/machinome/SKILL.md`
  (one) teach the root spelling; machinome-mechanics has four files on it (two
  tests, two documentation examples); machinome-viewer and molejo none.

### The counts, against the plan's

| zone | files | offences | the plan's count (5 October) |
|---|---|---|---|
| `machinome/` | 6 | 8 | 14 core modules |
| `tests/` | 291 | 491 | 292 files |
| `docs/` (without `docs/adrs/`) and `README.rst` | 20 | 58 | 21 files |

The differences come from what is counted. The gate counts the 21 names only,
wherever a reader runs them: in code, in a fixture's string, on a page, and as a
dotted address. On 815ceb9, `grep -rl "from machinome.node import"` finds 11
files under `machinome/` (module imports of `supported` and `phase` included,
which stay), 301 under `tests/` (279 with the statement at column 0, the
briefing's grep) and 21 under `docs/` and `README.rst` (the two ADRs included,
`api.rst`'s directives missed); the plan's 14 and 292 cannot be reproduced on
this head and were *inferred* to be greps of that kind on an earlier one. The
runtime half of the gate is red too: the root resolves all 21 names, `__all__`
lists 21, and five non-submodule names are public.

### Two facts that shape the design

- **The `openscad-out` gate forbids the root to spell a node type's class.**
  `tests/test_core_names_no_scad.py` admits the letters `scad` only in
  `machinome/node/openscad/`, `node/solid2.py`, `viewers/openscad.py` and
  `node/supported.py`; `OpenScadNode` in a root table would be an offence. The
  root must read the node types' names from the table, as `_EXPORTS` does today.
- **A fixture's import line is part of its source digest.** `currency.source_digest`
  digests every tracked source's bytes (`_scoped_digest` removes only sibling
  node classes, never module-level lines, `currency.py:194-224`), and
  `tests/leaf_contract_golden.py` records each artifact's source-record `digest`
  (`_record`, `:82-92`). All seven of its fixtures live in packages that import
  from the root (`leaf_contract_project/parts.py:9`, `markings_project/`,
  `sheet_project/`, `flexible_project/`), so repointing them moves every
  recorded `digest` and no artifact byte (Decision 9). The same holds for every
  project file the workspace pass rewrites: its parts rebuild once, to the same
  bytes.

## Goals / Non-Goals

**Goals:**

- The node root resolves no name of its own: each of the 21 former root names
  refuses naming its module; `__all__` is empty; the namespace binds no public
  name but submodules.
- One permanent gate, red first, holding that state in the code, the tests and
  the manual.
- Every reader in the framework repointed: the templates, the import-step
  generator, the docstrings, the suite, the manual; the API reference documenting
  each class under its module.
- `jscad` and `stl` are node packages in layer 1's sense: each has its extra,
  listed in `all`; the manual lists all eight node types with their extras.
- Behaviour, artifacts and verdicts unchanged: the classes are the same objects
  at the same modules; only spellings, a refusal and two extras change.

**Non-Goals:**

- The projects (the workspace's `scripts/rewrite-projects`, run by the
  orchestrator over every project repository before integration), the
  workspace's tables, and the sibling repositories (Migration Plan).
- The viewer seam and ADR-179's renderer column; the package split; the
  licence; the release; any rename of the pilot's lock.
- Discovery of node packages from installed portions; a contract version on
  the table.
- The `_MOVED` refusals and the dissolved `machinome.node.adapters` package
  stay as they are (Decision 4).

## Decisions

### 1. The root exports nothing: what it keeps and what it loses

`machinome/node/__init__.py` keeps: its docstring (rewritten to say what the
root is: a package path, a refusal and submodule access, and why it exports
nothing); its path extension (`_namespace_portions`); `_MOVED` and its
refusal; `_submodule` and `_load`, so `machinome.node.step` and `from
machinome.node import step` keep resolving a submodule and keep carrying an
absent extra's refusal unmodified and a broken install's import error spliced
with the requested name; `__getattr__` and `__dir__`; the dunder metadata.

It loses: `_EXPORTS`; the eager `from .base import StlRenderStart` (so
`import machinome.node` no longer imports `base` and its six submodules; it
imports what the refusal needs, `machinome.extras` and, on the first refused
name, `supported`); the binding of `NODE_TYPES`; the public bindings of
`import_module`, `find_spec` and `ExtraUnavailable` (bound under private
names). `__all__ = []`.

"Exports nothing" is read strictly: a name the root's namespace binds is a name
`from machinome.node import <name>` resolves, so `NODE_TYPES` and
`import_module` are second paths to the table's and importlib's names, against
the one-path rule as much as `AssemblyNode` is. The gate checks the namespace
(Decision 6) so the rule cannot be re-broken by an unprivate helper. Open
Question 1 asks the pilot to confirm the strict reading.

`__getattr__(name)` order: `_MOVED` (unchanged), then the former root names
(Decision 2), then a submodule, else `AttributeError`.

*Alternatives.* Keep `_EXPORTS` with a `DeprecationWarning`: rejected by the
pilot ("no alias, no deprecation path", ADR-169). Delete `__init__.py`'s logic
and let Python answer `cannot import name`: Python's message names no module,
against the rule for moved names (`_MOVED`, the adapters package), and the
sweep's explanation would lose its row (Decision 3).

### 2. Where the 21 names come from: the table for the node types, the root for the core's twelve

The refusal needs one thing per name, the module that defines it. Two sources
serve it:

- the nine class names of the table of supported node types, read from
  `machinome.node.supported.NODE_TYPES` (`{name: key for key, row in
  NODE_TYPES.items() for name in row.classes}`), each refused naming
  `machinome.node.<key>`, the address the table's docstring already states is a
  node type's name;
- the core's own twelve, in a table of the root, `_DEFINED_IN` (*name provisional*):
  `AssemblyNode: assembly`, `declared_children: declarative`, `FusionNode:
  fusion`, `SheetLeafNode: sheet_leaf`, `FlexibleNode: flexible`, `Marking`,
  `Wrapped`, `Flat`, `Svg: markings`, `Frame: frames`, `property_as_number:
  decorators`, `StlRenderStart: base`.

One table in `supported.py` serving both was examined and rejected, on
evidence:

1. The `openscad-out` gate admits `scad` in `supported.py` and not in the root,
   so the node types' names cannot move into the root's table; the root must
   derive them, whichever file holds the core's twelve.
2. `supported.py`'s responsibility is the node types the core supports: its
   readers are the CLI's command table, the snapshot command's renderers,
   `machinome new`'s templates and `load`'s refusal; its rows are keyed by a
   technology and carry an extra. `AssemblyNode` or `Frame` is not a node type,
   has no extra and no command; a row for it, or a second dict beside
   `NODE_TYPES`, would give the table a reader (the root's refusal) and a kind
   of name it does not otherwise have, and every other reader would skip it.
3. The core's twelve are closed history: the names the root resolved until this
   change. No future core name joins them (a new name is never a root export),
   so their table never changes and lives with the only code that reads it.
   The node types' half is live: a row added for a new node type gives its
   classes a refusal pointing at their module with no edit to the root, which
   is the same open-closed property `_EXPORTS` had.

The lookup is a mapping read with `.get(name)`, never a comparison with a
string literal, so `tests/test_no_class_name_recognition.py`'s scan (an
`ast.Compare` holding a string that spells a core class) stays without an
exception; and it decides nothing but the words of an error. ADR-181 records
that reading of ADR-166: a table keyed by the names a caller asks for, used only
to word a refusal, is not recognition of a node type.

### 3. The refusal, verbatim

`ImportError`, for the reason `_MOVED`'s comment gives (CPython's `from X
import Y` discards an `AttributeError`'s message from a module `__getattr__`),
raised for `from machinome.node import <name>`, for `getattr(machinome.node,
<name>)` and therefore for `hasattr`. Its message begins with Python's own
attribute sentence, `module 'machinome.node' has no attribute '<name>'`, which
`scripts/load-projects` already reads as the dotted name `machinome.node.<name>`
(its `COMPOSED` patterns), so a project load failing on the root is explained by
the row of `moved-names.toml` with that name. The texts, one per name:

```
module 'machinome.node' has no attribute 'AssemblyNode': the root of machinome.node exports nothing, and 'AssemblyNode' is imported from its module, 'machinome.node.assembly'. Write `from machinome.node.assembly import AssemblyNode`.
module 'machinome.node' has no attribute 'declared_children': the root of machinome.node exports nothing, and 'declared_children' is imported from its module, 'machinome.node.declarative'. Write `from machinome.node.declarative import declared_children`.
module 'machinome.node' has no attribute 'FusionNode': the root of machinome.node exports nothing, and 'FusionNode' is imported from its module, 'machinome.node.fusion'. Write `from machinome.node.fusion import FusionNode`.
module 'machinome.node' has no attribute 'CadQueryNode': the root of machinome.node exports nothing, and 'CadQueryNode' is imported from its module, 'machinome.node.cadquery'. Write `from machinome.node.cadquery import CadQueryNode`.
module 'machinome.node' has no attribute 'Build123dNode': the root of machinome.node exports nothing, and 'Build123dNode' is imported from its module, 'machinome.node.build123d'. Write `from machinome.node.build123d import Build123dNode`.
module 'machinome.node' has no attribute 'Build123dSheetNode': the root of machinome.node exports nothing, and 'Build123dSheetNode' is imported from its module, 'machinome.node.build123d'. Write `from machinome.node.build123d import Build123dSheetNode`.
module 'machinome.node' has no attribute 'SheetLeafNode': the root of machinome.node exports nothing, and 'SheetLeafNode' is imported from its module, 'machinome.node.sheet_leaf'. Write `from machinome.node.sheet_leaf import SheetLeafNode`.
module 'machinome.node' has no attribute 'FlexibleNode': the root of machinome.node exports nothing, and 'FlexibleNode' is imported from its module, 'machinome.node.flexible'. Write `from machinome.node.flexible import FlexibleNode`.
module 'machinome.node' has no attribute 'MolejoNode': the root of machinome.node exports nothing, and 'MolejoNode' is imported from its module, 'machinome.node.molejo'. Write `from machinome.node.molejo import MolejoNode`.
module 'machinome.node' has no attribute 'Solid2Node': the root of machinome.node exports nothing, and 'Solid2Node' is imported from its module, 'machinome.node.solid2'. Write `from machinome.node.solid2 import Solid2Node`.
module 'machinome.node' has no attribute 'OpenScadNode': the root of machinome.node exports nothing, and 'OpenScadNode' is imported from its module, 'machinome.node.openscad'. Write `from machinome.node.openscad import OpenScadNode`.
module 'machinome.node' has no attribute 'JScadNode': the root of machinome.node exports nothing, and 'JScadNode' is imported from its module, 'machinome.node.jscad'. Write `from machinome.node.jscad import JScadNode`.
module 'machinome.node' has no attribute 'StlNode': the root of machinome.node exports nothing, and 'StlNode' is imported from its module, 'machinome.node.stl'. Write `from machinome.node.stl import StlNode`.
module 'machinome.node' has no attribute 'Marking': the root of machinome.node exports nothing, and 'Marking' is imported from its module, 'machinome.node.markings'. Write `from machinome.node.markings import Marking`.
module 'machinome.node' has no attribute 'Wrapped': the root of machinome.node exports nothing, and 'Wrapped' is imported from its module, 'machinome.node.markings'. Write `from machinome.node.markings import Wrapped`.
module 'machinome.node' has no attribute 'Flat': the root of machinome.node exports nothing, and 'Flat' is imported from its module, 'machinome.node.markings'. Write `from machinome.node.markings import Flat`.
module 'machinome.node' has no attribute 'Svg': the root of machinome.node exports nothing, and 'Svg' is imported from its module, 'machinome.node.markings'. Write `from machinome.node.markings import Svg`.
module 'machinome.node' has no attribute 'Frame': the root of machinome.node exports nothing, and 'Frame' is imported from its module, 'machinome.node.frames'. Write `from machinome.node.frames import Frame`.
module 'machinome.node' has no attribute 'StepNode': the root of machinome.node exports nothing, and 'StepNode' is imported from its module, 'machinome.node.step'. Write `from machinome.node.step import StepNode`.
module 'machinome.node' has no attribute 'property_as_number': the root of machinome.node exports nothing, and 'property_as_number' is imported from its module, 'machinome.node.decorators'. Write `from machinome.node.decorators import property_as_number`.
module 'machinome.node' has no attribute 'StlRenderStart': the root of machinome.node exports nothing, and 'StlRenderStart' is imported from its module, 'machinome.node.base'. Write `from machinome.node.base import StlRenderStart`.
```

The form, as an f-string:

```python
(f"module {__name__!r} has no attribute {name!r}: the root of "
 f"machinome.node exports nothing, and {name!r} is imported from its "
 f"module, {module!r}. Write `from {module} import {name}`.")
```

The node types' sentences are composed at run time from the table's key, so no
token of the root spells `OpenScadNode` or `openscad`.

The table of names and modules:

| # | name | module | source of the row |
|---|---|---|---|
| 1 | `AssemblyNode` | `machinome.node.assembly` | root |
| 2 | `declared_children` | `machinome.node.declarative` | root |
| 3 | `FusionNode` | `machinome.node.fusion` | root |
| 4 | `CadQueryNode` | `machinome.node.cadquery` | table, `cadquery` |
| 5 | `Build123dNode` | `machinome.node.build123d` | table, `build123d` |
| 6 | `Build123dSheetNode` | `machinome.node.build123d` | table, `build123d` |
| 7 | `SheetLeafNode` | `machinome.node.sheet_leaf` | root |
| 8 | `FlexibleNode` | `machinome.node.flexible` | root |
| 9 | `MolejoNode` | `machinome.node.molejo` | table, `molejo` |
| 10 | `Solid2Node` | `machinome.node.solid2` | table, `solid2` |
| 11 | `OpenScadNode` | `machinome.node.openscad` | table, `openscad` |
| 12 | `JScadNode` | `machinome.node.jscad` | table, `jscad` |
| 13 | `StlNode` | `machinome.node.stl` | table, `stl` |
| 14-17 | `Marking`, `Wrapped`, `Flat`, `Svg` | `machinome.node.markings` | root |
| 18 | `Frame` | `machinome.node.frames` | root |
| 19 | `StepNode` | `machinome.node.step` | table, `step` |
| 20 | `property_as_number` | `machinome.node.decorators` | root |
| 21 | `StlRenderStart` | `machinome.node.base` | root |

A refusal imports nothing but `supported`: it never imports the named module,
so `from machinome.node import StepNode` where CadQuery is absent meets the
root's refusal, naming `machinome.node.step`, and the line it suggests then
meets the module's own refusal naming `machinome[step]`. A statement naming
several former names raises for the first (`from machinome.node import
AssemblyNode, RotationalPort` raises the `AssemblyNode` refusal, not the port
redirect), which is why the `ports` delta's old-path scenario now names only
moved names.

### 4. `_MOVED` and the adapters package stay

ADR-169 left both to this cycle. Both are refusals, not paths: neither resolves
a name, so neither contradicts "exports nothing", and each turns a released
spelling (the port names the 0.7 upgrading page already sends readers away from
`machinome.node`; `machinome.node.adapters.<x>`, the leaf addresses of 0.7.x)
into a message naming where the name went, for a user outside the catalogue
whom the workspace pass never reaches. Removing them would
replace those messages with Python's, which names no destination. The adapters
docstring's "the root spellings ... are unchanged" is reworded. Open Question 2.

### 5. The doors, after the root stops exporting

ADR-167's three doors were the module's import, the root's lazy export and the
CLI command. The second goes: the root resolves no class, so it imports no node
type's module on a class name. What remains, for a kernel module:

- the module's import, however spelled: `import machinome.node.step`,
  `from machinome.node.step import StepNode`, or through the package,
  `from machinome.node import step` and the attribute read `machinome.node.step`,
  which `_submodule`/`_load` carry with the refusal unmodified;
- the table's `load(key)`, which reads the refusal as an absent node type
  (`machinome new`, `import-step`, `snapshot`);
- the CLI command that needs the module (ADR-168).

`openscad-node`'s requirement keeps its title, "refused at three doors", with
the doors renamed (its delta). For `jscad` and `stl` there is no door: neither
module needs a kernel the core does not require, so neither calls
`require_extra` and neither is ever refused for an absent extra (Decision 7).

### 6. The gate: one permanent test, red first

`tests/test_node_root_exports_nothing.py`, with the 21 names and their modules
written out (not read from the package under test):

- **G1, the root resolves nothing.** For each name: `from machinome.node import
  <name>` (an `exec` of a statement composed from the table) raises
  `ImportError` whose message is Decision 3's text; `getattr` and `hasattr`
  raise the same; `from <module> import <name>` returns the object the module
  defines. `machinome.node.__all__ == []`; `from machinome.node import *` binds
  nothing; every public name of `vars(machinome.node)` is a module whose
  `__name__` is `machinome.node.<name>`. Every class name of every row of
  `supported.NODE_TYPES` is refused naming `machinome.node.<key>` (the derived
  half, checked against the table). Red on 815ceb9: all 21 resolve, `__all__`
  has 21 entries, five public names are not submodules.
- **G2, nothing spells them.** The scan of `gate-prototype.py`: every text file
  under `machinome/` and `tests/`, and under `docs/` without `docs/adrs/`,
  `_build/`, `_exports/`, plus `README.rst`, read as text (code, strings,
  docstrings, comments, prose), offends for each name of the 21 in a
  `from machinome.node import ...` statement (one line, parenthesised, or
  backslash-continued), for the star import, and for each dotted address
  `machinome.node.<name>`. A submodule import passes; a statement composed at
  run time (`f'from machinome.node import {name}'`) is not a literal and
  passes, which is how the refusal tests spell it; the gate's own planted
  samples are spelled in pieces (`'from machinome.node ' 'import X'`), as the
  earlier gates spell their words. No other exemption. Red on 815ceb9:
  `machinome/` 6 files (8), `tests/` 291 (491), docs 20 (58).
- **The scan's self-test**: planted samples of each offending form are found;
  a submodule import, a composed statement and a decision record are not.

### 7. `jscad` and `stl`: two extras that install nothing, in `all`

`machinome/node/jscad.py` imports `os`, `sys`, `tempfile`, `time`,
`subprocess` and four core modules (`:5-13`); it renders by running the `jscad`
command (`Popen`), a Node program from npm that no pip extra can install.
`machinome/node/stl.py` imports `trimesh` (`:35`), a required dependency
(`trimesh==4.4.*`, `pyproject.toml:26`) the core itself reads meshes with, and
two core modules. Neither needs a Python package the core does not require, so:

```toml
# `machinome.node.jscad` (JScadNode) runs the `jscad` command, a Node program
# no pip extra installs; the extra names the node type and installs nothing.
jscad = []
# `machinome.node.stl` (StlNode) reads meshes with trimesh, which the core
# requires; the extra names the node type and installs nothing.
stl = []
all = [
    "machinome[cadquery,build123d,step,molejo,brep,mesh,openscad,solid2,jscad,stl]",
]
```

Why declare an empty extra: the rule "address and extra are the node type's
name" (`supported.py`'s docstring, ADR-179) already promises `machinome[jscad]`
and `machinome[stl]`: `supported.load('jscad')`, for a cut package that is not
installed, refuses with `pip install "machinome[jscad]"` (`supported.py:79`),
an extra pip today warns it does not provide and installs nothing for. With the
extras declared that line is valid now and a manifest that declares its mix
(`machinome[cadquery,stl]`, the ruling's reason: "a project's dependencies must
say at once what mix it makes") keeps working when the node packages are cut
and the extras start pulling them. Restating `trimesh==4.4.*` in `stl` was
rejected: the `kernel-extras` rule that a requirement named twice carries one
range would hold, but the extra would claim a dependency the core already has,
and removing it from the core is the cut's decision, not this cycle's.

Probe: setuptools 84.0.0 (the venv's) writes `Provides-Extra` for an empty
`optional-dependencies` list and no `Requires-Dist` (scratch project, metadata
only); the framework's build backend is pinned `setuptools>=65.5,<77`, so the
same is checked with the pinned range as a validation leg (Decision 14).

The three doors: none (Decision 5). The rows `jscad` and `stl` exist in
`NODE_TYPES`. The vet universe already passes `machinome.node.jscad` and
`machinome.node.stl` (`vet` spec). The docs: the install page's extras table
gains the two rows and its sentence "``JScadNode`` and ``StlNode`` need no extra
to build" becomes the extras' description; the backends guide's node-type
table, whose "Needs" column says "nothing" for the CadQuery and build123d
classes since `lean-install`, gains a module and an extra per class, all eight
node types and nine classes.

### 8. The repointing: a script in this change, then the hand edits

The workspace tool is not the method, for three reasons read from it
(`scripts/rewrite-projects`): it walks the project catalogue and skips a linked
worktree, and the bench is one; it applies every table under
`scripts/rewrite-projects.d/` at once, which would also rewrite the suite's
deliberate spellings of earlier cycles' former names (the refusal tests of
`machinome.exact_engine`, `ExactLeafNode`, `--faceted`); and it rewrites import
statements through the syntax tree only, where 81 of the suite's offences are
fixture sources inside strings or dotted addresses.

So `repoint.py` (in this change, dry run by default) reads this change's
`moved-names.toml`, whose 21 rows equal the workspace table's root block name
for name (checked: 21 = 21, identical), and reads the gate's zones as text:

- a statement whose former names all go to one module is repointed in place
  (`machinome.node` → `machinome.node.<module>`), keeping its format, aliases
  and comments;
- a statement spanning several modules and beginning its physical line (code,
  a triple-quoted fixture, a page's code block) becomes one statement per
  module, in order of first appearance, at its indentation, each with the
  statement's trailing comment, parenthesised beyond 79 columns;
- a dotted address `machinome.node.<name>` becomes `machinome.node.<module>.<name>`;
- anything else the gate would still find is listed for a hand edit.

Dry run on 815ceb9: `machinome/` 3 files (2 in place, 1 split); `tests/` 290
files (273 in place, 76 split, 1 dotted address, 1 listed:
`test_external_wrapper_identity.py:260`, an f-string composing
`from machinome.node import {kind}, AssemblyNode, Frame`); docs 18 files (19 in
place, 11 split, 12 dotted addresses, the API reference's directives). Applied
in memory, every rewritten `.py` file parses (but the suite's deliberately
unparseable `tests/vet_projects/unparseable/sim/broken.py`), no new line exceeds
CI's 89 columns, and the gate's scan finds nothing outside the six files the
script never touches (`HAND`): the root, the adapters docstring,
`manager/import_step.py`, `tests/test_node_lazy_exports.py`, the changelog and
the upgrading page.

Then, by hand:

- `machinome/manager/import_step.py` composes its two import lines from the
  classes it writes for, `f'from {cls.__module__} import {cls.__name__}'` with
  `StepNode` from the loaded `step` module and `AssemblyNode` from
  `machinome.node.assembly`, so the command spells no node type's module
  (`tests/test_core_kernel_free.py` keeps it among `TABLE_READERS`).
- The docstrings of the root, `node/adapters/__init__.py`, `node/build123d.py`
  (":`machinome.node` resolves its adapters on first use") and
  `node/supported.py` (the `classes` column "the node root resolves").
- The tests whose subject is the root: `tests/test_node_lazy_exports.py`
  becomes `tests/test_node_root.py` (`git mv`, history kept; its export tests
  become refusal tests, its import-cost tests import the modules, its
  broken-backend tests go through the submodule, its star-import test asserts
  nothing is bound); `test_supported_node_types.py` (`assertIn(name,
  machinome.node.__all__)` and the identity through the root become the
  refusal); `test_leaf_addresses.py` (docstring and the root-identity test);
  `test_openscad_node.py:86-88` (the root identity becomes the refusal);
  `test_motion_package.py:136` (`test_a_node_class_is_still_a_node_export`
  becomes `test_a_node_class_is_imported_from_its_module` with the refusal);
  `test_markings.py:476` (`PublicModuleTest`: the four names are refused at the
  root naming `markings`); `test_leaf_capability_set.py:144` (iterates
  `machinome.node.__all__`, which becomes empty and would silently test
  nothing: it walks the table's modules' classes and the core's leaf bases
  instead); `test_external_wrapper_identity.py:260`; `test_core_kernel_free.py`
  (`SEAMS` admits the `cadquery` template naming `machinome.node.cadquery`, and
  the root moves from `SEAMS` to `TABLE_READERS`, naming none).

### 9. The goldens: one expected difference, the leaf-contract golden's source digests

`leaf_contract_golden.py --check` will differ in the `digest` of every
artifact's source record, for all seven fixtures, because each fixture's package
imports from the root and that line is digested (Context). Nothing else it
records can move: artifact bytes (`sha256`, `entities_sha256`), `record_version`,
`uniq_id` (the class and its parameters, `_build_uniq_id`, `node/base.py:457`), and the two
booleans. The script gains `ROOT_CLEANUP_EXPECTED`, in the shape of
`mesh_engine_golden.py`'s `BREP_MESH_EXPECTED`: under `--check`, a `digest`
that differs is reported as expected and every other field must be identical;
the golden's JSON is not re-recorded. *Inferred*, to be confirmed by the leg:
`scad_presentation_golden.py` (SCAD text and `.scad` files), 
`expression_type_golden.py` (serialized operations, SCAD, the published
document without `mtime` and `source`), `brep_engine_golden.py` (B-rep and STL
bytes, measurements) and `mesh_engine_golden.py` (verdict tuples) record nothing
a source line feeds and stay identical; any difference there is a defect.
Open Question 4.

### 10. The manual

- Every example repointed by the script; the six multi-name blocks of
  `concepts/joints.rst` and the tutorial's modules split per module.
- `reference/api.rst`: the twelve directives at module addresses; the Nodes
  section's "All node classes are importable from ``machinome.node``" becomes
  "Each node class is imported from its module, the address beside it below;
  the root of ``machinome.node`` exports nothing"; the frames section (`:652`)
  drops "and from ``machinome.node``".
- `concepts/values.rst:54` and `tutorial/03-dimensions.rst:24`: node classes
  come from their modules under ``machinome.node``.
- `start/install.rst`: the two extras' rows, the sentence on `JScadNode` and
  `StlNode`, and ":`from machinome.node import CadQueryNode`" (`:93`) becomes the
  module import the refusal answers.
- `howto/backends.rst`: the node-type table with module and extra per class.
- `project/upgrading.rst`: a section "Import every name from its module
  (unreleased)" with the 21-row mapping written as name → module (never as a
  root address, so the gate needs no exemption), the refusal, and the note that
  each part a rewrite touches rebuilds once; the port-imports example repointed.
- `project/changelog.rst`, Unreleased: this cycle's bullet, and the
  `lean-install` bullet's "The root spellings ... are unchanged" and "the same
  through ``from machinome.node import CadQueryNode``" revised in place to the
  shipped state (precedent: `brep-mesh`'s Open Question 5, ratified; nothing in
  Unreleased has been released).
- `docs/architecture.md` (`:315-347`): the root's paragraph and the doors.

### 11. The core modules touched

`machinome/node/__init__.py` (Decisions 1-3), `machinome/node/supported.py`
(docstring only: the `classes` column's readers are now the root's refusal and
`load`'s message), `machinome/manager/import_step.py` (Decision 8), the two
templates, `pyproject.toml` (Decision 7), four docstrings. No other module
changes behaviour.

### 12. Specs

Deltas for every baseline spec whose text or scenarios spell the root as a
path for a former name: `node-model` (new requirement "The node package's root
exports nothing"; "Each leaf type is one module under the node package"),
`cli-startup-cost` ("Node backend exports resolve on first use" renamed
"Importing the node package imports no backend"; "Deferred imports do not hide
a broken installation"), `kernel-extras` (the extras; the core's kernel-module
naming, where the scan scenario also gains the `cadquery` template, which
imports CadQuery today and which the baseline scenario omits while
`test_core_kernel_free.py` lists it), `openscad-node`, `markings`, `mates`,
`ports`, `vet`, `cli` (new requirement on generated source) and
`user-documentation` (new requirement "The manual imports every name from its
module"; the values page's statement). Examined and left: `kinematics`
(`from machinome.node import Time` is still refused naming the motion package),
`framework-identity` (its extras requirement names the product extras only),
`stl-import` and `step-import` (no root spelling; the extras live in
`kernel-extras`), `leaf-contract` (`StlRenderStart` at `machinome.node.base`
already), `step-assembly` (the generated import lines are specified once, in
`cli`). Scenario titles kept for OpenSpec 1.6.0 and renamed by the archive
task: `scenario-titles.tsv` (two rows).

### 13. Proof, red first

Each written before the code it proves, each red on 815ceb9 for the reason
given:

1. `tests/test_node_root_exports_nothing.py` (Decision 6): G1 red (the root
   resolves the 21), G2 red (6 + 291 + 20 files).
2. `tests/test_kernel_extras.py`: `EXTRAS` gains `jscad: set()`, `stl: set()`
   and the `all` line with both; a new test that every key of
   `supported.NODE_TYPES` is an extra. Red: `pyproject.toml` declares neither.
3. `tests/test_docs_structure.py`, `KernelExtrasTest.EXTRAS` gains `jscad` and
   `stl`: the install page must name `machinome[jscad]` and `machinome[stl]`.
   Red: it names neither.
4. `tests/test_manager_new.py`: `EXPECTED_INIT` and the CadQuery template's
   expectation carry the module import. Red: the templates import from the
   root.
5. `tests/test_import_step.py`: the generated `parts.py` and `assembly.py`
   import `StepNode` from `machinome.node.step` and `AssemblyNode` from
   `machinome.node.assembly`, and hold no `from machinome.node import`. Red: the
   generator writes the root spelling.
6. `tests/test_node_root.py` (from `test_node_lazy_exports.py`): the refusal
   per name, the empty `__all__`, the star import binding nothing, the submodule
   doors (`from machinome.node import step` with CadQuery refused carries the
   `step` refusal unmodified; broken, the splice naming `step`). Red: the root
   resolves the names.

### 14. Empirical validation (the orchestrator runs every leg)

After the suite, against the bench, one leg at a time (virtiofs):

- **The workspace pass first**: `scripts/rewrite-projects --apply` over every
  project repository (the orchestrator's, before integration, with the
  pilot's announcement), then **the universe sweep**: `scripts/load-projects`
  with the nine earlier tables plus this change's `moved-names.toml` (copied as
  `scripts/load-projects.d/root-cleanup.toml`), 300 s timeout. Expected: 117 or
  more `ok` (the four customers waiting since `lean-install` repaired by the
  pass), **zero `expected`**, the 2 pre-existing `unexpected` (wall_clock_41's
  own CadQuery error, Dum-E without machinome-freecad) and 6 no-model. Any
  `expected` row is a project the pass missed.
- **The goldens**, each in a fresh process, `--check`: `leaf_contract_golden.py`
  (only `digest` fields differ, reported as expected by `ROOT_CLEANUP_EXPECTED`),
  `scad_presentation_golden.py`, `expression_type_golden.py`,
  `brep_engine_golden.py`, `mesh_engine_golden.py` (with `BREP_MESH_EXPECTED`):
  no other difference.
- **A project on the module spelling, deep**: `Locks/Pin_tumbler_lock` after
  the pass: `machinome build` (each part whose file the pass rewrote rebuilds
  once; its 15 `.scad` hashes identical to the line's before the pass; STL
  compared by SCAD, since OpenSCAD's STL is not reproducible run to run), then
  `machinome test --mesh --no-verdict-store`: 24 tests with the brep-mesh
  validation's outcomes and its 2573 verdicts identical.
- **The generators**: `machinome new` under the three installs of the
  `openscad-out` leg (all extras; CadQuery only; neither), the generated module's
  import line and its two tests; `machinome import-step` on a document of the
  catalogue (the Internal-Cycloidal-Actuator's), the generated files' import
  lines, and the generated model loading.
- **The extras**: package metadata built with the pinned build backend
  (`setuptools>=65.5,<77`) shows `Provides-Extra: jscad` and `stl` with no
  requirement, and `pip install "<bench>[jscad,stl]"` in a throwaway environment
  warns of no unknown extra.
- **The doors** in throwaway processes with the finder helpers:
  `from machinome.node import Solid2Node` with SolidPython refused meets the
  root's refusal naming `machinome.node.solid2`;
  `from machinome.node.solid2 import Solid2Node` and `from machinome.node import
  solid2` meet the module's refusal naming `machinome[solid2]`.
- **The manual**: the docs job's build (`docs/requirements.txt`, warnings as
  errors) succeeds with the directives at module addresses.

## SOLID review

The pilot's standing requirement; where the design follows each principle and
where it bends.

- **Single responsibility.** The root had two jobs, being the package (its path,
  its submodules, its refusals) and being a facade that re-exported 21 names;
  it keeps the first. The table keeps its one job, the node types the core
  supports: the core's twelve names, which are not node types, stay out of it
  (Decision 2). The import-step generator writes what its classes report
  instead of knowing where they live.
- **Open/closed.** A node package added later contributes its module as a
  portion and its row to the table; projects import it from its module, and the
  root refuses its class names with no edit, because it derives them. **Bend:**
  the core's twelve-name table is closed by design, a record of the former
  exports, never extended.
- **Liskov.** No class changes; the object at `machinome.node.<module>.<Class>`
  is the object the root returned before, with the same `__module__`, so
  `isinstance`, `issubclass`, pickling, `uniq_id` and recipe identities are
  unchanged. A refusal is never a stand-in object that half-behaves like the
  class.
- **Interface segregation.** A project's import line now says exactly which
  modules it depends on, and so which node packages (and extras) its mix needs:
  `machinome.node.stl` and `machinome.node.assembly`, not the root's 21. Importing
  the package no longer imports `base` and its six submodules. Each node type
  has its own extra, `jscad` and `stl` included.
- **Dependency inversion.** The root depends on the table's rows, not on any node
  type's module, and imports none; generated source depends on the class's
  reported module. **Bend:** the two templates spell their node type's module;
  they are a project's files, copied and never imported, as they already spell
  their kernel.

## ADRs

Extracted after implementation, under the framework-change skill:

- **ADR-181** (NODE), "The node package's root exports nothing": the 21 former
  root names refused with `ImportError` naming their module (the text); the two
  sources of the refusal (the table for node types, the root's closed table for
  the core's twelve) and why not one table; the empty `__all__` and the strict
  reading of the namespace; `_MOVED` and the adapters package kept; the doors
  after the root (the root's lazy export door gone; the submodule door kept);
  `jscad` and `stl` as empty extras listed in `all`; generated source composed
  from class metadata; the gate. Amends ADR-169 (the root's re-exports struck;
  "the root spellings unchanged" no longer holds; the root cleanup decided
  `_MOVED` and the adapters package: both stay), ADR-167 (the three doors), and
  ADR-179 (the `classes` column's readers: the root's refusal and `load`'s
  message, no export table). Clarifies the reading of ADR-166 (a lookup of the
  requested name that words a refusal is not class-name recognition). Cites
  ADR-087, ADR-168, ADR-177 and ADR-180.

One ADR: the export rule, its refusal and the two extras are one decision of the
pilot's, and the extras are its symmetry.

## Moved names

`moved-names.toml` in this change, in the earlier cycles' format (`cycle`,
`date`, `[[moved]]` rows with `name` and `to`), holds the 21 rows
`machinome.node.<name>` → `<module>.<name>`, equal to the root block of the
workspace's `scripts/rewrite-projects.d/root-cleanup.toml`. No informational
row: the two extras are new, not moved.

## Risks / Trade-offs

- [A project file still spells the root after the pass] → its load fails at the
  import line with the refusal, which `load-projects` explains by its row; the
  sweep's expectation of zero `expected` rows catches it before integration. A
  repository skipped for uncommitted changes is reported by the tool and
  rewritten once clean.
- [Every rewritten part rebuilds once; every verdict store recomputes once] → the
  import line is in the source digest (Context), so each part whose file the
  pass rewrote rebuilds, to the same bytes; the verdict store's stamp digests
  the framework's sources and recomputes, as at every framework edit (ADR-156).
  The upgrading page says so; the heaviest projects (Prusa3-vanilla, the clocks)
  pay one cold run.
- [The leaf-contract golden reports differences] → `digest` only, expected by
  `ROOT_CLEANUP_EXPECTED` (Decision 9); any other field is a defect.
- [`hasattr(machinome.node, 'AssemblyNode')` raises instead of answering
  `False`] → as `_MOVED` already does for ports; no module under `machinome/`
  probes the root by name (grep), and a consumer probing must catch
  `ImportError`.
- [Removing the eager `base` import changes the import order] → nothing under
  `machinome/` or `tests/` relies on `import machinome.node` importing `base`
  (grep for its side effects and for `machinome.node.base` read without an
  import: the attribute read resolves the submodule on demand); the suite is the
  check.
- [`from machinome.node import *` silently binds nothing] → no project or page
  star-imports the root (lean-install's grep of 3 October; the gate forbids it
  in the framework).
- [Sibling repositories break against the line] → the studio's two skills teach
  the root spelling (seven lines); machinome-mechanics' two tests and two
  documentation examples import from the root and fail against the line until
  their paired change; follow-ups at the release (Migration Plan).
- [Empty extras under the pinned setuptools] → the metadata leg (Decision 14);
  if an older setuptools dropped an empty extra, `jscad` and `stl` would name
  nothing pip knows and the leg fails before integration.
- [A stale `__pycache__`] → this change deletes no package directory, so the
  namespace-package hazard of `openscad-out` and `brep-mesh` does not arise.
- [The text gate flags a page that quotes a former spelling] → the upgrading
  page and the changelog are written without the literal spellings (name →
  module), and decision records are outside the zone; a future page quoting one
  writes it the same way.
- [A future node type's class names are refused at the root although never
  exported] → intended: the refusal is a pointer to the one path, true for any
  class of the table.

## Migration Plan

- **Projects** (the orchestrator, before integration): the workspace's
  `scripts/rewrite-projects --apply --message <cycle>` over every project
  repository, one commit per repository on its checked-out branch, only the
  rewritten files; untracked `.env` files rewritten and not committed;
  worktrees inside a project reported, not rewritten; Voron-2's 29 `shape()`
  call sites by hand in the same pass. Then the sweep (Decision 14).
- **Persisted state, once, automatically**: rewritten parts rebuild and verdict
  stores recompute on their next build or test run. Nothing to run by hand.
- **Checkouts**: nothing to clean.
- **Outside the framework** (findings for the orchestrator, not this cycle's
  edits): machinome-studio's `shop-skills/machinome-api/SKILL.md` (six lines)
  and `shop-skills/machinome/SKILL.md` (one), a paired studio change at the
  release, with the `--faceted`/`--exact` follow-up already recorded;
  machinome-mechanics' `tests/test_motion.py`, `tests/test_declarative.py`,
  `docs/examples/slider_crank.py` and `docs/examples/gear_phase.py`, with its
  release pass (its pin `machinome>=0.7.0` is already on that list); the
  workspace's `scripts/load-projects.d/` gains `root-cleanup.toml` from this
  change's `moved-names.toml`.
- **Rollback**: revert the implementation commit; the projects' rewritten
  imports keep working against the reverted root (the modules are the same
  addresses), so rollback needs no second pass.

## Open Questions

1. **The strict reading of "exports nothing".** The root binds no public name
   but its submodules (`NODE_TYPES`, `import_module`, `find_spec`,
   `ExtraUnavailable` made private or dropped), and the gate checks it.
   Recommendation: strict, because each of those names is a second path today
   (`from machinome.node import NODE_TYPES` works); the alternative, refusing
   only the 21, leaves the rule to the next helper someone imports in the root.
2. **`_MOVED` and `machinome.node.adapters`.** Recommendation: keep both
   (Decision 4): they resolve nothing and they redirect released spellings for
   users the workspace pass does not reach. The alternative removes both now that
   the catalogue is rewritten, at the cost of Python's message for everyone else.
3. **The node types' refusals derived from the live table.** Recommendation: as
   designed (Decision 2): forced by the `openscad-out` gate and open to a new row.
   The alternative, a frozen list of the nine, would have to spell `OpenScadNode`
   in pieces in the root to pass that gate.
4. **The leaf-contract golden.** Recommendation: an expected-difference table for
   `digest` (Decision 9), as `brep-mesh` did for the mesh golden, the JSON not
   re-recorded. The alternative, re-recording, would also accept any other drift
   of the same run.
5. **The changelog's `lean-install` bullet.** Recommendation: revise in place
   (Decision 10), as ratified for `brep-mesh`'s Open Question 5.
6. **`tests/test_node_lazy_exports.py`.** Recommendation: rename it
   `tests/test_node_root.py` with `git mv`: its subject, lazy exports, no longer
   exists, and a reader of a failure sees the module name first.
7. **The refusal's words** (Decision 3). Recommendation: as written; it keeps
   Python's opening sentence, which the sweep reads, and names the module twice
   only once as data and once as the line to write.
8. **The root's table's name.** `_DEFINED_IN` is provisional; recommendation:
   keep it, beside `_MOVED`, both private.
