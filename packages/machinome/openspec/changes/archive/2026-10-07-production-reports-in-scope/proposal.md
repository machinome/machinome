## Why

Three defects of the production layer, recorded by the adversarial review
of the framework cycle `production-layer` in `workflow/warts.md`, section
"Findings from the adversarial review of the framework cycle
`production-layer` (4 October 2026)":

> **The Markdown gate refuses text that is not a dependency.** `_markdown`
> (`profile.py:143-181`) rejected `if a<b then c>d ok` and a code span
> containing a tag as an "unsupported HTML dependency". Version 1 was meant
> to refuse dependencies a bundle cannot carry, not inequalities or quoted
> markup. **Untriaged.**

> **An overlap anywhere in the root blocks an unambiguous child's reports.**
> With an overlap under `right`, `production.left.bom` raises
> `ProductionConflictError`: `_read` (`profile.py:361-374`) checks every
> overlap finding of the shared root, not the ones inside the queried
> scope. The design refuses ambiguous totals; the child's totals are not
> ambiguous. **Untriaged.**

> **Declaration paths change shape with the repetition count.** A
> one-member repeated child binding is named `kids/arbitrary_name` and a
> two-member one `kids-0/arbitrary_name` (`profile.py:1083-1085`), although
> the binding is a tuple in both cases, as the spec requires. A consumer
> test pinning a declaration path breaks when a count parameter moves from
> one to two. **Untriaged.**

**Reproduced on the bench `fix-warts-3` at `cd43432`**, with the
interpreter check printing
`/home/asa/devel/machinome/machinome/WTs/fix-warts-3/machinome/__init__.py`.
The fixtures are the suite's own (`Root` with `left = Submodel(count=2)` and
`right = Submodel(count=3)`, `SubProduction` sourcing `Submodel.nuts`),
in a scratch script (`repro_reports.py`, copied into evidence.md by the
applier):

```
--- 1. Markdown gate, direct ---
  inequality                         ProductionExportError: step: unsupported HTML dependency in assembly.md
  inequality, other letters          ProductionExportError: step: unsupported HTML dependency in assembly.md
  tag in code span                   ProductionExportError: step: unsupported HTML dependency in assembly.md
  tag in fenced code                 ProductionExportError: step: unsupported HTML dependency in assembly.md
  harmless element                   ProductionExportError: step: unsupported HTML dependency in assembly.md
  link in code span                  ProductionExportError: step: unsupported local or URL dependency 'local.png' in assembly.md
--- 1. Markdown gate, through steps ---
  steps of 'if a<b then c>d ok'      ProductionExportError: step: unsupported HTML dependency in <scratch>/md-.../assembly.md
--- 2. Overlap inside right; reading left ---
  overlap finding                    [(('right/nuts-0',), ('right/a', 'right/b')), (('right/nuts-1',), ...), (('right/nuts-2',), ...)]
  left.findings                      ()
  left.bom quantities                ProductionConflictError: overlapping ownership: right/a, right/b claim right/nuts-0; ...
  left.mass.complete                 ProductionConflictError: ...
  left.steps                         ProductionConflictError: ...
--- 2. Parent reaches inside left; reading right ---
  overlap finding                    [(('left/nuts-0',), ('extra', 'left')), (('left/nuts-1',), ('extra', 'left'))]
  right.bom quantities               ProductionConflictError: overlapping ownership: extra, left claim left/nuts-0; ...
--- 3. Declaration paths by repetition count ---
  repeat n=1: type=tuple paths=['kids/arbitrary_name'] bom.declarations=[('kids/arbitrary_name',)]
  repeat n=2: type=tuple paths=['kids-0/arbitrary_name', 'kids-1/arbitrary_name'] ...
  tuple of 1: type=tuple paths=['kids/arbitrary_name']
  tuple of 2: type=tuple paths=['kids-0/arbitrary_name', 'kids-1/arbitrary_name']
  single reference: type=SubProduction path=kid/arbitrary_name
```

(`inequality, other letters` is `keep x<y and z>w`; `harmless element` is
`press <kbd>Ctrl</kbd>`.) The draft manifest carries the same paths: a
repetition over a `Count` exports `bindings` `['', 'kids']` at one member
and `['', 'kids-0', 'kids-1']` at two (`probe_holder.py`).

Why each happens is in design.md, Context: the HTML check matches any
tag-shaped text over the whole file, code included; `_read` tests every
overlap finding of the shared root, where `findings` and the reports
themselves already read only the binding's scope; and the binding's tuple
shape and its members' names are decided by two different tests.

## What Changes

- **The Markdown gate reads what CommonMark renders and refuses a tag that
  can carry a dependency.** Fenced code blocks and code spans are not read
  for dependencies; an HTML block is read whole. A tag is refused when its
  element embeds or loads content (`img`, `script`, `link`, `iframe`,
  `object`, `style`, …) or it carries an attribute that names a resource
  (`src`, `href`, `data`, `srcset`, `style`, …). `if a<b then c>d ok`,
  `<kbd>Ctrl</kbd>` and markup quoted in code are accepted; every refusal
  the suite pins stands, `<a href="https://...">` included. The cases on
  both sides are design.md, Decision 1.
- **A binding refuses only for the overlaps in its own scope.** `_read`
  refuses with `ProductionConflictError` when an overlap finding names an
  occurrence within the binding's scope: the same test `findings` and the
  reports' records use. The root's scope holds every occurrence, so the
  root still refuses on any overlap; a parent Item reaching into a child's
  subtree still refuses that child; `findings` stays readable everywhere.
- **A tuple binding's members are always indexed.** A repeated child
  binding, or a tuple of references, names its members `name-0`,
  `name-1`, … at every count, one included; a single non-repeated
  reference is still named without an index.
- **Tests** in `tests/test_production.py`: the gate's accepted cases (red
  today) and its refused cases (guards, one red today), an inequality
  read through `steps` and `export` (red today), the overlap's scope in
  two fixtures (red today), and the indexed members at one and two members
  for a repeat and a tuple, with the manifest (red today), and a single
  reference unindexed (guard).
- **Records.** The manual's production paragraph on Markdown, repeated
  bindings and overlaps; a changelog bullet under `Unreleased`; the three
  warts items move to the campaign's `resolved.md`.

**Deliberately out**, with the reason:

- **HTML naming an external HTTP(S) resource stays refused.** Markdown
  links to one are accepted; an HTML link is a second grammar no project
  asks for (design.md, Open Question 1).
- **The rest of the review's section.** The bundle's absolute paths
  (changes the published bundle's keys), `Finding.check_status` (a
  contract decision now that 0.8.0 shipped) and the facade's copied
  lifecycle (design debt) are the pilot's; the bytes held in memory stays
  untriaged. Cycle 10 closed the doubled placements and the missing-file
  error.
- **The manifest's `version` stays 1.** Its shape is unchanged; only a
  one-member tuple's member paths gain their index (design.md, Decision 3
  and Open Question 2).
- **No Markdown parser.** The framework declares none; the gate's line
  scan reads more as HTML wherever it could differ from CommonMark, so it
  only ever refuses more.
- **No ADR.** The change applies the spec's own rules to the code.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `production-assets`: three requirements are modified.
  - "Actual nested delegation and traceable quantity": a sentence states
    that a repeated or tuple child binding is a tuple at every count and
    names each member by its index in declaration paths, and that a single
    reference is named without one. One scenario is added, "A count moves
    from one to two". The existing scenario "Differently sized repeated
    children" is carried unchanged.
  - "Honest exclusive ownership": the sentence on refusing ambiguous
    outputs states that a binding's reports are refused for an overlap
    naming an occurrence within its scope, the root's scope holding every
    occurrence. One scenario is added, "An overlap under one child leaves
    its sibling readable". The existing scenarios "Parent reaches inside a
    delegated subtree" and "Purchase replaces internal delegation" are
    carried unchanged.
  - "Instructions remain local and ordered": a sentence states what an
    HTML dependency is and that code spans and fenced code blocks are not
    read for dependencies. Two scenarios are added, "An inequality is not
    a dependency" and "Markup quoted in code is not a dependency". The
    existing scenarios "A local image would break the bundle" and "Child
    and parent use the same filename" are carried unchanged.

## Impact

- **Code:** `machinome/production/profile.py` only: `_markdown`
  (`:143-181`) and new private module constants and two private functions
  above it; `Production._read` (`:366-385`) and `findings` (`:394-416`),
  through a new private method `_in_scope`; the child-binding branch of
  `_Shared.resolve.populate` (`:1070-1110`).
- **Tests:** `tests/test_production.py` gains six tests (three
  parametrized); no existing test changes.
- **Public surface:** no new name. Three behaviours change: the gate
  accepts text it refused (and refuses a reference whose only definition
  is in a fenced block, which it accepted); a child's reports read where
  they were refused; a one-member repeated or tuple child binding's
  member paths gain `-0` in `BoundItem.declaration_path`,
  `BomLine.declaration_paths`, `Finding.declarations`,
  `ResolvedStep.step_id` and the draft manifest's `bindings`, `owners`
  and `instruction_files`.
- **Manual:** `docs/reference/api.rst`, the production section: one
  sentence each on what HTML dependency means and code, on indexed tuple
  members, and the overlap sentence scoped (design.md, Decision 5).
- **Projects:** a search of every `*.py` under `projects/` finds
  `machinome.production` only in the Curta production slice
  (`projects/Calculators/Curta-Type-I-3x`, worktree
  `WTs/production-layer-3x`, branch `production-layer-3x`, `7c9121e`). Its
  twelve Markdown files hold no `<` or `>` (the code spans they hold quote
  module and file names) and both the present and the proposed gate accept
  each of them; it declares no overlap; its child bindings are five single
  references and two tuples `springs` of ten and five members, already
  indexed, and its test pins no declaration path. Nothing it reads or pins
  changes, and no project edit is needed. As in cycle 10, the slice cannot
  be collected against this bench at `7c9121e` (its test imports
  `from machinome.node import AssemblyNode, StepNode`, which the 0.8 root
  refuses), so it runs through cycle 10's scratch overlay (the slice's
  `production/` package with that one import rewritten, beside links to
  the Curta's `main`, `1f3dc22`; recipe in
  `openspec/changes/archive/2026-10-07-production-reads-once/evidence.md`
  and that change's `tasks.md`),
  with a scratch `SOLID_BUILD_DIR` and nothing written in the project. At
  Stage P it passes 6 tests in 134.08 s (wall 135.36 s, a new build
  directory), and the Curta's `git status --short` is the same before and
  after.

## Authorization

The pilot's mandate of 6 October 2026 for the fix-warts-3 campaign
(`workflow/ongoing/fix-warts-3.md`, "Mandate"): "work on the items you can
autonomously, orchestrating opus subagents and using empirical evidence
from projects to validate, other than your adversarial review. if
something needs my input, record and defer, you'll go unsupervised." This
change is the campaign table's cycle 11, `production-reports-in-scope`,
validated in the Curta-Type-I-3x production slice. design.md's two Open
Questions each carry a recommendation, and neither blocks the fix.
