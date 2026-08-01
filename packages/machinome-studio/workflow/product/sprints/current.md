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
  - Content: `db59935`
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
  - Commits: pending
  - Archive: pending
  - Integrated: pending
- `solid-node` / `viewer-bundle-delivery`
  - Intent: the built viewer ships inside the Python distribution and a CLI
    accessor reports it; brief section 5 (F3)
  - Story: `STORY-006`
  - Requires: `solid-node` / `viewer-package`
  - Branch: pending
  - Commits: pending
  - Archive: pending
  - Integrated: pending
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
- 2026-08-01 - Operational note for the remaining framework cycles: the S1
  dev-env fix lives on shop `sprint-002` and does not reach shop `main` until
  the sprint is integrated, so the primary checkout's `scripts/dev-env` still
  links only the CRA app. Opening F2 with it produced a bench that could not
  build the widget. Open F3 and F4 by materializing the sprint-branch script at
  the shop root first (`git show sprint-002:scripts/dev-env`), running setup
  with it, and removing it; confirm the setup output links all four frontend
  directories before proposing.
- 2026-08-01 - Anchor the widget's ignore patterns (`/node_modules`, `/dist`)
  in the framework rather than tracking managed links or excluding them at
  setup time. A trailing-slash pattern matches directories but not symlinks, so
  the unanchored form left every bench worktree dirty. The CRA app already used
  the anchored form; matching it is what makes bench links work, and it removes
  the reason the abandoned cycle invented link-cleanliness metadata.

## Outcome

Completed when the sprint is archived.
