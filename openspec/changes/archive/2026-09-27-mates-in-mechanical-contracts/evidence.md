# Apply evidence

Framework worktree: `mates-in-mechanical-contracts`, standalone target `main`.
Planning-only commit: `956d0636e06aff3a042086a01b64757d9d1f46c5`;
base: `49a8fc5cb01852a76b878b55788229ef5857b517`.
Root adversarial review passed and completion was authorized on 2026-09-27.
This record belongs to the single implementation commit following planning.

## Red-first acceptance

Before source changes, `PYTHONPATH="$PWD"
/home/asa/devel/machinome/.venv/bin/python -m pytest
tests/test_mate_contracts.py -q --tb=short` reported **10 failed** in 0.62s.
Failures exercised written/factory mate range Bounds, missing own mate
`constrain`, and mate coordinate selections. Fixture setup was corrected
before recording these contract failures.

Root's independent `tests/test_mate_contract_review.py` subsequently exposed
two regressions red-first: foreign same-named paths could be laundered by
effective-path lookup, and inferred single-joint node reads could bypass
canonical self/duplicate checks. Written ownership is now checked before
effective lookup, and inferred node endpoints include their physical joint.
The four review tests (five subcases) pass. Root also verified the foreign
ownership refusals on the unchanged framework base.

## Framework green evidence

All commands used the workspace venv Python and `PYTHONPATH="$PWD"` from
the framework worktree.

- Acceptance plus independent review: `pytest tests/test_mate_contracts.py
  tests/test_mate_contract_review.py -q --tb=short`: **21 passed, 12 subtests**
  in 1.30s.
- Regression: `pytest tests/test_mates.py tests/test_joints.py
  tests/test_ancestor_constraints.py tests/test_controls.py
  tests/test_inherited_replaced_child_controls.py
  tests/test_port_enumeration_cache.py tests/test_running_reads.py
  tests/test_running_stops.py tests/test_running_simulation.py
  tests/test_clocked_bounds.py tests/test_clocked_refusals.py
  tests/test_running_document.py tests/test_clocked_document.py
  tests/test_simulation_enumeration.py tests/test_profile_running_bound.py
  tests/test_bound_read_demand.py -q --tb=short`: **909 passed, 942 subtests**
  in 34.17s. Four existing FutureWarnings. Includes unchanged ordinary running
  document byte-identity fixtures and existing simple-mate pinned documents.
- Manual/regression acceptance: `pytest tests/test_mate_contract_docs.py
  tests/test_docs_structure.py tests/test_tutorial_counter.py
  tests/test_docs_exports.py tests/test_viewer_documentation_links.py
  tests/test_mate_contracts.py tests/test_mate_contract_review.py -q --tb=short`:
  **51 passed, 136 subtests** in 58.30s, before adding the executable manual
  block check.
- The expanded `test_mate_contract_docs.py`: **3 passed** in 1.14s. The exact
  new Drive codeblock is extracted and executed with its declared Handle/Pawl
  dependencies and running drivers: its original Bound stops at 90; after
  pawl relief of 20, its additive constraint stops at 100.
- `git diff --check`: passed.

Final combined rerun after manual insertion first exposed four existing
manual tests selecting shifted codeblock ordinals: 4 failed, 929 passed,
929 subtests in 34.74s. This was a documentation-test regression, not a
declaration/import-order regression. Those four tests now select semantic
markers through an exact-one helper; all execution and behavior assertions
are preserved. Root reviewed and approved the correction. The final command
combined acceptance, review, executable manual tests and all sixteen
regression files listed above: **933 passed, 954 subtests** in 34.41s,
with four existing FutureWarnings. Strict OpenSpec change validation passed
before archive; strict validation of all **37 baseline specs** passed after
sync/archive. `git diff --check` also passed after completion edits.

The representative ordinary-joint/mate twin verifies bank/control ids,
independent turn/lift, pawl stop and relief, ancestor additive stop, composed
operation poses and exact snapshot replay. It is not a claim of complete
Curta migration; originating-project validation belongs to root.

## Manual build limitation

Strict HTML build `python -m sphinx -b html -n -W --keep-going docs
docs/_build/html` completed output but exited 1 for five existing unresolved
references: `AssemblyNode.simulate`, `AssemblyNode.time`, the `name` keyword,
and the return labels of `Sim.initial` and `Sim.state`. An independent strict
build using the untouched primary framework base and temporary output
`/tmp/mate-contract-docs-base.8hzy3H` produced exactly the same five warnings.
No new warnings were introduced; rendered changed sections were inspected.
Unrelated reference repairs were left outside this change.

## Completion ownership

Root supplied the following originating-project evidence from real Curta,
whose caller edits remain root-owned on project base `fb5505d`:

- Original six `simulation.test_running.RunningCurtaTest` cases: green in
  1009.671s against framework base `49a8fc5`.
- Migrated `python -m unittest -v simulation.test_running.RunningCurtaTest
  simulation.test_mate_refactor simulation.test_running_limits
  simulation.test_running_ratchet simulation.test_running_interlocks
  simulation.test_operating_loop`: **30 tests passed** in 1347.230s, with
  framework worktree on PYTHONPATH, 8 GiB memory cap and BLAS/OMP threads 1.
- Corrected public-declared-children pose comparison: **4 tests passed** in
  6.824s after deliberate 0.2 mm spindle-offset mutation failed red and was
  restored. Meshless simulations leave root.children empty; the corrected
  helper checks the actual declared subtree.
- Finite export: document 13, all 216 old coordinate ids and all 26 control
  names retained, 301 sources, 389 mesh references with all assets present.
  Two native views inspected. Fresh hosted browser pointer lift and selector
  probe passed without errors. Refactored declaration-graph program identity
  changes are expected; this is not a byte-identity claim for refactored Curta.
- Actual crank geometry: 7 faceted checks passed in 114.87s, epsilon 0;
  7 exact checks passed in 97.42s.
- Studio companion `c0f2bfd6dacc9008e7766ecbac24d148294b82aa`: 35 tests and
  skill quick validator passed, committed independently of this repository.
- Root's final framework rerun: 24 tests and 12 subtests passed in 1.32s.

All three delta specs were intelligently synced and verified before archive.
The APPLY agent performs the authorized archive and implementation commit;
root owns local integration and caller commits. No integration, publication
or pushes were performed by the APPLY agent. The next referenced-joint design
is a separate cycle and contributes no scope to this implementation.
