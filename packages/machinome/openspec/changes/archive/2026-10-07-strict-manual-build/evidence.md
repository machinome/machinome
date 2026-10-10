# Evidence — `strict-manual-build`

Cycle 15 of the fix-warts-3 campaign (`workflow/ongoing/fix-warts-3.md`).
Bench `machinome/WTs/fix-warts-3`, branch `fix-warts-3`, planning commit
`e29acd47a45b871238e1140089a46487c8c69dff` (`git -C <bench> rev-parse
HEAD`), clean tree before the apply. `<scratch>` is the campaign
scratchpad's `cycle15/` directory; every Sphinx build below wrote its
doctrees (`-d`) and HTML there, never to `docs/_build`. One build or test
run of ours at a time: `ps -eo pid,args | grep '[p]ytest\|[m]achinome
test\|[m]achinome snapshot\|[m]achinome build\|[s]phinx'` showed only its
own shell before each run. No project was read or run.

## 1. Baseline on the unmodified tree (e29acd4)

### 1.1 Environments

- Workspace venv: `env -C <bench> PYTHONPATH=<bench>
  /home/asa/devel/machinome/.venv/bin/python -c 'import machinome;
  print(machinome.__file__)'` prints
  `/home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py`.
- Fresh environment `<scratch>/docsenv` (made at Stage P with `uv venv -p
  3.12` and `uv pip install -r <bench>/docs/requirements.txt`, reused):
  `VIRTUAL_ENV=<scratch>/docsenv uv pip list`:

  ```
  docutils                      0.22.4
  machinome-viewer              0.8.0
  sphinx                        9.1.0
  sphinx-rtd-theme              3.1.0
  ```

  Its builds ran as `env -C <bench> <scratch>/docsenv/bin/python -m sphinx
  ...` with no `PYTHONPATH`, as CI runs them.

### 1.2 The CI command

```
$ env -C <bench> <scratch>/docsenv/bin/python -m sphinx -b html -W -d <scratch>/a-ci-doctrees docs <scratch>/a-ci-html
exit=0   wall 5 s   0 WARNING lines
build succeeded.
```

### 1.3 The strict build

```
$ env -C <bench> <scratch>/docsenv/bin/python -m sphinx -b html -n -W --keep-going -d <scratch>/a-n-doctrees docs <scratch>/a-n-html
<bench>/docs/reference/api.rst:193: WARNING: py:meth reference target not found: AssemblyNode.simulate [ref.meth]
<bench>/docs/reference/api.rst:205: WARNING: py:attr reference target not found: AssemblyNode.time [ref.attr]
<bench>/docs/reference/api.rst:236: WARNING: py:class reference target not found: name keyword [ref.class]
<bench>/machinome/simulation/sim.py:docstring of machinome.simulation.Sim.initial:3: WARNING: py:class reference target not found: The snapshot taken at construction [ref.class]
<bench>/machinome/simulation/sim.py:docstring of machinome.simulation.Sim.state:12: WARNING: py:class reference target not found: The current snapshot by qualified id [ref.class]
build finished with problems, 5 warnings (with warnings treated as errors).
exit=1   wall 4 s
```

The same five as Stage P (design.md, Context).

### 1.4 The docs pins

```
$ env -C <bench> PYTHONPATH=<bench> .venv/bin/pytest -q -p no:cacheprovider tests/test_docs_exports.py tests/test_docs_structure.py tests/test_frame_precision_docs.py tests/test_release_records.py tests/test_mate_contract_docs.py tests/test_viewer_documentation_links.py
48 passed, 836 subtests passed in 1.85s
```

### 1.5 The six architecture entries

`grep -n` in `docs/architecture.md` (section "Known gaps and tensions" at
line 3291):

| text | line |
|---|---|
| `Create React App` | 3298 |
| `installs the viewer from PyPI` | 3301 |
| `docs/scenarios.rst` | 3314 |
| `re-walked from every call` | 3324 |
| `keeps its whole-graph walk` | 3336 |
| `not yet VIEWED` | 3362 |

Each checked against its source before editing: `git -C <bench> log -1
6ff98062` is "perf(motion): memoise completed class port declarations"
(2026-09-22), and `machinome/motion/ports.py` reads and sets
`_machinome_declared_ports` on the class (lines 534 and 559); in
`machinome-viewer/workflow/adrs/`, `EXPORT/ADR-060` ("Only what moves along
a step's path is walked"), `EXPORT/ADR-062` ("The viewer executes a clocked
machine in thread") and `EXPORT/ADR-063` ("The clock is an input and a
frame advances it") are `**Status:** Accepted`, `VIEWER-WEB/ADR-052` ("The
development page is static") is Accepted and `VIEWER-WEB/ADR-013` is
"Superseded by ADR-052"; `.github/workflows/python-app.yml` line 94
installs `machinome-viewer[snapshot] @ git+https://github.com/machinome/machinome-viewer.git`;
`docs/concepts/running.rst` lines 256-260 state the band with the
mechanism's own width and that a single-valued gate "has no width and is
not promised to hold".

## 2. Red tests, unmodified source

`tests/test_docs_exports.py`: `import ast` at module level and the class
`StrictBuildTest` (design.md, Decision 6), placed after
`ActionsDocsJobBuildsNothingTest`. `tests/test_mate_contract_docs.py`:
`test_joints_tells_a_conditional_site_placement`.

```
$ pytest -q -p no:cacheprovider tests/test_docs_exports.py::StrictBuildTest tests/test_mate_contract_docs.py::MateContractDocumentationTest::test_joints_tells_a_conditional_site_placement
FAILED tests/test_docs_exports.py::StrictBuildTest::test_the_configuration_is_nitpicky
FAILED tests/test_mate_contract_docs.py::MateContractDocumentationTest::test_joints_tells_a_conditional_site_placement
2 failed, 1 passed in 0.13s
```

- 2.1 `AssertionError: 'nitpicky' not found in {'project': ..., 'copyright':
  ..., ..., 'html_static_path': ...} : docs/conf.py does not set nitpicky`.
  `test_read_the_docs_fails_on_warnings` passed (the guard).
- 2.2 `AssertionError: 'finally rests' not found in ", a joint is the
  parent's own statement about a child it is placing, ... refuses a site
  joint by name where a class-declared one would not."` (the whole site
  passage up to "Frames and mates").

## 3. The gate

- 3.1 `docs/conf.py`: `nitpicky = True` with its two-line comment, after
  `extensions`. `pytest ... tests/test_docs_exports.py::StrictBuildTest`:
  `2 passed in 0.09s`.
- 3.2 RED, the CI command with `--keep-going`, fresh environment:

  ```
  $ env -C <bench> <scratch>/docsenv/bin/python -m sphinx -b html -W --keep-going -d <scratch>/b-ci-doctrees docs <scratch>/b-ci-html
  <bench>/docs/reference/api.rst:193: WARNING: py:meth reference target not found: AssemblyNode.simulate [ref.meth]
  <bench>/docs/reference/api.rst:205: WARNING: py:attr reference target not found: AssemblyNode.time [ref.attr]
  <bench>/docs/reference/api.rst:236: WARNING: py:class reference target not found: name keyword [ref.class]
  <bench>/machinome/simulation/sim.py:docstring of machinome.simulation.Sim.initial:3: WARNING: py:class reference target not found: The snapshot taken at construction [ref.class]
  <bench>/machinome/simulation/sim.py:docstring of machinome.simulation.Sim.state:12: WARNING: py:class reference target not found: The current snapshot by qualified id [ref.class]
  build finished with problems, 5 warnings (with warnings treated as errors).
  exit=1   wall 4 s
  ```

  And CI's command exactly, without `--keep-going`
  (`-b html -W -d <scratch>/b2-ci-doctrees docs <scratch>/b2-ci-html`):
  `exit=1` with the same five lines and the same summary. Sphinx 9.1
  collects every warning before failing even without `--keep-going`, so
  CI's own log will list all of them.

## 4. The five fixes

- 4.1 `docs/reference/api.rst`: `:meth:\`AssemblyNode.simulate()
  <machinome.node.assembly.AssemblyNode.simulate>\`` (in
  `AbstractBaseNode.render`'s entry) and `:attr:\`AssemblyNode.time
  <machinome.node.assembly.AssemblyNode.time>\`` (in `rotate`'s), each on
  its own line of the paragraph.
- 4.2 `machinome/simulation/sim.py`: `Sim.initial`'s docstring is "The
  snapshot taken at construction, which is the rest pose."; `Sim.state`'s
  first line is "The current snapshot by qualified id, as a fresh dict, so
  a"; nothing else in either.
- 4.3 `machinome/node/openscad/__init__.py`: the `Args:` line is
  `name: the name of this node, by default the name of the class`.
- 4.4 GREEN:

  ```
  $ env -C <bench> <scratch>/docsenv/bin/python -m sphinx -b html -W -d <scratch>/c-ci-doctrees docs <scratch>/c-ci-html
  build succeeded.
  exit=0   wall 4 s   0 WARNING lines

  $ env -C <bench> <scratch>/docsenv/bin/python -m sphinx -b html -n -W --keep-going -E -d <scratch>/c-n-doctrees docs <scratch>/c-n-html
  build succeeded.
  exit=0   wall 5 s   0 WARNING lines
  ```

- 4.5 The rendered `reference/api.html`, before (`<scratch>/a-ci-html`) and
  after (`<scratch>/c-ci-html`), read with `<scratch>/rendered.py` and
  `<scratch>/rendered2.py` (tags stripped, whitespace collapsed):

  | place | before | after |
  |---|---|---|
  | `render()`'s last sentence | "What moves belongs to AssemblyNode.simulate()." as a bare `<code>`, no link | the same words, `<a class="reference internal" href="#machinome.node.assembly.AssemblyNode.simulate">` around the code |
  | `rotate()`'s last sentence | "... an expression involving AssemblyNode.time or any declared driver." bare `<code>` | the same words, linked to `#machinome.node.assembly.AssemblyNode.time` |
  | `Sim.initial` | "property initial the rest pose. Type : The snapshot taken at construction" | "property initial The snapshot taken at construction, which is the rest pose." (no "Type") |
  | `Sim.state` | "property state a fresh dict, so a caller holding one holds a value ... Type : The current snapshot by qualified id" | "property state The current snapshot by qualified id, as a fresh dict, so a caller holding one holds a value and not a view of the running simulation. Under a RUNNING root ..." (no "Type") |
  | `OpenScadNode.__init__` | "argument (name keyword) – the name of this node, defaul to name of the class" | "name – the name of this node, by default the name of the class" |

## 5. The joints page

- 5.1 `docs/concepts/joints.rst`, after "unless ``at`` names the child's
  placement." in the paragraph beginning "This is for the bought bearing":
  the sentence of design.md, Decision 4, verbatim. `pytest ...
  test_joints_tells_a_conditional_site_placement`: `1 passed in 0.08s`.
- 5.2 Rebuilt with the CI command into `<scratch>/d-ci-*`: `build
  succeeded.`, exit 0, wall 4 s, 0 WARNING lines. The paragraph in
  `concepts/joints.html` reads: "This is for the bought bearing, the
  fastener, the shared catalogue class that carries no joint of its own:
  where the parent's origin already is the line, no anchor is needed at
  all. The sentence a reader gets wrong: a child the parent translates
  swings about the parent's origin, not its own, unless at names the
  child's placement. A site joint's values are read where the child
  finally rests, after every rest operation the parent applies to it, so
  when one of those operations is conditional a plain value is right for
  one branch only: write the argument as a callable of the realized parent
  (Arguments, below). One declaration serves every copy of a repeat(), ..."
  The section "Arguments" (same page) says each argument may be "a
  callable of the realized declarer".

## 6. The architecture synthesis

`docs/architecture.md`, "Known gaps and tensions": deleted "Create React App
is deprecated", "`declared_ports` is re-walked from every call, not
memoised by class", "The viewer's TypeScript run keeps its whole-graph
walk" and "A clocked model is published but not yet VIEWED"; replaced "The
manual's build installs the viewer from PyPI" with "The CI
browser-snapshot job installs the viewer from Git
(`.github/workflows/python-app.yml`), with Node to build its widget, where
the manual's build installs the published package
(`docs/requirements.txt`)."; in "A self-read gate with no WIDTH is
silently wrong", `docs/scenarios.rst` became `docs/concepts/running.rst`.
Nothing else in the file changed (`git diff --stat`: 5 insertions, 34
deletions). 1.5's greps again:

```
3298:- **The CI browser-snapshot job installs the viewer from Git**
3309:  `docs/concepts/running.rst` and tested for what the framework promises, not
```

None of the deleted titles and neither old text is found.

## 7. Records

- 7.1 Items 5 and 6 of "Three findings from filming the clocked Curta"
  moved verbatim to `workflow/archive/fix-warts-3-2026-10-06/resolved.md`
  under `## \`strict-manual-build\``, with the "What shipped" paragraph;
  the section's opening paragraph in `workflow/warts.md` now says findings
  5 and 6 are fixed by `strict-manual-build`; items 8, 9 and 10 unchanged.
- 7.2 The Inmoov-sim entry, its `**Remaining (2026-10-04):**` note
  included, moved verbatim under the same heading; the section "Inmoov-sim
  (2026-09-10, stage B on ADR-098)" held nothing else and was deleted from
  `warts.md`. The "What shipped" paragraph names the studio craft skill's
  sentence as the studio repository's, in the campaign note's cycle 19.
  Checked by script against `git show HEAD:workflow/warts.md`: both moved
  texts (HEAD lines 504-524 and 1663-1668) occur byte for byte in
  `resolved.md`.
- 7.3 `git -C <bench> diff docs/project/changelog.rst`: empty.
- The campaign note `workflow/ongoing/fix-warts-3.md` gained the cycle 15
  Progress line after cycle 14's.

## 8. Sync, archive and checks

- 8.4 `openspec validate strict-manual-build`: "Change
  'strict-manual-build' is valid". Then `openspec archive
  strict-manual-build --yes` (openspec 1.6.0), the CLI's own sync: "Specs
  to update: user-documentation: update", "~ 2 modified", "Totals: + 0, ~ 2,
  - 0, → 0", "Change 'strict-manual-build' archived as
  '2026-10-07-strict-manual-build'". Its warnings: the Why section's
  length, and 20 of 24 tasks complete (8.1 to 8.4, done after it and
  ticked in the archived copy). Checked by script
  (`<scratch>/check_sync.py`, against `git show
  HEAD:openspec/specs/user-documentation/spec.md`): each of the two
  requirements occurs once in `openspec/specs/user-documentation/spec.md`,
  its text equal to the delta's (blank lines aside); "The public motion
  surface is documented" has 5 scenarios (its 4 carried, "A site joint
  under a conditional rest placement" added) and "The documentation build
  produces nothing" 5 (its 4 carried, "A reference names nothing the
  manual documents" added), no title repeated; 21 requirements before and
  after, the other 19 unchanged. `openspec validate --specs`: `Totals: 45
  passed, 0 failed (45 items)`; `openspec validate user-documentation`:
  "Specification 'user-documentation' is valid".
- 8.1 Lint on `machinome/simulation/sim.py`,
  `machinome/node/openscad/__init__.py`, `tests/test_docs_exports.py` and
  `tests/test_mate_contract_docs.py`, on the working tree and as at HEAD
  (HEAD's files and `setup.cfg` exported to `<scratch>/head/` with `git
  archive`):
  - `flake8 --max-line-length=89` (pyenv shim, 7.3.0): 2 findings at HEAD,
    the same 2 after (compared with line and column stripped: no
    difference), both pre-existing and in lines this change does not
    touch: `machinome/node/openscad/__init__.py:88:90: E501 line too long
    (92 > 89 characters)` and `tests/test_mate_contract_docs.py:31:9: E306
    expected 1 blank line before a nested definition, found 0`.
    `docs/conf.py`: 0 findings at HEAD and after.
  - `black --check` (26.5.1): `sim.py`, `openscad/__init__.py` and
    `test_docs_exports.py` "would reformat" at HEAD and after; neither
    follows black. Changed lines in black's diff: `sim.py` 238 at HEAD and
    after, `openscad/__init__.py` 23 and 23, `test_docs_exports.py` 189 and
    212, `test_mate_contract_docs.py` 52 and 65. The new tests are written
    in their files' own style (single quotes), which is the whole of the
    growth. Nothing was reformatted.
- 8.2 The focused tests on the final tree:

  ```
  $ pytest -q -p no:cacheprovider tests/test_docs_exports.py tests/test_docs_structure.py tests/test_frame_precision_docs.py tests/test_release_records.py tests/test_mate_contract_docs.py tests/test_viewer_documentation_links.py
  51 passed, 836 subtests passed in 1.72s

  $ pytest -q -p no:cacheprovider <the same six> tests/test_tutorial_counter.py tests/test_sphinx_ext.py
  67 passed, 836 subtests passed in 57.98s      (wall 58 s)
  ```

  (1.4 was 48; this change adds three tests.)
- 8.3 The full suite, alone (`ps` showed no run of ours), `pytest -q -p
  no:cacheprovider` at the bench root, log `<scratch>/full-suite.log`:

  ```
  4742 passed, 4 skipped, 55 warnings, 6677 subtests passed in 635.85s (0:10:35)   (exit 0, wall 638.33 s)
  ```

  (`report-the-instant` closed at 4739 passed and 6677 subtests; this
  change adds three tests.)

Everything is left uncommitted.
