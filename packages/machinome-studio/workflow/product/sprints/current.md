# SPRINT-002: One model viewer

## Goal

Every surface that shows a solid-node model — the shop floor, an exported
directory, the documentation, and the live development loop — renders it with
the same viewer, so an improvement to how models are seen is made once and
appears everywhere.

## Stories

- [ ] STORY-006 - See one model viewer everywhere
  - Source: `docs/product/stories/STORY-006-one-model-viewer.md`
  - Brief: `docs/product/sprints/SPRINT-002-brief.md` - findings, decisions with
    their rejected alternatives, the viewer interface consumers require, and the
    intent of every cycle. Read it before opening any cycle in this sprint.

## Ratified scope

- Included: one reusable viewer inside solid-node with the options its
  consumers need; one node-tree serializer behind both published documents;
  delivery of the built viewer inside the framework's Python distribution;
  the shop floor showing models through that viewer instead of its own; the
  development loop showing models through it as well.
- Excluded: publishing the viewer to a package registry; renaming the
  published export bundle, its auto-mount attribute, or its browser global;
  renaming either published document; making build publications portable and
  self-contained; viewer capabilities beyond parity and the options existing
  consumers require.

## Repositories

- `solid-node-shop`
  - Source: `main` @ `595eb00`
  - Sprint branch: `sprint-002`
  - Content: `5a93a4b`
  - Worktree: `WTs/sprint-002`
- `solid-node`
  - Source: `main` @ `6f8a5ae`
  - Sprint branch: `sprint-002`
  - Content: `5c14acf`
  - Worktree: `solid-node/WTs/sprint-002`
  - Shop link: `WTs/sprint-002/solid-node`

## Cycles

- `solid-node` / `unified-node-serializer`
  - Intent: one node-tree walk behind both published documents, converged
    additively; brief section 5 (F1)
  - Story: `STORY-006`
  - Requires: none
  - Branch: `sprint-002-unified-node-serializer` from `6f8a5ae`
  - Commits: `69f9c2e` (planning), `b1e05b9` (implementation/archive)
  - Archive: `openspec/changes/archive/2026-08-01-unified-node-serializer`
  - Integrated: framework `sprint-002` @ `b1e05b9`
- `solid-node-shop` / dev-env frontend package discovery
  - Intent: a framework bench can build any viewer package without installing
    inside a worktree; brief section 5 (S1)
  - Story: `STORY-006`
  - Requires: none
  - Branch: `sprint-002-adjust-dev-env-packages` from `80e0b81` - direct shop
    adjustment, not an OpenSpec cycle
  - Commits: `5a93a4b`
  - Archive: not applicable - direct adjustment
  - Integrated: shop `sprint-002` @ `5a93a4b`; paired framework ignore fix at
    `db59935`
- `solid-node` / `viewer-package`
  - Intent: the single reusable viewer with the interface in brief section 4,
    consumed by export and Sphinx embedding; brief section 5 (F2)
  - Story: `STORY-006`
  - Requires: `solid-node` / `unified-node-serializer`, the dev-env adjustment
  - Branch: `sprint-002-viewer-package` from `db59935`
  - Commits: `b89159f` (planning), `075104c` (implementation/archive)
  - Archive: `openspec/changes/archive/2026-08-01-viewer-package`
  - Integrated: framework `sprint-002` @ `075104c`
- `solid-node` / `viewer-bundle-delivery`
  - Intent: the built viewer ships inside the Python distribution and a CLI
    accessor reports it; brief section 5 (F3)
  - Story: `STORY-006`
  - Requires: `solid-node` / `viewer-package`
  - Branch: `sprint-002-viewer-bundle-delivery` from `075104c`
  - Commits: `369977c` (planning), `5c14acf` (implementation/archive). The
    planning commit was amended after it was first recorded as `8df79e9`;
    `369977c` is the commit on the branch.
  - Archive: `openspec/changes/archive/2026-08-02-viewer-bundle-delivery`
  - Integrated: framework `sprint-002` @ `5c14acf`
- `solid-node-shop` / `floor-uses-framework-viewer`
  - Intent: the shop floor shows models through the framework's viewer instead
    of its own copy; brief section 5 (S2)
  - Story: `STORY-006`
  - Requires: `solid-node` / `viewer-bundle-delivery`
  - Branch: pending
  - Commits: pending
  - Archive: pending
  - Integrated: pending
- `solid-node` / `dev-viewer-on-shared-package`
  - Intent: the development loop shows models through the same viewer and the
    last per-node walk retires; brief section 5 (F4)
  - Story: `STORY-006`
  - Requires: `solid-node` / `viewer-bundle-delivery`
  - Branch: pending
  - Commits: pending
  - Archive: pending
  - Integrated: pending
- `solid-node-shop` / `adjust-ignore-framework-link`
  - Story: none - sprint machinery
  - Requires: none
  - Branch: `sprint-002-adjust-ignore-framework-link` from `a0d74d3`
  - Commits: `f42cfe9`
  - Archive: not applicable - direct adjustment
  - Integrated: `sprint-002` @ `f42cfe9`

## Paired validation

- `python -m pytest tests/` (128 passed) and `bash tests/dev-env-test.sh`
  (all tests passed) passed from `WTs/sprint-002` after the rebase for shop
  content `f42cfe9` and framework content `6f8a5ae`.
- Framework suite (363 passed, 3 skipped, 5 subtests) passed for framework
  content `b1e05b9` before integrating F1. Combined shop/framework validation
  for shop content `f42cfe9` and framework content `b1e05b9` is pending the
  dev-env adjustment.
- Combined validation passed from `WTs/sprint-002` against its linked framework
  worktree for shop content `5a93a4b` and framework content `db59935`:
  shop `pytest tests/` 128 passed with 23 subtests; `bash tests/dev-env-test.sh`
  all tests passed; framework `pytest tests/` 363 passed, 3 skipped, 5 subtests.
- End-to-end bench proof for finding F-5: `scripts/dev-env probe-bench setup
  --base sprint-002` linked all four frontend directories, the bench worktree
  reported clean, `npm run build` produced `dist/solid-widget.js` (483.7kb)
  with no install inside the worktree, and teardown removed the bench cleanly.
- Combined validation passed from `WTs/sprint-002` against its linked framework
  worktree for shop content `5a93a4b` and framework content `075104c`: shop
  `pytest tests/` 128 passed with 23 subtests; `bash tests/dev-env-test.sh` all
  tests passed; viewer `npm test` 24 passed, `npm run typecheck` and
  `npm run build` passed; framework `pytest tests/` 372 passed with all 9
  widget browser tests running; the V8 export was regenerated from the tested
  framework content and the Sphinx build passed with `-W`; `openspec validate
  --all --strict` passed all 12 specs.
- Combined validation passed from `WTs/sprint-002` against its linked framework
  worktree for shop content `5a93a4b` and framework content `5c14acf`: shop
  `pytest tests/` 128 passed with 23 subtests; `bash tests/dev-env-test.sh` all
  tests passed; framework `pytest tests/` 380 passed with 5 subtests;
  `openspec validate --all --strict` passed all 13 specs; the V8 export was
  regenerated from the tested framework content and the Sphinx build passed
  with `-W`. The viewer package was not rebuilt because F3 changed no file
  under `solid_node/viewers/widget/`.
- Distribution provenance for framework content `5c14acf`, proved from a
  disposable clone outside every worktree: `python -m build` produced both
  distributions, and each carries
  `solid_node/viewers/widget/dist/solid-widget.js` (497823 bytes) with no
  `node_modules` entries. Installing that wheel into a throwaway virtualenv and
  running `solid viewer` from an unrelated directory printed the installed
  bundle path and `"apiVersion": 1` and exited 0. This closes finding F-4 and
  satisfies the F3 post-integration evidence task.

## Decisions and scope changes

- 2026-08-01 - Stage the work as separate cycles rather than one change,
  because the development-loop viewer rests on a different architecture than
  the other two and carries the sprint's largest risk.
- 2026-08-01 - Include the development-loop viewer in this sprint; the goal is
  not met while one surface still carries its own implementation.
- 2026-08-01 - Unify the node-tree serializer behind both published documents
  and keep both document names, because the two names distinguish a portable
  directory from a build publication.
- 2026-08-01 - Keep the published export bundle name, auto-mount attribute,
  browser global, and current package directory unchanged. A package-directory
  rename may return during F2 only with a proven dependency-source/refresh path
  for framework benches and explicit pilot ratification.
- 2026-08-01 - Report an absent or incompatible viewer as one shop preparation
  failure rather than a degraded browser state, because no user exists today
  for whom the shop and the framework are versioned independently.
- 2026-08-01 - Do not publish the viewer to a package registry; deliver it
  inside the framework's Python distribution, deferring public release surface
  until an external consumer exists.
- 2026-08-01 - Correct the shop ignore rule so the framework sprint link is
  ignored as required, as a direct adjustment on the sprint branch: a commit on
  shop `main` would move it off the recorded base and prevent fast-forward
  integration when the sprint is archived.
- 2026-08-01 - Rebase shop `sprint-002` onto `main` @ `595eb00` before opening
  any feature cycle, incorporating the unrelated running-the-shop documentation
  change while histories are uncontested and preserving fast-forward archive
  integration.
- 2026-08-01 - Serialize the framework viewer build cycles as F2, then F3,
  then F4 by making F4 depend on F3. Their benches share heavy frontend
  directories through the shop's development environment, so the sprint graph,
  rather than transient orchestrator state, prevents overlapping writers.
- 2026-08-01 - Prove final distribution provenance from a disposable full
  checkout of the exact integrated framework content commit, outside every
  worktree; shared bench outputs remain development conveniences rather than
  release evidence.
- 2026-08-01 - Withdraw the Hermes-authored `SPRINT-002-validation.md` proof
  matrix and the enlarged S1 scope derived from review findings. Neither was
  pilot-authored: the shop protocol defines no sprint-level validation artifact,
  and the S1 text had been rewritten to absorb reviewer output. Each cycle's
  proof belongs to its own OpenSpec proposal, as the brief already states.
- 2026-08-01 - Deliver S1 as a direct shop adjustment rather than an OpenSpec
  cycle. Discovering frontend packages in `scripts/dev-env` is a narrow
  correction to an internal development script with no user-visible behavior.
  Run as a cycle it grew into a shared-store transaction protocol that the
  sprint does not need; the abandoned attempt is recorded in `sprint-log.md`.
- 2026-08-01 - Cherry-pick the S1 dev-env fix onto shop `main` as `0032e26`.
  Benches are opened with the primary checkout's `scripts/dev-env`, which on
  `main` still linked only the CRA app, so opening F2 produced a bench that
  could not build the widget. Every remaining framework cycle would repeat it.
  Shop `main` had already advanced past the recorded sprint base `595eb00`
  before this, so fast-forward archive integration was already unavailable and
  the duplicate commit costs nothing it had not already lost: shop `sprint-002`
  must be rebased onto `main` before archive integration, where this identical
  patch is expected to drop out. F3 and F4 open with the ordinary command.
- 2026-08-01 - Anchor the widget's ignore patterns (`/node_modules`, `/dist`)
  in the framework rather than tracking managed links or excluding them at
  setup time. A trailing-slash pattern matches directories but not symlinks, so
  the unanchored form left every bench worktree dirty. The CRA app already used
  the anchored form; matching it is what makes bench links work, and it removes
  the reason the abandoned cycle invented link-cleanliness metadata.

## Outcome

Completed when the sprint is archived.
