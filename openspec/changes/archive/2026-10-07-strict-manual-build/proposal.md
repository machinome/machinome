## Why

Three entries of `workflow/warts.md` are about pages a reader is sent to or
a record a contributor is sent to, each with its fix stated.

From "Three findings from filming the clocked Curta (1 October 2026, found
by Videomaker's curta-video campaign)":

> 5. **The strict manual build is not a gate.** `sphinx -W` fails on `main` with
>    five warnings in untouched lines (`docs/reference/api.rst` 23, 35, 76 and
>    the `Sim.initial` and `Sim.state` docstrings). Found by `sim-identity`.
> 6. **A stale known gap in `docs/architecture.md`:** "A clocked model is
>    published but not yet VIEWED" predates viewer 0.7.0, which reads document
>    versions 1 to 13. Found by `sim-identity`.

From "Inmoov-sim (2026-09-10, stage B on ADR-098)":

> **A site joint's value is the line in the parent's frame where the
> child FINALLY rests, after every rest operation the parent applies to
> it — and when one of those is conditional, a plain value is silently
> wrong for the other branch.** [...] nothing in the docs says a plain
> site value should be treated as suspect whenever the parent's own rest
> placement of that child is conditional. Triage: one sentence in
> `docs/driving.rst`'s site paragraph and in the shop craft skill; no
> framework change.
>
> **Remaining (2026-10-04):** not done. `docs/driving.rst` no longer exists;
> the site paragraph is now in `docs/concepts/joints.rst`, which says
> nothing about a conditional placement.

Reproduced on the bench `fix-warts-3` at `e3ebab0` (design.md, Context):

- The CI docs job's own command, `python -m sphinx -b html -W docs <out>`,
  **succeeds**, in the workspace venv and in a fresh environment holding
  `docs/requirements.txt` alone. CI is green because it builds without
  `-n`: Sphinx reports an unresolved cross-reference only when nitpicky.
  The strict build the manual's own procedure names, `-n -W --keep-going`
  (the one `sim-identity` ran), fails with exactly five warnings. The
  finding's "`sphinx -W` fails" is therefore "`sphinx -n -W` fails, and CI
  does not run it": the gate a contributor runs and the gate CI and Read the
  Docs run disagree, and five broken references sit in the manual unseen.
- The five are two cross-references in `docs/reference/api.rst` that name
  `AssemblyNode` without its module (now lines 193 and 205; the page grew
  since the finding), and three docstrings that napoleon misreads: the
  `Sim.initial` and `Sim.state` properties, whose first lines read as
  `Type: description` and so render a bogus "Type:" field, and the
  `OpenScadNode.__init__` docstring, whose `name keyword argument:` line
  renders as a parameter called `argument` of type `name keyword` (Sphinx
  attributes this one to `api.rst:236`; the finding's "api.rst 76").
- `docs/architecture.md`'s "Known gaps and tensions" still says a clocked
  model does not reach a browser; viewer ADR-062 and ADR-063 (accepted
  17 September 2026) execute a clocked machine, and the released viewer
  reads document versions 1 to 13. Five neighbouring entries of the same
  list are provably stale in the same way (design.md, Decision 3).
- `docs/concepts/joints.rst`'s site-declaration passage says nothing about
  a conditional rest placement.

## What Changes

- **The manual's build refuses a cross-reference to nothing.** `docs/conf.py`
  sets `nitpicky = True`, so the warnings-as-errors build that CI
  (`python -m sphinx -b html -W docs docs/_build`) and Read the Docs
  (`fail_on_warning: true`) already run refuses an unresolved reference, in
  a page or a docstring, exactly as `-n` does. Neither build configuration
  changes.
- **The five warnings are fixed at their source.** The two `api.rst`
  references name `machinome.node.assembly.AssemblyNode` and keep their
  rendered text; the `Sim.initial` and `Sim.state` docstrings' first lines
  lose the colon napoleon read as a type; `OpenScadNode.__init__`'s
  `name keyword argument:` line becomes `name:`. The rendered meaning of
  the three docstrings changes from wrong to right (no "Type:" field; the
  parameter is called `name`); no word of what they say changes beyond
  that and the typo "defaul".
- **`docs/architecture.md`'s known gaps say only what is so.** The clocked
  "not yet VIEWED" entry, the Create React App entry, the
  `declared_ports` memo entry and the viewer whole-graph-walk entry are
  deleted, each closed by a named commit or accepted viewer ADR; the
  manual-build entry is rewritten to the one fact still true (the CI
  browser-snapshot job installs the viewer from Git); the self-read gate
  entry's dead page path `docs/scenarios.rst` becomes
  `docs/concepts/running.rst`.
- **The joints page says it.** One sentence in the existing site-declaration
  paragraph of `docs/concepts/joints.rst`: a site joint's values are read
  where the child finally rests, after every rest operation the parent
  applies to it, so when one of those is conditional a plain value is right
  for one branch only and the argument to write is a callable of the
  realized parent. No new section.
- Two red pins: `docs/conf.py` is nitpicky (`tests/test_docs_exports.py`),
  and the joints page's site passage names the conditional placement and
  the callable (`tests/test_mate_contract_docs.py`).

**Deliberately out**, with the reason:

- `nitpick_ignore` entries, or `-n` added to the CI command alone. The first
  hides the defects instead of fixing them; the second leaves Read the Docs
  and a contributor's plain `sphinx -W` without the check (design.md,
  Decision 1).
- The CI browser-snapshot job's Git install of the viewer. Whether it should
  install the published viewer is a CI choice nobody asked for; the record
  only stops calling it temporary.
- The other entries of the known-gaps list. None is provably stale from the
  sources at the bench commit (design.md, Decision 3, "Kept").
- The shop craft skill's half of the Inmoov-sim triage
  (`machinome-studio/shop-skills/machinome/SKILL.md`): another repository,
  reported to the campaign, not edited here.
- A changelog bullet. No behaviour a project uses changes: the gate is the
  manual's build, and the three docstrings say what they said, now rendered
  correctly (design.md, Decision 5).
- The projects. No project is read or run by this cycle.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `user-documentation`:
  - MODIFIED "The documentation build produces nothing": the manual's
    configuration is nitpicky, so both warnings-as-errors builds refuse an
    unresolved cross-reference; its four scenarios carried and one added.
  - MODIFIED "The public motion surface is documented": the joints page
    states how a site joint is written under a conditional rest placement;
    its four scenarios carried and one added.

`docs/architecture.md` is the framework's synthesis, not the manual, and no
baseline requirement governs its content (`framework-contributor-guidance`
governs the contributor briefing only); its correction carries no delta
(design.md, Open Questions, 2).

## Impact

- Manual: `docs/conf.py` (one setting), `docs/reference/api.rst` (two
  references), `docs/concepts/joints.rst` (one sentence).
- Docstrings: `machinome/simulation/sim.py` (`Sim.initial`, `Sim.state`,
  first line of each), `machinome/node/openscad/__init__.py`
  (`OpenScadNode.__init__`, one `Args:` line). No code changes.
- Records: `docs/architecture.md` (six entries of "Known gaps and
  tensions"); `workflow/warts.md` (the Curta section's items 5 and 6 move to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md`; the Inmoov-sim
  entry's remaining note is rewritten to the studio half).
- Tests: `tests/test_docs_exports.py` (the nitpicky pin, and a guard on
  Read the Docs' `fail_on_warning`), `tests/test_mate_contract_docs.py`
  (the joints passage pin).
- Builds: CI's docs job and Read the Docs keep their commands and now fail
  on an unresolved cross-reference. Measured at the bench commit, the
  build with the fixes is green from `docs/requirements.txt` alone.
- No ADR, no changelog bullet, no project run.

## Authorization

The pilot's mandate of 6 October 2026 for the fix-warts-3 campaign
(`workflow/ongoing/fix-warts-3.md`, "Mandate"): "work on the items you can
autonomously, orchestrating opus subagents and using empirical evidence
from projects to validate, other than your adversarial review. if
something needs my input, record and defer, you'll go unsupervised." This
change is the campaign table's cycle 15, `strict-manual-build`, validated by
the manual's own build.
