## Why

`workflow/warts.md`, "3DPrintedClocks wall clock 02 (2026-10-10, string
edits invalidate unrelated rigid geometry)", bullet **Finding**: "Editing
only `STRING_ROUTE.radius_clearance` or `STRING_ROUTE.front_clearance` in
the project's `simulation/wall_clock_02/spec.py` invalidates the source
digests of all 54 existing rigid STL cache entries for this clock." The
pilot tunes the cord by hand and needs the rigid parts reused between
saves. Measured on 10 October 2026 in the project worktree
`projects/3DPrintedClocks/WTs/string-cache` (project `2f846a8`, framework
`main` at 0.8.1): a cold `machinome build wall_clock_02` takes 53.7 s and
writes 54 STL artifacts; a warm build with no edit takes 13.5 s and touches
none of them; changing `front_clearance` on line 144 and building again
took 54.2 s with every rigid part re-derived (`before-1`, 5.0 to 4.9) and
54.7 s with all 54 written under new inodes (`before-2`, 4.9 to 4.8).

The cause is ADR-071's unit. A node's content digest covers every file of
its project-local import closure whole, except its own file, from which
only the sibling node classes it never names are removed. `spec.py` is in
the closure of every rigid part, so line 144 is in every rigid part's
digest, whether or not anything that part runs reads it.

## What Changes

- **The digest covers what the node names, across its whole closure.**
  For each node, a top-level definition (a class, a function, an assignment
  to plain names, an import other than a star import) that nothing the
  node retains ever names is left out of the digest, in every tracked
  Python file, not only the node's own. What the node retains starts from
  its own class statement and every top-level statement that is not a
  definition, and grows through the names that retained text mentions until
  nothing more is named. A bare name resolves as Python resolves it: in its
  own module, through `from X import y` to X's definition (package
  re-exports followed), through star imports, with an import anywhere in
  the module (inside a function, a method, a `try` or an `if` block)
  binding exactly as a top-level one does. An attribute chain rooted at a
  name bound to a tracked module resolves into that module (and also by
  the catch-all when the name is bound otherwise too). Any other attribute name and
  any string literal keeps every top-level definition of exactly that name
  in every tracked file, as ADR-071 already did for sibling node classes.
- **Every uncertainty keeps more text.** Never left out: non-definition
  statements, star imports, decorated definitions other than node classes,
  dunder definitions (`__all__`, a module `__getattr__`), a statement
  sharing a line with another, and comments outside statements. A file
  whose retained text calls `globals`, `locals`, `vars`, `dir`, `eval`,
  `exec`, `__import__`, `import_module` or `getmembers`, or reads
  `__dict__`, is digested whole with its own import closure; a computed
  `getattr`, `hasattr`, `setattr` or `delattr` on a name bound to a
  tracked module keeps that module whole. A file that
  cannot be parsed, a module the interpreter cannot place, a node class
  that is not a top-level class statement of its file, a Python file a node
  tracks beyond its own import closure (an imported mesh's wrapper module),
  and every file of a node with no Python source of its own are digested
  whole. A file that leaves nothing out digests byte for byte as today.
- **Nothing recorded by 0.8.1 is rebuilt merely because the framework
  changed.** A currency record gains a version, 4, meaning its digest was
  taken under the new rule. A version 2 or 3 record, or a legacy
  digest-only one, is verified once against ADR-071's digest, computed by
  ADR-071's code unchanged; when it matches and ADR-071 left out nothing
  the new rule retains, it is re-recorded as version 4 without rendering.
  A settled artifact with an unchanged fingerprint keeps its old record on
  the metadata-only path until its sources next change, so the first edit
  after upgrading is judged by 0.8.1's rule: the pilot's first cord edit
  after this lands still rebuilds all 54 rigid parts once, and only the
  edits after it are spared. The changelog and the warts note say so. An
  older reader refuses a version 4 record and rebuilds.
- **ADR-071 is amended by a new ADR-182**, written after implementation:
  the unit becomes the closure as one node sees it.
- **The project-side change** (the orchestrator's, in the project): wall
  clock 02's `Movement.__init__` stops storing `STRING_ROUTE`, and the
  cord's geometry moves to a `StringGeometry` the string nodes ask for.
  Without it every rigid part runs the movement's constructor, which names
  `STRING_ROUTE`, and no statement-level rule can separate them. Line 144
  stays where it is. This is a change to what the movement object holds,
  not to the file layout ADR-071 refuses to impose.

Deliberately out:

- No new public API, declaration or configuration on nodes.
- No analysis of attribute flow inside a class or a function: a kept class
  is kept whole (the route the pilot did not take).
- No change to the string nodes or to any other clock, to the import
  closure (`node.files`), the fingerprint, the hit path, the sweep or
  publication.
- No change to the viewer, which refetches a restamped mesh (the wart's
  "Other work on the same reload path"; a separate finding), and none to
  the per-process cost of constructing the movement.
- No guard on a computed name reaching a module through `sys.modules`, a
  variable, a parameter or a call: it is the exposure ADR-071 accepted and
  is stated, not closed.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `build-pipeline`: "Mtime-equality caching" — the digest's scope becomes
  the definitions the node names across its closure; the never-left-out
  statements, the whole-file cases and the migration of records written
  under the previous rule are stated; the scenarios that said "an edit to a
  source" now say "an edit to text the node retains", "Shared code in a
  shared file invalidates every node in it" becomes "Shared code
  invalidates the nodes that name it", "A single-class file digests as it
  always has" becomes "A closure that leaves nothing out digests as it
  always has", the legacy-record and sibling scenarios are extended;
  sixteen scenarios added, every other scenario carried unchanged.

## Impact

- Code: `machinome/currency.py` (the per-file analysis extended with
  definitions, bindings and mentions; the reach fixpoint; the retained-text
  digest; the version 4 record and the reading of earlier ones),
  `machinome/node/base.py` (`_content_verified` verifies an earlier record
  under the previous rule and re-records it; the node keeps the files its
  own source reaches beside `scope`), `machinome/node/internal.py` (unions
  that beside the scope); `machinome/node/sources.py`'s module placement
  (`_loaded_as`, `_project_file`) reused unchanged. `stl.py` and `step.py`
  need no edit: the whole-file rule for files beyond a node's own closure
  is computed in the base (design.md D6).
- Tests: a new `tests/test_reach_scoped_currency.py`, red where design.md
  says; `tests/test_node_scoped_currency.py`'s
  `test_editing_shared_code_re_derives_every_node_in_the_file` rewritten to
  the new rule (it pins the behaviour this change removes);
  `test_the_settled_path_reads_no_source_content` extended to patch the new
  analysis too; `tests/leaf_contract_golden.py` gains this change's
  expected-difference table (`record_version` 2 or 3 to 4) beside
  `ROOT_CLEANUP_EXPECTED`; every other currency, source-set and
  leaf-contract test unchanged.
- Cost: on a fingerprint miss, one AST per tracked Python file per process
  and one fixpoint per distinct seed set; nothing on the hit path.
- Records: ADR-182 (new) amending ADR-071, ADR-071's "Amended by" line and
  its index line; `docs/architecture.md`; `docs/concepts/node-tree.rst`;
  `docs/reference/api.rst` (`files`); one changelog bullet under
  `Unreleased`; the warts entry triaged and, at the end, marked fixed with
  the measured numbers.
- Behaviour beyond the clock: a node in any project stops rebuilding for
  edits to definitions it never names; a flexible leaf's state identity,
  which carries its digest, moves once for a leaf whose closure leaves
  something out, so the test framework's stored verdicts on it run once
  more. A build directory shared with a 0.8.1 reader rebuilds what that
  reader finds recorded as version 4.

## Originating project and caller evidence

3DPrintedClocks wall clock 02. The acceptance is the pilot's: "change
front_clearance at line 144 in spec.py and only the string is regenerated,
not the whole clock. you need to measure build time before and after, and
it needs to decrease drastically." The prototype `measurements/reach2.py`
shows the rule on the real closures: on the project as it is, `STRING_ROUTE`
stays in every rigid part (named by `Movement`); with the project change
applied (`measurements/restructure.py`, result in `measurements/overlay.json`),
`parts:Frame` keeps 503 of 926 statements and drops `STRING_ROUTE`,
`StringGeometry`, `string_geometry` and the `WoundStringRoute` import, while
`clock:WeightString` keeps them. The orchestrator applies the project
change and runs the caller measurement (tasks.md section 8); the applier
does not run the project.

## Authorization

The pilot authorized the whole cycle in advance on 10 October 2026, with
delegated review: among three routes, the pilot chose this one, a
framework cycle generalising ADR-071 plus a small project-side change, and
asked for "the orchestration and adversary review discipline": an Opus
agent proposes, the orchestrator reviews adversarially, a separate applier
implements red-first, and the orchestrator validates and measures.
Integration, push and publication stay the pilot's.
