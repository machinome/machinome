# ADR-182: The Digest Covers Only What the Node Names, Across Its Closure

**Status:** Accepted
**Date:** 2026-10-10
**Change:** `digest-only-what-the-node-names`
**Amends:**
- [ADR-071: Node-Scoped Content Currency](./ADR-071-node-scoped-content-currency.md)
**Depends on:**
- [ADR-033: Import-Closure Source Set and Up-To-Date Leaf Path](./ADR-033-import-closure-source-set-and-up-to-date-leaf-path.md)
- [ADR-058: Indexed Package Lookup for Source Closures](./ADR-058-indexed-package-lookup-for-source-closures.md)
- [ADR-060: Content-Verified Currency Beneath the Mtime Rule](./ADR-060-content-verified-currency-beneath-the-mtime-rule.md)
- [ADR-081: Per-Contributor Metadata Guards Aggregate-Mtime Currency](./ADR-081-per-contributor-metadata-guards-aggregate-mtime-currency.md)

## Context and Problem Statement

`workflow/warts.md`, "3DPrintedClocks wall clock 02 (2026-10-10, string
edits invalidate unrelated rigid geometry)": editing only
`STRING_ROUTE.radius_clearance` or `STRING_ROUTE.front_clearance` in the
project's `simulation/wall_clock_02/spec.py` invalidated the source
digests of all 54 existing rigid STL cache entries for that clock. The
pilot tunes the cord by hand and needs the rigid parts reused between
saves. Measured on 10 October 2026 in `projects/3DPrintedClocks/WTs/
string-cache` (project `2f846a8`, framework `main` at 0.8.1,
`measure/build_once.sh`): a cold build took 53.7 s and wrote 54 STL
artifacts; a warm build with no edit took 13.5 s and touched none of
them; editing `front_clearance` and building again took 54.2 s with
every rigid part re-derived, then 54.7 s with all 54 written under new
inodes on the next such edit (`before-2`).

ADR-071's unit is the file as one node sees it: a node's digest covers
its own tracked files whole, except its own source, from which only the
*sibling node classes* its own text never names are removed. `spec.py`
defines no node class, so ADR-071 never touches it: it is in the import
closure of every rigid part, and line 144 is in every rigid part's
digest whether or not anything that part runs reads it.

## Decision Drivers

ADR-071's own, unchanged: the hit path must not change; currency may
fail only in the direction of rebuilding too much, never too little;
nothing recorded by the previous release may become invalid without an
honest one-time migration; no new sidecar format, stamp, sweep or
publication change. Added by this change: no new public API,
declaration or configuration on nodes (ADR-033's boundary); no
attribute- or value-flow analysis inside a class or a function -- a
kept class or function is kept whole, the route the pilot did not take.

## Considered Options

1. **The unit is the closure as one node sees it**: a top-level
   definition in any tracked Python file -- not only the node's own --
   that nothing the node's retained text names is left out (chosen).
2. **Attribute-flow analysis inside classes**, separating a
   constructor's string state from its gear state so the project need
   not change.
3. **A declaration on the node** naming its geometry inputs.
4. **Per-definition digests in the sidecar**, recording which
   definitions a record covers.
5. For the migration: a `rule` field inside the existing version 3
   record, or no version marker at all, letting every record whose
   digest differs rebuild once.

## Decision Outcome

Chosen: **option 1**, implemented as `machinome/currency.py`'s
`source_digest`, `_retained` and `_reach_analysis`.

For each node, over every tracked Python file, a top-level *definition*
-- a class, a function, an assignment or annotated assignment to plain
names, or an import other than a star import -- that the node's
*retained text* never names is left out of the digest. What a node
retains starts from its own class statement(s) in its own file (the
seeds, from `scope`, as ADR-071 already computed it) and every top-level
statement that is **not** a definition; it grows by every definition a
retained statement's *mentions* -- bare names, attribute chains, string
constants -- name, resolved as Python resolves a name: in the mentioning
module's own definitions (including the import that bound the name, if
any); through `from X import y`, transitively, into a tracked module
`X`'s own definition of `y`, package re-exports followed; into every
tracked module a star import sources, whichever binds the name; and, for
an attribute chain rooted at a name bound to a tracked module, into that
module (walking submodule bindings), by the same bare-name rule there.
Every other attribute name, every string literal, and every name an
import binds that the system cannot follow retain every top-level
definition of exactly that name in every tracked file -- ADR-071's
catch-all, now for all definitions, not only sibling node classes. An
import is made at any depth in the module's text (inside a function, a
method, a conditional, a `try`), not only at the top level, since
`source_closure` already tracks the files these import regardless of
depth (ADR-033).

Every uncertainty keeps more text (D2-D6 of the change's design): a
non-definition statement, a star import, a decorated definition other
than a decorated node class, a definition of a dunder name, and a
statement sharing a line with another are never left out. A retained
call to `globals`, `locals`, `vars`, `dir`, `eval`, `exec`,
`__import__`, `import_module` or `getmembers`, or a read of `__dict__`,
keeps its own file and that file's whole import closure. A retained
`getattr`/`hasattr`/`setattr`/`delattr` whose first argument is a bare
name bound to a tracked module and whose second is not a string literal
keeps that module, and every module it star-imports, whole -- the
exposure this leaves open (a computed name reaching a module through
`sys.modules`, a variable, a parameter or a call) is the one ADR-033
already draws for `importlib` and computed names, stated rather than
closed. A file that cannot be parsed, or whose module the interpreter
cannot place; a node's own file in which its seed class is not a
top-level class statement; and every tracked file a node reaches beyond
its own source's import closure (an `StlNode`'s or `StepNode`'s wrapper
module, a file a subclass adds to `files` after construction) are
retained whole. A node with no Python source of its own (an empty
`scope`) has every tracked file whole, exactly as before. A file that
leaves nothing out digests byte for byte as under ADR-071.

**Why not option 2 (attribute-flow analysis).** It needs a sound model
of `self` and of every object a constructor builds, which arbitrary
Python and a project library such as `clocks` do not give, and its
failure would be silent. Rejected.

**Why not option 3 (a declaration).** ADR-033 already rejected per-node
source declarations as a decision driver: it puts the burden on every
author and fails silently when forgotten; the brief ruled out new public
API besides.

**Why not option 4 (per-definition sidecar digests).** A format change
carrying hundreds of entries per artifact for no gain the recomputed
reach does not already give.

**Migration (D8, D9).** A record written under this rule is version 4:
version 3's fields, with the digest taken under this rule. `record`
writes version 4 whenever it is given a fingerprint; the legacy
digest-only form stays for a caller giving none. The reader
(`_recorded_source`'s `rule`) treats version 2, version 3 and the legacy
form as the *previous* rule and version 4 as the *current* one.
Rejected for the migration itself: a `rule` field inside version 3 (an
older reader would wrongly compare its own digest against the new rule's
value -- unsafe); no marker at all (every project would rebuild once on
its first edit after upgrading, since under this rule most real
projects leave *something* out, against ADR-071's own driver that
nothing recorded by the previous release may be invalidated for free).
On a fingerprint or stamp miss, a previous-rule record is verified
against ADR-071's own digest of the sources now present (ADR-071's
`_analysis`/`_removed_spans`/`_scoped_digest`, kept unchanged and
renamed `previous_source_digest`), and only accepted -- restamped and
re-recorded as version 4 without re-deriving geometry -- when that
matches **and** every span ADR-071's rule leaves out is also left out by
this rule (`previous_rule_carries`): otherwise the previous match proves
nothing about what this rule would keep, and the artifact is rebuilt. A
settled artifact (stamp and fingerprint both match) never reads this
path at all, so the first edit after upgrading is still judged, once,
by the previous rule; only later edits are spared.

A leaf's own scope is unioned into an internal node's (`scope`, as
before) and its *whole-file set* is unioned the same way
(`AbstractBaseNode._own_whole_files`/`_effective_whole_files`,
`InternalNode.present`/`materialize`): the node keeps a snapshot of its
own source's closure (`_own_source_files`), taken the moment `files` is
first set, and every tracked file outside that snapshot -- or every
tracked file, when the node has no Python seed of its own -- is whole.

## Consequences

- The exposure ADR-071 accepted for sibling node classes alone -- a
  registry filled by a decorator and read under a different key, a name
  computed at runtime -- now covers every kind of definition. It is
  stated in the manual beside ADR-033's boundary, not closed.
- A project that relied on a whole-file rebuild to notice a run-time
  read outside what the digest can see (already outside ADR-033's
  tracked set) sees a stale artifact exactly as it would have before
  this change; nothing here widens that set.
- A flexible leaf's stored verdict identity, which carries its digest,
  moves once for a leaf whose closure leaves something out.
- `tests/leaf_contract_golden.py` gains
  `DIGEST_ONLY_WHAT_THE_NODE_NAMES_EXPECTED = ('record_version',)`
  beside `ROOT_CLEANUP_EXPECTED`; two fixtures' `digest` fields also move
  from the 1.3-baseline value under `ROOT_CLEANUP_EXPECTED`'s existing,
  field-name rule (unchanged by this ADR) -- see Evidence.
- The previous-rule verifier (`previous_source_digest`,
  `previous_rule_carries`) is ADR-071's own tested code, kept, reached
  only by records written before this change. Removing it later is a
  separate decision.
- On this project, the no-edit migration (a timestamp-only touch, no
  content change) carried 30 of 54 records (every `parts.py` node:
  `Frame`, `Arbor`, `Bearing` and the rest, each now retaining none of
  the 11 siblings ADR-071 had left out, where none carried before I3).
  The other 24, every `clock.py` node, still refuse: `clock:BobShell`
  and `clock:WeightString` retain the siblings `Hands` and `Standoffs`
  through string constants in the project's own library
  (`clocks/hands.py:1111`'s `'Hands'`, `clocks/assembly.py:23`'s
  `'Standoffs'`) -- the catch-all working exactly as D3 states, not a
  gap this change closes. A real project's no-edit migration therefore
  carries only the nodes whose current reach adds no sibling the
  previous rule left out; this project's count is above, and the first
  genuine edit after upgrading still rebuilds every node once
  regardless, under the previous rule, exactly as D9 states.
- An older (pre-this-change) reader refuses a version 4 record and
  rebuilds -- the same safe rollback ADR-081 recorded for its own
  version bump.

## Evidence

Framework: `tests/test_reach_scoped_currency.py` (new; R1-R5, G1-G16, and
I1-I3's own guards added after the caller measurement: a top-level
`try`/`except` that binds a name nothing else spells, a root bound to two
tracked modules, an unresolvable relative import, a framework import
that must not retain a same-named project class, and the previous-rule
migration still carrying with one in the closure);
`tests/test_node_scoped_currency.py`'s
`test_editing_shared_code_re_derives_every_node_in_the_file` replaced by
`test_editing_code_one_node_names_re_derives_that_node_alone` and
`test_editing_code_every_node_names_re_derives_every_node`;
`test_the_settled_path_reads_no_source_content` extended for
`_reach_analysis`/`_retained`; `TransientRecordTest` gains a test that a
transient record's `recorded_rule` is `'current'` (I4). Full details,
counts and the golden check's two reported (not silenced) digest moves
(`solid2_node`, `molejo_snapshot`) are in this change's `evidence.md`.

Caller (the orchestrator's, in `projects/3DPrintedClocks/WTs/
string-cache`, project change at `b980d59`, bench on `PYTHONPATH`,
`measure/build_once.sh`, inodes before/after). Final numbers, measured
on the bench after I1-I5 (load 2.1-2.8); the pre-fix numbers this
replaces are kept in `evidence.md`, labelled as the pre-fix state:

- (a) a fresh copy of the 0.8.1 build directory, `spec.py` touched with
  no content change: 24.0 s, 24 regenerated, 30 restamped; all 54
  records now version 4. The migration carries 30 of 54 (every
  `parts.py` node); the 24 `clock.py` nodes refuse, for `Hands` and
  `Standoffs` above.
- (a') a fresh copy of that build directory, the first `front_clearance`
  edit (5.0 to 4.9) after switching to the bench: 61.1 s, 54 regenerated
  under the previous rule, records version 4 -- unchanged by I1-I5,
  since this path is judged by the previous rule regardless.
- (b) the second edit (4.9 to 4.8): 17.4 s, 0 regenerated, 54 restamped;
  (b2) a third edit (4.8 to 4.7): 17.4 s, 0 regenerated, 54 restamped.
- (c) warm, no edit: 15.2 s.
- The acceptance pair, same load, a fresh value: framework `main` (the
  unmodified rule) 52.4 s with all 54 rigid parts re-derived; the bench
  17.4 s with none re-derived, 54 restamped.
- (d) `PLATE_THICK` edited (8 to 9): 69.5 s, 54 regenerated -- a real
  geometry input still rebuilds what reads it (pre-fix measurement;
  unaffected by I1-I5, not remeasured).
- (e) `machinome test wall_clock_02 --mesh` under the bench: 22 tests,
  15 passed, 7 failed in 35.6 s, the same seven as the clean control and
  as framework `main` (recorded pendulum-hardware debt, unrelated to
  this change; pre-fix measurement, not remeasured). The exact-engine
  suite on the restructured worktree under `main`: 18 passed, 4 failed
  in 1121 s, equal to the clean control's 18 passed, 4 failed in 1120 s,
  the same five pendulum pairs.
- The fixpoint cost on this project's real 42-file closure (I5): 1162 ms
  once (parsing the closure and the shared baseline), 2 ms per node
  after, against 70-90 ms per node before I5.
- Full-suite result of tasks.md 6.3, checked by the orchestrator: 4790
  passed, 4 skipped, 0 failed (pre-I1-I9; 4797 passed after, per this
  change's own full-suite rerun, `evidence.md`).

## References

- `machinome/currency.py` -- `source_digest`, `previous_source_digest`,
  `previous_rule_carries`, `_retained`, `_reach_analysis`, `_reach_analyse`,
  `_resolve_bare`, `_resolve_chain`, `_recorded_source`, `record`
- `machinome/node/base.py` -- `_own_source_files`, `whole_files`,
  `_own_whole_files`, `_effective_whole_files`, `_content_verified`
- `machinome/node/internal.py` -- the `whole_files` union beside `scope`
  in `present`/`materialize`
- `tests/test_reach_scoped_currency.py`, `tests/test_node_scoped_currency.py`,
  `tests/leaf_contract_golden.py`
- OpenSpec change `digest-only-what-the-node-names`, capability
  `build-pipeline`
