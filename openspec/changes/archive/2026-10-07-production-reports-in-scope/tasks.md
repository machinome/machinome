Bench: `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch
`fix-warts-3`.

- Every framework command runs as
  `env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1 /home/asa/devel/machinome/.venv/bin/<tool> ...`,
  with `-p no:cacheprovider` for pytest.
- `<scratch>` is the campaign scratchpad's `cycle11/` directory
  (`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle11/`).
  It holds Stage P's `repro_reports.py`, `probe_markdown.py`,
  `probe_remedies.py`, `probe_holder.py` and `curta_bindings.py`, a
  `pyproject.toml` (`[tool.machinome]`) that gives them a project root,
  and their `.before.out`/`.out` logs. Scratch scripts run as
  `env -C <scratch> PYTHONPATH=<bench>:<scratch> PYTHONDONTWRITEBYTECODE=1 SOLID_BUILD_DIR=<scratch>/_build /home/asa/devel/machinome/.venv/bin/python <scratch>/<script>`,
  filtering out ` INFO -` lines.
- `<project>` is `/home/asa/devel/machinome/projects/Calculators/Curta-Type-I-3x`
  (`main` at `1f3dc22` at Stage P). `<overlay>` is cycle 10's
  `/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle10/curta-overlay/`:
  the production slice's `production/` package from
  `<project>/WTs/production-layer-3x` (`7c9121e`), with the one line
  `from machinome.node import AssemblyNode, StepNode` of
  `production/test_production.py` rewritten as
  `from machinome.node.assembly import AssemblyNode` and
  `from machinome.node.step import StepNode`, beside symbolic links
  `simulation`, `pyproject.toml` and `CAD` to the same names in
  `<project>`. If the scratchpad has lost it, rebuild it that way
  (`openspec/changes/archive/2026-10-07-production-reads-once/evidence.md`,
  1.1). The Curta command, `<curta>`, is:

  ```sh
  env -C <overlay> PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="<bench>:<project>:<overlay>" \
    SOLID_BUILD_DIR=<scratch>/curta-build \
    /usr/bin/time -f 'wall %e s' /home/asa/devel/machinome/.venv/bin/python \
    -m pytest -q -p no:cacheprovider --basetemp=<scratch>/curta-basetemp \
    --rootdir=<overlay> <overlay>/production/test_production.py
  ```

  and `<curta-bindings>` is the same environment running
  `/home/asa/devel/machinome/.venv/bin/python <scratch>/curta_bindings.py`.
  Nothing is written in the project: compare `git -C <project> status
  --short` before and after each Curta run with `<scratch>/curta-status.before`
  (4 untracked entries).
- `<focused>` = `tests/test_model_consumption.py tests/test_production.py
  tests/test_production_documentation.py`.

Rules for the whole cycle:

- Run one test run or build of ours at a time
  (`ps -eo pid,args | grep '[p]ytest\|[m]achinome test\|[m]achinome snapshot\|[m]achinome build'`
  first).
- Every test marked RED in section 2 is run and seen red, for the reason
  it names, before the code that turns it green.
- Write nothing in any project. Record every command and its result in
  `evidence.md` as you go, in the shape of
  `openspec/changes/archive/2026-10-04-scad-presentation/evidence.md`.

## 1. Baseline on the unmodified tree

- [x] 1.1 Create `evidence.md` with the bench commit (`git -C <bench>
  rev-parse HEAD`), the interpreter check (`python -c 'import machinome;
  print(machinome.__file__)'` prints a path under the bench), the Curta's
  head (`git -C <project> rev-parse --short HEAD`) and the slice's head
  (`git -C <project>/WTs/production-layer-3x rev-parse --short HEAD`).
  Copy the sources of `<scratch>/repro_reports.py`,
  `<scratch>/probe_markdown.py`, `<scratch>/probe_holder.py` and
  `<scratch>/curta_bindings.py`, and the overlay recipe above, into
  `evidence.md`, because the scratchpad is not durable.
- [x] 1.2 Run `<scratch>/repro_reports.py`. Expect
  `<scratch>/repro_reports.before.out`: every direct gate case refused,
  the step refused with `unsupported HTML dependency`; in the first
  overlap fixture `left.findings` `()` and every report of `left`,
  `right` and the root refused; in the second, `right.bom` refused; paths
  `kids/arbitrary_name` for a one-member repeat and a one-member tuple,
  `kids-0/…`, `kids-1/…` for two, `kid/arbitrary_name` for a single
  reference.
- [x] 1.3 Run `<scratch>/probe_holder.py`. Expect
  `<scratch>/probe_holder.before.out`: manifest `bindings` `['', 'kids']`
  at `n=1`, `['', 'kids-0', 'kids-1']` at `n=2`.
- [x] 1.4 Run `<curta>`. Record counts and times (Stage P: `6 passed in
  134.08s`, wall 135.36 s, a new build directory). Run
  `<curta-bindings>` and record its output (Stage P:
  `<scratch>/curta_bindings.before.out`, 417 findings, all `unassigned`,
  21 binding paths, wall 29.03 s).
- [x] 1.5 Run `pytest -q -p no:cacheprovider <focused>` and record counts
  and time (Stage P: `57 passed, 4 warnings in 7.27s`, wall 8.32 s).

## 2. Tests

- [x] 2.1 In `tests/test_production.py`, after
  `test_markdown_refusal_is_contextual_and_leaves_no_target`, add
  `test_markdown_gate_accepts_what_is_not_a_dependency` and
  `test_markdown_gate_refuses_html_dependencies_outside_code`,
  parametrized over the two columns of design.md Decision 1 (the cases
  are `ACCEPT` and `REFUSE` in `<scratch>/probe_markdown.py`; the refused
  test takes the rows that are not already in the two existing Markdown
  tests). Each calls `_markdown(text, "declared/step", tmp_path /
  "instruction.md")`. RED today: every accepted case but `5 < 6 > 4` and
  the plain-Markdown line, with `unsupported HTML dependency` (or
  `unsupported local or URL dependency 'local.png'` for the code-span
  link, `'local.pdf'` for the fenced definition), and the refused case
  `[x][ref]` whose only definition is fenced (DID NOT RAISE).
- [x] 2.2 Add `test_an_inequality_in_a_step_is_read`, as design.md
  Decision 4, with `_profile_module`. RED today with `unsupported HTML
  dependency`.
- [x] 2.3 After `test_delegation_ownership_conflict_has_all_declarations`,
  add `test_an_overlap_refuses_only_the_reports_of_its_scope` and
  `test_a_parent_reaching_into_one_child_leaves_its_sibling_readable`, as
  Decision 4 (a module-level `Twice(Production[Submodel])` with Items `a`
  and `b` on `Submodel.nuts`). RED today at `left.bom` and at `right.bom`
  with `ProductionConflictError`.
- [x] 2.4 After `test_zero_repeat_is_not_absent_and_single_repeat_child_stays_tuple`,
  add `test_tuple_binding_members_are_always_indexed`, as Decision 4.
  RED today at `n=1` (`['kids/arbitrary_name'] != ['kids-0/arbitrary_name']`).
- [x] 2.5 Run the new tests on the unmodified code
  (`pytest -q -p no:cacheprovider tests/test_production.py -k
  "not_a_dependency or outside_code or inequality_in_a_step or
  only_the_reports_of_its_scope or leaves_its_sibling_readable or
  always_indexed"`). Record each failure line and the count of red and
  green cases; every red is for the reason named in 2.1 to 2.4.

## 3. The change

- [x] 3.1 `machinome/production/profile.py`: above `_markdown`, the
  private constants and `_rendered_text` and `_html_dependency`; in
  `_markdown`, read the rendered text first and replace the HTML check,
  as design.md Decision 1.
- [x] 3.2 `Production._in_scope`, `findings` through it, and `_read`
  refusing only the overlaps in scope, as Decision 2.
- [x] 3.3 `_Shared.resolve.populate`: the tuple test above the loop and
  the members named by it, as Decision 3.
- [x] 3.4 Run 2.5's selection: all green. Run `<focused>`: 1.5's count
  plus the new cases, all passing.
- [x] 3.5 `git -C <bench> status --short` lists only
  `machinome/production/profile.py`, `tests/test_production.py` and the
  change directory.

## 4. The reproductions and the originating project after the change

- [x] 4.1 Run `<scratch>/repro_reports.py`: the inequalities, the code
  span, the fenced code, `<kbd>` and the code-span link accepted, the
  dependency rows refused; the step read; in the first overlap fixture
  `left`'s reports read (`[2]`, `False`, `()`), `right`'s and the root's
  refused; in the second `right.bom` `[3]`, `left`'s and the root's
  refused; `kids-0/arbitrary_name` for every tuple, `kid/arbitrary_name`
  for the single reference. Run `<scratch>/probe_markdown.py`: `failures:
  0` (it carries its own copy of the gate; it confirms the cases, not
  the bench). Run `<scratch>/probe_holder.py`: `['', 'kids-0']` at
  `n=1`. Record the outputs.
- [x] 4.2 Run `<curta>` again against the same build directory. Expect
  1.4's counts. Record the times beside 1.4's, and the unchanged
  `git status --short`. Run `<curta-bindings>`: the same 417 findings and
  the same 21 binding paths as 1.4.

## 5. Records

- [x] 5.1 `docs/reference/api.rst`, the production section: the three
  edits of design.md Decision 5, and nothing else.
- [x] 5.2 Append Decision 5's bullet to the one `Unreleased` section of
  `docs/project/changelog.rst`, after its existing bullets.
- [x] 5.3 Grep `docs/` (excluding `adrs/` and `releases/`) for
  `ProductionConflictError`, `overlap`, `HTML`, `Markdown`,
  `declaration_path` and `repetition`, and confirm that no other page
  says something this change makes wrong. Record the result.

## 6. Warts

- [x] 6.1 Move the three items of the section "## Findings from the
  adversarial review of the framework cycle `production-layer` (4 October
  2026)" of `workflow/warts.md` verbatim, from "- **The Markdown gate
  refuses text that is not a dependency.**", "- **An overlap anywhere in
  the root blocks an unambiguous child's reports.**" and "-
  **Declaration paths change shape with the repetition count.**" each to
  its "**Untriaged.**", to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md`, under a heading
  `` ## `production-reports-in-scope` `` after the last entry, with a line
  "From "Findings from the adversarial review of the framework cycle
  `production-layer` (4 October 2026)", the items on the Markdown gate,
  the overlap scope and the declaration paths:". Add a "What shipped" paragraph: the gate
  reads what CommonMark renders and refuses a tag that can carry a
  dependency; a binding refuses only for the overlaps in its scope; a
  tuple binding's members are always indexed; the red tests; the
  reproductions before and after; the Curta slice's counts and times
  through the overlay, and why the overlay. Delete the three items from
  `warts.md`; the section's introduction and its other items stay.

## 7. Sync and archive

- [x] 7.1 Sync the delta into `openspec/specs/production-assets/spec.md`,
  replacing the three modified requirements. Diff against the baseline:
  each requirement differs only in its added or changed sentence and its
  added scenario or scenarios.
- [x] 7.2 Archive the change to
  `openspec/changes/archive/<date>-production-reports-in-scope/`. Then
  `openspec validate --specs` passes.
- [x] 7.3 Run `black --check` and `flake8 --max-line-length=89` on
  `machinome/production/profile.py` and `tests/test_production.py`.
- [x] 7.4 Run `<focused>` once more, then the full suite once, alone
  (`pytest -q -p no:cacheprovider` at the bench root), and record counts
  and wall time. A failure that is not this change's is recorded and
  stopped on, not worked around. Leave everything uncommitted.
