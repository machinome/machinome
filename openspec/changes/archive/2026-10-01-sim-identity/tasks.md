## 1. Red first

- [x] 1.1 Write `tests/test_clocked_identity.py` over
  `tests/clocked_project/counter.py`. It holds four tests. The first
  exports `Counter` with `export_node(..., widget=False)` and asserts that
  `Sim(Counter()).identity` equals the manifest's `clocked.identity`. The
  second asserts that the identity is unchanged under `state=`, a request,
  `restore` and `reset`, and equals the identity at rest. The third
  asserts that `Counter` and `Scaled` differ. The fourth asserts the refusal
  on an untimed root (`Stateless`) and on a running twin of it: a
  `TypeError` naming `identity` and the class, with `sim.program.identity`
  named under the running root.
- [x] 1.2 Run the file on the unchanged tree. Every test fails on
  `AttributeError: 'Sim' object has no attribute 'identity'` (the refusal
  test fails because it expects `TypeError`). Keep the output for
  `evidence.md`.

## 2. Implementation

- [x] 2.1 In `machinome/simulation/sim.py`, add `_clocked_only(what)` beside
  `_not_clocked` and `_running`. It returns the clocked machine, or raises
  `TypeError` in their shape, naming `what` and the model and adding the
  `sim.program.identity` sentence under a running root.
- [x] 2.2 Add the read-only `Sim.identity` property, returning
  `self._clocked_only('identity').identity`, with a docstring that states
  its equality with the exported `clocked.identity` and its independence of
  the bank.
- [x] 2.3 Run the new file green, then `tests/test_clocked_sim.py`,
  `tests/test_clocked_publication.py` and `tests/test_clocked_time.py`.

## 3. Documentation and records

- [x] 3.1 `docs/reference/api.rst`: add `identity` to `Sim`'s `:members:`,
  and one sentence to the "Clocked simulation" section.
- [x] 3.2 `docs/architecture.md`: one clause in the clocked mode's synthesis
  naming `sim.identity` as the identity the document publishes.
- [x] 3.3 Changelog: add the bullet under the existing `Unreleased` section
  of `docs/project/changelog.rst`. `HISTORY.rst` is not touched (the
  orchestrator's correction during implementation; design.md decision 6).
- [x] 3.4 Build the manual strictly
  (`python -m sphinx -b html -n -W --keep-going docs docs/_build/html`),
  if the venv carries Sphinx, and run `tests/test_docs_structure.py` and
  `tests/test_release_records.py`.

## 4. Proof and close

- [x] 4.1 Caller: from `/mnt/data/machinome-projects/Calculators/Curta-Type-I-3x`,
  with the worktree first on `PYTHONPATH`, print `Sim(ClockedCurta()).identity`
  and the `clocked.identity` of `export/clocked_curta/manifest.json`, and
  confirm they are equal. Write nothing into the project.
- [x] 4.2 Run the whole suite once on the final content and quote its
  summary line.
- [x] 4.3 Sync and archive the change with the OpenSpec CLI. Write
  `evidence.md` in the archived change, with the red output, every summary
  line, the caller's output, the findings, and "What was not done, and why".
