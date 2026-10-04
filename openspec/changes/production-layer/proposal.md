## Why

Curta-Type-I-3x imports printed and bought components from the same STEP source, while its author's BOM specifies repeated quantities, variable infill and finishing operations that geometry cannot express. Makers need independent production assets over the actual parameterized model, with honest partial coverage and no change to its simulation.

## What Changes

- Bundle a dependency-light `machinome.production` package in the Machinome distribution; simulation-only imports remain independent of production.
- Provide typed `Production[Model]`, explicit `Item(target, process)`, nested child production binding, ordered maker instructions, BOM/stock/mass/findings properties and portable draft exports.
- Introduce a narrowly read-only public model consumption facade for actual prepared occurrences, qualified declaration references and pinned geometry facts. Production never reconstructs model defaults or recognizes class-name strings.
- Keep mass unknown unless explicitly measured or requested under a homogeneous-solid assumption. Keep missing ownership and conflicting coverage visible.
- Validate a partial Curta3x production against the author's BOM and instructions. Two profiles on the same 3x instance are controlled regressions, not evidence of an author-approved alternate workshop. Curta2x is future work and excluded.

## Capabilities

### New Capabilities

- `production-assets`: independent typed production bindings, lazy outputs, coverage, consolidation, stock, mass and portable maker instructions.
- `model-consumption`: public read-only access to an existing model's resolved physical occurrences and coherent artifact facts.

### Modified Capabilities

None. Existing geometry, printed-piece identity, simulation, model declaration and viewer contracts retain their meanings.

## Impact

New modules under `machinome.production` and a public model facade; narrowly scoped internal adaptation behind that facade, distribution smoke tests and documentation of the new public contract. The existing vet purity classification must deny the new effectful ModelSnapshot and production profile entry points while retaining pure component/recipe records; this preserves the existing purity rule rather than adding a CLI or policy. No viewer/document-version change, new CLI, heavy mandatory dependency, simulation mass integration, standard catalogue database, CAM, nesting or automatic fabrication certification.

Cycle: branch `v0.8-production`, worktree `machinome/WTs/v0.8-production`, base `e570068287c56e84f6ccb4ed73f0bae7bed5a07c`, the completed `v0.8-scad-presentation` HEAD. At the pilot's explicit direction the planning commit was rebased from the original `63c887ed69ebccd2d5a78af4dc75ebeee1acdab1` before implementation. The original branch point was authorized despite an unrelated untracked report, which this cycle did not touch. This is a standalone cycle, not sprint work. Integration is not authorized.

## Pilot authority

The pilot explicitly instructed the orchestrator to carry out proposal and
apply with separate GPT-6.1 Sol agents, parent adversarial review and an
independent Curta implementation agent as a consumer review. That was advance
authorization for the agreed bundled, nested, lazy production scope, with only
Curta3x as the real Curta consumer. The pilot subsequently confirmed that this
authorization already covered ratification, corrected the redundant approval
pause, and instructed rebasing onto the finished source branch before apply.
The proposal and consumer reviews are recorded in review.md. Proceed through
validation, planning commit, apply, independent validation and completion
without another ratification prompt. This records delegated authority and
agent review, not a claim of human line-by-line review. No merge, push,
publication or geometry redesign is authorized.
