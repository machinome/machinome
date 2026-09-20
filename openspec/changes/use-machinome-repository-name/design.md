## Context

The prepared 0.7.0 wheel/sdist embed the old repository URL through project metadata and README. The framework identity spec explicitly names that URL. ADR-130 records the original identity decision; its runtime/package boundary remains correct and only its repository spelling is refined by this change.

Maintainer need: the pilot's pre-release source-repository rename.
Standalone primary base: `44edea849ec9aa15c30bfbd1d4298805f5f78636`, branch `main`, verified clean.
Cycle branch: `rename-framework-repository`.
Cycle worktree at opening: `/home/asa/devel/machinome-studio/machinome-framework/WTs/rename-framework-repository`.
Integration target: framework `main`. Shop companion cycle base: `2cc7c3c60dbcc0730f8899fb4c0bf0caca070c5e`. Neither cycle is sprint-scoped.

## Goals / Non-Goals

Goals: correct the public source identity and leave verified 0.7.0 distribution artifacts ready for release.
Non-goals: Python/API/schema/dependency changes, publishing, tagging, pushing, or rewriting historical release evidence.

## Decisions

1. Modify the existing identity requirement and its source-link scenario. Keep package/import/command `machinome` and version 0.7.0.
2. Update metadata and current docs together. Retain historical ADR and archived-change wording, with a current transition note referencing this change; no new architecture ADR is warranted.
3. Rebuild both wheel and sdist because the URL and README are embedded. Use a new explicit artifact directory and record hashes instead of silently overwriting the previous release set.
4. Rebuild companion distributions only when their packaged documentation changes; keep their prepared versions. Validate the resulting combined release set using the existing release smoke script.
5. The shop owns the filesystem move and affected local Git/installation metadata. Framework content is edited and committed only in its own isolated worktree.

## Risks / Trade-offs

- Retained old distributions can be uploaded accidentally → the release handoff identifies one exact new wheel/sdist set with checksums.
- Importing from source can disguise packaging errors → install and smoke both wheel and sdist sets in an isolated environment outside repository roots.
- Full manual links may retain the old name → rebuild the manual and inspect current links, distinguishing historical source records.
- Remote repository rename timing → verify the chosen remote read-only when available; do not perform the GitHub rename or publish anything.

## Migration Plan

Ratify and validate the planning artifacts, then create the planning-only commit. Change the existing homepage assertion first and prove it fails against current metadata; update metadata and current references, then run identity and release/docs-focused checks. Build corrected wheel/sdist artifacts, check metadata and both installation forms, rebuild the current manual and record hashes. Synchronize the baseline identity spec, archive and commit the implementation record with that evidence. Integrate locally after rechecking the base; coordinate the shop move, refresh the local origin URL and verify the retained artifacts at their final paths. Record final content commit IDs in subsequent release-evidence material if needed. The previous release evidence stays intact.

## Open Questions

None about name, versions or runtime scope. Publication remains the pilot's later action.
