# Adversarial proposal review

**Status:** Initial proposal reviewed on 2026-10-04 under the pilot's
end-to-end authorization, subsequently confirmed explicitly in response to
the orchestrator's mistaken redundant ratification pause. This is design
review, not implementation or fabrication
acceptance. At that initial proposal review, no production code, Curta assets,
or implementation tests had been run or committed by this cycle.

## Review arrangement and baseline

The proposal author and independent Curta consumer reviewer are separate
GPT-6.1 Sol agents. The parent orchestrator performed the framework-side
adversarial review. A different apply agent must implement the framework
under that authority; the consumer agent must deliver and test real Curta3x
assets in that project's own worktree, using the public contract.

Framework base: `e570068287c56e84f6ccb4ed73f0bae7bed5a07c`, the completed
`v0.8-scad-presentation` head. Before implementation, the planning commit on
`v0.8-production` was rebased from its original base
`63c887ed69ebccd2d5a78af4dc75ebeee1acdab1` at the pilot's explicit direction.
The pilot authorized leaving
the source worktree's untracked report untouched when branching. No source
worktree cleanup, integration, push, or publication was performed.

Curta source inspected by the consumer:
`fb4708e98463b3cb4c0130cc3e92514c2a31155b`, root
`simulation.mechanistic:MechanisticCurta`. Its pre-existing untracked files
remain outside this work. Curta2x was not inspected and supplies no evidence.

## Corrections incorporated through delegated review

- **Actual topology, not declarations alone.** An unprepared node has not
  necessarily linked its effective children; render can omit children.
  Core-owned rest-only reading must handle this without simulating or
  treating fusion ingredients and markings as independently handled parts.
- **Laziness, not a geometry-free promise for every output.** Manufactured
  BOM grouping may demand canonical artifact content. Grouping must not
  change because a caller happened to read mass first. Sourced-only and
  structural queries avoid unrelated geometry.
- **No generic save-and-restore simulation scheme.** Arbitrary project
  state cannot be reliably restored after running user simulation code.
  Unsupported stateful reads must be refused, not silently simulated.
- **Direct instances remain supported.** Binding a directly constructed
  model cannot retrospectively certify the bytes Python imported. The
  proposal states that provenance limitation without adding a required
  loader or evaluate call.
- **Whole-binding coherence.** A consumed artifact changing invalidates
  both root and held-child results; an old BOM cannot accompany new copied
  geometry. Canonical geometry identity and artifact byte digest remain
  distinct.
- **Incomplete BOMs are visibly incomplete.** Reading only `bom` exposes
  unassigned, invalid, and absent-target records. Unsupported recipes never
  become valid manufactured lines. Mass also includes unassigned candidates
  as unknown, rather than reporting only the conveniently assigned subset.
- **Independent consumers have declared result fields.** Bound items,
  BOM lines, findings, steps and occurrence records have specified public
  members. Curta tests must not inspect private framework dictionaries.
- **Instructions affect manufacturing identity conservatively.** No
  inference from prose or subject count decides whether a Step is finishing
  or assembly. Version-1 Markdown dependencies have an explicit restricted
  contract rather than silently producing broken exported links.
- **Real consumer delivery is mandatory.** A framework fixture alone does
  not satisfy the requested Curta implementation. Project and framework
  records and commits remain separate.

## Empirical acceptance and its limits

The delegated implementation review clarified the explicit public facade:
scoped selection, zero/one-repeat shape, declared sheet capability, shared
input observation/validation, read-only bound parameters and named mass/check
result fields. These refine the same independent, nested, lazy contract; no
new author-required lifecycle or speculative production process is added.
Failure cleanup must remain framework-owned and preserve held identities,
not attempt arbitrary user-state snapshot/restore. The design and model
consumption specification record these clarifications before final acceptance.

The [author BOM](https://docs.google.com/spreadsheets/d/16EJePozXW-uC6UFISzyT2eMk7c8wh6v-EP5L1U8fzfM/edit)
and its [hardware sheet](https://docs.google.com/spreadsheets/d/16EJePozXW-uC6UFISzyT2eMk7c8wh6v-EP5L1U8fzfM/edit#gid=1182246287)
were inspected on 2026-10-04. The hardware sheet links the seven M4 nuts to
[Bolt Depot product 4784](https://www.boltdepot.com/Product-Details.aspx?product=4784).
Supplier-indexed primary-source product information supports DIN 934 and
M4x0.7; direct product retrieval was restricted. Neither manufacturer nor
grade is asserted. Apply must retain reproducible, attributed source evidence.

The selected draft scope is four crank units and seven sourced nuts, with
fifteen made-wire carry springs explicitly present but unassigned. Two crank
units are existing simulation-fit replacements, not unchanged author STL
geometry. The retaining spring is one author-BOM item represented by five
mixed rigid/flexible patches; no terminal-count comparison can certify that
boundary. Conflicting ball quantities, the simulation-only clearing-loop
mounting and open whole-machine geometry acceptance remain limitations.

Cut uses the existing exact-sheet frame-panel regression fixture and its
historical ADR-053 project origin. It is not a current Metamaquina2 production
implementation: that project's ScadPart has no nominal-DXF contract.

## Proof still owed by apply

Red-first tests must establish state preservation, correct active occurrence
membership, exclusive nested ownership, independent reuse, visible incomplete
outputs, artifact/source invalidation, and pinned portable export. The real
Curta project must exercise the documented API and its existing simulation
regressions against the exact framework content. None of those proofs is
discharged by this review or by schema validation.

Supported draft check: `openspec validate production-layer --strict
--no-interactive` passes. `git diff --check` passes. OpenSpec reports all four
planning artifact categories present. Repeat validation before creating the
planning-only commit under the recorded authority. Integration remains a
separate pilot decision; it does not block isolated implementation.
