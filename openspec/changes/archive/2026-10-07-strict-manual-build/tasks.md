Bench: `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch
`fix-warts-3`. Framework commands run as
`env -C <bench> PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/<tool> ...`.
`<scratch>` is the campaign scratchpad's `cycle15/` directory. Every
Sphinx build writes its doctrees and HTML under `<scratch>` (`-d
<scratch>/<name>-doctrees` and `<scratch>/<name>-html`), never to
`docs/_build`. The fresh environment is `<scratch>/docsenv` (design.md,
Context, "The bench": `uv venv -p 3.12`, then `uv pip install -r
<bench>/docs/requirements.txt`; recreate it the same way if it is gone) and
its builds run as `env -C <bench> <scratch>/docsenv/bin/python -m sphinx
...` with no `PYTHONPATH`, as CI runs them. One build or test run of ours at
a time (`ps -eo pid,args | grep '[p]ytest\|[m]achinome test\|[m]achinome
snapshot\|[m]achinome build\|[s]phinx'` first). No project is read or run.
Record every command and its result in `evidence.md` as you go, in the
shape of `openspec/changes/archive/2026-10-04-scad-presentation/evidence.md`:
the scratchpad is not durable, so copy each warning list verbatim.

## 1. Baseline on the unmodified tree

- [x] 1.1 Create `evidence.md` with the bench commit (`git -C <bench>
  rev-parse HEAD`) and the interpreter check (`python -c 'import machinome;
  print(machinome.__file__)'` prints a path under the bench), and the
  fresh environment's `uv pip list` lines for sphinx, sphinx-rtd-theme,
  docutils and machinome-viewer.
- [x] 1.2 The CI command in the fresh environment, `python -m sphinx -b
  html -W -d <scratch>/a-ci-doctrees docs <scratch>/a-ci-html`: record the
  exit status and the last line (Stage P: `exit=0`, `build succeeded.`).
- [x] 1.3 The strict build, `python -m sphinx -b html -n -W --keep-going
  -d <scratch>/a-n-doctrees docs <scratch>/a-n-html`, fresh environment:
  record every `WARNING` line and the summary verbatim (Stage P: the five
  of design.md, Context, "The five warnings", and `build finished with
  problems, 5 warnings (with warnings treated as errors).`).
- [x] 1.4 The docs pins: `pytest -q -p no:cacheprovider
  tests/test_docs_exports.py tests/test_docs_structure.py
  tests/test_frame_precision_docs.py tests/test_release_records.py
  tests/test_mate_contract_docs.py tests/test_viewer_documentation_links.py`
  (Stage P: `48 passed, 836 subtests passed in 1.80s`).
- [x] 1.5 `grep -n` in `docs/architecture.md` for the six entries of
  design.md, Decision 3 (`not yet VIEWED`, `Create React App`,
  `installs the viewer from PyPI`, `docs/scenarios.rst`,
  `re-walked from every call`, `keeps its whole-graph walk`); record the
  line numbers.

## 2. Red tests

- [x] 2.1 RED `tests/test_docs_exports.py`: `import ast` at module level,
  and the class `StrictBuildTest` of design.md, Decision 6;
  `test_the_configuration_is_nitpicky` fails with `docs/conf.py does not
  set nitpicky`. `test_read_the_docs_fails_on_warnings` passes (a guard).
- [x] 2.2 RED `tests/test_mate_contract_docs.py`:
  `test_joints_tells_a_conditional_site_placement` of design.md, Decision
  6, fails on `'finally rests'`.

## 3. The gate

- [x] 3.1 `docs/conf.py`: `nitpicky = True` with its comment, after
  `extensions` (design.md, Decision 1). Run 2.1: green.
- [x] 3.2 RED The CI command, unchanged, in the fresh environment, `python
  -m sphinx -b html -W --keep-going -d <scratch>/b-ci-doctrees docs
  <scratch>/b-ci-html`: it now fails with the same five warnings. Record
  them verbatim. (`--keep-going` only so all five are listed; CI's own
  command stops at the first, which is enough to fail it.)

## 4. The five fixes

- [x] 4.1 `docs/reference/api.rst`: the two references of design.md,
  Decision 2, with explicit titles (`AssemblyNode.simulate()` and
  `AssemblyNode.time`).
- [x] 4.2 `machinome/simulation/sim.py`: the first lines of `Sim.initial`
  and `Sim.state`'s docstrings (design.md, Decision 2); nothing else in
  either docstring.
- [x] 4.3 `machinome/node/openscad/__init__.py`: the `name:` line of
  `OpenScadNode.__init__`'s `Args:` (design.md, Decision 2).
- [x] 4.4 GREEN The CI command exactly as CI runs it, fresh environment,
  `python -m sphinx -b html -W -d <scratch>/c-ci-doctrees docs
  <scratch>/c-ci-html`: `build succeeded.`, exit 0, no `WARNING` line.
  Then the same with `-n --keep-going -E` added: the same. Record both.
- [x] 4.5 Open `<scratch>/c-ci-html/reference/api.html` and record the
  rendered text of the four places (`AbstractBaseNode.render`'s last
  sentence, `rotate`'s last sentence, `Sim.initial`, `Sim.state`'s first
  sentence, `OpenScadNode.__init__`'s `name` parameter): each reads as
  design.md, Decision 2 says, the two references are links, and no
  "Type:" field remains on `initial` or `state`.

## 5. The joints page

- [x] 5.1 `docs/concepts/joints.rst`: the one sentence of design.md,
  Decision 4, after "unless ``at`` names the child's placement." in the
  paragraph beginning "This is for the bought bearing". Run 2.2: green.
- [x] 5.2 Rebuild (4.4's first command, into fresh `<scratch>/d-ci-*`) and
  read the paragraph once in `concepts/joints.html` as a reader.

## 6. The architecture synthesis

- [x] 6.1 `docs/architecture.md`, "Known gaps and tensions": the four
  deletions, the one rewrite and the one path correction of design.md,
  Decision 3, nothing else. Re-run 1.5's greps: only `docs/concepts/running.rst`
  and `The CI browser-snapshot job installs the viewer from Git` are
  found among the new texts, and none of the deleted titles.

## 7. Records

- [x] 7.1 `workflow/warts.md`, the Curta section: move items 5 and 6
  verbatim to `workflow/archive/fix-warts-3-2026-10-06/resolved.md` under
  `## \`strict-manual-build\``, introduced as `clocked-snapshot-identity`'s
  item 4 is ("From "Three findings ...", items 5 and 6:"), with a "What
  shipped" paragraph (the gate, the five fixes with the red and green
  builds, the six architecture entries and the evidence for each). In
  `warts.md`, rewrite the section's opening paragraph to say findings 5 and
  6 are fixed by `strict-manual-build`, and delete the two items; 8, 9 and
  10 stay as they are.
- [x] 7.2 `workflow/warts.md`, the Inmoov-sim entry (section "Inmoov-sim
  (2026-09-10, stage B on ADR-098)"): move it verbatim, its
  `**Remaining (2026-10-04):**` note included, to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md` under the same
  `## \`strict-manual-build\`` heading, with a "What shipped" paragraph
  saying the joints page's sentence shipped here and the sentence in the
  shop craft skill (`machinome-studio/shop-skills/machinome/SKILL.md`) is
  the studio repository's, recorded in the campaign note's
  outside-the-framework step (design.md, Open Questions, 1, as answered);
  delete the entry and, if nothing else remains in it, the section from
  `warts.md`.
- [x] 7.3 No changelog bullet (design.md, Decision 5); check `git diff
  docs/project/changelog.rst` is empty.

## 8. Close

- [x] 8.1 `black --check` and `flake8 --max-line-length=89` on
  `machinome/simulation/sim.py machinome/node/openscad/__init__.py
  tests/test_docs_exports.py tests/test_mate_contract_docs.py`.
- [x] 8.2 1.4's docs pins once more, plus `tests/test_tutorial_counter.py`
  and `tests/test_sphinx_ext.py`; record counts.
- [x] 8.3 The full suite once, alone (`pytest` at the bench root); record
  the summary line and wall time.
- [x] 8.4 Sync the delta into `openspec/specs/user-documentation/spec.md`
  (the two MODIFIED requirements replaced whole), archive the change to
  `openspec/changes/archive/<date>-strict-manual-build/`, and run
  `openspec validate --specs` (or `openspec validate user-documentation`)
  green. Leave everything uncommitted.
