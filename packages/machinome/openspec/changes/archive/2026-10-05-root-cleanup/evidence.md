# Evidence — `root-cleanup`

The tenth cycle of layer 1 of the lean-core campaign, the third of the phase
"The next phase: the architecture ready for the split"
(`workflow/ongoing/lean-core.md`, item 3) and the last before 0.8. Worktree
`machinome/WTs/v0.8-split-root-cleanup`, branch `v0.8-split-root-cleanup`,
cut from `v0.8-split` at 815ceb9 ("Merge branch 'v0.8-split-brep-mesh' into
v0.8-split"). Planning commit deb5244 ("root-cleanup: plan the node root that
exports nothing (decided 5 October 2026)"), decided by the pilot on 5 October
2026 and ratified by the orchestrator's review with every recommendation of
design.md's Open Questions taken. Every command below ran with
`env -C <worktree>`, `PYTHONPATH=<worktree>` and the workspace venv (Python
3.12.3), but `flake8`, which the venv does not carry and which ran from the
pyenv shim (flake8 7.3.0 on CPython 3.11.14); pytest ran one process at a
time, never two of this cycle's at once. Other sessions' processes on this
filesystem (the orchestrator's sweep among them) did not block this cycle's
runs, on the orchestrator's instruction. No run of this cycle died with "Too
many open files".

```
$ git -C <bench> log --oneline -2
deb5244 root-cleanup: plan the node root that exports nothing (decided 5 October 2026)
815ceb9 Merge branch 'v0.8-split-brep-mesh' into v0.8-split
```

The worktree was clean at the start: the planning files are
committed in deb5244.

## 1. Baseline on the unmodified tree (deb5244)

### 1.1 The gate's and the repointing's counts (task 1.2)

`python openspec/changes/root-cleanup/gate-prototype.py <bench> --files`:

```
machinome: 6 files, 8 offences
    2 machinome/manager/import_step.py
    1 machinome/manager/templates/project/root/cadquery.py
    1 machinome/manager/templates/project/root/solid2.py
    1 machinome/node/__init__.py
    1 machinome/node/adapters/__init__.py
    2 machinome/parameters.py
tests: 291 files, 491 offences
docs: 20 files, 58 offences
```

(the 291 test files listed in scratch; the largest are
`tests/test_node_lazy_exports.py` 9, `tests/test_stl_node.py`,
`tests/test_markings.py` and `tests/test_leaf_capability_set.py` 8 each.)

`python openspec/changes/root-cleanup/repoint.py <bench>` (dry run):

```
LISTED tests/test_external_wrapper_identity.py:260: left for a hand edit
machinome: {'files': 3, 'in place': 2, 'split': 1, 'dotted': 0, 'listed': 0}
tests: {'files': 290, 'in place': 273, 'split': 76, 'dotted': 1, 'listed': 1}
docs: {'files': 18, 'in place': 19, 'split': 11, 'dotted': 12, 'listed': 0}
HAND machinome/manager/import_step.py
HAND machinome/node/__init__.py
HAND machinome/node/adapters/__init__.py
HAND tests/test_node_lazy_exports.py
HAND docs/project/changelog.rst
HAND docs/project/upgrading.rst
dry run: nothing written
```

Both equal design.md's counts, zone for zone, and the six `HAND` files.

The probe of `vars(machinome.node)` in a fresh interpreter:

```
21
public: ['ExtraUnavailable', 'NODE_TYPES', 'StlRenderStart', 'base', 'declarative', 'find_spec', 'frames', 'import_module', 'markings', 'phase', 'presentation', 'sources', 'supported']
not submodules: ['ExtraUnavailable', 'NODE_TYPES', 'StlRenderStart', 'find_spec', 'import_module']
```

21 names in `__all__`; the five public names that are not submodules are
design.md's five.

### 1.2 The moved-names table against the workspace's (task 1.3)

Read-only, with `tomllib`: the `[[import]]` rows of the workspace's
`scripts/rewrite-projects.d/root-cleanup.toml` whose `from` is
`root-cleanup`, against this change's `moved-names.toml` `[[moved]]` rows:

```
21 21 True True
```

21 rows each, equal as ordered lists and as sets, `name` and `to` alike.

### 1.3 The suite on the base (task 1.4)

The first run hung: at 82 % (2427 s of wall time) its child
`machinome build tests/scad_where_read_project/machine.py:Machine` was
restarting its spawned build process every 2 to 4 seconds (PIDs sampled one
second apart: 3863703, 3863703, 3863764, 3863823, 3863823, 3863906),
the fresh-worktree defect of `workflow/warts.md` (a build in a project whose
sources were written moments earlier restarts with `SOURCE_CHANGED`
without end). It was killed by PID (rc=143), not read as a code failure.
On the orchestrator's instruction the tracked files under `tests/` were
given one old mtime, contents untouched
(`env -C <bench> sh -c 'git ls-files -z tests | xargs -0 touch -c -m -d @1791126775'`;
`git status` stayed clean), and the suite reran alone:

```
4568 passed, 4 skipped, 55 warnings, 6338 subtests passed in 660.04s (0:11:00)
```

the line's count at 815ceb9. The same touch (to the then-current time less
two hours) was repeated before each later whole-suite run over the files
this cycle rewrote, and over `docs/tutorial/` whose modules a test builds.

*A slip, outside the bench, recorded.* The orchestrator's first spelling of
that touch, `env -C <bench> git ls-files -z tests | xargs -0 touch ...`,
applies `env -C` to `git` only, so `touch` ran in the session's working
directory, the workspace, where it created 255 empty untracked files under
`tests/` and restamped one tracked file's mtime
(`tests/test_machinome_identity.py`, content unchanged). Reported at once;
the orchestrator removed the 255 files (each verified empty, untracked and
carrying the touch's stamp). The bench's touch above is the `sh -c` form.

### 1.4 The five goldens on the base

Each `--check` in a fresh process, before any source change:

```
leaf_contract_golden       golden comparison: 7 fixtures, 77 values, 0 differences                                                  (4.6 s)
scad_presentation_golden   golden comparison: 34 values, 0 differences, 9 presentation files absent as expected                      (3.5 s)
expression_type_golden     golden comparison: 17 values, 0 differences                                                             (1.3 s)
brep_engine_golden         golden comparison: 7 fixtures, 0 differences                                                            (4.6 s)
mesh_engine_golden         golden comparison: 1095 values, 0 differences, 2 expected (design.md Decision 4), 200 renamed (brep-mesh)   (116.0 s)
```

## 2. Red first (unmodified source)

The tests of group 2, written before any source change:

- 2.1 `tests/test_node_root_exports_nothing.py` (new): G1, the 21 names and
  modules written out, each refused at `from machinome.node import <name>`
  (composed with an f-string and `exec`), by `getattr` and by `hasattr`, with
  Decision 3's text spelled independently; each imported from its module;
  `__all__ == []`; the star import binding nothing; every public name of
  `vars(machinome.node)` a submodule; every class of every row of
  `supported.NODE_TYPES` refused naming `machinome.node.<key>`; a row added
  to the table (patched, `GizmoNode`) refused naming `machinome.node.gizmo`;
  `NoSuchNode`, `NODE_TYPES`, `import_module`, `find_spec`,
  `ExtraUnavailable` and `Length` plain `AttributeError`s; the table's nine
  classes equal to the nine written here. G2, the scan of
  `gate-prototype.py` over the three zones (`in_zone`, `offences`, `scan`),
  with its self-test: the one-line, parenthesised, continued, aliased, star,
  dotted, in-prose and in-string forms found; a submodule import, a module
  address, a moved port name and a composed statement passing; the zones'
  edges (a decision record, built output, `openspec/`, `workflow/` out).
- 2.2 `tests/test_kernel_extras.py`: `EXTRAS` gains `'jscad': set()` and
  `'stl': set()` and the `all` line names both; `test_all_names_every_kernel_extra`
  gains both; new `test_every_node_type_has_the_extra_of_its_name`.
- 2.3 `tests/test_docs_structure.py`: `KernelExtrasTest.EXTRAS` gains `jscad`
  and `stl`.
- 2.4 `tests/test_manager_new.py`: `EXPECTED_INIT` reads
  `from machinome.node.solid2 import Solid2Node`, `EXPECTED_CADQUERY`
  `from machinome.node.cadquery import CadQueryNode`.
- 2.5 `tests/test_import_step.py`: new `GeneratedImportsTest`, the generated
  `parts.py` holding `from machinome.node.step import StepNode` and
  `assembly.py` `from machinome.node.assembly import AssemblyNode`, neither
  holding `from machinome.node import`.
- 2.6 `git mv tests/test_node_lazy_exports.py tests/test_node_root.py`,
  revised by hand: the export tests are refusal tests (`__all__` empty, each
  former export refused naming its module, each defined by its module, the
  CadQuery class a real class from its module, the star import binding
  nothing in a fresh interpreter, `dir` offering none, a refusal never
  cached); the import-cost tests import the modules (`machinome.node.solid2`,
  each B-rep class from its module, `machinome.node.step` importing OCP), and
  gain "importing the package imports no node type" and "a refused name
  imports no node type"; the broken- and absent-backend tests go through
  `machinome.node.step` and `from machinome.node import step` (the refusal
  unmodified; the broken install spliced naming `step`), plus the doors'
  order (the root's refusal of the class name before the module's refusal of
  its kernel); the submodule tests gain
  `from machinome.node import supported, phase, step`; the parameter and
  moved-port tests stay; the docstring says what the root is now.

Run together (task 2.7):

```
142 failed, 114 passed, 870 subtests passed in 30.31s
```

The reasons, verbatim (`--tb=line`, counted):

```
     93 E   AssertionError: ImportError not raised
      4 E   AssertionError: AttributeError not raised
      2 E   AssertionError: Lists differ: ['StlRenderStart', 'AssemblyNode', 'declar[258 chars]ode'] != []
      2 E   AssertionError: 'from machinome.node import Solid2Node\nfrom solid2 import cu[180 chars]0)\n' != 'from machinome.node.solid2 import Solid2Node\nfrom solid2 im[187 chars]0)\n'
      1 E   KeyError: 'stl'
      1 E   KeyError: 'jscad'
      1 E   AssertionError: {'machinome': ['machinome/manager/import_step.py', 'mach[12111 chars]py']} != {'machinome': [], 'tests': [], 'docs': []}
      1 E   AssertionError: Lists differ: [] != ['REFUSED', 'False', 'REFUSED', 'False']
      1 E   AssertionError: Lists differ: ['AssemblyNode', 'Build123dNode', 'Build12[322 chars]ber'] != []
      1 E   AssertionError: Lists differ: ['AssemblyNode', 'Build123dNode', 'Build12[258 chars]ber'] != []
      1 E   AssertionError: Items in the second set but not the first:
      1 E   AssertionError: Items in the first set but not the second:
      1 E   AssertionError: False is not true : LOADED ['machinome.node.cadquery', 'machinome.node.step']
      1 E   AssertionError: False is not true : ExtraUnavailable | machinome.node.step (StepNode, StepAssembly) needs cadquery, which is not installed; install it with 'pip install "machinome[step]"'
      1 E   AssertionError: 'stl' not found in {'dev': ['machinome[all]', ...
      1 E   AssertionError: 'jscad' not found in {'dev': ['machinome[all]', ...
      1 E   AssertionError: 'machinome[stl]' not found in 'Install\n=======\n...
      1 E   AssertionError: 'machinome[jscad]' not found in 'Install\n=======\n...
      1 E   AssertionError: '\nfrom machinome.node.step import StepNode\n' not found in '# Machinome - generated by `machinome import-step`\n\n"""Parts scaffolded from \'import_simple.step\' ...
      1 E   AssertionError: '\nfrom machinome.node.assembly import AssemblyNode\n' not found in '# Machinome - generated by `machinome import-step`\n\n"""Assembly scaffolded from \'import_simple.step\' ...
      1 E   AssertionError: "impo[35 chars].node import CadQueryNode\n\n\nclass Myproj(Ca[206 chars]e)\n" != "impo[35 chars].node.cadquery import CadQueryNode\n\n\nclass [215 chars]e)\n"
      1 E   AssertionError: "cannot import name 'GizmoNode' from 'mach[100 chars].py)" != "module 'machinome.node' has no attribute [173 chars]de`."
     21 E   AssertionError: '<name>' unexpectedly found in ['AssemblyNode', 'Build123dNode', ... 'ExtraUnavailable', ...  (test_dir_offers_no_former_export, one per name)
```

Each is red for the reason its test states: the root resolves the 21 names
(the refusal, `getattr`, `hasattr`, the composed import, the table's rows,
the doors' order, the never-cached refusal, `dir`), `__all__` lists 21, the
star import binds them, five public names are not submodules and four
non-submodule helpers resolve; `pyproject.toml` declares neither `jscad` nor
`stl`; the install page names neither; the templates and the generator write
the root spelling; and G2 finds the three zones' offences. The tests that
stay green on the base are the ones that hold on both trees (the submodule
access, the moved names, the import cost of the package and of `base`, the
parameter surface, the broken-backend splice).

**A defect of the gate's own file, found by its first run and repaired before
group 3.** G2 counted `tests/test_node_root_exports_nothing.py` itself: five
expected values of the self-test (`['from machinome.node import AssemblyNode', ...]`)
were literal spellings, though the samples were in pieces. Each was spelled
in pieces too (`'from machinome.node ' 'import AssemblyNode'`); the gate's
file then holds no offence. The gate's count with the group-2 files in place:
`machinome` 6 files (8), `tests` 289 (480; the base's 291 less
`test_node_lazy_exports.py`'s 9 and `test_manager_new.py`'s 2, which 2.4 and
2.6 rewrote), docs 20 (58).

## 3. Implementation outside the root (group 3)

- 3.1 `pyproject.toml`: `jscad = []` and `stl = []` with Decision 7's two
  comments; `all` is
  `machinome[cadquery,build123d,step,molejo,brep,mesh,openscad,solid2,jscad,stl]`
  (82 columns in a TOML file; no lint reads it).
- 3.2 The templates import `from machinome.node.solid2 import Solid2Node`
  and `from machinome.node.cadquery import CadQueryNode`;
  `tests/test_core_kernel_free.py`'s `SEAMS` admits
  `machinome/manager/templates/project/root/cadquery.py` naming
  `machinome.node.cadquery`, and `machinome/node/__init__.py` moves from
  `SEAMS` (where it was admitted `KERNEL_MODULES`) to `TABLE_READERS`
  (naming none).
- 3.3 `machinome/manager/import_step.py`: `_import_line(cls)` returns
  `f'from {cls.__module__} import {cls.__name__}'`; `generate_parts` takes
  `StepNode` from `supported.load('step')`, `generate_assembly` imports
  `AssemblyNode` from `machinome.node.assembly` inside the function (the
  module's top imports nothing of the node package, as before). The command's
  module spells no node type's module; `test_core_kernel_free.py` keeps it
  among `TABLE_READERS`.

```
tests/test_kernel_extras.py tests/test_manager_new.py tests/test_import_step.py tests/test_core_kernel_free.py
71 passed, 85 subtests passed in 14.38s
```

- 3.4 Docstrings: `parameters.py`'s example block imports per module;
  `node/adapters/__init__.py` says the root exports no class either (the
  refusal message unchanged); `node/build123d.py` says `machinome.node`
  imports no node type's module; `node/supported.py`'s `classes` column is
  "the names its module defines for a project to import", which the root
  refuses naming that module and `load` names in its refusal, and its
  readers are the root's refusals, `load`'s message, the CLI and the
  snapshot, `new` and `import-step` commands.

The gate after group 3: `machinome` 1 file (1, the root's docstring),
`tests` 289 (480), docs 20 (58).

## 4. The suite and the manual repointed (group 4)

### 4.1 The script

`repoint.py <bench> --diff` after group 3 (the counts of 1.1 less what
groups 2 and 3 had done by hand: `machinome` 0, the three core files done;
`tests` 289 files, 271 in place, 2 fewer than 1.1 for `test_manager_new.py`;
`test_node_lazy_exports.py`, now `test_node_root.py`, holds no offence and
the script left it alone):

```
LISTED tests/test_external_wrapper_identity.py:260: left for a hand edit
machinome: {'files': 0, 'in place': 0, 'split': 0, 'dotted': 0, 'listed': 0}
tests: {'files': 289, 'in place': 271, 'split': 76, 'dotted': 1, 'listed': 1}
docs: {'files': 18, 'in place': 19, 'split': 11, 'dotted': 12, 'listed': 0}
HAND machinome/manager/import_step.py
HAND machinome/node/__init__.py
HAND docs/project/changelog.rst
HAND docs/project/upgrading.rst
dry run: nothing written
```

The diff (4234 lines) was reviewed: every split statement (32 hunks under
`tests/` and the docs' eleven, each one line per module in order of first
appearance at the statement's indentation, e.g.
`from machinome.node import AssemblyNode, Solid2Node, Frame` →
`from machinome.node.assembly import AssemblyNode` /
`from machinome.node.solid2 import Solid2Node` /
`from machinome.node.frames import Frame`), the one dotted address under
`tests/` (`test_openscad_node.py`'s `machinome.node.OpenScadNode`, replaced
by hand in 4.2) and every page: the twelve API directives at module
addresses, the code blocks of eight how-to and concept pages and the
tutorial's seven modules. The tutorial's `literalinclude`s were checked:
none selects lines of a module the split lengthened (`06-fit.rst`'s
`:lines: 1-13` includes `test_c06_fit.py`, which imports nothing from the
node package; the others start or end at text anchors or `:lines: 2-`).
Applied with `--apply`: 321 files changed, 831 insertions, 551 deletions
(the cycle's diff to that point). The gate after it:

```
machinome: 1 files, 1 offences   (machinome/node/__init__.py)
tests: 1 files, 2 offences       (tests/test_external_wrapper_identity.py)
docs: 2 files, 4 offences        (docs/project/changelog.rst, docs/project/upgrading.rst)
```

### 4.2 The hand edits, and why each assertion target changed

| file | before | after | reason |
|---|---|---|---|
| `test_external_wrapper_identity.py:250-262` | an f-string composing `from machinome.node import {kind}, AssemblyNode, Frame` | the loop carries each kind's module; three lines, `from machinome.node.{module_name} import {kind}`, `...assembly import AssemblyNode`, `...frames import Frame` | the script lists composed statements |
| `test_external_wrapper_identity.py:54-62` (`wrapper`) | `f'from machinome.node import {kind}\n'` | a kind → module map, `f'from machinome.node.{module} import {kind}\n'` | a composed statement neither the gate nor the script reads (design.md Decision 6); found by 5.2's run, 10 red with the root's refusal |
| `test_supported_node_types.py` `test_the_root_exports_the_same_objects` | `assertIn(name, __all__)`, the root's object `is` the module's | renamed `test_the_root_refuses_each_class_naming_its_module`: `__all__ == []`, each class's `__module__` is `machinome.node.<key>`, the root refuses it with `` `from machinome.node.<key> import <name>` `` | the root's identity becomes the refusal |
| `test_leaf_addresses.py` docstring, `LeafAddressTest` | "the root resolving the same object", `assertIs(getattr(machinome.node, name), value)`; the docstring's root spelling (repointed by the script into a false sentence, "The root's spellings (`from machinome.node.step import StepNode`) do not move") | the root refuses naming `its module, '<module>'`; the docstring says each class is imported from its module only | the root-identity test becomes the refusal; the script's in-place repoint of the docstring read for meaning and rewritten |
| `test_openscad_node.py:84-93` | `assertIs(machinome.node.openscad.OpenScadNode, OpenScadNode)` (the script's dotted repoint) | the root refuses `OpenScadNode` naming `machinome.node.openscad` | the root identity becomes the refusal |
| `test_openscad_node.py` `TheThreeDoorsTest` | `test_the_root_export_carries_the_refusal` (repointed by the script to the module import) | renamed `test_the_class_import_carries_the_refusal`; new `test_the_package_door_carries_the_refusal`, `from machinome.node import solid2` carrying R2 | the doors of the `openscad-node` delta: the module import however spelled; the root is no door |
| `test_motion_package.py:136` | `test_a_node_class_is_still_a_node_export` | `test_a_node_class_is_imported_from_its_module`: imported from `machinome.node.assembly`, and the root refuses it naming that module | the `ports` delta's renamed scenario |
| `test_markings.py:476` `PublicModuleTest` | the four names in `__all__`, the root's objects `is` the module's | `test_the_names_are_refused_at_the_node_root`: not in `__all__`, classes of `machinome.node.markings`, refused with `` `from machinome.node.markings import <name>` `` | the `markings` delta |
| `test_leaf_capability_set.py:144` | walks `machinome.node.__all__` | walks `AbstractBaseNode`'s subclasses after importing the core's leaf bases and internal nodes and each table row's module through `supported.load` (an absent node type skipped) | `__all__` is empty and would test nothing |
| `test_leaf_contract_recipe.py` `test_no_recipe_records_what_the_tree_recorded_before` | each record's `digest` equal to `tests/data/leaf_contract_golden.json`'s | each record's `digest` equal to the node's plain source digest (`currency.source_digest` over the artifact's tracked sources, no recipe folded), computed in the same run; the key set still the golden's | the orchestrator's ruling (b), below |

**A second reader of Decision 9's expected difference.** 4.4's suite found
`tests/test_leaf_contract_recipe.py` red, five subtests:

```
SUBFAILED(fixture='solid2_node', artifact='.scad') tests/test_leaf_contract_recipe.py::SourceRecipeTest::test_no_recipe_records_what_the_tree_recorded_before
SUBFAILED(fixture='solid2_node', artifact='.stl') tests/test_leaf_contract_recipe.py::SourceRecipeTest::test_no_recipe_records_what_the_tree_recorded_before
SUBFAILED(fixture='exact_leaf_with_marking', artifact='.marking-digits.stl') tests/test_leaf_contract_recipe.py::SourceRecipeTest::test_no_recipe_records_what_the_tree_recorded_before
SUBFAILED(fixture='exact_leaf_with_marking', artifact='.brep') tests/test_leaf_contract_recipe.py::SourceRecipeTest::test_no_recipe_records_what_the_tree_recorded_before
SUBFAILED(fixture='exact_leaf_with_marking', artifact='.stl') tests/test_leaf_contract_recipe.py::SourceRecipeTest::test_no_recipe_records_what_the_tree_recorded_before
```

with these reasons, in that order:

```
E                   AssertionError: 'a40f7418a779df175baa38217e6a0e5d44b75cc6bbfc21ec847b1e6f8859085f' != '125e8ae977ba70d095d5c3fc6a66872579264eec7a95cd9d28b7d5bc9d1a9732'
E                   AssertionError: 'a40f7418a779df175baa38217e6a0e5d44b75cc6bbfc21ec847b1e6f8859085f' != '125e8ae977ba70d095d5c3fc6a66872579264eec7a95cd9d28b7d5bc9d1a9732'
E                   AssertionError: 'be348abd17026a96b8f084c479c076b1069c4a97c41169c9906dbcd06dca02e5' != '879a2091d9b5f30c04de382a80a9c0090c2477db699b03e0eb28fb12c8472b09'
E                   AssertionError: '6b57128d4c8ce944caa511db5a27a4acbe461567b017d9b943348f6346e754c6' != 'f5793c6b461752fe471b8edb411d4682c3e4e5b84135e006beb22e46f07bbcaf'
E                   AssertionError: '6b57128d4c8ce944caa511db5a27a4acbe461567b017d9b943348f6346e754c6' != 'f5793c6b461752fe471b8edb411d4682c3e4e5b84135e006beb22e46f07bbcaf'
```

The test builds two of the golden's fixtures (`leaf_contract_project.parts.Washer`,
`markings_project.dial.Dial`) with no recipe and compared each record's
source digest with the golden JSON's, recorded on the tree before
`source_recipe`; the repoint moved those fixtures' import lines, so it is the
digest difference Decision 9 expects, reached through a pytest test the
design did not list. Reported to the orchestrator with three options
((a) read `ROOT_CLEANUP_EXPECTED`, which would leave the test pinning nothing;
(b) keep its intent with the plain source digest of the same run; (c)
re-record, forbidden). Ruling (5 October 2026): (b). After it the test
reads the golden only for the artifact set and compares each `digest` with
`currency.source_digest(<the artifact's tracked sources>, node._project_root,
node.scope)`, the digest `_with_recipe` returns unchanged when no recipe is
declared; its sibling `test_a_recipe_reaches_every_artifact` still proves a
recipe moves every digest and fingerprint:

```
tests/test_leaf_contract_recipe.py
2 passed, 4 warnings, 14 subtests passed in 3.40s
```

design.md's Decision 9 gains one sentence naming the second reader. The
golden JSON is not re-recorded.

### 4.3 The leaf-contract golden's expected table

`tests/leaf_contract_golden.py` gains `ROOT_CLEANUP_EXPECTED = ('digest',)`,
in the shape of `mesh_engine_golden.py`'s `BREP_MESH_EXPECTED`: under
`--check` a value whose flattened key ends `.digest`, a string on both
sides, is printed `EXPECTED:` and counted as expected; every other
difference is `DIFFERS:` and fails the check; the summary line gains
`%d expected (root-cleanup: source digests)`. The JSON is not re-recorded.
The orchestrator's leg (9.2) runs it.

### 4.4 The suite after group 4, before the root

```
151 failed, 4587 passed, 4 skipped, 55 warnings, 6340 subtests passed in 659.23s (0:10:59)
```

The reds, per test (subtests counted):

```
      2 tests/test_docs_structure.py::KernelExtrasTest::test_the_installation_page_names_every_kernel_extra
      9 tests/test_leaf_addresses.py::LeafAddressTest::test_every_leaf_is_defined_at_its_module
      5 tests/test_leaf_contract_recipe.py::SourceRecipeTest::test_no_recipe_records_what_the_tree_recorded_before
      4 tests/test_markings.py::PublicModuleTest::test_the_names_are_refused_at_the_node_root
      1 tests/test_motion_package.py::OldPathRefusedTest::test_a_node_class_is_imported_from_its_module
      1 tests/test_node_root.py::NodePackageBrokenBackend::test_the_root_refuses_a_class_before_the_module_refuses_its_kernel
      1 tests/test_node_root.py::NodePackageImportCost::test_a_refused_name_imports_no_node_type
      1 tests/test_node_root.py::NodePackageRefusals::test_a_refused_name_is_never_cached
      1 tests/test_node_root.py::NodePackageRefusals::test_all_is_empty
     21 tests/test_node_root.py::NodePackageRefusals::test_dir_offers_no_former_export
     21 tests/test_node_root.py::NodePackageRefusals::test_every_former_export_is_refused_naming_its_module
      1 tests/test_node_root.py::NodePackageRefusals::test_star_import_binds_nothing
      1 tests/test_node_root_exports_nothing.py::NothingSpellsTheRootTest::test_no_file_of_the_three_zones_spells_a_former_root_name
      1 tests/test_node_root_exports_nothing.py::TheRootResolvesNothingTest::test_a_row_added_to_the_table_is_refused_naming_its_module
      4 tests/test_node_root_exports_nothing.py::TheRootResolvesNothingTest::test_another_name_is_a_missing_attribute
     21 tests/test_node_root_exports_nothing.py::TheRootResolvesNothingTest::test_each_former_name_is_refused_as_an_attribute
     21 tests/test_node_root_exports_nothing.py::TheRootResolvesNothingTest::test_each_former_name_is_refused_at_the_import_line
      9 tests/test_node_root_exports_nothing.py::TheRootResolvesNothingTest::test_every_class_of_the_table_is_refused_naming_its_row
      1 tests/test_node_root_exports_nothing.py::TheRootResolvesNothingTest::test_every_public_name_of_the_namespace_is_a_submodule
     21 tests/test_node_root_exports_nothing.py::TheRootResolvesNothingTest::test_hasattr_raises_the_refusal
      1 tests/test_node_root_exports_nothing.py::TheRootResolvesNothingTest::test_the_root_lists_nothing
      1 tests/test_node_root_exports_nothing.py::TheRootResolvesNothingTest::test_the_star_import_binds_nothing
      1 tests/test_openscad_node.py::ThePackageTest::test_the_node_type_is_defined_at_its_address
      1 tests/test_supported_node_types.py::TheTableTest::test_the_root_refuses_each_class_naming_its_module
```

All of them the root still resolving the names (2.1's G1, 2.6, and 4.2's
root-subject tests, which group 5 turns green), G2 for what the script
leaves (the root's docstring, the wrapper test's listed line, the changelog
and the upgrading page), the install page (6.3) — and the recipe test,
above. Nothing else was red: every one of the 289 repointed test files
imports and passes against the root that still resolves the names.

## 5. The root (group 5)

`machinome/node/__init__.py` rewritten (Decisions 1-3): no `_EXPORTS`; no
eager `from .base import StlRenderStart` or `from .supported import
NODE_TYPES`; `_DEFINED_IN`, the core's twelve, beside `_MOVED`;
`_defined_in(name)` reads `_DEFINED_IN`, then (a dunder name excepted) the
table, `{cls: key for key, node_type in NODE_TYPES.items() for cls in
node_type.classes}.get(name)`, importing `supported` on that first lookup;
`__getattr__` refuses `_MOVED`, then the former names with Decision 3's
f-string, then resolves a submodule, else `AttributeError`; `__all__ = []`;
`import_module`, `find_spec` and `ExtraUnavailable` bound as
`_import_module`, `_find_spec`, `_ExtraUnavailable`; `_namespace_portions`,
`_load`, `_submodule` kept; `__dir__` is `sorted(globals())` (the `__all__`
union has nothing to add). The docstring says what the root is (a package
path, refusals and submodules), why it exports nothing, the refusals and
the submodule doors.

*A reading of Decision 1 recorded:* the table is derived on every refused
lookup rather than once, so a row present when a name is asked for is
refused naming its module (the gate's patched-row test); the derivation is a
nine-entry comprehension on an error path. No refusal is cached in the
namespace (`test_a_refused_name_is_never_cached`).

Task 5.2, together with every test 4.2 edited:

```
tests/test_node_root_exports_nothing.py tests/test_node_root.py tests/test_no_class_name_recognition.py tests/test_core_names_no_scad.py tests/test_core_names_no_split_words.py tests/test_core_kernel_free.py tests/test_cli_lazy_imports.py tests/test_motion_package.py tests/test_leaf_addresses.py tests/test_supported_node_types.py tests/test_openscad_node.py tests/test_markings.py tests/test_leaf_capability_set.py tests/test_external_wrapper_identity.py tests/test_time_base.py
1 failed, 353 passed, 5 warnings, 642 subtests passed in 42.06s
```

The one red is G2, for the changelog and the upgrading page (group 6). The
first run of the same set had ten red in `test_external_wrapper_identity.py`,
each with the root's refusal (`ImportError: module 'machinome.node' has no
attribute 'OpenScadNode': the root of machinome.node exports nothing, ...`),
from its `wrapper` helper's composed import (4.2's table).

## 6. Docs (group 6)

- 6.1 `docs/reference/api.rst`: the Nodes section says each node class is
  imported from its module, the address beside it below, and the root of
  `machinome.node` exports nothing; the frames section says a frame is
  imported from `machinome.node.frames`; the twelve directives at module
  addresses (4.1).
- 6.2 `docs/concepts/values.rst` and `docs/tutorial/03-dimensions.rst`: node
  classes come from their modules under `machinome.node`.
- 6.3 `docs/start/install.rst`: rows for `machinome[jscad]` and
  `machinome[stl]` (each installs nothing, with why), `all` installing every
  extra above, the sentence on `JScadNode` and `StlNode` rewritten (the
  extras exist so every node type has the extra of its name), and the
  refusal's sentence names the module import every `CadQueryNode` part makes.
- 6.4 `docs/howto/backends.rst`: the node-type table gains "Imported from"
  and its "Needs" column the extras, nine classes of eight node types, the
  OCCT classes' "nothing" corrected to their extras; a sentence after it.
- 6.5 `docs/project/upgrading.rst`: "Import every name from its module
  (unreleased)": the root exports nothing, nothing aliases, the refusal's
  text for `AssemblyNode`, the 21 names mapped name → module (no root
  address), the submodules and the star import, the generated source, and
  that each rewritten part rebuilds once to the same bytes while the kept
  verdicts recompute once; "Update port imports" imports per module.
- 6.6 `docs/project/changelog.rst`, Unreleased: this cycle's bullet first
  (ADR-181, the two BREAKING notes); `lean-install`'s bullet revised in place
  ("each class imported from its module (the root of `machinome.node`
  exports nothing; see the first entry)" for "The root spellings ... are
  unchanged", and the refusal "the same through
  `from machinome.node.cadquery import CadQueryNode`"); and, beyond
  Decision 10's two, `openscad-out`'s bullet's "for the node root's
  exports" read "for the node root's refusals" (unreleased, and false after
  this change).
- 6.7 `docs/architecture.md`: the table's `classes` column; a paragraph
  "The node root exports nothing" (the one address, what the root is, the two
  sources of its refusals, ADR-166's reading, `_MOVED` and the adapters
  package, the submodule doors, the generated source); the extras sentence
  gains `[jscad]` and `[stl]`; the three doors are the module's import
  however spelled, `load(key)` and the CLI command, the root's refusal being
  no door; and, beyond the lines task 6.7 names, the CLI paragraph's "the
  node and simulation packages resolve their exports on first access" now
  says the node package imports no backend and exports nothing. ADR-181 is
  cited ahead of its record (task 10.1).
- 6.8 The gate: `gate-prototype.py <bench> --files`:

```
machinome: 0 files, 0 offences
tests: 0 files, 0 offences
docs: 0 files, 0 offences
```

```
tests/test_docs_structure.py tests/test_node_root_exports_nothing.py tests/test_docs_*.py
46 passed, 814 subtests passed in 3.56s
```

## 7. The campaign plan (group 7)

`workflow/ongoing/lean-core.md`: item 3 of "The next phase" gains
"Implemented, awaiting validation" with the branch, the planning commit,
task 1.2's counts, the suite's count, the evidence path and the three
follow-ups outside the framework (the studio's two skills, seven lines;
machinome-mechanics' four files; the workspace's
`scripts/load-projects.d/root-cleanup.toml`); "State of the campaign" opens
with "Layer 1 complete, once recorded": layer 1 is complete once the
orchestrator's validation legs and integration are recorded. Marked done
by the records (group 10), not here.

## 8. The whole suite, lint, validation (group 8)

The whole suite, alone (`python -m pytest -q tests`, task 8.1), after the
same mtime touch. Its first run:

```
1 failed, 4594 passed, 4 skipped, 54 warnings, 5 errors, 6481 subtests passed in 642.19s (0:10:42)
```

The 5 errors (`tests/test_generate_parity_fixture.py`'s
`CoverageAcrossBindingsAndCasesTest` setup) and the 1 failure
(`tests/test_clocked_corpus.py::ExactnessGuardTest::test_what_pins_the_documents_own_remainder_is_not_the_parity_fixture`)
were one cause: both import `tools/generate_parity_fixture.py`, which
imports `spike/expressions/machine_model.py`, whose line
`from machinome.node import AssemblyNode, Solid2Node` met the root's refusal:

```
E           ImportError: module 'machinome.node' has no attribute 'AssemblyNode': the root of machinome.node exports nothing, and 'AssemblyNode' is imported from its module, 'machinome.node.assembly'. Write `from machinome.node.assembly import AssemblyNode`.
```

`spike/` is outside the gate's three zones and the script's, so neither the
baseline counts nor `repoint.py` saw it: a reader of the root the design did
not list. A scan of every tracked file outside the zones with the gate's
`offences` found it in `spike/expressions/machine_model.py` and
`spike/axis/axis_model.py` (2 each), in `workflow/` (records:
`warts.md` and an archived campaign quoting code as it was, and the plans'
prose) and in `openspec/` (archived changes and this change's own
artifacts); nothing under `tools/`. The two spike modules, code the suite
imports (`machine_model.py`) or a runner beside it executes
(`axis_model.py`), were split by hand into
`from machinome.node.assembly import AssemblyNode` /
`from machinome.node.solid2 import Solid2Node`; the records were left as
they are. Then:

```
tests/test_generate_parity_fixture.py tests/test_clocked_corpus.py
42 passed, 2 warnings, 157 subtests passed in 4.96s
```

and the whole suite again, alone:

```
4600 passed, 4 skipped, 55 warnings, 6487 subtests passed in 707.78s (0:11:47)
```

against the line's 4568 passed, 4 skipped at 815ceb9: 32 more, the new
tests of groups 2 and 4 (the gate's 22, the import-step, extras and doors
tests, and the reworked root module's). The gate after everything:

```
machinome: 0 files, 0 offences
tests: 0 files, 0 offences
docs: 0 files, 0 offences
```

`flake8 --max-line-length=89 machinome tests` (CI's command; its job runs
with `continue-on-error`) reports 770 findings on the bench against 839 on
the base tree (`git archive HEAD` into scratch, the same command). Compared
with line numbers removed, four lines are new and 73 base findings are gone
with the rewritten import blocks. The four: `tests/test_stl_node.py`'s
unused `FusionNode` (F401), the base's own finding at its new address
`machinome.node.fusion.FusionNode`; `tests/test_node_root.py:78` (E128), the
base's `test_node_lazy_exports.py:85` under the module's new name; and two
E128 in `tests/test_external_wrapper_identity.py`, the two lines 4.2 added to
a `self.load(...)` call whose every continuation line already carried E128
on the base. No error class is new (no F8xx, E9xx).

`openspec validate root-cleanup --strict`:

```
Change 'root-cleanup' is valid
```

## 9. Empirical validation (group 9, the orchestrator's legs)

Measured by the orchestrator on the bench at deb5244 plus this cycle's
uncommitted implementation, 5 October 2026, and handed to the paused
applier. Every leg green.

**9.1 The projects' rewrite pass, then the universe sweep.** Before this
change, the workspace's `scripts/rewrite-projects` (workspace main 76fb48c)
rewrote 56 of the 62 project repositories, 910 files, one commit per
repository on its checked-out branch; a second pass wrapped 61 `shape()`
sites in seven repositories; hand edits were committed in the clocks
(`check_models --engine`), Dum-E, Thor, the v8 engine, the Actuator,
OpenAstroMount, Voron-2 (53 files through a `cq_shape` helper; its `Printer`
model 10 passed and four edited modules 20 passed on the line) and the Curta
(130 `shape()` sites and 17 `intersect_shapes` results cast; 12 test modules
green on the line). The sweep, `scripts/load-projects` against this bench
with the ten tables (the nine earlier and this change's `moved-names.toml`
as `scripts/load-projects.d/root-cleanup.toml`), 300 s timeout:

```
62 repositories, 129 rows: 121 ok, 0 expected, 2 unexpected, 0 timeout, 6 no-model; 2 skipped
```

**Zero `expected`**: no project file the root refuses remains. The two
`unexpected` are pre-existing and not the campaign's (wall_clock_41's own
CadQuery error at `clocks/plates.py:5224`; Dum-E without
machinome-freecad). The same sweep against the line at 815ceb9, before this
change and after the pass, gave the same counts (the projects import from
the modules, which both trees define). The JSON is this change's
`load-projects.json`, archived with it.

**9.2 The goldens**, each `--check` in a fresh process on the bench:

```
brep_engine_golden         golden comparison: 7 fixtures, 0 differences
expression_type_golden     golden comparison: 17 values, 0 differences
leaf_contract_golden       golden comparison: 7 fixtures, 77 values, 0 differences, 12 expected (root-cleanup: source digests)
markings_golden            golden comparison: 18 values, 0 differences
mesh_engine_golden         golden comparison: 1095 values, 0 differences, 2 expected (design.md Decision 4), 200 renamed (brep-mesh)
scad_presentation_golden   golden comparison: 34 values, 0 differences, 9 presentation files absent as expected
```

The leaf-contract golden's twelve differences are all source-record
`digest` fields, read through `ROOT_CLEANUP_EXPECTED`; every artifact byte,
record version, `uniq_id` and flag is identical. The JSON is not
re-recorded.

**9.3 `Locks/Pin_tumbler_lock`** (main aef325a, after the pass; a fresh
build directory). `machinome build`: exit 0, its 11 `.scad` files'
SHA-256 identical to the same project built on the line at 815ceb9, like for
like. `machinome test --mesh --no-verdict-store`: 24 passed, 0 failed, 2573
verdicts, answers identical to the `brep-mesh` cycle's log, path word
`mesh`.

**9.4 The generators.** `machinome new demo` under three installs (the
finder of `tests/brep_engine_absent.py`): every extra, the template imports
`from machinome.node.solid2 import Solid2Node`, `machinome build` exit 0,
`machinome test` 2 passed; SolidPython blocked, the CadQuery template,
`import cadquery as cq` and `from machinome.node.cadquery import
CadQueryNode`; both blocked, exit 1 with R8 ("machinome new scaffolds its
first part with SolidPython or CadQuery, and neither is installed; install
one with 'pip install "machinome[solid2]"' or 'pip install
"machinome[cadquery]"'"), nothing created.
`machinome import-step "<Internal Cycloidal Actuator.stp>" --into imported`:
exit 0 in 13 s; the generated `parts.py` and `assembly.py` import
`from machinome.node.step import StepNode` and
`from machinome.node.assembly import AssemblyNode`, no root spelling.

**9.5 The extras.** `python -m build --sdist` on the bench: exit 0; `PKG-INFO`
`Provides-Extra: dev docs viewer web-snapshot mechanics brep mesh cadquery
build123d step molejo openscad solid2 jscad stl all studio`, `jscad` and
`stl` present and empty.

**9.6 The doors with SolidPython refused.** Not among the orchestrator's
reports; run by the applier after them, in throwaway processes with the
finder of `tests/brep_engine_absent.py` refusing `solid2`
(`run_python(snippet, absent=('solid2',))`), each statement in a `try`:

```
$ from machinome.node import Solid2Node
ImportError | module 'machinome.node' has no attribute 'Solid2Node': the root of machinome.node exports nothing, and 'Solid2Node' is imported from its module, 'machinome.node.solid2'. Write `from machinome.node.solid2 import Solid2Node`.
$ from machinome.node.solid2 import Solid2Node
ExtraUnavailable | machinome.node.solid2 (Solid2Node) needs solid2, which is not installed; install it with 'pip install "machinome[solid2]"'
$ from machinome.node import solid2
ExtraUnavailable | machinome.node.solid2 (Solid2Node) needs solid2, which is not installed; install it with 'pip install "machinome[solid2]"'
```

The root refuses the class name naming `machinome.node.solid2` and imports
nothing; the line it suggests, and the package door, meet the module's
refusal naming `machinome[solid2]`, unmodified. The suite pins the same
(`test_openscad_node.py`'s `TheThreeDoorsTest`, `test_node_root.py`'s
`test_the_root_refuses_a_class_before_the_module_refuses_its_kernel` for
`step`).

**9.7 The manual.** `python -m sphinx -b html -W docs <scratch>`: exit 0, no
warning or error line, every directive at its module address.

## 10. Records, specs, archive (group 10)

**10.1 ADR-181** (`docs/adrs/NODE/ADR-181-the-node-packages-root-exports-nothing.md`),
linking this archive: the refusal and its text, the two sources of the
names, the empty `__all__` and the strict reading of the namespace, `_MOVED`
and the adapters package kept, the doors, the two empty extras, the
generated source, the gate; ADR-166 read, ADR-087, 168, 177 and 180 cited.
ADR-167, ADR-169 and ADR-179 carry a status clause and an "Amendment
(2026-10-05)" section saying what ADR-181 amended in each;
`docs/adrs/README.md` indexes ADR-181 under NODE and marks the three
"amended by 181". `docs/architecture.md`, written in group 6, was read
against the record and agrees (the root's paragraph, the doors, the extras).

**10.2** `openspec validate root-cleanup --strict`: `Change 'root-cleanup'
is valid`. `openspec archive root-cleanup --yes`:

```
Totals: + 3, ~ 13, - 0, → 1
Specs updated successfully.
Change 'root-cleanup' archived as '2026-10-05-root-cleanup'.
```

The renamed requirement of `cli-startup-cost` is in place
("Requirement: Importing the node package imports no backend"; the former
title found nowhere under `openspec/specs/`). The scenario titles of
`scenario-titles.tsv`, renamed by a script that fails on a row whose old
title is missing:

```
rows 2 replaced 2 missing 0
```

`openspec validate --specs --strict`:

```
Totals: 45 passed, 0 failed (45 items)
```

What the baseline specs still spell of the root is intended: the scenarios
that state the refusal (`node-model`'s, `openscad-node`'s, `ports`',
`vet`'s and `user-documentation`'s upgrading reader), and `node-model`'s
star import, which binds nothing. Specs are outside the gate's zones.

**10.3** `evidence.md`, `moved-names.toml` (21 rows, the workspace's
`scripts/load-projects.d/root-cleanup.toml` being the orchestrator's),
`gate-prototype.py`, `repoint.py`, `scenario-titles.tsv` and the sweep's
`load-projects.json` stay in this archive. The campaign plan's entry is
marked done with this file as its evidence.

The whole suite after the archive, once, alone (10 min 45 s of wall time):

```
4600 passed, 4 skipped, 55 warnings, 6487 subtests passed in 642.81s (0:10:42)
```

**10.4** The implementation commit on the orchestrator's word, a further
commit on deb5244 (the planning commit is not amended); nothing pushed.

## Residual notes

- The briefing names `tests/exact_engine_absent.py` among the finder helpers
  "which this change renames" and asks for a residual review of the word
  `exact`: both belong to `brep-mesh` (the helpers are already
  `brep_engine_absent.py` and `mesh_engine_absent.py`; this change renames
  only `test_node_lazy_exports.py`). No word `exact` is this cycle's to
  review.
- Composed import statements (`f'from machinome.node import {name}'`) are
  outside the gate by design (Decision 6). Besides the refusal tests'
  deliberate ones, two remain in the suite, both refusal tests of the moved
  port names (`test_motion_package.py:118`, `test_time_base.py:159`), which
  stay; the one that was not (the wrapper helper) failed loudly at the root's
  refusal and was repointed.
