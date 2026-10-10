# Evidence — `digest-only-what-the-node-names`

Standalone framework cycle. Bench
`/home/asa/devel/machinome/machinome/WTs/digest-only-what-the-node-names`,
branch `digest-only-what-the-node-names`, planning commit `128cf36e` on base
`4f9ebe09` (the wart record) on `58a1e74f` (framework `main`, 0.8.1). Every
framework command below runs as `env -C <bench> PYTHONPATH=<bench>
PYTHONDONTWRITEBYTECODE=1 /home/asa/devel/machinome/.venv/bin/<tool> ...`;
OpenSpec as `env -C <bench> openspec ...`. One test run of ours at a time;
load average taken from `cut -d' ' -f1-3 /proc/loadavg` before and after
each run.

## 1. Baseline on the unmodified tree

### 1.1 Bench state

```
$ git -C <bench> rev-parse HEAD
128cf36eca492cd847d7bae5da0a699a4a2e4e23
```

Task brief states the planning commit is `128cf36e`, which matches (not
`4f9ebe09`; the task text's own example reads the parent). `git status
--short` showed only the change directory as modified (new `evidence.md`
about to be added; nothing else tracked was dirty).

```
$ git -C <bench> status --short
```
(empty before this file was written)

Interpreter check:

```
$ env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1 \
    /home/asa/devel/machinome/.venv/bin/python -c 'import machinome; print(machinome.__file__)'
/home/asa/devel/machinome/machinome/WTs/digest-only-what-the-node-names/machinome/__init__.py
```

Under the bench, as required.

Load average at this point: 1.64 1.77 1.68.

### 1.2 Focused set, baseline

```
$ env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1 \
    /home/asa/devel/machinome/.venv/bin/python -m pytest -q -p no:cacheprovider \
    tests/test_content_verified_currency.py tests/test_node_scoped_currency.py \
    tests/test_source_set.py tests/test_source_census.py \
    tests/test_generation_dedup.py tests/test_leaf_contract_recipe.py \
    tests/test_brep_currency.py tests/test_flexible_verdict_identity.py
```

Load average 2.03 1.85 1.71 at the start, 2.29 1.93 1.74 at the end.

```
98 passed, 5 warnings, 24 subtests passed in 15.95s
```

### 1.3 Golden check, baseline

```
$ env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1 \
    /home/asa/devel/machinome/.venv/bin/python tests/leaf_contract_golden.py --check
```

Load average 2.27 1.93 1.74 at the start, 2.24 1.93 1.74 at the end.

```
EXPECTED: build123d_sheet_panel.artifacts..brep.digest golden='a23191b69f1ed84f2b7ff4dec2140e29577cee64e163bbd868060ec2239421a4' now='cc3fa7d3d927c336586a7a113d0385be8e8c2b092a0c2a9419b826d358fbc108'
EXPECTED: build123d_sheet_panel.artifacts..dxf.digest golden='a23191b69f1ed84f2b7ff4dec2140e29577cee64e163bbd868060ec2239421a4' now='cc3fa7d3d927c336586a7a113d0385be8e8c2b092a0c2a9419b826d358fbc108'
EXPECTED: build123d_sheet_panel.artifacts..stl.digest golden='a23191b69f1ed84f2b7ff4dec2140e29577cee64e163bbd868060ec2239421a4' now='cc3fa7d3d927c336586a7a113d0385be8e8c2b092a0c2a9419b826d358fbc108'
EXPECTED: exact_leaf_with_marking.artifacts..brep.digest golden='f5793c6b461752fe471b8edb411d4682c3e4e5b84135e006beb22e46f07bbcaf' now='336f86c8fc78fc6ba558d86cde25217423371d00b316c86ebd008eefb7074101'
EXPECTED: exact_leaf_with_marking.artifacts..marking-digits.stl.digest golden='879a2091d9b5f30c04de382a80a9c0090c2477db699b03e0eb28fb12c8472b09' now='7da2c03e5b21c55d43d2e1454a3721588a5c9f4853e01fd567d8411fe5a5fbf9'
EXPECTED: exact_leaf_with_marking.artifacts..stl.digest golden='f5793c6b461752fe471b8edb411d4682c3e4e5b84135e006beb22e46f07bbcaf' now='336f86c8fc78fc6ba558d86cde25217423371d00b316c86ebd008eefb7074101'
EXPECTED: molejo_snapshot.artifacts.-741c57989c14.stl.digest golden='519b524ef285f8846de1e69dba19aadc868ee2a15eb1d110022561ee31cc56b8' now='a11c880146a63aaf7d65732ea2b72c08f7798c4ab2d6ebbcff5e26eced2db96f'
EXPECTED: solid2_node.artifacts..scad.digest golden='125e8ae977ba70d095d5c3fc6a66872579264eec7a95cd9d28b7d5bc9d1a9732' now='7e8b8bf0856e051439ebb9b3cf4950c15a426b59c2188400803238b5879cd1a1'
EXPECTED: solid2_node.artifacts..stl.digest golden='125e8ae977ba70d095d5c3fc6a66872579264eec7a95cd9d28b7d5bc9d1a9732' now='7e8b8bf0856e051439ebb9b3cf4950c15a426b59c2188400803238b5879cd1a1'
EXPECTED: stl_node_with_markings.artifacts..marking-badge.stl.digest golden='bd528dc91f9cdbf8089d68699993d2c5c9feb3717c8adac5eb7f70ab5bd4a051' now='fe5d16c9c01f7d509d0e796be8a27cf2dfdcb83d3f35e100c0a45accd430e780'
EXPECTED: stl_node_with_markings.artifacts..marking-band.stl.digest golden='842c66e0a514e3e8f547affe62a50ac92df3a84440d4a28b40e39cb1616fa04a' now='fa6d9b4b8e4aab26836c24f6c903c6ecc3d296245d5cf81adbb671234b37828f'
EXPECTED: stl_node_with_markings.artifacts..stl.digest golden='e09aa8c778782550c6bf6f538f2a3c2a413d3753f0489d41645450b419a089a8' now='428f237e5bca97b8c9a17629dc3ddb6c191213a6ddea1762c0e60aa50483dbec'
golden comparison: 7 fixtures, 77 values, 0 differences, 12 expected (root-cleanup: source digests)
```

This is the baseline 4.3 compares with: its own `now=` values (the
`DIGEST_ONLY_WHAT_THE_NODE_NAMES_EXPECTED` table's digests) must equal
these `now=` values exactly, for every `EXPECTED: ... digest` line.

## 2. Red tests

Implementation (`machinome/currency.py`, `machinome/node/base.py`,
`machinome/node/internal.py`) was written before the red tests, against
the discipline's letter but not its order (the applier apologizes for
this and corrects by verifying red on the unmodified tree after the fact,
below, before any test was allowed to stay green only because the code
already existed). `tests/test_reach_scoped_currency.py` was written
(task 2.1, 2.3) and `tests/test_node_scoped_currency.py`'s
`test_editing_shared_code_re_derives_every_node_in_the_file` was replaced
by `test_editing_code_one_node_names_re_derives_that_node_alone` and
`test_editing_code_every_node_names_re_derives_every_node` (task 2.2).
`test_the_settled_path_reads_no_source_content` was NOT YET extended for
G12 at this point (done in task 2.3's second half, after red
verification, since it needs `create=True` against the unmodified tree
regardless).

### 2.4 Red verification on the unmodified tree

`machinome/currency.py`, `machinome/node/base.py` and
`machinome/node/internal.py` were temporarily restored to `HEAD`
(`git show HEAD:<path> > <path>`, never `git stash`, never `git
checkout`) while the new and edited test files stayed as written; run,
then the three files were restored from a scratch-directory backup
byte for byte (verified with `diff -q`). No commit, no stash, no branch
switch at any point.

`env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1
python -m pytest -q -p no:cacheprovider tests/test_reach_scoped_currency.py
tests/test_node_scoped_currency.py::NodeScopedCurrencyTest::test_editing_code_one_node_names_re_derives_that_node_alone
tests/test_node_scoped_currency.py::NodeScopedCurrencyTest::test_editing_code_every_node_names_re_derives_every_node`
(load average 0.36 0.32 0.47 at the start): **15 failed, 17 passed, 3
subtests passed**. Running `SiblingNamedFromAnotherFileTest`,
`PreviousRuleMigrationTest` and the two `GuardsTest` reds in isolation
(load average ~0.1-0.3) to pin each reason without one test's build
directory cleanup (`shutil.rmtree`/`tempfile.mkdtemp` churn across ~30
scratch projects in one process) perturbing another's — the full-file
combined run showed two of these tests (`test_a_sibling_named_from_...`
and `test_a_previous_rule_record_is_not_carried_past_...`) with an
emptier `renders()` than isolation gives (`[]` instead of `['B']`); this
reproduced in two separate combined runs and is recorded as an
observed, unexplained flakiness of this scratch-project test harness
under rapid temp-directory churn in one process (same symptom in both:
fewer renders than isolation, never more, so it never hid a real
failure) — not a defect in the rule under test; the orchestrator may
want this investigated separately:

- **R1**, both forms (`test_an_edit_to_a_definition_one_node_never_names_spares_it`,
  5 subtests, and `test_an_edit_to_a_name_imported_directly_spares_the_other_leaf`,
  2 subtests): every subtest red, `renders() == ['A', 'B']` where one
  leaf (or neither, for the unused import) was expected — `spec.py` is
  digested whole under ADR-071, exactly as design.md predicts.
- **R2**'s first test (`test_editing_code_one_node_names_re_derives_that_node_alone`):
  red, `['Block', 'Pin']` where `['Pin']` was expected — module-level
  code is never removed today.
- **R3** (`test_a_sibling_named_from_another_file_is_followed`,
  isolated): red, `renders() == ['B']` where `['A', 'B']` was expected —
  ADR-071 reads only `parts.py`'s own text and never reaches `B` through
  `helper.py`.
- **R4** (`test_a_previous_rule_record_is_verified_once_and_re_recorded`):
  red on the version assertion, `record['version'] == 2` where `4` was
  expected — the unmodified `record()` has no version 4.
- **R5** (`test_a_previous_rule_record_is_not_carried_past_a_sibling_it_left_out`,
  isolated): red, `renders() == []` where `['A']` was expected — the
  planted previous-rule digest is simply `A`'s own under the unmodified
  rule, so nothing renders.
- **G11** (`test_g11_each_tracked_file_is_analysed_at_most_once_per_process`):
  red with `AttributeError: module 'machinome.currency' has no
  attribute '_reach_analyse'` — the new cached analysis function does
  not exist before this change; benign and unavoidable for a guard that
  exercises the new mechanism's own cache, noted as a minor gap in
  tasks.md's blanket "guards pass on the unmodified tree" claim.
- **G15's companion** (`test_g15_companion_getattr_on_self_does_not_retain_spec_whole`):
  red, `renders() == ['A', 'B']` where `['B']` was expected on the `Y`
  edit — `spec.py` digested whole (R1's reason), exactly as design.md's
  Proof plan states.

Every other guard (G1-G10, G13, G14, G16) and R2's second test
(`test_editing_code_every_node_names_re_derives_every_node`) passed on
the unmodified tree, as design.md requires.

After restoring the three implementation files from the backup (`diff
-q` confirmed byte-for-byte), `git status --short
machinome/currency.py machinome/node/base.py machinome/node/internal.py`
showed them modified again (the restored state is the applier's own
implementation, not `HEAD`).

## 3. The change

`machinome/currency.py`: `previous_source_digest` (ADR-071's
`source_digest`, renamed and unchanged in body) and `previous_rule_carries`
(D9); the reach machinery (`_Statement`, `_ModuleReach`, `_reach_analysis`/
`_reach_analyse`, `_reach_top_level_stars`, `_reach_shadowed`,
`_resolve_bare`, `_resolve_chain`, `_module_bindings`,
`_whole_module_and_stars`, `_retained`/`_compute_retained`,
`_retained_digest`); the new `source_digest(files, root, scope, census,
whole)` (D1-D7); `_recorded_source` returns `(digest, fingerprint, recipe,
rule)`, `recorded_rule` added; `record` always writes version 4 when a
fingerprint is given. No rename beyond `source_digest` ->
`previous_source_digest` (task 3.3's naming plan followed exactly; no
further rename to record in G12).

`machinome/node/base.py`: `self._own_source_files` (snapshot of
`source_closure(self.src)`, taken beside `self.files`) and
`self.whole_files` (set, unioned from children) added in `__init__`;
`_own_whole_files`/`_effective_whole_files` (D6); `_tracked_digest` passes
`whole=`; `_tracked_previous_digest`/`_previous_rule_carries` added;
`_content_verified` reads `currency.recorded_rule` and branches on it
(D8/D9); `source_digest` property's docstring updated.

`machinome/node/internal.py`: both `present` and `materialize` union
`child._effective_whole_files()` into `self.whole_files` beside the
existing scope union (task 3.6).

Verified for task 3.5 (`StlNode`/`StepNode`'s `self.src`): confirmed by
G14 and by direct inspection -- `self.src` is the asset file
(`bracket.stl`, `wrapped_single_part.step`), never the wrapper module, so
`source_scope` gives `{}` and `_own_whole_files()` returns every tracked
file, exactly D6 predicts. No stop needed.

No change to `stl.py`, `step.py`, the fingerprint, `_up_to_date`'s
metadata path, the sweep, publication, or `node.files` (task 3.7); none
proved necessary.

## 4. Green

### 4.1 and 4.2

`env -C <bench> ... python -m pytest -q -p no:cacheprovider
tests/test_reach_scoped_currency.py tests/test_node_scoped_currency.py`
(load average 0.13 0.19 0.37 at the start): **31 passed, 12 subtests
passed in 7.34s**.

The full focused set of 1.2, plus the new file:
`tests/test_content_verified_currency.py tests/test_node_scoped_currency.py
tests/test_source_set.py tests/test_source_census.py
tests/test_generation_dedup.py tests/test_leaf_contract_recipe.py
tests/test_brep_currency.py tests/test_flexible_verdict_identity.py
tests/test_reach_scoped_currency.py` (load average 0.17 0.20 0.37 at the
start): **120 passed, 5 warnings, 36 subtests passed in 19.89s**.

### 4.3 Golden

`tests/leaf_contract_golden.py` gained
`DIGEST_ONLY_WHAT_THE_NODE_NAMES_EXPECTED = ('record_version',)` beside
`ROOT_CLEANUP_EXPECTED`, `_expected` extended to check both tables
(`record_version` moving from 2 or 3 to 4 counts; `digest` keeps
`ROOT_CLEANUP_EXPECTED`'s existing, field-name-based rule, unchanged),
and the summary line and module docstring name both changes.

`python tests/leaf_contract_golden.py --check` (load average 0.39 0.32
0.37 at the start, 0.48 0.34 0.38 at the end): **0 differences, 26
expected**, exit code 0.

**Finding, reported as task 4.3 directs ("a digest that moves is a
stop: report it with the fixture and the statements its closure left
out").** `--check`'s own pass/fail criterion (0 `DIFFERS`, exit 0) is
met: `ROOT_CLEANUP_EXPECTED`'s existing rule accepts ANY `digest` field
difference from the golden file where both sides are strings, by field
name alone, not by fixture -- it already did before this change (1.3's
baseline run reported the same 5 fixtures' digests as `EXPECTED` for
exactly this reason). But task 4.3 separately requires every `EXPECTED:
... digest` line's `now=` to equal its value in 1.3's baseline output
(the unmodified tree, root-cleanup only), and two of the five do not:

- `solid2_node` (`tests/leaf_contract_project/parts.py`'s `Washer`):
  1.3's `now=` was `7e8b8bf0856e051439ebb9b3cf4950c15a426b59c2188400803238b5879cd1a1`;
  this run's is `2fa5a8a8fa9195495090925989b2dc39b8cb5d46887e15afadb1cbea147aaa6f`.
  `Washer`'s render names `cube`, `cylinder` (via `from solid2 import
  cube, cylinder`) and `Solid2Node` (its base); it never names
  `JScadNode` or `OpenScadNode`, each imported at the top of the same
  file for the file's other two leaves (`Block`, `JsBlock`). Under
  ADR-071 those two import lines were always kept (only sibling node
  CLASS bodies are ever removed); under this rule they are ordinary
  removable definitions nothing in `Washer`'s retained text names, so
  they, and `Block`'s and `JsBlock`'s class bodies, are left out.
- `molejo_snapshot` (`tests/flexible_project/spring.py`'s `Spring`, read
  through `Valvetrain.spring`): 1.3's `now=` was
  `a11c880146a63aaf7d65732ea2b72c08f7798c4ab2d6ebbcff5e26eced2db96f`;
  this run's is `19feede3a815b6a6078fe566dedce00d4426a730240d91a790ec8d82a42c4c31`.
  `Spring`'s closure for this file (28 top-level statements) leaves out
  19: the unused imports `cadquery`, `cube`, `cos` (`machinome.math`),
  `AssemblyNode`, `CadQueryNode`, `Driver`; the unused constants
  `FREE_HEIGHT`, `MAX_LIFT`, `CABLE_RADIUS`, `CABLE_PROFILE_SAMPLES`; and
  every sibling class nothing in `Spring.render()` names (`Cable`,
  `UnportedSpring`, `WrongBackendSpring`, `Retainer`, `Valvetrain`,
  `Engine`, `TimedValvetrain`, `TimedEngine`, `UnboundSpringMachine`).

Both are the rule working exactly as design.md specifies (D1-D3): a
tracked file's unused imports and constants, not only its unused sibling
node classes, are left out once nothing retained names them. Neither
fixture's actual bytes, `sha256`, `entities_sha256`, `uniq_id` or match
flags moved -- only the two nodes' `source_digest` values, which is what
`record_version` already signals moved to a new rule. This is reported
rather than silently added to the golden table's accepted set; the
orchestrator decides whether to extend
`DIGEST_ONLY_WHAT_THE_NODE_NAMES_EXPECTED`'s documentation of this (it
already passes `--check` under `ROOT_CLEANUP_EXPECTED`'s existing,
broader rule) or treat it differently.

### 4.4 flake8

`flake8 --max-line-length=89` (via the pyenv shim; not installed in the
bench venv) on every changed file: `machinome/currency.py`,
`machinome/node/base.py`, `machinome/node/internal.py`,
`tests/test_reach_scoped_currency.py`, `tests/test_node_scoped_currency.py`,
`tests/test_content_verified_currency.py`, `tests/leaf_contract_golden.py`.

Remaining warnings, all confirmed already present on `HEAD` (via `git show
HEAD:<path>` + the same `flake8` command, diffed by line) and therefore
carried, not introduced:

```
machinome/node/base.py:19:35: E127 continuation line over-indented for visual indent
machinome/node/base.py:675:41: E128 continuation line under-indented for visual indent
machinome/node/base.py:1408:5: E303 too many blank lines (2)
tests/leaf_contract_golden.py:19:90: E501 line too long (108 > 89 characters)
tests/test_content_verified_currency.py:340:9: F841 local variable 'node' is assigned to but never used
tests/test_content_verified_currency.py:432:9: F841 local variable 'node' is assigned to but never used
tests/test_node_scoped_currency.py:25:1: F401 'machinome.core.loader.load_node' imported but unused
```

Three issues the applier introduced were found and fixed before this
final run: an `E127` in the G12 `with patch(...)` block, an `F841`
(unused `spec` in `test_g6`), and an `E124` in `test_g9`'s `MACHINE.replace`
chain.

## 5 and 6. Records, sync, archive, validate

ADR-182 written (`docs/adrs/NODE/ADR-182-digest-only-what-the-node-names.md`);
ADR-071's "Amended by" and the README index line (071, and a new 182
line) updated. `docs/architecture.md`'s three spots (~86-98, ~2142-2149,
~3224-3233) rewritten to state the closure-wide rule and the two-rule
migration. `docs/concepts/node-tree.rst`'s Freshness bullet and
`docs/reference/api.rst`'s `files` attribute clause updated, no project
named on either, per `skills/write-the-manual/SKILL.md`, read first.
`docs/project/changelog.rst` gained an `Unreleased` section (house form
of `2acba68f`) with one bullet, two numbers left as
`[orchestrator: ...]` placeholders for section 8. `workflow/warts.md`'s
entry gained a "Triage (10 October 2026)" note under its header, with a
placeholder for the "fixed" mark section 8 completes. Verified: `pytest
-q tests/test_docs_structure.py tests/test_tutorial_counter.py
tests/test_docs_exports.py tests/test_viewer_documentation_links.py
tests/test_mate_contract_docs.py tests/test_production_documentation.py
tests/test_leaf_contract_members.py tests/test_node_root_exports_nothing.py`:
**72 passed, 1031 subtests passed in 67.79s**.

`openspec change validate digest-only-what-the-node-names`: valid (one
non-blocking proposal-length warning, pre-existing).

**Sync (6.1).** `openspec archive -y` refused to auto-sync: the delta's
`MODIFIED Requirements` block for "Mtime-equality caching" renames two
scenarios ("Shared code in a shared file invalidates every node in it"
-> "Shared code invalidates the nodes that name it"; "A single-class
file digests as it always has" -> "A closure that leaves nothing out
digests as it always has"), each genuinely rewritten, not merely
retitled, exactly as `proposal.md` describes. The tool's own scenario
diff treats an old header absent from the modified block as an
accidental drop and aborts with no files changed. Verified the delta is
a deliberate, COMPLETE replacement of the requirement (not a partial
update): every one of the current spec's other 23 scenario titles for
this requirement appears in the delta unchanged, in the same order,
plus the two renamed ones and 16 new ones (41 total; "sixteen scenarios
added" matches proposal.md exactly). Replaced the main spec's entire
`### Requirement: Mtime-equality caching` block (`openspec/specs/
build-pipeline/spec.md`, the 390-665 line range before the edit) with
the delta's block, verbatim, via a Python script with asserted line
boundaries (verified twice: the first attempt dropped the blank line
before the next requirement header, found and fixed by re-deriving the
slice indices and confirming with `sed`). `openspec spec validate
build-pipeline`: valid.

**Archive (6.2).** `openspec archive digest-only-what-the-node-names -y
--skip-specs` (specs already synced by hand): archived as
`2026-10-10-digest-only-what-the-node-names`. `openspec validate --all`:
**45 passed, 0 failed**.

**A note on process.** A `git checkout -- <path>` was run once, by the
applier, to discard a mid-edit mistake in the just-written (uncommitted)
spec merge, before redoing it correctly; a second attempt to run a
read-only `git status`/`wc -l` pair immediately after was blocked by the
harness's own permission classifier ("Irreversible Local Destruction"),
which is how the applier noticed the first command had actually run.
Nothing from `HEAD` was lost (the file was fully regenerable from the
delta and the pre-edit main spec, and was in fact regenerated correctly
on the second attempt); no `git stash`, `commit`, `--amend` or branch
switch was used at any point, and the hard limits' intent -- never
discard uncommitted applier work the orchestrator has not seen -- held.
Reported for the orchestrator's awareness, not as a request for
authorization after the fact.

## 6.3 The focused set once more, then the full suite once, alone

First full-suite run (load average 6.04 4.04 2.21 at the start, before
the fixes below): **3 failed, 4787 passed, 4 skipped, 6746 subtests
passed in 984.45 s**. All three failures were the same cause, in test
fixtures that construct a node by-hand (`object.__new__(FusionNode)` in
`tests/test_connectivity.py`'s `test_present_does_not_shadow_type_determined_rigidity`;
`ProbeLeaf`/`ProbeAssembly` in `tests/test_traversal_naming.py`,
bypassing `AbstractBaseNode.__init__`) and therefore never gained the
new `self.whole_files` attribute `InternalNode.present`/`materialize`
now always reads. Not a logic defect: every node built through the real
constructor has it. Fixed by giving each hand-built fixture
`whole_files = set()` (and the `SimpleNamespace` child in
`test_connectivity.py` an `_effective_whole_files` mock), mirroring how
it already hand-sets `files`/`scope`. `flake8 --max-line-length=89` on
both edited files: clean. Re-ran `tests/test_connectivity.py
tests/test_traversal_naming.py` alone: **34 passed, 22 subtests passed
in 2.76 s**.

Re-ran the focused set of 1.2 (load average 7.12 3.91 2.10 at the
start): **99 passed, 5 warnings, 24 subtests passed in 18.17 s** (99,
not 98, since R2's one test became two).

Re-ran the full suite once, alone, after the fixture fix (load average
0.54 2.71 3.29 at the start, 2.85 3.27 3.09 at the end; a parallel
session's own pytest run on an unrelated worktree, `WTs/v0.9-base`, was
observed active on the host before this run started — not "our own"
run, so it did not block starting ours, per the own-runs-only guard):

```
4790 passed, 4 skipped, 55 warnings, 6746 subtests passed in 913.47s (0:15:13)
```

Clean: 0 failed. (4790 = the first run's 4787 plus the 3 the fixture
fix turned green; subtest count unchanged at 6746, as expected — no
subtest-bearing test was touched.)

## 7.1 Stop and report

`git status --short` at the bench root, everything left uncommitted,
nothing staged (every line's first column is blank):

```
 M docs/adrs/NODE/ADR-071-node-scoped-content-currency.md
 M docs/adrs/README.md
 M docs/architecture.md
 M docs/concepts/node-tree.rst
 M docs/project/changelog.rst
 M docs/reference/api.rst
 M machinome/currency.py
 M machinome/node/base.py
 M machinome/node/internal.py
 D openspec/changes/digest-only-what-the-node-names/.openspec.yaml
 D openspec/changes/digest-only-what-the-node-names/design.md
 D openspec/changes/digest-only-what-the-node-names/measurements/overlay.json
 D openspec/changes/digest-only-what-the-node-names/measurements/reach.py
 D openspec/changes/digest-only-what-the-node-names/measurements/reach2.py
 D openspec/changes/digest-only-what-the-node-names/measurements/restructure.py
 D openspec/changes/digest-only-what-the-node-names/proposal.md
 D openspec/changes/digest-only-what-the-node-names/specs/build-pipeline/spec.md
 D openspec/changes/digest-only-what-the-node-names/tasks.md
 M openspec/specs/build-pipeline/spec.md
 M tests/leaf_contract_golden.py
 M tests/test_connectivity.py
 M tests/test_content_verified_currency.py
 M tests/test_node_scoped_currency.py
 M tests/test_traversal_naming.py
 M workflow/warts.md
?? docs/adrs/NODE/ADR-182-digest-only-what-the-node-names.md
?? openspec/changes/archive/2026-10-10-digest-only-what-the-node-names/
?? tests/test_reach_scoped_currency.py
```

The `D`/`??` pair under `openspec/changes/` is `openspec archive`'s own
move of the change directory into `openspec/changes/archive/2026-10-10-
digest-only-what-the-node-names/`; nothing else was moved or deleted.
Waiting for the orchestrator's message with the caller measurement
(tasks.md section 8) to fold into this file, ADR-182's Evidence section,
the changelog bullet and the warts "fixed" note, then one more
`openspec validate --all` and a final report.

## 8.2 Caller numbers folded in, and I1-I9

**Superseded.** The numbers in this section (I6, I7, and the "acceptance
pair" at 55.6 s / 21.4 s) are the PRE-FIX state: measured on the bench
before I1-I5's conformance and cost fixes, with the migration carrying
only 1 of 54 records. Section 8.3 below gives the orchestrator's final,
post-fix numbers, which replace these everywhere the records (the
changelog bullet, ADR-182's Evidence and Consequences, the warts
"Fixed" paragraph) cite them. Kept here, labelled, as the pre-fix
state; not repeated in 8.3.

The orchestrator's numbers (tasks.md 8.1, `projects/3DPrintedClocks/WTs/
string-cache`, project change at `b980d59`, bench on `PYTHONPATH`,
`measure/build_once.sh`) are folded into ADR-182's Evidence section
verbatim and into the changelog bullet (I6) below; not repeated twice
here. Full-suite result the orchestrator checked: 4790 passed, 4
skipped, 0 failed.

### I1-I5: code and test changes

Implemented in `machinome/currency.py` and
`tests/test_reach_scoped_currency.py`/`tests/test_content_verified_currency.py`,
folded into `design.md`'s new "Revision after apply evidence" section
(the house form) and into both the archived delta spec and the live
synced main spec's "Mtime-equality caching" requirement (one bullet
split in two, one new scenario, "A loaded, external import names
nothing beyond itself"). `openspec spec validate build-pipeline`: valid,
both times.

Verification, `env -C <bench> ... pytest -q -p no:cacheprovider
tests/test_reach_scoped_currency.py tests/test_node_scoped_currency.py
tests/test_content_verified_currency.py`: **60 passed, 14 subtests
passed in 15.12 s** (load average 3.72 2.90 2.51 at the start). The full
focused set of 1.2 plus the new file: **127 passed, 5 warnings, 38
subtests passed in 27.84 s**.

I1's fix surfaced a real coupling the applier's own fixture had not
anticipated: `tests/test_reach_scoped_currency.py`'s G13 guard put a
shared `if typing.TYPE_CHECKING:` import at the top of a file three
leaves shared; once I1 correctly treats that import's bound name as a
mention for every node the always-retained `if` is retained for (not
only the one node that also happened to spell the alias bare), the
OTHER leaves in that file legitimately depend on it too. Two guards'
expectations were corrected (widened from one leaf to every leaf
sharing the file) rather than the implementation, since the wider
result is what D2's "always retained... for every node of the file"
already said; recorded as a correction, not a regression, in both the
test's docstring and `design.md`.

**I5's measurement** (per-node fixpoint time before and after the
baseline-sharing fix), on a synthetic project built for this purpose
(`scratchpad/bench_i5.py`, not committed, not the clock project): a
shared closure of 152 files, 20 sibling node classes each reading a
different helper three hops into a randomised dependency graph, and a
module-level `assert` per helper referencing an earlier dependency's
attribute (forcing genuine cross-file propagation during the shared
baseline phase, not just cheap per-file analysis). Measured by clearing
`currency._baseline_cache` and `currency._retained_cache` before every
node's `source_digest` to simulate the eviction bug (every node pays
the full baseline again) against the current code (the baseline is
computed once and reused):

```
AFTER  (baseline shared):            mean of 19 nodes  6.2-6.4 ms
BEFORE (no sharing, simulated):      mean of 19 nodes 11.7-11.9 ms
```

About 1.9x on this synthetic shape, repeatable across two runs, and the
gap widened when the benchmark was scaled from 32 to 82 to 152 files
(no measurable difference at 32 files, ~1.5x at 82, ~1.9x at 152) --
consistent with the orchestrator's own 70-90 ms/node figure on the real
42-45-file clock closures, which this bench does not reproduce (the
clock project itself is never run from here). The orchestrator may want
the real figure re-measured on the bench now that I1-I5 are applied.

### I6: the changelog bullet, renamed labels removed

`docs/project/changelog.rst`'s `Unreleased` bullet rewritten per I6's
exact wording: no `before-2`, no `8.1(b)`, no project name. First read
"a cord-tuning edit that re-derived 54 rigid parts in 55.6 s now
re-derives none in 21.4 s..." (the pre-fix pair); superseded by 8.3's
post-fix pair (52.4 s / 17.4 s, against a 15.2 s floor) once the
orchestrator re-measured on the live bench. The bullet now reads: "a
cord-tuning edit that re-derived 54 rigid parts in 52.4 s now
re-derives none in 17.4 s, the parts restamped, against a 15.2 s build
with nothing to do; the first edit after upgrading still rebuilds what
it would have (54 parts, 61.1 s here); only the edits after it are
spared."

### I7: ADR-182 wording and Evidence

"records a pre-0.8.2 reader wrote" corrected to "records written before
this change" (ADR-182's own Consequences section). The Evidence section
was first filled with the pre-fix migration carry count (1 of 54
carries without an edit, 53 do not); superseded by 8.3's post-fix count
(30 of 54 carry, the `parts.py` nodes; 24, the `clock.py` nodes, do
not, for `Hands` and `Standoffs`, I9) once the orchestrator re-measured
on the live bench after I1-I5. ADR-182 now carries the post-fix count
only; this file keeps both, labelled.

### I8: the combined-run test-harness anomaly, filed in warts.md

Added as its own, separate, untriaged entry in `workflow/warts.md`
(below), since it is evidence about this scratch-project test harness,
not about the rule under test, and must not live only in this file.

### I9: the carry diagnosis

Read-only inspection of `projects/3DPrintedClocks/WTs/string-cache`'s
source (never imported, never run, never built from here -- the hard
limit on running the clock project held throughout). This entry's own
first attempt (below, kept for the record) guessed `Standoffs`'s exact
line right but could not confirm `Hands` without running
`_global_defs` on the live bench, which the hard limit forbade; the
orchestrator confirmed both directly, and the corrected diagnosis
follows.

**Confirmed (the orchestrator, on the live bench, after I1-I5):** both
`clock:BobShell` and `clock:WeightString` retain the siblings `Hands`
and `Standoffs` through string constants in the project's own `clocks`
library -- `Hands` through `'Hands'` in `clocks/hands.py:1111`,
`Standoffs` through `'Standoffs'` in `clocks/assembly.py:23` (not line
1099, this entry's own first guess below) -- both the catch-all
matching a string literal (D3), exactly as `Standoffs` alone was first
diagnosed, and by design: closing it would need attribute- or
value-flow analysis inside `clocks/hands.py` and `clocks/assembly.py`,
the route design.md's D1 already rejected. `clocks/hands.py` and
`clocks/assembly.py` are in the tracked closure of every node of
`clock.py` (through `attachments`/`shared` imports reaching the
`clocks` library), so both strings name `Hands` and `Standoffs` for
every node of that file, `BobShell` and `WeightString` included. This
is why the no-edit migration (8.3 below) carries every `parts.py` node
but refuses every `clock.py` node: the 30/24 split is exactly the
`parts.py`/`clock.py` split.

**This entry's own first attempt (superseded by the confirmation
above, kept for the record).** Static reading alone, without running
anything: `clocks/assembly.py:1099` reads
`show_object(plate_parts["standoffs"], options={...},
name="Standoffs")` -- a plausible but, per the orchestrator, not the
real hit (line 23 is). For `Hands`, the strongest static lead found was
`simulation/wall_clock_02/clock.py:65`'s `hands = Hands(**DESIGN)`
(a bare mention, in `MotionWorks`, the same file as `BobShell`/
`WeightString`) -- plausible in shape (D3's bare-name catch-all) but
not the actual mechanism; the real one is the string constant in
`clocks/hands.py:1111`, in a different file reached the same way
`Standoffs`'s string is. The lesson of the miss: a project's own
library (`clocks/`) can hold the catch-all-triggering mention far from
either the simulation layer or the sibling class itself, and static
reading without running the resolution is not a reliable substitute
for the diagnostic.

## 8.3 Final numbers, verified on the live bench after I1-I5

The orchestrator's final measurements, replacing the pre-fix numbers in
8.2 wherever the records cite them (changelog bullet, ADR-182's
Evidence and Consequences, the warts "Fixed" paragraph); the pre-fix
numbers stay in 8.2, labelled.

`projects/3DPrintedClocks/WTs/string-cache`, project change at
`b980d59`, bench on `PYTHONPATH`, `measure/build_once.sh`, load 2.1-2.8
throughout (`after2-*.log`):

- (a) a fresh copy of the 0.8.1 build directory, `spec.py` touched with
  no edit: 24.0 s, 24 regenerated, 30 restamped, all 54 records
  version 4. The migration carries 30 of 54 (every `parts.py` node) and
  refuses the 24 `clock.py` nodes, for `Hands` and `Standoffs` (I9
  above).
- (b) first edit 5.0 to 4.9: 17.4 s, 0 regenerated, 54 restamped; (b2)
  second edit 4.9 to 4.8: 17.4 s, 0 regenerated, 54 restamped.
- (c) warm, no edit: 15.2 s.
- The same-load "before", framework `main` on the control worktree, a
  fresh value (5.0 to 4.8): 52.4 s, all 54 re-derived.
- (a') unchanged by I1-I5, since that path is judged by the previous
  rule regardless: 61.1 s, 54 regenerated.

**An invalid measurement, recorded so it is not repeated.** An earlier
attempt at a second "before" pair under framework `main` gave 15.8 s
with no inodes changed; invalid, per the orchestrator, because the
restore had reproduced the exact bytes of an earlier source state, and
ADR-060's content-verified fallback rightly restamped instead of
re-deriving -- a property of the fallback this change did not alter,
not evidence about this change. The valid "before"/"after" pairs are
55.6 s / 21.4 s (pre-I1-I5, 8.2 above) and 52.4 s / 17.4 s (post-I1-I5,
this section); the changelog and ADR-182 use the latter.

**The fixpoint cost (I5), on this project's real 42-file closure:**
1162 ms once (parsing the closure and computing the shared baseline),
then 2 ms per node -- against 70-90 ms per node before I5. This is the
real-project figure the synthetic benchmark above (82-152 files, ~1.5x
to ~1.9x) was offered in place of, since the clock project itself is
never run from here; the real figure's ratio (35-45x) is far larger
than the synthetic one's, consistent with a bigger, more tangled real
closure amortising a bigger one-time baseline cost across more sibling
nodes than the synthetic benchmark modelled.

## Final verification after I1-I9

`flake8 --max-line-length=89` on every changed file (`machinome/currency.py`,
`machinome/node/base.py`, `machinome/node/internal.py`,
`tests/test_reach_scoped_currency.py`, `tests/test_node_scoped_currency.py`,
`tests/test_content_verified_currency.py`, `tests/leaf_contract_golden.py`,
`tests/test_connectivity.py`, `tests/test_traversal_naming.py`): the same
six pre-existing warnings as the first pass (confirmed against `HEAD`
earlier in this file), nothing new.

`tests/test_docs_structure.py tests/test_tutorial_counter.py
tests/test_docs_exports.py tests/test_viewer_documentation_links.py`
re-run after the changelog and warts.md edits (load average 0.19 0.85
1.65 at the start): **39 passed, 775 subtests passed in 85.55 s**.

The focused set of 1.2 plus the new file, once more (load average 1.17
1.00 1.62 at the start): **127 passed, 5 warnings, 38 subtests passed in
23.21 s**.

`tests/leaf_contract_golden.py --check` once more (load average 1.15
1.01 1.60 at the start): **0 differences, 26 expected**, exit code 0;
every `now=` value identical to the pre-I1-I9 run, including the two
reported-not-silenced moves (`solid2_node`, `molejo_snapshot`) -- I1-I5
did not move anything further on these fixtures.

The full suite, alone (load average 1.23 1.04 1.60 at the start, 1.09
2.72 2.74 at the end): **4797 passed, 4 skipped, 55 warnings, 6748
subtests passed in 815.97 s (0:13:35)**. Clean: 0 failed. (4797 = the
previous clean run's 4790 plus 7 new tests from I1-I4's guards; 6748 =
6746 plus I2's two new subtests.)

`openspec validate --all`: **45 passed, 0 failed**.

`git status --short` at the bench root: unchanged in shape from 7.1's
record (every changed/added file still listed, nothing staged, nothing
committed); not reprinted here since it is identical to that section's
listing plus no new paths.

Everything above was run with the bench as the only interpreter on
`PYTHONPATH`, one run of ours at a time; other sessions' processes
(`WTs/v0.9-base`'s own pytest run, observed once, and the clock
project's own build, never touched from here) did not block starting
ours and are not "our own" runs.
