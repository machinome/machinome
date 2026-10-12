Bench: `/home/asa/devel/machinome/machinome/WTs/digest-only-what-the-node-names`,
branch `digest-only-what-the-node-names`, base `58a1e74f` (framework `main`,
Machinome 0.8.1 at released state) plus `4f9ebe09` (the pilot's wart record,
cherry-picked). Every framework command runs as `env -C <bench>
PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1
/home/asa/devel/machinome/.venv/bin/<tool> ...`; OpenSpec as `env -C <bench>
openspec ...`. `<change>` is `openspec/changes/digest-only-what-the-node-names/`;
its `measurements/` holds the prototypes (`reach.py`, `reach2.py`), the
project change (`restructure.py`) and the prototype's result on the changed
project (`overlay.json`). The originating project is 3DPrintedClocks wall
clock 02; the applier never runs it, never writes under
`/home/asa/devel/machinome/projects`, under the primary checkout
`/home/asa/devel/machinome/machinome`, or under `/mnt/data`. One test run of
ours at a time; wait on a PID, never on a `pgrep -f` pattern that matches its
own command line. Every test marked RED is run and seen red, for the reason
it names, before the code that turns it green; a test red for another reason
is fixed, not its expectation, and the reason recorded. Record every command,
its result and the load average in `<change>/evidence.md` as you go. Nothing
is committed: the applier stops before committing (section 7).

## 1. Baseline on the unmodified tree

- [x] 1.1 Create `evidence.md` with the bench commit (`git rev-parse HEAD`
  is `4f9ebe09`), `git status --short` (only `<change>`), and the
  interpreter check (`python -c 'import machinome; print(machinome.__file__)'`
  prints a path under the bench).
- [x] 1.2 Run `pytest -q -p no:cacheprovider
  tests/test_content_verified_currency.py tests/test_node_scoped_currency.py
  tests/test_source_set.py tests/test_source_census.py
  tests/test_generation_dedup.py tests/test_leaf_contract_recipe.py
  tests/test_brep_currency.py tests/test_flexible_verdict_identity.py`;
  record the counts and wall time. This is the focused set of 4.2.
- [x] 1.3 Run `python tests/leaf_contract_golden.py --check` and record its
  whole output (every `EXPECTED` and `DIFFERS` line and the summary): the
  baseline 4.3 compares with. The `EXPECTED: ... digest` lines are
  root-cleanup's; their `now=` values are the digests this change must not
  move.

## 2. Red tests

- [x] 2.1 Write `tests/test_reach_scoped_currency.py` on
  `tests.test_content_verified_currency.ScratchProjectTest`, with the
  fixture of design.md "Proof plan" and the five red tests R1 to R5 there:
  R1 (an edit to a definition one node never names spares it: `X`, `Y`, a
  function, a non-node class, an unused import, as subtests with a fresh
  build each; and its second form, `from .spec import X, Y` read as bare
  `X` by `A` and bare `Y` by `B`), R3 (a sibling named from another tracked file is followed),
  R4 (a previous-rule record is verified once and re-recorded as version
  4), R5 (a previous-rule record is not carried past a sibling it left
  out). R4 and R5 share one helper computing the previous rule's digest in
  the test: every tracked file by its bytes except the leaves' file, whose
  entry is the sha256 of its lines without `B`'s class statement, in the
  entry encoding `whole_file_digest` in `tests/test_node_scoped_currency.py`
  uses. Planted records are version 2 JSON with the node's current
  `source_fingerprint`.
- [x] 2.2 In `tests/test_node_scoped_currency.py` replace
  `test_editing_shared_code_re_derives_every_node_in_the_file` by R2's two
  tests: `test_editing_code_one_node_names_re_derives_that_node_alone`
  (`PIN_RADIUS = 1.0` to `1.5`, then `return SIZE * 1.5` to `2.0`, each
  re-derives `['Pin']`) and
  `test_editing_code_every_node_names_re_derives_every_node` (`from . import
  trace` to `from . import trace as trace` re-derives `['Block', 'Pin']`).
  Update the module docstring's sentence on module-level code. No other
  test in that file changes.
- [x] 2.3 Write the guards G1 to G11 and G13 to G16 of design.md in the new
  file (G14 in it too, loading `tests/stl_project` and `tests/step_project`
  as their own tests do), and extend
  `test_the_settled_path_reads_no_source_content` in
  `tests/test_content_verified_currency.py` to patch
  `currency._reach_analysis` and `currency._retained` beside `_analysis`
  (G12; `create=True` on the unchanged tree, where they do not exist yet).
- [x] 2.4 Run the new file and the two edited tests on the unmodified tree.
  RED, each for its reason: R1 because `spec.py` is digested whole
  (`renders()` gives `['A', 'B']` where one leaf, or for the unused import
  none, is expected); R2's first test because module-level
  code is never removed (`['Block', 'Pin']` for `['Pin']`); R3 because
  ADR-071 reads only the leaves' own file and leaves `B` out of `A`'s
  digest (`['B']` for `['A', 'B']`); R4 because the record is rewritten as
  version 2 and the later `Y` edit renders `['A', 'B']`; R5 because the
  planted digest is today's own, so `A` is not re-derived; G15's companion
  (a computed `getattr(self, name)` does not retain `spec` whole) for R1's
  reason. R1's second form is red for the same reason. The guards G1 to
  G14, G15's main half, G16 and R2's second test pass.
  Record the output.

## 3. The change

- [x] 3.1 `machinome/currency.py`: `_reach_analysis(path, census=None)`,
  cached on `_file_key` in `_reach_analyses` and read through the census
  when one is active, giving per top-level statement its line span (first
  decorator to `end_lineno`), whether it is a definition (design.md D1)
  and which names it binds, whether it is always retained (D2: not a
  definition, a star import, decorated unless a node class of the file, a
  dunder name, sharing a line with another statement), its mentions (bare
  names, attribute chains, string constants; for an import statement the
  names it binds are recorded apart, counted as mentions only when the
  statement is always retained or its file is retained whole, never when
  it is retained because one of its names was named; design.md D3, the
  reviewer's F8), whether it holds a dynamic lookup (D4), and the
  bare names it passes as the first argument of a `getattr`, `hasattr`,
  `setattr` or `delattr` whose second argument is not a string literal;
  and for the module: its import bindings from every import statement in
  the file at any depth (D3, the reviewer's F1) and its star sources,
  resolved to tracked paths through the loaded-module index
  (`sources._loaded_as`, `sources._project_file`), and the names bound
  otherwise anywhere in the file (parameters, assignment, loop, `with` and
  `except` targets, imports of untracked modules), for D3's shadowing rule;
  `None` (retain whole) when the file does not parse or no loaded module
  came from it.
- [x] 3.2 Same file: the fixpoint of D1 and D3 over a node's tracked Python
  files, from its seeds, its always-retained statements and its whole files
  (D5, D6), resolving bare names in their module (every binding of the
  name, import bindings followed transitively through re-exports, star
  sources always consulted), attribute chains rooted at a tracked-module
  binding into that module (and also by the catch-all when the root name is
  shadowed), and every other attribute name, string constant and
  unfollowable import binding by the catch-all; a dynamic lookup in a
  retained statement makes its file and that file's own import closure
  whole, a computed module `getattr` makes that module and its star
  sources whole (D4, the reviewer's F2), and the fixpoint resumes; an
  import statement's bound names join the mentions only once its file is
  whole or when it is always retained (D3, F8); a seed
  name that is not a top-level class statement of its file makes that file
  whole. This is `_retained(files, root, scope, whole, census)`, returning
  the left-out statement indices per file, cached on (file keys, seeds,
  whole-file set).
- [x] 3.3 Same file: `source_digest(files, root, scope, census, ...)`
  returns the current-rule digest: each Python file's entry is
  `_file_digest` when it leaves nothing out and otherwise the sha256 of its
  lines outside the left-out spans, built as `_scoped_digest` builds it
  (D7) by `_retained_digest(path, left_out, census)`, cached on (file key,
  frozenset of left-out indices); non-Python files by their bytes; an empty
  or absent scope retains every file whole, so a direct call without a
  scope is unchanged. ADR-071's `_analysis`, `_analyse`, `_removed_spans`
  and `_scoped_digest` stay unchanged and compute the previous rule's
  digest through `previous_source_digest(files, root, scope, census)`;
  `previous_rule_carries(files, root, scope, whole, census)` answers
  whether every span the previous rule leaves out is left out by the
  current rule (D9). A rename of any of these is recorded in evidence and
  in G12.
- [x] 3.4 Same file: `record` writes version 4 whenever a fingerprint is
  given (fields as version 3); the legacy digest-only form stays for a
  caller that gives none. `_recorded_source` returns the rule beside
  digest, fingerprint and recipe: versions 2 and 3 and the legacy form are
  the previous rule, version 4 the current, anything else certifies
  nothing; `recipe` is read from versions 3 and 4. Docstrings of the module,
  `source_digest`, `record` and `_recorded_source` state the rule and the
  versions.
- [x] 3.5 `machinome/node/base.py`: the node keeps, beside `scope`, the
  files its own source reaches (a copy of `source_closure(self.src)` taken
  where `self.files` is first set, before any subclass adds files) and
  derives its whole-file set when a digest is asked: every tracked Python
  file outside that set, or every tracked file when its scope is empty
  (D6). `_tracked_digest` passes the whole-file set. `_content_verified`
  reads the record's rule: a current-rule record is compared with the
  current digest as today; a previous-rule record with the previous digest
  (recipe folded the same way), and on a match that also passes D9's
  condition the artifact is restamped and recorded with the current digest
  and fingerprint (version 4); otherwise not current. `source_digest`'s
  docstring says what the digest covers. Verify and record in evidence
  what `self.src` is for an `StlNode` (`tests/stl_project/parts.py`) and a
  `StepNode` (`tests/step_project/parts.py`): design.md D6 reads it from
  the code as the asset, so their scope is empty and every file is
  retained whole; if either is the wrapper module, stop and report.
- [x] 3.6 `machinome/node/internal.py`: both union sites (`present`,
  `materialize`) also union the children's whole-file sets.
- [x] 3.7 No change to `stl.py`, `step.py`, the fingerprint, `_up_to_date`'s
  metadata path, the sweep, publication or `node.files`. If any proves
  necessary, stop and report it with the evidence.

## 4. Green

- [x] 4.1 Run `tests/test_reach_scoped_currency.py` and
  `tests/test_node_scoped_currency.py`; all green. Record.
- [x] 4.2 Run the focused set of 1.2; same counts plus the new tests, all
  green. Record counts and wall time.
- [x] 4.3 `tests/leaf_contract_golden.py`, following its own docstring's
  convention: add beside `ROOT_CLEANUP_EXPECTED` a table for this change
  (`DIGEST_ONLY_WHAT_THE_NODE_NAMES_EXPECTED`, commented with the change's
  name and design.md D8) through which `_expected` counts a
  `record_version` moving from 2 or 3 to 4 as expected, and name both
  changes in the summary line; update the docstring's sentence on the
  table. Run `--check`: it must report 0 differences, and every
  `EXPECTED: ... digest` line's `now=` value must equal its value in 1.3's
  output. A digest that moves is a stop: report it with the fixture and
  the statements its closure left out. The golden JSON is not
  regenerated.
- [x] 4.4 `flake8 --max-line-length=89` on the changed files; record
  anything a file already carried.

## 5. Records

- [x] 5.1 Write `docs/adrs/NODE/ADR-186-<slug>.md`, Accepted, amending
  ADR-071 and depending on ADR-033, ADR-058, ADR-060 and ADR-081: context
  (wall clock 02's 54 rigid parts invalidated by a cord clearance; the
  numbers of design.md Context), drivers (ADR-071's, unchanged), the
  options of design.md D1, D4, D8 and D9 with why each was rejected, the
  decision (the closure as one node sees it; always-retained statements;
  resolution and catch-all; dynamic lookups; whole files; version 4 and
  the migration by ADR-071's own code), consequences (the exposure
  extended from node classes to all definitions; D10's correction; the
  flexible identity moving once; an older reader rebuilding version 4
  records), evidence (filled from section 8), and the archived change.
  ADR-071 gains an "Amended by" entry for ADR-186, and its index line in
  `docs/adrs/README.md` reads "amended by 081/182"; ADR-186 gets its own
  index line in the NODE section.
- [x] 5.2 `docs/architecture.md`: the paragraph at ~86-98 (the digest is
  of what the node names across its closure, ADR-071/182), the paragraph
  at ~2142-2149 (a record of the earlier rule verifies once under it and
  is re-recorded), and the bullet at ~3224-3233 (the scope, the
  always-retained statements, the whole-file cases, the stated exposure).
- [x] 5.3 Read `/home/asa/devel/machinome/skills/write-the-manual/SKILL.md`
  first. Then `docs/concepts/node-tree.rst`, the "Freshness" bullet at
  ~115: the digest covers what the node names in its sources, so editing a
  definition a node never names, in any tracked module, only restamps it;
  geometry reached through a name the code never spells is outside what
  the digest sees. Rewrite the bullet in place; add nothing else.
  `docs/reference/api.rst`, the `files` attribute: one clause that a
  Python file a subclass adds is read whole. No project is named on either
  page.
- [x] 5.4 `docs/project/changelog.rst`: add an `Unreleased` section above
  `Machinome 0.8.1` (the house form of 2acba68f) with one bullet: a node
  is rebuilt only for edits to what it names in its sources; editing a
  definition no node names, in any tracked module, restamps instead of
  rebuilding; a clock's cord tuning that rebuilt every rigid part now
  regenerates only the cord, with 8.1(b)'s measured wall time and STL
  count against `before-2`'s 54.7 s and 54 regenerated; a build directory
  from 0.8.1 is kept, its records verified under 0.8.1's rule and
  re-recorded, but the first edit after upgrading is still judged by
  0.8.1's rule and rebuilds what 0.8.1 would (8.1(a')'s numbers), and only
  the edits after it are spared (digest-only-what-the-node-names). By
  kind, never by project.
- [x] 5.5 `workflow/warts.md`, the entry "3DPrintedClocks wall clock 02
  (2026-10-10, string edits invalidate unrelated rigid geometry)": a
  triage note under its header that the pilot took up route one on 10
  October 2026, this change plus the project's cord geometry moved off the
  movement, with the viewer refetch and the movement-construction floor
  left open as recorded, and that the pilot's first cord edit after the
  change lands rebuilds all 54 rigid parts once under 0.8.1's rule before
  later edits are spared.

## 6. Sync, archive, validate

- [x] 6.1 Sync the delta into `openspec/specs/build-pipeline/spec.md`.
- [x] 6.2 Archive the change; `openspec validate --all` passes.
- [x] 6.3 The focused set of 1.2 once more, then the full suite once,
  alone (`pytest -q -p no:cacheprovider` at the bench root); record counts
  and wall time.

## 7. Stop and report

- [x] 7.1 Leave everything uncommitted, `git status --short` recorded, and
  report: the red output of 2.4, the green counts of 4.1, 4.2 and 6.3,
  4.3's golden result, any decision taken that design.md does not
  state, and anything left undone. Then wait for the orchestrator's
  message.

## 8. Caller evidence (run by the orchestrator, folded by the applier)

- [x] 8.1 The orchestrator, in `projects/3DPrintedClocks/WTs/string-cache`
  with `measurements/restructure.py` applied and its records written by
  framework `main` (51.7 s, 54 regenerated, on 10 October), keeps a copy
  of that 0.8.1 build directory and runs one at a time with the bench on
  `PYTHONPATH`, through `measure/build_once.sh`:
  (a) `spec.py` touched with no content change: expect 0 regenerated and
  the rigid records re-recorded as version 4 (the migration without an
  edit);
  (a') on a fresh copy of the 0.8.1 build directory, the first line 144
  `front_clearance` edit after switching to the bench: expect 54
  regenerated under the previous rule and the records re-recorded as
  version 4 (the first edit after upgrading);
  (b) the second line 144 edit (0.1 further): expect no rigid STL with a
  new inode, the cord re-evaluated, wall time near the floor; the before is
  `before-2`, 54.7 s and 54 regenerated on framework `main` for the same
  kind of edit;
  (c) a warm build with no edit: the floor under the bench;
  (d) `PLATE_THICK` edited in `spec.py`: expect the parts that read it
  regenerated;
  (e) `machinome test wall_clock_02 --mesh`, compared test for test with
  the clean control at `2f846a8`, which gives 15 passed and 7 failed on
  both today, the seven being recorded pendulum-hardware debt (the
  project's
  `openspec/changes/archive/2026-10-09-clocks-care-and-frame-mates/evidence/reference.md`
  reproduces the same volumes); a single clock test cannot run under
  plain pytest. The exact-engine run is the orchestrator's own.
  The orchestrator also checks 6.3's full-suite result.
- [x] 8.2 On receipt, fold the numbers into `evidence.md` (in the archived
  change; both (a) and (a') recorded), ADR-186's evidence, the changelog
  bullet of 5.4 ((b) against `before-2`, and (a')'s first-edit rebuild)
  and a "fixed" note on the warts entry of 5.5 (the edit's wall time and
  STL counts before and after, the first-edit rebuild, and what remains
  open); run `openspec validate --all`;
  leave everything uncommitted and report again.
