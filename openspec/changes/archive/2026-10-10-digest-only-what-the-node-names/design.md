## Context

### The finding

`workflow/warts.md`, "3DPrintedClocks wall clock 02 (2026-10-10, string
edits invalidate unrelated rigid geometry)". Its probe replaced only
`spec.py`'s digest with that of the file with one string clearance changed
by 0.1 mm and found all 54 rigid STL entries' source digests changed (30
from `parts.py`, 24 from `clock.py`). The orchestrator measured the cost on
10 October 2026 in the project worktree
`projects/3DPrintedClocks/WTs/string-cache` at project `2f846a8`, against
framework `main` (0.8.1), building with `measure/build_once.sh` (inodes of
every STL taken before and after; a new inode is a regenerated artifact, the
same inode with a new ctime a restamped one):

| Build | Wall | STL artifacts |
| --- | ---: | --- |
| cold, nothing built | 53.7 s | 54 written |
| warm, no edit (the floor: process start, imports, movement construction, currency checks, document) | 13.5 s | 54 untouched |
| `front_clearance` 5.0 to 4.9 on line 144 (`before-1`) | 54.2 s | every rigid part re-derived |
| `front_clearance` 4.9 to 4.8 on line 144 (`before-2`) | 54.7 s | 54 regenerated |
| the project change applied (`measurements/restructure.py`), framework `main` | 51.7 s | 54 regenerated |

### The mechanism today

- A node's tracked set is its own source and its project-local import
  closure (`machinome/node/base.py:705`, `source_closure` at
  `machinome/node/sources.py:208`). Its scope maps its own source to its
  own class name (`base.py:711`, `source_scope` at `sources.py:331`); an
  internal node unions its children's files and scopes
  (`machinome/node/internal.py:188-190` and `218-220`). Leaves whose source
  is not Python (`StlNode`, `StepNode`) union their wrapper module's
  closure into `files` with no scope entry (`machinome/node/stl.py:149`,
  `machinome/node/step.py:499`).
- `_up_to_date` (`base.py:1354`) returns current on stamp equality plus
  fingerprint equality, opening no source. Otherwise `_content_verified`
  (`base.py:1392`) compares the recorded digest with
  `_tracked_digest` (`base.py:1048`): `currency.source_digest(files, root,
  scope)` with the producer recipe folded in (`base.py:49`).
- `currency.source_digest` (`machinome/currency.py:226`) hashes a sorted
  sequence of (project-relative path, per-file digest). A file with no
  scope entry contributes the sha256 of its bytes (`_file_digest`, `:91`).
  A file with one contributes its retained text (`_scoped_digest`, `:194`):
  `_analyse` (`:134`) records, per top-level statement, the node-class span
  it defines and the identifiers and strings it mentions, and gives up
  (whole file) when the file does not parse or the interpreter names no
  node class in it (`node_classes_in`, `sources.py:347`); `_removed_spans`
  (`:168`) removes the sibling node classes the retained statements of
  that same file never name, to a fixpoint.
- The record is `<artifact>.sources`, a version 2 or 3 JSON object
  (`{"version","digest","fingerprint","recipe"?,"transient"?}`) or a legacy
  bare digest, read by `_recorded_source` (`:331`) and written by `record`
  (`:395`), which drops the old record before writing the new one.

Wall clock 02's `spec.py` is in the closure of every rigid part.
`STRING_ROUTE` (lines 138-149) is not a node class, so ADR-071 never
removes it, and line 144 is in every rigid part's digest. Even a rule that
looked across the closure would keep it: `Movement.__init__` (spec.py:199)
spells `STRING_ROUTE`, and every rigid part runs the movement.

### What the prototype measured

`measurements/reach2.py` implements the rule of Decision 1 outside the
framework (it reports, it changes no digest, and it does not act on the
dynamic-lookup flag), run from the project worktree at `2f846a8` against
framework `main`:

| Project | Node | Closure | Statements kept | `spec.py` | `STRING_ROUTE` |
| --- | --- | ---: | ---: | ---: | --- |
| as it is | `parts:Frame` | 42 files | 505 / 924 | 32 / 32 | kept: "name STRING_ROUTE from spec.py:176" (`Movement`) |
| as it is | `clock:WeightString` | 45 files | 539 / 1010 | 32 / 32 | kept |
| changed (`overlay.json`) | `parts:Frame` | 42 | 503 / 926 | 30 / 34 | dropped, with `StringGeometry`, `string_geometry`, the `WoundStringRoute` import |
| changed | `parts:Arbor`, `parts:Bearing` | 42 | 504, 503 / 926 | 30 / 34 | dropped |
| changed | `clock:BobShell`, `clock:SlidingWeightShell` | 45 | 537, 539 / 1012 | 30 / 34 | dropped |
| changed | `clock:WeightString` | 45 | 541 / 1012 | 34 / 34 | kept: "attr spec.string_geometry from clock.py:214" |
| changed | `clock:StringAssembly`, `clock:Movement`, `clock:WallClock02` | 45 | 546, 679, 701 / 1012 | 34 / 34 | kept |

`measurements/reach.py`, the first prototype, matched bare names with no
resolution and kept 728 of 1,010 statements on a `clock.py` node's
closure, where `reach2.py` keeps 539 to 541: `Movement` names three classes in the closure (`spec.py`,
`shared/movement.py`, and `clock.py`'s assembly), and a bare match reached
the cord through `clock.py`'s `Movement` assembly. Dynamic lookups appear in
kept text in `clocks/cuckoo_bits.py` and `clocks/utility.py` (`if
'show_object' not in globals():` at top level); neither closure reaches
`spec.py`.

## Goals / Non-Goals

**Goals:**

- The pilot's acceptance: with the project change applied, editing
  `front_clearance` on line 144 regenerates the cord and no rigid STL, and
  the build's wall time falls from 54.7 s to near the 13.5 s floor.
- A node's digest covers the top-level definitions its retained text names,
  in every tracked Python file, and every edit to text it retains still
  rebuilds it.
- Every uncertainty keeps more text; nothing ADR-071 retains for a reason
  other than "it is a file" is lost.
- No record written by 0.8.1 rebuilds merely because the framework changed.
- The hit path, `node.files`, the fingerprint, the sweep, publication and
  `source_recipe` folding are unchanged.

**Non-Goals:**

- A public API, declaration or configuration on nodes.
- Attribute- or value-flow analysis inside classes and functions.
- Any change to the string nodes, to another clock, to the viewer's mesh
  fetching, or to the per-process cost of constructing the movement.
- Closing the computed-`getattr` exposure.

## Decisions

### D1. The unit is the closure as one node sees it

For each node, over every tracked Python file, a top-level **definition**
that the node's **retained text** never names is left out of the digest.

- *Definitions* (removable): `ClassDef`, `FunctionDef`, `AsyncFunctionDef`;
  `Assign` whose every target is a plain name or a tuple or list of them,
  and `AnnAssign` whose target is a plain name; `Import`, and `ImportFrom`
  other than a star import. A definition binds the names it defines; an
  import binds its alias, or the first component of a dotted name.
- *Seeds:* the node's own class statement(s) in its own file, taken from
  the scope as today; an internal node's seeds are the union of its
  children's and its own, as today.
- *Always retained* (D2): every other top-level statement.
- *Mentions* of a retained statement, found by `ast.walk`: bare names,
  attribute chains (root name and attribute names), and string constants
  whole.
- *Resolution* (D3) maps each mention to definitions.
- *Fixpoint:* start from the seeds and the always-retained statements;
  retain every definition a retained statement's mentions resolve to;
  repeat until nothing is added. Only a definition nothing retained names is
  left out.

The retained text of a file is its bytes with the line spans of its
left-out statements removed (D7).

*Alternatives considered.*

- **Bare-name matching without resolution** (`measurements/reach.py`).
  Rejected on its measurement: a name defined in three closure files keeps
  all three, and on wall clock 02 `Movement` reached the cord through the
  wrong `Movement`, keeping 728 of 1,010 statements where resolution keeps
  539 to 541.
- **Attribute-flow analysis inside classes**, separating a constructor's
  string state from its gear state so the project need not change. The
  route the pilot did not take: it needs a sound model of `self` and of
  every object the constructor builds, which arbitrary Python and the
  `clocks` library do not give, and its failure would be silent. A kept
  class or function is kept whole.
- **A declaration on the node** naming its geometry inputs. Rejected as
  ADR-033 rejected per-node source declarations: it puts the burden on
  every author, fails silently when forgotten, and the brief rules out new
  public API.
- **Per-definition digests in the sidecar**, so a record could say which
  definitions it covered. A format change carrying hundreds of entries per
  artifact for no gain: the reach is recomputed from the sources anyway.

### D2. What is never left out

- Every top-level statement that is not a definition: `Expr`, `If`,
  `For`, `While`, `With`, `Try`, `AugAssign`, assignments to attributes or
  subscripts, `Assert`, `Delete`, `Global`, `Match`, an `Assign` with any
  non-name target. They run at import, and a definition nested under one
  (`try: import x / except: x = None`) is retained with it.
- A star import (`from x import *`): it binds names the text never spells.
- A decorated definition, except a decorated node class, which ADR-071
  already removes. A decorator runs code at definition time (registration
  is the common case) and the source cannot say which do.
- A definition of a dunder name (`__all__`, a module `__getattr__` or
  `__dir__`, `__path__`): the interpreter reads them without any spelling
  in project text (a star import reads `__all__`; an attribute missing on a
  module falls into its `__getattr__`). This is an addition to the brief.
- A statement that shares a line with another statement (`import os; X =
  1`): line spans could not remove one without the other.
- Comments and blank lines outside every statement, and a module
  docstring. The suite's `tests/utils.py::edit_source` marks an edit with a
  trailing comment, so every source-set test that relies on it keeps
  meaning an edit.

*Alternative considered: dropping decorated definitions too.* Rejected:
`@register`-style decorators fill registries read under another name. The
cost is real but small: wall clock 02's `movement()` is `@lru_cache`-
decorated and is therefore always retained, which retains `Movement`,
which every part names anyway.

### D3. Resolution, and the catch-all

**Bindings.** A module's import bindings are made by every import statement
in the module's text, at any depth: a top-level import, and equally one
nested in a function, a method, a class body, an `if TYPE_CHECKING:` block
or a `try`/`except ImportError` (`def f(): from .spec import X; return X *
2`, `from . import spec` inside a method). Each binds names exactly as a
top-level import would, for resolving that module's mentions: a module
binding, or a name binding followed to the tracked module's definitions;
one the system cannot follow falls to the catch-all below. Star sources are
likewise every star import in the module, top level or inside a top-level
`if` or `try`. Taking every import in the text, not only those in retained
statements, keeps the analysis a property of the file (cached on its key)
and never removes a target a retained-only table would give, except
through an attribute chain, which the shadowing rule below covers.
`source_closure` already walks nested imports (`_parse_project_imports`
uses `ast.walk`), so these files are tracked today; only resolution would
miss them. The names an import statement binds count as mentions only
when the statement is retained without having been named: when its file is
retained whole (D4, D5, D6, or a module kept whole by D4's module-`getattr`
guard), or when it is always retained (a star import, or an import nested
inside a non-definition statement such as a top-level `try` or `if`). Its
aliases carry no `ast.Name` nodes, so without this a file retained whole
would not follow its imports. An import retained because one of its names
resolved through it contributes only its text: that name was already
followed by resolution, and its other names are not mentions, so `from
.spec import X, Y` read only as `X` keeps `spec.py`'s `X` and not its `Y`
(the reviewer's F8; R1's second form pins it).

- A **bare name** resolves in its own module: every top-level definition of
  that name there (a rebound name keeps every binding), and the import
  bindings of it. A binding made by `from X import y`, with X a tracked
  module, also resolves to X's definitions of `y`, transitively, so a
  package `__init__` re-export reaches the defining module. A binding of a
  tracked submodule (`from pkg import mod`, `import pkg.mod`) is a module
  binding. A name is also looked up in every star-import source of its
  module, whether or not the module defines it: the brief said only when
  it does not, but which binding wins depends on statement order, and the
  union keeps more.
- An **attribute chain whose root is bound to a tracked module** (by any
  import in its module, as above) resolves into that module, walking
  further through submodule bindings (`clocks.types.HandType` through
  `clocks/__init__.py`), then by D3's bare-name rule in the module reached;
  attribute names past the definition fall to the catch-all. A root name
  bound to two tracked modules resolves into both. When the root name is
  also bound in that module by anything other than an import of a tracked
  module (a parameter, an assignment or loop target, a `with ... as` or
  `except ... as` name, an import of something else), the chain also falls
  to the catch-all: the same spelling may name a different object in
  another scope.
- **Every other attribute name** (`self.built.plates`,
  `movement.string_route`), **every string constant**, and **every name an
  import binds that the system cannot follow** (a relative import in a
  module whose package is unknown, an absolute import of a project module
  not in the closure) retain every top-level definition of exactly that
  name in every tracked file. This is ADR-071's catch-all for sibling node
  classes, now for all definitions: it keeps `getattr(module, 'Name')`, a
  class instantiated through `self.<name>`, a base passed through a
  variable.
- Names nothing defines (builtins, locals, parameters) resolve to nothing.

### D4. Dynamic lookups keep a file whole

A retained statement that calls `globals`, `locals`, `vars`, `dir`, `eval`,
`exec`, `__import__`, `import_module` or `getmembers` (spelled bare or as
the last attribute of a call, so `importlib.import_module` and
`inspect.getmembers` count), or reads an attribute named `__dict__`, makes
its own file and every tracked file in that file's own import closure
retained whole. `getmembers` is an addition to the brief: it enumerates a
module as `dir` does. A file retained whole retains every statement, and
every statement's mentions count.

A retained call to `getattr`, `hasattr`, `setattr` or `delattr` whose first
argument is a bare name bound to a tracked module (by any import in the
module, D3) and whose second argument is not a string literal makes that
module retained whole, together with every tracked module it star-imports,
transitively; the names its retained imports bind are followed by D3. This
is the reviewer's finding F2, taken: the first argument distinguishes
`getattr(spec, name)` in a loop, the common module-enumeration idiom, from
`getattr(self, name)` statically, so the guard costs nothing on objects. A
string-literal second argument is already a mention.

*Alternative considered: guarding every computed `getattr(obj, name)`.*
Rejected. It is ubiquitous on objects (`getattr(self, name)` runs through
every adapter and most project helpers), and a guard on it would make the
rule whole-file nearly everywhere. What remains exposed is a computed name
reaching a module that is not a bare module-bound name: `sys.modules[key]`,
`getattr(sys.modules[__name__], name)`, a module passed through a variable,
a parameter or a call's result. That is the exposure ADR-071 accepted for
sibling node classes, now for all definitions; it is stated (Soundness),
not guarded.

### D5. Files that are retained whole

- A file that does not parse, or whose module the interpreter cannot place
  (no loaded module came from it); every name it mentions resolves by the
  catch-all.
- A node's own file in which a seed name is not the name of a top-level
  class statement: the class was made by a factory, nested, or renamed, and
  its real source cannot be located by name. An addition to the brief:
  without it a factory-made node would seed nothing and lose its own code.
- Every tracked file of a node with no Python seed (D6).
- Every non-Python source, as today.

### D6. Files a node tracks beyond its own closure

The brief assumes every tracked file is reached through imports from the
node's own source. Two existing cases break that: `StlNode` and `StepNode`
union their wrapper module's closure into `files` with an empty scope, and
the API (`docs/reference/api.rst`, `files`) lets a subclass add files after
the base constructor. A file added that way may be read at run time, not
named. So:

- the node keeps, beside `scope`, the files its own source reaches (its
  source closure as computed at construction, before a subclass adds any);
- a tracked Python file outside that set is retained whole, and its
  statements seed the fixpoint;
- a node with an empty scope (a non-Python source) has no seeds, and every
  tracked file is retained whole, which is today's digest for it;
- an internal node unions its children's whole-file sets beside their
  scopes, so a seedless child's files stay whole in every ancestor's digest
  even where the ancestor's own closure also reaches them.

Read from the code: `self.src` is `realpath(self.get_source_file())`
(`base.py:653`), and `StlNode.get_source_file` and `StepNode.get_source_file`
return the asset (`stl.py:151`, `step.py:501`), so `source_scope` returns
an empty scope for both and they digest every file whole, exactly today's
value. The applier verifies this on the suite's fixtures and records it
(tasks.md 3.5), and G14 pins the equality.

### D7. Line spans, and a digest that leaves nothing out

A left-out statement removes the lines from its first line (its first
decorator, if any) to its `end_lineno`, on the lines `bytes.splitlines`
gives, as ADR-071 does. A file that leaves nothing out contributes exactly
`_file_digest`'s value, the sha256 of its bytes; a file that leaves some
statements out contributes the sha256 of the concatenation of its other
lines, exactly as ADR-071's `_scoped_digest` builds it. The entry sequence,
its sorting and its encoding are unchanged, so a node whose closure leaves
nothing out has a digest byte-identical to 0.8.1's, and a node whose
closure leaves out exactly the spans ADR-071 left out has ADR-071's digest.

### D8. The record says which rule wrote it

A record written under this rule is version 4: the version 3 fields
(`digest`, `fingerprint`, optional `recipe`, optional `transient`), with the
digest taken under this rule. `record` writes version 4 whenever it is
given a fingerprint; the digest-only legacy form stays for a caller that
gives none. The reader accepts versions 2, 3 and the legacy form as *the
previous rule*, version 4 as *the current rule*, and anything else as
certifying nothing. 0.8.1's reader accepts only 2 and 3, so it refuses a
version 4 record and rebuilds, the same safe rollback ADR-081 recorded.

*Alternatives considered.*

- **A `rule` field inside version 3.** An older reader would accept the
  record and compare its own digest with the new one. That is safe only by
  an argument about which retained bytes can coincide, where a refused
  version is safe by construction.
- **No marker**, letting every record whose digest differs rebuild once,
  as ADR-071 let multi-node files. Rejected: under this rule most nodes of
  a real project leave something out (on wall clock 02 every part does), so
  every project would rebuild whole on its first edit or branch switch
  after upgrading, against ADR-071's driver.
- **A one-time migration rebuild**: the same objection.

### D9. Migration: the previous rule is ADR-071's code, kept

On a fingerprint or stamp miss, `_content_verified` reads the record's
rule. A current-rule record is compared with the current digest. A
previous-rule record is compared with the previous digest of the sources
now present, with the recipe folded in the same way, computed by ADR-071's
`_analysis`, `_removed_spans` and `_scoped_digest`, kept unchanged. When it
matches, and every statement the previous rule left out is also left out by
the current rule, the artifact is restamped and re-recorded as version 4
with the current digest and fingerprint; otherwise it is rebuilt.

The brief proposed the previous rule as the new algorithm with "removable"
restricted to node classes of the node's own file. That is not ADR-071's
rule: ADR-071 counts only identifiers and strings of the node's own file,
where the new fixpoint counts attribute names and every closure file, so
the parameterised rule would keep a sibling ADR-071 removed whenever
another file or an attribute names it, and that node's 0.8.1 record would
fail to verify and rebuild. Keeping ADR-071's three functions as the
verifier reproduces 0.8.1's digest exactly, and they are already pinned by
`tests/test_node_scoped_currency.py`.

*Soundness of the migration.* A previous-rule match proves the text the
previous rule retains is unchanged since the record. The extra condition
makes the current rule's retained text a part of it: the previous rule
leaves out only sibling node classes, and when the current rule also
leaves each of them out, the current fixpoint starts from the same seeds and
always-retained statements over identical text, never reaches a
left-out sibling, and so retains identical text in both states. Without the
condition a sibling named from another closure file (D10's latent ADR-071
miss) would be carried forward on 0.8.1's word; with it, that record
rebuilds once. A settled artifact whose stamp and fingerprint match keeps
its previous-rule record on the metadata-only path, unread, until its
sources next change; the first change after upgrading is therefore judged
by the previous rule, and an edit the previous rule sees rebuilds once more
under it.

### D10. A sibling named from elsewhere

ADR-071's fixpoint reads only the node's own file. A sibling node class
named from another closure file (a helper doing `parts.B.HINT`, or
`getattr(parts, 'B')`) is removed today, so editing `B` leaves the other
nodes of `parts.py` current although a function they call reads it. The
new fixpoint counts every closure file, so `B` is retained. This is a
correction the rule gives for free; a red test pins it.

### D11. Caches and cost

- The per-file analysis, `currency._reach_analysis(path, census=None)`
  (statement spans, definitions, bindings from every import in the file,
  shadowed names, mentions, dynamic flags, module-`getattr` targets, star
  sources), is cached on the file key in `_reach_analyses`, as `_analyses`
  is, and reads through the census when one is active
  (`source-closure-cost`). Resolving bindings consults the loaded-module
  index, as `_import_cache` already does on the same key.
- The fixpoint, `currency._retained(files, root, scope, whole, census)`,
  returns the left-out statement indices per file and is cached on (the
  file keys of the node's tracked Python files, its seeds, its whole-file
  set).
- The retained-text digest, `currency._retained_digest(path, left_out,
  census)`, is cached on (file key, frozenset of left-out statement
  indices).
- The previous rule's digest, `currency.previous_source_digest(files,
  root, scope, census)`, is today's `source_digest` body under a new name,
  over ADR-071's unchanged `_analysis`, `_removed_spans` and
  `_scoped_digest`; `currency.previous_rule_carries(files, root, scope,
  whole, census)` answers D9's condition. These names are the plan; the
  applier may rename them only by recording the rename in evidence and
  the tests that patch them (G12).
- All of it runs only on a stamp or fingerprint miss. The cost is one AST
  per tracked Python file per process and one fixpoint per distinct seed
  set; the hit path still stats and reads one sidecar.

### D12. The project-side change is the project's

The framework rule cannot separate rigid geometry from the cord while
every rigid part runs a constructor that stores `STRING_ROUTE`. The
project change (`measurements/restructure.py`): `Movement.__init__` drops
`self.string_route = STRING_ROUTE`; the seven string properties move to
`StringGeometry(movement, route)`, defined below `Movement`, and
`string_geometry(movement)` returns one routed by `STRING_ROUTE`;
`shared/motion.py`'s `WoundWeightString` and `WoundWeightStringAssembly`
read the cord through a `string_geometry` property defaulting to
`self.built`; `clock.py`'s `WeightString` and `StringAssembly` override it
with `spec.string_geometry(self.built)`. The file layout does not change,
line 144 does not move, and ADR-071's refusal to make layout serve the
cache is not touched: what changes is what the movement object holds. The
framework rule is correct without it; without it the clock gains nothing.

## Soundness and exposures

The rule leaves out a definition only when no retained text names it by
identifier, by resolved attribute, by any attribute name, or by any string,
and when no file in which a dynamic lookup runs could reach it. Python
reaches a top-level definition only by executing a reference to its name;
every reference the source spells is a mention, so a definition left out
is one no retained code refers to by a spelled name. Where that can still
be wrong:

- **A definition statement whose execution has a side effect another
  node's geometry reads, through a name that node never spells:** `_ =
  register(Gear)`, a class whose metaclass or `__init_subclass__` fills a
  registry read under a different key, an assignment whose call mutates
  module state. Decorated definitions are retained (D2); these are not.
- **A computed name reaching a module the text does not bind by name:**
  `sys.modules[key]`, `getattr(sys.modules[__name__], name)`, or a module
  passed through a variable, a parameter or a call, read with a name
  assembled at run time. A computed `getattr` on a module-bound name is
  guarded (D4).

Both are the exposure ADR-071 accepted for sibling node classes ("a
registry filled by a decorator and read under a different key, a name
computed at runtime"), and ADR-033's boundary for `importlib` and
computed names; this change extends it from node classes to all
definitions. The direction of every other uncertainty (D2 to D6) is
toward retaining more.

## Risks / Trade-offs

- [The exposure above now covers constants, functions and imports, which
  are far more common than sibling node classes] → it requires a name
  never spelled; the dynamic-lookup rule and the module-`getattr` guard
  cover the module-enumerating spellings; the manual states the boundary
  beside ADR-033's.
- [A project that edits a definition its nodes do not name sees fewer
  rebuilds, by design; a project that relied on a whole-file rebuild to
  pick up a run-time read sees a stale artifact] → that read is already
  outside ADR-033's set; stated in the manual.
- [The first edit after upgrading is judged by the previous rule] → the
  pilot's first cord edit after this lands still rebuilds all 54 parts
  once, and every later one does not; the changelog bullet and the warts
  note say so, and the caller measurement records both (tasks.md 8.1 a'
  and b).
- [The previous-rule verifier is a second code path that lives on] → it is
  ADR-071's existing, tested code, reached only by records 0.8.1 wrote;
  removing it later is a separate decision.
- [A flexible leaf's state identity carries its digest] → it moves once for
  a leaf whose closure leaves something out, and stored test verdicts on
  that leaf run once more.
- [Restamped artifacts still change observation: the viewer refetches a
  restamped mesh, and other per-artifact records keyed on observation see a
  new stamp] → out of scope; the caller measurement reports what the build
  costs, not the viewer.
- [`tests/leaf_contract_golden.py --check` records `record_version`] → it
  would report 4 where the golden holds 2 or 3. Following the script's own
  convention (`ROOT_CLEANUP_EXPECTED`), this change adds a table naming
  itself that counts `record_version` moving from 2 or 3 to 4 as expected,
  and `--check` must report zero differences; a digest whose current value
  differs from the baseline run is a stop.

## Proof plan

New file `tests/test_reach_scoped_currency.py`, built on
`tests.test_content_verified_currency.ScratchProjectTest` as
`tests/test_node_scoped_currency.py` is: a scratch package with
`spec.py` (constants `X`, `Y`, a function, a non-node class, an import
nothing uses), `parts.py` with leaves `A` (reads `spec.X` through `from .
import spec`) and `B` (reads `spec.Y`, the function and the class), and an
assembly; each leaf records its `render()` in the trace log. Red tests, each seen red on the unchanged
tree for the reason given:

- **R1** `test_an_edit_to_a_definition_one_node_never_names_spares_it`:
  editing `Y` re-derives `B` and not `A`; editing `X` re-derives `A` and
  not `B`; editing the function or the non-node class, each read by `B`
  alone, re-derives `B` alone; changing the import nothing names
  re-derives neither (subtests, a fresh build each). A second form of the
  fixture imports names rather than the module: `from .spec import X, Y`
  at the top of the leaves' module, `A` reads bare `X`, `B` reads bare `Y`;
  editing `Y` re-derives `B` alone, editing `X` re-derives `A` alone. Red:
  `spec.py` is digested whole, so `renders()` is `['A', 'B']` where one
  leaf or none is expected.
- **R2** `tests/test_node_scoped_currency.py`:
  `test_editing_shared_code_re_derives_every_node_in_the_file` is replaced
  by `test_editing_code_one_node_names_re_derives_that_node_alone`
  (`PIN_RADIUS` and `pin_height` each edited re-derive `Pin` alone) and
  `test_editing_code_every_node_names_re_derives_every_node` (`from .
  import trace` rewritten as `from . import trace as trace` re-derives
  both). Red: the first gets `['Block', 'Pin']`, since module-level code is
  never removed today. The old test pins the behaviour this change
  removes; it is the one existing test whose expectation changes.
- **R3** `test_a_sibling_named_from_another_file_is_followed`: `parts.py`
  holds `A` and `B`; `helper.py`, imported by `parts.py`, has a function
  `A` calls that reads `parts.B.HINT` through a function-level `from .
  import parts`; editing `B`'s `HINT` re-derives `A`. Under D3 the nested
  import binds `parts` as a module in `helper.py`, so the chain resolves
  into `parts.py`'s `B` (it no longer rests on the attribute catch-all,
  which G13 does not rely on either). Red: ADR-071 reads only `parts.py`'s
  text, removes `B` from `A`'s digest, and `renders()` is `['B']`.
- **R4** `test_a_previous_rule_record_is_verified_once_and_re_recorded`:
  after a build, `A`'s STL and BREP records are replaced by version 2
  records holding the previous rule's digest and the current fingerprint.
  The test computes that digest itself, with one helper shared with R5:
  every tracked file by its bytes, except `parts.py`, whose entry is the
  sha256 of its lines without `B`'s class statement. Timestamps are
  rewritten; the build renders nothing, and both records read version 4
  with `A.source_digest`; then `Y` is edited and the build renders
  `['B']`. Red: the record is rewritten as version 2, and the later edit
  renders `['A', 'B']`.
- **R5** `test_a_previous_rule_record_is_not_carried_past_a_sibling_it_left_out`:
  on R3's fixture, `A`'s records are replaced by version 2 records holding
  the previous rule's digest (R4's helper) and the current fingerprint;
  timestamps are rewritten; `A` is re-derived. Red: today that digest is
  `A`'s own, so nothing renders.

Guards, green today and green after (the rule must not lose them):

- **G1** a definition reached by `from .spec import Z`, through a package
  `__init__` re-export (`from .lib import W`, `lib/__init__.py` doing
  `from .defs import W`), and through a star import (`from .stars import
  *` then `V`): each edit re-derives its node.
- **G2** a definition named only by a string (`getattr(spec, 'S')`) is
  kept: editing `S` re-derives the node.
- **G3** a non-definition statement keeps what it names for every node:
  `spec.py` holds `ALL = []` and `ALL.append(K)`; editing `K` re-derives
  `A` and `B`, neither of which names `K`.
- **G4** a decorated non-node definition is never left out:
  `@functools.lru_cache def helper(): return H`, named by no node; editing
  `H` re-derives every node whose closure holds `spec.py`.
- **G5** `vars(spec)` in a function `A` calls keeps `spec.py` whole:
  editing `Y` re-derives `A`.
- **G16** a file retained whole follows the names its imports bind:
  `spec.py` holds `from .defs import K`, and no text spells `K`; `A` calls
  a function doing `getattr(spec, name)` with a computed `name`, which keeps
  `spec.py` whole (D4's module-`getattr` guard) but not `defs.py`; editing
  `K` in `defs.py` re-derives `A`. The module-`getattr` case is used rather
  than G5's `vars(spec)` because D4 keeps the import closure of the file
  holding `vars` whole, so `defs.py` would be whole there anyway and the
  import-follow rule would go unexercised; G5 also asserts the `K` edit
  re-derives `A`, as a second witness of the result.
- **G6** a node class made by a factory (`Gear = make_gear(20)`, the class
  named inside `make_gear`) keeps its file whole: editing `make_gear`
  re-derives it.
- **G7** `__all__` in a star-imported module is never left out: removing a
  name from it changes the digest of a node importing by star.
- **G8** a definition sharing a line with a retained one (`import os; Y2 =
  1`) is kept.
- **G9** a Python file a leaf adds to `files` after construction, naming
  nothing the leaf names, is digested whole: editing a constant in it
  changes the leaf's digest.
- **G10** a node whose closure leaves nothing out has a digest equal to
  the whole-file digest (the existing `SingleClassFileTest`, plus one node
  of the new fixture that names everything).
- **G11** digesting every node of the fixture analyses each tracked Python
  file at most once per process (the analysis function patched to count
  per path).
- **G12** `test_the_settled_path_reads_no_source_content` extended to patch
  `currency._reach_analysis` and `currency._retained` (D11) beside
  `_analysis`, and still pass.
- **G13** imports nested in a retained statement bind (D3): `spec.py`
  holds `X2`; a function `A` calls does `from .spec import X2` and reads
  bare `X2`, and a method of another leaf does `from . import spec` and
  reads `spec.X2`; neither leaf's module imports `spec` at top level, and
  no other text spells `X2`. Editing `X2` re-derives both. Also a `try:
  from .defs import K` / `except ImportError: K = None` at top level and an
  `if TYPE_CHECKING:` import, each read by bare name, each re-deriving its
  node when the definition is edited.
- **G14** a leaf whose source is not Python digests as today (D6): the
  `StlNode` of `tests/stl_project/parts.py` and the `StepNode` of
  `tests/step_project/parts.py` have an empty `scope`, and each one's
  `source_digest` equals the whole-file digest of its `node.files` (every
  file by its bytes, in `whole_file_digest`'s encoding), byte for byte.
- **G15** a computed module `getattr` keeps the module whole (D4):
  `for name in NAMES: total += getattr(spec, name)` in a function `A`
  calls, with `NAMES` a tuple of strings that does not spell `Y`; editing
  `Y` re-derives `A`. Its companion, `getattr(self, name)` with a computed
  name, does not retain `spec` whole: editing `Y` leaves `A` current when
  nothing else names it. The companion is red on the unchanged tree for
  R1's reason (`spec.py` digested whole) and is run with the red tests.
- Every other test in `tests/test_content_verified_currency.py`,
  `tests/test_node_scoped_currency.py`, `tests/test_source_set.py`,
  `tests/test_source_census.py`, `tests/test_generation_dedup.py`,
  `tests/test_leaf_contract_recipe.py`, `tests/test_brep_currency.py` and
  `tests/test_flexible_verdict_identity.py` unchanged and green.

## Caller validation

The orchestrator's, in the project worktree with the project change
applied and its records written by framework `main`, building with the
bench on `PYTHONPATH` through `measure/build_once.sh`, one run at a time
(tasks.md section 8): (a) a timestamp-only touch of `spec.py`: 0
regenerated, every rigid record re-recorded as version 4 (the migration
without an edit); (a') on a fresh copy of the 0.8.1 build directory, the
first line 144 edit after switching to the bench: 54 regenerated under the
previous rule and re-recorded as version 4 (the honest first edit after
upgrading); (b) the second line 144 edit: no rigid STL regenerated, the
cord re-evaluated, wall time near the floor, compared with `before-2`'s
54.7 s; (c) a warm build with no edit: the floor under the bench; (d)
`PLATE_THICK` edited: the parts that read it regenerate; (e) `machinome
test wall_clock_02 --mesh` compared test for test with the clean control
at `2f846a8` (15 passed, 7 failed on both today; the seven are recorded
pendulum-hardware debt). The exact-engine test run is the orchestrator's
own.

## Open Questions

- Whether the floor itself (13.5 s, most of it movement construction in a
  fresh builder process) should be the next finding: the wart records it
  and this cycle does not change it.

## Revision after apply evidence (10 October 2026, the orchestrator's ruling)

The apply implemented D1-D9 as written and passed its own proof plan, the
focused set, and the full suite. The caller measurement
(`projects/3DPrintedClocks/WTs/string-cache`, project change at `b980d59`,
bench on `PYTHONPATH`, `measure/build_once.sh`) confirmed the acceptance --
same-load pair, main 55.6 s with all 54 rigid parts re-derived against the
bench 21.4 s with none, 54 restamped -- and the migration: a timestamp-only
touch re-recorded 54 version-2 records as version 4 with 53 regenerated and
1 restamped, and a fresh copy's first line-144 edit after switching to the
bench regenerated all 54 under the previous rule before later edits were
spared, exactly as D9 states. Review of the implementation against that
evidence found five defects in the mechanism itself, all within D1-D9's own
terms -- none asks for a different rule.

**I1 (an always-retained statement's own nested import did not bind).** The
rule says an import nested inside a statement that is not a definition --
a top-level `if` or `try` -- names what its bound names resolve to simply
by being always retained, with no need for anything else to spell them
(D3). The apply's mention-collection walked a statement's `Name`,
`Attribute`, `Constant` and `Call` nodes, which never includes an
`Import`/`ImportFrom` alias (aliases are plain strings, not `ast.Name`
nodes), so a top-level `try: from .defs import K` whose `except` arm did
not also spell `K` (`except ImportError: pass`, rather than `except
ImportError: K = None`) bound nothing a retained statement could be said
to name. Fixed: every statement additionally collects the names any
`Import`/`ImportFrom` nested anywhere inside it binds
(`_nested_import_names`); when a statement is retained because it is
always retained or its file is whole -- never because one specific name
of it was named, which still contributes only that name (D3, F8) -- those
names are resolved exactly as the statement's own top-level import names
already were. Guards: a dedicated fixture pins the never-spelled case
directly on `_retained`; the existing `if TYPE_CHECKING:` guard's
expectation widens from "the one node that also spells the alias bare" to
"every node of the file", since the `if` is always retained file-wide, not
per node -- a correction this fix makes, not a regression.

**I2 (two conformance gaps in resolution).** `_resolve_chain` stopped at
the first `('module', ...)` binding of an attribute chain's root; D3 says
a root bound to two tracked modules (`if X: from . import a as m / else:
from . import b as m`) resolves into both, since which one wins is a
runtime fact the static walk does not evaluate. Fixed: every matching
module binding is unioned. Separately, an `ImportFrom` whose relative
import could not be resolved (no package, or `resolve_name` raising)
registered no binding at all for the names it tried to bind, so
`_resolve_bare` never reached the catch-all D3 promises for an
unfollowable import; fixed by registering `('name', None, <name>)` there
too, exactly as every other unfollowable binding already does.

**I3 (the catch-all was too wide: a loaded, known, external module is not
an ambiguous one).** Diagnosed on the bench against the project: a project
leaf (`parts:Frame`) retained nothing ADR-071 had dropped, but a sibling
(`parts:Arbor`) retained the sibling node class `Frame` it never names,
because `simulation/shared/attachments.py` does `from
machinome.node.frames import Frame`; the framework module lies outside
the project, `_reach_import_target` answered `None` (its only answer for
"not trackable"), and `None` fed the catch-all, which then matched every
tracked definition named `Frame` -- including the clock's own part. The
distinction D3 needs and did not have: an import the interpreter has
*loaded* and can place, but whose file is definitely outside the project
(or inside the framework, or has no `__file__`), is known, not ambiguous,
and resolves to nothing beyond its own binding's text; the catch-all is
for a name the interpreter genuinely cannot place at all -- not loaded, an
unresolved relative import, or the importer's own package `__init__`
(ADR-033's tracked-nowhere gap). `_reach_import_target` now returns a
third answer, `_EXTERNAL`, distinguished from `None` by exactly that test,
and every binding and resolution site (`_resolve_bare`, `_resolve_chain`,
the star-source walk) treats it as "names nothing" rather than "ambiguous,
match everything of this name". Guards: a project node class shadowing a
framework class by name, reached only through the framework import in a
sibling file, is no longer retained by a node that never names the
project's own class; the previous-rule migration still carries on a
fixture with such a framework import in the closure, unaffected by the
narrower catch-all (the previous rule never looked at that file at all).
Rerun on the bench after the fix: `parts:Arbor` no longer carries `Frame`.

**I4 (a transient record was written under the previous rule).** `record
(..., transient=True)` still wrote version 3; `_recorded_source` reads
version 3 as the *previous* rule (D8), so a transient artifact verified
later in the same process was compared against the wrong digest and
rebuilt for no reason. Fixed: a transient record is version 4 with
`"transient": true`, carrying every version-3 field as D8 already
provides for; `recorded_transient` is unchanged, since it only reads the
mark. Guard: a transient record's `recorded_rule` is `'current'`.

**I5 (cost: the fixpoint was recomputed once per artifact, not once per
shared closure).** `_retained`'s eviction keyed only on the path set, so
two nodes sharing a closure -- the ordinary case, since siblings in one
project commonly share most of their import closure -- evicted each
other's cached entry on every call, turning what should be an
amortised-once cost into one full fixpoint per artifact. Fixed in two
parts: eviction now drops only an entry whose file keys differ from the
current call's, never one that merely belongs to a different node's scope
over the same, unchanged files; and the fixpoint is split into a shared
phase (`_compute_baseline`, keyed on the tracked files and the caller's
whole-file set alone: the always-retained statements, the whole files,
and everything they reach by resolution or a dynamic/getattr guard) and a
per-node phase (`_compute_retained`, continuing the same, monotone
fixpoint from a copy of the baseline with that node's own seeds added).
`_baseline_cache` is evicted the same careful way. Measured on a synthetic
project of comparable shape (a 152-file shared closure, 20 sibling node
classes, cross-file assertions forcing real baseline propagation, since
the clock project itself is never run from here): before the fix
(`_baseline_cache` cleared before every node, simulating the eviction
bug), each sibling's `source_digest` after the first cost a mean 11.7-11.9
ms; after the fix, 6.2-6.4 ms -- about 1.9x, widening with closure size.
The orchestrator's own numbers on the real project are in `evidence.md`.

**I6-I9 are evidence and wording, not code**: the changelog bullet and
ADR-182 are corrected to name no scratch labels and no presumed future
version; `workflow/warts.md` gains the combined-run test-harness anomaly
as its own untriaged finding; the carry diagnosis (which siblings carry,
which do not and why, down to the exact mention) is recorded in
`evidence.md`.

Acceptance, on top of the Proof plan: every guard and red test above is
new or updated and green; the full focused set and the full suite are
green once more, alone; `openspec validate --all` passes; nothing of D1-D9
changes in substance -- I1-I5 are conformance and cost fixes to the rule
already decided, not a different rule.
