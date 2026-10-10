# Independent implementation review

Status: accepted on 2026-10-04. The complete framework rerun is green after
correcting two release-page regressions. A subsequent isolated arithmetic
correction passes focused and paired validation, recorded separately below.
There are no unresolved implementation-review blockers. This record does not
claim whole-machine fabrication acceptance or a released capability.

## Roles and tested base

- Proposal: separate GPT-6.1 Sol proposal agent.
- Framework apply: GPT-6.1 Sol implementation agent, with an exclusively
  scoped Sol model-facade implementation worker.
- Curta3x: independent Sol consumer agent, project-owned production assets
  and public-API tests, with no framework workaround or simulation rewrite.
- Adversarial review and final regression: parent orchestrator. The parent
  amended planning records and reviewed/reproduced defects; the implementation
  agents made the framework and project code changes.

The planning commit was rebased at the pilot's explicit direction onto the
completed `v0.8-scad-presentation` head
`e570068287c56e84f6ccb4ed73f0bae7bed5a07c` before implementation. Current
planning-only commit is `41d24cef37817f2a8c0c79ea9014eb93b77a0261`;
implementation is recorded in the separate completion commit containing this
review, not mixed into the planning commit.
The pilot's end-to-end authorization is recorded in proposal.md. No repeated
ratification, integration, push or publication is inferred.

## Review findings addressed in implementation

1. The existing rest walker normalized malformed render results to an empty
   tuple before a consumer could validate them. Structure-only reading now
   validates the original result and refuses legacy state reads, without
   simulating or materializing the machine.
2. A public scoped-reference probe returned root sibling `wire` through
   `compound.external`, even with scope `compound`. The independently run
   probe demonstrated the escaped occurrence. Scoped selection now excludes
   aliases outside the delegated subtree, with a regression test.
3. Initial failure cleanup copied arbitrary instance containers and replaced
   whole instance dictionaries. That is not a valid rollback of arbitrary
   user code and can detach held simulation/container references. Review
   required cleanup to remain limited to framework-owned placement/rest
   bookkeeping and preserve container identities.
4. Rigid rest structure needed to be reused by subsequent normal preparation,
   not rendered again with duplicated placements. Same-instance and normal
   lifecycle regressions pin this boundary; inherited field references select
   the actual replacement rather than reconstructing an ancestor's child.
5. Wrong production constructor values could become latent child declarations.
   Explicit supported-reference recognition now rejects them. A parent probe
   confirms integer, string and arbitrary-object arguments raise BindingError.
   Concrete profile inheritance and result-member shadowing are refused.
6. An invalid recipe on an assembly could hide its descendant candidates and
   collapse unknown mass. Only valid whole-assembly sourcing replaces their
   acquisition/mass obligations. Empty assemblies also retain delegation
   ownership boundaries, and absent findings remain scoped to their binding.
7. Child export originally copied every file previously read anywhere in the
   shared root. Its result therefore depended on whether root instructions had
   already been requested. Export now selects the queried steps/mass evidence,
   and the regression compares both read orders.
8. Instruction resolution initially used only the importing profile's module.
   Imported/reused Step and measured-evidence declarations now retain their
   constructing module's source attribution. Unsupported Markdown dependencies
   are refused contextually, not silently exported with broken dependencies.
9. The new consumption/profile entry points would otherwise inherit the vet
   universe's trust in framework imports. Narrow effectful-entry classification
   preserves the existing pure-model rule while retaining neutral records and
   Reference. No new CLI or production-to-model dependency is introduced.
10. Final arithmetic inspection found that multiplying finite solid volume
    and density before unit conversion could overflow despite a representable
    result, and that a known-mass subtotal could silently become infinite.
    Public-path tests reproduced overflow, false known-zero underflow and
    infinite subtotals. Exponent-scaled arithmetic now preserves representable
    results, treats unrepresentable solid mass as unknown and refuses an
    unrepresentable subtotal, without inventing physical parameter limits.
    Export retains its existing ProductionExportError wrapper and arithmetic
    cause, leaving neither a destination nor staging residue. The parent's
    initial test request incorrectly expected the underlying OverflowError
    directly from export; the test was corrected to the existing wrapper
    contract, not the implementation changed to satisfy that mistaken request.

Supporting facade helpers, sheet-capability facts, bound parameters and named
mass/check result fields were clarified in the planning commit under the
existing delegated scope. These remove private production access; they add no
author-required evaluate/plan lifecycle. A structural finding's check status
does not certify unrequested geometry or mass checks.

## Empirical review

The independent Curta consumer initially used a nonexistent `src/` import path,
so its first installed-primary run was disqualified as paired evidence. The
corrected run verifies both imported framework module paths inside this exact
flat-layout worktree. It then exposed a genuine consumer-authoring error: the
last three M4 nuts belong under `frame/upper_frame`, not the bell assembly.
The expected total stayed seven; selectors were corrected rather than the
oracle weakened. This history is retained in the project's evidence record.

The corrected live paired run passed 12 tests and six subtests in 94.80 seconds.
It exercises four printed crank occurrences, seven DIN 934 M4x0.7 nuts,
fifteen unassigned made-wire candidates, scoped instructions, direct exports,
two profiles on the same nondefault running model, and preservation of source,
parameters and simulation state. A strengthened exact five-patch retaining
spring assertion is included in the final frozen-source rerun. No Curta2x
source was inspected or used. The parent reviewed every staged project asset
and authorized its focused commit after the final stable paired run. That run
passed 12 tests and six subtests in 100.25 seconds with identical framework
package hashes before and after. The resulting independent project commit is
`bab7c156b50bf672f54021479f3caf500ecf11ae`; its evidence distinguishes the tested
tree from subsequent evidence-only additions.

## Validation checkpoints

Before implementation, the parent ran:

```text
python -m pytest -q tests/test_state_binding.py tests/test_builder_lifecycle.py tests/test_pieces.py tests/test_sheet_leaf.py tests/test_source_generation.py tests/test_scad_presentation.py
152 passed, 9 warnings, 30 subtests passed in 120.40s
```

This is a rebased-baseline check, not proof of the later implementation.
Apply subsequently reported 89 focused tests and 62 subtests passing across
production, facade and vet checks, including the existing exact 6mm sheet
fixture's Cut/DXF path. The parent independently ran the complete framework
suite with `python -m pytest -q -p no:cacheprovider -rf` after source freeze:
**2 failed, 4433 passed, 4 skipped, 55 warnings, 3672 subtests, 670.42s**.
Both failures are the release-only status-page checks in
`test_profile_documentation.py` and `test_release_records.py`: the added
development paragraph violated that page's released-facts contract. The parent
had accepted this paragraph during review and requested its removal after the
tests exposed the mistake. Existing tests are not weakened; unreleased feature
documentation stays in the development changelog and API reference.

An isolated wheel and sdist build plus dependency-minimal installed import
smokes passed. Strict Sphinx still reports five existing cross-reference
warnings. The apply agent reproduced exactly the same five targets using the
same command and environment against an isolated archive of base `e570068`;
this is a reported baseline limitation, not a green strict documentation build.

Scoped lint found formatting and unused-import/local issues in the new files.
The source freeze was released after the full run for focused cleanup and the
release-page correction. Focused and paired reruns follow it; no broad baseline
reformat or ignore-rule weakening is authorized. Final outcomes and content
identities are owed before this review can be marked complete.

## Final-source checks

After the correction and scoped cleanup, **115 tests and 337 subtests passed
in 9.32s**, including both previously failing release-page checks. Scoped
flake8 reports zero, and diff checks pass. The final isolated wheel and sdist
build and both installed import smokes also passed; their hashes are in
evidence.md.

The independent Curta rerun passed **12 tests and six subtests in 100.79s**
against unchanged project implementation `bab7c156b50bf672f54021479f3caf500ecf11ae`
(tree `e17dfd7d58f50c72b9989e41808614f0d49d03de`). Import checks identified this
framework worktree, and the framework Python-package fingerprint was identical
before and after:
`4c60b1115f303d30a6a5cfcc00376cf9292a5be7a4a70932244c0609e76153d5`.
The parent independently reproduced that fingerprint. The consumer's later
evidence-only commit will identify the completed framework commit without
changing its implementation or simulation.

Studio public-contract synchronization is independently committed as
`4f161c89929a057ea7557676ef21d8f8c2c0129e`, based on
`fabb754eca0a04624a4208fbf5ef26c6dc1b0eea`. Skill validation, 17 contract tests
and diff checks pass; its primary and isolated branch are clean and unmerged.
Only the API skill changed, with the capability explicitly development-only.

The parent synchronized all four model-consumption and nine production-assets
requirements, comparing every delta requirement to the resulting baseline.
Both baseline specs and the change pass strict supported OpenSpec validation.
The runtime instruction snapshot's obsolete one-commit context does not
override the workspace's explicit two-commit cycle contract. No optional
archive operation guidance is supplied by this installed schema.

The second complete suite passed **4435 tests, 4 skipped, 55 warnings and
3672 subtests in 668.37s**, on package fingerprint `4c60b111…76153d5`.
This is the full-suite checkpoint before the final arithmetic correction.
The correction changes only the mass calculation and its tests, so subsequent
verification uses the complete focused contract/docs/vet group, paired Curta
tests, lint and distribution smokes rather than implying another full-suite
run. The parent compared the exact pre/post production source: only the mass
arithmetic block changed, with 630 leading and 592 trailing lines unchanged.
The final independent focused command reran production, model-consumption,
vet universe/assertions, production documentation, docs structure, class-name
recognition, profile documentation and release records: **119 passed,
337 subtests, four existing warnings, 9.90s**. Scoped flake8 returned zero.
Final package fingerprint is
`cba98e7237076f001503e3e0f5aff55ff35cbaa18476de18feff85a534924ffa`.
The final Curta paired run passed **12 tests and six subtests in 97.55s**
with that exact package fingerprint unchanged before/after. Project production
code and simulation remain at implementation commit `bab7c156`; only cumulative
evidence records have changed. No Curta2x work was performed.

The post-correction, post-test-assertion wheel and sdist build and both
outside-checkout installed import smokes passed. Final artifact hashes are in
evidence.md. The strict Sphinx build's five reproduced baseline warnings remain
the only reported validation limitation; they were neither hidden nor expanded
into unrelated repair work.

## Completion disposition

Accepted ADRs 174 and 175 and the architecture/index updates describe the tested
design. The independent Curta asset and Studio API skill are committed on their
own isolated lines; Curta's evidence-only follow-up records the final framework
commit after this record is committed. All thirteen new baseline requirements
match their deltas and strict OpenSpec validation passes.

This is standalone work in
`/home/asa/devel/machinome/machinome/WTs/v0.8-production`, based on the completed
`v0.8-scad-presentation` commit stated above. It has no sprint dependencies.
No integration destination or merge is newly authorized: the source line is
the pilot-selected base, not permission to advance that line or primary.
Framework, Studio and Curta branches remain unmerged and unpushed. No server,
release, tag, publication or external contact is part of completion.

OpenSpec archival completed at
`openspec/changes/archive/2026-10-04-production-layer/`, preserving the schema
record and all completed tasks. The change passed strict validation immediately
before moving; all 45 remaining baseline specs passed strict validation after
moving (the prior 46th item was the now-archived change). The completion commit
contains implementation, tests, manuals, synchronized specs and this archive.
After archival, the parent reran production, model-consumption and production
documentation tests: **52 passed, four existing warnings, 6.78s**. The package
fingerprint still matches the final paired Curta run. Diff checks pass and all
staged files belong to this cycle.
