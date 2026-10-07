## Context

### The bench

Bench `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch
`fix-warts-3`, `git rev-parse HEAD` =
`e3ebab088ea18ab07c9f024575513c7746b19828`, clean tree.
`python -c 'import machinome; print(machinome.__file__)'` under
`PYTHONPATH=<bench>` prints `<bench>/machinome/__init__.py`.

`<scratch>` is the campaign scratchpad's `cycle15/` directory,
`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle15`.
Every build below writes its doctrees (`-d`) and its HTML there, never to
`docs/_build`.

Two environments:

- the workspace venv, `/home/asa/devel/machinome/.venv` (Sphinx 9.1.0,
  sphinx_rtd_theme 3.1.0, docutils 0.22.4, machinome-viewer 0.7.0 editable),
  run as `env -C <bench> PYTHONPATH=<bench> .venv/bin/python -m sphinx ...`;
- a fresh environment holding `docs/requirements.txt` alone, as CI and Read
  the Docs install it: `uv venv -p 3.12 <scratch>/docsenv` then
  `VIRTUAL_ENV=<scratch>/docsenv uv pip install -r <bench>/docs/requirements.txt`
  (Sphinx 9.1.0, sphinx-rtd-theme 3.1.0, docutils 0.22.4, machinome-viewer
  0.8.0 from PyPI), run as `env -C <bench> <scratch>/docsenv/bin/python -m
  sphinx ...` with no `PYTHONPATH`, as CI runs it (`docs/conf.py` puts the
  source tree on `sys.path`).

### How CI is green

`.github/workflows/python-app.yml`, job `docs`, installs
`docs/requirements.txt` and runs `python -m sphinx -b html -W docs
docs/_build` (line 126). `.readthedocs.yaml` installs the same file and sets
`sphinx.fail_on_warning: true`. Neither passes `-n`, and `docs/conf.py`
does not set `nitpicky`, so Sphinx does not report an unresolved
cross-reference to either of them. There is no allowed warning and no
second requirements set: the build is simply not nitpicky.

The CI command, in both environments, at `e3ebab0`:

```text
$ env -C <bench> <scratch>/docsenv/bin/python -m sphinx -b html -W -d <scratch>/fresh-ci-doctrees docs <scratch>/fresh-ci-html
exit=0
build succeeded.
```

(the workspace venv: the same, `exit=0`, 0 warnings, `<scratch>/sphinx-ci.log`).

### The five warnings, verbatim

The strict build of the manual's procedure, `-n -W --keep-going`, fresh
environment (`<scratch>/fresh-n.log`; the workspace venv with `-E` prints
the same five lines, `<scratch>/sphinx-before-n.log`):

```text
$ env -C <bench> <scratch>/docsenv/bin/python -m sphinx -b html -n -W --keep-going -d <scratch>/fresh-n-doctrees docs <scratch>/fresh-n-html
<bench>/docs/reference/api.rst:193: WARNING: py:meth reference target not found: AssemblyNode.simulate [ref.meth]
<bench>/docs/reference/api.rst:205: WARNING: py:attr reference target not found: AssemblyNode.time [ref.attr]
<bench>/docs/reference/api.rst:236: WARNING: py:class reference target not found: name keyword [ref.class]
<bench>/machinome/simulation/sim.py:docstring of machinome.simulation.Sim.initial:3: WARNING: py:class reference target not found: The snapshot taken at construction [ref.class]
<bench>/machinome/simulation/sim.py:docstring of machinome.simulation.Sim.state:12: WARNING: py:class reference target not found: The current snapshot by qualified id [ref.class]
build finished with problems, 5 warnings (with warnings treated as errors).
exit=1
```

The finding's line numbers (23, 35, 76) predate the page's growth; these
are the same five. Their sources:

1. `api.rst:193` is `:meth:\`AssemblyNode.simulate\`` at line 201, inside
   `.. autoclass:: machinome.node.base.AbstractBaseNode`'s `render()`
   entry. The current module there is `machinome.node.base`; the method is
   documented as `machinome.node.assembly.AssemblyNode.simulate`
   (`.. autoclass:: machinome.node.assembly.AssemblyNode`, line 544,
   `:members: simulate, set_state, set_keyframe, clear_keyframe, time`).
2. `api.rst:205` is `:attr:\`AssemblyNode.time\`` at line 213, the same
   class's `rotate()` entry, for the same reason.
3. `api.rst:236` is not in `api.rst`'s own text. It is
   `OpenScadNode.__init__`'s docstring (`machinome/node/openscad/__init__.py`
   line 61, documented by `.. autoclass:: machinome.node.openscad.OpenScadNode`,
   `:members: __init__`, api.rst line 436): its `Args:` line `name keyword
   argument: the name of this node, defaul to name of the class` is read by
   napoleon as a parameter `argument` of type `name keyword`. The rendered
   HTML today reads "**argument** (*name keyword*) – the name of this node,
   defaul to name of the class". Sphinx attributes the warning to an
   unrelated `api.rst` line.
4. `Sim.initial` (`machinome/simulation/sim.py` line 389), a property whose
   docstring is `"""The snapshot taken at construction: the rest pose."""`.
   Napoleon reads a property's first line `X: Y` as type `X` and
   description `Y`; the page renders "the rest pose. Type: The snapshot
   taken at construction".
5. `Sim.state` (line 415), the same: "The current snapshot by qualified id:
   a fresh dict, ..." renders "Type: The current snapshot by qualified id".

The `sim-identity` change met the same mechanism: its first draft of
`Sim.identity`'s docstring added a sixth warning, and was reworded
(`openspec/changes/archive/2026-10-01-sim-identity/evidence.md`).

### The stale gaps

`docs/architecture.md`, "Known gaps and tensions" (line 3291), at
`e3ebab0`, checked entry by entry against the sources:

- "**A clocked model is published but not yet VIEWED** (ADR-128)" (line
  3362): "no released viewer reports version 8, so a build and an export
  warn, a web snapshot is refused before the browser starts, and such a
  model still does not reach a browser." Stale: machinome-viewer's ADR-062
  ("The viewer executes a clocked machine in thread", accepted 2026-09-17,
  `machinome-viewer/workflow/adrs/EXPORT/`) and ADR-063 ("The clock is an
  input and a frame advances it", accepted) execute it, and the released
  viewer declares document versions 1 to 13 (`docs/conf.py`'s
  `document_versions`, the viewer 0.7.0 and 0.8.0 on PyPI). The framework
  warns only when the INSTALLED viewer does not render a version
  (`machinome/viewers/bundle.py`, `unreadable_document`), which no released
  viewer since 0.7.0 does for version 8.
- "**Create React App is deprecated** (ADR-013, now in machinome-viewer)"
  (line 3297). Stale: viewer ADR-052 ("The development page is static",
  accepted) supersedes ADR-013 and deletes React and Create React App; the
  widget builds with esbuild (`machinome_viewer/widget/package.json`).
- "**The manual's build installs the viewer from PyPI** ... so it builds only
  once machinome-viewer is uploaded; the CI browser-snapshot job still
  installs the viewer from Git until then." (line 3300). The condition is
  met: the viewer has been on PyPI since 0.7.0 (26 September 2026), and the
  fresh environment above installed 0.8.0 from it. What remains true is
  that the CI browser-snapshot job installs
  `machinome-viewer[snapshot] @ git+https://github.com/machinome/machinome-viewer.git`
  (`python-app.yml` line 94) and sets up Node to build its widget.
- "**A self-read gate with no WIDTH is silently wrong** (ADR-121): ... It is
  documented in `docs/scenarios.rst`" (line 3310). The gap stands; the page
  does not exist. The knife-edge gate is documented in
  `docs/concepts/running.rst` (lines 255-261: "State the disengaged region
  as a band with the mechanism's own width ... A gate whose disengaged
  state is a single value has no width and is not promised to hold.").
- "**`declared_ports` is re-walked from every call, not memoised by
  class**" (line 3324). Stale: commit `6ff98062` (22 September 2026, "perf(motion):
  memoise completed class port declarations") caches each completed
  class's enumeration on the class itself
  (`machinome/motion/ports.py`, `declared_ports`,
  `_machinome_declared_ports`), and answers the entry's own question in its
  comment: kept on the class rather than in a process-global cache, so a
  site's class stays collectable, and published only once `NodeMeta` has
  completed the class.
- "**The viewer's TypeScript run keeps its whole-graph walk**" (line 3335).
  Stale: viewer ADR-060 ("Only what moves along a step's path is walked",
  accepted, `machinome-viewer/workflow/adrs/EXPORT/`) adopts ADR-124's
  mechanism in the viewer and quotes this entry as its origin.

Kept, because nothing at the bench commit shows them closed: OpenSCAD
outside the parity fixture; sequential STL rendering (`build_stls` in
`machinome/node/base.py` still renders one STL at a time); a driven GROUP
with a self-read; curved source paths; a block's construction check; block
stop location; a `sign`-gated source; a push needing two inputs; the two
`%`s; one driver per clocked instruction; the running landing walk; the
unclipped clock; the class body without `time`; the clocked bound read
once; a clocked ranged joint reached from the bank; the process-wide
clocked mark; two clocked writers.

### The joints page

`docs/concepts/joints.rst`, section "Joints", the site-declaration passage:
"Passed as a **keyword where a parent declares a child**, a joint is the
parent's own statement about a child it is placing, read in the parent's
frame, with ``at`` defaulting to the parent's origin:" (line 85), a code
block, then the paragraph beginning "This is for the bought bearing"
(line 99), whose second sentence is "The sentence a reader gets wrong:
**a child the parent translates swings about the parent's origin, not its
own**, unless ``at`` names the child's placement." Nothing on the page
mentions a conditional rest placement. The section "Arguments" (line 550)
already says each of `axis`, `at`, `range` and `carries` may be "a callable
of the realized declarer ... one passed where the child is declared is
handed that parent instead."

### Existing pins

`tests/test_docs_exports.py tests/test_docs_structure.py
tests/test_frame_precision_docs.py tests/test_release_records.py
tests/test_mate_contract_docs.py tests/test_viewer_documentation_links.py`
at `e3ebab0`: `48 passed, 836 subtests passed in 1.80s`. No test reads
`docs/architecture.md`.

## Goals / Non-Goals

**Goals:** the build CI and Read the Docs run refuses an unresolved
cross-reference; the five warnings are fixed where they are written; the
known-gaps list states only gaps that exist; the joints page tells a reader
how to write a site joint under a conditional placement.

**Non-goals:** the CI snapshot job's install route; any gap not provably
closed; the studio's craft skill; any change to what the framework does.

## Decisions

### 1. `nitpicky = True` in `docs/conf.py`, and the build commands unchanged

`nitpicky = True` is what `-n` sets. In `conf.py` it reaches every build of
the manual: the CI docs job, Read the Docs (which has no nitpicky switch of
its own; `fail_on_warning` only turns warnings into errors), and a
contributor's plain `sphinx -W`.

Alternatives:

- **`-n` added to the CI command.** CI would refuse, Read the Docs would
  not, and the two configurations that `tests/test_docs_exports.py` holds
  in step would differ in what they check. Rejected.
- **Fix the five and add nothing.** The build stays non-nitpicky; the next
  broken reference goes unseen exactly as these five did (the
  `sim-identity` draft added a sixth and was caught only because its author
  ran `-n` by hand). Rejected: the finding is that the build is not a
  gate.
- **`nitpick_ignore` for the five.** Hides five real rendering defects
  (three docstrings render wrong). Rejected.

The setting sits after `extensions`, with a two-line comment:

```python
# Every cross-reference must resolve, so a warnings-as-errors build (CI,
# Read the Docs) refuses a link to nothing.
nitpicky = True
```

### 2. The five fixes, at their source, rendered text kept

`docs/reference/api.rst`, explicit titles so the page reads as it did:

```rst
      moves belongs to
      :meth:`AssemblyNode.simulate() <machinome.node.assembly.AssemblyNode.simulate>`.
```

```rst
      :attr:`AssemblyNode.time <machinome.node.assembly.AssemblyNode.time>`
      or any declared driver.
```

(`~machinome.node.assembly.AssemblyNode.simulate` would render "simulate()"
alone, losing the class name the sentence needs; an explicit title adds no
parentheses, so the method's title carries them, as Sphinx rendered it
before.)

`machinome/simulation/sim.py`:

```python
        """The snapshot taken at construction, which is the rest pose."""
```

```python
        """The current snapshot by qualified id, as a fresh dict, so a
        caller holding one holds a value and not a view of the running
        simulation.
```

(the rest of `Sim.state`'s docstring unchanged).

`machinome/node/openscad/__init__.py`, the one `Args:` line:

```python
           name: the name of this node, by default the name of the class
```

A trial of exactly these edits plus Decision 1 on a copy of the bench's
`docs/` and `machinome/` in `<scratch>/trial/` (diff:
`<scratch>/trial.diff`; the `simulate` title there lacked the
parentheses this design adds) built with the CI command in the fresh
environment: `exit=0`, `build succeeded.`, no warning
(`<scratch>/trial2.log`). The rendered `api.html` then reads "What moves
belongs to AssemblyNode.simulate" linked to the method, "an expression
involving AssemblyNode.time" linked to the property, "property initial —
The snapshot taken at construction, which is the rest pose." with no Type
field, and "**name** – the name of this node, by default the name of the
class".

### 3. The known gaps: delete what is closed, rewrite what is half true

In `docs/architecture.md`, "Known gaps and tensions":

- delete "A clocked model is published but not yet VIEWED";
- delete "Create React App is deprecated";
- delete "`declared_ports` is re-walked from every call, not memoised by
  class";
- delete "The viewer's TypeScript run keeps its whole-graph walk";
- replace "The manual's build installs the viewer from PyPI" with the one
  fact still true:

  ```markdown
  - **The CI browser-snapshot job installs the viewer from Git**
    (`.github/workflows/python-app.yml`), with Node to build its widget,
    where the manual's build installs the published package
    (`docs/requirements.txt`).
  ```

- in "A self-read gate with no WIDTH is silently wrong", replace
  `` `docs/scenarios.rst` `` with `` `docs/concepts/running.rst` ``.

A closed gap is deleted rather than rewritten as "now done": the list is of
gaps, and the history is in the ADRs and Git. Nothing is added to the list.

### 4. One sentence on the joints page, in the existing paragraph

After "unless ``at`` names the child's placement." in the paragraph
beginning "This is for the bought bearing" (`docs/concepts/joints.rst`,
line 103):

```rst
A site joint's values are read where the child finally rests, after every
rest operation the parent applies to it, so when one of those operations
is conditional a plain value is right for one branch only: write the
argument as a callable of the realized parent (Arguments, below).
```

It names no project (the Inmoov-sim forearm is the provenance, kept in
`workflow/`), adds no section and no example, and the mechanism it relies
on is already documented under "Arguments".

### 5. No changelog bullet; no ADR

The manual's own rule (`skills/write-the-manual/SKILL.md`, "Work after a
release") asks for a bullet when a change "adds, changes or removes what a
reader can use". Nothing here does: the framework's behaviour is
untouched, the gate is the manual's build, and the three docstrings say
what they said, now rendered as written. The `Unreleased` section's bullets
are all behaviour a project meets. No architectural decision is made.

### 6. Red first

- `tests/test_docs_exports.py`, a new class beside
  `ActionsDocsJobBuildsNothingTest`:

  ```python
  class StrictBuildTest(unittest.TestCase):
      """Both warnings-as-errors builds refuse a cross-reference to
      nothing."""

      def test_the_configuration_is_nitpicky(self):
          tree = ast.parse((DOCS / 'conf.py').read_text())
          values = {target.id: node.value
                    for node in tree.body if isinstance(node, ast.Assign)
                    for target in node.targets
                    if isinstance(target, ast.Name)}
          self.assertIn('nitpicky', values,
                        'docs/conf.py does not set nitpicky')
          self.assertIs(ast.literal_eval(values['nitpicky']), True)

      def test_read_the_docs_fails_on_warnings(self):
          self.assertIs(readthedocs()['sphinx']['fail_on_warning'], True)
  ```

  RED: the first, `docs/conf.py does not set nitpicky`. The second is a
  guard, green both ways. The module imports `ast` only inside one test
  today (line 266); add `import ast` to the module's imports.

- `tests/test_mate_contract_docs.py`, beside
  `test_joints_teaches_mate_read_scope_and_constraint_target`:

  ```python
  def test_joints_tells_a_conditional_site_placement(self):
      joints = (ROOT / 'docs/concepts/joints.rst').read_text()
      site = joints.partition(
          'Passed as a **keyword where a parent declares a child**')[2]
      site = ' '.join(site.partition('\nFrames and mates\n')[0].split())
      self.assertIn('finally rests', site)
      self.assertIn('conditional', site)
      self.assertIn('callable of the realized parent', site)
  ```

  RED: `'finally rests' not found`.

- The gate itself: with Decision 1 applied and nothing else, the CI command
  in the fresh environment fails with the five warnings above (RED); with
  Decision 2 applied, it succeeds (GREEN). This pair is the proof the
  finding asks for.

## Risks / Trade-offs

- **A future Sphinx or theme may report a reference these versions
  resolve.** The CI and Read the Docs requirements are unpinned, so a new
  release can turn the build red with no change here; that was already
  true of every other warning under `-W`, and the remedy is the same: fix
  the reference.
- **Read the Docs builds older tags with their own `conf.py`.** Unaffected.

## Migration Plan

None. Contributors building the manual locally get the check without a flag.

## Open Questions

1. **The Inmoov-sim entry.** Its framework half (the joints sentence)
   ships; its other half (a sentence in the studio's craft skill,
   `machinome-studio/shop-skills/machinome/SKILL.md`) is another
   repository's. The plan keeps the entry in `workflow/warts.md` with its
   `**Remaining (2026-10-04)**` note replaced by one saying only the
   studio's sentence remains. Whether to move it to `resolved.md` instead,
   as framework-complete, is the orchestrator's call. Answered at review
   (7 October 2026): move it to `resolved.md` as framework-complete, the
   "What shipped" paragraph naming the studio sentence as the campaign
   note's outside-the-framework step (recorded there); the tasks' step
   for the entry changes accordingly.
2. **No delta for `docs/architecture.md`.** No baseline requirement governs
   the synthesis's content: `framework-contributor-guidance` covers the
   contributor briefing, and `user-documentation` covers what the build
   reads, which excludes `.md`. The correction is recorded in this design,
   the tasks and the evidence, not in a spec. Adding a requirement for the
   synthesis would be new governance nobody asked for.
3. **The workspace skill names a file the framework does not have.**
   `skills/write-the-manual/SKILL.md` lists `workflow/documentation.md`
   (build and hosting) among the framework's records; there is no such file
   at the bench commit. A workspace correction, not this change's;
   recorded in the campaign note's outside-the-framework step at review.
